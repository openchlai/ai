# tests/test_translator_model.py
import pytest
import sys
import os
import torch
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_translator_model():
    """Create a mocked translator model for testing"""
    with patch("app.model_scripts.translator_model.AutoTokenizer.from_pretrained") as mock_tokenizer, \
         patch("app.model_scripts.translator_model.AutoModelForSeq2SeqLM.from_pretrained") as mock_model_cls, \
         patch("os.path.exists", return_value=True):
        
        # Mock tokenizer
        mock_tok = MagicMock()
        mock_tok.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_tok.decode.return_value = "Mocked translation"
        mock_tokenizer.return_value = mock_tok
        
        # Mock model
        mock_model = MagicMock()
        mock_model.generate.return_value = torch.tensor([[1, 2, 3, 4, 5]])
        mock_model_cls.return_value = mock_model
        
        from app.model_scripts.translator_model import TranslationModel
        model = TranslationModel()
        model.tokenizer = mock_tok
        model.model = mock_model
        model.loaded = True
        model.load_time = datetime.now()
        model.device = torch.device("cpu")
        return model

def test_translator_model_initialization():
    """Test TranslationModel initialization"""
    with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
        from app.model_scripts.translator_model import TranslationModel
        model = TranslationModel()
        assert model.model_path == "/fake/path"
        assert not model.loaded
        assert model.max_length == 512

def test_translator_model_load_success():
    """Test successful model loading"""
    with patch("app.model_scripts.translator_model.AutoTokenizer.from_pretrained") as mock_tokenizer, \
         patch("app.model_scripts.translator_model.AutoModelForSeq2SeqLM.from_pretrained") as mock_model, \
         patch("os.path.exists", return_value=True):
        
        mock_tokenizer.return_value = MagicMock()
        mock_model.return_value = MagicMock()
        
        from app.model_scripts.translator_model import TranslationModel
        model = TranslationModel()
        result = model.load()
        
        assert result is True
        assert model.loaded is True
        assert model.load_time is not None

def test_translator_model_load_failure():
    """Test model loading failure"""
    with patch("os.path.exists", return_value=False):
        from app.model_scripts.translator_model import TranslationModel
        model = TranslationModel()
        result = model.load()
        
        assert result is False
        assert model.loaded is False
        assert model.error is not None

def test_translate_short_text(mock_translator_model):
    """Test translating short text"""
    result = mock_translator_model.translate("Hello world", target_language="sw")
    
    assert result == "Mocked translation"
    mock_translator_model.model.generate.assert_called_once()

def test_translate_empty_text(mock_translator_model):
    """Test translating empty text"""
    result = mock_translator_model.translate("", target_language="sw")
    assert result == ""

def test_translate_model_not_loaded():
    """Test translating when model is not loaded"""
    from app.model_scripts.translator_model import TranslationModel
    model = TranslationModel()
    
    with pytest.raises(RuntimeError, match="Translation model is not loaded"):
        model.translate("Hello", target_language="sw")

def test_translate_with_chunking(mock_translator_model):
    """Test translation with text chunking for long text"""
    long_text = "This is a very long text. " * 50  # Make it long enough to require chunking
    
    with patch("app.core.text_chunker.IntelligentTextChunker.chunk_text") as mock_chunk:
        # Mock chunker to return fake chunks
        from types import SimpleNamespace
        fake_chunks = [
            SimpleNamespace(text="Chunk 1 text", chunk_id=0),
            SimpleNamespace(text="Chunk 2 text", chunk_id=1)
        ]
        mock_chunk.return_value = fake_chunks
        
        result = mock_translator_model.translate(long_text, target_language="sw")
        
        # Should call translation for each chunk
        assert result is not None
        assert isinstance(result, str)

def test_translate_with_fallback(mock_translator_model):
    """Test translation with fallback on failure"""
    # Mock the main translate method to fail
    with patch.object(mock_translator_model, 'translate', side_effect=RuntimeError("Translation failed")):
        result = mock_translator_model.translate_with_fallback("Hello world", target_language="sw")
        
        # Should return a fallback result
        assert result is not None
        assert isinstance(result, str)

def test_get_supported_languages(mock_translator_model):
    """Test getting supported languages"""
    languages = mock_translator_model.get_supported_languages()
    
    assert isinstance(languages, dict)
    assert "en" in languages
    assert "sw" in languages

def test_estimate_translation_time(mock_translator_model):
    """Test translation time estimation"""
    text = "This is a test text for time estimation."
    estimated_time = mock_translator_model.estimate_translation_time(text)
    
    assert isinstance(estimated_time, float)
    assert estimated_time > 0

def test_get_model_info(mock_translator_model):
    """Test getting model information"""
    info = mock_translator_model.get_model_info()
    
    assert isinstance(info, dict)
    assert "loaded" in info
    assert "model_path" in info
    assert "device" in info
    assert info["loaded"] is True

def test_is_ready(mock_translator_model):
    """Test model readiness check"""
    assert mock_translator_model.is_ready() is True
    
    mock_translator_model.loaded = False
    assert mock_translator_model.is_ready() is False

def test_detect_language(mock_translator_model):
    """Test language detection"""
    with patch("app.model_scripts.translator_model.detect") as mock_detect:
        mock_detect.return_value = "en"
        
        result = mock_translator_model.detect_language("Hello world")
        assert result == "en"

def test_translate_batch(mock_translator_model):
    """Test batch translation"""
    texts = ["Hello", "World", "Test"]
    
    results = mock_translator_model.translate_batch(texts, target_language="sw")
    
    assert isinstance(results, list)
    assert len(results) == len(texts)
    assert all(isinstance(r, str) for r in results)

def test_chunked_translation_aggregation(mock_translator_model):
    """Test aggregating chunked translation results"""
    chunk_results = ["First part.", "Second part.", "Third part."]
    
    aggregated = mock_translator_model._aggregate_translation_results(chunk_results)
    
    assert isinstance(aggregated, str)
    assert "First part." in aggregated
    assert "Second part." in aggregated
    assert "Third part." in aggregated

def test_translation_quality_check(mock_translator_model):
    """Test translation quality assessment"""
    original = "Hello world"
    translation = "Hola mundo"
    
    quality_score = mock_translator_model._assess_translation_quality(original, translation)
    
    assert isinstance(quality_score, float)
    assert 0 <= quality_score <= 1