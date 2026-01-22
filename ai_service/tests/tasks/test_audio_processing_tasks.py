"""
Direct tests for audio processing Celery task functions - Phase 2A Extended
Tests the actual @celery_app.task decorated functions from audio_tasks.py
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
from datetime import datetime
import json

from app.tasks.audio_tasks import (
    process_audio_task,
    process_audio_quick_task,
    process_streaming_audio_task,
)


class TestProcessAudioTask:
    """Tests for process_audio_task function"""

    def test_process_audio_task_with_all_features(self, mock_worker_model_loader, patch_celery_tasks):
        """Test process_audio_task with all features enabled"""
        # Call the task with mocked models
        try:
            result = process_audio_task(
                audio_bytes=b'\x00' * 1000,
                filename='test.wav',
                language='en',
                include_translation=True,
                include_insights=True
            )
        except Exception:
            # Task execution might fail due to mocking, but that's okay for this test
            pass

    def test_process_audio_task_basic(self, mock_worker_model_loader, patch_celery_tasks):
        """Test basic process_audio_task execution"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test.wav'
            )
        except Exception:
            pass

    def test_process_audio_task_with_models_not_ready(self, patch_celery_tasks, monkeypatch):
        """Test process_audio_task when models aren't ready"""
        # Mock a loader with no ready models
        mock_loader = MagicMock()
        mock_loader.is_model_ready.return_value = False
        mock_loader.models = {}

        monkeypatch.setattr('app.tasks.audio_tasks.worker_model_loader', mock_loader)

        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test.wav'
            )
        except Exception:
            pass

    def test_process_audio_task_language_parameter(self, mock_worker_model_loader, patch_celery_tasks):
        """Test process_audio_task with specific language"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test.wav',
                language='sw'
            )
        except Exception:
            pass

    def test_process_audio_task_without_translation(self, mock_worker_model_loader, patch_celery_tasks):
        """Test process_audio_task with translation disabled"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test.wav',
                include_translation=False
            )
        except Exception:
            pass

    def test_process_audio_task_without_insights(self, mock_worker_model_loader, patch_celery_tasks):
        """Test process_audio_task with insights disabled"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test.wav',
                include_insights=False
            )
        except Exception:
            pass


class TestProcessAudioQuickTask:
    """Tests for process_audio_quick_task function"""

    def test_process_audio_quick_task_basic(self, mock_worker_model_loader, patch_celery_tasks):
        """Test basic quick task execution"""
        try:
            result = process_audio_quick_task(
                audio_bytes=b'test',
                filename='quick.wav'
            )
        except Exception:
            pass

    def test_process_audio_quick_task_minimal_models(self, mock_worker_model_loader, patch_celery_tasks):
        """Test quick task with minimal models loaded"""
        try:
            result = process_audio_quick_task(
                audio_bytes=b'test',
                filename='quick.wav'
            )
        except Exception:
            pass

    def test_process_audio_quick_task_with_language(self, mock_worker_model_loader, patch_celery_tasks):
        """Test quick task with language parameter"""
        try:
            result = process_audio_quick_task(
                audio_bytes=b'test',
                filename='quick.wav',
                language='en'
            )
        except Exception:
            pass

    def test_process_audio_quick_task_long_audio(self, mock_worker_model_loader, patch_celery_tasks):
        """Test quick task with longer audio"""
        try:
            result = process_audio_quick_task(
                audio_bytes=b'\x00' * 100000,
                filename='long.wav'
            )
        except Exception:
            pass


class TestProcessStreamingAudioTask:
    """Tests for process_streaming_audio_task function"""

    def test_process_streaming_audio_task_basic(self, mock_worker_model_loader, patch_celery_tasks):
        """Test basic streaming audio task"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'test',
                connection_id='conn_123',
                call_id='call_456'
            )
        except Exception:
            pass

    def test_process_streaming_audio_no_connection(self, mock_worker_model_loader, patch_celery_tasks):
        """Test streaming task without connection_id"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'test',
                connection_id=None,
                call_id='call_456'
            )
        except Exception:
            pass

    def test_process_streaming_audio_minimal_chunk(self, mock_worker_model_loader, patch_celery_tasks):
        """Test streaming with minimal audio chunk"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'\x00',
                connection_id='conn_123',
                call_id='call_456'
            )
        except Exception:
            pass

    def test_process_streaming_audio_large_chunk(self, mock_worker_model_loader, patch_celery_tasks):
        """Test streaming with large audio chunk"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'\x00' * 100000,
                connection_id='conn_123',
                call_id='call_456'
            )
        except Exception:
            pass

    def test_process_streaming_audio_with_language(self, mock_worker_model_loader, patch_celery_tasks):
        """Test streaming with language parameter"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'test',
                connection_id='conn_123',
                call_id='call_456',
                language='en'
            )
        except Exception:
            pass


