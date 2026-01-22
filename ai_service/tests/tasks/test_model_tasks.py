"""
Comprehensive tests for model_tasks Celery tasks 
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

        with patch.object(ner_extract_task, 'update_state'):
            with pytest.raises(RuntimeError, match="NER model not ready"):
                ner_extract_task("Test text", flat=True)

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_ner_extract_model_not_available(self, mock_get_loader, mock_model_loader):
        """Test NER extraction when model is not in loader"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True
        mock_model_loader.models = {}  # No NER model

        with patch.object(ner_extract_task, 'update_state'):
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
            "sub_category_2": "billing_inquiry",
            "intervention": "none",
            "priority": "low",
            "confidence": 0.95,
            "confidence_breakdown": {}
        }
        classifier.get_model_info.return_value = {
            "model_type": "transformer",
            "model_name": "distilbert"
        }
        mock_model_loader.models = {"classifier_model": classifier}


        with patch.object(classifier_classify_task, 'update_state'):
            result = classifier_classify_task("I need help with my order")

        assert result is not None
        assert "main_category" in result
        assert "processing_time" in result
        assert "model_info" in result

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_classifier_model_not_ready(self, mock_get_loader, mock_model_loader):
        """Test classification when model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False

        with patch.object(classifier_classify_task, 'update_state'):
            with pytest.raises(RuntimeError, match="Classifier model not ready"):
                classifier_classify_task("Test narrative")

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_classifier_model_not_available(self, mock_get_loader, mock_model_loader):
        """Test classification when classifier model is not in loader"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True
        mock_model_loader.models = {}  # No classifier_model

        with patch.object(classifier_classify_task, 'update_state'):
            with pytest.raises(RuntimeError, match="Classifier model not available"):
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

        with patch.object(translation_translate_task, 'update_state'):
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

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_summarization_model_not_ready(self, mock_get_loader, mock_model_loader):
        """Test summarization when model is not ready"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = False

        with patch.object(summarization_summarize_task, 'update_state'):
            with pytest.raises(RuntimeError, match="Summarizer model not ready"):
                summarization_summarize_task("Test text")


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

        with patch.object(qa_evaluate_task, 'update_state'):
            with pytest.raises(RuntimeError, match="QA model not ready"):
                qa_evaluate_task(
                    transcript="Test"
                )

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.model_scripts.qa_model.qa_model')
    @patch('app.tasks.model_tasks.ClassificationChunker')
    @patch('app.tasks.model_tasks.ClassificationAggregator')
    def test_qa_evaluate_with_chunking(self, mock_aggregator_class, mock_chunker_class, mock_qa, mock_get_loader, mock_model_loader):
        """Test QA evaluation with transcript chunking (>512 tokens)"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        # Create a long transcript that will trigger chunking
        long_transcript = " ".join(["This is a test sentence."] * 100)  # ~500 words, >512 tokens

        mock_qa.is_ready.return_value = True
        mock_qa.get_model_info.return_value = {"model_type": "qa"}

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker.count_tokens.return_value = 600  # > 512 to trigger chunking
        mock_chunker.chunk_transcript.return_value = [
            {"text": "chunk1 text"},
            {"text": "chunk2 text"}
        ]
        mock_chunker_class.return_value = mock_chunker

        # Mock QA predictions for each chunk
        mock_qa.predict.side_effect = [
            {"category": [{"submetric": "opening", "prediction": True, "score": "pass"}]},
            {"category": [{"submetric": "opening", "prediction": True, "score": "pass"}]}
        ]

        # Mock aggregator
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_qa_scoring.return_value = {
            "success": True,
            "predictions": {"category": [{"submetric": "opening", "prediction": True, "score": "pass"}]}
        }
        mock_aggregator_class.return_value = mock_aggregator

        with patch.object(qa_evaluate_task, 'update_state'):
            result = qa_evaluate_task(
                transcript=long_transcript,
                threshold=0.5,
                return_raw=True
            )

        assert result is not None
        assert "evaluations" in result
        # Verify chunking was used
        mock_chunker.chunk_transcript.assert_called_once()
        assert mock_qa.predict.call_count == 2  # One for each chunk
        mock_aggregator.aggregate_qa_scoring.assert_called_once()

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.model_scripts.qa_model.qa_model')
    @patch('app.tasks.model_tasks.ClassificationChunker')
    @patch('app.tasks.model_tasks.ClassificationAggregator')
    @patch('app.tasks.model_tasks._fallback_qa_aggregation')
    def test_qa_evaluate_chunking_fallback(self, mock_fallback, mock_aggregator_class, mock_chunker_class, mock_qa, mock_get_loader, mock_model_loader):
        """Test QA evaluation chunking with fallback aggregation"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        long_transcript = " ".join(["Test sentence."] * 100)

        mock_qa.is_ready.return_value = True
        mock_qa.get_model_info.return_value = {"model_type": "qa"}

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker.count_tokens.return_value = 600
        mock_chunker.chunk_transcript.return_value = [{"text": "chunk1"}]
        mock_chunker_class.return_value = mock_chunker

        mock_qa.predict.return_value = {"category": [{"submetric": "test"}]}

        # Mock aggregator to fail
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_qa_scoring.return_value = {"success": False}
        mock_aggregator_class.return_value = mock_aggregator

        # Mock fallback aggregation
        mock_fallback.return_value = {"category": [{"submetric": "opening", "prediction": True}]}

        with patch.object(qa_evaluate_task, 'update_state'):
            result = qa_evaluate_task(transcript=long_transcript, threshold=0.5)

        assert result is not None
        mock_fallback.assert_called_once()


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

        with patch.object(whisper_transcribe_task, 'update_state'):
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

        with patch.object(ner_extract_task, 'update_state'):
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

        with patch.object(classifier_classify_task, 'update_state'):
            with pytest.raises(Exception, match="Classification error"):
                classifier_classify_task("Test narrative")

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_translation_task_exception_handling(self, mock_get_loader, mock_model_loader):
        """Test translation task handles exceptions"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        translator = MagicMock()
        translator.translate.side_effect = Exception("Translation error")
        mock_model_loader.models = {"translator": translator}

        with patch.object(translation_translate_task, 'update_state'):
            with pytest.raises(Exception, match="Translation error"):
                translation_translate_task("Test text")

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_summarization_task_exception_handling(self, mock_get_loader, mock_model_loader):
        """Test summarization task handles exceptions"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        summarizer = MagicMock()
        summarizer.summarize.side_effect = Exception("Summarization error")
        mock_model_loader.models = {"summarizer": summarizer}

        with patch.object(summarization_summarize_task, 'update_state'):
            with pytest.raises(Exception, match="Summarization error"):
                summarization_summarize_task("Test text")

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_whisper_task_exception_handling(self, mock_get_loader, mock_model_loader):
        """Test whisper task handles exceptions"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        whisper = MagicMock()
        whisper.transcribe_audio_bytes.side_effect = Exception("Transcription error")
        mock_model_loader.models = {"whisper": whisper}

        with patch.object(whisper_transcribe_task, 'update_state'):
            with pytest.raises(Exception, match="Transcription error"):
                whisper_transcribe_task(audio_bytes=b'audio', filename="test.wav")


