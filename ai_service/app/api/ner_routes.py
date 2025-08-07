from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Union, Optional
import logging
from datetime import datetime

from ..models.model_loader import model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ner", tags=["ner"])

class NERRequest(BaseModel):
    text: str
    flat: bool = True  # Return flat list by default

class NEREntity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float

class NERResponse(BaseModel):
    entities: Union[List[NEREntity], Dict[str, List[str]]]
    processing_time: float
    model_info: Dict
    timestamp: str

@router.post("/extract", response_model=NERResponse)
async def extract_entities(request: NERRequest):
    """Extract named entities from text"""
    
    # Check if NER model is loaded
    if not model_loader.is_model_ready("ner"):
        raise HTTPException(
            status_code=503, 
            detail="NER model not ready. Check /health/models for status."
        )
    
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    try:
        start_time = datetime.now()
        
        # Get the loaded NER model
        ner_model = model_loader.models.get("ner")
        if not ner_model:
            raise HTTPException(
                status_code=503,
                detail="NER model not available"
            )
        
        # Extract entities
        entities = ner_model.extract_entities(request.text, flat=request.flat)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Get model info
        model_info = ner_model.get_model_info()
        
        logger.info(f"NER processed {len(request.text)} chars in {processing_time:.3f}s")
        
        return NERResponse(
            entities=entities,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"NER processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"NER processing failed: {str(e)}"
        )

@router.get("/info")
async def get_ner_info():
    """Get NER model information"""
    if not model_loader.is_model_ready("ner"):
        return {
            "status": "not_ready",
            "message": "NER model not loaded"
        }
    
    ner_model = model_loader.models.get("ner")
    if ner_model:
        return {
            "status": "ready",
            "model_info": ner_model.get_model_info()
        }
    else:
        return {
            "status": "error",
            "message": "NER model not found"
        }

@router.post("/demo")
async def ner_demo():
    """Demo endpoint with sample text"""
    demo_text = "Barack Obama was the 44th President of the United States. He was born in Honolulu, Hawaii on August 4, 1961. He served from 2009 to 2017 and worked with Michelle Obama."
    
    request = NERRequest(text=demo_text, flat=True)
    return await extract_entities(request)