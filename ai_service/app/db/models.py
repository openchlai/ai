from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .session import Base


class PipelineTask(Base):
    """
    Stores information about pipeline processing tasks.
    Each task represents one audio processing job through the AI pipeline.
    """
    __tablename__ = "pipeline_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    call_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    status = Column(String, default="pending", nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to feedbacks
    feedbacks = relationship("ModelFeedback", back_populates="task", cascade="all, delete-orphan")
    
    # Additional indexes for common queries
    __table_args__ = (
        Index('idx_task_status_created', 'status', 'created_at'),
        Index('idx_call_agent', 'call_id', 'agent_id'),
    )


class ModelFeedback(Base):
    """
    Stores user feedback for individual AI models in the pipeline.
    
    Supported models:
    - whisper: Speech-to-text transcription
    - distilbert-ner: Named Entity Recognition
    - classifier: Text classification
    - summarization: Text summarization
    - translation: Language translation
    """
    __tablename__ = "model_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey('pipeline_tasks.task_id', ondelete='CASCADE'), 
                     index=True, nullable=False)
    model_name = Column(String, index=True, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship back to task
    task = relationship("PipelineTask", back_populates="feedbacks")
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_task_model', 'task_id', 'model_name'),
        Index('idx_model_rating', 'model_name', 'rating'),
        Index('idx_model_created', 'model_name', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ModelFeedback(model={self.model_name}, rating={self.rating}, task={self.task_id})>"

