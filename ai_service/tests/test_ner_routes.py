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
    """Test successful NER extraction with a valid text and default flat=True."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_ner_model = mock_loader.models.get.return_value
        
        mock_ner_model.extract_entities.return_value = MOCK_FLAT_ENTITIES
        mock_ner_model.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.post("/ner/extract", json={"text": VALID_TEXT})
        
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["entities"] == MOCK_FLAT_ENTITIES
        assert "processing_time" in response_json
        assert isinstance(response_json["processing_time"], float)
        assert response_json["model_info"] == MOCK_MODEL_INFO

def test_extract_success_grouped():
    """Test successful NER extraction with flat=False."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_ner_model = mock_loader.models.get.return_value
        
        mock_ner_model.extract_entities.return_value = MOCK_GROUPED_ENTITIES
        mock_ner_model.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.post("/ner/extract", json={"text": VALID_TEXT, "flat": False})
        
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["entities"] == MOCK_GROUPED_ENTITIES

def test_extract_empty_text():
    """Test the case where the text is an empty string."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        
        response = client.post("/ner/extract", json={"text": EMPTY_TEXT})
        
        assert response.status_code == 400
        assert response.json() == {"detail": "Text input cannot be empty"}

def test_extract_model_not_ready():
    """Test the case where the NER model is not ready."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.post("/ner/extract", json={"text": VALID_TEXT})
        
        assert response.status_code == 503
        assert response.json() == {"detail": "NER model not ready. Check /health/models for status."}

def test_extract_exception_on_run():
    """Test the case where an unexpected exception occurs during extraction."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_ner_model = mock_loader.models.get.return_value
        
        mock_ner_model.extract_entities.side_effect = Exception("Mock NER error")

        response = client.post("/ner/extract", json={"text": VALID_TEXT})
        
        assert response.status_code == 500
        assert response.json()["detail"] == "NER processing failed: Mock NER error"


def test_get_ner_info_ready():
    """Test the /ner/info endpoint when the model is ready."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_ner_model = mock_loader.models.get.return_value
        mock_ner_model.get_model_info.return_value = MOCK_MODEL_INFO
        
        response = client.get("/ner/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["model_info"] == MOCK_MODEL_INFO

def test_get_ner_info_not_ready():
    """Test the /ner/info endpoint when the model is not ready."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.get("/ner/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
        assert "message" in response.json()


def test_ner_demo_endpoint_success():
    """Test the /ner/demo endpoint for a successful run."""
    with patch('app.api.ner_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_ner_model = mock_loader.models.get.return_value
        
        mock_ner_model.extract_entities.return_value = MOCK_FLAT_ENTITIES
        mock_ner_model.get_model_info.return_value = MOCK_MODEL_INFO
        
        response = client.post("/ner/demo")
        
        assert response.status_code == 200
        response_json = response.json()
        assert "entities" in response_json
        assert "processing_time" in response_json
        assert "model_info" in response_json