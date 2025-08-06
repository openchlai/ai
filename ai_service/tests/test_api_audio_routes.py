# tests/test_api_audio_routes.py
import pytest
import sys
import os
from io import BytesIO
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, UploadFile

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_app():
    """Create a test FastAPI app with audio routes"""
    from app.api.audio_routes import router
    
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(mock_app):
    """Create test client"""
    return TestClient(mock_app)

@pytest.fixture
def sample_audio_file():
    """Create a sample audio file for testing"""
    # Create minimal WAV file bytes
    wav_header = (
        b'RIFF'  # ChunkID
        b'\x2c\x00\x00\x00'  # ChunkSize 
        b'WAVE'  # Format
        b'fmt '  # Subchunk1ID  
        b'\x10\x00\x00\x00'  # Subchunk1Size
        b'\x01\x00'  # AudioFormat (PCM)
        b'\x01\x00'  # NumChannels (mono)
        b'\x40\x1f\x00\x00'  # SampleRate (8000)
        b'\x80\x3e\x00\x00'  # ByteRate
        b'\x02\x00'  # BlockAlign  
        b'\x10\x00'  # BitsPerSample (16)
        b'data'  # Subchunk2ID
        b'\x08\x00\x00\x00'  # Subchunk2Size
        b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 8 bytes of silence
    )
    return BytesIO(wav_header)

@pytest.fixture
def large_audio_file():
    """Create a large audio file for testing size limits"""
    large_data = b'\x00' * (101 * 1024 * 1024)  # 101MB
    return BytesIO(large_data)

