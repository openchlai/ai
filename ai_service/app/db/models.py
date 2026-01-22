from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, Index, UniqueConstraint
from sqlalchemy.sql import func
from .session import Base


class AgentFeedback(Base):
    """
    Stores agent feedback on AI model predictions per call and task.
    Allows tracking of model performance from real-world agent perspective.
    """
    __tablename__ = "agent_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(100), nullable=False, index=True)
    task = Column(String(50), nullable=False, index=True)
    prediction = Column(JSON, nullable=False)
    feedback = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    processing_mode = Column(String(20))
    model_version = Column(String(50))

    __table_args__ = (
        UniqueConstraint('call_id', 'task', name='uix_call_task'),
        Index('idx_call_task', 'call_id', 'task'),
        Index('idx_task_feedback', 'task', 'feedback'),
        Index('idx_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<AgentFeedback(call_id={self.call_id}, task={self.task}, feedback={self.feedback})>"
