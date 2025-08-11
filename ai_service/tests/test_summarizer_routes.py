import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI
from app.api.summarizer_routes import router
from app.main import app

client = TestClient(app)

# --- Mock Data ---

VALID_TEXT = "Jane called the helpline about her neigbour's son. He has not been attending scool, and he looked out of diet and sick. his parents have not been how for three weeks"
EMPTY_TEXT = ""

# Mock summary result
MOCK_SUMMARY = "Jane reported that a boy was neglected by parents and needs immediate care."

# Mocked model info
MOCK_MODEL_INFO = {
    "name": "mock-summarizer-v1.0",
    "version": "1.0",
    "last_updated": "2024-01-01T12:00:00Z"
}


def test_summarize_success():
    """
    Test successful text summarization with a valid text.
    We mock the model_loader to simulate a ready and functioning model.
    """
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_summarizer = mock_loader.models.get.return_value
        
        mock_summarizer.summarize.return_value = MOCK_SUMMARY
        mock_summarizer.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.post("/summarizer/summarize", json={"text": VALID_TEXT, "max_length": 60})
        
        assert response.status_code == 200
        response_json = response.json()
        
        assert response_json["summary"] == MOCK_SUMMARY
        
        assert "processing_time" in response_json
        assert isinstance(response_json["processing_time"], float)
        assert "timestamp" in response_json
        assert isinstance(response_json["timestamp"], str)
        assert response_json["model_info"] == MOCK_MODEL_INFO

def test_summarize_empty_text():
    """
    Test the case where the text input is an empty string.
    The endpoint should return a 400 Bad Request error.
    """
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True # Model is ready for this check
        
        response = client.post("/summarizer/summarize", json={"text": EMPTY_TEXT})
        
        assert response.status_code == 400
        assert response.json() == {"detail": "Text input cannot be empty"}

def test_summarize_model_not_ready():
    """
    Test the case where the summarizer model is not ready.
    The endpoint should return a 503 Service Unavailable error.
    """
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.post("/summarizer/summarize", json={"text": VALID_TEXT})
        
        assert response.status_code == 503
        assert response.json() == {"detail": "Summarizer model not ready. Check /health/models for status."}

def test_summarize_model_not_available():
    """
    Test the case where the summarizer model is not found in model_loader.models.
    The endpoint should return a 503 Service Unavailable error.
    """
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None # Simulate model not being found
        
        response = client.post("/summarizer/summarize", json={"text": VALID_TEXT})
        
        assert response.status_code == 503
        assert response.json() == {"detail": "Summarizer model not available"}

def test_summarize_exception_on_run():
    """
    Test the case where an unexpected exception occurs during summarization.
    The endpoint should return a 500 Internal Server Error.
    """
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_summarizer = mock_loader.models.get.return_value
        
        # Configure the mock summarizer to raise an exception
        mock_summarizer.summarize.side_effect = Exception("Mock summarization error")

        response = client.post("/summarizer/summarize", json={"text": VALID_TEXT})
        
        assert response.status_code == 500
        assert response.json()["detail"] == "Summarization failed: Mock summarization error"



def test_get_summarizer_info_ready():
    """Test the /summarizer/info endpoint when the model is ready."""
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_summarizer = mock_loader.models.get.return_value
        mock_summarizer.get_model_info.return_value = MOCK_MODEL_INFO
        
        response = client.get("/summarizer/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["model_info"] == MOCK_MODEL_INFO

def test_get_summarizer_info_not_ready():
    """Test the /summarizer/info endpoint when the model is not ready."""
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.get("/summarizer/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
        assert "message" in response.json()

def test_get_summarizer_info_not_found():
    """Test the /summarizer/info endpoint when the model is not found."""
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True # Simulate that it passed the initial check
        mock_loader.models.get.return_value = None # But the model object itself is None
        
        response = client.get("/summarizer/info")
        
        assert response.status_code == 200 # Info endpoint returns 200 even if model not found
        assert response.json()["status"] == "error"
        assert "message" in response.json()



def test_summarizer_demo_endpoint_success():
    """Test the /summarizer/demo endpoint for a successful run."""
    with patch('app.api.summarizer_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_summarizer = mock_loader.models.get.return_value
        
        mock_summarizer.summarize.return_value = MOCK_SUMMARY
        mock_summarizer.get_model_info.return_value = MOCK_MODEL_INFO
        
        response = client.post("/summarizer/demo")
        
        assert response.status_code == 200
        response_json = response.json()
        assert "summary" in response_json
        assert "processing_time" in response_json
        assert "model_info" in response_json
        assert response_json["summary"] == MOCK_SUMMARY 