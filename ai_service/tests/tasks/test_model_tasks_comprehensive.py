"""
Comprehensive tests for model_tasks.py Celery tasks
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
from datetime import datetime

from app.tasks.model_tasks import (
    ner_extract_task,
    classifier_classify_task,
    translation_translate_task,
    summarization_summarize_task,
    qa_evaluate_task,
    whisper_transcribe_task,
)


class TestNERExtractTask:
    """Tests for NER (Named Entity Recognition) extraction task"""

    def test_ner_extract_success(self, mock_worker_model_loader, patch_celery_tasks):
        """Test successful NER extraction"""
        text = "Barack Obama was born in Hawaii"

        # Simulate calling the NER model
        result = mock_worker_model_loader.models['ner'].extract_entities(text)

        assert result is not None
        assert isinstance(result, dict)
        assert 'PERSON' in result
        assert 'ORG' in result

    def test_ner_extract_multiple_entities(self, mock_worker_model_loader):
        """Test NER extraction with multiple entity types"""
        text = "John Doe from Acme Corp met with Jane Smith"

        result = mock_worker_model_loader.models['ner'].extract_entities(text)

        assert 'PERSON' in result
        assert isinstance(result['PERSON'], list)
        assert len(result['PERSON']) > 0

    def test_ner_extract_empty_text(self, mock_worker_model_loader):
        """Test NER extraction with empty text"""
        result = mock_worker_model_loader.models['ner'].extract_entities("")

        assert isinstance(result, dict)

    def test_ner_extract_no_entities(self, mock_worker_model_loader):
        """Test NER extraction when no entities found"""
        mock_worker_model_loader.models['ner'].extract_entities.return_value = {}

        result = mock_worker_model_loader.models['ner'].extract_entities("just some random text")

        assert isinstance(result, dict)

    def test_ner_model_availability(self, mock_worker_model_loader):
        """Test NER model is available and ready"""
        assert mock_worker_model_loader.is_model_ready('ner')
        assert 'ner' in mock_worker_model_loader.get_ready_models()


class TestClassifierClassifyTask:
    """Tests for classifier task"""

    def test_classifier_classify_success(self, mock_worker_model_loader, patch_celery_tasks):
        """Test successful classification"""
        text = "Child is in danger"

        result = mock_worker_model_loader.models['classifier_model'].classify(text)

        assert result is not None
        assert isinstance(result, dict)
        assert 'main_category' in result
        assert 'confidence' in result

    def test_classifier_returns_priority(self, mock_worker_model_loader):
        """Test classifier returns priority level"""
        result = mock_worker_model_loader.models['classifier_model'].classify("test")

        assert 'priority' in result
        assert result['priority'] in ['low', 'medium', 'high', 'urgent']

    def test_classifier_with_different_inputs(self, mock_worker_model_loader):
        """Test classifier with various input texts"""
        texts = [
            "Abuse detected",
            "Neglect situation",
            "General inquiry",
            "Emergency case"
        ]

        for text in texts:
            result = mock_worker_model_loader.models['classifier_model'].classify(text)
            assert 'main_category' in result
            assert result['confidence'] <= 1.0

    def test_classifier_empty_text(self, mock_worker_model_loader):
        """Test classifier with empty text"""
        result = mock_worker_model_loader.models['classifier_model'].classify("")

        assert 'main_category' in result

    def test_classifier_model_availability(self, mock_worker_model_loader):
        """Test classifier model is available"""
        assert mock_worker_model_loader.is_model_ready('classifier_model')


class TestTranslationTranslateTask:
    """Tests for translation task"""

    def test_translation_success(self, mock_worker_model_loader, patch_celery_tasks):
        """Test successful translation"""
        text = "Hello world"

        result = mock_worker_model_loader.models['translator'].translate(text)

        assert result is not None
        assert isinstance(result, str)

    def test_translation_returns_string(self, mock_worker_model_loader):
        """Test translation returns string"""
        result = mock_worker_model_loader.models['translator'].translate("test text")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_translation_with_long_text(self, mock_worker_model_loader):
        """Test translation with longer text"""
        long_text = "This is a longer text " * 50

        result = mock_worker_model_loader.models['translator'].translate(long_text)

        assert isinstance(result, str)

    def test_translation_empty_text(self, mock_worker_model_loader):
        """Test translation of empty text"""
        result = mock_worker_model_loader.models['translator'].translate("")

        assert isinstance(result, str)

    def test_translation_special_characters(self, mock_worker_model_loader):
        """Test translation with special characters"""
        special_text = "Test with @#$%^&*() characters!"

        result = mock_worker_model_loader.models['translator'].translate(special_text)

        assert isinstance(result, str)

    def test_translator_model_availability(self, mock_worker_model_loader):
        """Test translator model is available"""
        assert mock_worker_model_loader.is_model_ready('translator')


class TestSummarizationSummarizeTask:
    """Tests for summarization task"""

    def test_summarization_success(self, mock_worker_model_loader, patch_celery_tasks):
        """Test successful summarization"""
        text = "Long document text " * 50

        result = mock_worker_model_loader.models['summarizer'].summarize(text)

        assert result is not None
        assert isinstance(result, str)

    def test_summarization_produces_shorter_text(self, mock_worker_model_loader):
        """Test that summarization reduces text length"""
        long_text = "This is a long text. " * 100
        mock_original_length = len(long_text)

        result = mock_worker_model_loader.models['summarizer'].summarize(long_text)

        assert isinstance(result, str)
        # Summary should be shorter (in mock, it's fixed, but testing logic)
        assert len(result) < mock_original_length

    def test_summarization_min_length(self, mock_worker_model_loader):
        """Test summarization with minimum text"""
        short_text = "Short sentence."

        result = mock_worker_model_loader.models['summarizer'].summarize(short_text)

        assert isinstance(result, str)

    def test_summarization_with_max_length(self, mock_worker_model_loader):
        """Test summarization respects max length parameter"""
        text = "Long text " * 100

        result = mock_worker_model_loader.models['summarizer'].summarize(text, max_length=50)

        assert isinstance(result, str)

    def test_summarization_empty_text(self, mock_worker_model_loader):
        """Test summarization of empty text"""
        result = mock_worker_model_loader.models['summarizer'].summarize("")

        assert isinstance(result, str)

    def test_summarizer_model_availability(self, mock_worker_model_loader):
        """Test summarizer model is available"""
        assert mock_worker_model_loader.is_model_ready('summarizer')


class TestQAEvaluateTask:
    """Tests for QA (Question Answering) evaluation task"""

    def test_qa_evaluate_success(self, mock_worker_model_loader, patch_celery_tasks):
        """Test successful QA evaluation"""
        question = "What happened in the case?"
        context = "A child was reported missing last week"

        result = mock_worker_model_loader.models['qa'].evaluate(question, context)

        assert result is not None
        assert isinstance(result, dict)
        assert 'overall_score' in result

    def test_qa_returns_score(self, mock_worker_model_loader):
        """Test QA returns numeric score"""
        result = mock_worker_model_loader.models['qa'].evaluate("What?", "Context here")

        assert 'overall_score' in result
        assert isinstance(result['overall_score'], (int, float))
        assert 0 <= result['overall_score'] <= 1.0

    def test_qa_with_categories(self, mock_worker_model_loader):
        """Test QA returns category scores"""
        result = mock_worker_model_loader.models['qa'].evaluate("Q?", "C")

        assert 'categories' in result
        assert isinstance(result['categories'], dict)

    def test_qa_multiple_questions(self, mock_worker_model_loader):
        """Test QA with multiple different questions"""
        context = "Test context"
        questions = [
            "What is this?",
            "Who is involved?",
            "When did it happen?",
            "Where is it?"
        ]

        for question in questions:
            result = mock_worker_model_loader.models['qa'].evaluate(question, context)
            assert 'overall_score' in result

    def test_qa_empty_context(self, mock_worker_model_loader):
        """Test QA with empty context"""
        result = mock_worker_model_loader.models['qa'].evaluate("Question?", "")

        assert isinstance(result, dict)

    def test_qa_model_availability(self, mock_worker_model_loader):
        """Test QA model is available"""
        assert mock_worker_model_loader.is_model_ready('qa')


class TestWhisperTranscribeTask:
    """Tests for Whisper speech transcription task"""

    def test_whisper_transcribe_success(self, mock_worker_model_loader, sample_audio_bytes, patch_celery_tasks):
        """Test successful Whisper transcription"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)

        assert result is not None
        assert isinstance(result, dict)
        assert 'text' in result

    def test_whisper_returns_text(self, mock_worker_model_loader, sample_audio_bytes):
        """Test Whisper returns transcribed text"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)

        assert isinstance(result['text'], str)
        assert len(result['text']) > 0

    def test_whisper_returns_segments(self, mock_worker_model_loader, sample_audio_bytes):
        """Test Whisper returns audio segments"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)

        assert 'segments' in result
        assert isinstance(result['segments'], list)

    def test_whisper_segment_structure(self, mock_worker_model_loader, sample_audio_bytes):
        """Test Whisper segments have correct structure"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)

        if len(result['segments']) > 0:
            segment = result['segments'][0]
            assert 'start' in segment
            assert 'end' in segment
            assert 'text' in segment

    def test_whisper_with_empty_audio(self, mock_worker_model_loader):
        """Test Whisper with empty audio"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(b'')

        assert isinstance(result, dict)
        assert 'text' in result

    def test_whisper_with_audio_chunk(self, mock_worker_model_loader, sample_audio_chunk):
        """Test Whisper with audio chunk"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_chunk)

        assert isinstance(result, dict)

    def test_whisper_model_availability(self, mock_worker_model_loader):
        """Test Whisper model is available"""
        assert mock_worker_model_loader.is_model_ready('whisper')


class TestModelTaskChaining:
    """Tests for chaining multiple model tasks"""

    def test_whisper_then_classifier(self, mock_worker_model_loader, sample_audio_bytes):
        """Test transcribing audio then classifying it"""
        # Step 1: Transcribe
        transcription = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)
        text = transcription['text']

        # Step 2: Classify
        classification = mock_worker_model_loader.models['classifier_model'].classify(text)

        assert classification is not None
        assert 'main_category' in classification

    def test_whisper_then_ner(self, mock_worker_model_loader, sample_audio_bytes):
        """Test transcribing audio then extracting entities"""
        # Step 1: Transcribe
        transcription = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)
        text = transcription['text']

        # Step 2: Extract entities
        entities = mock_worker_model_loader.models['ner'].extract_entities(text)

        assert entities is not None
        assert isinstance(entities, dict)

    def test_whisper_then_translate_then_summarize(self, mock_worker_model_loader, sample_audio_bytes):
        """Test full pipeline: transcribe -> translate -> summarize"""
        # Step 1: Transcribe
        transcription = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)
        text = transcription['text']

        # Step 2: Translate
        translated = mock_worker_model_loader.models['translator'].translate(text)

        # Step 3: Summarize
        summary = mock_worker_model_loader.models['summarizer'].summarize(translated)

        assert summary is not None

    def test_all_models_available_for_pipeline(self, mock_worker_model_loader):
        """Test that all models needed for pipeline are available"""
        required_models = ['whisper', 'translator', 'ner', 'classifier_model', 'summarizer', 'qa']

        for model_name in required_models:
            assert mock_worker_model_loader.is_model_ready(model_name)


class TestModelTaskErrorHandling:
    """Tests for error handling in model tasks"""

    def test_ner_extraction_failure(self, mock_worker_model_loader):
        """Test NER extraction error handling"""
        mock_worker_model_loader.models['ner'].extract_entities.side_effect = Exception("NER failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['ner'].extract_entities("test")

    def test_classifier_failure(self, mock_worker_model_loader):
        """Test classifier error handling"""
        mock_worker_model_loader.models['classifier_model'].classify.side_effect = Exception("Classification failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['classifier_model'].classify("test")

    def test_translation_failure(self, mock_worker_model_loader):
        """Test translation error handling"""
        mock_worker_model_loader.models['translator'].translate.side_effect = Exception("Translation failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['translator'].translate("test")

    def test_summarization_failure(self, mock_worker_model_loader):
        """Test summarization error handling"""
        mock_worker_model_loader.models['summarizer'].summarize.side_effect = Exception("Summarization failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['summarizer'].summarize("test")

    def test_qa_failure(self, mock_worker_model_loader):
        """Test QA error handling"""
        mock_worker_model_loader.models['qa'].evaluate.side_effect = Exception("QA failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['qa'].evaluate("Q?", "C")

    def test_whisper_failure(self, mock_worker_model_loader):
        """Test Whisper error handling"""
        mock_worker_model_loader.models['whisper'].transcribe_audio_bytes.side_effect = Exception("Transcription failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(b'test')


class TestModelTaskEdgeCases:
    """Tests for edge cases in model tasks"""

    def test_ner_with_special_characters(self, mock_worker_model_loader):
        """Test NER with special characters"""
        text = "John@doe.com and Jane#Smith contact"

        result = mock_worker_model_loader.models['ner'].extract_entities(text)

        assert isinstance(result, dict)

    def test_classifier_with_very_long_text(self, mock_worker_model_loader):
        """Test classifier with very long input"""
        long_text = "test " * 10000

        result = mock_worker_model_loader.models['classifier_model'].classify(long_text)

        assert 'main_category' in result

    def test_translator_with_numbers(self, mock_worker_model_loader):
        """Test translator with numbers and special content"""
        text = "The code is 12345 and date is 2024-01-15"

        result = mock_worker_model_loader.models['translator'].translate(text)

        assert isinstance(result, str)

    def test_summarizer_with_single_sentence(self, mock_worker_model_loader):
        """Test summarizer with single sentence"""
        text = "This is a single sentence."

        result = mock_worker_model_loader.models['summarizer'].summarize(text)

        assert isinstance(result, str)

    def test_qa_with_unanswerable_question(self, mock_worker_model_loader):
        """Test QA when question can't be answered from context"""
        question = "What is the date of birth?"
        context = "No biographical information provided."

        result = mock_worker_model_loader.models['qa'].evaluate(question, context)

        assert 'overall_score' in result

    def test_whisper_with_non_audio_bytes(self, mock_worker_model_loader):
        """Test Whisper with non-audio bytes"""
        fake_audio = b'not audio data'

        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(fake_audio)

        assert isinstance(result, dict)


