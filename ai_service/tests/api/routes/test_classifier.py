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
def classifier_app():
    """FastAPI app with classifier routes"""
    from app.api.classifier_route import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a sample text for testing various NLP models and their functionality."

# Classifier Route Tests
class TestClassifierRoutes:
    """Test classifier API routes"""

    @patch('app.api.classifier_route.model_loader')
    def test_classify_text_success(self, mock_loader, classifier_app, sample_text):
        """Test successful text classification"""
        mock_model = MagicMock()
        mock_model.classify.return_value = {
            "main_category": "general_inquiry",
            "sub_category": "account_support",
            "confidence": 0.89,
            "priority": "medium",
            "chunks_processed": 1,
            "processing_time": 0.1,
            "model_info": {"version": "1.0"},
            "timestamp": "2023-01-01T00:00:00"
        }
        mock_loader.get_model.return_value = mock_model

        response = classifier_app.post(
            "/classifier/classify",
            json={"narrative": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "task_id" in data

    @patch('app.api.classifier_route.model_loader')
    def test_classify_text_empty(self, mock_loader, classifier_app):
        """Test classification with empty text"""
        response = classifier_app.post(
            "/classifier/classify",
            json={"narrative": ""}
        )

        assert response.status_code == 400
        assert "Narrative input cannot be empty" in response.json()["detail"]

    @patch('app.api.classifier_route.model_loader')
    @patch('app.api.classifier_route.is_api_server_mode', return_value=False) # Simulate standalone mode
    def test_classify_model_not_loaded(self, mock_api_server_mode, mock_loader, classifier_app, sample_text):
        """Test classification when model is not loaded"""
        mock_loader.is_model_ready.return_value = False
        mock_loader.get_model.return_value = None # Ensure get_model also returns None

        response = classifier_app.post(
            "/classifier/classify",
            json={"narrative": sample_text}
        )

        assert response.status_code == 503
        assert "Classifier model not ready" in response.json()["detail"]

    def test_get_classifier_info(self, classifier_app):
        """Test getting classifier model information"""
        with patch('app.api.classifier_route.model_loader') as mock_loader, \
             patch('app.api.classifier_route.is_api_server_mode', return_value=False): # Simulate standalone mode
            mock_model = MagicMock()
            mock_model.get_model_info.return_value = {
                "loaded": True,
                "categories": ["general", "technical"],
                "version": "1.0"
            }
            mock_loader.is_model_ready.return_value = True
            mock_loader.models.get.return_value = mock_model

            response = classifier_app.get("/classifier/info")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["model_info"]["loaded"] is True
            assert "categories" in data["model_info"]

    def test_get_classifier_info_api_server_mode(self, classifier_app):
        """Test getting classifier model information in API server mode."""
        with patch('app.api.classifier_route.is_api_server_mode', return_value=True):
            response = classifier_app.get("/classifier/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "api_server_mode"
            assert data["model_info"]["mode"] == "api_server"

    def test_get_classifier_info_not_ready(self, classifier_app):
        """Test getting classifier model information when not ready in standalone mode."""
        with patch('app.api.classifier_route.model_loader') as mock_loader, \
             patch('app.api.classifier_route.is_api_server_mode', return_value=False):
            mock_loader.is_model_ready.return_value = False
            response = classifier_app.get("/classifier/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"
            assert "not loaded" in data["message"]

    def test_get_classifier_info_model_not_found(self, classifier_app):
        """Test getting classifier model information when model instance is not found."""
        with patch('app.api.classifier_route.model_loader') as mock_loader, \
             patch('app.api.classifier_route.is_api_server_mode', return_value=False):
            mock_loader.is_model_ready.return_value = True
            mock_loader.models.get.return_value = None # Simulate model not found
            response = classifier_app.get("/classifier/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "not found" in data["message"]

    @patch('app.api.classifier_route.classifier_classify_task')
    def test_classify_narrative_exception(self, mock_celery_task, classifier_app, sample_text):
        """Test exception handling during classification task submission."""
        mock_celery_task.apply_async.side_effect = Exception("Celery error")
        response = classifier_app.post(
            "/classifier/classify",
            json={"narrative": sample_text}
        )
        assert response.status_code == 500
        assert "Failed to submit task" in response.json()["detail"]

    @patch('app.api.classifier_route.AsyncResult')
    def test_get_classifier_task_status_pending(self, mock_async_result, classifier_app):
        """Test getting task status for a PENDING task."""
        mock_task = MagicMock()
        mock_task.state = "PENDING"
        mock_task.info = None
        mock_async_result.return_value = mock_task

        response = classifier_app.get("/classifier/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "pending"
        assert "queued" in data["progress"]["message"]

    @patch('app.api.classifier_route.AsyncResult')
    def test_get_classifier_task_status_processing(self, mock_async_result, classifier_app):
        """Test getting task status for a PROCESSING task."""
        mock_task = MagicMock()
        mock_task.state = "PROCESSING"
        mock_task.info = {"progress": 50, "step": "chunking"}
        mock_async_result.return_value = mock_task

        response = classifier_app.get("/classifier/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "processing"
        assert data["progress"]["progress"] == 50

    @patch('app.api.classifier_route.AsyncResult')
    def test_get_classifier_task_status_success(self, mock_async_result, classifier_app):
        """Test getting task status for a SUCCESS task."""
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.result = {
            "main_category": "general_inquiry",
            "sub_category": "account_support",
            "intervention": "referral",
            "priority": "medium",
            "confidence_scores": {"main_category": 0.9},
            "chunks_processed": 1,
            "processing_time": 0.1,
            "model_info": {"version": "1.0"},
            "timestamp": "2023-01-01T00:00:00"
        }
        mock_async_result.return_value = mock_task

        response = classifier_app.get("/classifier/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "success"
        assert data["result"]["main_category"] == "general_inquiry"

    @patch('app.api.classifier_route.AsyncResult')
    def test_get_classifier_task_status_failure(self, mock_async_result, classifier_app):
        """Test getting task status for a FAILURE task."""
        mock_task = MagicMock()
        mock_task.state = "FAILURE"
        mock_task.info = "Task failed due to XYZ"
        mock_async_result.return_value = mock_task

        response = classifier_app.get("/classifier/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "failed"
        assert "Task failed" in data["error"]

    @patch('app.api.classifier_route.AsyncResult')
    def test_get_classifier_task_status_other_state(self, mock_async_result, classifier_app):
        """Test getting task status for an unknown/other state."""
        mock_task = MagicMock()
        mock_task.state = "REVOKED"
        mock_task.info = None
        mock_async_result.return_value = mock_task

        response = classifier_app.get("/classifier/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "revoked"

    @patch('app.api.classifier_route.AsyncResult')
    def test_get_classifier_task_status_exception(self, mock_async_result, classifier_app):
        """Test exception handling when getting task status."""
        mock_async_result.side_effect = Exception("Celery lookup error")

        response = classifier_app.get("/classifier/task/mock_task_id")
        assert response.status_code == 500
        assert "Error checking task" in response.json()["detail"]

    @patch('app.api.classifier_route.is_api_server_mode', return_value=False)
    @patch('app.api.classifier_route.model_loader')
    def test_classifier_demo_success(self, mock_loader, mock_api_server_mode, classifier_app):
        """Test the classifier demo endpoint."""
        mock_model = MagicMock()
        mock_model.classify.return_value = {
            "main_category": "abuse",
            "sub_category": "sexual_abuse",
            "intervention": "referral",
            "priority": "urgent",
            "confidence_scores": {"main_category": 0.95},
            "chunks_processed": 1,
            "processing_time": 0.1,
            "model_info": {"version": "1.0"},
            "timestamp": "2023-01-01T00:00:00"
        }
        mock_loader.is_model_ready.return_value = True
        mock_loader.get_model.return_value = mock_model
        
        with patch('app.api.classifier_route.classifier_classify_task') as mock_celery_task:
            mock_celery_task.apply_async.return_value = MagicMock(id="demo_task_id")

            response = classifier_app.post("/classifier/demo")
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "demo_task_id"
            assert data["status"] == "queued"
            mock_celery_task.apply_async.assert_called_once()
            args, kwargs = mock_celery_task.apply_async.call_args
            assert kwargs['args'][0] == "On 2023-05-15 a girl (age 16) from District X called to report sexual abuse by her stepfather. She is currently 2 months pregnant and being forced to abort. The stepfather has threatened to kill her if she doesn't comply. Her mother is also being abused."