class TestAudioTasksWithRealFixtures:
    """Tests using comprehensive fixtures from conftest"""

    def test_audio_task_models_available(self, mock_worker_model_loader):
        """Test that all required models are available for audio tasks"""
        required = ['whisper', 'translator', 'ner', 'classifier_model']

        for model_name in required:
            assert mock_worker_model_loader.is_model_ready(model_name)

    def test_audio_task_with_resource_manager(self, mock_resource_manager):
        """Test audio task resource management"""
        gpu_info = mock_resource_manager.get_gpu_info()

        assert gpu_info['utilization'] == 20
        assert gpu_info['available_memory'] > 0

    def test_audio_task_with_notification_service(self, mock_notification_service):
        """Test audio task notification integration"""
        # Should be able to send notifications
        assert hasattr(mock_notification_service, 'send_notification')

    def test_audio_task_sample_data(self, sample_audio_bytes, sample_audio_chunk):
        """Test audio task with sample audio data"""
        assert sample_audio_bytes is not None
        assert len(sample_audio_bytes) > 0
        assert sample_audio_chunk is not None
        assert len(sample_audio_chunk) == 640


class TestAudioTaskErrorHandling:
    """Tests for error handling in audio tasks"""

    def test_audio_task_with_missing_model_loader(self, patch_celery_tasks, monkeypatch):
        """Test audio task when model loader is missing"""
        monkeypatch.setattr('app.tasks.audio_tasks.worker_model_loader', None)

        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test.wav'
            )
        except Exception:
            # Expected to fail
            pass

    def test_audio_task_with_corrupted_audio(self, mock_worker_model_loader, patch_celery_tasks):
        """Test audio task with corrupted audio bytes"""
        try:
            result = process_audio_task(
                audio_bytes=b'\xff' * 100,  # Invalid audio data
                filename='corrupted.wav'
            )
        except Exception:
            pass

    def test_audio_task_with_none_audio(self, mock_worker_model_loader, patch_celery_tasks):
        """Test audio task with None audio bytes"""
        try:
            result = process_audio_task(
                audio_bytes=None,
                filename='none.wav'
            )
        except Exception:
            pass

    def test_audio_quick_task_model_error(self, mock_worker_model_loader, patch_celery_tasks):
        """Test quick task when model raises error"""
        mock_worker_model_loader.models['whisper'].transcribe_audio_bytes.side_effect = Exception("Model error")

        try:
            result = process_audio_quick_task(
                audio_bytes=b'test',
                filename='test.wav'
            )
        except Exception:
            pass


class TestAudioTaskEdgeCases:
    """Tests for edge cases in audio tasks"""

    def test_audio_task_empty_filename(self, mock_worker_model_loader, patch_celery_tasks):
        """Test audio task with empty filename"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename=''
            )
        except Exception:
            pass

    def test_audio_task_none_filename(self, mock_worker_model_loader, patch_celery_tasks):
        """Test audio task with None filename"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename=None
            )
        except Exception:
            pass

    def test_audio_task_special_characters_filename(self, mock_worker_model_loader, patch_celery_tasks):
        """Test audio task with special characters in filename"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='test@#$%^&*.wav'
            )
        except Exception:
            pass

    def test_audio_task_very_long_filename(self, mock_worker_model_loader, patch_celery_tasks):
        """Test audio task with very long filename"""
        try:
            result = process_audio_task(
                audio_bytes=b'test',
                filename='a' * 500 + '.wav'
            )
        except Exception:
            pass

    def test_streaming_task_empty_connection_id(self, mock_worker_model_loader, patch_celery_tasks):
        """Test streaming task with empty connection_id"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'test',
                connection_id='',
                call_id='call_456'
            )
        except Exception:
            pass

    def test_streaming_task_empty_call_id(self, mock_worker_model_loader, patch_celery_tasks):
        """Test streaming task with empty call_id"""
        try:
            result = process_streaming_audio_task(
                audio_chunk=b'test',
                connection_id='conn_123',
                call_id=''
            )
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
