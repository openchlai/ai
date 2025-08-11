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
        with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
            from app.models.translator_model import TranslationModel
            model = TranslationModel()
            
            assert model.model_path == "/fake/path"
            assert not model.loaded
            assert model.max_length == 512

    def test_translator_load_success(self):
        """Test successful translator loading"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()
            
            from app.models.translator_model import TranslationModel
            model = TranslationModel()
            result = model.load()
            
            assert result is True
            assert model.loaded is True

    def test_translator_load_failure(self):
        """Test translator loading failure"""
        with patch("os.path.exists", return_value=False):
            from app.models.translator_model import TranslationModel
            model = TranslationModel()
            result = model.load()
            
            assert result is False
            assert not model.loaded

    def test_translator_basic_methods(self):
        """Test basic translator methods"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tokenizer = MagicMock()
            mock_tokenizer.encode.return_value = [1, 2, 3]
            mock_tokenizer.decode.return_value = "Translated text"
            mock_tok.return_value = mock_tokenizer
            
            mock_model_instance = MagicMock()
            mock_model_instance.generate.return_value = [[1, 2, 3]]
            mock_model.return_value = mock_model_instance
            
            from app.models.translator_model import TranslationModel
            model = TranslationModel()
            model.load()
            
            # Test translate method
            result = model.translate("Hello", target_language="es")
            assert result == "Translated text"
            
            # Test get_supported_languages
            languages = model.get_supported_languages()
            assert isinstance(languages, dict)
            
            # Test is_ready
            assert model.is_ready() is True

    def test_translator_empty_text(self):
        """Test translator with empty text"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()
            
            from app.models.translator_model import TranslationModel
            model = TranslationModel()
            model.load()
            
            result = model.translate("", target_language="es")
            assert result == ""

    def test_translator_not_loaded(self):
        """Test translator when not loaded"""
        from app.models.translator_model import TranslationModel
        model = TranslationModel()
        
        with pytest.raises(RuntimeError):
            model.translate("Hello", target_language="es")

    def test_translator_model_info(self):
        """Test getting translator model info"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()
            
            from app.models.translator_model import TranslationModel
            model = TranslationModel()
            model.load()
            
            info = model.get_model_info()
            assert isinstance(info, dict)
            assert "loaded" in info