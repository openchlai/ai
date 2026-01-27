"""
Comprehensive tests for model_tasks.py - all Celery model tasks
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, mock_open
from datetime import datetime


@pytest.fixture
def mock_model_loader():
    """Mock model loader with all models"""
    loader = MagicMock()

    # NER model
    ner = MagicMock()
    ner.extract_entities.return_value = {
        "entities": {
            "PERSON": ["John Doe", "Mary Smith"],
            "ORG": ["Acme Corp"],
            "LOC": ["New York"]
        }
    }

    # Classifier model
    classifier = MagicMock()
    classifier.classify.return_value = {
        "main_category": "general_inquiry",
        "sub_category": "information_request",
        "intervention": "provide_information",
        "priority": "normal",
        "confidence_scores": {
            "main_category": 0.95,
            "sub_category": 0.88,
            "intervention": 0.92,
            "priority": 0.90
        }
    }

    # Translator model
    translator = MagicMock()
    translator.translate.return_value = "Translated text"

    # Summarizer model
    summarizer = MagicMock()
    summarizer.summarize.return_value = "This is a summary of the text"

    # QA model
    qa = MagicMock()
    qa.evaluate.return_value = {
        "overall_score": 0.85,
        "categories": {
            "opening": {"score": 0.9, "passed": True},
            "listening": {"score": 0.8, "passed": True}
        }
    }

    # Whisper model
    whisper = MagicMock()
    whisper.transcribe_audio_bytes.return_value = {
        "text": "This is a transcription",
        "language": "en",
        "segments": []
    }

    loader.models = {
        "ner": ner,
        "classifier_model": classifier,
        "translator": translator,
        "summarizer": summarizer,
        "qa": qa,
        "whisper": whisper
    }

    return loader


class TestInitializeModelWorker:
    """Tests for initialize_model_worker function"""

    @patch('app.tasks.model_tasks.ModelLoader')
    @patch('app.tasks.model_tasks.logger')
    def test_initialize_model_worker_success(self, mock_logger, mock_loader_class):
        """Test successful model worker initialization"""
        from app.tasks.model_tasks import initialize_model_worker

        # Setup mock
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_all_models_sync.return_value = True
        mock_loader_instance.get_ready_models.return_value = ["ner", "classifier", "whisper"]
        mock_loader_instance.get_failed_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = []
        mock_loader_class.return_value = mock_loader_instance

        # Call initialization
        initialize_model_worker()

        # Verify
        mock_loader_class.assert_called_once()
        mock_loader_instance.load_all_models_sync.assert_called_once()
        mock_logger.info.assert_called()

    @patch('app.tasks.model_tasks.ModelLoader')
    @patch('app.tasks.model_tasks.logger')
    def test_initialize_model_worker_no_models_loaded(self, mock_logger, mock_loader_class):
        """Test initialization when no models are loaded"""
        from app.tasks.model_tasks import initialize_model_worker

        mock_loader_instance = MagicMock()
        mock_loader_instance.load_all_models_sync.return_value = True
        mock_loader_instance.get_ready_models.return_value = []
        mock_loader_instance.get_failed_models.return_value = ["ner", "classifier"]
        mock_loader_instance.get_blocked_models.return_value = ["whisper"]
        mock_loader_class.return_value = mock_loader_instance

        initialize_model_worker()

        # Should log warnings about no models loaded
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any("No models" in call or "WARNING" in call for call in error_calls)

    @patch('app.tasks.model_tasks.ModelLoader')
    @patch('app.tasks.model_tasks.logger')
    def test_initialize_model_worker_loading_failed(self, mock_logger, mock_loader_class):
        """Test initialization when model loading fails"""
        from app.tasks.model_tasks import initialize_model_worker

        mock_loader_instance = MagicMock()
        mock_loader_instance.load_all_models_sync.return_value = False
        mock_loader_class.return_value = mock_loader_instance

        initialize_model_worker()

        # Should log error
        mock_logger.error.assert_called()

    @patch('app.tasks.model_tasks.ModelLoader')
    @patch('app.tasks.model_tasks.logger')
    def test_initialize_model_worker_exception(self, mock_logger, mock_loader_class):
        """Test initialization with exception"""
        from app.tasks.model_tasks import initialize_model_worker

        mock_loader_class.side_effect = Exception("Failed to create loader")

        initialize_model_worker()

        # Should log exception
        mock_logger.exception.assert_called()


class TestGetWorkerModelLoader:
    """Tests for get_worker_model_loader function"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_get_worker_model_loader_initialized(self, mock_loader):
        """Test getting loader when initialized"""
        from app.tasks.model_tasks import get_worker_model_loader

        mock_loader.__bool__.return_value = True

        result = get_worker_model_loader()

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_get_worker_model_loader_not_initialized(self):
        """Test getting loader when not initialized"""
        from app.tasks.model_tasks import get_worker_model_loader

        with pytest.raises(RuntimeError) as exc_info:
            get_worker_model_loader()

        assert "not initialized" in str(exc_info.value)


