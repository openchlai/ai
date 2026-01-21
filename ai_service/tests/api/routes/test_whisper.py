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


# Additional tests for better coverage

def test_transcribe_api_server_mode():
    """Test transcription in API server mode (delegates to Celery worker)."""
    mock_audio_file = create_mock_audio_file()
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=True), \
         patch('app.api.whisper_routes.whisper_transcribe_task.apply_async') as mock_task:
        mock_result = type('obj', (object,), {'id': 'test-whisper-task-123'})()
        mock_task.return_value = mock_result

        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", mock_audio_file, "audio/wav")},
            data={"language": "sw"}
        )

        assert response.status_code == 200
        response_json = response.json()
        assert "task_id" in response_json
        assert response_json["task_id"] == "test-whisper-task-123"
        assert response_json["status"] == "queued"


def test_transcribe_model_not_available():
    """Test transcription when model instance is None in standalone mode.
    The HTTPException(503) from inside try block gets caught and wrapped in 500 error.
    """
    mock_audio_file = create_mock_audio_file()
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None  # Model instance not found

        response = client.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", mock_audio_file, "audio/wav")}
        )

        # HTTPException(503) inside try gets caught and wrapped in 500
        assert response.status_code == 500
        assert "not available" in response.json()["detail"]


def test_get_task_status_pending():
    """Test getting task status when task is pending."""
    with patch('app.api.whisper_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {'state': 'PENDING'})()
        mock_async.return_value = mock_result

        response = client.get("/whisper/task/test-pending-task")

        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        assert response.json()["progress"]["message"] == "Task is queued"


def test_get_task_status_processing():
    """Test getting task status when task is processing."""
    with patch('app.api.whisper_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {'state': 'PROCESSING', 'info': {"progress": 50}})()
        mock_async.return_value = mock_result

        response = client.get("/whisper/task/test-processing-task")

        assert response.status_code == 200
        assert response.json()["status"] == "processing"


def test_get_task_status_success():
    """Test getting task status when task completed successfully."""
    with patch('app.api.whisper_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {
            'state': 'SUCCESS',
            'result': {
                'transcript': 'This is a test transcription.',
                'language': 'en',
                'processing_time': 2.5,
                'model_info': {'model': 'whisper-large'},
                'timestamp': '2024-01-01T12:00:00',
                'audio_info': {'filename': 'test.wav', 'file_size_mb': 1.5}
            }
        })()
        mock_async.return_value = mock_result

        response = client.get("/whisper/task/test-success-task")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["result"]["transcript"] == "This is a test transcription."


def test_get_task_status_failure():
    """Test getting task status when task failed."""
    with patch('app.api.whisper_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {
            'state': 'FAILURE',
            'info': Exception("Transcription failed")
        })()
        mock_async.return_value = mock_result

        response = client.get("/whisper/task/test-failed-task")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "error" in data


def test_get_task_status_other_state():
    """Test getting task status when task is in other state."""
    with patch('app.api.whisper_routes.AsyncResult') as mock_async:
        mock_result = type('obj', (object,), {'state': 'RETRY'})()
        mock_async.return_value = mock_result

        response = client.get("/whisper/task/test-retry-task")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "retry"


def test_get_task_status_exception():
    """Test getting task status when exception occurs."""
    with patch('app.api.whisper_routes.AsyncResult') as mock_async:
        mock_async.side_effect = Exception("Connection error")

        response = client.get("/whisper/task/test-exception-task")

        assert response.status_code == 500
        assert "Error checking task" in response.json()["detail"]


def test_get_whisper_info_api_server_mode():
    """Test getting whisper info in API server mode."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=True):
        response = client.get("/whisper/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "api_server_mode"
        assert "Celery workers" in data["message"]


def test_get_whisper_info_model_not_found():
    """Test the /whisper/info endpoint when the model is not found."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None

        response = client.get("/whisper/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "not found" in data["message"]


def test_get_supported_languages_api_server_mode():
    """Test getting supported languages in API server mode."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=True):
        response = client.get("/whisper/languages")

        assert response.status_code == 200
        data = response.json()
        assert "supported_languages" in data
        assert data["mode"] == "api_server"


def test_get_supported_languages_model_not_found():
    """Test getting supported languages when model is not found."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=False), \
         patch('app.api.whisper_routes.model_loader') as mock_loader:
        mock_loader.is_model_ready.return_value = True
        mock_loader.models.get.return_value = None

        response = client.get("/whisper/languages")

        assert response.status_code == 200
        data = response.json()
        assert data["error"] == "Whisper model not available"


def test_whisper_demo_api_server_mode():
    """Test the /whisper/demo endpoint in API server mode."""
    with patch('app.api.whisper_routes.is_api_server_mode', return_value=True):
        response = client.post("/whisper/demo")

        assert response.status_code == 200
        response_json = response.json()
        assert "demo_info" in response_json
        assert response_json["model_status"]["status"] == "api_server_mode"