import pytest
import sys
import os
from io import BytesIO
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Test fixtures for different route groups
@pytest.fixture
def classifier_app():
    """FastAPI app with classifier routes"""
    from app.api.classifier_route import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def ner_app():
    """FastAPI app with NER routes"""
    from app.api.ner_routes import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def qa_app():
    """FastAPI app with QA routes"""
    from app.api.qa_route import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def summarizer_app():
    """FastAPI app with summarizer routes"""
    from app.api.summarizer_routes import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def translator_app():
    """FastAPI app with translator routes"""
    from app.api.translator_routes import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def whisper_app():
    """FastAPI app with whisper routes"""
    from app.api.whisper_routes import router
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a sample text for testing various NLP models and their functionality."

@pytest.fixture
def sample_audio_file():
    """Sample audio file for testing"""
    # Create minimal WAV file bytes
    wav_header = (
        b'RIFF' b'\x2c\x00\x00\x00' b'WAVE' b'fmt '
        b'\x10\x00\x00\x00' b'\x01\x00' b'\x01\x00'
        b'\x40\x1f\x00\x00' b'\x80\x3e\x00\x00'
        b'\x02\x00' b'\x10\x00' b'data'
        b'\x08\x00\x00\x00' b'\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    return BytesIO(wav_header)

# Classifier Route Tests
class TestClassifierRoutes:
    """Test classifier API routes"""

    @patch('app.api.classifier_route.model_loader')
    def test_classify_text_success(self, mock_loader, classifier_app, sample_text):
        """Test successful text classification"""
        mock_model = MagicMock()
        mock_model.classify.return_value = {
            "main_category": "general_inquiry",
            "sub_category": "account_support",
            "confidence": 0.89,
            "priority": "medium"
        }
        mock_loader.get_model.return_value = mock_model

        response = classifier_app.post(
            "/classifier/classify",
            json={"text": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["main_category"] == "general_inquiry"
        assert data["confidence"] == 0.89

    @patch('app.api.classifier_route.model_loader')
    def test_classify_text_empty(self, mock_loader, classifier_app):
        """Test classification with empty text"""
        mock_model = MagicMock()
        mock_model.classify.return_value = {
            "main_category": "general_inquiry",
            "confidence": 0.0
        }
        mock_loader.get_model.return_value = mock_model

        response = classifier_app.post(
            "/classifier/classify",
            json={"text": ""}
        )

        assert response.status_code == 200

    @patch('app.api.classifier_route.model_loader')
    def test_classify_model_not_loaded(self, mock_loader, classifier_app, sample_text):
        """Test classification when model is not loaded"""
        mock_loader.get_model.return_value = None

        response = classifier_app.post(
            "/classifier/classify",
            json={"text": sample_text}
        )

        assert response.status_code == 503
        assert "not available" in response.json()["detail"]

    @patch('app.api.classifier_route.model_loader')
    def test_classify_batch_success(self, mock_loader, classifier_app):
        """Test batch classification"""
        mock_model = MagicMock()
        mock_model.classify.return_value = {"main_category": "test", "confidence": 0.8}
        mock_loader.get_model.return_value = mock_model

        texts = ["Text 1", "Text 2", "Text 3"]
        response = classifier_app.post(
            "/classifier/classify-batch",
            json={"texts": texts}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_get_classifier_info(self, classifier_app):
        """Test getting classifier model information"""
        with patch('app.api.classifier_route.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.get_model_info.return_value = {
                "loaded": True,
                "categories": ["general", "technical"],
                "version": "1.0"
            }
            mock_loader.get_model.return_value = mock_model

            response = classifier_app.get("/classifier/info")

            assert response.status_code == 200
            data = response.json()
            assert data["loaded"] is True
            assert "categories" in data

# NER Route Tests
class TestNERRoutes:
    """Test NER API routes"""

    @patch('app.api.ner_routes.model_loader')
    def test_extract_entities_success(self, mock_loader, ner_app, sample_text):
        """Test successful entity extraction"""
        mock_model = MagicMock()
        mock_model.extract_entities.return_value = [
            {"text": "sample", "label": "MISC", "start": 10, "end": 16, "confidence": 0.95}
        ]
        mock_loader.get_model.return_value = mock_model

        response = ner_app.post(
            "/ner/extract",
            json={"text": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["entities"]) == 1
        assert data["entities"][0]["label"] == "MISC"

    @patch('app.api.ner_routes.model_loader')
    def test_extract_entities_grouped(self, mock_loader, ner_app, sample_text):
        """Test entity extraction with grouping"""
        mock_model = MagicMock()
        mock_model.extract_entities.return_value = {
            "PERSON": [{"text": "John", "start": 0, "end": 4}],
            "ORG": [{"text": "Company", "start": 10, "end": 17}]
        }
        mock_loader.get_model.return_value = mock_model

        response = ner_app.post(
            "/ner/extract",
            json={"text": sample_text, "flat": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert "PERSON" in data["entities"]
        assert "ORG" in data["entities"]

    def test_ner_model_info(self, ner_app):
        """Test getting NER model information"""
        with patch('app.api.ner_routes.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.get_model_info.return_value = {
                "loaded": True,
                "labels": ["PERSON", "ORG", "MISC"]
            }
            mock_loader.get_model.return_value = mock_model

            response = ner_app.get("/ner/info")

            assert response.status_code == 200
            data = response.json()
            assert data["loaded"] is True

# QA Route Tests
class TestQARoutes:
    """Test QA API routes"""

    @patch('app.api.qa_route.model_loader')
    def test_evaluate_transcript_success(self, mock_loader, qa_app):
        """Test successful transcript evaluation"""
        mock_model = MagicMock()
        mock_model.evaluate_transcript.return_value = {
            "scores": {
                "opening": 0.8,
                "listening": 0.7,
                "resolution": 0.9
            },
            "overall_score": 0.8,
            "recommendations": ["Improve greeting"]
        }
        mock_loader.get_model.return_value = mock_model

        transcript = "Hello, thank you for calling. How can I help you?"
        response = qa_app.post(
            "/qa/evaluate",
            json={"transcript": transcript}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] == 0.8
        assert "opening" in data["scores"]

    @patch('app.api.qa_route.model_loader')
    def test_evaluate_batch_transcripts(self, mock_loader, qa_app):
        """Test batch transcript evaluation"""
        mock_model = MagicMock()
        mock_model.evaluate_transcript.return_value = {
            "overall_score": 0.75,
            "scores": {"opening": 0.8}
        }
        mock_loader.get_model.return_value = mock_model

        transcripts = ["Transcript 1", "Transcript 2"]
        response = qa_app.post(
            "/qa/evaluate-batch",
            json={"transcripts": transcripts}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_qa_metrics_info(self, qa_app):
        """Test getting QA metrics information"""
        with patch('app.api.qa_route.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.get_qa_metrics.return_value = {
                "opening": "Call opening quality",
                "listening": "Active listening skills"
            }
            mock_loader.get_model.return_value = mock_model

            response = qa_app.get("/qa/metrics")

            assert response.status_code == 200
            data = response.json()
            assert "opening" in data

# Summarizer Route Tests
class TestSummarizerRoutes:
    """Test summarizer API routes"""

    @patch('app.api.summarizer_routes.model_loader')
    def test_summarize_text_success(self, mock_loader, summarizer_app, sample_text):
        """Test successful text summarization"""
        mock_model = MagicMock()
        mock_model.summarize.return_value = "This is a summary of the sample text."
        mock_loader.get_model.return_value = mock_model

        response = summarizer_app.post(
            "/summarizer/summarize",
            json={"text": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert len(data["summary"]) > 0

    @patch('app.api.summarizer_routes.model_loader')
    def test_summarize_with_custom_length(self, mock_loader, summarizer_app, sample_text):
        """Test summarization with custom length"""
        mock_model = MagicMock()
        mock_model.summarize.return_value = "Short summary."
        mock_loader.get_model.return_value = mock_model

        response = summarizer_app.post(
            "/summarizer/summarize",
            json={"text": sample_text, "max_length": 50}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Short summary."

    @patch('app.api.summarizer_routes.model_loader')
    def test_summarize_empty_text(self, mock_loader, summarizer_app):
        """Test summarization with empty text"""
        mock_model = MagicMock()
        mock_model.summarize.return_value = ""
        mock_loader.get_model.return_value = mock_model

        response = summarizer_app.post(
            "/summarizer/summarize",
            json={"text": ""}
        )

        assert response.status_code == 200

    def test_summarizer_info(self, summarizer_app):
        """Test getting summarizer information"""
        with patch('app.api.summarizer_routes.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.get_model_info.return_value = {
                "loaded": True,
                "max_input_length": 1024
            }
            mock_loader.get_model.return_value = mock_model

            response = summarizer_app.get("/summarizer/info")

            assert response.status_code == 200

# Translator Route Tests
class TestTranslatorRoutes:
    """Test translator API routes"""

    @patch('app.api.translator_routes.model_loader')
    def test_translate_text_success(self, mock_loader, translator_app, sample_text):
        """Test successful text translation"""
        mock_model = MagicMock()
        mock_model.translate.return_value = "Este es un texto de muestra para probar."
        mock_loader.get_model.return_value = mock_model

        response = translator_app.post(
            "/translator/translate",
            json={"text": sample_text, "target_language": "es"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "translation" in data
        assert data["target_language"] == "es"

    @patch('app.api.translator_routes.model_loader')
    def test_translate_with_source_language(self, mock_loader, translator_app, sample_text):
        """Test translation with specified source language"""
        mock_model = MagicMock()
        mock_model.translate.return_value = "Translated text"
        mock_loader.get_model.return_value = mock_model

        response = translator_app.post(
            "/translator/translate",
            json={
                "text": sample_text,
                "source_language": "en",
                "target_language": "fr"
            }
        )

        assert response.status_code == 200

    @patch('app.api.translator_routes.model_loader')
    def test_translate_batch_texts(self, mock_loader, translator_app):
        """Test batch translation"""
        mock_model = MagicMock()
        mock_model.translate_batch.return_value = ["Texto 1", "Texto 2"]
        mock_loader.get_model.return_value = mock_model

        texts = ["Text 1", "Text 2"]
        response = translator_app.post(
            "/translator/translate-batch",
            json={"texts": texts, "target_language": "es"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["translations"]) == 2

    def test_supported_languages(self, translator_app):
        """Test getting supported languages"""
        with patch('app.api.translator_routes.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.get_supported_languages.return_value = {
                "en": "English",
                "es": "Spanish",
                "fr": "French"
            }
            mock_loader.get_model.return_value = mock_model

            response = translator_app.get("/translator/languages")

            assert response.status_code == 200
            data = response.json()
            assert "en" in data["languages"]

# Whisper Route Tests
class TestWhisperRoutes:
    """Test Whisper API routes"""

    @patch('app.api.whisper_routes.model_loader')
    def test_transcribe_audio_success(self, mock_loader, whisper_app, sample_audio_file):
        """Test successful audio transcription"""
        mock_model = MagicMock()
        mock_model.transcribe_audio.return_value = {
            "text": "This is a transcribed audio content",
            "segments": [{"start": 0, "end": 5, "text": "This is a transcribed audio content"}]
        }
        mock_loader.get_model.return_value = mock_model

        response = whisper_app.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "en"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        assert data["transcript"] == "This is a transcribed audio content"

    @patch('app.api.whisper_routes.model_loader')
    def test_transcribe_with_segments(self, mock_loader, whisper_app, sample_audio_file):
        """Test transcription with segment information"""
        mock_model = MagicMock()
        mock_model.transcribe_audio.return_value = {
            "text": "Audio content",
            "segments": [
                {"start": 0.0, "end": 2.5, "text": "Audio"},
                {"start": 2.5, "end": 5.0, "text": "content"}
            ]
        }
        mock_loader.get_model.return_value = mock_model

        response = whisper_app.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "en", "include_segments": "true"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "segments" in data
        assert len(data["segments"]) == 2

    @patch('app.api.whisper_routes.model_loader')
    def test_transcribe_auto_language(self, mock_loader, whisper_app, sample_audio_file):
        """Test transcription with auto language detection"""
        mock_model = MagicMock()
        mock_model.transcribe_audio.return_value = {
            "text": "Detected language content"
        }
        mock_loader.get_model.return_value = mock_model

        response = whisper_app.post(
            "/whisper/transcribe",
            files={"audio": ("test.wav", sample_audio_file, "audio/wav")},
            data={"language": "auto"}
        )

        assert response.status_code == 200

    def test_transcribe_unsupported_format(self, whisper_app):
        """Test transcription with unsupported file format"""
        text_file = BytesIO(b"This is not audio")
        
        response = whisper_app.post(
            "/whisper/transcribe",
            files={"audio": ("test.txt", text_file, "text/plain")}
        )

        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    def test_whisper_supported_languages(self, whisper_app):
        """Test getting supported languages"""
        with patch('app.api.whisper_routes.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.get_supported_languages.return_value = {
                "en": "English",
                "es": "Spanish",
                "auto": "Auto-detect"
            }
            mock_loader.get_model.return_value = mock_model

            response = whisper_app.get("/whisper/languages")

            assert response.status_code == 200
            data = response.json()
            assert "languages" in data

# Cross-Route Integration Tests
class TestCrossRouteIntegration:
    """Test integration between different API routes"""

    def test_model_availability_consistency(self, classifier_app, ner_app):
        """Test that model availability is consistent across routes"""
        with patch('app.api.classifier_route.model_loader') as mock_classifier_loader, \
             patch('app.api.ner_routes.model_loader') as mock_ner_loader:
            
            # Both models unavailable
            mock_classifier_loader.get_model.return_value = None
            mock_ner_loader.get_model.return_value = None

            classifier_response = classifier_app.post("/classifier/classify", json={"text": "test"})
            ner_response = ner_app.post("/ner/extract", json={"text": "test"})

            # Both should return 503
            assert classifier_response.status_code == 503
            assert ner_response.status_code == 503

    def test_text_processing_pipeline(self, classifier_app, ner_app, summarizer_app):
        """Test a complete text processing pipeline"""
        sample_text = "John works at Microsoft and needs help with billing."

        # Mock all models
        with patch('app.api.classifier_route.model_loader') as mock_c, \
             patch('app.api.ner_routes.model_loader') as mock_n, \
             patch('app.api.summarizer_routes.model_loader') as mock_s:

            # Setup mocks
            mock_c.get_model.return_value.classify.return_value = {"main_category": "billing"}
            mock_n.get_model.return_value.extract_entities.return_value = [{"text": "John", "label": "PERSON"}]
            mock_s.get_model.return_value.summarize.return_value = "Customer billing issue"

            # Test pipeline
            classify_response = classifier_app.post("/classifier/classify", json={"text": sample_text})
            ner_response = ner_app.post("/ner/extract", json={"text": sample_text})
            summary_response = summarizer_app.post("/summarizer/summarize", json={"text": sample_text})

            assert classify_response.status_code == 200
            assert ner_response.status_code == 200
            assert summary_response.status_code == 200

# Error Handling Tests
class TestAPIErrorHandling:
    """Test error handling across all API routes"""

    def test_malformed_json_requests(self, classifier_app, ner_app, qa_app):
        """Test handling of malformed JSON requests"""
        clients = [classifier_app, ner_app, qa_app]
        endpoints = ["/classifier/classify", "/ner/extract", "/qa/evaluate"]

        for client, endpoint in zip(clients, endpoints):
            response = client.post(endpoint, data="invalid json")
            assert response.status_code == 422

    def test_missing_required_fields(self, classifier_app, ner_app):
        """Test handling of missing required fields"""
        # Missing text field
        response = classifier_app.post("/classifier/classify", json={})
        assert response.status_code == 422

        # Missing text field for NER
        response = ner_app.post("/ner/extract", json={})
        assert response.status_code == 422

    def test_model_processing_errors(self, classifier_app):
        """Test handling of model processing errors"""
        with patch('app.api.classifier_route.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.classify.side_effect = Exception("Model processing error")
            mock_loader.get_model.return_value = mock_model

            response = classifier_app.post("/classifier/classify", json={"text": "test"})
            assert response.status_code == 500

# Performance Tests
class TestAPIPerformance:
    """Test API performance characteristics"""

    def test_concurrent_requests(self, classifier_app):
        """Test handling of concurrent requests"""
        import threading
        import time

        with patch('app.api.classifier_route.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.classify.return_value = {"main_category": "test"}
            mock_loader.get_model.return_value = mock_model

            results = []

            def make_request():
                response = classifier_app.post("/classifier/classify", json={"text": "test"})
                results.append(response.status_code)

            # Start multiple threads
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()

            # Wait for completion
            for thread in threads:
                thread.join()

            # All should succeed
            assert all(status == 200 for status in results)
            assert len(results) == 5

    def test_response_times(self, classifier_app):
        """Test that API responses are reasonably fast"""
        import time

        with patch('app.api.classifier_route.model_loader') as mock_loader:
            mock_model = MagicMock()
            mock_model.classify.return_value = {"main_category": "test"}
            mock_loader.get_model.return_value = mock_model

            start_time = time.time()
            response = classifier_app.post("/classifier/classify", json={"text": "test"})
            end_time = time.time()

            assert response.status_code == 200
            # Response should be fast (under 1 second)
            assert (end_time - start_time) < 1.0