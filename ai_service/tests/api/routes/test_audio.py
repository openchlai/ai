"""
Tests for the audio API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from io import BytesIO
from app.main import app as fastapi_app
from app.db.session import get_db # Keep for consistency, though not directly used here
from fastapi import UploadFile, File, Depends # Import File and Depends for patching
# from app.api.audio_routes import process_audio_complete 
import os
import app.api.audio_routes
from datetime import datetime, timedelta
import asyncio # Import asyncio for mocking sleep
import json # Import json for parsing streamed data

# Mock the get_db dependency, as it might be used by other parts of the app
mock_db = MagicMock()
def get_db_override():
    return mock_db
fastapi_app.dependency_overrides[get_db] = get_db_override

client = TestClient(fastapi_app)

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test."""
    mock_db.reset_mock()
    fastapi_app.dependency_overrides = {} # Ensure overrides are reset

@pytest.fixture
def mock_celery_tasks():
    """Fixture to mock Celery tasks."""
    with patch('app.api.audio_routes.process_audio_task') as mock_process_audio_task, \
         patch('app.api.audio_routes.process_audio_quick_task') as mock_process_audio_quick_task, \
         patch('app.api.audio_routes.celery_app') as mock_celery_app, \
         patch('app.api.audio_routes.celery_monitor') as mock_celery_monitor, \
         patch('app.tasks.health_tasks.health_check_models') as mock_health_check_models, \
         patch('app.api.audio_routes.redis_task_client') as mock_redis_task_client, \
         patch('app.api.audio_routes.audio_streaming') as mock_audio_streaming, \
         patch('asyncio.sleep', return_value=None) as mock_async_sleep: # Mock asyncio.sleep
        
        # Mock Celery task methods
        mock_task1 = MagicMock()
        mock_task1.id = "mock_task_id_1"
        mock_process_audio_task.delay.return_value = mock_task1
        
        mock_task2 = MagicMock()
        mock_task2.id = "mock_task_id_2"
        mock_process_audio_quick_task.delay.return_value = mock_task2
        
        # Mock AsyncResult for task status checks
        mock_async_result = MagicMock()
        mock_async_result.state = "PENDING"
        mock_async_result.info = {}
        mock_async_result.result = None
        mock_celery_app.AsyncResult.return_value = mock_async_result

        # Mock Celery control for revoke and inspect
        mock_celery_app.control.revoke.return_value = None
        mock_inspect = MagicMock()
        mock_inspect.stats.return_value = {"worker1": {"total": 10}}
        mock_inspect.active.return_value = {"worker1": []}
        mock_inspect.scheduled.return_value = {"worker1": []}
        mock_inspect.reserved.return_value = {"worker1": []}
        mock_celery_app.control.inspect.return_value = mock_inspect

        # Mock celery_monitor
        mock_celery_monitor.get_active_tasks.return_value = {"active_tasks": []}
        mock_celery_monitor.get_worker_stats.return_value = {}

        # Mock health_check_models
        mock_health_check_models.return_value = {"status": "ok"}

        # Mock redis_task_client
        mock_redis_task_client.hgetall.return_value = {}

        # Mock audio_streaming
        mock_audio_streaming.subscribe_to_task.return_value = MagicMock() # For async for

        yield {
            "process_audio_task": mock_process_audio_task,
            "process_audio_quick_task": mock_process_audio_quick_task,
            "celery_app": mock_celery_app,
            "celery_monitor": mock_celery_monitor,
            "health_check_models": mock_health_check_models,
            "redis_task_client": mock_redis_task_client,
            "audio_streaming": mock_audio_streaming,
            "mock_async_result": mock_async_result,
            "mock_inspect": mock_inspect,
            "mock_async_sleep": mock_async_sleep
        }

# Helper function to create a mock UploadFile
def create_mock_upload_file(filename: str, content: bytes, content_type: str = "audio/wav"):
    return UploadFile(filename=filename, file=BytesIO(content))

