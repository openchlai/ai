# app/api/ner_routes.py - Updated with Celery Task Management
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Union, Optional
import logging
from datetime import datetime
from celery.result import AsyncResult

from ..tasks.model_tasks import ner_extract_task
from ..model_scripts.model_loader import model_loader
from ..utils.mode_detector import is_api_server_mode, get_execution_mode

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


class NERTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: str
    status_endpoint: str


class NERTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[NERResponse] = None
    error: Optional[str] = None
    progress: Optional[Dict] = None


@router.post("/extract", response_model=NERTaskResponse)
async def extract_entities(request: NERRequest):
    """
    Extract named entities from text (async via Celery)
    
    Returns task_id immediately for status checking
    """
    
    # Mode-aware validation: only check local models in standalone mode
    if not is_api_server_mode():
        # In standalone mode, check if local model is ready
        if not model_loader.is_model_ready("ner"):
            raise HTTPException(
                status_code=503, 
                detail="NER model not ready. Check /health/models for status."
            )
    # In API server mode, skip local model check - models are on workers
    
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    try:
        # Submit task to Celery
        task = ner_extract_task.apply_async(
            args=[request.text, request.flat],
            queue='model_processing'
        )
        
        logger.info(f"📤 NER task submitted: {task.id}")
        
        return NERTaskResponse(
            task_id=task.id,
            status="queued",
            message="NER processing started. Check status at /ner/task/{task_id}",
            estimated_time="5-15 seconds",
            status_endpoint=f"/ner/task/{task.id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit NER task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit NER task: {str(e)}"
        )


@router.get("/task/{task_id}", response_model=NERTaskStatusResponse)
async def get_ner_task_status(task_id: str):
    """
    Get the status of an NER processing task
    
    Status values:
    - PENDING: Task is waiting to be processed
    - PROCESSING: Task is currently being processed
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed with an error
    """
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return NERTaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress={"message": "Task is queued and waiting to be processed"}
            )
        
        elif task_result.state == 'PROCESSING':
            progress_info = task_result.info or {}
            return NERTaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=progress_info
            )
        
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            
            # Convert result to NERResponse format
            ner_response = NERResponse(
                entities=result['entities'],
                processing_time=result['processing_time'],
                model_info=result['model_info'],
                timestamp=result['timestamp']
            )
            
            return NERTaskStatusResponse(
                task_id=task_id,
                status="success",
                result=ner_response
            )
        
        elif task_result.state == 'FAILURE':
            error_msg = str(task_result.info)
            logger.error(f"NER task {task_id} failed: {error_msg}")
            
            return NERTaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=error_msg
            )
        
        else:
            return NERTaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress={"message": f"Task state: {task_result.state}"}
            )
            
    except Exception as e:
        logger.error(f"Error checking NER task status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking task status: {str(e)}"
        )


@router.get("/info")
async def get_ner_info():
    """Get NER model information"""
    if is_api_server_mode():
        # API Server mode - models are on Celery workers
        return {
            "status": "api_server_mode",
            "message": "NER model loaded on Celery workers",
            "model_info": {"mode": "api_server"},
            "task_management": "enabled",
            "queue": "model_processing"
        }
    else:
        # Standalone mode - check local model
        if not model_loader.is_model_ready("ner"):
            return {
                "status": "not_ready",
                "message": "NER model not loaded"
            }

        ner_model = model_loader.models.get("ner")
        if ner_model:
            model_info = ner_model.get_model_info()
            return {
                "status": "ready",
                "model_info": model_info,
                "task_management": "enabled",
                "queue": "model_processing"
            }
        else:
            return {
                "status": "error",
                "message": "NER model not found",
                "model_info": {"error": "Model instance not found"}
            }


@router.post("/demo")
async def ner_demo():
    """Demo endpoint with sample text"""
    demo_text = (
        "On 2023-05-15 a girl (age 16) from District X called to report sexual abuse. "
        "The incident occurred in Nairobi, Kenya. Contact John Doe at john@example.com "
        "or call +254712345678 for more information."
    )
    
    request = NERRequest(text=demo_text, flat=True)
    return await extract_entities(request)