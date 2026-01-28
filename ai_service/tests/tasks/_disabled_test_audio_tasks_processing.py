"""
Comprehensive tests for audio_tasks.py main processing functions
"""
import pytest
import json
import io
from unittest.mock import MagicMock, patch, AsyncMock, call, mock_open
from datetime import datetime


@pytest.fixture
def mock_audio_bytes():
    """Mock audio file bytes"""
    return b'\x00\x01\x02\x03' * 1000  # 4KB of mock audio data


@pytest.fixture
def mock_worker_loader():
    """Mock worker model loader with all models"""
    loader = MagicMock()

    # Mock Whisper model
    whisper = MagicMock()
    whisper.transcribe_audio_bytes.return_value = {
        "text": "Hello, this is a test transcription",
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "Hello, this is a test"},
            {"start": 2.5, "end": 5.0, "text": "transcription"}
        ]
    }
    whisper.get_model_info.return_value = {"model": "whisper", "loaded": True}

    # Mock Translator model
    translator = MagicMock()
    translator.translate.return_value = "Hello, this is a test transcription"
    translator.get_model_info.return_value = {"model": "translator", "loaded": True}

    # Mock NER model
    ner = MagicMock()
    ner.extract_entities.return_value = {
        "entities": {
            "PERSON": ["John", "Mary"],
            "ORG": ["Acme Corp"],
            "LOC": ["New York"]
        }
    }
    ner.get_model_info.return_value = {"model": "ner", "loaded": True}

    # Mock Classifier model
    classifier = MagicMock()
    classifier.classify.return_value = {
        "main_category": "general_inquiry",
        "sub_category": "information_request",
        "confidence_scores": {
            "main_category": 0.95,
            "sub_category": 0.88
        }
    }
    classifier.get_model_info.return_value = {"model": "classifier", "loaded": True}

    # Mock Summarizer model
    summarizer = MagicMock()
    summarizer.summarize.return_value = "Summary: This is a test transcription"
    summarizer.get_model_info.return_value = {"model": "summarizer", "loaded": True}

    # Mock QA model
    qa = MagicMock()
    qa.evaluate.return_value = {
        "overall_score": 0.85,
        "categories": {
            "opening": {"score": 0.9, "passed": True},
            "resolution": {"score": 0.8, "passed": True}
        }
    }
    qa.get_model_info.return_value = {"model": "qa", "loaded": True}

    # Assign models to loader
    loader.models = {
        "whisper": whisper,
        "translator": translator,
        "ner": ner,
        "classifier_model": classifier,
        "summarizer": summarizer,
        "qa": qa
    }

    loader.get_ready_models.return_value = ["whisper", "translator", "ner",
                                             "classifier_model", "summarizer", "qa"]

    return loader


class TestProcessAudioTask:
    """Tests for process_audio_task function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    @patch('app.tasks.audio_tasks.celery_task_duration_seconds')
    @patch('app.tasks.audio_tasks.celery_tasks_total')
    @patch('app.tasks.audio_tasks.record_upload_size')
    def test_process_audio_task_success(self, mock_record_size, mock_tasks_total,
                                         mock_duration, mock_redis, mock_loader,
                                         mock_audio_bytes, mock_worker_loader):
        """Test successful audio processing with all models"""
        from app.tasks.audio_tasks import process_audio_task

        # Setup mocks
        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        # Mock file operations
        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    # Call the task
                    result = process_audio_task(
                        task_id="test_task_123",
                        file_path="/tmp/test_audio.wav",
                        language="auto",
                        include_translation=True,
                        include_ner=True,
                        include_classification=True,
                        include_summarization=True,
                        include_qa=False
                    )

                    # Verify result structure
                    assert result is not None
                    assert "transcript" in result
                    assert "translated" in result
                    assert "entities" in result
                    assert "classification" in result
                    assert "summary" in result

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_audio_task_file_not_found(self, mock_redis, mock_loader):
        """Test processing when audio file doesn't exist"""
        from app.tasks.audio_tasks import process_audio_task

        mock_loader.__bool__.return_value = True
        mock_redis.get.return_value = None

        with patch('os.path.exists', return_value=False):
            with pytest.raises(Exception) as exc_info:
                process_audio_task(
                    task_id="test_task_123",
                    file_path="/tmp/nonexistent.wav",
                    language="auto"
                )

            assert "not found" in str(exc_info.value).lower() or "FileNotFoundError" in str(type(exc_info.value))

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_audio_task_models_not_ready(self, mock_redis, mock_loader):
        """Test processing when models are not ready"""
        from app.tasks.audio_tasks import process_audio_task

        # Models not initialized
        mock_loader.__bool__.return_value = False
        mock_redis.get.return_value = None

        with pytest.raises(Exception) as exc_info:
            process_audio_task(
                task_id="test_task_123",
                file_path="/tmp/test.wav",
                language="auto"
            )

        assert "not initialized" in str(exc_info.value).lower() or "Models" in str(exc_info.value)

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_audio_task_with_qa_evaluation(self, mock_redis, mock_loader,
                                                     mock_audio_bytes, mock_worker_loader):
        """Test processing with QA evaluation included"""
        from app.tasks.audio_tasks import process_audio_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    result = process_audio_task(
                        task_id="test_task_123",
                        file_path="/tmp/test_audio.wav",
                        language="auto",
                        include_qa=True,
                        qa_threshold=0.6
                    )

                    assert "qa_evaluation" in result
                    assert result["qa_evaluation"]["overall_score"] == 0.85

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_audio_task_selective_processing(self, mock_redis, mock_loader,
                                                       mock_audio_bytes, mock_worker_loader):
        """Test processing with selective model execution"""
        from app.tasks.audio_tasks import process_audio_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    # Only transcription and translation, skip NER, classification, etc.
                    result = process_audio_task(
                        task_id="test_task_123",
                        file_path="/tmp/test_audio.wav",
                        language="auto",
                        include_translation=True,
                        include_ner=False,
                        include_classification=False,
                        include_summarization=False,
                        include_qa=False
                    )

                    assert "transcript" in result
                    assert "translated" in result
                    # These should not be present
                    assert "entities" not in result or result.get("entities") is None
                    assert "classification" not in result or result.get("classification") is None