def parse_sse_events(response_iterator):

    events = []

    buffer = b""

    for chunk in response_iterator:

        buffer += chunk

        # Process all complete events in the buffer

        while b"\n\n" in buffer:

            event_block, rest = buffer.split(b"\n\n", 1)

            buffer = rest # Keep the rest in the buffer for the next iteration



            # Each event block can have multiple lines, but only 'data:' lines are relevant for JSON

            data_lines = [line for line in event_block.split(b"\n") if line.startswith(b"data:")]

            

            for data_line in data_lines:

                try:

                    json_str = data_line.decode("utf-8").lstrip("data:").strip()

                    event_data = json.loads(json_str)

                    events.append(event_data)

                except json.JSONDecodeError:

                    # Log or handle malformed JSON, but don't stop processing

                    pass

    return events

# --- Tests for POST /audio/process ---
def test_process_audio_complete_background_success(mock_celery_tasks):
    """Test successful background audio processing."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    response = client.post(
        "/audio/process",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True,
            "background": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id_1"
    assert data["status"] == "queued"  # Actual code returns "queued"
    mock_celery_tasks["process_audio_task"].delay.assert_called_once_with(
        audio_bytes=audio_content,
        filename="test.wav",
        language="en",
        include_translation=True,
        include_insights=True
    )

@pytest.mark.parametrize("lang_input, expected_lang", [
    (None, "sw"),
    ("", "sw"),
    ("string", "sw"),
    ("en", "en"),
    ("auto", "auto"),
])
def test_process_audio_complete_language_handling(mock_celery_tasks, lang_input, expected_lang):
    """Test language parameter handling for /audio/process."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    data = {
        "include_translation": True,
        "include_insights": True,
        "background": True
    }
    if lang_input is not None:
        data["language"] = lang_input

    response = client.post(
        "/audio/process",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data=data
    )

    assert response.status_code == 200
    mock_celery_tasks["process_audio_task"].delay.assert_called_once()
    call_args = mock_celery_tasks["process_audio_task"].delay.call_args[1]
    assert call_args["language"] == expected_lang

def test_process_audio_complete_no_file_provided(mock_celery_tasks):
    """Test /audio/process with no audio file provided at all."""
    response = client.post(
        "/audio/process",
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True,
            "background": True
        }
    )
    assert response.status_code == 422 # Expect 422 from FastAPI validation
    assert "Field required" in response.json()["detail"][0]["msg"]


