# tests/test_whisper_model.py
import pytest
import sys
import os
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_whisper_model():
    """Create a mocked Whisper model for testing"""
    with patch("transformers.pipeline") as mock_pipeline, \
         patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
         patch("transformers.AutoProcessor.from_pretrained") as mock_processor, \
         patch("os.path.exists", return_value=True):
        
        # Mock pipeline return value
        mock_pipe = MagicMock()
        mock_pipe.return_value = {"text": "Mocked transcription result"}
        mock_pipeline.return_value = mock_pipe
        
        from app.models.whisper_model import WhisperModel
        model = WhisperModel()
        model.pipe = mock_pipe
        model.is_loaded = True
        model.load_time = datetime.now()
        model.device = "cpu"
        return model

def test_whisper_model_initialization():
    """Test WhisperModel initialization"""
    with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
        from app.models.whisper_model import WhisperModel
        model = WhisperModel()
        assert model.model_path == "/fake/path"
        assert model.fallback_model_id == "openai/whisper-large-v3-turbo"
        assert not model.is_loaded
        assert model.device is None

def test_whisper_model_load_success():
    """Test successful model loading"""
    with patch("transformers.pipeline") as mock_pipeline, \
         patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
         patch("transformers.AutoProcessor.from_pretrained") as mock_processor, \
         patch("os.path.exists", return_value=True), \
         patch("torch.cuda.is_available", return_value=True):
        
        mock_pipe = MagicMock()
        mock_pipeline.return_value = mock_pipe
        
        from app.models.whisper_model import WhisperModel
        model = WhisperModel()
        result = model.load()
        
        assert result is True
        assert model.is_loaded is True
        assert model.pipe is not None

def test_transcribe_audio_file(mock_whisper_model):
    """Test transcribing an audio file"""
    mock_whisper_model.pipe.return_value = {"text": "Hello world"}
    
    result = mock_whisper_model.transcribe_audio_file("/fake/audio.wav")
    
    assert result == "Hello world"  # The method returns string, not dict
    mock_whisper_model.pipe.assert_called_once()

def test_transcribe_empty_file_path(mock_whisper_model):
    """Test transcribing with empty file path"""
    result = mock_whisper_model.transcribe_audio_file("")
    assert result is None or result == ""

def test_transcribe_model_not_loaded():
    """Test transcribing when model is not loaded"""
    from app.models.whisper_model import WhisperModel
    model = WhisperModel()
    
    with pytest.raises(RuntimeError, match="not loaded"):
        model.transcribe_audio_file("/fake/audio.wav")

def test_transcribe_audio_bytes(mock_whisper_model):
    """Test transcribing audio from bytes"""
    audio_bytes = b'\x00' * 1000  # Fake audio data
    
    with patch("tempfile.NamedTemporaryFile") as mock_temp, \
         patch("soundfile.write") as mock_write:
        
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/test.wav"
        mock_temp.__enter__.return_value = mock_temp_file
        
        mock_whisper_model.pipe.return_value = {"text": "From bytes"}
        
        result = mock_whisper_model.transcribe_audio_bytes(
            audio_bytes, sample_rate=16000
        )
        
        assert result["text"] == "From bytes"

def test_get_supported_languages(mock_whisper_model):
    """Test getting supported languages"""
    languages = mock_whisper_model.get_supported_languages()
    
    assert isinstance(languages, dict)
    assert "en" in languages
    assert "sw" in languages
    assert languages["en"] == "English"

def test_is_ready(mock_whisper_model):
    """Test model readiness check"""
    assert mock_whisper_model.is_ready() is True
    
    mock_whisper_model.is_loaded = False
    assert mock_whisper_model.is_ready() is False

def test_get_model_info(mock_whisper_model):
    """Test getting model information"""
    info = mock_whisper_model.get_model_info()
    
    assert isinstance(info, dict)
    assert "loaded" in info
    assert "model_path" in info
    assert "device" in info
    assert info["loaded"] is True

def test_estimate_transcription_time(mock_whisper_model):
    """Test transcription time estimation"""
    # Mock audio duration of 10 seconds
    time_estimate = mock_whisper_model.estimate_transcription_time(10.0)
    
    assert isinstance(time_estimate, float)
    assert time_estimate > 0

def test_transcribe_with_language_specification(mock_whisper_model):
    """Test transcribing with specific language"""
    mock_whisper_model.pipe.return_value = {"text": "Bonjour le monde"}
    
    result = mock_whisper_model.transcribe_audio(
        "/fake/audio.wav", 
        language="fr"
    )
    
    assert result["text"] == "Bonjour le monde"

def test_transcribe_with_invalid_language(mock_whisper_model):
    """Test transcribing with invalid language code"""
    result = mock_whisper_model.transcribe_audio(
        "/fake/audio.wav",
        language="invalid_lang"
    )
    
    # Should fallback to auto-detect
    assert result is not None

def test_model_load_failure():
    """Test model loading failure"""
    with patch("transformers.pipeline", side_effect=Exception("Load failed")), \
         patch("os.path.exists", return_value=True):
        
        from app.models.whisper_model import WhisperModel
        model = WhisperModel()
        result = model.load()
        
        assert result is False
        assert model.is_loaded is False
        assert model.error is not None