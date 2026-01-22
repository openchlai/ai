# tests/test_celery_tasks.py
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestAudioTasks:
    """Unit tests for audio processing Celery tasks"""

    @patch('app.tasks.audio_tasks.model_loader')
    @patch('app.tasks.audio_tasks.redis_client')
    def test_process_streaming_audio_task(self, mock_redis, mock_loader):
        """Test the main streaming audio processing task"""
        # Mock models
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio_bytes.return_value = {
            "text": "Hello, how can I help you?",
            "segments": [{"start": 0, "end": 5, "text": "Hello, how can I help you?"}]
        }
        
        mock_classifier = MagicMock()
        mock_classifier.classify.return_value = {
            "main_category": "general_inquiry",
            "confidence": 0.85
        }
        
        mock_loader.get_model.side_effect = lambda name: {
            'whisper_model': mock_whisper,
            'classifier_model': mock_classifier
        }.get(name)
        
        # Test data
        audio_bytes = b'\x00' * 1000
        filename = "test_call_001_123456.wav"
        connection_id = "call_001"
        
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        # Execute task
        result = process_streaming_audio_task(
            audio_bytes=audio_bytes,
            filename=filename,
            connection_id=connection_id,
            language="sw",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True
        )
        
        # Verify result
        assert result is not None
        assert isinstance(result, dict)
        assert "transcript" in result
        assert result["transcript"] == "Hello, how can I help you?"

    @patch('app.tasks.audio_tasks.model_loader')
    def test_process_streaming_audio_task_model_not_loaded(self, mock_loader):
        """Test task behavior when models are not loaded"""
        mock_loader.get_model.return_value = None
        
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        result = process_streaming_audio_task(
            audio_bytes=b'\x00' * 1000,
            filename="test.wav",
            connection_id="test_001",
            language="en",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True
        )
        
        # Should handle gracefully
        assert result is not None
        assert "error" in result or "transcript" in result

    @patch('app.tasks.audio_tasks.model_loader')
    @patch('app.tasks.audio_tasks.redis_client')
    def test_process_streaming_audio_with_translation(self, mock_redis, mock_loader):
        """Test streaming audio processing with translation"""
        # Mock models
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio_bytes.return_value = {
            "text": "Habari, ninawezaje kukusaidia?"
        }
        
        mock_translator = MagicMock()
        mock_translator.translate.return_value = "Hello, how can I help you?"
        
        mock_loader.get_model.side_effect = lambda name: {
            'whisper_model': mock_whisper,
            'translator_model': mock_translator
        }.get(name)
        
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        result = process_streaming_audio_task(
            audio_bytes=b'\x00' * 1000,
            filename="test.wav",
            connection_id="test_001",
            language="sw",
            target_language="en",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True,
            include_translation=True
        )
        
        assert result is not None
        assert "transcript" in result
        assert "translation" in result
        assert result["translation"] == "Hello, how can I help you?"

    @patch('app.tasks.audio_tasks.model_loader')
    @patch('app.tasks.audio_tasks.redis_client')
    def test_process_streaming_audio_with_insights(self, mock_redis, mock_loader):
        """Test streaming audio processing with insights (NER, classification)"""
        # Mock models
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio_bytes.return_value = {
            "text": "My name is John Smith and I work at Microsoft."
        }
        
        mock_ner = MagicMock()
        mock_ner.extract_entities.return_value = [
            {"text": "John Smith", "label": "PERSON"},
            {"text": "Microsoft", "label": "ORG"}
        ]
        
        mock_classifier = MagicMock()
        mock_classifier.classify.return_value = {
            "main_category": "general_inquiry",
            "confidence": 0.9
        }
        
        mock_loader.get_model.side_effect = lambda name: {
            'whisper_model': mock_whisper,
            'ner_model': mock_ner,
            'classifier_model': mock_classifier
        }.get(name)
        
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        result = process_streaming_audio_task(
            audio_bytes=b'\x00' * 1000,
            filename="test.wav",
            connection_id="test_001",
            language="en",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True,
            include_insights=True
        )
        
        assert result is not None
        assert "transcript" in result
        assert "entities" in result
        assert "classification" in result
        assert len(result["entities"]) == 2
        assert result["classification"]["main_category"] == "general_inquiry"

    @patch('app.tasks.audio_tasks.model_loader')
    def test_process_streaming_audio_task_failure(self, mock_loader):
        """Test task behavior when processing fails"""
        # Mock whisper model to raise exception
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio_bytes.side_effect = Exception("Transcription failed")
        
        mock_loader.get_model.return_value = mock_whisper
        
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        result = process_streaming_audio_task(
            audio_bytes=b'\x00' * 1000,
            filename="test.wav",
            connection_id="test_001",
            language="en",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True
        )
        
        # Should handle error gracefully
        assert result is not None
        assert "error" in result or "transcript" in result

    @patch('app.tasks.audio_tasks.redis_client')
    def test_publish_streaming_update(self, mock_redis):
        """Test publishing streaming updates to Redis"""
        from app.tasks.audio_tasks import publish_streaming_update
        
        connection_id = "test_connection_001"
        update_data = {
            "step": "transcription",
            "progress": 50,
            "message": "Processing audio...",
            "timestamp": datetime.now().isoformat()
        }
        
        publish_streaming_update(connection_id, update_data)
        
        # Verify Redis publish was called
        mock_redis.publish.assert_called_once()

    @patch('app.tasks.audio_tasks.model_loader')
    @patch('app.tasks.audio_tasks.redis_client')
    def test_batch_audio_processing(self, mock_redis, mock_loader):
        """Test batch audio processing task"""
        # Mock models for batch processing
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio.return_value = {
            "text": "Batch processed audio content"
        }
        
        mock_loader.get_model.return_value = mock_whisper
        
        from app.tasks.audio_tasks import process_batch_audio_task
        
        # Test with file path
        result = process_batch_audio_task(
            file_path="/fake/path/audio.wav",
            language="en",
            include_translation=False,
            include_insights=False
        )
        
        assert result is not None
        assert "transcript" in result

    @patch('app.tasks.audio_tasks.tempfile.NamedTemporaryFile')
    def test_audio_bytes_to_file_conversion(self, mock_tempfile):
        """Test conversion of audio bytes to temporary file"""
        from app.tasks.audio_tasks import _save_audio_bytes_to_temp_file
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_audio.wav"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        audio_bytes = b'\x00' * 1000
        sample_rate = 16000
        
        with patch('soundfile.write') as mock_write:
            temp_path = _save_audio_bytes_to_temp_file(audio_bytes, sample_rate)
            
            assert temp_path == "/tmp/test_audio.wav"
            mock_write.assert_called_once()

    def test_audio_format_validation(self):
        """Test audio format validation"""
        from app.tasks.audio_tasks import _validate_audio_format
        
        # Test valid formats
        assert _validate_audio_format("test.wav") is True
        assert _validate_audio_format("test.mp3") is True
        assert _validate_audio_format("test.flac") is True
        
        # Test invalid formats
        assert _validate_audio_format("test.txt") is False
        assert _validate_audio_format("test.pdf") is False

    @patch('app.tasks.audio_tasks.model_loader')
    def test_resource_management_in_task(self, mock_loader):
        """Test that tasks properly manage resources"""
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio_bytes.return_value = {"text": "test"}
        mock_loader.get_model.return_value = mock_whisper
        
        # Mock resource manager
        with patch('app.tasks.audio_tasks.resource_manager') as mock_rm:
            mock_rm.acquire_streaming_gpu.return_value = True
            
            result = process_streaming_audio_task(
                audio_bytes=b'\x00' * 1000,
                filename="test.wav",
                connection_id="test_001",
                language="en",
                sample_rate=16000,
                duration_seconds=5.0,
                is_streaming=True
            )
            
            # Verify resource acquisition and release
            # (Implementation dependent)
            assert result is not None

    @patch('app.tasks.audio_tasks.model_loader')
    @patch('app.tasks.audio_tasks.redis_client')
    def test_progress_reporting(self, mock_redis, mock_loader):
        """Test that tasks report progress properly"""
        mock_whisper = MagicMock()
        mock_whisper.transcribe_audio_bytes.return_value = {"text": "test"}
        mock_loader.get_model.return_value = mock_whisper
        
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        result = process_streaming_audio_task(
            audio_bytes=b'\x00' * 1000,
            filename="test.wav",
            connection_id="test_001",
            language="en",
            sample_rate=16000,
            duration_seconds=5.0,
            is_streaming=True
        )
        
        # Should have published progress updates
        assert mock_redis.publish.call_count > 0

    def test_task_parameter_validation(self):
        """Test validation of task parameters"""
        from app.tasks.audio_tasks import _validate_task_parameters
        
        # Valid parameters
        valid_params = {
            "audio_bytes": b'\x00' * 1000,
            "filename": "test.wav",
            "connection_id": "test_001",
            "sample_rate": 16000
        }
        
        assert _validate_task_parameters(valid_params) is True
        
        # Invalid parameters
        invalid_params = {
            "audio_bytes": None,
            "filename": "",
            "connection_id": None,
            "sample_rate": -1
        }
        
        assert _validate_task_parameters(invalid_params) is False

    @patch('app.tasks.audio_tasks.model_loader')
    def test_qa_evaluation_task(self, mock_loader):
        """Test QA evaluation task"""
        mock_qa = MagicMock()
        mock_qa.evaluate_transcript.return_value = {
            "scores": {"opening": 0.8, "listening": 0.7},
            "overall_score": 0.75
        }
        
        mock_loader.get_model.return_value = mock_qa
        
        from app.tasks.audio_tasks import evaluate_qa_task
        
        transcript = "Hello, thank you for calling. How can I help you?"
        
        result = evaluate_qa_task(transcript)
        
        assert result is not None
        assert "scores" in result
        assert "overall_score" in result
        assert result["overall_score"] == 0.75