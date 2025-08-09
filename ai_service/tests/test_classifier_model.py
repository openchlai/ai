import sys
import os
import torch
import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

# Add project root to sys.path for import resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(
        "app.config.settings.Settings.get_model_path",
        lambda self, name: "/fake/classifier/path"
    )

@pytest.fixture
def mock_classifier_model():
    with patch("app.models.classifier_model.AutoTokenizer.from_pretrained"), \
         patch("app.models.classifier_model.MultiTaskDistilBert.from_pretrained"), \
         patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='["violence", "neglect"]')), \
         patch("json.load", side_effect=[
             ["violence", "neglect"],
             ["physical_abuse", "emotional_abuse"],
             ["intervention_1", "intervention_2"],
             ["low", "medium", "high", "urgent"]
         ]):
        from app.models.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.load_time = datetime.now()
        model.tokenizer = MagicMock()
        model.model = MagicMock()
        model.main_categories = ["violence", "neglect"]
        model.sub_categories = ["physical_abuse", "emotional_abuse"]
        model.interventions = ["intervention_1", "intervention_2"]
        model.priorities = ["low", "medium", "high", "urgent"]
        return model

def test_model_load_success():
    with patch("app.models.classifier_model.AutoTokenizer.from_pretrained"), \
         patch("app.models.classifier_model.MultiTaskDistilBert.from_pretrained"), \
         patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='["main1", "main2"]')), \
         patch("json.load", side_effect=[
             ["main1", "main2"],
             ["sub1", "sub2"],
             ["int1", "int2"],
             ["low", "high"]
         ]):
        from app.models.classifier_model import ClassifierModel
        model = ClassifierModel()
        assert model.load() is True
        assert model.loaded is True

def test_classify_single_text(mock_classifier_model):
    with patch.object(mock_classifier_model, "_classify_single", return_value={
        "main_category": "violence",
        "sub_category": "physical_abuse",
        "intervention": "intervention_1",
        "priority": "medium",
        "confidence": 0.9
    }):
        mock_classifier_model.tokenizer.encode.return_value = [1] * 50
        result = mock_classifier_model.classify("A child was hit at home.")
        assert result["main_category"] == "violence"

def test_classify_empty_text_returns_default(mock_classifier_model):
    result = mock_classifier_model.classify("")
    assert result["main_category"] == "general_inquiry"
    assert result["confidence"] == 0.0

def test_fallback_classification_success(mock_classifier_model):
    with patch.object(mock_classifier_model, "classify", return_value={"main_category": "violence"}):
        result = mock_classifier_model.classify_with_fallback("Something serious happened.")
        assert result["main_category"] == "violence"

def test_fallback_classification_failure(mock_classifier_model):
    with patch.object(mock_classifier_model, "classify", side_effect=RuntimeError("Failure")):
        result = mock_classifier_model.classify_with_fallback("Trigger retry")
        assert result["main_category"] == "general_inquiry"

def test_get_model_info(mock_classifier_model):
    info = mock_classifier_model.get_model_info()
    assert info["loaded"] is True
    assert "main" in info["num_categories"]

def test_is_ready(mock_classifier_model):
    assert mock_classifier_model.is_ready() is True

def test_classify_chunked(mock_classifier_model):
    from types import SimpleNamespace

    # Fake chunk objects
    fake_chunks = [
        SimpleNamespace(text="Chunk 1", token_count=50),
        SimpleNamespace(text="Chunk 2", token_count=60),
    ]
    
    with patch("app.core.text_chunker.text_chunker.chunk_text", return_value=fake_chunks), \
         patch.object(mock_classifier_model, "_classify_single", return_value={
             "main_category": "violence",
             "sub_category": "physical_abuse",
             "intervention": "intervention_1",
             "priority": "medium",
             "confidence": 0.8
         }), \
         patch.object(mock_classifier_model, "_aggregate_classification_results", return_value={
             "main_category": "violence",
             "sub_category": "physical_abuse",
             "intervention": "intervention_1",
             "priority": "medium",
             "confidence": 0.85
         }):
        result = mock_classifier_model._classify_chunked("Some long text needing chunking")
        assert result["main_category"] == "violence"

def test_aggregate_classification_results(mock_classifier_model):
    chunked_results = [
        {
            "main_category": "violence",
            "sub_category": "physical_abuse",
            "intervention": "intervention_1",
            "priority": "high",
            "confidence": 0.9
        },
        {
            "main_category": "violence",
            "sub_category": "emotional_abuse",
            "intervention": "intervention_2",
            "priority": "medium",
            "confidence": 0.8
        }
    ]
    from types import SimpleNamespace
    fake_chunks = [SimpleNamespace(token_count=50), SimpleNamespace(token_count=50)]

    result = mock_classifier_model._aggregate_classification_results(chunked_results, fake_chunks)
    assert result["main_category"] == "violence"
    assert "confidence" in result

def test_estimate_classification_time(mock_classifier_model):
    fake_chunks = [MagicMock(), MagicMock()]
    with patch("app.core.text_chunker.text_chunker.chunk_text", return_value=fake_chunks), \
         patch("app.core.text_chunker.text_chunker.estimate_processing_time", return_value=1.2):
        mock_classifier_model.tokenizer.encode.return_value = [1] * 300
        result = mock_classifier_model.estimate_classification_time("Long test text")
        assert result > 0
