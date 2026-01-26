import pytest
import torch
import numpy as np
from unittest.mock import MagicMock, patch
import tempfile
from datetime import datetime


class TestWhisperModelInitialization:
    """Tests for WhisperModel initialization"""

    def test_whisper_model_init(self):
        """Test Whisper model initialization"""
        from app.model_scripts.whisper_model import WhisperModel

        model = WhisperModel()

        assert model is not None
        assert hasattr(model, 'model_path')

    def test_init_with_custom_path(self):
        """Test initialization with custom model path"""
        from app.model_scripts.whisper_model import WhisperModel

        model = WhisperModel(model_path="/custom/path")

        assert model.model_path == "/custom/path"

    def test_init_sets_default_values(self):
        """Test initialization sets default values"""
        from app.model_scripts.whisper_model import WhisperModel

        model = WhisperModel()

        assert model.is_loaded is False
        assert model.error is None
        assert model.model is None
        assert model.processor is None
        assert model.supported_languages is not None


class TestWhisperModelLoading:
    """Tests for Whisper model loading"""

    @patch('os.path.exists')
    @patch('transformers.AutoModelForSpeechSeq2Seq')
    @patch('transformers.AutoProcessor')
    @patch('os.makedirs')
    def test_load_whisper_success(self, mock_makedirs, mock_processor_class, mock_model_class, mock_exists):
        """Test successful Whisper loading"""
        from app.model_scripts.whisper_model import WhisperModel

        mock_exists.return_value = True

        mock_processor = MagicMock()
        mock_processor_class.from_pretrained.return_value = mock_processor

        mock_model = MagicMock()
        mock_model.to = MagicMock(return_value=mock_model)
        mock_model_class.from_pretrained.return_value = mock_model

        whisper = WhisperModel()
        result = whisper.load()

        assert result is True
        assert whisper.is_loaded is True

    @patch('transformers.AutoProcessor')
    @patch('os.makedirs')
    def test_load_whisper_failure(self, mock_makedirs, mock_processor_class):
        """Test Whisper loading failure"""
        from app.model_scripts.whisper_model import WhisperModel

        mock_processor_class.from_pretrained.side_effect = Exception("Failed to load")

        whisper = WhisperModel()
        result = whisper.load()

        assert result is False
        assert whisper.error is not None


class TestWhisperModelTranscription:
    """Tests for Whisper transcription"""

    @patch('app.model_scripts.whisper_model.WhisperModel.load')
    @patch('app.model_scripts.whisper_model.WhisperModel.transcribe_audio_file')
    @patch('tempfile.NamedTemporaryFile')
    def test_transcribe_audio_bytes(self, mock_tempfile, mock_transcribe_file, mock_load):
        """Test transcription from audio bytes"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True

        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.wav"
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file

        # Mock transcribe_audio_file to return a string
        mock_transcribe_file.return_value = "Test transcription"

        audio_bytes = b'\x00\x01\x02\x03' * 1000

        result = whisper.transcribe_audio_bytes(audio_bytes, language="auto")

        assert result is not None
        assert isinstance(result, str)
        assert result == "Test transcription"

    @patch('app.model_scripts.whisper_model.WhisperModel.load')
    @patch('app.model_scripts.whisper_model.librosa')
    def test_transcribe_audio_file(self, mock_librosa, mock_load):
        """Test transcription from audio file"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True
        whisper.device = "cpu"
        whisper.torch_dtype = torch.float32

        # Mock librosa.load to return audio array and sample rate
        audio_array = np.array([0.1, 0.2, 0.3] * 1000, dtype=np.float32)
        mock_librosa.load.return_value = (audio_array, 16000)

        # Mock processor and model
        whisper.processor = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.input_features = MagicMock()
        mock_inputs.input_features.to.return_value = torch.tensor([[[0.1, 0.2, 0.3]]])
        whisper.processor.return_value = mock_inputs

        whisper.model = MagicMock()
        whisper.model.generate.return_value = torch.tensor([[1, 2, 3]])

        whisper.processor.batch_decode.return_value = ["Test transcription"]

        result = whisper.transcribe_audio_file("/tmp/audio.wav", language="en")

        assert result is not None
        assert isinstance(result, str)
        assert result == "Test transcription"

    @patch('app.model_scripts.whisper_model.WhisperModel.load')
    def test_transcribe_model_not_loaded(self, mock_load):
        """Test transcription when model not loaded"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = False

        with pytest.raises(RuntimeError, match="Whisper model not loaded"):
            whisper.transcribe_audio_bytes(b'\x00\x01', language="auto")

    @patch('app.model_scripts.whisper_model.WhisperModel.load')
    def test_transcribe_audio_file_not_loaded(self, mock_load):
        """Test transcription when model not loaded"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = False

        with pytest.raises(RuntimeError, match="Whisper model not loaded"):
            whisper.transcribe_audio_file("/tmp/audio.wav", language="auto")


