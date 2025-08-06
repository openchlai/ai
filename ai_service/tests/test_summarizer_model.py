import sys
import os

# Add the project root directory to sys.path so `app` can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

@pytest.fixture
def mock_model():
    with patch("app.models.summarizer_model.AutoTokenizer.from_pretrained"), \
         patch("app.models.summarizer_model.AutoModelForSeq2SeqLM.from_pretrained"), \
         patch("app.models.summarizer_model.pipeline"), \
         patch("os.path.exists", return_value=True), \
         patch("app.config.settings.Settings.get_model_path", return_value="/fake/model/path"):

        from app.models.summarizer_model import SummarizationModel
        model = SummarizationModel()
        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = list(range(100))  # Simulate 100 tokens
        model.pipeline = MagicMock()
        model.pipeline.return_value = [{"summary_text": "Mocked summary"}]
        model.loaded = True

        yield model



def test_load_model_success():
    with patch("app.models.summarizer_model.AutoTokenizer.from_pretrained"), \
         patch("app.models.summarizer_model.AutoModelForSeq2SeqLM.from_pretrained"), \
         patch("app.models.summarizer_model.pipeline"), \
         patch("os.path.exists", return_value=True), \
         patch("app.config.settings.Settings.get_model_path", return_value="/fake/model/path"):

        from app.models.summarizer_model import SummarizationModel
        model = SummarizationModel()
        result = model.load()
        assert result is True
        assert model.loaded is True


def test_summarize_short_text(mock_model):
    text = "This is a short test input."
    summary = mock_model.summarize(text)
    assert isinstance(summary, str)

def test_summarize_empty_text_returns_blank(mock_model):
    result = mock_model.summarize("   ")
    assert result == ""

def test_summarize_not_loaded_raises():
    from app.models.summarizer_model import SummarizationModel
    model = SummarizationModel()
    with pytest.raises(RuntimeError):
        model.summarize("Some input")

def test_fallback_summary_generation(mock_model):
    long_text = "This is a long sentence. Here is another one. Yet another one."
    result = mock_model._create_fallback_summary(long_text)
    assert isinstance(result, str)

def test_get_model_info(mock_model):
    info = mock_model.get_model_info()
    assert isinstance(info, dict)
    assert info["task"] == "text-summarization"
    assert "loaded" in info

def test_summarization_strategy_info_single(mock_model):
    result = mock_model.get_summarization_strategy_info("Short text.")
    assert result["strategy"] == "single_pass"

def test_summarize_with_fallback_success(mock_model):
    result = mock_model.summarize_with_fallback("A test input.")
    assert isinstance(result, str)

def test_summarize_with_fallback_failure(mock_model):
    from app.models.summarizer_model import SummarizationModel
    with patch.object(mock_model, "summarize", side_effect=RuntimeError("fail")):
        result = mock_model.summarize_with_fallback("Fallback trigger input.")
        assert isinstance(result, str)


def test_estimate_summarization_time(mock_model):
    result = mock_model.estimate_summarization_time("This is a test.")
    assert isinstance(result, float)
