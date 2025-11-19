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

    # Additional indexes for common queries
    __table_args__ = (
        Index('idx_task_status_created', 'status', 'created_at'),
        Index('idx_call_agent', 'call_id', 'agent_id'),
    )

