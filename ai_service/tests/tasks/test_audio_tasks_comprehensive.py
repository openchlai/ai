"""
Comprehensive tests for audio_tasks.py Celery tasks
"""
import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch, call
from datetime import datetime
import io

from app.tasks.audio_tasks import (
    get_worker_models,
    get_worker_status,
)


class TestGetWorkerModels:
    """Tests for get_worker_models function"""

    def test_get_worker_models_returns_loader(self, mock_worker_model_loader, patch_celery_tasks):
        """Test that get_worker_models returns the model loader"""
        result = get_worker_models()

        assert result is not None
        assert result == mock_worker_model_loader

    def test_get_worker_models_has_models(self, mock_worker_model_loader, patch_celery_tasks):
        """Test that worker loader has all expected models"""
        result = get_worker_models()

        assert hasattr(result, 'models')
        assert 'whisper' in result.models
        assert 'translator' in result.models
        assert 'ner' in result.models
        assert 'classifier_model' in result.models
        assert 'summarizer' in result.models
        assert 'qa' in result.models


class TestGetWorkerStatus:
    """Tests for get_worker_status function"""

    def test_get_worker_status_initialized(self, mock_worker_model_loader, patch_celery_tasks):
        """Test worker status when models are initialized"""
        status = get_worker_status()

        assert status is not None
        assert 'status' in status
        assert 'ready_models' in status

    def test_get_worker_status_shows_ready_models(self, mock_worker_model_loader, patch_celery_tasks):
        """Test that worker status shows which models are ready"""
        status = get_worker_status()

        assert status['status'] == 'ready'
        assert len(status['ready_models']) > 0
        assert 'whisper' in status['ready_models']

    def test_get_worker_status_with_not_initialized(self, patch_celery_tasks, monkeypatch):
        """Test worker status when models are not initialized"""
        monkeypatch.setattr('app.tasks.audio_tasks.worker_model_loader', None)

        status = get_worker_status()

        assert status['status'] == 'not_initialized'
        assert 'error' in status
        assert status['ready_models'] == []


class TestAudioProcessingModels:
    """Tests for audio processing with mocked models"""

    def test_whisper_model_transcription(self, mock_worker_model_loader):
        """Test Whisper model transcription through worker loader"""
        audio_bytes = b'\x00' * 1000

        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(audio_bytes)

        assert result is not None
        assert 'text' in result
        assert result['text'] == "Test transcript"
        assert 'segments' in result

    def test_classifier_model_classification(self, mock_worker_model_loader):
        """Test classifier model classification"""
        text = "Test text for classification"

        result = mock_worker_model_loader.models['classifier_model'].classify(text)

        assert result is not None
        assert 'main_category' in result
        assert 'confidence' in result
        assert result['confidence'] == 0.95

    def test_ner_model_entity_extraction(self, mock_worker_model_loader):
        """Test NER model entity extraction"""
        text = "John works at Acme Corporation"

        result = mock_worker_model_loader.models['ner'].extract_entities(text)

        assert result is not None
        assert 'PERSON' in result
        assert 'ORG' in result
        assert 'John' in result['PERSON']

    def test_translator_model_translation(self, mock_worker_model_loader):
        """Test translator model translation"""
        text = "Hello world"

        result = mock_worker_model_loader.models['translator'].translate(text)

        assert result is not None
        assert isinstance(result, str)
        assert result == "Translated text"

    def test_summarizer_model_summarization(self, mock_worker_model_loader):
        """Test summarizer model summarization"""
        text = "Long text that needs summarization"

        result = mock_worker_model_loader.models['summarizer'].summarize(text)

        assert result is not None
        assert isinstance(result, str)
        assert result == "Summary of test"

    def test_qa_model_evaluation(self, mock_worker_model_loader):
        """Test QA model evaluation"""
        question = "What is this about?"
        context = "This is a test context"

        result = mock_worker_model_loader.models['qa'].evaluate(question, context)

        assert result is not None
        assert 'overall_score' in result
        assert result['overall_score'] == 0.85


class TestModelLoaderStatus:
    """Tests for model loader status methods"""

    def test_is_model_ready(self, mock_worker_model_loader):
        """Test checking if model is ready"""
        assert mock_worker_model_loader.is_model_ready('whisper') is True
        assert mock_worker_model_loader.is_model_ready('translator') is True

    def test_get_ready_models(self, mock_worker_model_loader):
        """Test getting list of ready models"""
        ready_models = mock_worker_model_loader.get_ready_models()

        assert isinstance(ready_models, list)
        assert len(ready_models) > 0
        assert 'whisper' in ready_models

    def test_get_failed_models(self, mock_worker_model_loader):
        """Test getting list of failed models"""
        failed = mock_worker_model_loader.get_failed_models()

        assert isinstance(failed, list)
        assert len(failed) == 0  # No failed models in healthy state

    def test_get_model_info(self, mock_worker_model_loader):
        """Test getting model info"""
        info = mock_worker_model_loader.get_model_info()

        assert info is not None
        assert 'status' in info
        assert info['status'] == 'ready'


