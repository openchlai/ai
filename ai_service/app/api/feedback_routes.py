"""
Agent Feedback API Routes
=========================

API endpoints for handling agent feedback on call transcription quality
and triggering audio preprocessing workflows.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..tasks.audio_tasks import process_feedback_audio_task
from ..config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/feedback", tags=["agent-feedback"])


# Request/Response Models
class TranscriptionRatingRequest(BaseModel):
    """Request model for agent transcription rating"""
    call_id: str = Field(..., description="Unique call identifier")
    agent_id: str = Field(..., description="Agent identifier who provided feedback")
    quality_rating: str = Field(..., description="Quality rating: 'good' or 'bad'")
    feedback_notes: Optional[str] = Field(None, description="Optional feedback notes from agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "call_id": "1668327648.27104",
                "agent_id": "agent_001",
                "quality_rating": "bad",
                "feedback_notes": "Audio quality poor, lots of background noise making transcription difficult"
            }
        }


class FeedbackTaskResponse(BaseModel):
    """Response model for feedback task creation"""
    success: bool
    task_id: str
    message: str
    call_id: str
    estimated_processing_time: str
    status_endpoint: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "task_id": "12345678-1234-1234-1234-123456789012",
                "message": "Audio preprocessing task created successfully",
                "call_id": "1668327648.27104",
                "estimated_processing_time": "2-5 minutes",
                "status_endpoint": "/api/v1/feedback/status/12345678-1234-1234-1234-123456789012"
            }
        }


class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str  # pending, processing, completed, failed
    call_id: str
    progress: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "12345678-1234-1234-1234-123456789012",
                "status": "completed",
                "call_id": "1668327648.27104",
                "progress": {
                    "stage": "completed",
                    "total_chunks": 61,
                    "quality_chunks": 8,
                    "s3_uploads": 8
                },
                "result": {
                    "batch_id": "feedback_1668327648.27104_abc12345",
                    "s3_urls": ["https://bucket.s3.amazonaws.com/..."],
                    "processing_time_seconds": 7.2
                },
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:07Z"
            }
        }


class BatchResultsResponse(BaseModel):
    """Response model for batch results"""
    batch_id: str
    call_id: str
    agent_id: str
    total_chunks: int
    quality_chunks: int
    s3_urls: list[str]
    processing_time_seconds: float
    created_at: str
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "feedback_1668327648.27104_abc12345",
                "call_id": "1668327648.27104",
                "agent_id": "agent_001",
                "total_chunks": 61,
                "quality_chunks": 8,
                "s3_urls": ["https://bucket.s3.amazonaws.com/feedback-chunks/1668327648.27104/chunk_1.wav"],
                "processing_time_seconds": 7.2,
                "created_at": "2025-01-15T10:30:00Z",
                "status": "completed"
            }
        }


@router.post("/transcription-rating", response_model=FeedbackTaskResponse)
async def submit_transcription_rating(
    request: TranscriptionRatingRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit agent rating for call transcription quality.
    If rating is 'bad', triggers audio preprocessing workflow.
    """
    
    if not settings.enable_feedback_preprocessing:
        raise HTTPException(
            status_code=503, 
            detail="Feedback preprocessing is currently disabled"
        )
    
    # Validate quality rating
    if request.quality_rating not in ["good", "bad"]:
        raise HTTPException(
            status_code=400,
            detail="quality_rating must be either 'good' or 'bad'"
        )
    
    logger.info(f"Received transcription rating from {request.agent_id} for call {request.call_id}: {request.quality_rating}")
    
    # If rating is good, just log and return success
    if request.quality_rating == "good":
        return FeedbackTaskResponse(
            success=True,
            task_id="no-processing-needed",
            message="Feedback recorded. No preprocessing needed for good quality rating.",
            call_id=request.call_id,
            estimated_processing_time="N/A",
            status_endpoint="N/A"
        )
    
    # If rating is bad, trigger preprocessing workflow
    try:
        # Create Celery task for audio preprocessing
        task = process_feedback_audio_task.delay(
            call_id=request.call_id,
            agent_id=request.agent_id,
            feedback_notes=request.feedback_notes or ""
        )
        
        logger.info(f"Created preprocessing task {task.id} for call {request.call_id}")
        
        return FeedbackTaskResponse(
            success=True,
            task_id=task.id,
            message="Audio preprocessing task created successfully. Poor quality audio will be processed and uploaded to Label Studio.",
            call_id=request.call_id,
            estimated_processing_time="2-5 minutes",
            status_endpoint=f"/api/v1/feedback/status/{task.id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to create preprocessing task for call {request.call_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create preprocessing task: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get status of audio preprocessing task
    """
    
    if task_id == "no-processing-needed":
        raise HTTPException(
            status_code=400,
            detail="No task created - transcription was rated as good quality"
        )
    
    try:
        # Get task from Celery
        from ..celery_app import celery_app
        task = celery_app.AsyncResult(task_id)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        # Build response based on task state
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
        
        # Get task info
        task_info = task.info or {}
        call_id = task_info.get('call_id', 'unknown')
        
        # Build progress info
        progress = {
            "stage": task.state.lower(),
            "message": task_info.get('message', ''),
        }
        
        # Add result if completed
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
            created_at=datetime.now().isoformat(),  # Would ideally come from task metadata
            updated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task status: {str(e)}"
        )


@router.get("/batch/{batch_id}/results", response_model=BatchResultsResponse)
async def get_batch_results(batch_id: str):
    """
    Get results for a specific preprocessing batch
    """
    
    try:
        # This would typically query a database for batch results
        # For now, return a placeholder response
        # In a full implementation, you'd query the preprocessing database
        
        logger.info(f"Retrieving batch results for {batch_id}")
        
        # TODO: Implement database query for batch results
        # This is a placeholder implementation
        raise HTTPException(
            status_code=501,
            detail="Batch results endpoint not yet implemented. Use task status endpoint instead."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch results for {batch_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving batch results: {str(e)}"
        )


@router.get("/health")
async def feedback_health_check():
    """
    Health check for feedback service
    """
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