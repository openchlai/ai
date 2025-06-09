import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from core.pipeline.transcription import (
    WhisperTranscriber, 
    transcribe, 
    detect_hallucination,
    load_whisper_model,
    get_transcriber
)


class TestDetectHallucination:
    """Test hallucination detection functionality"""

    def test_detect_no_hallucination(self):
        """Test text without hallucinations"""
        text = "This is a normal transcription with varied content. Each sentence is different. No repetition here."
        result = detect_hallucination(text)
        assert result is False

    def test_detect_hallucination_excessive_repetition(self):
        """Test detection of excessive repetition"""
        text = "Thank you for calling. Thank you for calling. Thank you for calling. Thank you for calling."
        result = detect_hallucination(text)
        assert result is True

    def test_detect_hallucination_short_text(self):
        """Test that short texts don't trigger hallucination detection"""
        text = "Short text"
        result = detect_hallucination(text)
        assert result is False

    def test_detect_hallucination_empty_text(self):
        """Test empty text handling"""
        text = ""
        result = detect_hallucination(text)
        assert result is False

    def test_detect_hallucination_whitespace_text(self):
        """Test whitespace-only text handling"""
        text = "   \n\t   "
        result = detect_hallucination(text)
        assert result is False

    def test_detect_hallucination_custom_threshold(self):
        """Test custom repetition threshold"""
        text = "Hello world. Hello world. Hello world."
        
        # With default threshold (0.4) - should detect
        result_default = detect_hallucination(text)
        assert result_default is True
        
        # With higher threshold (0.8) - should not detect
        result_high = detect_hallucination(text, max_repetition_ratio=0.8)
        assert result_high is False


class TestLoadWhisperModel:
    """Test Whisper model loading functionality"""

    @patch('core.pipeline.transcription.whisper.load_model')
    @patch('torch.cuda.is_available')
    def test_load_whisper_model_gpu(self, mock_cuda, mock_load_model):
        """Test loading Whisper model with GPU"""
        mock_cuda.return_value = True
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        result = load_whisper_model("base")
        
        mock_load_model.assert_called_once_with("base", device="cuda")
        assert result == mock_model

    @patch('core.pipeline.transcription.whisper.load_model')
    @patch('torch.cuda.is_available')
    def test_load_whisper_model_cpu(self, mock_cuda, mock_load_model):
        """Test loading Whisper model with CPU"""
        mock_cuda.return_value = False
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        result = load_whisper_model("tiny")
        
        mock_load_model.assert_called_once_with("tiny", device="cpu")
        assert result == mock_model

    @patch('core.pipeline.transcription.whisper.load_model')
    @patch('torch.cuda.is_available')
    @patch('os.path.exists')
    def test_load_whisper_model_custom_path(self, mock_exists, mock_cuda, mock_load_model):
        """Test loading Whisper model from custom path"""
        mock_exists.return_value = True
        mock_cuda.return_value = False
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        custom_path = "/path/to/custom/model"
        result = load_whisper_model(custom_path)
        
        mock_load_model.assert_called_once_with(custom_path, device="cpu")
        assert result == mock_model

    @patch('core.pipeline.transcription.whisper.load_model')
    @patch('torch.cuda.is_available')
    def test_load_whisper_model_failure(self, mock_cuda, mock_load_model):
        """Test handling of model loading failure"""
        mock_cuda.return_value = False
        mock_load_model.side_effect = Exception("Model loading failed")
        
        with pytest.raises(RuntimeError, match="Could not load Whisper model"):
            load_whisper_model("base")


