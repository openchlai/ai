"""
API endpoints for agent feedback on model predictions
"""
import logging
from datetime import datetime
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..db.repositories.feedback_repository import FeedbackRepository
from ..db.models import AgentFeedback

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agent-feedback", tags=["Agent Feedback"])


# Request/Response Models
class FeedbackUpdateRequest(BaseModel):
    """Request model for updating feedback"""
    call_id: str = Field(..., description="Unique call identifier")
    task: str = Field(..., description="Task type (classification, ner, summarization, etc.)")
    feedback: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    reason: Optional[str] = Field(None, description="Optional explanation for the rating")
    
    @validator('task')
    def validate_task(cls, v):
        valid_tasks = ['transcription', 'classification', 'ner', 'summarization', 'translation', 'qa']
        if v not in valid_tasks:
            raise ValueError(f"Task must be one of: {', '.join(valid_tasks)}")
        return v


class FeedbackResponse(BaseModel):
    """Response model for feedback operations"""
    id: int
    call_id: str
    task: str
    prediction: Any  # Changed from dict to Any for better JSON handling
    feedback: Optional[int]
    reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    processing_mode: Optional[str] = None
    model_version: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FeedbackStatisticsResponse(BaseModel):
    """Response model for feedback statistics"""
    period_days: int
    tasks: dict


# API Endpoints
@router.post("/update", response_model=FeedbackResponse, status_code=200)
async def update_feedback(
    request: FeedbackUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update feedback for a specific call and task.
    This endpoint is called by the agent interface after reviewing results.

    - **call_id**: Unique identifier for the call
    - **task**: Type of task being rated (classification, ner, summarization, etc.)
    - **feedback**: Rating from 1-5 (1=poor, 5=excellent)
    - **reason**: Optional explanation for the rating
    """
    try:
        feedback = FeedbackRepository.update_feedback(
            db=db,
            call_id=request.call_id,
            task=request.task,
            feedback_rating=request.feedback,
            reason=request.reason
        )

        if not feedback:
            raise HTTPException(
                status_code=404,
                detail=f"Feedback entry not found for call_id={request.call_id}, task={request.task}"
            )

        # Refresh the object to ensure all fields are loaded
        db.refresh(feedback)

        # Convert to dict for safe serialization
        response_data = {
            "id": feedback.id,
            "call_id": feedback.call_id,
            "task": feedback.task,
            "prediction": feedback.prediction,
            "feedback": feedback.feedback,
            "reason": feedback.reason,
            "created_at": feedback.created_at,
            "updated_at": feedback.updated_at,
            "processing_mode": feedback.processing_mode,
            "model_version": feedback.model_version
        }

        return jsonable_encoder(response_data)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Failed to update feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update feedback: {str(e)}")


@router.get("/call/{call_id}", response_model=List[FeedbackResponse])
async def get_call_feedback(
    call_id: str,
    task: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve feedback entries for a specific call.
    Optionally filter by task type.
    
    - **call_id**: Unique identifier for the call
    - **task**: Optional task filter
    """
    try:
        feedbacks = FeedbackRepository.get_feedback(
            db=db,
            call_id=call_id,
            task=task
        )
        
        if not feedbacks:
            raise HTTPException(
                status_code=404,
                detail=f"No feedback found for call_id={call_id}"
            )
        
        return feedbacks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to retrieve feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")


@router.get("/statistics", response_model=FeedbackStatisticsResponse)
async def get_feedback_statistics(
    task: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get feedback statistics for monitoring model performance.
    
    - **task**: Optional task filter
    - **days**: Number of days to look back (default: 30)
    """
    try:
        statistics = FeedbackRepository.get_feedback_statistics(
            db=db,
            task=task,
            days=days
        )
        
        if 'error' in statistics:
            raise HTTPException(status_code=500, detail=statistics['error'])
        
        return statistics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for feedback system.
    Verifies database connectivity and returns system status.
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        # Get some basic stats
        from ..db.models import AgentFeedback
        from sqlalchemy import func
        
        total_feedback = db.query(func.count(AgentFeedback.id)).scalar()
        rated_feedback = db.query(func.count(AgentFeedback.id)).filter(
            AgentFeedback.feedback.isnot(None)
        ).scalar()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_feedback_entries": total_feedback,
            "rated_entries": rated_feedback,
            "rating_coverage": round(rated_feedback / total_feedback * 100, 2) if total_feedback > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Feedback system health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")