def test_process_audio_complete_unsupported_format(mock_celery_tasks):
    """Test /audio/process with an unsupported audio format."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.mp4", audio_content) # Unsupported format

    response = client.post(
        "/audio/process",
        files={"audio": ("test.mp4", BytesIO(audio_content), "video/mp4")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True,
            "background": True
        }
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]

def test_process_audio_complete_file_too_large(mock_celery_tasks):
    """Test /audio/process with an audio file exceeding the max size."""
    # Create a file larger than 100MB
    large_audio_content = b"a" * (100 * 1024 * 1024 + 1) 
    mock_file = create_mock_upload_file("large.wav", large_audio_content)

    response = client.post(
        "/audio/process",
        files={"audio": ("large.wav", BytesIO(large_audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True,
            "background": True
        }
    )
    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]

def test_process_audio_complete_synchronous_success(mock_celery_tasks):
    """Test successful synchronous audio processing."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)
    
    # The expected result must conform to TaskResponse
    expected_task_response = {
        "task_id": "sync_task_id",
        "status": "completed",
        "message": "Synchronous processing complete",
        "estimated_time": "N/A",
        "status_endpoint": "/audio/task/sync_task_id"
    }
    mock_celery_tasks["process_audio_task"].return_value = expected_task_response # For synchronous call

    response = client.post(
        "/audio/process",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True,
            "background": False # Synchronous call
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data == expected_task_response # Direct comparison now works
    mock_celery_tasks["process_audio_task"].assert_called_once_with(
        audio_bytes=audio_content,
        filename="test.wav",
        language="en",
        include_translation=True,
        include_insights=True
    )
    mock_celery_tasks["process_audio_task"].delay.assert_not_called() # Ensure delay was not called

def test_process_audio_complete_exception_handling(mock_celery_tasks):
    """Test /audio/process when an unexpected exception occurs."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)
    
    mock_celery_tasks["process_audio_task"].delay.side_effect = Exception("Celery submission failed")

    response = client.post(
        "/audio/process",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True,
            "background": True
        }
    )
    assert response.status_code == 500
    assert "Audio processing failed" in response.json()["detail"]

# --- Tests for POST /audio/analyze ---
def test_quick_audio_analysis_background_success(mock_celery_tasks):
    """Test successful background quick audio analysis."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    response = client.post(
        "/audio/analyze",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "background": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id_2"
    assert data["status"] == "queued"
    mock_celery_tasks["process_audio_quick_task"].delay.assert_called_once_with(
        audio_bytes=audio_content,
        filename="test.wav",
        language="en"
    )

@pytest.mark.parametrize("lang_input, expected_lang", [
    (None, "sw"),
    ("", "sw"),
    ("string", "sw"),
    ("en", "en"),
    ("auto", "auto"),
])
def test_quick_audio_analysis_language_handling(mock_celery_tasks, lang_input, expected_lang):
    """Test language parameter handling for /audio/analyze."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    data = {
        "background": True
    }
    if lang_input is not None:
        data["language"] = lang_input

    response = client.post(
        "/audio/analyze",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data=data
    )

    assert response.status_code == 200
    mock_celery_tasks["process_audio_quick_task"].delay.assert_called_once()
    call_args = mock_celery_tasks["process_audio_quick_task"].delay.call_args[1]
    assert call_args["language"] == expected_lang

def test_quick_audio_analysis_no_file_provided(mock_celery_tasks):
    """Test /audio/analyze with no audio file provided at all."""
    response = client.post(
        "/audio/analyze",
        data={
            "language": "en",
            "background": True
        }
    )
    assert response.status_code == 422 # Expect 422 from FastAPI validation
    assert "Field required" in response.json()["detail"][0]["msg"]

def test_quick_audio_analysis_unsupported_format(mock_celery_tasks):
    """Test /audio/analyze with an unsupported audio format."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.mp4", audio_content) # Unsupported format

    response = client.post(
        "/audio/analyze",
        files={"audio": ("test.mp4", BytesIO(audio_content), "video/mp4")},
        data={
            "language": "en",
            "background": True
        }
    )
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["detail"]

def test_quick_audio_analysis_file_too_large(mock_celery_tasks):
    """Test /audio/analyze with an audio file exceeding the max size (50MB)."""
    # Create a file larger than 50MB
    large_audio_content = b"a" * (50 * 1024 * 1024 + 1) 
    mock_file = create_mock_upload_file("large.wav", large_audio_content)

    response = client.post(
        "/audio/analyze",
        files={"audio": ("large.wav", BytesIO(large_audio_content), "audio/wav")},
        data={
            "language": "en",
            "background": True
        }
    )
    assert response.status_code == 400
    assert "File too large for quick analysis" in response.json()["detail"]

def test_quick_audio_analysis_synchronous_success(mock_celery_tasks):
    """Test successful synchronous quick audio analysis."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)
    
    expected_task_response = {
        "task_id": "sync_quick_task_id",
        "status": "completed",
        "message": "Synchronous quick analysis complete",
        "estimated_time": "N/A",
        "status_endpoint": "/audio/task/sync_quick_task_id"
    }
    mock_celery_tasks["process_audio_quick_task"].return_value = expected_task_response # For synchronous call

    response = client.post(
        "/audio/analyze",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "background": False # Synchronous call
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data == expected_task_response
    mock_celery_tasks["process_audio_quick_task"].assert_called_once_with(
        audio_bytes=audio_content,
        filename="test.wav",
        language="en"
    )
    mock_celery_tasks["process_audio_quick_task"].delay.assert_not_called()

def test_quick_audio_analysis_exception_handling(mock_celery_tasks):
    """Test /audio/analyze when an unexpected exception occurs."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)
    
    mock_celery_tasks["process_audio_quick_task"].delay.side_effect = Exception("Quick analysis submission failed")

    response = client.post(
        "/audio/analyze",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "background": True
        }
    )
    assert response.status_code == 500
    assert "Quick analysis failed" in response.json()["detail"]