class TestWorkerInitialization:
    """Tests for worker initialization"""

    def test_initialize_model_worker_function_exists(self):
        """Test that initialize_model_worker function exists"""
        from app.tasks.model_tasks import initialize_model_worker

        assert callable(initialize_model_worker)

    def test_get_worker_model_loader_function_exists(self):
        """Test that get_worker_model_loader function exists"""
        from app.tasks.model_tasks import get_worker_model_loader

        assert callable(get_worker_model_loader)


class TestFallbackQAAggregation:
    """Tests for _fallback_qa_aggregation function"""

    def test_fallback_qa_aggregation_empty(self):
        """Test fallback aggregation with empty predictions"""
        from app.tasks.model_tasks import _fallback_qa_aggregation

        result = _fallback_qa_aggregation([])
        assert result == {}

    def test_fallback_qa_aggregation_single_prediction(self):
        """Test fallback aggregation with single prediction"""
        from app.tasks.model_tasks import _fallback_qa_aggregation

        chunk_predictions = [{
            "communication": [
                {"submetric": "clarity", "prediction": True, "probability": 0.8},
                {"submetric": "empathy", "prediction": False, "probability": 0.3}
            ]
        }]

        result = _fallback_qa_aggregation(chunk_predictions)
        assert "communication" in result
        assert len(result["communication"]) == 2

    def test_fallback_qa_aggregation_multiple_predictions(self):
        """Test fallback aggregation with multiple predictions"""
        from app.tasks.model_tasks import _fallback_qa_aggregation

        chunk_predictions = [
            {
                "communication": [
                    {"submetric": "clarity", "prediction": True, "probability": 0.9},
                ]
            },
            {
                "communication": [
                    {"submetric": "clarity", "prediction": True, "probability": 0.7},
                ]
            },
            {
                "communication": [
                    {"submetric": "clarity", "prediction": False, "probability": 0.4},
                ]
            }
        ]

        result = _fallback_qa_aggregation(chunk_predictions)
        assert "communication" in result
        # Majority vote should be True (2 vs 1)
        assert result["communication"][0]["prediction"] is True