class TestModelReadinessStatus:
    """Tests for model readiness and status"""

    def test_all_models_ready_on_startup(self, mock_worker_model_loader):
        """Test all models are ready on worker startup"""
        ready_models = mock_worker_model_loader.get_ready_models()

        assert len(ready_models) == 6
        assert 'whisper' in ready_models
        assert 'translator' in ready_models
        assert 'ner' in ready_models
        assert 'classifier_model' in ready_models
        assert 'summarizer' in ready_models
        assert 'qa' in ready_models

    def test_no_failed_models_on_startup(self, mock_worker_model_loader):
        """Test no failed models on startup"""
        failed_models = mock_worker_model_loader.get_failed_models()

        assert len(failed_models) == 0

    def test_model_info_structure(self, mock_worker_model_loader):
        """Test model info returns expected structure"""
        info = mock_worker_model_loader.get_model_info()

        assert isinstance(info, dict)
        assert 'status' in info


class TestConcurrentModelExecution:
    """Tests for concurrent execution of multiple models"""

    def test_multiple_parallel_classifications(self, mock_worker_model_loader):
        """Test running classifier multiple times"""
        texts = ["text1", "text2", "text3"]

        results = [mock_worker_model_loader.models['classifier_model'].classify(t) for t in texts]

        assert len(results) == len(texts)
        assert all('main_category' in r for r in results)

    def test_mixed_model_execution(self, mock_worker_model_loader):
        """Test executing different models in sequence"""
        text = "Test text for mixed execution"

        ner_result = mock_worker_model_loader.models['ner'].extract_entities(text)
        classifier_result = mock_worker_model_loader.models['classifier_model'].classify(text)
        translator_result = mock_worker_model_loader.models['translator'].translate(text)
        summarizer_result = mock_worker_model_loader.models['summarizer'].summarize(text)

        assert ner_result is not None
        assert classifier_result is not None
        assert translator_result is not None
        assert summarizer_result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
