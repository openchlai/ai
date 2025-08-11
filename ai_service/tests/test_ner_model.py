import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Make sure app/ is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Patch settings.get_model_path globally
@pytest.fixture(autouse=True)
def patch_settings_path(monkeypatch):
    monkeypatch.setattr(
        "app.config.settings.Settings.get_model_path",
        lambda self, name: "/fake/model/path"
    )

@pytest.fixture
def mock_ner_model():
    with patch("app.model_scripts.ner_model.spacy.load") as mock_spacy_load, \
         patch("os.path.exists", return_value=False):

        # Fake SpaCy nlp pipeline mock
        mock_nlp = MagicMock()
        mock_nlp.meta = {
            "version": "3.8.0",
            "lang": "en"
        }
        mock_nlp.pipe_names = ["ner"]
        mock_nlp.get_pipe.return_value.labels = ["PERSON", "ORG"]

        # Simulated entity object
        mock_ent = MagicMock()
        mock_ent.text = "Barack Obama"
        mock_ent.label_ = "PERSON"
        mock_ent.start_char = 0
        mock_ent.end_char = 12
        mock_ent.confidence = 0.99

        # Mocked document returned by nlp("...")
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]

        # When mock_nlp is called (like nlp(text)), return the mock_doc
        mock_nlp.side_effect = lambda text: mock_doc


        # Set spacy.load(...) to return the mocked nlp
        mock_spacy_load.return_value = mock_nlp

        from app.model_scripts.ner_model import NERModel
        model = NERModel()
        model.nlp = mock_nlp
        model.loaded = True
        model.load_time = datetime.now()
        yield model

def test_load_model_success():
    with patch("app.model_scripts.ner_model.spacy.load"), \
         patch("os.path.exists", return_value=False), \
         patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
        from app.model_scripts.ner_model import NERModel
        model = NERModel()
        result = model.load()
        assert result is True
        assert model.loaded is True

def test_extract_entities_flat(mock_ner_model):
    result = mock_ner_model.extract_entities("Barack Obama is in Kenya.")
    assert isinstance(result, list)
    assert result[0]["text"] == "Barack Obama"
    assert result[0]["label"] == "PERSON"

def test_extract_entities_grouped(mock_ner_model):
    result = mock_ner_model.extract_entities("Barack Obama is in Kenya.", flat=False)
    assert isinstance(result, dict)
    assert "PERSON" in result

def test_extract_entities_empty_text(mock_ner_model):
    result = mock_ner_model.extract_entities("   ")
    assert result == []

def test_extract_entities_raises_if_not_loaded():
    from app.model_scripts.ner_model import NERModel
    model = NERModel()
    with pytest.raises(RuntimeError):
        model.extract_entities("Barack Obama")

def test_get_model_info(mock_ner_model):
    info = mock_ner_model.get_model_info()
    assert isinstance(info, dict)
    assert info["loaded"] is True
    assert "labels" in info

def test_is_ready_true(mock_ner_model):
    assert mock_ner_model.is_ready() is True
