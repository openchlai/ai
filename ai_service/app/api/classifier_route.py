from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime
from ..utils.text_utils import ClassificationChunker, ClassificationAggregator
from ..model_scripts.model_loader import model_loader
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/classifier", tags=["classifier"])

   

class ConfidenceScores(BaseModel):
    main_category: float
    sub_category: float
    intervention: float
    priority: float


class ChunkPrediction(BaseModel):
    chunk_index: int
    token_count: int
    sentence_count: int
    position_ratio: float
    main_category: str
    sub_category: str
    intervention: str
    priority: str
    confidence_scores: ConfidenceScores


class ClassifierRequest(BaseModel):
    narrative: str

class ClassifierResponse(BaseModel):
    main_category: str
    sub_category: str
    intervention: str
    priority: str
    confidence_scores: ConfidenceScores
    chunks_processed: int
    chunk_predictions: Optional[List[ChunkPrediction]] = None
    processing_time: float
    model_info: dict
    timestamp: str 

@router.post("/classify", response_model=ClassifierResponse)
async def classify_narrative(request: ClassifierRequest):
    """Classify case narrative into categories"""
    
    # Check if classifier model is loaded
    if not model_loader.is_model_ready("classifier_model"):
        raise HTTPException(
            status_code=503, 
            detail="Classifier model not ready. Check /health/models for status."
        )
    
    if not request.narrative.strip():
        raise HTTPException(
            status_code=400,
            detail="Narrative input cannot be empty"
        )
    
    try:
        start_time = datetime.now()
        
        # Get the loaded classifier model
        classifier = model_loader.models.get("classifier_model")
        if not classifier:
            raise HTTPException(
                status_code=503,
                detail="Classifier model not available"
            )
        
        # Initialize chunker with configuration
        tokenizer_name = "distilbert-base-uncased"

        # Initialize chunker with configuration
        chunker = ClassificationChunker(
            tokenizer_name=tokenizer_name,
            max_tokens=512,
            overlap_tokens=150
        )
        
        # Count tokens
        token_count = chunker.count_tokens(request.narrative)
        MAX_SOURCE_LENGTH = 512
        
        logger.info(f"🔍 Classification request: {token_count} tokens")
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct classification for short text
            logger.info("✅ Text within limit, processing directly (no chunking)")
            classification = classifier.classify(request.narrative)
            
            # Format single response as if it were aggregated
            aggregated_result = {
                'main_category': classification['main_category'],
                'sub_category': classification['sub_category'],
                'intervention': classification['intervention'],
                'priority': classification['priority'],
                'confidence_scores': classification.get('confidence_scores', {
                    'main_category': 0.0,
                    'sub_category': 0.0,
                    'intervention': 0.0,
                    'priority': 0.0
                }),
                'chunks_processed': 1,
                'chunk_predictions': None
            }
        else:
            # Chunking needed for long text
            logger.info(f"📦 Chunking required: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            # Create chunks
            chunks = chunker.chunk_transcript(request.narrative)
            logger.info(f"📊 Created {len(chunks)} chunks with 150 token overlap")
            
            # Log chunk information
            for chunk in chunks:
                logger.debug(
                    f"  Chunk {chunk['chunk_index'] + 1}: "
                    f"{chunk['token_count']} tokens, "
                    f"{chunk['sentence_count']} sentences, "
                    f"position: {chunk['position_ratio']:.2%}"
                )
            
            # Classify each chunk
            chunk_predictions = []
            for i, chunk_info in enumerate(chunks):
                logger.info(f"🔄 Processing chunk {i + 1}/{len(chunks)}")
                
                chunk_classification = classifier.classify(chunk_info['text'])
                
                # Build chunk prediction with metadata
                chunk_pred = {
                    'main_category': chunk_classification['main_category'],
                    'sub_category': chunk_classification['sub_category'],
                    'intervention': chunk_classification['intervention'],
                    'priority': chunk_classification['priority'],
                    'confidence_scores': chunk_classification.get('confidence_scores', {
                        'main_category': 0.0,
                        'sub_category': 0.0,
                        'intervention': 0.0,
                        'priority': 0.0
                    })
                }
                chunk_predictions.append(chunk_pred)
                
                # Log chunk classification
                logger.info(
                    f"  ✓ Chunk {i + 1}: "
                    f"Category={chunk_pred['main_category']}, "
                    f"Sub={chunk_pred['sub_category']}, "
                    f"Priority={chunk_pred['priority']}, "
                    f"Confidence={chunk_pred['confidence_scores']['main_category']:.3f}"
                )
            
            # Aggregate predictions using confidence-weighted voting
            logger.info("🔗 Aggregating chunk predictions with confidence weighting")
            aggregator = ClassificationAggregator()
            aggregated_result = aggregator.aggregate_case_classification(chunk_predictions)
            aggregated_result['chunks_processed'] = len(chunks)
            
            # Log aggregation results
            logger.info(
                f"📈 Aggregated result: "
                f"Category={aggregated_result['main_category']}, "
                f"Sub={aggregated_result['sub_category']}, "
                f"Priority={aggregated_result['priority']}"
            )
            logger.info(
                f"   Confidence scores: "
                f"Main={aggregated_result['confidence_scores']['main_category']:.3f}, "
                f"Sub={aggregated_result['confidence_scores']['sub_category']:.3f}, "
                f"Int={aggregated_result['confidence_scores']['intervention']:.3f}, "
                f"Pri={aggregated_result['confidence_scores']['priority']:.3f}"
            )
            
            # Create chunk prediction objects for response
            chunk_pred_objects = []
            for i, chunk in enumerate(chunks):
                chunk_pred_obj = ChunkPrediction(
                    chunk_index=chunk['chunk_index'],
                    token_count=chunk['token_count'],
                    sentence_count=chunk['sentence_count'],
                    position_ratio=chunk['position_ratio'],
                    main_category=chunk_predictions[i]['main_category'],
                    sub_category=chunk_predictions[i]['sub_category'],
                    intervention=chunk_predictions[i]['intervention'],
                    priority=chunk_predictions[i]['priority'],
                    confidence_scores=ConfidenceScores(
                        **chunk_predictions[i]['confidence_scores']
                    )
                )
                chunk_pred_objects.append(chunk_pred_obj)
            
            aggregated_result['chunk_predictions'] = chunk_pred_objects
        
        processing_time = (datetime.now() - start_time).total_seconds()
        

        # # Classify narrative
        # classification = classifier.classify(request.narrative)
        
        # processing_time = (datetime.now() - start_time).total_seconds()
        
        # Get model info
        model_info = classifier.get_model_info()
        
        logger.info(f"✅ Classification complete: "
                    f"{len(request.narrative)} chars, "
                    f"{aggregated_result['chunks_processed']} chunks, "
                    f"{processing_time:.3f}s"
                )   
             
        return ClassifierResponse(
            main_category=aggregated_result['main_category'],
            sub_category=aggregated_result['sub_category'],
            intervention=aggregated_result['intervention'],
            priority=aggregated_result['priority'],
            confidence_scores=ConfidenceScores(
                **aggregated_result['confidence_scores']
            ),
            chunks_processed=aggregated_result['chunks_processed'],
            chunk_predictions=aggregated_result.get('chunk_predictions'),
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )

@router.get("/info")
async def get_classifier_info():
    """Get classifier model information"""
    if not model_loader.is_model_ready("classifier_model"):
        return {
            "status": "not_ready",
            "message": "Classifier model not loaded"
        }

    classifier = model_loader.models.get("classifier_model")
    if classifier:
        model_info = classifier.get_model_info()
        return {
            "status": "ready",
            "model_info": model_info
        }
    else:
        return {
            "status": "error",
            "message": "Classifier model not found",
            "model_info": {"error": "Model instance not found"}
        }

@router.post("/demo")
async def classifier_demo():
    """Demo endpoint with sample narrative"""
    demo_narrative = (
        "On 2023-05-15 a girl (age 16) from District X called to report sexual abuse by her stepfather. "
        "She is currently 2 months pregnant and being forced to abort. The stepfather has threatened to "
        "kill her if she doesn't comply. Her mother is also being abused."
    )
    
    request = ClassifierRequest(narrative=demo_narrative)
    return await classify_narrative(request)