import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
client = TestClient(app)

# --- Mock Data ---
VALID_TEXT = "A child reported physical abuse at home by John Doe."
EMPTY_TEXT = ""

MOCK_FLAT_ENTITIES = [
    {"text": "John Doe", "label": "PERSON", "start": 39, "end": 47, "confidence": 0.95}
]

MOCK_GROUPED_ENTITIES = {
    "PERSON": ["John Doe"]
}

# Mock model info
MOCK_MODEL_INFO = {
    "name": "mock-ner-v1.0",
    "version": "1.0",
    "last_updated": "2024-01-01T12:00:00Z"
}


def test_extract_success_flat():
    """Test successful NER extraction task submission with flat=True."""
    with patch('app.api.ner_routes.ner_extract_task.apply_async') as mock_task:
        mock_result = type('obj', (object,), {'id': 'test_ner_task_123'})()
        mock_task.return_value = mock_result

        response = client.post("/ner/extract", json={"text": VALID_TEXT})

        assert response.status_code == 202
        response_json = response.json()
        # Endpoint now returns task_id for async processing
        assert "task_id" in response_json
        assert response_json["task_id"] == "test_ner_task_123"
        assert response_json["status"] == "queued"
        assert "status_endpoint" in response_json

def test_extract_success_grouped():
    """Test successful NER extraction task submission with flat=False."""
    with patch('app.api.ner_routes.ner_extract_task.apply_async') as mock_task:
        mock_result = type('obj', (object,), {'id': 'test_ner_task_456'})()
        mock_task.return_value = mock_result

        response = client.post("/ner/extract", json={"text": VALID_TEXT, "flat": False})

        assert response.status_code == 202
        response_json = response.json()
        assert "task_id" in response_json
        assert response_json["status"] == "queued"

def test_extract_empty_text():
    """Test the case where the text is an empty string."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        
        response = client.post("/ner/extract", json={"text": EMPTY_TEXT})

        assert response.status_code == 400
        assert "Text input cannot be empty" in response.json()["detail"]["error"]["message"]

def test_extract_model_not_ready():
    """Test the case where the NER model is not ready in standalone mode."""
    with patch('app.api.ner_routes.is_api_server_mode', return_value=False), \
         patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False

        response = client.post("/ner/extract", json={"text": VALID_TEXT})

        assert response.status_code == 503
        assert "NER model not ready" in response.json()["detail"]["error"]["message"]

def test_extract_exception_on_run():
    """Test the case where an unexpected exception occurs during task submission."""
    with patch('app.api.ner_routes.ner_extract_task.apply_async') as mock_task:
        mock_task.side_effect = Exception("Task submission failed")

        response = client.post("/ner/extract", json={"text": VALID_TEXT})

        assert response.status_code == 500
        assert "Failed to submit NER task" in response.json()["detail"]["error"]["message"]


def test_get_ner_info_ready():
    """Test the /ner/info endpoint when the model is ready."""
    with patch('app.api.ner_routes.is_api_server_mode', return_value=False), \
         patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_ner_model = mock_loader.models.get.return_value
        mock_ner_model.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.get("/ner/info")

        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["model_info"] == MOCK_MODEL_INFO

def test_get_ner_info_not_ready():
    """Test the /ner/info endpoint when the model is not ready."""
    with patch('app.api.ner_routes.is_api_server_mode', return_value=False), \
         patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False

        response = client.get("/ner/info")

        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
        assert "message" in response.json()


def test_ner_demo_endpoint_success():
    """Test the /ner/demo endpoint for a successful task submission."""
    with patch('app.api.ner_routes.ner_extract_task.apply_async') as mock_task:
        mock_result = type('obj', (object,), {'id': 'test_demo_task_789'})()
        mock_task.return_value = mock_result

        response = client.post("/ner/demo")

        assert response.status_code == 200
        response_json = response.json()
        # Demo endpoint also returns task_id now
        assert "task_id" in response_json
        assert response_json["status"] == "queued"



def test_get_task_status_success():
    """Test retrieving a successful NER task result."""
    with patch('app.api.ner_routes.AsyncResult') as mock_async_result:
        # Mocking a successful Celery result
        mock_instance = mock_async_result.return_value
        mock_instance.state = 'SUCCESS'
        mock_instance.result = {
            'entities': MOCK_FLAT_ENTITIES,
            'processing_time': 0.5,
            'model_info': MOCK_MODEL_INFO,
            'timestamp': "2024-01-01T12:00:00Z"
        }

        response = client.get("/ner/task/test_task_123")

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["result"]["entities"] == MOCK_FLAT_ENTITIES

def test_get_task_status_processing():
    """Test retrieving a task that is still processing."""
    with patch('app.api.ner_routes.AsyncResult') as mock_async_result:
        mock_instance = mock_async_result.return_value
        mock_instance.state = 'PROCESSING'
        mock_instance.info = {"percent": 50}

        response = client.get("/ner/task/test_task_123")

        assert response.status_code == 200
        assert response.json()["status"] == "processing"
        assert response.json()["progress"]["percent"] == 50

def test_get_task_status_failure():
    """Test retrieving a failed task."""
    with patch('app.api.ner_routes.AsyncResult') as mock_async_result:
        mock_instance = mock_async_result.return_value
        mock_instance.state = 'FAILURE'
        mock_instance.info = "Model Timeout Error"

        response = client.get("/ner/task/test_task_123")

        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        assert "Model Timeout Error" in response.json()["error"]


def test_get_task_status_pending():
    """Test retrieving a task that is still PENDING."""
    with patch('app.api.ner_routes.AsyncResult') as mock_async_result:
        mock_instance = mock_async_result.return_value
        mock_instance.state = 'PENDING'
        
        response = client.get("/ner/task/test_task_000")
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

def test_get_ner_info_api_mode():
    """Test /ner/info when running in API Server mode."""
    with patch('app.api.ner_routes.is_api_server_mode', return_value=True):
        response = client.get("/ner/info")
        assert response.status_code == 200
        assert response.json()["status"] == "api_server_mode"

def test_get_task_status_exception():
    """Test the exception handler in the status endpoint."""
    with patch('app.api.ner_routes.AsyncResult') as mock_async_result:
        mock_async_result.side_effect = Exception("Redis connection lost")
        
        response = client.get("/ner/task/test_task_error")
        assert response.status_code == 500
        assert "Error checking task status" in response.json()["detail"]

def test_get_task_status_other_state():
    """Test retrieving a task with an unhandled Celery state (Line 159)."""
    with patch('app.api.ner_routes.AsyncResult') as mock_async_result:
        mock_instance = mock_async_result.return_value
        # Mocking an uncommon state like 'REVOKED'
        mock_instance.state = 'REVOKED'
        
        response = client.get("/ner/task/test_task_revoked")
        assert response.status_code == 200
        assert response.json()["status"] == "revoked"
        assert "Task state: REVOKED" in response.json()["progress"]["message"]

def test_get_ner_info_model_instance_missing():
    """Test /ner/info when model is 'ready' but instance is None (Line 203)."""
    with patch('app.api.ner_routes.is_api_server_mode', return_value=False), \
         patch('app.api.ner_routes.model_loader') as mock_loader:
        
        # Simulate condition: loader thinks it is ready, but get() returns None
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None

        response = client.get("/ner/info")
        assert response.status_code == 200
        assert response.json()["status"] == "error"
        assert response.json()["message"] == "NER model not found"