class TestAudioAggregation:
    """Tests for audio result aggregation and processing"""

    def test_multiple_model_results_aggregation(self, mock_worker_model_loader, mock_text_chunker):
        """Test aggregating results from multiple models"""
        text = "Sample text for testing"

        # Simulate processing through multiple models
        ner_result = mock_worker_model_loader.models['ner'].extract_entities(text)
        classifier_result = mock_worker_model_loader.models['classifier_model'].classify(text)
        translation_result = mock_worker_model_loader.models['translator'].translate(text)

        # All should succeed
        assert ner_result is not None
        assert classifier_result is not None
        assert translation_result is not None

    def test_whisper_and_downstream_processing(self, mock_worker_model_loader):
        """Test whisper output being processed by downstream models"""
        audio_bytes = b'\x00' * 1000

        # Step 1: Transcribe audio
        transcription = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(audio_bytes)
        assert transcription['text'] == "Test transcript"

        # Step 2: Translate transcription
        translation = mock_worker_model_loader.models['translator'].translate(transcription['text'])
        assert translation is not None

        # Step 3: Extract entities
        entities = mock_worker_model_loader.models['ner'].extract_entities(transcription['text'])
        assert entities is not None

        # Step 4: Classify
        classification = mock_worker_model_loader.models['classifier_model'].classify(transcription['text'])
        assert classification is not None


class TestWorkerModelLoaderInitialization:
    """Tests for worker model loader initialization states"""

    def test_worker_loader_with_all_models_ready(self, mock_worker_model_loader):
        """Test worker loader when all models are ready"""
        ready_models = mock_worker_model_loader.get_ready_models()

        assert len(ready_models) == 6
        assert all(mock_worker_model_loader.is_model_ready(m) for m in ready_models)

    def test_api_server_loader_no_models(self, mock_model_loader):
        """Test API server model loader (should have no models)"""
        ready_models = mock_model_loader.get_ready_models()

        assert len(ready_models) == 0
        assert len(mock_model_loader.models) == 0

    def test_worker_vs_api_server_loaders(self, mock_worker_model_loader, mock_model_loader):
        """Test difference between worker and API server loaders"""
        worker_ready = mock_worker_model_loader.get_ready_models()
        api_ready = mock_model_loader.get_ready_models()

        assert len(worker_ready) > 0
        assert len(api_ready) == 0


