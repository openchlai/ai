import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..model_scripts.qa_model import qa_model
from ..utils.text_utils import ClassificationChunker, ClassificationAggregator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/qa", tags=["quality_assurance"])

# --- Pydantic Models ---
class QARequest(BaseModel):
    transcript: str = Field(..., min_length=10, description="The call center transcript to be evaluated.")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Classification threshold. Uses model default if not provided.")
    return_raw: bool = Field(False, description="If true, include raw prediction probabilities in the response.")

class SubmetricResult(BaseModel):
    submetric: str
    prediction: bool
    score: str
    probability: Optional[float] = None

class QAResponse(BaseModel):
    evaluations: Dict[str, List[SubmetricResult]]
    processing_time: float
    model_info: dict
    timestamp: str
    chunk_info: Optional[Dict] = None  # Add chunking metadata


    chunk_info: Optional[Dict] = None  # Add chunking metadata

# --- Helper Functions ---
def _log_aggregation_details(chunk_predictions: List[Dict], aggregated_result: Dict):
    """Log detailed information about the aggregation process"""
    
    # Calculate chunk-level statistics
    total_chunks = len(chunk_predictions)
    
    for category, aggregated_metrics in aggregated_result['predictions'].items():
        logger.info(f" Aggregation results for {category}:")
        
        for metric in aggregated_metrics:
            metric_name = metric['submetric']
            
            # Collect predictions and probabilities from all chunks
            chunk_predictions_list = []
            chunk_probabilities = []
            
            for chunk_idx, chunk_pred in enumerate(chunk_predictions):
                if category in chunk_pred and isinstance(chunk_pred[category], list):
                    for chunk_metric in chunk_pred[category]:
                        if chunk_metric['submetric'] == metric_name:
                            chunk_predictions_list.append(chunk_metric['prediction'])
                            chunk_probabilities.append(chunk_metric.get('probability', 0.5))
                            break
            
            # Calculate statistics
            true_count = sum(chunk_predictions_list)
            false_count = total_chunks - true_count
            avg_probability = sum(chunk_probabilities) / len(chunk_probabilities) if chunk_probabilities else 0
            
            logger.info(f"    {metric_name}:")
            logger.info(f"      Final: {metric['prediction']} (p={metric['probability']:.3f})")
            logger.info(f"      Chunk votes: {true_count}/{total_chunks} True")
            logger.info(f"      Avg probability: {avg_probability:.3f}")

def _fallback_aggregation(chunk_predictions: List[Dict]) -> Dict:
    """Fallback aggregation strategy if primary method fails"""
    
    if not chunk_predictions:
        return {}
    
    # Simple majority voting fallback
    aggregated_result = {}
    
    # Get all categories from first chunk
    first_chunk = chunk_predictions[0]
    
    for category, metrics in first_chunk.items():
        if not isinstance(metrics, list):
            continue
            
        aggregated_result[category] = []
        
        for metric_idx, metric_template in enumerate(metrics):
            metric_name = metric_template['submetric']
            
            # Collect predictions across chunks
            predictions = []
            probabilities = []
            
            for chunk_pred in chunk_predictions:
                if category in chunk_pred and isinstance(chunk_pred[category], list):
                    if metric_idx < len(chunk_pred[category]):
                        chunk_metric = chunk_pred[category][metric_idx]
                        if chunk_metric['submetric'] == metric_name:
                            predictions.append(chunk_metric['prediction'])
                            probabilities.append(chunk_metric.get('probability', 0.5))
            
            # Majority voting
            if predictions:
                final_prediction = sum(predictions) > len(predictions) / 2
                avg_probability = sum(probabilities) / len(probabilities)
                
                aggregated_result[category].append({
                    'submetric': metric_name,
                    'prediction': final_prediction,
                    'score': '✓' if final_prediction else '✗',
                    'probability': float(avg_probability)
                })
    
    return aggregated_result



