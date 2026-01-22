"""
Comprehensive tests for database models - AgentFeedback model
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, Mock
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, Index
from sqlalchemy.orm import declarative_base

# Import the model
from app.db.models import AgentFeedback
from app.db.session import Base


class TestAgentFeedbackModel:
    """Tests for AgentFeedback model structure and attributes"""

    def test_agent_feedback_table_name(self):
        """Test AgentFeedback has correct table name"""
        assert AgentFeedback.__tablename__ == "agent_feedback"

    def test_agent_feedback_primary_key(self):
        """Test AgentFeedback has id as primary key"""
        assert AgentFeedback.id.primary_key is True

    def test_agent_feedback_id_column(self):
        """Test id column configuration"""
        id_col = AgentFeedback.id
        assert id_col.type.__class__.__name__ == "Integer"
        assert id_col.primary_key is True

    def test_agent_feedback_call_id_column(self):
        """Test call_id column configuration"""
        call_id_col = AgentFeedback.call_id
        assert call_id_col.nullable is False
        assert str(call_id_col.type) == "VARCHAR(100)"

    def test_agent_feedback_task_column(self):
        """Test task column configuration"""
        task_col = AgentFeedback.task
        assert task_col.nullable is False
        assert str(task_col.type) == "VARCHAR(50)"

    def test_agent_feedback_prediction_column(self):
        """Test prediction column is JSON type"""
        prediction_col = AgentFeedback.prediction
        assert prediction_col.nullable is False
        assert "JSON" in str(prediction_col.type)

    def test_agent_feedback_feedback_column(self):
        """Test feedback column allows null"""
        feedback_col = AgentFeedback.feedback
        assert feedback_col.nullable is True
        assert feedback_col.type.__class__.__name__ == "Integer"

    def test_agent_feedback_reason_column(self):
        """Test reason column allows null and is text"""
        reason_col = AgentFeedback.reason
        assert reason_col.nullable is True
        assert reason_col.type.__class__.__name__ == "Text"

    def test_agent_feedback_created_at_column(self):
        """Test created_at has timezone and server default"""
        created_at_col = AgentFeedback.created_at
        assert created_at_col.nullable is False
        assert "DATETIME" in str(created_at_col.type).upper()

    def test_agent_feedback_updated_at_column(self):
        """Test updated_at column exists"""
        updated_at_col = AgentFeedback.updated_at
        assert updated_at_col is not None

    def test_agent_feedback_processing_mode_column(self):
        """Test processing_mode column"""
        processing_mode_col = AgentFeedback.processing_mode
        assert str(processing_mode_col.type) == "VARCHAR(20)"

    def test_agent_feedback_model_version_column(self):
        """Test model_version column"""
        model_version_col = AgentFeedback.model_version
        assert str(model_version_col.type) == "VARCHAR(50)"

    def test_agent_feedback_has_constraints(self):
        """Test AgentFeedback has unique and index constraints"""
        # Check that table args exist
        assert AgentFeedback.__table_args__ is not None
        assert len(AgentFeedback.__table_args__) > 0

    def test_agent_feedback_unique_constraint(self):
        """Test unique constraint on call_id and task"""
        table_args = AgentFeedback.__table_args__
        # Should have UniqueConstraint
        constraints = [arg for arg in table_args if hasattr(arg, "name")]
        assert len(constraints) >= 1

    def test_agent_feedback_indexes(self):
        """Test indexes are properly configured"""
        table_args = AgentFeedback.__table_args__
        # Should have Index objects
        indexes = [arg for arg in table_args if hasattr(arg, "expressions")]
        assert len(indexes) >= 1

    def test_agent_feedback_repr(self):
        """Test __repr__ method of AgentFeedback"""
        # Create a mock instance
        feedback = AgentFeedback(
            call_id="call_123",
            task="classification",
            feedback=4
        )
        repr_str = repr(feedback)
        assert "AgentFeedback" in repr_str
        assert "call_123" in repr_str
        assert "classification" in repr_str
        assert "4" in repr_str

    def test_agent_feedback_creation_with_all_fields(self):
        """Test creating AgentFeedback instance with all fields"""
        prediction = {"class": "urgent", "confidence": 0.95}
        feedback = AgentFeedback(
            id=1,
            call_id="call_001",
            task="classification",
            prediction=prediction,
            feedback=5,
            reason="Correct classification",
            processing_mode="realtime",
            model_version="v1.0"
        )
        assert feedback.id == 1
        assert feedback.call_id == "call_001"
        assert feedback.task == "classification"
        assert feedback.prediction == prediction
        assert feedback.feedback == 5
        assert feedback.reason == "Correct classification"
        assert feedback.processing_mode == "realtime"
        assert feedback.model_version == "v1.0"

    def test_agent_feedback_creation_with_minimal_fields(self):
        """Test creating AgentFeedback with minimal required fields"""
        prediction = {"output": "test"}
        feedback = AgentFeedback(
            call_id="call_002",
            task="ner",
            prediction=prediction
        )
        assert feedback.call_id == "call_002"
        assert feedback.task == "ner"
        assert feedback.prediction == prediction
        assert feedback.feedback is None
        assert feedback.reason is None

    def test_agent_feedback_feedback_can_be_none(self):
        """Test feedback field can be None"""
        feedback = AgentFeedback(
            call_id="call_003",
            task="summarization",
            prediction={"summary": "test"}
        )
        assert feedback.feedback is None

    def test_agent_feedback_feedback_can_be_integer(self):
        """Test feedback field can hold integer values"""
        feedback = AgentFeedback(
            call_id="call_004",
            task="translation",
            prediction={"translated": "test"},
            feedback=3
        )
        assert feedback.feedback == 3

    def test_agent_feedback_reason_can_be_none(self):
        """Test reason field can be None"""
        feedback = AgentFeedback(
            call_id="call_005",
            task="qa",
            prediction={"answer": "test"}
        )
        assert feedback.reason is None

    def test_agent_feedback_reason_can_be_text(self):
        """Test reason field can hold text"""
        reason_text = "Model performed well on this classification task"
        feedback = AgentFeedback(
            call_id="call_006",
            task="classification",
            prediction={"class": "test"},
            reason=reason_text
        )
        assert feedback.reason == reason_text

    def test_agent_feedback_processing_mode_values(self):
        """Test different processing_mode values"""
        for mode in ["realtime", "postcall", "hybrid"]:
            feedback = AgentFeedback(
                call_id=f"call_{mode}",
                task="classification",
                prediction={"class": "test"},
                processing_mode=mode
            )
            assert feedback.processing_mode == mode

    def test_agent_feedback_model_version_format(self):
        """Test model_version field"""
        version = "v2.1.0"
        feedback = AgentFeedback(
            call_id="call_version",
            task="classification",
            prediction={"class": "test"},
            model_version=version
        )
        assert feedback.model_version == version

    def test_agent_feedback_complex_prediction(self):
        """Test prediction can store complex JSON data"""
        complex_prediction = {
            "class": "urgent",
            "confidence": 0.95,
            "alternatives": [
                {"class": "normal", "confidence": 0.05}
            ],
            "metadata": {
                "processing_time": 0.123,
                "model": "transformer_v2"
            }
        }
        feedback = AgentFeedback(
            call_id="call_complex",
            task="classification",
            prediction=complex_prediction
        )
        assert feedback.prediction == complex_prediction
        assert feedback.prediction["class"] == "urgent"
        assert len(feedback.prediction["alternatives"]) == 1

    def test_agent_feedback_inherits_from_base(self):
        """Test AgentFeedback inherits from declarative base"""
        # Check if AgentFeedback has registry from Base
        assert hasattr(AgentFeedback, '__table__')
        assert hasattr(AgentFeedback, '__mapper__')

    def test_agent_feedback_column_indexing(self):
        """Test that indexed columns are properly configured"""
        # call_id should be indexed
        assert AgentFeedback.call_id.index is True
        # task should be indexed
        assert AgentFeedback.task.index is True

    def test_agent_feedback_repr_with_none_feedback(self):
        """Test __repr__ when feedback is None"""
        feedback = AgentFeedback(
            call_id="call_none",
            task="classification"
        )
        repr_str = repr(feedback)
        assert "AgentFeedback" in repr_str
        assert "call_none" in repr_str

    def test_agent_feedback_repr_with_none_task(self):
        """Test __repr__ works with various task values"""
        tasks = ["classification", "ner", "summarization", "translation", "qa"]
        for task in tasks:
            feedback = AgentFeedback(
                call_id="call_test",
                task=task
            )
            repr_str = repr(feedback)
            assert task in repr_str

    def test_agent_feedback_all_fields_assigned(self):
        """Test all expected fields are present"""
        expected_fields = [
            'id', 'call_id', 'task', 'prediction', 'feedback',
            'reason', 'created_at', 'updated_at', 'processing_mode', 'model_version'
        ]
        for field in expected_fields:
            assert hasattr(AgentFeedback, field), f"Missing field: {field}"

    def test_agent_feedback_created_at_datetime_type(self):
        """Test created_at column has datetime type"""
        from sqlalchemy import DateTime
        created_at_col = AgentFeedback.created_at
        # Check if it's a DateTime type
        assert "DATETIME" in str(created_at_col.type).upper()

    def test_agent_feedback_table_args_structure(self):
        """Test table_args contains expected constraint types"""
        table_args = AgentFeedback.__table_args__
        # Should be a tuple
        assert isinstance(table_args, tuple)
        # Should contain multiple items (UniqueConstraint and Indexes)
        assert len(table_args) >= 2

    def test_agent_feedback_with_long_call_id(self):
        """Test AgentFeedback with maximum length call_id"""
        long_call_id = "c" * 100  # Max 100 chars
        feedback = AgentFeedback(
            call_id=long_call_id,
            task="classification",
            prediction={"class": "test"}
        )
        assert feedback.call_id == long_call_id

    def test_agent_feedback_with_long_task(self):
        """Test AgentFeedback with task string"""
        task = "classification_extended"
        feedback = AgentFeedback(
            call_id="call_test",
            task=task,
            prediction={"class": "test"}
        )
        assert feedback.task == task
