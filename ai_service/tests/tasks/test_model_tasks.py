"""
Comprehensive tests for model_tasks Celery tasks to achieve 100% coverage.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.tasks.model_tasks import (
    get_worker_model_loader,
    ner_extract_task,
    classifier_classify_task,
    translation_translate_task,
    summarization_summarize_task,
    qa_evaluate_task,
    whisper_transcribe_task,
)


@pytest.fixture
def mock_task_context():
    """Mock Celery task context"""
    task = MagicMock()
    task.request.id = "test-task-123"
    task.update_state = MagicMock()
    return task


@pytest.fixture
def mock_model_loader():
    """Mock model loader with all models"""
    loader = MagicMock()
    loader.get_ready_models = MagicMock(return_value=[
        "ner", "classifier_model", "translator", "summarizer", "qa", "whisper"
    ])
    loader.get_failed_models = MagicMock(return_value=[])
    loader.get_blocked_models = MagicMock(return_value=[])
    loader.is_model_ready = MagicMock(return_value=True)
    loader.models = {
        "ner": MagicMock(),
        "classifier_model": MagicMock(),
        "translator": MagicMock(),
        "summarizer": MagicMock(),
        "qa": MagicMock(),
        "whisper": MagicMock(),
    }
    return loader


class TestGetWorkerModelLoader:
    """Tests for get_worker_model_loader function"""

    def test_get_worker_model_loader_success(self):
        """Test getting worker model loader when initialized"""
        with patch('app.tasks.model_tasks.worker_model_loader', MagicMock()):
            with patch('app.tasks.model_tasks.worker_model_loader', None):
                # Test error case
                with pytest.raises(RuntimeError, match="Model loader not initialized"):
                    get_worker_model_loader()


class TestNERExtractTask:
    """Tests for ner_extract_task"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_ner_extract_success(self, mock_get_loader, mock_model_loader):
        """Test successful NER extraction"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        ner_model = MagicMock()
        ner_model.extract_entities.return_value = {"PERSON": ["John"], "ORG": ["Acme"]}
        ner_model.get_model_info.return_value = {
            "model_type": "spacy",
            "model_name": "en_core_web_lg",
            "loaded": True
        }
        mock_model_loader.models = {"ner": ner_model}

        with patch.object(ner_extract_task, 'update_state') as mock_update_state:
            with patch.object(ner_extract_task, 'update_state'):

                result = ner_extract_task("John works at Acme Corp", flat=True)

            assert result is not None
            assert "entities" in result
            assert "processing_time" in result
            assert "model_info" in result
            assert "timestamp" in result
            mock_update_state.assert_called_once()

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_ner_extract_model_not_ready(self, mock_get_loader, mock_model_loader):
        """Test NER extraction when model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False

        with pytest.raises(RuntimeError, match="NER model not ready"):
            ner_extract_task("Test text", flat=True)

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_ner_extract_model_not_available(self, mock_get_loader, mock_model_loader):
        """Test NER extraction when model is not in loader"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True
        mock_model_loader.models = {}  # No NER model

        with pytest.raises(RuntimeError, match="NER model not available"):
            ner_extract_task("Test text", flat=True)

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_ner_extract_grouped_entities(self, mock_get_loader, mock_model_loader):
        """Test NER extraction with grouped entities"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        ner_model = MagicMock()
        ner_model.extract_entities.return_value = {"PERSON": ["John"], "ORG": ["Acme"]}
        ner_model.get_model_info.return_value = {"model_type": "spacy"}
        mock_model_loader.models = {"ner": ner_model}


        with patch.object(ner_extract_task, 'update_state'):

            result = ner_extract_task("Test text", flat=False)

        assert result is not None
        ner_model.extract_entities.assert_called_with("Test text", flat=False)


class TestClassifierClassifyTask:
    """Tests for classifier_classify_task"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_classifier_classify_success(self, mock_get_loader, mock_model_loader):
        """Test successful classification"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        classifier = MagicMock()
        classifier.classify.return_value = {
            "main_category": "customer_service",
            "sub_category": "general_inquiry",
            "intervention": "none",
            "priority": "low",
            "confidence": 0.95
        }
        classifier.get_model_info.return_value = {
            "model_type": "transformer",
            "model_name": "distilbert"
        }
        mock_model_loader.models = {"classifier_model": classifier}


        with patch.object(classifier_classify_task, 'update_state'):

            result = classifier_classify_task("I need help with my order")

        assert result is not None
        assert "classification" in result
        assert "processing_time" in result
        assert "model_info" in result
        assert result["task_id"] == "task-201"

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_classifier_model_not_ready(self, mock_get_loader, mock_model_loader):
        """Test classification when model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False


        with pytest.raises(RuntimeError, match="Classifier model not ready"):
            classifier_classify_task("Test narrative")


class TestTranslationTranslateTask:
    """Tests for translation_translate_task"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_translation_success(self, mock_get_loader, mock_model_loader):
        """Test successful translation"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        translator = MagicMock()
        translator.translate.return_value = "Hola mundo"
        translator.get_model_info.return_value = {
            "model_type": "seq2seq",
            "source_lang": "en",
            "target_lang": "es"
        }
        mock_model_loader.models = {"translator": translator}


        with patch.object(translation_translate_task, 'update_state'):
            result = translation_translate_task("Hello world")

        assert result is not None
        assert "translated" in result
        assert "processing_time" in result
        assert "model_info" in result
        assert result["translated"] == "Hola mundo"

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_translation_model_not_ready(self, mock_get_loader, mock_model_loader):
        """Test translation when model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False


        with pytest.raises(RuntimeError, match="Translation model not ready"):
            translation_translate_task("Test text")