class TestNERExtractTask:
    """Tests for ner_extract_task"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    @patch('app.tasks.model_tasks.track_model_time')
    @patch('app.tasks.model_tasks.update_model_status')
    def test_ner_extract_task_success(self, mock_status, mock_track, mock_loader, mock_model_loader):
        """Test successful NER extraction"""
        from app.tasks.model_tasks import ner_extract_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = ner_extract_task("John works at Acme Corp in New York", flat=True)

        assert result is not None
        assert "entities" in result
        assert "PERSON" in result["entities"]

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_ner_extract_task_grouped_output(self, mock_loader, mock_model_loader):
        """Test NER extraction with grouped output"""
        from app.tasks.model_tasks import ner_extract_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = ner_extract_task("John works at Acme", flat=False)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_ner_extract_task_long_text(self, mock_loader, mock_model_loader):
        """Test NER extraction with long text (chunking)"""
        from app.tasks.model_tasks import ner_extract_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        long_text = "This is a very long text. " * 200  # Create long text

        result = ner_extract_task(long_text, flat=True)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_ner_extract_task_model_not_ready(self):
        """Test NER task when model is not ready"""
        from app.tasks.model_tasks import ner_extract_task

        with pytest.raises(RuntimeError):
            ner_extract_task("Some text")


class TestClassifierClassifyTask:
    """Tests for classifier_classify_task"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    @patch('app.tasks.model_tasks.track_model_time')
    def test_classifier_classify_task_success(self, mock_track, mock_loader, mock_model_loader):
        """Test successful classification"""
        from app.tasks.model_tasks import classifier_classify_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = classifier_classify_task("This is a general inquiry about services")

        assert result is not None
        assert "main_category" in result
        assert "confidence_scores" in result

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_classifier_classify_task_long_text(self, mock_loader, mock_model_loader):
        """Test classification with long text"""
        from app.tasks.model_tasks import classifier_classify_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        long_narrative = "This is a long narrative. " * 150

        result = classifier_classify_task(long_narrative)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_classifier_classify_task_model_not_ready(self):
        """Test classification when model is not ready"""
        from app.tasks.model_tasks import classifier_classify_task

        with pytest.raises(RuntimeError):
            classifier_classify_task("Some text")


class TestTranslationTranslateTask:
    """Tests for translation_translate_task"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    @patch('app.tasks.model_tasks.track_model_time')
    def test_translation_translate_task_success(self, mock_track, mock_loader, mock_model_loader):
        """Test successful translation"""
        from app.tasks.model_tasks import translation_translate_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = translation_translate_task("Habari yako")

        assert result is not None
        assert "translated" in result
        assert result["translated"] == "Translated text"

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_translation_translate_task_long_text(self, mock_loader, mock_model_loader):
        """Test translation with long text"""
        from app.tasks.model_tasks import translation_translate_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        long_text = "Habari yako. " * 200

        result = translation_translate_task(long_text)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_translation_translate_task_model_not_ready(self):
        """Test translation when model is not ready"""
        from app.tasks.model_tasks import translation_translate_task

        with pytest.raises(RuntimeError):
            translation_translate_task("Some text")


class TestSummarizationSummarizeTask:
    """Tests for summarization_summarize_task"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    @patch('app.tasks.model_tasks.track_model_time')
    def test_summarization_summarize_task_success(self, mock_track, mock_loader, mock_model_loader):
        """Test successful summarization"""
        from app.tasks.model_tasks import summarization_summarize_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = summarization_summarize_task("This is a long text that needs summarization")

        assert result is not None
        assert "summary" in result

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_summarization_summarize_task_with_max_length(self, mock_loader, mock_model_loader):
        """Test summarization with custom max length"""
        from app.tasks.model_tasks import summarization_summarize_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = summarization_summarize_task("Text to summarize", max_length=100)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_summarization_summarize_task_long_text(self, mock_loader, mock_model_loader):
        """Test summarization with very long text"""
        from app.tasks.model_tasks import summarization_summarize_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        long_text = "This is a paragraph. " * 300

        result = summarization_summarize_task(long_text, max_length=150)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_summarization_summarize_task_model_not_ready(self):
        """Test summarization when model is not ready"""
        from app.tasks.model_tasks import summarization_summarize_task

        with pytest.raises(RuntimeError):
            summarization_summarize_task("Some text")