# --- Tests for GET /audio/task/{task_id} ---
def test_get_task_status_pending(mock_celery_tasks):
    """Test getting task status for a PENDING task."""
    mock_celery_tasks["mock_async_result"].state = "PENDING"
    mock_celery_tasks["mock_async_result"].info = {}

    response = client.get("/audio/task/mock_task_id")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id"
    assert data["status"] == "queued"
    assert data["progress"] == 0
    assert "waiting" in data["message"]

def test_get_task_status_processing(mock_celery_tasks):
    """Test getting task status for a PROCESSING task."""
    mock_celery_tasks["mock_async_result"].state = "PROCESSING"
    mock_celery_tasks["mock_async_result"].info = {
        "progress": 50,
        "step": "transcription",
        "filename": "test.wav"
    }

    response = client.get("/audio/task/mock_task_id")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id"
    assert data["status"] == "processing"
    assert data["progress"] == 50
    assert data["current_step"] == "transcription"
    assert data["filename"] == "test.wav"

def test_get_task_status_success(mock_celery_tasks):
    """Test getting task status for a SUCCESS task."""
    mock_celery_tasks["mock_async_result"].state = "SUCCESS"
    mock_celery_tasks["mock_async_result"].result = {
        "transcription": "hello world",
        "processing_time": 10.5
    }

    response = client.get("/audio/task/mock_task_id")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id"
    assert data["status"] == "completed"
    assert data["progress"] == 100
    assert data["result"]["transcription"] == "hello world"
    assert data["processing_time"] == 10.5

def test_get_task_status_failure(mock_celery_tasks):
    """Test getting task status for a FAILURE task."""
    mock_celery_tasks["mock_async_result"].state = "FAILURE"
    mock_celery_tasks["mock_async_result"].info = {
        "exc_type": "ValueError",
        "exc_message": "Invalid audio",
        "filename": "bad.wav"
    }

    response = client.get("/audio/task/mock_task_id")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id"
    assert data["status"] == "failed"
    assert "ValueError" in data["error"]
    assert data["filename"] == "bad.wav"

def test_get_task_status_other_state(mock_celery_tasks):
    """Test getting task status for an unknown/other state."""
    mock_celery_tasks["mock_async_result"].state = "REVOKED"
    mock_celery_tasks["mock_async_result"].info = {"reason": "cancelled"}

    response = client.get("/audio/task/mock_task_id")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "mock_task_id"
    assert data["status"] == "revoked"
    assert data["info"]["reason"] == "cancelled"

def test_get_task_status_exception_handling(mock_celery_tasks):
    """Test /audio/task/{task_id} when an unexpected exception occurs."""
    mock_celery_tasks["celery_app"].AsyncResult.side_effect = Exception("Celery lookup failed")

    response = client.get("/audio/task/mock_task_id")
    assert response.status_code == 500
    assert "Error retrieving task status" in response.json()["detail"]

# --- Tests for GET /audio/tasks/active ---
def test_get_active_tasks_success(mock_celery_tasks):
    """Test getting active tasks successfully."""
    mock_celery_tasks["celery_monitor"].get_active_tasks.return_value = {
        "active_tasks": [
            {"id": "task1", "name": "process_audio_task"},
            {"id": "task2", "name": "process_audio_quick_task"},
            {"id": "task3", "name": "other_task"}
        ]
    }
    mock_celery_tasks["redis_task_client"].hgetall.return_value = {
        b"redis_task_1": b"data1", b"redis_task_2": b"data2"
    }

    response = client.get("/audio/tasks/active")
    assert response.status_code == 200
    data = response.json()
    assert data["total_active"] == 2 # Only audio tasks
    assert len(data["active_tasks"]) == 2
    assert data["data_sources"]["celery_events"] == 3 # Total from celery_monitor
    assert data["data_sources"]["redis_backup"] == 2

