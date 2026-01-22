"""
Comprehensive tests for NER Model
"""
import pytest
from unittest.mock import MagicMock, patch


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
        assert isinstance(info, dict)
