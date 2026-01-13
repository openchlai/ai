import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from ..tasks.model_tasks import qa_evaluate_task
from ..model_scripts.model_loader import model_loader
from ..model_scripts.qa_model import qa_model
from ..utils.mode_detector import is_api_server_mode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/qa", tags=["quality_assurance"])


class QARequest(BaseModel):
    transcript: str = Field(..., min_length=10)
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    return_raw: bool = Field(False)


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
    # chunk_info: Optional[Dict] = None


class QATaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: str
    status_endpoint: str


class QATaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[QAResponse] = None
    error: Optional[str] = None
    progress: Optional[Dict] = None


@router.post("/evaluate", response_model=QATaskResponse)
async def evaluate_transcript(request: QARequest):
    """Evaluate transcript (async via Celery)"""
    
    if is_api_server_mode():
        # API Server mode - delegate to Celery worker
        # Skip local model check as models are on workers
        pass
    else:
        # Standalone mode - check local model
        from ..model_scripts.qa_model import qa_model
        if not qa_model.is_ready():
            raise HTTPException(
                status_code=503, 
                detail="QA model not ready. Check /health/models for status."
            )
    
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    
    try:
        task = qa_evaluate_task.apply_async(
            args=[request.transcript, request.threshold, request.return_raw],
            queue='model_processing'
        )
        
        logger.info(f"📤 QA evaluation task submitted: {task.id}")
        
        return QATaskResponse(
            task_id=task.id,
            status="queued",
            message="QA evaluation started. Check status at /qa/task/{task_id}",
            estimated_time="15-45 seconds",
            status_endpoint=f"/qa/task/{task.id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit QA task: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit task")


@router.get("/task/{task_id}", response_model=QATaskStatusResponse)
async def get_qa_task_status(task_id: str):
    """Get QA evaluation task status"""
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return QATaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress={"message": "Task is queued"}
            )
        
        elif task_result.state == 'PROCESSING':
            return QATaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=task_result.info or {}
            )
        
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            
            qa_response = QAResponse(
                evaluations=result['evaluations'],
                processing_time=result['processing_time'],
                model_info=result['model_info'],
                timestamp=result['timestamp'],
                # chunk_info=result.get('chunk_info')
            )
            
            return QATaskStatusResponse(
                task_id=task_id,
                status="success",
                result=qa_response
            )
        
        elif task_result.state == 'FAILURE':
            return QATaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(task_result.info)
            )
        
        else:
            return QATaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress={"message": f"Task state: {task_result.state}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking task")

@router.get("/info")
async def get_qa_info():
    """Get QA model information"""
    if is_api_server_mode():
        # API Server mode - models are on Celery workers
        return {"status": "api_server_mode", "message": "QA model loaded on Celery workers", "model_info": {"mode": "api_server"}}
    else:
        # Standalone mode - check local model
        if not qa_model.is_ready():
            # Return the error from the model if loading failed
            return {"status": "not_ready", "message": "QA model not loaded", "model_info": qa_model.get_model_info()}
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