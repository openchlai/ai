import pytest
import sys
import os
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestWhisperModelBasic:
    """Basic tests for whisper model"""

    def test_whisper_initialization(self):
        """Test whisper model can be initialized"""
        with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()

            assert model.model_path == "/fake/path"
            assert not model.is_loaded
            # fallback_model_id comes from settings
            assert hasattr(model, 'fallback_model_id')

    def test_whisper_load_success(self):
        """Test successful whisper loading"""
        with patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
             patch("transformers.AutoProcessor.from_pretrained") as mock_proc, \
             patch("transformers.pipeline") as mock_pipeline, \
             patch("os.path.exists", return_value=True), \
             patch("torch.cuda.is_available", return_value=False):
            
            mock_model.return_value = MagicMock()
            mock_proc.return_value = MagicMock()
            mock_pipeline.return_value = MagicMock()
            
            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            result = model.load()
            
            assert result is True
            assert model.is_loaded is True

    def test_whisper_load_failure(self):
        """Test whisper loading failure"""
        with patch("os.path.exists", return_value=False), \
             patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained", side_effect=Exception("Model not found")):
            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            result = model.load()
            
            assert result is False
            assert not model.is_loaded

    def test_whisper_check_local_model_exists(self):
        """Test checking if local model exists"""
        from app.model_scripts.whisper_model import WhisperModel
        model = WhisperModel()
        
        # Test with non-existent path
        with patch("os.path.exists", return_value=False):
            assert model._check_local_model_exists() is False
        
        # Test with existing path but no config
        with patch("os.path.exists", side_effect=lambda path: "/config.json" not in path):
            assert model._check_local_model_exists() is False
        
        # Test with config but no model files
        def mock_exists(path):
            if "config.json" in path:
                return True
            return False
            
        with patch("os.path.exists", side_effect=mock_exists):
            assert model._check_local_model_exists() is False

    def test_whisper_validate_language(self):
        """Test language validation"""
        with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            
            # Test valid language
            result = model._validate_language("en")
            assert result == "en"
            
            # Test auto language
            result = model._validate_language("auto")
            assert result is None  # Whisper uses None for auto-detect
            
            # Test invalid language (should return the input for Whisper to handle)
            result = model._validate_language("invalid")
            assert result == "invalid"

    def test_whisper_basic_methods(self):
        """Test basic whisper methods"""
        with patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
             patch("transformers.AutoProcessor.from_pretrained") as mock_proc, \
             patch("transformers.pipeline") as mock_pipeline, \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"), \
             patch("torch.cuda.is_available", return_value=False):

            mock_pipeline.return_value = MagicMock()

            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            model.load()

            # Mock the components needed for transcription
            model.processor = MagicMock()
            model.model = MagicMock()

            # Test transcribe_audio_file
            with patch("librosa.load", return_value=(np.array([0.1, 0.2, 0.3]), 16000)):
                model.processor.return_value = MagicMock(input_features=MagicMock(to=lambda **kwargs: MagicMock()))
                model.model.generate.return_value = [[1, 2, 3]]
                model.processor.batch_decode.return_value = ["Transcribed text"]

                result = model.transcribe_audio_file("/fake/audio.wav")
                assert result == "Transcribed text"

            # Test get_supported_languages
            languages = model.get_supported_languages()
            assert isinstance(languages, dict)
            assert "en" in languages
            assert "auto" in languages

            # Test is_ready
            assert model.is_ready() is True

            # Test get_model_info
            info = model.get_model_info()
            assert isinstance(info, dict)
            assert info["loaded"] is True

    def test_whisper_transcribe_audio_bytes(self):
        """Test transcribing audio from bytes"""
        with patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
             patch("transformers.AutoProcessor.from_pretrained") as mock_proc, \
             patch("transformers.pipeline") as mock_pipeline, \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"), \
             patch("torch.cuda.is_available", return_value=False), \
             patch("tempfile.NamedTemporaryFile") as mock_temp, \
             patch("librosa.load") as mock_load:

            # Setup mocks
            mock_pipeline.return_value = MagicMock()

            mock_temp_file = MagicMock()
            mock_temp_file.name = "/tmp/test.wav"
            mock_temp.__enter__.return_value = mock_temp_file

            mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 16000)

            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            model.load()

            # Mock the components needed for transcription
            model.processor = MagicMock()
            model.processor.return_value = MagicMock(input_features=MagicMock(to=lambda **kwargs: MagicMock()))
            model.model = MagicMock()
            model.model.generate.return_value = [[1, 2, 3]]
            model.processor.batch_decode.return_value = ["Audio from bytes"]

            # Test transcribe_audio_bytes
            audio_bytes = b'\x00' * 1000
            result = model.transcribe_audio_bytes(audio_bytes)
            assert result == "Audio from bytes"

    def test_whisper_transcribe_pcm_audio(self):
        """Test transcribing PCM audio"""
        with patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
             patch("transformers.AutoProcessor.from_pretrained") as mock_proc, \
             patch("transformers.pipeline") as mock_pipeline, \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"), \
             patch("torch.cuda.is_available", return_value=False), \
             patch("tempfile.NamedTemporaryFile") as mock_temp, \
             patch("librosa.load") as mock_load, \
             patch("numpy.frombuffer") as mock_frombuffer:

            # Setup mocks
            mock_pipeline.return_value = MagicMock()

            mock_temp_file = MagicMock()
            mock_temp_file.name = "/tmp/test.wav"
            mock_temp.__enter__.return_value = mock_temp_file

            mock_frombuffer.return_value = np.array([0.1, 0.2, 0.3])  # Mock audio data
            mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 16000)

            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            model.load()

            # Mock the components needed for transcription
            model.processor = MagicMock()
            model.processor.return_value = MagicMock(input_features=MagicMock(to=lambda **kwargs: MagicMock()))
            model.model = MagicMock()
            model.model.generate.return_value = [[1, 2, 3]]
            model.processor.batch_decode.return_value = ["PCM audio content"]

            # Test transcribe_pcm_audio
            pcm_bytes = b'\x00' * 1000
            result = model.transcribe_pcm_audio(pcm_bytes, sample_rate=16000)
            assert result == "PCM audio content"

    def test_whisper_not_loaded_error(self):
        """Test whisper methods when not loaded"""
        from app.model_scripts.whisper_model import WhisperModel
        model = WhisperModel()
        
        with pytest.raises(RuntimeError):
            model.transcribe_audio_file("/fake/audio.wav")
        
        with pytest.raises(RuntimeError):
            model.transcribe_audio_bytes(b"fake audio")
        
        with pytest.raises(RuntimeError):
            model.transcribe_pcm_audio(b"fake audio")

    def test_whisper_empty_file_handling(self):
        """Test handling of empty or invalid files"""
        with patch("transformers.AutoModelForSpeechSeq2Seq.from_pretrained") as mock_model, \
             patch("transformers.AutoProcessor.from_pretrained") as mock_proc, \
             patch("transformers.pipeline") as mock_pipeline, \
             patch("os.path.exists", return_value=True), \
             patch("torch.cuda.is_available", return_value=False):
            
            mock_pipeline.return_value = MagicMock()
            
            from app.model_scripts.whisper_model import WhisperModel
            model = WhisperModel()
            model.load()
            
            # Test with empty file path
            with patch("librosa.load", side_effect=Exception("Empty file")):
                with pytest.raises(RuntimeError):
                    model.transcribe_audio_file("")
            
            # Test with non-existent file
            with patch("os.path.exists", return_value=False), \
                 patch("librosa.load", side_effect=Exception("File not found")):
                with pytest.raises(RuntimeError):
                    model.transcribe_audio_file("/nonexistent.wav")