class TestWhisperTranscriber:
    """Test WhisperTranscriber class"""

    @patch('core.pipeline.transcription.load_whisper_model')
    def test_whisper_transcriber_init(self, mock_load_model):
        """Test WhisperTranscriber initialization"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        transcriber = WhisperTranscriber("base")
        
        assert transcriber.model_size == "base"
        assert transcriber.model == mock_model
        mock_load_model.assert_called_once_with("base")

    @patch('core.pipeline.transcription.load_whisper_model')
    def test_validate_audio_path_success(self, mock_load_model, sample_audio_path):
        """Test successful audio path validation"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        transcriber = WhisperTranscriber("tiny")
        validated_path = transcriber._validate_audio_path(sample_audio_path)
        
        assert isinstance(validated_path, Path)
        assert validated_path.exists()

    @patch('core.pipeline.transcription.load_whisper_model')
    def test_validate_audio_path_not_found(self, mock_load_model):
        """Test audio path validation with non-existent file"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        transcriber = WhisperTranscriber("tiny")
        
        with pytest.raises(FileNotFoundError):
            transcriber._validate_audio_path("/non/existent/file.wav")

    @patch('core.pipeline.transcription.load_whisper_model')
    def test_get_anti_hallucination_params(self, mock_load_model):
        """Test anti-hallucination parameter generation"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        transcriber = WhisperTranscriber("tiny")
        
        # Test different attempts
        params_0 = transcriber._get_anti_hallucination_params(0)
        params_1 = transcriber._get_anti_hallucination_params(1)
        params_2 = transcriber._get_anti_hallucination_params(2)
        
        # Check that parameters change between attempts
        assert params_0['temperature'] == 0.0
        assert params_1['temperature'] == [0.0, 0.2]
        assert params_2['temperature'] == [0.0, 0.2, 0.4, 0.6, 0.8]

    @patch('core.pipeline.transcription.load_whisper_model')
    @patch('core.pipeline.transcription.detect_hallucination')
    def test_transcribe_success(self, mock_detect_hallucination, mock_load_model, sample_audio_path):
        """Test successful transcription"""
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "This is a successful transcription",
            "language": "en"
        }
        mock_load_model.return_value = mock_model
        mock_detect_hallucination.return_value = False
        
        transcriber = WhisperTranscriber("tiny")
        result = transcriber.transcribe(sample_audio_path)
        
        assert result == "This is a successful transcription"
        mock_model.transcribe.assert_called_once()

    @patch('core.pipeline.transcription.load_whisper_model')
    def test_transcribe_file_not_found(self, mock_load_model):
        """Test transcription with non-existent file"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        transcriber = WhisperTranscriber("tiny")
        
        with pytest.raises(FileNotFoundError):
            transcriber.transcribe("/non/existent/file.wav")

    @patch('core.pipeline.transcription.load_whisper_model')
    @patch('core.pipeline.transcription.detect_hallucination')
    def test_transcribe_with_hallucination_retry(self, mock_detect_hallucination, mock_load_model, sample_audio_path):
        """Test transcription with hallucination detection and retry"""
        mock_model = Mock()
        
        # First attempt has hallucination, second is clean
        transcription_results = [
            {"text": "Thank you. Thank you. Thank you.", "language": "en"},
            {"text": "This is a clean transcription", "language": "en"}
        ]
        mock_model.transcribe.side_effect = transcription_results
        mock_load_model.return_value = mock_model
        
        # First call detects hallucination, second doesn't
        mock_detect_hallucination.side_effect = [True, False]
        
        transcriber = WhisperTranscriber("tiny")
        result = transcriber.transcribe(sample_audio_path)
        
        assert result == "This is a clean transcription"
        assert mock_model.transcribe.call_count == 2

    def test_get_model_info(self):
        """Test model info retrieval"""
        with patch('core.pipeline.transcription.load_whisper_model') as mock_load_model:
            mock_model = Mock()
            mock_load_model.return_value = mock_model
            
            transcriber = WhisperTranscriber("base")
            info = transcriber.get_model_info()
            
            assert info['model_size'] == "base"
            assert info['model_loaded'] is True


class TestGlobalFunctions:
    """Test global transcription functions"""

    @patch('core.pipeline.transcription.WhisperTranscriber')
    def test_transcribe_global_function(self, mock_transcriber_class, sample_audio_path):
        """Test global transcribe function"""
        mock_transcriber = Mock()
        mock_transcriber.transcribe.return_value = "Global transcription result"
        mock_transcriber_class.return_value = mock_transcriber
        
        result = transcribe(sample_audio_path, model_size="tiny")
        
        assert result == "Global transcription result"
        mock_transcriber_class.assert_called_once_with(model_size="tiny")
        mock_transcriber.transcribe.assert_called_once_with(sample_audio_path)

    @patch('core.pipeline.transcription.WhisperTranscriber')
    def test_get_transcriber_singleton(self, mock_transcriber_class):
        """Test get_transcriber singleton behavior"""
        mock_transcriber1 = Mock()
        mock_transcriber1.model_size = "base"
        mock_transcriber_class.return_value = mock_transcriber1
        
        # First call should create new transcriber
        transcriber1 = get_transcriber("base")
        
        # Second call with same model should return cached instance
        transcriber2 = get_transcriber("base")
        
        assert transcriber1 == transcriber2
        mock_transcriber_class.assert_called_once_with("base")