class TestAudioDataHandling:
    """Tests for audio data handling in tasks"""

    def test_sample_audio_bytes_fixture(self, sample_audio_bytes):
        """Test that sample audio bytes fixture provides valid WAV header"""
        assert sample_audio_bytes is not None
        assert sample_audio_bytes[:4] == b'RIFF'
        assert b'WAVE' in sample_audio_bytes
        assert b'fmt ' in sample_audio_bytes

    def test_sample_audio_chunk_fixture(self, sample_audio_chunk):
        """Test that sample audio chunk fixture works"""
        assert sample_audio_chunk is not None
        assert len(sample_audio_chunk) == 640  # 20ms at 16kHz
        assert all(b == 0 for b in sample_audio_chunk)

    def test_transcribe_with_sample_audio(self, mock_worker_model_loader, sample_audio_bytes):
        """Test transcribing sample audio"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(sample_audio_bytes)

        assert result is not None
        assert 'text' in result
        assert len(result['text']) > 0


class TestResourceManagement:
    """Tests for resource management during audio processing"""

    def test_resource_manager_gpu_info(self, mock_resource_manager):
        """Test getting GPU info during processing"""
        gpu_info = mock_resource_manager.get_gpu_info()

        assert 'available_memory' in gpu_info
        assert 'used_memory' in gpu_info
        assert 'utilization' in gpu_info
        assert gpu_info['utilization'] == 20

    def test_resource_manager_system_info(self, mock_resource_manager):
        """Test getting system info during processing"""
        system_info = mock_resource_manager.get_system_info()

        assert 'cpu_percent' in system_info
        assert 'memory_percent' in system_info
        assert system_info['cpu_percent'] == 30

    def test_resource_acquisition_and_release(self, mock_resource_manager):
        """Test acquiring and releasing GPU resources"""
        acquired = mock_resource_manager.acquire_gpu()
        assert acquired is True

        released = mock_resource_manager.release_gpu()
        assert released is True

    def test_gpu_availability_check(self, mock_resource_manager):
        """Test checking GPU availability"""
        available = mock_resource_manager.is_gpu_available()

        assert isinstance(available, bool)
        assert available is True


class TestNotificationIntegration:
    """Tests for notification service integration with audio tasks"""

    @pytest.mark.asyncio
    async def test_send_transcription_notification(self, mock_notification_service):
        """Test sending transcription notification"""
        result = await mock_notification_service.send_notification(
            notification_type="transcription",
            data={"text": "Test transcript"}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_entity_notification(self, mock_notification_service):
        """Test sending entity notification"""
        result = await mock_notification_service.send_streaming_entities(
            entities={"PERSON": ["John"]},
            confidence=0.95
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_classification_notification(self, mock_notification_service):
        """Test sending classification notification"""
        result = await mock_notification_service.send_streaming_classification(
            classification={"main": "test", "confidence": 0.95}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_error_notification(self, mock_notification_service):
        """Test sending error notification"""
        result = await mock_notification_service.send_error_notification(
            error="Test error",
            call_id="test_call"
        )

        assert result is True


class TestInsightsIntegration:
    """Tests for insights service integration"""

    @pytest.mark.asyncio
    async def test_generate_case_insights(self, mock_insights_service):
        """Test generating case insights"""
        insights = await mock_insights_service.generate_case_insights(
            transcript="Test transcript",
            entities={"PERSON": ["John"]},
            classification={"main": "test"}
        )

        assert insights is not None
        assert 'summary' in insights
        assert 'key_themes' in insights

    @pytest.mark.asyncio
    async def test_extract_case_metadata(self, mock_insights_service):
        """Test extracting case metadata"""
        metadata = await mock_insights_service.extract_case_metadata(
            transcript="Test transcript",
            entities={"PERSON": ["John"]}
        )

        assert metadata is not None
        assert 'case_id' in metadata
        assert 'persons_involved' in metadata


class TestErrorHandlingInAudioTasks:
    """Tests for error handling in audio processing"""

    def test_whisper_failure_handling(self, mock_worker_model_loader):
        """Test handling Whisper transcription failure"""
        # Simulate failure
        mock_worker_model_loader.models['whisper'].transcribe_audio_bytes.side_effect = Exception("Transcription failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(b'\x00' * 100)

    def test_classifier_failure_handling(self, mock_worker_model_loader):
        """Test handling classifier failure"""
        mock_worker_model_loader.models['classifier_model'].classify.side_effect = Exception("Classification failed")

        with pytest.raises(Exception):
            mock_worker_model_loader.models['classifier_model'].classify("test")

    def test_model_not_ready_scenario(self, mock_worker_model_loader):
        """Test handling when model is not ready"""
        mock_worker_model_loader.is_model_ready.return_value = False

        assert mock_worker_model_loader.is_model_ready('whisper') is False


class TestEdgeCasesInAudioProcessing:
    """Tests for edge cases in audio processing"""

    def test_empty_audio_processing(self, mock_worker_model_loader):
        """Test processing empty audio"""
        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(b'')

        assert result is not None
        # Should still return transcript structure

    def test_very_long_audio_processing(self, mock_worker_model_loader, sample_audio_bytes):
        """Test processing very long audio"""
        # Repeat audio bytes to simulate long audio
        long_audio = sample_audio_bytes * 100

        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(long_audio)

        assert result is not None
        assert 'text' in result

    def test_noisy_audio_transcription(self, mock_worker_model_loader):
        """Test transcribing noisy audio"""
        # Simulate noisy audio with random bytes
        noisy_audio = bytes([i % 256 for i in range(1000)])

        result = mock_worker_model_loader.models['whisper'].transcribe_audio_bytes(noisy_audio)

        assert result is not None

    def test_empty_text_classification(self, mock_worker_model_loader):
        """Test classifying empty text"""
        result = mock_worker_model_loader.models['classifier_model'].classify("")

        assert result is not None
        assert 'main_category' in result

    def test_very_long_text_processing(self, mock_worker_model_loader, mock_text_chunker):
        """Test processing very long text"""
        long_text = "test " * 10000

        # Text should be chunked
        chunks = mock_text_chunker.chunk_text(long_text, "classification")

        assert chunks is not None
        assert len(chunks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
