import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestTranslatorModelBasic:
    """Basic tests for translator model"""

    def test_translator_initialization(self):
        """Test translator model can be initialized"""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "TRANSLATION_HF_REPO_ID": "Helsinki-NLP/opus-mt-en-es"
            }.get(key, default)

            from app.model_scripts.translator_model import TranslationModel
            model = TranslationModel()

            assert model.loaded is False
            assert model.max_length == 512
            assert model.target_language == "en"  # Default value

    def test_translator_load_success(self):
        """Test successful translator loading"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.getenv") as mock_getenv:

            mock_getenv.side_effect = lambda key, default=None: {
                "TRANSLATION_HF_REPO_ID": "Helsinki-NLP/opus-mt-en-es"
            }.get(key, default)

            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()

            from app.model_scripts.translator_model import TranslationModel
            model = TranslationModel()
            result = model.load()

            assert result is True
            assert model.loaded is True

    def test_translator_load_failure(self):
        """Test translator loading failure"""
        with patch("os.getenv") as mock_getenv:
            # Return None for TRANSLATION_HF_REPO_ID to trigger failure
            # But allow other env vars to pass through with their defaults
            def getenv_side_effect(key, default=None):
                if key == "TRANSLATION_HF_REPO_ID":
                    return None
                return os.environ.get(key, default)

            mock_getenv.side_effect = getenv_side_effect

            from app.model_scripts.translator_model import TranslationModel
            model = TranslationModel()
            # Force hf_repo_id to None to trigger the failure
            model.hf_repo_id = None
            result = model.load()

            assert result is False
            assert not model.loaded

    def test_translator_basic_methods(self):
        """Test basic translator methods"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.getenv") as mock_getenv:

            mock_getenv.side_effect = lambda key, default=None: {
                "TRANSLATION_HF_REPO_ID": "Helsinki-NLP/opus-mt-en-es",
                "TRANSLATION_TARGET_LANGUAGE": "es"
            }.get(key, default)

            mock_tokenizer = MagicMock()
            mock_tokenizer.encode.return_value = [1, 2, 3]
            mock_tokenizer.decode.return_value = "Translated text"
            mock_tok.return_value = mock_tokenizer

            mock_model_instance = MagicMock()
            mock_model_instance.generate.return_value = [[1, 2, 3]]
            mock_model.return_value = mock_model_instance

            from app.model_scripts.translator_model import TranslationModel
            model = TranslationModel()
            model.load()

            # Test translate method (only takes text parameter)
            result = model.translate("Hello")
            assert result == "Translated text"

            # Test get_model_info
            info = model.get_model_info()
            assert isinstance(info, dict)
            assert "model_type" in info

            # Test is model ready (check loaded attribute)
            assert model.loaded is True

    def test_translator_empty_text(self):
        """Test translator with empty text"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.getenv") as mock_getenv:

            mock_getenv.side_effect = lambda key, default=None: {
                "TRANSLATION_HF_REPO_ID": "Helsinki-NLP/opus-mt-en-es"
            }.get(key, default)

            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()

            from app.model_scripts.translator_model import TranslationModel
            model = TranslationModel()
            model.load()

            result = model.translate("")
            assert result == ""

    def test_translator_not_loaded(self):
        """Test translator when not loaded"""
        from app.model_scripts.translator_model import TranslationModel
        model = TranslationModel()

        with pytest.raises(RuntimeError):
            model.translate("Hello")

    def test_translator_model_info(self):
        """Test getting translator model info"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.getenv") as mock_getenv:

            mock_getenv.side_effect = lambda key, default=None: {
                "TRANSLATION_HF_REPO_ID": "Helsinki-NLP/opus-mt-en-es"
            }.get(key, default)

            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()

            from app.model_scripts.translator_model import TranslationModel
            model = TranslationModel()
            model.load()

            info = model.get_model_info()
            assert isinstance(info, dict)
            assert "loaded" in info
            assert info["loaded"] is True