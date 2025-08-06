import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
import factory


# Configure Django settings before importing other modules
import django
from django.conf import settings
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
    django.setup()

# Now import Django REST framework components
from rest_framework.test import APIClient
from core.models import AudioFile


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database"""
    pass


@pytest.fixture
def api_client():
    """Provide API client for testing"""
    return APIClient()


@pytest.fixture
def sample_text():
    """Sample text for testing text processing pipelines"""
    return "Barack Obama was the 44th President of the United States. He visited New York on January 15, 2023."


@pytest.fixture
def sample_audio_file():
    """Create a mock audio file for testing"""
    # Create a simple WAV file content (minimal header)
    wav_content = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    return SimpleUploadedFile(
        name="test_audio.wav",
        content=wav_content,
        content_type="audio/wav"
    )


@pytest.fixture
def sample_audio_path(tmp_path):
    """Create a temporary audio file path for testing"""
    audio_file = tmp_path / "test_audio.wav"
    # Write minimal WAV content
    wav_content = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    audio_file.write_bytes(wav_content)
    return str(audio_file)


@pytest.fixture
def mock_whisper_model():
    """Mock Whisper model for transcription tests"""
    mock_model = Mock()
    mock_model.transcribe.return_value = {
        "text": "This is a test transcription from Whisper",
        "language": "en"
    }
    return mock_model


@pytest.fixture
def mock_spacy_nlp():
    """Mock spaCy NLP model"""
    mock_ent1 = Mock()
    mock_ent1.text = "Barack Obama"
    mock_ent1.label_ = "PERSON"
    
    mock_ent2 = Mock()
    mock_ent2.text = "United States"
    mock_ent2.label_ = "GPE"
    
    mock_doc = Mock()
    mock_doc.ents = [mock_ent1, mock_ent2]
    
    mock_nlp = Mock()
    mock_nlp.return_value = mock_doc
    return mock_nlp


@pytest.fixture
def mock_requests():
    """Mock requests for external API calls"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'response': json.dumps({
            "case_summary": "Test case summary",
            "classification": {"category": "test", "priority_level": "medium"},
            "named_entities": {"persons": ["John Doe"], "locations": ["New York"]}
        })
    }
    mock_response.raise_for_status.return_value = None
    
    with patch('requests.post', return_value=mock_response) as mock_post:
        yield mock_post


@pytest.fixture
def mock_transformers():
    """Mock transformers models"""
    mock_pipeline = Mock()
    mock_pipeline.return_value = [{"summary_text": "This is a test summary"}]
    
    mock_tokenizer = Mock()
    mock_model = Mock()
    
    return {
        'pipeline': mock_pipeline,
        'tokenizer': mock_tokenizer,
        'model': mock_model
    }


# Factory for AudioFile model
class AudioFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AudioFile
    
    audio = factory.django.FileField(filename='test_audio.wav')
    transcript = factory.Faker('text', max_nb_chars=200)
    translated_text = factory.Faker('text', max_nb_chars=200)
    annotated_text = factory.Faker('text', max_nb_chars=200)
    summary = factory.Faker('text', max_nb_chars=100)
    insights = factory.Dict({
        'case_summary': factory.Faker('sentence'),
        'classification': {'category': 'test', 'priority_level': 'medium'}
    })


@pytest.fixture
def audio_file_factory():
    """Provide AudioFile factory"""
    return AudioFileFactory


@pytest.fixture
def load_test_fixtures():
    """Load test fixtures from JSON file"""
    from fixtures.test_utils import load_test_data
    return load_test_data()


@pytest.fixture  
def test_audio_files():
    """Provide different sizes of test audio files"""
    from fixtures.test_utils import create_test_audio_file
    return {
        'small': create_test_audio_file("small_audio.wav", "small"),
        'medium': create_test_audio_file("medium_audio.wav", "medium"), 
        'large': create_test_audio_file("large_audio.wav", "large")
    }


@pytest.fixture
def mock_logger():
    """Provide mock logger for testing"""
    from fixtures.test_utils import MockLogger
    return MockLogger()


# Global settings override
from django.test import TestCase as DjangoTestCase

# Global settings override
@override_settings(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    MEDIA_ROOT=tempfile.gettempdir(),
    USE_TZ=True,
    SECRET_KEY='test-secret-key',
)
class TestCase(DjangoTestCase):
    """Base test case with common settings""" 
    pass