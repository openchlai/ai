from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from ..model_scripts.model_loader import model_loader
from ..utils.text_utils import TranslationChunker
from ..utils.mode_detector import is_api_server_mode

from typing import Dict, Optional
import logging
from celery.result import AsyncResult
from ..tasks.model_tasks import translation_translate_task


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translate", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str


class TranslationResponse(BaseModel):
    translated: str
    processing_time: float
    model_info: Dict
    timestamp: str


class TranslationTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: str
    status_endpoint: str


class TranslationTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[TranslationResponse] = None
    error: Optional[str] = None
    progress: Optional[Dict] = None


@router.post("/", response_model=TranslationTaskResponse)
async def translate_text(request: TranslationRequest):
    """Translate text (async via Celery)"""
    
    # Mode-aware model readiness check
    if not is_api_server_mode():
        # In standalone mode, check local model readiness
        if not model_loader.is_model_ready("translator"):
            raise HTTPException(
                status_code=503,
                detail="Translation model not ready. Check /health/models for status."
            )
    # In API server mode, models are on workers - no local check needed
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    try:
        task = translation_translate_task.apply_async(
            args=[request.text],
            queue='model_processing'
        )
        
        logger.info(f"📤 Translation task submitted: {task.id}")
        
        return TranslationTaskResponse(
            task_id=task.id,
            status="queued",
            message="Translation started. Check status at /translate/task/{task_id}",
            estimated_time="5-20 seconds",
            status_endpoint=f"/translate/task/{task.id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit translation task: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit task")


@router.get("/task/{task_id}", response_model=TranslationTaskStatusResponse)
async def get_translation_task_status(task_id: str):
    """Get translation task status"""
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return TranslationTaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress={"message": "Task is queued"}
            )
        
        elif task_result.state == 'PROCESSING':
            return TranslationTaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=task_result.info or {}
            )
        
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            
            translation_response = TranslationResponse(
                translated=result['translated'],
                processing_time=result['processing_time'],
                model_info=result['model_info'],
                timestamp=result['timestamp']
            )
            
            return TranslationTaskStatusResponse(
                task_id=task_id,
                status="success",
                result=translation_response
            )
        
        elif task_result.state == 'FAILURE':
            return TranslationTaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(task_result.info)
            )
        
        else:
            return TranslationTaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress={"message": f"Task state: {task_result.state}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking task")

@router.get("/info")
async def get_translation_info():
    if is_api_server_mode():
        # In API server mode, models are on Celery workers
        return {
            "status": "api_server_mode",
            "message": "Translation model available on Celery workers",
            "mode": "api_server",
            "model_info": {
                "name": "Translation Model",
                "location": "celery_workers",
                "note": "Model loaded on worker nodes"
            }
        }
    else:
        # In standalone mode, check local model
        if not model_loader.is_model_ready("translator"):
            return {
                "status": "not_ready",
                "message": "Translation model not loaded",
                "mode": "standalone"
            }

        translator_model = model_loader.models.get("translator")
        if translator_model:
            model_info = translator_model.get_model_info()
            return {
                "status": "ready",
                "mode": "standalone",
                "model_info": model_info
            }
        else:
            return {
                "status": "error",
                "message": "Translation model not found",
                "mode": "standalone",
                "model_info": {"error": "Model instance not found"}
            }

@router.post("/demo")
async def translation_demo():
    """Demo endpoint for translation"""

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

    request = TranslationRequest(text=demo_transcript)
    return await translate_text(request)
    # return demo_transcript
