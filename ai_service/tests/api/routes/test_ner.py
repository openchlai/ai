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
def ner_app():
    """FastAPI app with NER routes"""
    from app.api.ner_routes import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a sample text for testing various NLP models and their functionality."

# NER Route Tests
class TestNERRoutes:
    """Test NER API routes"""

    @patch('app.api.ner_routes.model_loader')
    @patch('app.api.ner_routes.is_api_server_mode', return_value=False) # Simulate standalone mode
    @patch('app.api.ner_routes.ner_extract_task')
    def test_extract_entities_success(self, mock_celery_task, mock_api_server_mode, mock_loader, ner_app, sample_text):
        """Test successful entity extraction"""
        mock_model = MagicMock()
        mock_model.extract_entities.return_value = [
            {"text": "sample", "label": "MISC", "start": 10, "end": 16, "confidence": 0.95}
        ]
        mock_loader.is_model_ready.return_value = True
        mock_loader.get_model.return_value = mock_model
        mock_celery_task.apply_async.return_value = MagicMock(id="mock_task_id")

        response = ner_app.post(
            "/ner/extract",
            json={"text": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "task_id" in data
        mock_celery_task.apply_async.assert_called_once()
        args, kwargs = mock_celery_task.apply_async.call_args
        assert kwargs['args'][0] == sample_text
        assert kwargs['args'][1] is True # flat=True by default

    @patch('app.api.ner_routes.model_loader')
    @patch('app.api.ner_routes.is_api_server_mode', return_value=False) # Simulate standalone mode
    @patch('app.api.ner_routes.ner_extract_task')
    def test_extract_entities_grouped(self, mock_celery_task, mock_api_server_mode, mock_loader, ner_app, sample_text):
        """Test entity extraction with grouping"""
        mock_model = MagicMock()
        mock_model.extract_entities.return_value = {
            "PERSON": [{"text": "John", "start": 0, "end": 4}],
            "ORG": [{"text": "Company", "start": 10, "end": 17}]
        }
        mock_loader.is_model_ready.return_value = True
        mock_loader.get_model.return_value = mock_model
        mock_celery_task.apply_async.return_value = MagicMock(id="mock_task_id")

        response = ner_app.post(
            "/ner/extract",
            json={"text": sample_text, "flat": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "task_id" in data
        mock_celery_task.apply_async.assert_called_once()
        args, kwargs = mock_celery_task.apply_async.call_args
        assert kwargs['args'][0] == sample_text
        assert kwargs['args'][1] is False # flat=False

    @patch('app.api.ner_routes.model_loader')
    @patch('app.api.ner_routes.is_api_server_mode', return_value=True) # Simulate API server mode
    @patch('app.api.ner_routes.ner_extract_task')
    def test_extract_entities_api_server_mode(self, mock_celery_task, mock_api_server_mode, mock_loader, ner_app, sample_text):
        """Test entity extraction in API server mode (should skip local model check)."""
        mock_celery_task.apply_async.return_value = MagicMock(id="mock_task_id")

        response = ner_app.post(
            "/ner/extract",
            json={"text": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        mock_loader.is_model_ready.assert_not_called() # Should not check local model
        mock_loader.get_model.assert_not_called() # Should not try to get local model
        mock_celery_task.apply_async.assert_called_once()

    def test_ner_model_info(self, ner_app):
        """Test getting NER model information"""
        with patch('app.api.ner_routes.model_loader') as mock_loader, \
             patch('app.api.ner_routes.is_api_server_mode', return_value=False): # Simulate standalone mode
            mock_model = MagicMock()
            mock_model.get_model_info.return_value = {
                "loaded": True,
                "labels": ["PERSON", "ORG", "MISC"]
            }
            mock_loader.is_model_ready.return_value = True
            mock_loader.models.get.return_value = mock_model

            response = ner_app.get("/ner/info")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["model_info"]["loaded"] is True
            assert "labels" in data["model_info"]

    def test_ner_model_info_api_server_mode(self, ner_app):
        """Test getting NER model information in API server mode."""
        with patch('app.api.ner_routes.is_api_server_mode', return_value=True):
            response = ner_app.get("/ner/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "api_server_mode"
            assert data["model_info"]["mode"] == "api_server"

    def test_ner_model_info_not_ready(self, ner_app):
        """Test getting NER model information when not ready in standalone mode."""
        with patch('app.api.ner_routes.model_loader') as mock_loader, \
             patch('app.api.ner_routes.is_api_server_mode', return_value=False):
            mock_loader.is_model_ready.return_value = False
            response = ner_app.get("/ner/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"
            assert "not loaded" in data["message"]

    def test_ner_model_info_model_not_found(self, ner_app):
        """Test getting NER model information when model instance is not found."""
        with patch('app.api.ner_routes.model_loader') as mock_loader, \
             patch('app.api.ner_routes.is_api_server_mode', return_value=False):
            mock_loader.is_model_ready.return_value = True
            mock_loader.models.get.return_value = None # Simulate model not found
            response = ner_app.get("/ner/info")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "not found" in data["message"]

    @patch('app.api.ner_routes.ner_extract_task')
    def test_extract_entities_exception(self, mock_celery_task, ner_app, sample_text):
        """Test exception handling during NER task submission."""
        mock_celery_task.apply_async.side_effect = Exception("Celery error")
        response = ner_app.post(
            "/ner/extract",
            json={"text": sample_text}
        )
        assert response.status_code == 500
        assert "Failed to submit NER task" in response.json()["detail"]

    @patch('app.api.ner_routes.AsyncResult')
    def test_get_ner_task_status_pending(self, mock_async_result, ner_app):
        """Test getting task status for a PENDING task."""
        mock_task = MagicMock()
        mock_task.state = "PENDING"
        mock_task.info = None
        mock_async_result.return_value = mock_task

        response = ner_app.get("/ner/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "pending"
        assert "queued" in data["progress"]["message"]

    @patch('app.api.ner_routes.AsyncResult')
    def test_get_ner_task_status_processing(self, mock_async_result, ner_app):
        """Test getting task status for a PROCESSING task."""
        mock_task = MagicMock()
        mock_task.state = "PROCESSING"
        mock_task.info = {"progress": 50, "step": "entity_extraction"}
        mock_async_result.return_value = mock_task

        response = ner_app.get("/ner/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "processing"
        assert data["progress"]["progress"] == 50

    @patch('app.api.ner_routes.AsyncResult')
    def test_get_ner_task_status_success(self, mock_async_result, ner_app):
        """Test getting task status for a SUCCESS task."""
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.result = {
            "entities": [{"text": "John", "label": "PERSON", "start": 0, "end": 4, "confidence": 0.99}],
            "processing_time": 0.05,
            "model_info": {"version": "1.0"},
            "timestamp": "2023-01-01T00:00:00"
        }
        mock_async_result.return_value = mock_task

        response = ner_app.get("/ner/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "success"
        assert len(data["result"]["entities"]) == 1
        assert data["result"]["entities"][0]["start"] == 0 # Check for new fields

    @patch('app.api.ner_routes.AsyncResult')
    def test_get_ner_task_status_failure(self, mock_async_result, ner_app):
        """Test getting task status for a FAILURE task."""
        mock_task = MagicMock()
        mock_task.state = "FAILURE"
        mock_task.info = "NER task failed due to XYZ"
        mock_async_result.return_value = mock_task

        response = ner_app.get("/ner/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "failed"
        assert "NER task failed" in data["error"]

    @patch('app.api.ner_routes.AsyncResult')
    def test_get_ner_task_status_other_state(self, mock_async_result, ner_app):
        """Test getting task status for an unknown/other state."""
        mock_task = MagicMock()
        mock_task.state = "REVOKED"
        mock_task.info = None
        mock_async_result.return_value = mock_task

        response = ner_app.get("/ner/task/mock_task_id")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "mock_task_id"
        assert data["status"] == "revoked"

    @patch('app.api.ner_routes.AsyncResult')
    def test_get_ner_task_status_exception(self, mock_async_result, ner_app):
        """Test exception handling when getting task status."""
        mock_async_result.side_effect = Exception("Celery lookup error")

        response = ner_app.get("/ner/task/mock_task_id")
        assert response.status_code == 500
        assert "Error checking task status" in response.json()["detail"]

    @patch('app.api.ner_routes.is_api_server_mode', return_value=False)
    @patch('app.api.ner_routes.model_loader')
    def test_ner_demo_success(self, mock_loader, mock_api_server_mode, ner_app):
        """Test the NER demo endpoint."""
        mock_model = MagicMock()
        mock_model.extract_entities.return_value = [
            {"text": "John Doe", "label": "PERSON", "start": 0, "end": 8, "confidence": 0.99},
            {"text": "Nairobi", "label": "GPE", "start": 20, "end": 27, "confidence": 0.98}
        ]
        mock_loader.is_model_ready.return_value = True
        mock_loader.get_model.return_value = mock_model
        
        with patch('app.api.ner_routes.ner_extract_task') as mock_celery_task:
            mock_celery_task.apply_async.return_value = MagicMock(id="demo_task_id")

            response = ner_app.post("/ner/demo")
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "demo_task_id"
            assert data["status"] == "queued"
            mock_celery_task.apply_async.assert_called_once()
            args, kwargs = mock_celery_task.apply_async.call_args
            assert kwargs['args'][0].startswith("On 2023-05-15") # Check narrative content
            assert kwargs['args'][1] is True # flat=True