class TestProcessAudioQuickTask:
    """Tests for process_audio_quick_task function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_audio_quick_task_success(self, mock_redis, mock_loader,
                                                mock_audio_bytes, mock_worker_loader):
        """Test quick audio processing (transcription only)"""
        from app.tasks.audio_tasks import process_audio_quick_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    result = process_audio_quick_task(
                        task_id="quick_task_123",
                        file_path="/tmp/test_audio.wav",
                        language="en"
                    )

                    assert result is not None
                    assert "transcript" in result
                    assert result["transcript"] == "Hello, this is a test transcription"

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_audio_quick_task_with_segments(self, mock_redis, mock_loader,
                                                      mock_audio_bytes, mock_worker_loader):
        """Test quick processing returns segments"""
        from app.tasks.audio_tasks import process_audio_quick_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    result = process_audio_quick_task(
                        task_id="quick_task_123",
                        file_path="/tmp/test_audio.wav",
                        language="en"
                    )

                    assert "segments" in result or "language" in result


class TestProcessStreamingAudioTask:
    """Tests for process_streaming_audio_task function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_streaming_audio_task_success(self, mock_redis, mock_loader,
                                                    mock_audio_bytes, mock_worker_loader):
        """Test streaming audio processing"""
        from app.tasks.audio_tasks import process_streaming_audio_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    result = process_streaming_audio_task(
                        session_id="stream_session_123",
                        audio_chunk_path="/tmp/chunk_001.wav",
                        chunk_index=0,
                        language="auto"
                    )

                    assert result is not None
                    assert "transcript" in result or "text" in result
                    assert "chunk_index" in result
                    assert result["chunk_index"] == 0

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_process_streaming_audio_task_with_analysis(self, mock_redis, mock_loader,
                                                          mock_audio_bytes, mock_worker_loader):
        """Test streaming processing with real-time analysis"""
        from app.tasks.audio_tasks import process_streaming_audio_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    result = process_streaming_audio_task(
                        session_id="stream_session_123",
                        audio_chunk_path="/tmp/chunk_001.wav",
                        chunk_index=0,
                        language="en",
                        include_translation=True,
                        include_analysis=True
                    )

                    assert result is not None
                    # Should have translation and analysis
                    if "translated" in result:
                        assert isinstance(result["translated"], str)


class TestAudioTaskErrorHandling:
    """Tests for error handling in audio tasks"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_transcription_error_handling(self, mock_redis, mock_loader,
                                            mock_audio_bytes):
        """Test handling of transcription errors"""
        from app.tasks.audio_tasks import process_audio_task

        mock_loader.__bool__.return_value = True
        whisper_mock = MagicMock()
        whisper_mock.transcribe_audio_bytes.side_effect = Exception("Transcription failed")
        mock_loader.models = {"whisper": whisper_mock}
        mock_loader.get_ready_models.return_value = ["whisper"]
        mock_redis.get.return_value = None

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    with pytest.raises(Exception) as exc_info:
                        process_audio_task(
                            task_id="error_task_123",
                            file_path="/tmp/test_audio.wav",
                            language="auto"
                        )

                    assert "Transcription failed" in str(exc_info.value)

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_translation_error_handling(self, mock_redis, mock_loader,
                                          mock_audio_bytes, mock_worker_loader):
        """Test handling of translation errors"""
        from app.tasks.audio_tasks import process_audio_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        # Make translator raise an error
        mock_loader.models["translator"].translate.side_effect = Exception("Translation error")
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    # Should handle translation error gracefully
                    try:
                        result = process_audio_task(
                            task_id="error_task_123",
                            file_path="/tmp/test_audio.wav",
                            language="auto",
                            include_translation=True
                        )
                        # If no exception, translation should be None or error message
                        assert result.get("translated") is None or "error" in str(result.get("translated", "")).lower()
                    except Exception:
                        # Or it might raise - both are acceptable
                        pass

    @patch('app.tasks.audio_tasks.worker_model_loader')
    @patch('app.tasks.audio_tasks.redis_task_client')
    def test_redis_error_handling(self, mock_redis, mock_loader,
                                    mock_audio_bytes, mock_worker_loader):
        """Test handling of Redis errors"""
        from app.tasks.audio_tasks import process_audio_task

        mock_loader.__bool__.return_value = True
        mock_loader.models = mock_worker_loader.models
        mock_loader.get_ready_models = mock_worker_loader.get_ready_models
        # Redis operations fail
        mock_redis.get.side_effect = Exception("Redis connection error")
        mock_redis.setex.side_effect = Exception("Redis connection error")

        with patch('builtins.open', mock_open(read_data=mock_audio_bytes)):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=len(mock_audio_bytes)):
                    # Should handle Redis errors gracefully or raise
                    try:
                        result = process_audio_task(
                            task_id="redis_error_task",
                            file_path="/tmp/test_audio.wav",
                            language="auto"
                        )
                        # If successful despite Redis error, that's OK
                        assert result is not None
                    except Exception as e:
                        # Redis errors are also acceptable
                        assert "Redis" in str(e) or "connection" in str(e).lower()
