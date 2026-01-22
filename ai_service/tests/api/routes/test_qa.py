import pytest
import sys
import os
from io import BytesIO
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def qa_app():
    """FastAPI app with QA routes"""
    from app.api.qa_route import router
    app = FastAPI()
    app.include_router(router)
    
    # Patch qa_model.is_ready here to default to True for most tests
    with patch('app.api.qa_route.qa_model.is_ready', return_value=True):
        yield TestClient(app)

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a sample text for testing various NLP models and their functionality."

# QA Route Tests
class TestQARoutes:
    """Test QA API routes"""

    @patch('app.api.qa_route.model_loader')
    @patch('app.api.qa_route.is_api_server_mode', return_value=False) # Simulate standalone mode
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_evaluate_transcript_success(self, mock_celery_task, mock_api_server_mode, mock_loader, qa_app):
        """Test successful transcript evaluation"""
        mock_model = MagicMock()
        mock_model.evaluate_transcript.return_value = {
            "scores": {
                "opening": 0.8,
                "listening": 0.7,
                "resolution": 0.9
            },
            "overall_score": 0.8,
            "recommendations": ["Improve greeting"]
        }
        mock_loader.get_model.return_value = mock_model
        mock_celery_task.apply_async.return_value = MagicMock(id="mock_task_id")

        transcript = "Hello, thank you for calling. How can I help you?"
        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": transcript}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "task_id" in data
        assert isinstance(data["task_id"], str)
        mock_celery_task.apply_async.assert_called_once()
        args, kwargs = mock_celery_task.apply_async.call_args
        assert kwargs['args'][0] == transcript

    @patch('app.api.qa_route.model_loader')
    @patch('app.api.qa_route.is_api_server_mode', return_value=False) # Simulate standalone mode
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_evaluate_transcript_empty(self, mock_celery_task, mock_api_server_mode, mock_loader, qa_app):
        """Test transcript evaluation with empty transcript"""
        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": ""}
        )
        assert response.status_code == 422 # Fix: Expect 422 from FastAPI validation
        assert "string_too_short" in response.json()["detail"][0]["type"] # Fix: Check for Pydantic error type

    @patch('app.api.qa_route.qa_model.is_ready', return_value=False) # Patch directly
    @patch('app.api.qa_route.model_loader')
    @patch('app.api.qa_route.is_api_server_mode', return_value=False) # Simulate standalone mode
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_evaluate_transcript_model_not_loaded(self, mock_celery_task, mock_api_server_mode, mock_loader, mock_is_model_ready, qa_app):
        """Test transcript evaluation when model is not loaded"""
        mock_loader.get_model.return_value = None # Ensure get_model also returns None

        transcript = "Hello, thank you for calling. How can I help you?"
        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": transcript}
        )

        assert response.status_code == 503
        assert "QA model not ready" in response.json()["detail"]

    @patch('app.api.qa_route.AsyncResult')
    def test_get_qa_task_status_pending(self, mock_async_result, qa_app):
        """Test getting task status for a PENDING task."""
        mock_task = MagicMock()
        mock_task.state = "PENDING"
        mock_task.info = None
        mock_async_result.return_value = mock_task

        response = qa_app.get("/qa/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "pending"
        assert "queued" in data["progress"]["message"]

    @patch('app.api.qa_route.AsyncResult')
    def test_get_qa_task_status_processing(self, mock_async_result, qa_app):
        """Test getting task status for a PROCESSING task."""
        mock_task = MagicMock()
        mock_task.state = "PROCESSING"
        mock_task.info = {"progress": 50, "step": "evaluation"}
        mock_async_result.return_value = mock_task

        response = qa_app.get("/qa/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "processing"
        assert data["progress"]["progress"] == 50

    @patch('app.api.qa_route.AsyncResult')
    def test_get_qa_task_status_success(self, mock_async_result, qa_app):
        """Test getting task status for a SUCCESS task."""
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.result = {
            "evaluations": {"category": [{"submetric": "opening", "prediction": True, "score": "pass"}]},
            "processing_time": 0.1,
            "model_info": {"version": "1.0", "name": "qa_model"},
            "timestamp": "2023-01-01T00:00:00"
        }
        mock_async_result.return_value = mock_task

        response = qa_app.get("/qa/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "success"
        assert data["result"]["processing_time"] == 0.1

    @patch('app.api.qa_route.AsyncResult')
    def test_get_qa_task_status_failure(self, mock_async_result, qa_app):
        """Test getting task status for a FAILURE task."""
        mock_task = MagicMock()
        mock_task.state = "FAILURE"
        mock_task.info = "QA task failed due to XYZ"
        mock_async_result.return_value = mock_task

        response = qa_app.get("/qa/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "failed"
        assert "QA task failed" in data["error"]

    @patch('app.api.qa_route.AsyncResult')
    def test_get_qa_task_status_other_state(self, mock_async_result, qa_app):
        """Test getting task status for an unknown/other state."""
        mock_task = MagicMock()
        mock_task.state = "REVOKED"
        mock_task.info = None
        mock_async_result.return_value = mock_task

        response = qa_app.get("/qa/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "revoked"

    @patch('app.api.qa_route.AsyncResult')
    def test_get_qa_task_status_exception(self, mock_async_result, qa_app):
        """Test exception handling when getting task status."""
        mock_async_result.side_effect = Exception("Celery lookup error")

        response = qa_app.get("/qa/task/mock_task_id")
        assert response.status_code == 500
        assert "Error checking task" in response.json()["detail"] # Fix: Match endpoint's actual detail message

    @patch('app.api.qa_route.model_loader')
    @patch('app.api.qa_route.is_api_server_mode', return_value=False)
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_qa_demo_success(self, mock_celery_task, mock_api_server_mode, mock_loader, qa_app):
        """Test the QA demo endpoint."""
        mock_model = MagicMock()
        mock_model.evaluate_transcript.return_value = {
            "overall_score": 0.85,
            "scores": {"opening": 0.9},
            "recommendations": ["Good job"],
            "processing_time": 0.1,
            "model_info": {"version": "1.0", "name": "qa_model"}, # More complete model_info
            "timestamp": "2023-01-01T00:00:00"
        }
        mock_loader.get_model.return_value = mock_model

        with patch('app.api.qa_route.qa_evaluate_task') as mock_celery_task:
            mock_celery_task.apply_async.return_value = MagicMock(id="demo_task_id")

            response = qa_app.post("/qa/demo")
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "demo_task_id"
            assert data["status"] == "queued"
            mock_celery_task.apply_async.assert_called_once()
            args, kwargs = mock_celery_task.apply_async.call_args
            assert kwargs['args'][0].startswith("Agent:") # Match demo transcript

    @patch('app.api.qa_route.is_api_server_mode', return_value=True)
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_evaluate_transcript_api_server_mode(self, mock_celery_task, mock_api_server_mode, qa_app):
        """Test transcript evaluation in API server mode (skips local model check)"""
        mock_celery_task.apply_async.return_value = MagicMock(id="api_server_task_id")

        transcript = "This is a test transcript for API server mode execution."
        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": transcript}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["task_id"] == "api_server_task_id"
        mock_celery_task.apply_async.assert_called_once()

    @patch('app.api.qa_route.model_loader')
    @patch('app.api.qa_route.is_api_server_mode', return_value=False)
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_evaluate_transcript_empty_after_strip(self, mock_celery_task, mock_api_server_mode, mock_loader, qa_app):
        """Test transcript evaluation with whitespace-only transcript"""
        mock_model = MagicMock()
        mock_model.is_ready.return_value = True
        mock_loader.get_model.return_value = mock_model

        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": "          "}  # Only whitespace
        )

        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]

    @patch('app.api.qa_route.model_loader')
    @patch('app.api.qa_route.is_api_server_mode', return_value=False)
    @patch('app.api.qa_route.qa_evaluate_task')
    def test_evaluate_transcript_task_submission_exception(self, mock_celery_task, mock_api_server_mode, mock_loader, qa_app):
        """Test exception handling when task submission fails"""
        mock_model = MagicMock()
        mock_model.is_ready.return_value = True
        mock_loader.get_model.return_value = mock_model
        mock_celery_task.apply_async.side_effect = Exception("Celery connection error")

        transcript = "This is a test transcript that will fail during submission."
        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": transcript}
        )

        assert response.status_code == 500
        assert "Failed to submit task" in response.json()["detail"]

    @patch('app.api.qa_route.is_api_server_mode', return_value=True)
    def test_get_qa_info_api_server_mode(self, mock_api_server_mode, qa_app):
        """Test QA info endpoint in API server mode"""
        response = qa_app.get("/qa/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "api_server_mode"
        assert "Celery workers" in data["message"]
        assert data["model_info"]["mode"] == "api_server"

    @patch('app.api.qa_route.qa_model.is_ready', return_value=False)
    @patch('app.api.qa_route.is_api_server_mode', return_value=False)
    def test_get_qa_info_model_not_ready(self, mock_api_server_mode, mock_is_ready, qa_app):
        """Test QA info endpoint when model is not ready in standalone mode"""
        with patch('app.api.qa_route.qa_model.get_model_info', return_value={"error": "Model failed to load"}):
            response = qa_app.get("/qa/info")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"
            assert "not loaded" in data["message"]
            assert "model_info" in data
