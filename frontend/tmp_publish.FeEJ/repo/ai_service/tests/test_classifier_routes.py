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
    Test successful classification with a valid narrative.
    We mock the model_loader to simulate a ready and functioning model.
    """
    with patch('app.api.classifier_route.model_loader') as mock_loader:
        # Configure the mock to simulate a ready model
        mock_loader.is_model_ready.return_value = True
        mock_classifier = mock_loader.models.get.return_value
        
        # Configure the mock classifier's methods
        mock_classifier.classify.return_value = MOCK_CLASSIFICATION
        mock_classifier.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.post("/classifier/classify", json={"narrative": VALID_NARRATIVE})
        
        assert response.status_code == 200
        response_json = response.json()
        
        # Assert that the classification data is correct
        assert response_json["main_category"] == MOCK_CLASSIFICATION["main_category"]
        assert response_json["sub_category"] == MOCK_CLASSIFICATION["sub_category"]
        assert response_json["intervention"] == MOCK_CLASSIFICATION["intervention"]
        assert response_json["priority"] == MOCK_CLASSIFICATION["priority"]
        
        # Assert dynamic fields exist and have correct types
        assert "processing_time" in response_json
        assert isinstance(response_json["processing_time"], float)
        assert "timestamp" in response_json
        assert isinstance(response_json["timestamp"], str)

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
    Test the case where the classifier model is not ready.
    The endpoint should return a 503 Service Unavailable error.
    """
    with patch('app.api.classifier_route.model_loader') as mock_loader:
        # Configure the mock to simulate the model not being ready
        mock_loader.is_model_ready.return_value = False
        
        response = client.post("/classifier/classify", json={"narrative": VALID_NARRATIVE})
        
        assert response.status_code == 503
        assert response.json() == {"detail": "Classifier model not ready. Check /health/models for status."}

def test_classify_exception_on_run():
    """
    Test the case where an unexpected exception occurs during classification.
    The endpoint should return a 500 Internal Server Error.
    """
    with patch('app.api.classifier_route.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_classifier = mock_loader.models.get.return_value
        
        # Configure the mock classifier to raise an exception
        mock_classifier.classify.side_effect = Exception("Mock classification error")

        response = client.post("/classifier/classify", json={"narrative": VALID_NARRATIVE})
        
        assert response.status_code == 500
        assert response.json()["detail"] == "Classification failed: Mock classification error"

