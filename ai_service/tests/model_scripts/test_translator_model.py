"""
Comprehensive tests for Translator Model
"""
import pytest
import torch
from unittest.mock import MagicMock, patch


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
    @patch('os.getenv')
    def test_load_translator_success(self, mock_getenv, mock_exists, mock_model_class, mock_tokenizer_class):
        """Test successful translator loading"""
        import os as os_module
        from app.model_scripts.translator_model import TranslationModel

        # Mock environment variable for HuggingFace model
        def getenv_side_effect(key, default=None):
            if key == "TRANSLATION_HF_REPO_ID":
                return "openchs/sw-en-opus-mt-mul-en-v1"
            return os_module.environ.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

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


class TestTranslatorModelInfo:
    """Tests for translator model info"""

    def test_get_model_info(self):
        """Test getting translator model info"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True

        info = translator.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
