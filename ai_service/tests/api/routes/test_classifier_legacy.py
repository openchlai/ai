import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import os
import sys



# Add project root to sys.path for import resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
client = TestClient(app)


# Mocked classification result
MOCK_CLASSIFICATION = {
    "main_category": "Child Protection",
    "sub_category": "Physical Abuse",
    "intervention": "Emergency",
    "priority": "High"
}

# Mocked model info
MOCK_MODEL_INFO = {
    "name": "mock-classifier-v1.0",
    "version": "1.0",
    "last_updated": "2024-01-01T12:00:00Z"
}

VALID_NARRATIVE = "A child reported physical abuse at home."
EMPTY_NARRATIVE = ""


def test_classify_success():
    """
    Test successful classification task submission with a valid narrative.
    """
    with patch('app.api.classifier_route.classifier_classify_task.apply_async') as mock_task:
        mock_result = type('obj', (object,), {'id': 'test_classify_task_123'})()
        mock_task.return_value = mock_result

        response = client.post("/classifier/classify", json={"narrative": VALID_NARRATIVE})

        assert response.status_code == 200
        response_json = response.json()

        # Endpoint now returns task_id for async processing
        assert "task_id" in response_json
        assert response_json["task_id"] == "test_classify_task_123"
        assert response_json["status"] == "queued"
        assert "status_endpoint" in response_json

def test_classify_empty_narrative():
    """
    Test the case where the narrative is an empty string.
    The endpoint should return a 400 Bad Request error.
    """
    with patch('app.api.classifier_route.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True  # Model is ready.
        
        response = client.post("/classifier/classify", json={"narrative": EMPTY_NARRATIVE})
        
    assert response.status_code == 400
    assert response.json() == {"detail": "Narrative input cannot be empty"}


def test_classify_model_not_ready():
    """
    Test the case where the classifier model is not ready in standalone mode.
    The endpoint should return a 503 Service Unavailable error.
    """
    with patch('app.api.classifier_route.is_api_server_mode', return_value=False), \
         patch('app.api.classifier_route.model_loader') as mock_loader:
        # Configure the mock to simulate the model not being ready
        mock_loader.is_model_ready.return_value = False

        response = client.post("/classifier/classify", json={"narrative": VALID_NARRATIVE})

        assert response.status_code == 503
        assert response.json() == {"detail": "Classifier model not ready. Check /health/models for status."}

def test_classify_exception_on_run():
    """
    Test the case where an unexpected exception occurs during task submission.
    The endpoint should return a 500 Internal Server Error.
    """
    with patch('app.api.classifier_route.classifier_classify_task.apply_async') as mock_task:
        mock_task.side_effect = Exception("Task submission failed")

        response = client.post("/classifier/classify", json={"narrative": VALID_NARRATIVE})

        assert response.status_code == 500
        assert "Failed to submit task" in response.json()["detail"]