class TestQAEvaluateTask:
    """Tests for qa_evaluate_task"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    @patch('app.tasks.model_tasks.track_model_time')
    def test_qa_evaluate_task_success(self, mock_track, mock_loader, mock_model_loader):
        """Test successful QA evaluation"""
        from app.tasks.model_tasks import qa_evaluate_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        transcript = "Hello, this is 116 helpline. How can I help you?"

        result = qa_evaluate_task(transcript, threshold=0.5)

        assert result is not None
        assert "overall_score" in result or "categories" in result

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_qa_evaluate_task_custom_threshold(self, mock_loader, mock_model_loader):
        """Test QA evaluation with custom threshold"""
        from app.tasks.model_tasks import qa_evaluate_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = qa_evaluate_task("Call transcript", threshold=0.7, return_raw=False)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_qa_evaluate_task_return_raw(self, mock_loader, mock_model_loader):
        """Test QA evaluation with return_raw=True"""
        from app.tasks.model_tasks import qa_evaluate_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        result = qa_evaluate_task("Call transcript", threshold=0.5, return_raw=True)

        assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_qa_evaluate_task_model_not_ready(self):
        """Test QA evaluation when model is not ready"""
        from app.tasks.model_tasks import qa_evaluate_task

        with pytest.raises(RuntimeError):
            qa_evaluate_task("Some transcript")


class TestWhisperTranscribeTask:
    """Tests for whisper_transcribe_task"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    @patch('app.tasks.model_tasks.track_model_time')
    def test_whisper_transcribe_task_success(self, mock_track, mock_loader, mock_model_loader):
        """Test successful transcription"""
        from app.tasks.model_tasks import whisper_transcribe_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        audio_bytes = b'\x00\x01\x02\x03' * 1000

        with patch('builtins.open', mock_open(read_data=audio_bytes)):
            with patch('os.path.exists', return_value=True):
                result = whisper_transcribe_task("/tmp/audio.wav", language="auto")

                assert result is not None
                assert "text" in result or "transcript" in result

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_whisper_transcribe_task_specific_language(self, mock_loader, mock_model_loader):
        """Test transcription with specific language"""
        from app.tasks.model_tasks import whisper_transcribe_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        audio_bytes = b'\x00\x01\x02\x03' * 1000

        with patch('builtins.open', mock_open(read_data=audio_bytes)):
            with patch('os.path.exists', return_value=True):
                result = whisper_transcribe_task("/tmp/audio.wav", language="sw")

                assert result is not None

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_whisper_transcribe_task_file_not_found(self, mock_loader, mock_model_loader):
        """Test transcription when file doesn't exist"""
        from app.tasks.model_tasks import whisper_transcribe_task

        mock_loader.models = mock_model_loader.models
        mock_loader.__bool__.return_value = True

        with patch('os.path.exists', return_value=False):
            with pytest.raises(Exception):
                whisper_transcribe_task("/tmp/nonexistent.wav")

    @patch('app.tasks.model_tasks.worker_model_loader', None)
    def test_whisper_transcribe_task_model_not_ready(self):
        """Test transcription when model is not ready"""
        from app.tasks.model_tasks import whisper_transcribe_task

        with pytest.raises(RuntimeError):
            whisper_transcribe_task("/tmp/audio.wav")


class TestModelTasksErrorHandling:
    """Tests for error handling across all model tasks"""

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_ner_task_model_error(self, mock_loader):
        """Test NER task when model raises error"""
        from app.tasks.model_tasks import ner_extract_task

        mock_loader.__bool__.return_value = True
        ner_mock = MagicMock()
        ner_mock.extract_entities.side_effect = Exception("NER model error")
        mock_loader.models = {"ner": ner_mock}

        with pytest.raises(Exception) as exc_info:
            ner_extract_task("Some text")

        assert "NER model error" in str(exc_info.value)

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_classifier_task_model_error(self, mock_loader):
        """Test classifier task when model raises error"""
        from app.tasks.model_tasks import classifier_classify_task

        mock_loader.__bool__.return_value = True
        classifier_mock = MagicMock()
        classifier_mock.classify.side_effect = Exception("Classification error")
        mock_loader.models = {"classifier_model": classifier_mock}

        with pytest.raises(Exception) as exc_info:
            classifier_classify_task("Some text")

        assert "Classification error" in str(exc_info.value)

    @patch('app.tasks.model_tasks.worker_model_loader')
    def test_translation_task_model_error(self, mock_loader):
        """Test translation task when model raises error"""
        from app.tasks.model_tasks import translation_translate_task

        mock_loader.__bool__.return_value = True
        translator_mock = MagicMock()
        translator_mock.translate.side_effect = Exception("Translation error")
        mock_loader.models = {"translator": translator_mock}

        with pytest.raises(Exception) as exc_info:
            translation_translate_task("Some text")

        assert "Translation error" in str(exc_info.value)
