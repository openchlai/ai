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
    """Test successful text translation with a valid text."""
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_translator = mock_loader.models.get.return_value
        
        mock_translator.translate.return_value = MOCK_TRANSLATED_TEXT
        mock_translator.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.post("/translate/", json={"text": VALID_TEXT})
        
        assert response.status_code == 200
        response_json = response.json()
        
        assert response_json["translated"] == MOCK_TRANSLATED_TEXT
        
        assert "processing_time" in response_json
        assert isinstance(response_json["processing_time"], float)
        assert "timestamp" in response_json
        assert isinstance(response_json["timestamp"], str)
        assert response_json["model_info"] == MOCK_MODEL_INFO

def test_translate_empty_text():
    """
    Test the case where the text input is an empty string.
    The endpoint should return a 400 Bad Request error.
    """
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True 
        
        response = client.post("/translate/", json={"text": EMPTY_TEXT})
        
        assert response.status_code == 400
        assert response.json() == {"detail": "Text input cannot be empty"}

def test_translate_model_not_ready():
    """
    Test the case where the translation model is not ready.
    The endpoint should return a 503 Service Unavailable error.
    """
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.post("/translate/", json={"text": VALID_TEXT})
        
        assert response.status_code == 503
        assert response.json() == {"detail": "Translation model not ready. Check /health/models for status."}

def test_translate_model_not_available():
    """
    Test the case where the translation model is not found in model_loader.models.
    The endpoint should return a 500 Internal Server Error due to the generic exception handler.
    """
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None # Simulate model not being found

        response = client.post("/translate/", json={"text": VALID_TEXT})

        assert response.status_code == 500

        assert response.json()["detail"] == "Translation failed: 503: Translator model not available"


        
def test_translate_exception_on_run():
    """
    Test the case where an unexpected exception occurs during translation.
    The endpoint should return a 500 Internal Server Error.
    """
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_translator = mock_loader.models.get.return_value
        

        mock_translator.translate.side_effect = Exception("Mock translation error")

        response = client.post("/translate/", json={"text": VALID_TEXT})
        
        assert response.status_code == 500
        assert response.json()["detail"] == "Translation failed: Mock translation error"


def test_get_translation_info_ready():
    """Test the /translate/info endpoint when the model is ready."""
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
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.get("/translate/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
        assert "message" in response.json()

def test_get_translation_info_not_found():
    """Test the /translate/info endpoint when the model is not found."""
    with patch('app.api.translator_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True 
        mock_loader.models.get.return_value = None 
        
        response = client.get("/translate/info")
        
        assert response.status_code == 200 
        assert response.json()["status"] == "error"
        assert "message" in response.json()