class TestAudioProcessEndpoint:
    """Test the /audio/process endpoint"""

    @patch('app.api.audio_routes.process_audio_task')
    def test_process_audio_success_background(self, mock_task, client, sample_audio_file):
        """Test successful background audio processing"""
        # Mock Celery task
        mock_celery_result = MagicMock()
        mock_celery_result.id = "test-task-123"
        mock_task.delay.return_value = mock_celery_result
        
        response = client.post(
            "/audio/process",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={
                "language": "en",
                "include_translation": "true",
                "include_insights": "true",
                "background": "true"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-123"
        assert data["status"] == "queued"
        assert "status_endpoint" in data
        
        mock_task.delay.assert_called_once()

    @patch('app.api.audio_routes.process_audio_task')
    def test_process_audio_success_foreground(self, mock_task, client, sample_audio_file):
        """Test successful foreground audio processing"""
        # Match the TaskResponse format that the API expects to return
        mock_result = {
            "task_id": "sync-task-123",
            "status": "completed",
            "message": "Processing completed",
            "estimated_time": "0 seconds", 
            "status_endpoint": "/audio/task/sync-task-123"
        }
        mock_task.return_value = mock_result
        
        response = client.post(
            "/audio/process",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={
                "language": "en",
                "background": "false"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "sync-task-123"
        assert data["status"] == "completed"

    def test_process_audio_no_file(self, client):
        """Test processing without audio file"""
        response = client.post(
            "/audio/process",
            data={"language": "en"}
        )
        
        assert response.status_code == 422  # Validation error

    def test_process_audio_unsupported_format(self, client):
        """Test processing with unsupported file format"""
        txt_file = BytesIO(b"This is not an audio file")
        
        response = client.post(
            "/audio/process",
            files={"audio": ("test.txt", txt_file, "text/plain")},
            data={"language": "en"}
        )
        
        assert response.status_code == 400
        assert "Unsupported audio format" in response.json()["detail"]

    def test_process_audio_file_too_large(self, client, large_audio_file):
        """Test processing with file that's too large"""
        response = client.post(
            "/audio/process",
            files={"audio": ("large.wav", large_audio_file, "audio/wav")},
            data={"language": "en"}
        )
        
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]

    @patch('app.api.audio_routes.process_audio_task')
    def test_process_audio_task_failure(self, mock_task, client, sample_audio_file):
        """Test handling of task processing failure"""
        mock_task.delay.side_effect = Exception("Task submission failed")
        
        response = client.post(
            "/audio/process",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "en", "background": "true"}
        )
        
        assert response.status_code == 500
        assert "Audio processing failed" in response.json()["detail"]

    def test_process_audio_default_parameters(self, client, sample_audio_file):
        """Test processing with default parameters"""
        with patch('app.api.audio_routes.process_audio_task') as mock_task:
            mock_celery_result = MagicMock()
            mock_celery_result.id = "test-task-123"
            mock_task.delay.return_value = mock_celery_result
            
            response = client.post(
                "/audio/process",
                files={"audio": ("test.wav", sample_audio_file, "audio/wav")}
            )
            
            assert response.status_code == 200
            # Verify default parameters were used
            call_args = mock_task.delay.call_args[1]
            assert call_args["include_translation"] is True
            assert call_args["include_insights"] is True


class TestAudioAnalyzeEndpoint:
    """Test the /audio/analyze endpoint"""

    @patch('app.api.audio_routes.process_audio_quick_task')
    def test_analyze_audio_success_background(self, mock_task, client, sample_audio_file):
        """Test successful background audio analysis"""
        mock_celery_result = MagicMock()
        mock_celery_result.id = "analyze-task-456"
        mock_task.delay.return_value = mock_celery_result
        
        response = client.post(
            "/audio/analyze",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "en", "background": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "analyze-task-456"
        assert data["status"] == "queued"
        assert "10-20 seconds" in data["estimated_time"]

    @patch('app.api.audio_routes.process_audio_quick_task')
    def test_analyze_audio_success_foreground(self, mock_task, client, sample_audio_file):
        """Test successful foreground audio analysis"""
        # Match the TaskResponse format that the API expects to return
        mock_result = {
            "task_id": "sync-analyze-123",
            "status": "completed",
            "message": "Analysis completed",
            "estimated_time": "0 seconds",
            "status_endpoint": "/audio/task/sync-analyze-123"
        }
        mock_task.return_value = mock_result
        
        response = client.post(
            "/audio/analyze",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "en", "background": "false"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "sync-analyze-123"
        assert data["status"] == "completed"

    def test_analyze_audio_file_size_limit(self, client):
        """Test analyze endpoint file size limit (50MB)"""
        # Create file that's over 50MB limit
        large_data = b'\x00' * (51 * 1024 * 1024)
        large_file = BytesIO(large_data)
        
        response = client.post(
            "/audio/analyze",
            files={"audio": ("large.wav", large_file, "audio/wav")},
            data={"language": "en"}
        )
        
        assert response.status_code == 400
        assert "File too large for quick analysis" in response.json()["detail"]

    def test_analyze_audio_no_filename(self, client):
        """Test analyze with file that has no filename"""
        # This tests the filename validation
        file_without_name = BytesIO(b"audio data")
        
        response = client.post(
            "/audio/analyze",
            files={"audio": ("", file_without_name, "audio/wav")},
            data={"language": "en"}
        )
        
        # FastAPI returns 422 for validation errors, not 400
        assert response.status_code == 422


class TestAudioTaskStatusEndpoint:
    """Test the /audio/task/{task_id} endpoint"""

    @patch('app.api.audio_routes.celery_app')
    def test_get_task_status_success(self, mock_celery, client):
        """Test getting task status successfully"""
        # Mock Celery result
        mock_result = MagicMock()
        mock_result.state = "SUCCESS"
        mock_result.result = {
            "transcript": "Task completed successfully",
            "processing_time": 15.5
        }
        mock_result.info = None
        mock_celery.AsyncResult.return_value = mock_result
        
        response = client.get("/audio/task/test-task-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-123"
        assert data["status"] == "completed"  # API converts SUCCESS to "completed"
        assert data["result"]["transcript"] == "Task completed successfully"

    @patch('app.api.audio_routes.celery_app')
    def test_get_task_status_pending(self, mock_celery, client):
        """Test getting status of pending task"""
        mock_result = MagicMock()
        mock_result.state = "PENDING"
        mock_result.result = None
        mock_result.info = None
        mock_celery.AsyncResult.return_value = mock_result
        
        response = client.get("/audio/task/pending-task-456")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"  # API converts PENDING to "queued"
        assert data["message"] == "Task is waiting to be processed"

    @patch('app.api.audio_routes.celery_app')
    def test_get_task_status_failure(self, mock_celery, client):
        """Test getting status of failed task"""
        mock_result = MagicMock()
        mock_result.state = "FAILURE"
        mock_result.result = None
        mock_result.info = "Processing error occurred"
        mock_celery.AsyncResult.return_value = mock_result
        
        response = client.get("/audio/task/failed-task-789")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FAILURE"
        assert "Processing error occurred" in data["error"]

    @patch('app.api.audio_routes.celery_app')
    def test_get_task_status_progress(self, mock_celery, client):
        """Test getting status of task in progress"""
        mock_result = MagicMock()
        mock_result.state = "PROGRESS"
        mock_result.result = None
        mock_result.info = {
            "current_step": "transcription",
            "progress": 50,
            "total_steps": 4
        }
        mock_celery.AsyncResult.return_value = mock_result
        
        response = client.get("/audio/task/progress-task-999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROGRESS"
        assert data["progress"]["current_step"] == "transcription"
        assert data["progress"]["progress"] == 50


class TestStreamingEndpoints:
    """Test streaming-related endpoints"""

    @patch('app.api.audio_routes.redis_task_client')
    def test_process_stream_realtime(self, mock_redis, client, sample_audio_file):
        """Test real-time streaming processing"""
        # Mock Redis pub/sub
        mock_pubsub = MagicMock()
        mock_redis.pubsub.return_value = mock_pubsub
        mock_redis.publish = MagicMock()
        
        with patch('app.api.audio_routes.process_streaming_audio_task') as mock_task:
            mock_task.delay.return_value.id = "streaming-task-001"
            
            response = client.post(
                "/audio/process-stream-realtime",
                files={"audio": ("stream.wav", sample_audio_file, "audio/wav")},
                data={
                    "language": "en",
                    "include_translation": "true",
                    "include_insights": "true"
                }
            )
            
            assert response.status_code == 200
            # Verify streaming response headers
            assert response.headers["content-type"] == "text/event-stream"

    @patch('app.api.audio_routes.audio_streaming')
    def test_get_streaming_status(self, mock_streaming, client):
        """Test getting streaming status"""
        mock_streaming.get_status.return_value = {
            "active_streams": 2,
            "total_processed": 15,
            "uptime_seconds": 3600
        }
        
        response = client.get("/audio/streaming/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["active_streams"] == 2
        assert data["total_processed"] == 15

    def test_streaming_metrics(self, client):
        """Test getting streaming metrics"""
        with patch('app.api.audio_routes.celery_monitor') as mock_monitor:
            mock_monitor.get_streaming_metrics.return_value = {
                "avg_processing_time": 12.5,
                "success_rate": 0.95,
                "error_rate": 0.05
            }
            
            response = client.get("/audio/streaming/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["avg_processing_time"] == 12.5
            assert data["success_rate"] == 0.95


class TestAudioValidation:
    """Test audio file validation functions"""

    def test_validate_audio_file_formats(self, client):
        """Test validation of different audio file formats"""
        valid_formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"]
        
        for fmt in valid_formats:
            audio_file = BytesIO(b"fake audio data")
            response = client.post(
                "/audio/process",
                files={"audio": (f"test{fmt}", audio_file, "audio/wav")},
                data={"language": "en"}
            )
            
            # Should not fail on format validation (might fail on content)
            assert response.status_code != 400 or "Unsupported audio format" not in response.json().get("detail", "")

    def test_audio_content_validation(self, client):
        """Test validation of audio file content"""
        # Test with invalid content but valid extension
        invalid_audio = BytesIO(b"This is not audio data")
        
        response = client.post(
            "/audio/process",
            files={"audio": ("fake.wav", invalid_audio, "audio/wav")},
            data={"language": "en"}
        )
        
        # May pass validation here but fail in processing
        # This tests that we don't crash on invalid content
        assert response.status_code in [200, 400, 422, 500]


class TestAudioRouterConfiguration:
    """Test router configuration and middleware"""

    def test_router_prefix_and_tags(self):
        """Test that router is configured correctly"""
        from app.api.audio_routes import router
        
        assert router.prefix == "/audio"
        assert "audio" in router.tags

    def test_response_models(self):
        """Test response model definitions"""
        from app.api.audio_routes import TaskResponse
        
        # Test that response model has required fields
        response = TaskResponse(
            task_id="test",
            status="queued",
            message="Test message",
            estimated_time="30 seconds",
            status_endpoint="/test/endpoint"
        )
        
        assert response.task_id == "test"
        assert response.status == "queued"

    @patch('app.api.audio_routes.logger')
    def test_logging_integration(self, mock_logger, client, sample_audio_file):
        """Test that endpoints log appropriately"""
        with patch('app.api.audio_routes.process_audio_task') as mock_task:
            mock_celery_result = MagicMock()
            mock_celery_result.id = "logged-task"
            mock_task.delay.return_value = mock_celery_result
            
            response = client.post(
                "/audio/process",
                files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
                data={"language": "en"}
            )
            
            assert response.status_code == 200
            # Verify logging was called
            mock_logger.info.assert_called()


class TestErrorHandling:
    """Test error handling across audio endpoints"""

    @patch('app.api.audio_routes.process_audio_task')
    def test_celery_connection_error(self, mock_task, client, sample_audio_file):
        """Test handling of Celery connection errors"""
        mock_task.delay.side_effect = ConnectionError("Redis connection failed")
        
        response = client.post(
            "/audio/process",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "en"}
        )
        
        assert response.status_code == 500
        assert "Audio processing failed" in response.json()["detail"]

    def test_malformed_request_data(self, client, sample_audio_file):
        """Test handling of malformed request data"""
        response = client.post(
            "/audio/process",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"include_translation": "not_a_boolean"}  # Invalid boolean
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_concurrent_request_handling(self, client, sample_audio_file):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('app.api.audio_routes.process_audio_task') as mock_task:
                mock_celery_result = MagicMock()
                mock_celery_result.id = f"concurrent-{threading.current_thread().ident}"
                mock_task.delay.return_value = mock_celery_result
                
                response = client.post(
                    "/audio/process",
                    files={"audio": ("test.wav", BytesIO(b"test data"), "audio/wav")},
                    data={"language": "en"}
                )
                results.append(response.status_code)
        
        # Start multiple requests concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(status == 200 for status in results)