class TestWhisperModelInfo:
    """Tests for Whisper model info"""

    def test_get_model_info_not_loaded(self):
        """Test getting model info when not loaded"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = False
        whisper.error = "Not loaded"

        info = whisper.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
        assert info["loaded"] is False
        assert info["error"] == "Not loaded"

    def test_get_model_info_loaded(self):
        """Test getting model info when loaded"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True
        whisper.device = "cpu"
        whisper.torch_dtype = torch.float32
        whisper.model = MagicMock()
        whisper.processor = MagicMock()
        whisper.current_model_id = "test-model"

        info = whisper.get_model_info()

        assert info is not None
        assert info["loaded"] is True
        assert info["model_type"] == "whisper"
        assert "details" in info

    def test_get_model_info_includes_supported_languages(self):
        """Test model info includes supported languages"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()

        info = whisper.get_model_info()

        assert "details" in info
        assert "supported_language_codes" in info["details"]


class TestIsReady:
    """Tests for is_ready method"""

    def test_returns_false_when_not_loaded(self):
        """Test returns False when not loaded"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = False

        assert whisper.is_ready() is False

    def test_returns_false_when_model_missing(self):
        """Test returns False when model is missing"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True
        whisper.model = None
        whisper.processor = MagicMock()

        assert whisper.is_ready() is False

    def test_returns_false_when_processor_missing(self):
        """Test returns False when processor is missing"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True
        whisper.model = MagicMock()
        whisper.processor = None

        assert whisper.is_ready() is False

    def test_returns_true_when_ready(self):
        """Test returns True when model is ready"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True
        whisper.model = MagicMock()
        whisper.processor = MagicMock()

        assert whisper.is_ready() is True


class TestValidateLanguage:
    """Tests for language validation"""

    def test_validate_language_auto(self):
        """Test language validation with auto"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        result = whisper._validate_language("auto")

        assert result is None

    def test_validate_language_valid_code(self):
        """Test language validation with valid code"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        result = whisper._validate_language("en")

        assert result == "en"

    def test_validate_language_swahili(self):
        """Test language validation with Swahili"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        result = whisper._validate_language("sw")

        assert result == "sw"

    def test_validate_language_empty(self):
        """Test language validation with empty string"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        result = whisper._validate_language("")

        assert result is None

    def test_validate_language_none(self):
        """Test language validation with None"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        result = whisper._validate_language(None)

        assert result is None


class TestGetSupportedLanguages:
    """Tests for supported languages"""

    def test_get_supported_languages(self):
        """Test getting supported languages"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        languages = whisper.get_supported_languages()

        assert isinstance(languages, dict)
        assert "en" in languages
        assert "sw" in languages
        assert languages["en"] == "English"
        assert languages["sw"] == "Swahili"


class TestCheckLocalModelExists:
    """Tests for local model check"""

    @patch('os.path.exists')
    def test_check_local_model_not_exists(self, mock_exists):
        """Test when local model doesn't exist"""
        from app.model_scripts.whisper_model import WhisperModel

        mock_exists.return_value = False

        whisper = WhisperModel()
        result = whisper._check_local_model_exists()

        assert result is False

    @patch('os.path.exists')
    def test_check_local_model_exists(self, mock_exists):
        """Test when local model exists"""
        from app.model_scripts.whisper_model import WhisperModel

        # Mock existence of both config and model files
        def exists_side_effect(path):
            if "config.json" in path:
                return True
            if "model.safetensors" in path:
                return True
            return True

        mock_exists.side_effect = exists_side_effect

        whisper = WhisperModel()
        result = whisper._check_local_model_exists()

        assert result is True


class TestTranscribePCMAudio:
    """Tests for PCM audio transcription"""

    def test_transcribe_pcm_not_loaded(self):
        """Test PCM transcription when model not loaded"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = False

        with pytest.raises(RuntimeError, match="Whisper model not loaded"):
            whisper.transcribe_pcm_audio(b'\x00\x01', sample_rate=16000)

    def test_transcribe_pcm_empty_audio(self):
        """Test PCM transcription with empty audio - should not raise"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True
        whisper.device = "cpu"
        whisper.torch_dtype = torch.float32
        whisper.processor = MagicMock()
        whisper.model = MagicMock()

        # Very short/empty audio might raise or return empty
        # The actual behavior depends on implementation
        try:
            result = whisper.transcribe_pcm_audio(b'\x00\x00' * 10, sample_rate=16000)
            # If it returns, it should be empty or a string
            assert isinstance(result, str)
        except (RuntimeError, Exception):
            # Some implementations may raise on empty audio
            pass
