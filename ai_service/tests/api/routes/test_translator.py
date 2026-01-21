import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI
from app.api.translator_routes import router

from app.main import app

client = TestClient(app)

# --- Mock Data ---

# A valid text for testing translation
VALID_TEXT = "Hello, how are you?"
EMPTY_TEXT = ""
MOCK_TRANSLATED_TEXT = "Halo, habari yako?"

# Mocked model info
MOCK_MODEL_INFO = {
    "name": "mock-translator-v1.0",
    "version": "1.0",
    "last_updated": "2024-01-01T12:00:00Z"
}


def test_translate_success():
    """Test successful text translation task submission."""
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader, \
         patch('app.api.translator_routes.translation_translate_task.apply_async') as mock_task:
        mock_loader.is_model_ready.return_value = True
        mock_result = type('obj', (object,), {'id': 'test_task_123'})()
        mock_task.return_value = mock_result

        response = client.post("/translate/", json={"text": VALID_TEXT})

        assert response.status_code == 202
        response_json = response.json()

        # Endpoint now returns task_id for async processing
        assert "task_id" in response_json
        assert response_json["task_id"] == "test_task_123"
        assert response_json["status"] == "queued"
        assert "status_endpoint" in response_json

def test_translate_empty_text():
    """
    Test the case where the text input is an empty string.
    The endpoint should return a 400 Bad Request error.
    """
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True

        response = client.post("/translate/", json={"text": EMPTY_TEXT})

        assert response.status_code == 400
        assert response.json() == {"detail": "Text input cannot be empty"}

def test_translate_model_not_ready():
    """
    Test the case where the translation model is not ready in standalone mode.
    The endpoint should return a 503 Service Unavailable error.
    """
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False

        response = client.post("/translate/", json={"text": VALID_TEXT})

        assert response.status_code == 503
        assert response.json() == {"detail": "Translation model not ready. Check /health/models for status."}

def test_translate_model_not_available():
    """
    Test the case where task submission fails.
    The endpoint should return a 500 Internal Server Error.
    """
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader, \
         patch('app.api.translator_routes.translation_translate_task.apply_async') as mock_task:
        mock_loader.is_model_ready.return_value = True
        mock_task.side_effect = Exception("Task submission failed")

        response = client.post("/translate/", json={"text": VALID_TEXT})

        assert response.status_code == 500
        assert "Failed to submit task" in response.json()["detail"]



def test_translate_exception_on_run():
    """
    Test the case where an unexpected exception occurs during task submission.
    The endpoint should return a 500 Internal Server Error.
    """
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader, \
         patch('app.api.translator_routes.translation_translate_task.apply_async') as mock_task:
        mock_loader.is_model_ready.return_value = True
        mock_task.side_effect = RuntimeError("Celery connection error")

        response = client.post("/translate/", json={"text": VALID_TEXT})

        assert response.status_code == 500
        assert "Failed to submit task" in response.json()["detail"]


def test_get_translation_info_ready():
    """Test the /translate/info endpoint when the model is ready."""
    # In API server mode (default), status is "api_server_mode"
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False):
        with patch('app.api.translator_routes.model_loader') as mock_loader:
            mock_loader.is_model_ready.return_value = True
            mock_translator = mock_loader.models.get.return_value
            mock_translator.get_model_info.return_value = MOCK_MODEL_INFO

            response = client.get("/translate/info")

            assert response.status_code == 200
            assert response.json()["status"] == "ready"
            assert response.json()["model_info"] == MOCK_MODEL_INFO

def test_get_translation_info_not_ready():
    """Test the /translate/info endpoint when the model is not ready."""
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False):
        with patch('app.api.translator_routes.model_loader') as mock_loader:
            mock_loader.is_model_ready.return_value = False

            response = client.get("/translate/info")

            assert response.status_code == 200
            assert response.json()["status"] == "not_ready"
            assert "message" in response.json()

def test_get_translation_info_not_found():
    """Test the /translate/info endpoint when the model is not found in standalone mode."""
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None

        response = client.get("/translate/info")

        assert response.status_code == 200
        assert response.json()["status"] == "error"
        assert "message" in response.json()


# Additional tests for better coverage

def test_translate_api_server_mode():
    """Test translation in API server mode (doesn't check local model)."""
    with patch('app.api.translator_routes.is_api_server_mode', return_value=True), \
         patch('app.api.translator_routes.translation_translate_task.apply_async') as mock_task:
        mock_result = type('obj', (object,), {'id': 'test-api-server-task'})()
        mock_task.return_value = mock_result

        response = client.post("/translate/", json={"text": VALID_TEXT})

        assert response.status_code == 202
        assert response.json()["task_id"] == "test-api-server-task"


def test_get_task_status_pending():
    """Test getting task status when task is pending."""
    with patch('app.api.translator_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {'state': 'PENDING'})()
        mock_async.return_value = mock_result

        response = client.get("/translate/task/test-pending-task")

        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        assert response.json()["progress"]["message"] == "Task is queued"


def test_get_task_status_processing():
    """Test getting task status when task is processing."""
    with patch('app.api.translator_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {'state': 'PROCESSING', 'info': {"progress": 50}})()
        mock_async.return_value = mock_result

        response = client.get("/translate/task/test-processing-task")

        assert response.status_code == 200
        assert response.json()["status"] == "processing"


def test_get_task_status_success():
    """Test getting task status when task completed successfully."""
    with patch('app.api.translator_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {
            'state': 'SUCCESS',
            'result': {
                'translated': 'Halo, habari yako?',
                'processing_time': 1.5,
                'model_info': {'model': 'test-model'},
                'timestamp': '2024-01-01T12:00:00'
            }
        })()
        mock_async.return_value = mock_result

        response = client.get("/translate/task/test-success-task")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["result"]["translated"] == "Halo, habari yako?"


def test_get_task_status_failure():
    """Test getting task status when task failed."""
    with patch('app.api.translator_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {
            'state': 'FAILURE',
            'info': Exception("Task failed with error")
        })()
        mock_async.return_value = mock_result

        response = client.get("/translate/task/test-failed-task")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "error" in data


def test_get_task_status_other_state():
    """Test getting task status when task is in other state."""
    with patch('app.api.translator_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {'state': 'RETRY'})()
        mock_async.return_value = mock_result

        response = client.get("/translate/task/test-retry-task")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "retry"


def test_get_task_status_exception():
    """Test getting task status when exception occurs."""
    with patch('app.api.translator_routes.AsyncResult') as mock_async:
        mock_async.side_effect = Exception("Connection error")

        response = client.get("/translate/task/test-exception-task")

        assert response.status_code == 500
        assert "Error checking task" in response.json()["detail"]


def test_get_translation_info_api_server_mode():
    """Test getting translation info in API server mode."""
    with patch('app.api.translator_routes.is_api_server_mode', return_value=True):
        response = client.get("/translate/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "api_server_mode"
        assert "Celery workers" in data["message"]


def test_translation_demo_endpoint_success():
    """Test the /translate/demo endpoint for a successful task submission."""
    with patch('app.api.translator_routes.is_api_server_mode', return_value=False), \
         patch('app.api.translator_routes.model_loader') as mock_loader, \
         patch('app.api.translator_routes.translation_translate_task.apply_async') as mock_task:
        mock_loader.is_model_ready.return_value = True
        mock_result = type('obj', (object,), {'id': 'test_demo_task_123'})()
        mock_task.return_value = mock_result

        response = client.post("/translate/demo")

        # Demo endpoint returns 200 OK (its default status code)
        assert response.status_code == 200
        response_json = response.json()
        assert "task_id" in response_json
        assert response_json["status"] == "queued"