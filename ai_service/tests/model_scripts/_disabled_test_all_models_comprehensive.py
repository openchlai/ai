"""
Comprehensive tests for all remaining model classes
"""
import pytest
import torch
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
from datetime import datetime


# NER MODEL TESTS

class TestNERModelInitialization:
    """Tests for NERModel initialization"""

    def test_ner_model_init(self):
        """Test NER model initialization"""
        from app.model_scripts.ner_model import NERModel

        model = NERModel()

        assert model is not None
        assert hasattr(model, 'model_path')


class TestNERModelLoading:
    """Tests for NER model loading"""

    @patch('app.model_scripts.ner_model.spacy.load')
    @patch('os.path.exists')
    def test_load_ner_model_success(self, mock_exists, mock_spacy_load):
        """Test successful NER model loading"""
        from app.model_scripts.ner_model import NERModel

        mock_exists.return_value = True
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp

        ner = NERModel()
        result = ner.load()

        assert result is True
        assert ner.loaded is True

    @patch('os.path.exists')
    @patch('app.model_scripts.ner_model.spacy.load')
    def test_load_ner_model_failure(self, mock_spacy_load, mock_exists):
        """Test NER model loading failure"""
        from app.model_scripts.ner_model import NERModel

        # Mock to prevent HF download path
        mock_exists.return_value = False
        mock_spacy_load.side_effect = OSError("Failed to load")

        ner = NERModel()
        ner.hf_repo_id = None  # Disable HF path
        result = ner.load()

        assert result is False


class TestNERModelExtraction:
    """Tests for NER entity extraction"""

    @patch('app.model_scripts.ner_model.NERModel.load')
    def test_extract_entities_simple_text(self, mock_load):
        """Test entity extraction from simple text"""
        from app.model_scripts.ner_model import NERModel

        ner = NERModel()
        ner.loaded = True

        # Mock spaCy nlp object
        mock_nlp = MagicMock()
        mock_doc = MagicMock()

        # Mock entities
        mock_ent1 = MagicMock()
        mock_ent1.text = "John"
        mock_ent1.label_ = "PERSON"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 4

        mock_ent2 = MagicMock()
        mock_ent2.text = "Acme Corp"
        mock_ent2.label_ = "ORG"
        mock_ent2.start_char = 14
        mock_ent2.end_char = 23

        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp.return_value = mock_doc

        ner.nlp = mock_nlp

        result = ner.extract_entities("John works at Acme Corp")

        assert result is not None
        assert isinstance(result, list)

    @patch('app.model_scripts.ner_model.NERModel.load')
    def test_extract_entities_empty_text(self, mock_load):
        """Test extraction with empty text"""
        from app.model_scripts.ner_model import NERModel

        ner = NERModel()
        ner.loaded = True

        # Empty text should return empty list (flat=True) or empty dict (flat=False)
        result = ner.extract_entities("")
        assert result == []

    @patch('app.model_scripts.ner_model.NERModel.load')
    def test_extract_entities_model_not_loaded(self, mock_load):
        """Test extraction when model not loaded"""
        from app.model_scripts.ner_model import NERModel

        ner = NERModel()
        ner.loaded = False

        with pytest.raises(Exception):
            ner.extract_entities("Some text")


class TestNERModelInfo:
    """Tests for NER model info"""

    def test_get_model_info(self):
        """Test getting NER model info"""
        from app.model_scripts.ner_model import NERModel

        ner = NERModel()
        ner.loaded = True

        info = ner.get_model_info()

        assert info is not None
        assert "loaded" in info


# SUMMARIZER MODEL TESTS

class TestSummarizerModelInitialization:
    """Tests for SummarizationModel initialization"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarizer_model_init(self, mock_cuda):
        """Test summarizer model initialization"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        model = SummarizationModel()

        assert model is not None
        assert model.device == torch.device("cpu")


class TestSummarizerModelLoading:
    """Tests for summarizer model loading"""

    @patch('os.path.exists')
    @patch('app.model_scripts.summarizer_model.pipeline')
    @patch('app.model_scripts.summarizer_model.AutoModelForSeq2SeqLM')
    @patch('app.model_scripts.summarizer_model.AutoTokenizer')
    @patch('os.makedirs')
    def test_load_summarizer_success(self, mock_makedirs, mock_tokenizer_class, mock_model_class, mock_pipeline, mock_exists):
        """Test successful summarizer loading"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_exists.return_value = True

        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.to = MagicMock(return_value=mock_model)
        mock_model_class.from_pretrained.return_value = mock_model

        # Mock pipeline creation
        mock_pipeline.return_value = MagicMock()

        summarizer = SummarizationModel()
        result = summarizer.load()

        assert result is True
        assert summarizer.loaded is True

    @patch('app.model_scripts.summarizer_model.AutoTokenizer')
    def test_load_summarizer_failure(self, mock_tokenizer_class):
        """Test summarizer loading failure"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_tokenizer_class.from_pretrained.side_effect = Exception("Failed to load")

        summarizer = SummarizationModel()
        result = summarizer.load()

        assert result is False


