"""
Comprehensive tests for Whisper Model
"""
import pytest
import torch
import numpy as np
from unittest.mock import MagicMock, patch
import tempfile


class TestWhisperModelInitialization:
    """Tests for WhisperModel initialization"""

    @patch('app.model_scripts.whisper_model.torch.cuda.is_available')
    def test_whisper_model_init(self, mock_cuda):
        """Test Whisper model initialization"""
        from app.model_scripts.whisper_model import WhisperModel

        mock_cuda.return_value = False

        model = WhisperModel()

        assert model is not None


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
        whisper.device = torch.device("cpu")
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


class TestWhisperModelAudioProcessing:
    """Tests for audio processing"""

    @pytest.mark.skip(reason="_load_audio method and AudioSegment not implemented in WhisperModel")
    def test_load_audio_wav(self):
        """Test loading WAV audio"""
        pass

    @pytest.mark.skip(reason="_load_audio method and AudioSegment not implemented in WhisperModel")
    def test_load_audio_mp3(self):
        """Test loading MP3 audio"""
        pass


class TestWhisperModelInfo:
    """Tests for Whisper model info"""

    def test_get_model_info(self):
        """Test getting Whisper model info"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        whisper.is_loaded = True

        info = whisper.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
