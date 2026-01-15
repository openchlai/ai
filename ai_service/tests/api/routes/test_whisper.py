import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from fastapi import FastAPI
from app.api.whisper_routes import router
import io

from app.main import app


client = TestClient(app)

# --- Mock Data and Helper Functions ---

MOCK_TRANSCRIPT = "This is a test transcription."
MOCK_MODEL_INFO = {
    "name": "mock-whisper-v1.0",
    "version": "1.0",
    "last_updated": "2024-01-01T12:00:00Z"
}
MOCK_LANGUAGES = {"en": "English", "sw": "Swahili"}

# Create a mock audio file for testing
def create_mock_audio_file(filename="test.wav", content=b"mock audio data"):
    file_like_object = io.BytesIO(content)
    file_like_object.name = filename
    return file_like_object

# --- Tests for the /whisper/transcribe endpoint ---

def test_transcribe_success_with_language():
    """Test successful audio transcription with a specified language."""
    mock_audio_file = create_mock_audio_file()
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_whisper = mock_loader.models.get.return_value

        mock_whisper.transcribe_audio_bytes.return_value = MOCK_TRANSCRIPT
        mock_whisper.get_model_info.return_value = MOCK_MODEL_INFO
        
        # Test using multipart/form-data
        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", mock_audio_file, "audio/wav")},
            data={"language": "en"}
        )
        
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["transcript"] == MOCK_TRANSCRIPT
        assert response_json["language"] == "en"
        assert "processing_time" in response_json
        assert "audio_info" in response_json
        assert response_json["audio_info"]["filename"] == "test.wav"

def test_transcribe_success_auto_detect():
    """Test successful transcription without specifying a language."""
    mock_audio_file = create_mock_audio_file(filename="test_auto.mp3")
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_whisper = mock_loader.models.get.return_value

        mock_whisper.transcribe_audio_bytes.return_value = MOCK_TRANSCRIPT
        mock_whisper.get_model_info.return_value = MOCK_MODEL_INFO

        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("test_auto.mp3", mock_audio_file, "audio/mpeg")}
        )
        
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["transcript"] == MOCK_TRANSCRIPT
        assert response_json["language"] is None  # Auto-detection is handled by the model, so we expect None here if not passed
        assert response_json["audio_info"]["filename"] == "test_auto.mp3"

def test_transcribe_model_not_ready():
    """Test the case where the Whisper model is not ready."""
    mock_audio_file = create_mock_audio_file()
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", mock_audio_file, "audio/wav")}
        )
        
        assert response.status_code == 503
        assert response.json() == {"detail": "Whisper model not ready. Check /health/models for status."}

def test_transcribe_no_audio_file():
    """Test the case where no audio file is provided."""
    response = client.post("/whisper/transcribe")
    assert response.status_code == 422 # FastAPI's default validation error for missing fields

def test_transcribe_unsupported_format():
    """Test with an unsupported audio file format."""
    mock_audio_file = create_mock_audio_file(filename="unsupported.pdf")
    with patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        
        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("unsupported.pdf", mock_audio_file, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "Unsupported audio format" in response.json()["detail"]

def test_transcribe_file_too_large():
    """Test the case where the uploaded file exceeds the size limit."""
    # Create a mock file larger than 100MB
    large_content = b'a' * (101 * 1024 * 1024)
    mock_audio_file = create_mock_audio_file(content=large_content)
    
    with patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True

        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("large_file.wav", mock_audio_file, "audio/wav")}
        )
        
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]

def test_transcribe_exception_on_run():
    """Test the case where an unexpected exception occurs during transcription."""
    mock_audio_file = create_mock_audio_file()
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_whisper = mock_loader.models.get.return_value

        mock_whisper.transcribe_audio_bytes.side_effect = Exception("Mock transcription error")

        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", mock_audio_file, "audio/wav")}
        )
        
        assert response.status_code == 500
        assert response.json()["detail"] == "Transcription failed: Mock transcription error"

# --- Tests for the /whisper/info endpoint ---

def test_get_whisper_info_ready():
    """Test the /whisper/info endpoint when the model is ready."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_whisper = mock_loader.models.get.return_value
        mock_whisper.get_model_info.return_value = MOCK_MODEL_INFO
        
        response = client.get("/whisper/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["model_info"] == MOCK_MODEL_INFO

def test_get_whisper_info_not_ready():
    """Test the /whisper/info endpoint when the model is not ready."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.get("/whisper/info")
        
        assert response.status_code == 200
        assert response.json()["status"] == "not_ready"
        assert "message" in response.json()

# --- Tests for the /whisper/languages endpoint ---

def test_get_supported_languages_ready():
    """Test the /whisper/languages endpoint when the model is ready."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_whisper = mock_loader.models.get.return_value
        mock_whisper.get_supported_languages.return_value = MOCK_LANGUAGES
        
        response = client.get("/whisper/languages")
        
        assert response.status_code == 200
        assert response.json()["supported_languages"] == MOCK_LANGUAGES
        assert "total_supported" in response.json()

def test_get_supported_languages_not_ready():
    """Test the /whisper/languages endpoint when the model is not ready."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = False
        
        response = client.get("/whisper/languages")
        
        assert response.status_code == 200
        assert response.json()["error"] == "Whisper model not ready"

# --- Tests for the /whisper/demo endpoint ---

def test_whisper_demo_endpoint():
    """Test the /whisper/demo endpoint returns a 200 OK and valid data structure."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_whisper = mock_loader.models.get.return_value
        mock_whisper.get_model_info.return_value = MOCK_MODEL_INFO
        mock_whisper.get_supported_languages.return_value = MOCK_LANGUAGES
        
        response = client.post("/whisper/demo")
        
        assert response.status_code == 200
        response_json = response.json()
        assert "demo_info" in response_json
        assert "model_status" in response_json
        assert "supported_languages" in response_json
        assert response_json["model_status"]["status"] == "ready"
        assert response_json["supported_languages"]["supported_languages"] == MOCK_LANGUAGES