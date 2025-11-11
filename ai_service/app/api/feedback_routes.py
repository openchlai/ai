import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..tasks.audio_tasks import process_feedback_audio_task
from ..config.settings import settings
from ..db.session import SessionLocal
from ..db.models import ModelFeedback, PipelineTask

logger = logging.getLogger(__name__)  
router = APIRouter(prefix="/feedback", tags=["agent-feedback"])

# In-memory storage and counter used by the no-database feedback endpoints
feedback_storage: List[Dict[str, Any]] = []
feedback_counter: int = 1

# DB Dependency

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

# Request/Response Models

class TranscriptionRatingRequest(BaseModel):
    call_id: str
    agent_id: str
    quality_rating: str
    feedback_notes: Optional[str] = None

class FeedbackTaskResponse(BaseModel):
    success: bool
    task_id: str
    message: str
    call_id: str
    estimated_processing_time: str
    status_endpoint: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    call_id: str
    progress: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

class BatchResultsResponse(BaseModel):
    batch_id: str
    call_id: str
    agent_id: str
    total_chunks: int
    quality_chunks: int
    s3_urls: list[str]
    processing_time_seconds: float
    created_at: str
    status: str

class ModelFeedbackCreate(BaseModel):
    task_id: str
    model_name: str
    rating: int = Field(..., ge=1, le=5)
    reason: Optional[str] = None

class ModelFeedbackBatchCreate(BaseModel):
    task_id: str
    feedbacks: List[ModelFeedbackCreate]

class ModelFeedbackResponse(BaseModel):
    id: int
    task_id: str
    model_name: str
    rating: int
    reason: Optional[str]
    created_at: datetime

    class Config:  
        orm_mode = True

# Model Feedback Routes
@router.post("/model-feedback", response_model=ModelFeedbackResponse)
async def submit_model_feedback(feedback: ModelFeedbackCreate):
    """
    Submit feedback for a specific AI model result - without database
    """
    try:
        # Create proper mock response with required fields
        mock_response = ModelFeedbackResponse(
            id=1,  # Provide an integer ID
            task_id=feedback.task_id,
            model_name=feedback.model_name,
            rating=feedback.rating,
            reason=feedback.reason,
            created_at=datetime.now()  # Provide a datetime object
        )
        logger.info(f"Mock saved model feedback for {feedback.model_name} (task {feedback.task_id})")
        return mock_response

    except Exception as e:
        logger.error(f"Error saving model feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/model-feedback/batch")
async def submit_batch_model_feedback(batch: ModelFeedbackBatchCreate):
    """
    Submit feedback for all models in a completed pipeline task.
    """
    global feedback_counter
    
    try:
        # task = db.query(PipelineTask).filter(PipelineTask.task_id == batch.task_id).first()
        # if not task:
        #     raise HTTPException(status_code=404, detail=f"Pipeline task {batch.task_id} not found")

        feedback_ids = []
        for item in batch.feedbacks:
            feedback_id = feedback_counter
            feedback_counter += 1
            
            feedback_record = {
                "id": feedback_id,
                "task_id": batch.task_id,
                "model_name": item.model_name,
                "rating": item.rating,
                "reason": item.reason,
                "created_at": datetime.now()
            }
            
            feedback_storage.append(feedback_record)
            feedback_ids.append(feedback_id)

        logger.info(f"Saved {len(feedback_ids)} feedback records for task {batch.task_id}")
        return {
            "success": True, 
            "count": len(feedback_ids), 
            "task_id": batch.task_id, 
            "feedback_ids": feedback_ids
        }

    except Exception as e:
        logger.error(f"Batch feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    if task_id == "no-processing-needed":
        raise HTTPException(status_code=400, detail="No task created - transcription was rated as good quality")

    try:
        from ..celery_app import celery_app
        task = celery_app.AsyncResult(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        status_mapping = {
            'PENDING': 'pending',
            'STARTED': 'processing',
            'PROGRESS': 'processing',
            'SUCCESS': 'completed',
            'FAILURE': 'failed',
            'RETRY': 'processing',
            'REVOKED': 'failed'
        }
        status = status_mapping.get(task.state, 'unknown')
        task_info = task.info or {}
        call_id = task_info.get('call_id', 'unknown')

        progress = {"stage": task.state.lower(), "message": task_info.get('message', '')}
        result = None
        if task.state == 'SUCCESS':
            result = task_info
            progress.update({
                "total_chunks": task_info.get('total_chunks', 0),
                "quality_chunks": task_info.get('quality_chunks', 0),
                "s3_uploads": len(task_info.get('s3_urls', []))
            })
        elif task.state == 'FAILURE':
            progress["error"] = str(task_info)

        return TaskStatusResponse(
            task_id=task_id,
            status=status,
            call_id=call_id,
            progress=progress,
            result=result,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")

@router.get("/health")
async def feedback_health_check():
    return {
        "service": "agent-feedback",
        "status": "healthy",
        "preprocessing_enabled": settings.enable_feedback_preprocessing,
        "s3_configured": bool(settings.aws_access_key_id and settings.s3_bucket_name),
        "thresholds": {
            "stage1": {
                "speech_ratio": settings.stage1_speech_ratio_threshold,
                "vad_snr": settings.stage1_vad_snr_threshold
            },
            "stage2": {
                "speech_ratio": settings.stage2_speech_ratio_threshold,
                "vad_snr": settings.stage2_vad_snr_threshold
            }
        }
    }
