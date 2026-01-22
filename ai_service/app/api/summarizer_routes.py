from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import logging
from typing import Dict, Optional
from celery.result import AsyncResult
from ..tasks.model_tasks import summarization_summarize_task
from ..model_scripts.model_loader import model_loader
from ..utils.mode_detector import is_api_server_mode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/summarizer", tags=["summarizer"])


class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 256


class SummarizationResponse(BaseModel):
    summary: str
    processing_time: float
    model_info: Dict
    timestamp: str


class SummarizationTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: str
    status_endpoint: str


class SummarizationTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[SummarizationResponse] = None
    error: Optional[str] = None
    progress: Optional[Dict] = None


@router.post("/summarize", response_model=SummarizationTaskResponse, status_code=202)
async def summarize_text_endpoint(request: SummarizationRequest):
    """Summarize text (async via Celery)"""
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    if is_api_server_mode():
        # API Server mode - delegate to Celery worker
        # Skip local model check as models are on workers
        pass
    else:
        # Standalone mode - check local model
        if not model_loader.is_model_ready("summarizer"):
            raise HTTPException(
                status_code=503,
                detail="Summarizer model not ready. Check /health/models for status."
            )
    
    try:
        task = summarization_summarize_task.apply_async(
            args=[request.text, request.max_length],
            queue='model_processing'
        )
        
        logger.info(f"📤 Summarization task submitted: {task.id}")
        
        return SummarizationTaskResponse(
            task_id=task.id,
            status="queued",
            message="Summarization started. Check status at /summarizer/task/{task_id}",
            estimated_time="10-30 seconds",
            status_endpoint=f"/summarizer/task/{task.id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit summarization task: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit task")


@router.get("/task/{task_id}", response_model=SummarizationTaskStatusResponse)
async def get_summarization_task_status(task_id: str):
    """Get summarization task status"""
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return SummarizationTaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress={"message": "Task is queued"}
            )
        
        elif task_result.state == 'PROCESSING':
            return SummarizationTaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=task_result.info or {}
            )
        
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            
            summary_response = SummarizationResponse(
                summary=result['summary'],
                processing_time=result['processing_time'],
                model_info=result['model_info'],
                timestamp=result['timestamp']
            )
            
            return SummarizationTaskStatusResponse(
                task_id=task_id,
                status="success",
                result=summary_response
            )
        
        elif task_result.state == 'FAILURE':
            return SummarizationTaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(task_result.info)
            )
        
        else:
            return SummarizationTaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress={"message": f"Task state: {task_result.state}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking task")


@router.get("/info")
async def get_summarizer_info():
    """Get summarizer model information"""
    if is_api_server_mode():
        # API Server mode - models are on Celery workers
        return {
            "status": "api_server_mode",
            "message": "Summarizer model loaded on Celery workers",
            "model_info": {"mode": "api_server"}
        }
    else:
        # Standalone mode - check local model
        if not model_loader.is_model_ready("summarizer"):
            return {"status": "not_ready", "message": "Summarizer model not loaded"}

        summarizer_model = model_loader.models.get("summarizer")
        if summarizer_model:
            model_info = summarizer_model.get_model_info()
            return {"status": "ready", "model_info": model_info}
        return {
            "status": "error",
            "message": "Summarizer model not found",
            "model_info": {"error": "Model instance not found"}
        }


@router.post("/demo", response_model=SummarizationTaskResponse)
async def summarizer_demo():
    """Demo endpoint with sample text"""
    demo_text = (
        "Artificial intelligence (AI) refers to the simulation of human intelligence "
        "in machines that are programmed to think and learn like humans. It is a field "
        "of computer science that aims to create systems capable of performing tasks that "
        "normally require human intelligence, such as visual perception, speech recognition, "
        "decision-making, and language translation."
    )

    request = SummarizationRequest(text=demo_text, max_length=60)
    return await summarize_text_endpoint(request)