def test_get_active_tasks_exception_handling(mock_celery_tasks):
    """Test /audio/tasks/active when an unexpected exception occurs."""
    mock_celery_tasks["celery_monitor"].get_active_tasks.side_effect = Exception("Monitor error")

    response = client.get("/audio/tasks/active")
    assert response.status_code == 200 # Endpoint returns 200 with error in body
    data = response.json()
    assert data["total_active"] == 0
    assert "Monitor error" in data["error"]

# --- Tests for DELETE /audio/task/{task_id} ---
def test_cancel_task_success(mock_celery_tasks):
    """Test successful task cancellation."""
    response = client.delete("/audio/task/task_to_cancel")
    assert response.status_code == 200
    assert response.json()["message"] == "Task task_to_cancel cancelled successfully"
    mock_celery_tasks["celery_app"].control.revoke.assert_called_once_with(
        "task_to_cancel", terminate=True
    )

def test_cancel_task_exception_handling(mock_celery_tasks):
    """Test /audio/task/{task_id} cancellation when an unexpected exception occurs."""
    mock_celery_tasks["celery_app"].control.revoke.side_effect = Exception("Revoke failed")

    response = client.delete("/audio/task/task_to_cancel")
    assert response.status_code == 500
    assert "Error cancelling task" in response.json()["detail"]