# --- API Endpoints ---
@router.post("/evaluate", response_model=QAResponse)
async def evaluate_transcript(request: QARequest):
    """Evaluate call center transcript against QA metrics"""
    
    if not qa_model.is_ready():
        raise HTTPException(
            status_code=503, 
            detail="QA model not ready. Check /health/models for status."
        )
    
    if not request.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty"
        )
    
    try:
        start_time = datetime.now()
        
        # evaluation = qa_model.predict(
        #     request.transcript,
        #     threshold=request.threshold,
        #     return_raw=request.return_raw
        # )
        # Initialize chunker
        tokenizer_name = "distilbert-base-uncased" 
        chunker = ClassificationChunker(
            tokenizer_name=tokenizer_name,
            max_tokens=512,
            overlap_tokens=150  # Important for context preservation in QA
        )
        
        # Count tokens to decide if chunking is needed
        token_count = chunker.count_tokens(request.transcript)
        MAX_SOURCE_LENGTH = 512
        
        chunk_info = {
            "total_chunks": 1,
            "token_count": token_count,
            "chunking_applied": False,
            "chunk_predictions": []
        }
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct evaluation for short text
            logger.info(f" QA evaluation - no chunking needed: {token_count} tokens")
            evaluation_result = qa_model.predict(
                request.transcript,
                threshold=request.threshold,
                return_raw=request.return_raw
            )
        else:
            # Chunking needed for long text
            logger.info(f"📦 Applying QA chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            # Create chunks with overlap for context preservation
            chunks = chunker.chunk_transcript(request.transcript)
            chunk_info.update({
                "total_chunks": len(chunks),
                "chunking_applied": True,
                "chunk_details": [{
                    "chunk_index": chunk['chunk_index'],
                    "token_count": chunk['token_count'],
                    "sentence_count": chunk['sentence_count']
                } for chunk in chunks]
            })
            
            # Run QA evaluation on each chunk
            chunk_predictions = []
            for i, chunk_info_item in enumerate(chunks):
                logger.info(f"  Processing chunk {i+1}/{len(chunks)}: {chunk_info_item['token_count']} tokens")
                
                chunk_result = qa_model.predict(
                    chunk_info_item['text'],
                    threshold=request.threshold,
                    return_raw=True  # Always get raw probabilities for aggregation
                )
                
                # Store chunk prediction for monitoring
                chunk_pred_data = {
                    'chunk_index': i,
                    'token_count': chunk_info_item['token_count'],
                    'predictions': chunk_result
                }
                chunk_info['chunk_predictions'].append(chunk_pred_data)
                
                chunk_predictions.append(chunk_result)
                logger.debug(f"    Chunk {i+1} evaluation completed")
            
            # Aggregate results from all chunks
            logger.info(f" Aggregating {len(chunk_predictions)} chunk predictions")
            aggregator = ClassificationAggregator()
            aggregated_result = aggregator.aggregate_qa_scoring(chunk_predictions)
            
            if aggregated_result and aggregated_result['success']:
                evaluation_result = aggregated_result['predictions']
                chunk_info['aggregation_success'] = True
                chunk_info['aggregation_method'] = 'confidence_weighted_voting'
                
                # Log aggregation details
                _log_aggregation_details(chunk_predictions, aggregated_result)
            else:
                logger.error("QA aggregation failed, using fallback strategy")
                evaluation_result = _fallback_aggregation(chunk_predictions)
                chunk_info['aggregation_success'] = False
                chunk_info['aggregation_method'] = 'fallback_majority_voting'
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = qa_model.get_model_info()
        
        logger.info(f" QA evaluation completed: {token_count} tokens, {processing_time:.3f}s")
        
        return QAResponse(
            evaluations=evaluation_result,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat(),
            chunk_info=chunk_info
        )
        
    except Exception as e:
        logger.error(f"QA evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )

@router.get("/info")
async def get_qa_info():
    """Get QA model information"""
    if not qa_model.is_ready():
        # Return the error from the model if loading failed
        return {"status": "not_ready", "message": "QA model not loaded", "error": qa_model.error}

    return {"status": "ready", "model_info": qa_model.get_model_info()}

@router.post("/demo")
async def qa_demo():
    """Demo endpoint with sample transcript"""
    demo_transcript = (
        "Agent: Good morning! Thank you for calling TechSupport. My name is Alex. How can I help you today? "
        "Customer: Hi, I'm having issues with my internet connection. "
        "Agent: I'm sorry to hear that. Let me help you with that. Could you please tell me what exactly is happening? "
        "Customer: It keeps disconnecting every few minutes. "
        "Agent: I understand how frustrating that must be. Let me check your connection settings. "
        "Could you please hold for a moment while I investigate this? "
        "Agent: Thank you for holding. I've found the issue. "
        "I'll guide you through the steps to fix it. First, please open your network settings..."
    )
    
    request = QARequest(transcript=demo_transcript, return_raw=True)
    return await evaluate_transcript(request)

@router.post("/chunking-test")
async def qa_chunking_test():
    """Test endpoint to demonstrate chunking with a long transcript"""
    long_transcript = (
        "Agent: Good morning! Thank you for calling TechSupport. My name is Alex. How can I help you today? "
        "Customer: Hi, I'm having issues with my internet connection. It's been very unreliable lately. "
        "Agent: I'm sorry to hear that. Let me help you with that. Could you please tell me what exactly is happening? "
        "Customer: Well, it started about a week ago. The connection drops randomly, and sometimes it's very slow. "
        "I work from home, so this is really affecting my productivity. I've tried restarting the router multiple times, "
        "but the problem keeps coming back. Yesterday, I had an important video call that got disconnected three times. "
        "Agent: I understand how frustrating that must be, especially when you're working from home. "
        "Let me check your connection settings on our end. Could you please hold for a moment while I investigate this? "
        "Customer: Sure, I can hold. "
        "Agent: Thank you for holding. I can see some fluctuations in your connection signal. "
        "Let me run a more detailed diagnostic to pinpoint the issue. This might take another minute or two. "
        "Customer: That's fine, I appreciate you looking into this thoroughly. "
        "Agent: Thank you for your patience. I've found that there seems to be some interference affecting your line. "
        "I'll guide you through some troubleshooting steps to resolve this. First, please open your network settings... "
        "Customer: Okay, I'm ready. What should I do next? "
        "Agent: Please look for the Wi-Fi settings and tell me what networks you can see. "
        "We need to check if there's channel congestion from neighboring networks. "
        "Customer: I can see my network, and about five others from nearby apartments. "
        "Agent: That confirms what I suspected. There's significant channel overlap. "
        "Let's change your router's channel to a less congested one. I'll walk you through the process step by step. "
        "First, please open a web browser and type in your router's IP address..."
    ) * 3  # Repeat to ensure it's long enough for chunking
    
    request = QARequest(transcript=long_transcript, return_raw=True)
    return await evaluate_transcript(request)