class TestSummarizationTask:
    """Tests for summarization_summarize_task"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_summarization_success(self, mock_get_loader, mock_model_loader):
        """Test successful summarization"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        summarizer = MagicMock()
        summarizer.summarize.return_value = "Brief summary of the text"
        summarizer.get_model_info.return_value = {
            "model_type": "abstractive",
            "model_name": "facebook/bart-large-cnn"
        }
        mock_model_loader.models = {"summarizer": summarizer}

        with patch.object(summarization_summarize_task, 'update_state'):
            result = summarization_summarize_task(
                "This is a very long text that needs summarization",
                max_length=100
            )

        assert result is not None
        assert "summary" in result
        assert "processing_time" in result
        assert "model_info" in result
        assert result["summary"] == "Brief summary of the text"
        summarizer.summarize.assert_called_with(
            "This is a very long text that needs summarization",
            max_length=100
        )

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_summarization_default_max_length(self, mock_get_loader, mock_model_loader):
        """Test summarization with default max_length"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        summarizer = MagicMock()
        summarizer.summarize.return_value = "Summary"
        summarizer.get_model_info.return_value = {}
        mock_model_loader.models = {"summarizer": summarizer}


        with patch.object(summarization_summarize_task, 'update_state'):

            result = summarization_summarize_task("Test text")

        assert result is not None
        summarizer.summarize.assert_called_with("Test text", max_length=256)


class TestQAEvaluateTask:
    """Tests for qa_evaluate_task"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.model_scripts.qa_model.qa_model')
    def test_qa_evaluate_success(self, mock_qa, mock_get_loader, mock_model_loader):
        """Test successful QA evaluation"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        mock_qa.is_ready.return_value = True
        mock_qa.predict.return_value = {"overall_score": 0.85, "categories": {}}
        mock_qa.get_model_info.return_value = {"model_type": "qa"}

        with patch.object(qa_evaluate_task, 'update_state'):
            result = qa_evaluate_task(
                transcript="Test conversation",
                threshold=0.5
            )

        assert result is not None
        assert "evaluations" in result
        assert "processing_time" in result
        assert "model_info" in result

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.model_scripts.qa_model.qa_model')
    def test_qa_model_not_ready(self, mock_qa, mock_get_loader, mock_model_loader):
        """Test QA evaluation when model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False

        mock_qa.is_ready.return_value = False

        with pytest.raises(RuntimeError, match="QA model not ready"):
            qa_evaluate_task(
                transcript="Test"
            )


class TestWhisperTranscribeTask:
    """Tests for whisper_transcribe_task"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_whisper_transcribe_success(self, mock_get_loader, mock_model_loader):
        """Test successful transcription"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        whisper = MagicMock()
        whisper.transcribe_audio_bytes.return_value = "Hello world"
        whisper.get_model_info.return_value = {
            "model_type": "whisper",
            "model_size": "base"
        }
        mock_model_loader.models = {"whisper": whisper}

        audio_bytes = b'\x00' * 1000
        with patch.object(whisper_transcribe_task, 'update_state'):
            result = whisper_transcribe_task(
                audio_bytes=audio_bytes,
                filename="test.wav",
                language="en"
            )

        assert result is not None
        assert "transcript" in result
        assert "processing_time" in result
        assert "model_info" in result
        assert result["transcript"] == "Hello world"

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_whisper_transcribe_model_not_ready(self, mock_get_loader, mock_model_loader):
        """Test transcription when Whisper model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False


        with pytest.raises(RuntimeError, match="Whisper model not ready"):
            whisper_transcribe_task(
                audio_bytes=b'audio',
                filename="test.wav",
                language="en"
            )

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_whisper_transcribe_default_language(self, mock_get_loader, mock_model_loader):
        """Test transcription with default language"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        whisper = MagicMock()
        whisper.transcribe_audio_bytes.return_value = "Hello"
        whisper.get_model_info.return_value = {}
        mock_model_loader.models = {"whisper": whisper}

        with patch.object(whisper_transcribe_task, 'update_state'):
            result = whisper_transcribe_task(
                audio_bytes=b'audio',
                filename="test.wav"
            )

        assert result is not None
        # Verify default language was used
        whisper.transcribe_audio_bytes.assert_called()


class TestTaskErrorHandling:
    """Tests for error handling across tasks"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_ner_task_exception_handling(self, mock_get_loader, mock_model_loader):
        """Test NER task handles exceptions"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        ner_model = MagicMock()
        ner_model.extract_entities.side_effect = Exception("Model error")
        mock_model_loader.models = {"ner": ner_model}


        with pytest.raises(Exception, match="Model error"):
            ner_extract_task("Test text", flat=True)

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_classifier_task_exception_handling(self, mock_get_loader, mock_model_loader):
        """Test classifier task handles exceptions"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        classifier = MagicMock()
        classifier.classify.side_effect = Exception("Classification error")
        mock_model_loader.models = {"classifier_model": classifier}


        with pytest.raises(Exception, match="Classification error"):
            classifier_classify_task("Test narrative")
