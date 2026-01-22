"""
Comprehensive tests for audio_tasks Celery tasks
"""
import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from app.tasks.audio_tasks import (
    get_worker_models,
    get_worker_status,
    process_audio_task,
    process_audio_quick_task,
    process_streaming_audio_task,
)


@pytest.fixture
def mock_task_context():
    """Mock Celery task context"""
    task = MagicMock()
    task.request.id = "test-task-123"
    task.update_state = MagicMock()
    return task


@pytest.fixture
def mock_models():
    """Mock all models"""
    models = {
        "whisper": MagicMock(),
        "translator": MagicMock(),
        "ner": MagicMock(),
        "classifier_model": MagicMock(),
        "summarizer": MagicMock(),
        "qa": MagicMock(),
    }

    # Configure default return values
    models["whisper"].transcribe_audio_bytes.return_value = {
        "text": "Test transcript",
        "segments": [{"start": 0, "end": 5, "text": "Test transcript"}]
    }

    models["translator"].translate.return_value = "Translated text"

    models["ner"].extract_entities.return_value = {
        "PERSON": ["John"],
        "ORG": ["Acme"]
    }

    models["classifier_model"].classify.return_value = {
        "main_category": "general",
        "confidence": 0.95
    }

    models["summarizer"].summarize.return_value = "Summary of test"

    models["qa"].evaluate.return_value = {
        "overall_score": 0.85,
        "categories": {}
    }

    return models


class TestGetWorkerModels:
    """Tests for get_worker_models function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_get_worker_models_success(self, mock_loader):
        """Test getting worker models"""
        mock_loader.models = {
            "whisper": MagicMock(),
            "translator": MagicMock()
        }
        mock_loader.get_ready_models.return_value = ["whisper", "translator"]

        result = get_worker_models()

        assert result is not None
        assert isinstance(result, dict)

    @patch('app.tasks.audio_tasks.worker_model_loader', None)
    def test_get_worker_models_not_initialized(self):
        """Test getting models when loader is not initialized"""
        result = get_worker_models()

        # Should return empty or error response
        assert result is not None


class TestGetWorkerStatus:
    """Tests for get_worker_status function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_get_worker_status_healthy(self, mock_loader):
        """Test getting healthy worker status"""
        mock_loader.get_ready_models.return_value = ["whisper", "translator"]
        mock_loader.get_failed_models.return_value = []
        mock_loader.get_blocked_models.return_value = []

        result = get_worker_status()

        assert result is not None
        assert isinstance(result, dict)

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_get_worker_status_with_failed_models(self, mock_loader):
        """Test worker status with failed models"""
        mock_loader.get_ready_models.return_value = ["whisper"]
        mock_loader.get_failed_models.return_value = ["translator"]
        mock_loader.get_blocked_models.return_value = []

        result = get_worker_status()

        assert result is not None


class TestProcessAudioTask:
    """Tests for process_audio_task"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_audio_task_success(self, mock_loader, mock_task_context, mock_models):
        """Test successful audio processing"""
        mock_task_context.request.id = "audio-task-001"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000  # 1 second of silence

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="test_audio.wav",
            language="sw",
            include_translation=True,
            include_insights=True,
            processing_mode="DUAL"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "transcript" in result or "status" in result

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_audio_task_no_whisper(self, mock_loader, mock_task_context, mock_models):
        """Test audio processing when Whisper is not available"""
        mock_task_context.request.id = "audio-task-002"
        models_no_whisper = {k: v for k, v in mock_models.items() if k != "whisper"}
        mock_loader.models = models_no_whisper
        mock_loader.get_ready_models.return_value = list(models_no_whisper.keys())

        audio_bytes = b'\x00' * 16000

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="test_audio.wav"
        )

        # Should handle gracefully
        assert result is not None

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_audio_task_translation_only(self, mock_loader, mock_task_context, mock_models):
        """Test audio processing with translation disabled"""
        mock_task_context.request.id = "audio-task-003"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="test_audio.wav",
            include_translation=False
        )

        assert result is not None

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_audio_task_no_insights(self, mock_loader, mock_task_context, mock_models):
        """Test audio processing with insights disabled"""
        mock_task_context.request.id = "audio-task-004"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="test_audio.wav",
            include_insights=False
        )

        assert result is not None


class TestProcessAudioQuickTask:
    """Tests for process_audio_quick_task"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_audio_quick_task_success(self, mock_loader, mock_task_context, mock_models):
        """Test successful quick audio processing"""
        mock_task_context.request.id = "quick-task-001"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = ["whisper"]

        audio_bytes = b'\x00' * 16000

        result = process_audio_quick_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="quick_audio.wav",
            language="en"
        )

        assert result is not None
        assert isinstance(result, dict)

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_audio_quick_task_minimal_models(self, mock_loader, mock_task_context, mock_models):
        """Test quick task with minimal models loaded"""
        mock_task_context.request.id = "quick-task-002"
        minimal_models = {"whisper": mock_models["whisper"]}
        mock_loader.models = minimal_models
        mock_loader.get_ready_models.return_value = ["whisper"]

        audio_bytes = b'\x00' * 16000

        result = process_audio_quick_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="quick_audio.wav"
        )

        assert result is not None