# --- Tests for GET /audio/queue/status ---
def test_get_queue_status_success(mock_celery_tasks):
    """Test getting queue status successfully."""
    mock_celery_tasks["mock_inspect"].stats.return_value = {
        "worker1@host": {"total": {"task_name": 5}},
        "worker2@host": {"total": {"task_name": 3}}
    }
    mock_celery_tasks["mock_inspect"].active.return_value = {
        "worker1@host": [{"id": "active_task_1"}],
        "worker2@host": [{"id": "active_task_2"}]
    }
    mock_celery_tasks["mock_inspect"].scheduled.return_value = {
        "worker1@host": [{"id": "scheduled_task_1"}]
    }
    mock_celery_tasks["mock_inspect"].reserved.return_value = {
        "worker2@host": [{"id": "reserved_task_1"}]
    }

    response = client.get("/audio/queue/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["workers"] == 2
    assert len(data["worker_info"]) == 2
    assert data["queue_stats"]["active_tasks"] == 2
    assert data["queue_stats"]["scheduled_tasks"] == 1
    assert data["queue_stats"]["reserved_tasks"] == 1
    assert data["queue_stats"]["total_pending"] == 4

def test_get_queue_status_no_workers(mock_celery_tasks):
    """Test getting queue status when no workers are running."""
    mock_celery_tasks["mock_inspect"].stats.return_value = None
    mock_celery_tasks["mock_inspect"].active.return_value = None
    mock_celery_tasks["mock_inspect"].scheduled.return_value = None
    mock_celery_tasks["mock_inspect"].reserved.return_value = None

    response = client.get("/audio/queue/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_workers"
    assert data["workers"] == 0

def test_get_queue_status_inspection_timeout(mock_celery_tasks):
    """Test getting queue status when inspection times out after retries."""
    mock_celery_tasks["mock_inspect"].stats.side_effect = [Exception("Timeout"), Exception("Timeout"), Exception("Timeout") ]
    
    response = client.get("/audio/queue/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "inspection_timeout"
    assert "Workers busy" in data["message"]

def test_get_queue_status_exception_handling(mock_celery_tasks):
    """Test /audio/queue/status when an unexpected exception occurs."""
    mock_celery_tasks["celery_app"].control.inspect.side_effect = Exception("Celery inspect failed")

    response = client.get("/audio/queue/status")
    assert response.status_code == 200 # Endpoint returns 200 with error in body
    data = response.json()
    assert data["status"] == "error"
    assert "Celery inspect failed" in data["message"]

# --- Tests for GET /audio/workers/status ---
def test_get_worker_status_success(mock_celery_tasks):
    """Test getting worker status successfully."""
    mock_celery_tasks["celery_monitor"].get_worker_stats.return_value = {
        "worker1@host": {"status": "online", "tasks_processed": 10}
    }
    mock_celery_tasks["mock_inspect"].stats.return_value = {
        "worker1@host": {"total": {"task_name": 5}}
    }
    mock_celery_tasks["mock_inspect"].active.return_value = {
        "worker1@host": [{"id": "active_task_1"}]
    }

    response = client.get("/audio/workers/status")
    assert response.status_code == 200
    data = response.json()
    assert "event_monitoring" in data
    assert "celery_inspection" in data
    assert data["celery_inspection"]["available"] is True
    assert data["celery_inspection"]["stats"]["worker1@host"]["total"]["task_name"] == 5
    assert data["celery_inspection"]["active"]["worker1@host"][0]["id"] == "active_task_1"

def test_get_worker_status_inspection_timeout(mock_celery_tasks):
    """Test getting worker status when inspection times out."""
    mock_celery_tasks["celery_monitor"].get_worker_stats.return_value = {
        "worker1@host": {"status": "online", "tasks_processed": 10}
    }
    # Mock the methods of the inspect object to raise exceptions
    mock_celery_tasks["mock_inspect"].stats.side_effect = Exception("Inspection timeout")
    mock_celery_tasks["mock_inspect"].active.side_effect = Exception("Inspection timeout")

    response = client.get("/audio/workers/status")
    assert response.status_code == 200
    data = response.json()
    assert data["celery_inspection"]["available"] is False
    assert data["celery_inspection"]["stats"] is None
    assert data["celery_inspection"]["active"] is None
    assert "explanation" in data

def test_get_worker_status_exception_handling(mock_celery_tasks):
    """Test /audio/workers/status when an unexpected exception occurs."""
    mock_celery_tasks["celery_monitor"].get_worker_stats.side_effect = Exception("Monitor error")

    response = client.get("/audio/workers/status")
    assert response.status_code == 200 # Endpoint returns 200 with error in body
    data = response.json()
    assert "error" in data
    assert "Monitor error" in data["error"]

# --- Tests for POST /audio/process-stream ---
def test_process_audio_stream_initiation_success(mock_celery_tasks):
    """Test successful initiation of audio streaming."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    response = client.post(
        "/audio/process-stream",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Use parse_sse_events to check initial message
    events = parse_sse_events(response.iter_bytes())
    assert events[0]["status"] == "submitted"
    assert events[0]["task_id"] == "mock_task_id_1"

def test_process_audio_stream_task_states(mock_celery_tasks):
    """Test streaming updates for various task states."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    # Configure mock_async_result to simulate state changes
    mock_async_result = mock_celery_tasks["mock_async_result"]
    mock_async_result.state = "PENDING"
    mock_async_result.info = {}

    # Simulate state transitions
    states = [
        ("PENDING", {}),
        ("PROCESSING", {"progress": 25, "step": "transcribing"}),
        ("PROCESSING", {"progress": 75, "step": "analyzing"}),
        ("SUCCESS", {"transcription": "final text", "processing_time": 10.0}),
    ]

    # Use a side_effect for AsyncResult to return different states over time
    # This requires a more complex mock setup or direct manipulation within the test
    # For simplicity, we'll mock AsyncResult.state and .info directly in a sequence
    
    # Let's create a sequence of mock AsyncResult objects
    mock_results_sequence = []
    for state, info in states:
        mock_res = MagicMock()
        mock_res.state = state
        mock_res.status = state  # Celery uses .status (alias of .state)
        mock_res.info = info
        mock_res.result = info if state == "SUCCESS" else None
        mock_results_sequence.append(mock_res)
    
    # The generator calls AsyncResult multiple times in a loop.
    # We use a side effect that returns the sequence elements and then stays on the last one.
    def async_result_side_effect(*args, **kwargs):
        if not hasattr(async_result_side_effect, 'counter'):
            async_result_side_effect.counter = 0
        idx = min(async_result_side_effect.counter, len(mock_results_sequence) - 1)
        async_result_side_effect.counter += 1
        return mock_results_sequence[idx]
        
    mock_celery_tasks["celery_app"].AsyncResult.side_effect = async_result_side_effect

    response = client.post(
        "/audio/process-stream",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    events = parse_sse_events(response.iter_bytes())
    
    # Assert initial submitted event
    assert events[0]["status"] == "submitted"
    assert events[0]["task_id"] == "mock_task_id_1"

    # Assert that we have at least some state transitions
    assert len(events) >= 2  # At least submitted + one state

    # Find the final completed event (could be at different positions)
    final_event = events[-1]
    # The last event should be "completed" or contain the final result
    assert final_event["status"] in ["completed", "SUCCESS"]

def test_process_audio_stream_timeout(mock_celery_tasks):
    """Test audio streaming timeout."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    # Mock AsyncResult to always be PENDING, simulating a task that never finishes
    mock_celery_tasks["mock_async_result"].state = "PENDING"
    mock_celery_tasks["mock_async_result"].info = {}

    # Mock datetime.now() to simulate time passing
    mock_now = datetime.now()
    with patch('app.api.audio_routes.datetime') as mock_dt:
        mock_dt.now.side_effect = [
            mock_now, # Initial call
            mock_now + timedelta(seconds=10), # First loop iteration
            mock_now + timedelta(seconds=301) # Timeout
        ]
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw) # Ensure datetime.now() works for other calls
        mock_dt.strptime = datetime.strptime # Ensure strptime works

        response = client.post(
            "/audio/process-stream",
            files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
            data={
                "language": "en",
                "include_translation": True,
                "include_insights": True
            }
        )
    
    assert response.status_code == 200
    events = parse_sse_events(response.iter_bytes())
    
    assert events[0]["status"] == "submitted"
    assert events[-1]["status"] == "timeout"
    assert "timeout" in events[-1]["error"]
def test_process_audio_stream_exception_in_generator(mock_celery_tasks):
    """Test audio streaming when an exception occurs within the event_stream generator."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    # Make AsyncResult lookup fail after the first call
    mock_res1 = MagicMock()
    mock_res1.state = "PENDING"
    mock_res1.info = {}
    mock_res1.status = "PENDING"
    mock_res1.result = None

    # Second result that will cause an error during JSON serialization
    def raise_error(*args, **kwargs):
        raise Exception("Generator error")

    mock_celery_tasks["celery_app"].AsyncResult.side_effect = [
        mock_res1,  # First call (initial loop state)
        raise_error  # Second call triggers exception
    ]

    response = client.post(
        "/audio/process-stream",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )

    assert response.status_code == 200
    events = parse_sse_events(response.iter_bytes())

    assert events[0]["status"] == "submitted"
    assert events[-1]["status"] == "stream_error"
    # Error message can vary, just check it's a stream error
    assert "error" in events[-1]

def test_process_audio_stream_no_file_provided(mock_celery_tasks):
    """Test /audio/process-stream with no audio file provided."""
    response = client.post(
        "/audio/process-stream",
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 422 # Expect 422 from FastAPI validation
    assert "Field required" in response.json()["detail"][0]["msg"]

def test_process_audio_stream_unsupported_format(mock_celery_tasks):
    """Test /audio/process-stream with an unsupported audio format."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.mp4", audio_content) # Unsupported format

    response = client.post(
        "/audio/process-stream",
        files={"audio": ("test.mp4", BytesIO(audio_content), "video/mp4")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]

def test_process_audio_stream_file_too_large(mock_celery_tasks):
    """Test /audio/process-stream with an audio file exceeding the max size."""
    large_audio_content = b"a" * (100 * 1024 * 1024 + 1) 
    mock_file = create_mock_upload_file("large.wav", large_audio_content)

    response = client.post(
        "/audio/process-stream",
        files={"audio": ("large.wav", BytesIO(large_audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]

def test_process_audio_stream_initial_exception(mock_celery_tasks):
    """Test /audio/process-stream when an exception occurs during initial task submission."""
    audio_content = b"mock_audio_data"
    mock_file = create_mock_upload_file("test.wav", audio_content)

    mock_celery_tasks["process_audio_task"].delay.side_effect = Exception("Initial submission failed")

    response = client.post(
        "/audio/process-stream",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 500
    assert "Failed to start audio processing" in response.json()["detail"]


# --- Tests for POST /audio/process-stream-realtime ---

def test_process_audio_realtime_streaming_success(mock_celery_tasks):
    """Test successful initiation of real-time Redis streaming."""
    audio_content = b"mock_audio_data"

    # Mock the subscribe_to_task to return a simple async generator
    async def mock_subscribe(*args, **kwargs):
        yield {"task_id": "mock_task_id_1", "step": "transcribing", "progress": 50}
        yield {"task_id": "mock_task_id_1", "step": "completed", "progress": 100}

    mock_celery_tasks["audio_streaming"].subscribe_to_task.return_value = mock_subscribe()

    response = client.post(
        "/audio/process-stream-realtime",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    events = parse_sse_events(response.iter_bytes())
    assert events[0]["status"] == "submitted"
    assert events[0]["streaming_type"] == "redis_pubsub"


def test_process_audio_realtime_streaming_no_file(mock_celery_tasks):
    """Test /audio/process-stream-realtime with no audio file provided."""
    response = client.post(
        "/audio/process-stream-realtime",
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]


def test_process_audio_realtime_streaming_unsupported_format(mock_celery_tasks):
    """Test /audio/process-stream-realtime with an unsupported audio format."""
    audio_content = b"mock_audio_data"

    response = client.post(
        "/audio/process-stream-realtime",
        files={"audio": ("test.mp4", BytesIO(audio_content), "video/mp4")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]


def test_process_audio_realtime_streaming_file_too_large(mock_celery_tasks):
    """Test /audio/process-stream-realtime with an audio file exceeding the max size."""
    large_audio_content = b"a" * (100 * 1024 * 1024 + 1)

    response = client.post(
        "/audio/process-stream-realtime",
        files={"audio": ("large.wav", BytesIO(large_audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]


def test_process_audio_realtime_streaming_initial_exception(mock_celery_tasks):
    """Test /audio/process-stream-realtime when an exception occurs during initial task submission."""
    audio_content = b"mock_audio_data"

    mock_celery_tasks["process_audio_task"].delay.side_effect = Exception("Initial submission failed")

    response = client.post(
        "/audio/process-stream-realtime",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )
    assert response.status_code == 500
    assert "Failed to start real-time audio processing" in response.json()["detail"]


def test_process_audio_realtime_streaming_redis_error(mock_celery_tasks):
    """Test /audio/process-stream-realtime when Redis streaming error occurs."""
    audio_content = b"mock_audio_data"

    # Mock the subscribe_to_task to raise an exception
    async def mock_subscribe_error(*args, **kwargs):
        yield {"task_id": "mock_task_id_1", "step": "starting"}
        raise Exception("Redis connection lost")

    mock_celery_tasks["audio_streaming"].subscribe_to_task.return_value = mock_subscribe_error()

    response = client.post(
        "/audio/process-stream-realtime",
        files={"audio": ("test.wav", BytesIO(audio_content), "audio/wav")},
        data={
            "language": "en",
            "include_translation": True,
            "include_insights": True
        }
    )

    assert response.status_code == 200
    events = parse_sse_events(response.iter_bytes())
    assert events[0]["status"] == "submitted"
    # Last event should be stream_error or stream_closed
    assert events[-1]["status"] in ["stream_error", "stream_closed"]
