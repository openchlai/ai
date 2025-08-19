from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Union, Optional
import logging
from datetime import datetime
from celery.exceptions import TimeoutError as CeleryTimeoutError

from ..tasks.inference_tasks import ner_extract_inference

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

@router.post("/extract")
async def extract_entities(request: NERRequest):
    """
    Extract named entities from text using hybrid sync/async pattern
    
    Returns:
    - 200 OK: Immediate result if processing completes within 8 seconds
    - 202 Accepted: Task started, use /task/{task_id} to check status
    """
    
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    try:
        # Start Celery task
        task = ner_extract_inference.delay(request.text, request.flat)
        
        try:
            # Try to get result quickly (8 second timeout)
            result = task.get(timeout=8)
            
            logger.info(f"🏷️ NER extraction completed immediately in {result['processing_time']:.2f}s")
            
            # Return immediate success (200 OK)
            return NERResponse(**result)
            
        except CeleryTimeoutError:
            # System is busy, return task ID for async polling (202 Accepted)
            logger.info(f"⏰ NER extraction queued, task_id: {task.id}")
            
            return JSONResponse(
                status_code=202,
                content={
                    "status": "processing",
                    "task_id": task.id,
                    "message": "System busy, processing in background",
                    "polling_url": f"/task/{task.id}",
                    "estimated_time": "15-30 seconds",
                    "request_info": {
                        "text_length": len(request.text),
                        "flat": request.flat
                    },
                    "instructions": {
                        "check_status": f"GET /task/{task.id}",
                        "cancel_task": f"DELETE /task/{task.id}"
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"❌ NER extraction task failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start NER extraction task: {str(e)}"
        )

@router.get("/info")
async def get_ner_info():
    """Get NER model information from Celery workers"""
    return {
        "status": "info_via_celery", 
        "message": "NER model info available through inference tasks",
        "usage": "Submit a NER extraction request to test model availability"
    }

@router.post("/demo")
async def ner_demo():
    """Demo endpoint with sample text"""
    demo_text = "Barack Obama was the 44th President of the United States. He was born in Honolulu, Hawaii on August 4, 1961. He served from 2009 to 2017 and worked with Michelle Obama."
    
    request = NERRequest(text=demo_text, flat=True)
    return await extract_entities(request)