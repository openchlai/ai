"""
Repository for Agent Feedback database operations
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..models import AgentFeedback

logger = logging.getLogger(__name__)


class FeedbackRepository:
    """Handles database operations for agent feedback"""
    
    @staticmethod
    def create_initial_feedback(
        db: Session,
        call_id: str,
        task: str,
        prediction: Dict[str, Any],
        processing_mode: str = None,
        model_version: str = None
    ) -> Optional[AgentFeedback]:
        """
        Create initial feedback entry when processing completes.
        Feedback rating starts as NULL until agent provides it.
        
        Args:
            db: Database session
            call_id: Unique call identifier
            task: Task type (e.g., 'classification', 'ner', 'summarization')
            prediction: The actual model prediction/output
            processing_mode: Processing mode used ('realtime', 'postcall', 'hybrid')
            model_version: Version of the model used
            
        Returns:
            Created AgentFeedback object or None if failed
        """
        try:
            feedback = AgentFeedback(
                call_id=call_id,
                task=task,
                prediction=prediction,
                feedback=None,  # NULL until agent provides feedback
                reason=None,
                processing_mode=processing_mode,
                model_version=model_version
            )
            
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            
            logger.info(f"✅ Created initial feedback entry: call_id={call_id}, task={task}")
            return feedback
            
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"⚠️ Feedback entry already exists: call_id={call_id}, task={task}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to create feedback entry: {e}")
            return None
    
    @staticmethod
    def update_feedback(
        db: Session,
        call_id: str,
        task: str,
        feedback_rating: int,
        reason: Optional[str] = None
    ) -> Optional[AgentFeedback]:
        """
        Update feedback entry with agent's rating and reason.
        
        Args:
            db: Database session
            call_id: Unique call identifier
            task: Task type
            feedback_rating: Rating from 1-5
            reason: Optional explanation for the rating
            
        Returns:
            Updated AgentFeedback object or None if not found
        """
        try:
            # Validate rating
            if not 1 <= feedback_rating <= 5:
                raise ValueError("Feedback rating must be between 1 and 5")
            
            # Find existing feedback entry
            feedback = db.query(AgentFeedback).filter(
                AgentFeedback.call_id == call_id,
                AgentFeedback.task == task
            ).first()
            
            if not feedback:
                logger.warning(f"⚠️ Feedback entry not found: call_id={call_id}, task={task}")
                return None
            
            # Update feedback
            feedback.feedback = feedback_rating
            feedback.reason = reason
            feedback.updated_at = datetime.now()
            
            db.commit()
            db.refresh(feedback)
            
            logger.info(f"✅ Updated feedback: call_id={call_id}, task={task}, rating={feedback_rating}")
            return feedback
            
        except ValueError as e:
            logger.error(f"❌ Invalid feedback rating: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to update feedback: {e}")
            return None
    
    @staticmethod
    def get_feedback(
        db: Session,
        call_id: str,
        task: Optional[str] = None
    ) -> List[AgentFeedback]:
        """
        Retrieve feedback entries for a call.
        
        Args:
            db: Database session
            call_id: Unique call identifier
            task: Optional task filter
            
        Returns:
            List of AgentFeedback objects
        """
        try:
            query = db.query(AgentFeedback).filter(AgentFeedback.call_id == call_id)
            
            if task:
                query = query.filter(AgentFeedback.task == task)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve feedback: {e}")
            return []
    
    @staticmethod
    def get_feedback_statistics(
        db: Session,
        task: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get feedback statistics for monitoring model performance.
        
        Args:
            db: Database session
            task: Optional task filter
            days: Number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        try:
            from sqlalchemy import func
            from datetime import timedelta
            
            query = db.query(
                AgentFeedback.task,
                func.count(AgentFeedback.id).label('total_count'),
                func.count(AgentFeedback.feedback).label('rated_count'),
                func.avg(AgentFeedback.feedback).label('avg_rating'),
                func.min(AgentFeedback.feedback).label('min_rating'),
                func.max(AgentFeedback.feedback).label('max_rating')
            )
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(AgentFeedback.created_at >= cutoff_date)
            
            if task:
                query = query.filter(AgentFeedback.task == task)
            
            query = query.group_by(AgentFeedback.task)
            
            results = query.all()
            
            statistics = {
                'period_days': days,
                'tasks': {}
            }
            
            for row in results:
                statistics['tasks'][row.task] = {
                    'total_predictions': row.total_count,
                    'rated_predictions': row.rated_count,
                    'rating_coverage': round(row.rated_count / row.total_count * 100, 2) if row.total_count > 0 else 0,
                    'average_rating': round(float(row.avg_rating), 2) if row.avg_rating else None,
                    'min_rating': row.min_rating,
                    'max_rating': row.max_rating
                }
            
            return statistics
            
        except Exception as e:
            logger.error(f"❌ Failed to get feedback statistics: {e}")
            return {'error': str(e)}