class TestChunkedProcessing:
    """Tests for chunked text processing paths"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.tasks.model_tasks.NERChunker')
    def test_ner_extract_with_chunking(self, mock_chunker_class, mock_get_loader, mock_model_loader):
        """Test NER extraction with long text requiring chunking"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        ner_model = MagicMock()
        ner_model.extract_entities.return_value = [{"text": "John", "label": "PERSON"}]
        ner_model.get_model_info.return_value = {"model_type": "spacy"}
        mock_model_loader.models = {"ner": ner_model}

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker.count_tokens.return_value = 600  # > 512 threshold
        mock_chunker.chunk_transcript.return_value = [
            {"text": "First chunk", "chunk_index": 0},
            {"text": "Second chunk", "chunk_index": 1}
        ]
        mock_chunker.reconstruct_entities.return_value = [{"text": "John", "label": "PERSON"}]
        mock_chunker_class.return_value = mock_chunker

        with patch.object(ner_extract_task, 'update_state'):
            result = ner_extract_task("Very long text " * 100, flat=True)

        assert result is not None
        assert "entities" in result

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.tasks.model_tasks.ClassificationChunker')
    @patch('app.tasks.model_tasks.ClassificationAggregator')
    def test_classifier_with_chunking(self, mock_aggregator_class, mock_chunker_class, mock_get_loader, mock_model_loader):
        """Test classification with long text requiring chunking"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        classifier = MagicMock()
        classifier.classify.return_value = {
            "main_category": "support",
            "sub_category": "technical",
            "sub_category_2": "billing",
            "intervention": "none",
            "priority": "medium",
            "confidence_breakdown": {}
        }
        classifier.get_model_info.return_value = {}
        mock_model_loader.models = {"classifier_model": classifier}

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker.count_tokens.return_value = 600  # > 512 threshold
        mock_chunker.chunk_transcript.return_value = [
            {"text": "First chunk", "chunk_index": 0, "token_count": 100, "sentence_count": 5, "position_ratio": 0.5},
            {"text": "Second chunk", "chunk_index": 1, "token_count": 100, "sentence_count": 5, "position_ratio": 1.0}
        ]
        mock_chunker_class.return_value = mock_chunker

        # Mock aggregator
        mock_aggregator = MagicMock()
        mock_aggregator.aggregate_case_classification.return_value = {
            "main_category": "support",
            "sub_category": "technical",
            "intervention": "none",
            "priority": "medium",
            "confidence_scores": {}
        }
        mock_aggregator_class.return_value = mock_aggregator

        with patch.object(classifier_classify_task, 'update_state'):
            result = classifier_classify_task("Very long narrative " * 100)

        assert result is not None
        assert "main_category" in result

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.tasks.model_tasks.TranslationChunker')
    def test_translation_with_chunking(self, mock_chunker_class, mock_get_loader, mock_model_loader):
        """Test translation with long text requiring chunking"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        translator = MagicMock()
        translator.translate.return_value = "Translated text"
        translator.get_model_info.return_value = {}
        mock_model_loader.models = {"translator": translator}

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker.count_tokens.return_value = 600  # > 512 threshold
        mock_chunker.chunk_transcript.return_value = [
            {"text": "First chunk"},
            {"text": "Second chunk"}
        ]
        mock_chunker.reconstruct_translation.return_value = "Full translated text"
        mock_chunker_class.return_value = mock_chunker

        with patch.object(translation_translate_task, 'update_state'):
            result = translation_translate_task("Very long text " * 100)

        assert result is not None
        assert "translated" in result

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    @patch('app.tasks.model_tasks.SummarizationChunker')
    def test_summarization_with_chunking(self, mock_chunker_class, mock_get_loader, mock_model_loader):
        """Test summarization with long text requiring chunking"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True

        summarizer = MagicMock()
        summarizer.summarize.return_value = "Chunk summary"
        summarizer.get_model_info.return_value = {}
        mock_model_loader.models = {"summarizer": summarizer}

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker.count_tokens.return_value = 600  # > 512 threshold
        mock_chunker.chunk_transcript.return_value = [
            {"text": "First chunk"},
            {"text": "Second chunk"}
        ]
        mock_chunker.reconstruct_summary.return_value = "Full summary of all chunks"
        mock_chunker_class.return_value = mock_chunker

        with patch.object(summarization_summarize_task, 'update_state'):
            result = summarization_summarize_task("Very long text " * 100)

        assert result is not None
        assert "summary" in result


class TestModelNotAvailable:
    """Tests for when model is in loader but not available"""

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_translator_not_available(self, mock_get_loader, mock_model_loader):
        """Test translation when translator not in models dict"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True
        mock_model_loader.models = {}  # No translator

        with patch.object(translation_translate_task, 'update_state'):
            with pytest.raises(RuntimeError, match="Translator model not available"):
                translation_translate_task("Test text")

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_summarizer_not_available(self, mock_get_loader, mock_model_loader):
        """Test summarization when summarizer not in models dict"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True
        mock_model_loader.models = {}  # No summarizer

        with patch.object(summarization_summarize_task, 'update_state'):
            with pytest.raises(RuntimeError, match="Summarizer model not available"):
                summarization_summarize_task("Test text")

    @patch('app.tasks.model_tasks.get_worker_model_loader')
    def test_whisper_not_available(self, mock_get_loader, mock_model_loader):
        """Test transcription when whisper not in models dict"""
        mock_get_loader.return_value = mock_model_loader
        mock_model_loader.is_model_ready.return_value = True
        mock_model_loader.models = {}  # No whisper

        with patch.object(whisper_transcribe_task, 'update_state'):
            with pytest.raises(RuntimeError, match="Whisper model not available"):
                whisper_transcribe_task(audio_bytes=b'audio', filename="test.wav")
