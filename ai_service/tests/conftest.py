# tests/conftest.py
#  test support
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
from datetime import datetime

# Add project root to Python path for all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Async test support
pytest_plugins = ('pytest_asyncio',)

# Global fixture to patch settings for all tests .....
@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    """Globally patch settings paths for all tests"""
    monkeypatch.setattr(
        "app.config.settings.Settings.get_model_path",
        lambda self, name: f"/fake/{name}/path"
    )

# Model fixtures
@pytest.fixture
def mock_classifier_model():
    """Fixture for mocked classifier model"""
    with patch("app.model_scripts.classifier_model.AutoTokenizer.from_pretrained"), \
         patch("app.model_scripts.classifier_model.MultiTaskDistilBert.from_pretrained"), \
         patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='["violence", "neglect"]')), \
         patch("json.load", side_effect=[
             ["violence", "neglect"],
             ["physical_abuse", "emotional_abuse"],
             ["intervention_1", "intervention_2"],
             ["low", "medium", "high", "urgent"]
         ]):
        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.load_time = datetime.now()
        model.tokenizer = MagicMock()
        model.model = MagicMock()
        model.main_categories = ["violence", "neglect"]
        model.sub_categories = ["physical_abuse", "emotional_abuse"]
        model.interventions = ["intervention_1", "intervention_2"]
        model.priorities = ["low", "medium", "high", "urgent"]
        return model

@pytest.fixture
def mock_ner_model():
    """Fixture for mocked NER model"""
    with patch("app.model_scripts.ner_model.spacy.load") as mock_spacy_load, \
         patch("os.path.exists", return_value=False):

        # Fake SpaCy nlp pipeline mock
        mock_nlp = MagicMock()
        mock_nlp.meta = {
            "version": "3.8.0",
            "lang": "en"
        }
        mock_nlp.pipe_names = ["ner"]
        mock_nlp.get_pipe.return_value.labels = ["PERSON", "ORG"]

        # Simulated entity object
        mock_ent = MagicMock()
        mock_ent.text = "Barack Obama"
        mock_ent.label_ = "PERSON"
        mock_ent.start_char = 0
        mock_ent.end_char = 12
        mock_ent.confidence = 0.99

        # Mocked document returned by nlp("...")
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]

        # When mock_nlp is called (like nlp(text)), return the mock_doc
        mock_nlp.side_effect = lambda text: mock_doc

        # Set spacy.load(...) to return the mocked nlp
        mock_spacy_load.return_value = mock_nlp

        from app.model_scripts.ner_model import NERModel
        model = NERModel()
        model.nlp = mock_nlp
        model.loaded = True
        model.load_time = datetime.now()
        return model

@pytest.fixture
def mock_summarizer_model():
    """Fixture for mocked summarizer model"""
    with patch("app.model_scripts.summarizer_model.AutoTokenizer.from_pretrained"), \
         patch("app.model_scripts.summarizer_model.AutoModelForSeq2SeqLM.from_pretrained"), \
         patch("app.model_scripts.summarizer_model.pipeline"), \
         patch("os.path.exists", return_value=True):

        from app.model_scripts.summarizer_model import SummarizationModel
        model = SummarizationModel()
        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = list(range(100))  # Simulate 100 tokens
        model.pipeline = MagicMock()
        model.pipeline.return_value = [{"summary_text": "Mocked summary"}]
        model.loaded = True
        model.load_time = datetime.now()
        return model

@pytest.fixture
def mock_whisper_model():
    """Fixture for mocked Whisper model"""
    with patch("app.model_scripts.whisper_model.whisper.load_model") as mock_load, \
         patch("os.path.exists", return_value=True):
        
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Mocked transcription",
            "segments": [{"start": 0, "end": 5, "text": "Mocked transcription"}]
        }
        mock_load.return_value = mock_model
        
        from app.model_scripts.whisper_model import WhisperModel
        model = WhisperModel()
        model.model = mock_model
        model.loaded = True
        model.load_time = datetime.now()
        return model

@pytest.fixture
def mock_translator_model():
    """Fixture for mocked translator model"""
    with patch("app.model_scripts.translator_model.AutoTokenizer.from_pretrained"), \
         patch("app.model_scripts.translator_model.AutoModelForSeq2SeqLM.from_pretrained"), \
         patch("app.model_scripts.translator_model.pipeline"), \
         patch("os.path.exists", return_value=True):

        from app.model_scripts.translator_model import TranslatorModel
        model = TranslatorModel()
        model.tokenizer = MagicMock()
        model.pipeline = MagicMock()
        model.pipeline.return_value = [{"translation_text": "Mocked translation"}]
        model.loaded = True
        model.load_time = datetime.now()
        return model

# Streaming component fixtures
@pytest.fixture
def mock_tcp_server():
    """Fixture for mocked TCP server"""
    from app.streaming.tcp_server import AsteriskTCPServer
    server = AsteriskTCPServer()
    return server

@pytest.fixture
def mock_audio_buffer():
    """Fixture for mocked audio buffer"""
    from app.streaming.audio_buffer import AsteriskAudioBuffer
    return AsteriskAudioBuffer()

# Test data fixtures
@pytest.fixture
def sample_audio_chunk():
    """Sample audio chunk data"""
    return b'\x00' * 640  # 20ms of silence

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a sample text for testing various NLP models."

@pytest.fixture
def sample_long_text():
    """Sample long text for testing chunking"""
    return "This is a long text. " * 100

# Common mock configurations
@pytest.fixture
def mock_celery_task():
    """Fixture for mocking Celery tasks"""
    with patch('app.tasks.audio_tasks.process_streaming_audio_task.delay') as mock_task:
        mock_task.return_value.id = "test_task_123"
        yield mock_task

# Async service fixtures
@pytest.fixture
def mock_call_session_manager():
    """Global fixture for mocked call session manager with AsyncMock"""
    manager = AsyncMock()
    manager.get_all_active_sessions = AsyncMock(return_value=[])
    manager.get_session_stats = AsyncMock(return_value={
        "active_sessions": 0,
        "total_sessions_today": 0,
        "average_duration": 0.0,
        "success_rate": 1.0
    })
    manager.get_session = AsyncMock(return_value=None)
    manager.end_session = AsyncMock(return_value=None)
    manager._trigger_ai_pipeline = AsyncMock(return_value=True)
    return manager

@pytest.fixture
def mock_progressive_processor():
    """Global fixture for mocked progressive processor"""
    processor = MagicMock()
    processor.get_status.return_value = {
        "active_processors": 0,
        "queue_size": 0,
        "processing_rate": 0.0,
        "average_latency": 0.0
    }
    processor.get_call_processing_status.return_value = {
        "call_id": "test_call",
        "processing_stage": "idle",
        "progress": 0.0
    }
    processor.get_call_analysis.return_value = None
    return processor

@pytest.fixture
def mock_agent_notification_service():
    """Global fixture for mocked agent notification service"""
    service = AsyncMock()
    service.get_health_status = AsyncMock(return_value={
        "status": "healthy",
        "notifications_sent": 0,
        "success_rate": 1.0
    })
    service.send_call_start = AsyncMock(return_value=True)
    service.send_test_notification = AsyncMock(return_value=True)
    service._ensure_valid_token = AsyncMock(return_value=True)
    service.bearer_token = "mock_token_12345"
    service.token_expires_at = datetime.now()
    return service
