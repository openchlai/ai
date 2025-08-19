from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import logging
from celery.exceptions import TimeoutError as CeleryTimeoutError

from ..tasks.inference_tasks import translator_inference

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translate", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    translated: str
    processing_time: float
    model_info: Dict
    timestamp: str

@router.post("/")
async def translate_text(request: TranslationRequest):
    """
    Translate text using hybrid sync/async pattern
    
    Returns:
    - 200 OK: Immediate result if processing completes within 12 seconds
    - 202 Accepted: Task started, use /task/{task_id} to check status
    """

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    try:
        # Start Celery task
        task = translator_inference.delay(request.text)
        
        try:
            # Try to get result quickly (12 second timeout)
            result = task.get(timeout=12)
            
            logger.info(f"📝 Translation completed immediately in {result['processing_time']:.2f}s")
            
            # Return immediate success (200 OK)
            return TranslationResponse(**result)
            
        except CeleryTimeoutError:
            # System is busy, return task ID for async polling (202 Accepted)
            logger.info(f"⏰ Translation queued, task_id: {task.id}")
            
            return JSONResponse(
                status_code=202,
                content={
                    "status": "processing",
                    "task_id": task.id,
                    "message": "System busy, processing in background",
                    "polling_url": f"/task/{task.id}",
                    "estimated_time": "20-40 seconds",
                    "request_info": {
                        "text_length": len(request.text)
                    },
                    "instructions": {
                        "check_status": f"GET /task/{task.id}",
                        "cancel_task": f"DELETE /task/{task.id}"
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Translation task failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start translation task: {str(e)}"
        )

@router.get("/info")
async def get_translation_info():
    """Get translation model information from Celery workers"""
    return {
        "status": "info_via_celery", 
        "message": "Translation model info available through inference tasks",
        "usage": "Submit a translation request to test model availability"
    }