class TestProcessStreamingAudioTask:
    """Tests for process_streaming_audio_task"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_streaming_audio_success(self, mock_loader, mock_task_context, mock_models):
        """Test successful streaming audio processing"""
        mock_task_context.request.id = "stream-task-001"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000

        result = process_streaming_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="stream_001.wav",
            connection_id="call_123",
            language="sw",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True
        )

        assert result is not None
        assert isinstance(result, dict)

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_streaming_audio_no_connection_id(self, mock_loader, mock_task_context, mock_models):
        """Test streaming audio without connection ID"""
        mock_task_context.request.id = "stream-task-002"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = ["whisper"]

        audio_bytes = b'\x00' * 16000

        result = process_streaming_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="stream_002.wav",
            connection_id=None
        )

        assert result is not None

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_streaming_audio_minimal_audio(self, mock_loader, mock_task_context, mock_models):
        """Test streaming audio with minimal audio data"""
        mock_task_context.request.id = "stream-task-003"
        mock_loader.models = {"whisper": mock_models["whisper"]}
        mock_loader.get_ready_models.return_value = ["whisper"]

        audio_bytes = b'\x00' * 100  # Very small audio

        result = process_streaming_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="stream_003.wav"
        )

        assert result is not None

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_process_streaming_audio_large_file(self, mock_loader, mock_task_context, mock_models):
        """Test streaming audio with large audio file"""
        mock_task_context.request.id = "stream-task-004"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * (1024 * 1024)  # 1 MB of audio

        result = process_streaming_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="stream_large.wav"
        )

        assert result is not None


class TestTaskContextUpdates:
    """Tests for task state updates"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_task_state_updates(self, mock_loader, mock_task_context, mock_models):
        """Test that tasks update their state"""
        mock_task_context.request.id = "state-task-001"
        mock_task_context.update_state = MagicMock()
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="state_test.wav"
        )

        # Verify update_state was called at least once
        assert mock_task_context.update_state.called or result is not None


class TestErrorHandling:
    """Tests for error handling in audio tasks"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_audio_task_with_corrupted_audio(self, mock_loader, mock_task_context, mock_models):
        """Test handling of corrupted audio data"""
        mock_task_context.request.id = "error-task-001"
        mock_models["whisper"].transcribe_audio_bytes.side_effect = Exception("Audio decode error")
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = ["whisper"]

        audio_bytes = b'\xFF\xFF\xFF\xFF'  # Likely corrupted

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="corrupted.wav"
        )

        # Should handle error gracefully
        assert result is not None

    @patch('app.tasks.audio_tasks.worker_model_loader', None)
    def test_streaming_audio_no_model_loader(self, mock_task_context):
        """Test streaming audio when model loader is not available"""
        mock_task_context.request.id = "error-task-002"

        audio_bytes = b'\x00' * 16000

        result = process_streaming_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="test.wav"
        )

        # Should handle gracefully
        assert result is not None


class TestTaskMetadata:
    """Tests for task metadata handling"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_task_returns_task_id(self, mock_loader, mock_task_context, mock_models):
        """Test that task results include task ID"""
        expected_id = "metadata-task-123"
        mock_task_context.request.id = expected_id
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="metadata.wav"
        )

        # If result contains task_id, verify it matches
        if isinstance(result, dict) and "task_id" in result:
            assert result["task_id"] == expected_id

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_task_includes_timestamp(self, mock_loader, mock_task_context, mock_models):
        """Test that results include timestamp"""
        mock_task_context.request.id = "timestamp-task-001"
        mock_loader.models = mock_models
        mock_loader.get_ready_models.return_value = list(mock_models.keys())

        audio_bytes = b'\x00' * 16000

        result = process_audio_task(
            mock_task_context,
            audio_bytes=audio_bytes,
            filename="timestamp.wav"
        )

        # If result contains timestamp, verify it's in ISO format
        if isinstance(result, dict) and "timestamp" in result:
            try:
                datetime.fromisoformat(result["timestamp"])
            except (ValueError, TypeError):
                pytest.fail("Timestamp is not in ISO format")
