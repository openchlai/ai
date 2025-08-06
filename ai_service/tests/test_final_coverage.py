import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_app_init():
    """Test app module can be imported"""
    import app
    assert app is not None

def test_streaming_init():
    """Test streaming module init"""
    from app.streaming import __init__ as streaming_init
    assert streaming_init is not None

def test_audio_buffer_basic():
    """Test audio buffer basic functionality"""
    from app.streaming.audio_buffer import AsteriskAudioBuffer
    
    buffer = AsteriskAudioBuffer()
    assert buffer is not None
    
    # Test adding data
    buffer.add_chunk(b"test_audio_data", 1234567890)
    assert len(buffer.chunks) > 0
    
    # Test getting duration
    duration = buffer.get_total_duration()
    assert duration >= 0

def test_config_settings_methods():
    """Test additional settings methods"""
    from app.config.settings import Settings, settings
    
    # Test Settings class instantiation
    settings_obj = Settings()
    assert settings_obj is not None
    
    # Test default model path functionality
    path = settings_obj.get_model_path("test_model")
    assert isinstance(path, str)
    
    # Test settings singleton
    assert settings is not None
    path2 = settings.get_model_path("another_model")
    assert isinstance(path2, str)

def test_text_chunker_basic_methods():
    """Test text chunker basic methods"""
    from app.core.text_chunker import IntelligentTextChunker, ChunkConfig
    
    # Test chunker initialization
    chunker = IntelligentTextChunker()
    assert chunker is not None
    assert len(chunker.chunk_configs) > 0
    
    # Test basic config
    config = ChunkConfig(max_tokens=100, overlap_tokens=10, min_chunk_tokens=5)
    assert config.max_tokens == 100
    assert config.overlap_tokens == 10

def test_model_loader_basic():
    """Test model loader basic functionality"""
    from app.models.model_loader import ModelLoader, AVAILABLE_LIBRARIES
    
    # Test ModelLoader initialization
    loader = ModelLoader()
    assert loader is not None
    assert hasattr(loader, 'models')
    assert isinstance(loader.models, dict)
    
    # Test available libraries
    assert isinstance(AVAILABLE_LIBRARIES, dict)

def test_tcp_server_methods():
    """Test TCP server additional methods"""
    from app.streaming.tcp_server import AsteriskTCPServer
    
    server = AsteriskTCPServer()
    assert server is not None
    
    # Test get_status method 
    status = server.get_status()
    assert isinstance(status, dict)
    assert 'server_running' in status
    assert 'active_connections' in status
    assert 'active_calls' in status
    
    # Test basic properties
    assert hasattr(server, 'active_connections')
    assert isinstance(server.active_connections, dict)

def test_whisper_model_methods():
    """Test whisper model additional methods"""
    with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
        from app.models.whisper_model import WhisperModel
        
        model = WhisperModel()
        
        # Test get_supported_languages
        languages = model.get_supported_languages()
        assert isinstance(languages, dict)
        assert "en" in languages
        assert "auto" in languages
        
        # Test is_ready when not loaded
        assert model.is_ready() is False
        
        # Test model info when not loaded
        info = model.get_model_info()
        assert isinstance(info, dict)
        assert "loaded" in info
        assert info["loaded"] is False