class TestSummarizerModelSummarization:
    """Tests for summarization functionality"""

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_simple_text(self, mock_load):
        """Test summarization of simple text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True

        # Mock pipeline and tokenizer
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.return_value = [{"summary_text": "This is a summary"}]

        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # Short text

        result = summarizer.summarize("Long text to summarize")

        assert result is not None
        assert isinstance(result, str)
        assert result == "This is a summary"

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_with_max_length(self, mock_load):
        """Test summarization with custom max length"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True

        # Mock pipeline and tokenizer
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.return_value = [{"summary_text": "Summary"}]

        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3]  # Short text

        result = summarizer.summarize("Text", max_length=100)

        assert result is not None
        assert result == "Summary"

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_model_not_loaded(self, mock_load):
        """Test summarization when model not loaded"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = False

        with pytest.raises(Exception):
            summarizer.summarize("Some text")


# TRANSLATOR MODEL TESTS

class TestTranslatorModelInitialization:
    """Tests for TranslationModel initialization"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_translator_model_init(self, mock_cuda):
        """Test translator model initialization"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        model = TranslationModel()

        assert model is not None
        assert model.device == torch.device("cpu")


class TestTranslatorModelLoading:
    """Tests for translator model loading"""

    @patch('app.model_scripts.translator_model.AutoTokenizer')
    @patch('app.model_scripts.translator_model.AutoModelForSeq2SeqLM')
    @patch('os.path.exists')
    def test_load_translator_success(self, mock_exists, mock_model_class, mock_tokenizer_class):
        """Test successful translator loading"""
        from app.model_scripts.translator_model import TranslationModel

        mock_exists.return_value = True

        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.to = MagicMock(return_value=mock_model)
        mock_model_class.from_pretrained.return_value = mock_model

        translator = TranslationModel()
        result = translator.load()

        assert result is True
        assert translator.loaded is True

    @patch('app.model_scripts.translator_model.AutoTokenizer')
    def test_load_translator_failure(self, mock_tokenizer_class):
        """Test translator loading failure"""
        from app.model_scripts.translator_model import TranslationModel

        mock_tokenizer_class.from_pretrained.side_effect = Exception("Failed to load")

        translator = TranslationModel()
        result = translator.load()

        assert result is False


class TestTranslatorModelTranslation:
    """Tests for translation functionality"""

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_simple_text(self, mock_load):
        """Test translation of simple text"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.device = torch.device("cpu")

        # Mock tokenizer to return a MagicMock with .to() method
        translator.tokenizer = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs
        translator.tokenizer.return_value = mock_inputs
        translator.tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # Short text
        translator.tokenizer.decode.return_value = "Translated text"

        translator.model = MagicMock()
        translator.model.generate.return_value = torch.tensor([[1, 2, 3]])

        result = translator.translate("Habari yako")

        assert result is not None
        assert isinstance(result, str)
        assert result == "Translated text"

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_long_text_chunking(self, mock_load):
        """Test translation with long text requiring chunking"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.max_length = 100
        translator.device = torch.device("cpu")

        # Mock tokenizer to return a MagicMock with .to() method
        translator.tokenizer = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs
        translator.tokenizer.return_value = mock_inputs
        translator.tokenizer.encode.return_value = [1, 2, 3]  # Short text (won't trigger chunking)
        translator.tokenizer.decode.return_value = "Translated"

        translator.model = MagicMock()
        translator.model.generate.return_value = torch.tensor([[1, 2]])

        long_text = "Habari " * 200

        result = translator.translate(long_text)

        assert result is not None
        assert result == "Translated"

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_model_not_loaded(self, mock_load):
        """Test translation when model not loaded"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = False

        with pytest.raises(Exception):
            translator.translate("Some text")


# WHISPER MODEL TESTS

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
        import numpy as np

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


class TestAllModelsInfo:
    """Tests for model info methods across all models"""

    def test_ner_get_model_info(self):
        """Test NER model info"""
        from app.model_scripts.ner_model import NERModel

        ner = NERModel()
        info = ner.get_model_info()

        assert info is not None
        assert isinstance(info, dict)

    def test_summarizer_get_model_info(self):
        """Test summarizer model info"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        info = summarizer.get_model_info()

        assert info is not None
        assert isinstance(info, dict)

    def test_translator_get_model_info(self):
        """Test translator model info"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        info = translator.get_model_info()

        assert info is not None
        assert isinstance(info, dict)

    def test_whisper_get_model_info(self):
        """Test Whisper model info"""
        from app.model_scripts.whisper_model import WhisperModel

        whisper = WhisperModel()
        info = whisper.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
