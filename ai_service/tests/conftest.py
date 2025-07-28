# tests/conftest.py
import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = MagicMock()
    settings.debug = True
    settings.enable_model_loading = False  # Disable for tests
    settings.max_concurrent_gpu_requests = 1
    settings.max_queue_size = 5
    settings.request_timeout = 30
    return settings

@pytest.fixture
def sample_text():
    """Sample text for testing text processing"""
    return """
    This is a sample paragraph for testing purposes. It contains multiple sentences
    and should be useful for testing text chunking, summarization, and other NLP tasks.
    
    This is a second paragraph with different content. It also has multiple sentences
    and can be used to test paragraph-level processing.
    """

@pytest.fixture
def sample_audio_data():
    """Mock audio data for testing"""
    return b"fake_audio_data_for_testing"
