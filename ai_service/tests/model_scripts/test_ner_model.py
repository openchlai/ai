import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestNERModelInitialization:
    """Tests for NERModel initialization"""

    def test_ner_model_init(self):
        """Test NER model initialization"""
        from app.model_scripts.ner_model import NERModel

        model = NERModel()

        assert model is not None
        assert hasattr(model, 'model_path')

    def test_init_with_custom_path(self):
        """Test initialization with custom model path"""
        from app.model_scripts.ner_model import NERModel

        model = NERModel(model_path="/custom/path")

        assert model.model_path == "/custom/path"

    def test_init_sets_default_values(self):
        """Test initialization sets default values"""
        from app.model_scripts.ner_model import NERModel

        model = NERModel()

        assert model.loaded is False
        assert model.error is None
        assert model.nlp is None
        assert model.hf_pipeline is None

    def test_init_sets_hf_repo_id(self):
        """Test initialization sets HF repo ID"""
        from app.model_scripts.ner_model import NERModel

        model = NERModel()

        assert hasattr(model, 'hf_repo_id')


class TestNERModelLoading:
    """Tests for NER model loading"""

    @patch('app.model_scripts.ner_model.pipeline')
    @patch('app.model_scripts.ner_model.AutoModelForTokenClassification')
    @patch('app.model_scripts.ner_model.AutoTokenizer')
    @patch('os.path.exists')
    def test_load_ner_success(self, mock_exists, mock_tokenizer_class, mock_model_class, mock_pipeline):
        """Test successful NER model loading"""
        from app.model_scripts.ner_model import NERModel

        mock_exists.return_value = True

        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.to.return_value = mock_model
        mock_model_class.from_pretrained.return_value = mock_model

        mock_pipeline.return_value = MagicMock()

        ner_model = NERModel()
        result = ner_model.load()

        assert result is True
        assert ner_model.loaded is True

    @patch('app.model_scripts.ner_model.spacy.load')
    @patch('os.path.exists')
    def test_load_ner_with_spacy_fallback(self, mock_exists, mock_spacy_load):
        """Test NER loading falls back to spaCy"""
        from app.model_scripts.ner_model import NERModel

        mock_exists.return_value = True
        mock_nlp = MagicMock()
        mock_nlp.meta = {"version": "1.0", "lang": "en"}
        mock_nlp.pipe_names = ["ner"]
        mock_nlp.get_pipe = MagicMock(return_value=MagicMock(labels=["PERSON", "ORG"]))
        mock_spacy_load.return_value = mock_nlp

        ner_model = NERModel()
        ner_model.hf_repo_id = None  # Disable HF path
        result = ner_model.load()

        assert result is True
        assert ner_model.loaded is True

    @patch('os.path.exists')
    @patch('app.model_scripts.ner_model.spacy.load')
    def test_load_ner_failure(self, mock_spacy_load, mock_exists):
        """Test NER model loading failure"""
        from app.model_scripts.ner_model import NERModel

        mock_exists.return_value = False
        mock_spacy_load.side_effect = OSError("Failed to load")

        ner_model = NERModel()
        ner_model.hf_repo_id = None  # Disable HF path
        result = ner_model.load()

        assert result is False


class TestExtractEntities:
    """Tests for entity extraction"""

    def test_extract_entities_not_loaded(self):
        """Test extract_entities when model not loaded"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = False

        with pytest.raises(RuntimeError, match="NER model not loaded"):
            ner_model.extract_entities("Test text")

    def test_extract_entities_empty_text(self):
        """Test extract_entities with empty text"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.nlp = MagicMock()

        result = ner_model.extract_entities("")

        assert result == []

    def test_extract_entities_whitespace_only(self):
        """Test extract_entities with whitespace only"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.nlp = MagicMock()

        result = ner_model.extract_entities("   ")

        assert result == []

    def test_extract_entities_with_spacy(self):
        """Test entity extraction with spaCy"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.use_hf = False

        # Mock spaCy nlp
        mock_ent1 = MagicMock()
        mock_ent1.text = "John"
        mock_ent1.label_ = "PERSON"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 4

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1]

        mock_nlp = MagicMock()
        mock_nlp.return_value = mock_doc
        ner_model.nlp = mock_nlp

        result = ner_model.extract_entities("John works")

        assert len(result) == 1
        assert result[0]["text"] == "John"
        assert result[0]["label"] == "PERSON"

    def test_extract_entities_with_hf_pipeline(self):
        """Test entity extraction with HF pipeline"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.use_hf = True
        ner_model.nlp = None

        # Mock HF pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [
            {"entity_group": "PERSON", "word": "John", "score": 0.99, "start": 0, "end": 4}
        ]
        ner_model.hf_pipeline = mock_pipeline

        result = ner_model.extract_entities("John works")

        assert len(result) == 1
        assert result[0]["text"] == "John"
        assert result[0]["label"] == "PERSON"

    def test_extract_entities_grouped(self):
        """Test entity extraction with grouped output"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.use_hf = False

        # Mock spaCy nlp
        mock_ent1 = MagicMock()
        mock_ent1.text = "John"
        mock_ent1.label_ = "PERSON"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 4

        mock_ent2 = MagicMock()
        mock_ent2.text = "Acme"
        mock_ent2.label_ = "ORG"
        mock_ent2.start_char = 10
        mock_ent2.end_char = 14

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, mock_ent2]

        mock_nlp = MagicMock()
        mock_nlp.return_value = mock_doc
        ner_model.nlp = mock_nlp

        result = ner_model.extract_entities("John works at Acme", flat=False)

        assert "PERSON" in result
        assert "ORG" in result
        assert "John" in result["PERSON"]
        assert "Acme" in result["ORG"]


class TestGetModelInfo:
    """Tests for model info"""

    def test_get_model_info_not_loaded(self):
        """Test getting model info when not loaded"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = False
        ner_model.error = "Not loaded"

        info = ner_model.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
        assert info["loaded"] is False
        assert info["error"] == "Not loaded"

    def test_get_model_info_loaded(self):
        """Test getting model info when loaded"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.load_time = datetime.now()
        ner_model.nlp = MagicMock()
        ner_model.nlp.meta = {"version": "1.0", "lang": "en"}
        ner_model.nlp.pipe_names = ["ner"]
        ner_model.nlp.get_pipe = MagicMock(return_value=MagicMock(labels=["PERSON"]))

        info = ner_model.get_model_info()

        assert info is not None
        assert info["loaded"] is True
        assert info["model_type"] == "ner"
        assert "details" in info


class TestIsReady:
    """Tests for is_ready method"""

    def test_returns_false_when_not_loaded(self):
        """Test returns False when not loaded"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = False

        assert ner_model.is_ready() is False

    def test_returns_false_when_nlp_and_pipeline_missing(self):
        """Test returns False when nlp and hf_pipeline are missing"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.nlp = None
        ner_model.hf_pipeline = None

        assert ner_model.is_ready() is False

    def test_returns_true_when_ready_with_nlp(self):
        """Test returns True when model is ready with spaCy"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.nlp = MagicMock()
        ner_model.error = None

        assert ner_model.is_ready() is True

    def test_returns_true_when_ready_with_hf_pipeline(self):
        """Test returns True when model is ready with HF pipeline"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.nlp = None
        ner_model.hf_pipeline = MagicMock()
        ner_model.error = None

        assert ner_model.is_ready() is True

    def test_returns_false_when_error_set(self):
        """Test returns False when error is set"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        ner_model.loaded = True
        ner_model.nlp = MagicMock()
        ner_model.error = "Some error"

        assert ner_model.is_ready() is False


class TestDownloadSpacyFromHF:
    """Tests for downloading spaCy from HuggingFace"""

    @patch('app.model_scripts.ner_model.TRANSFORMERS_AVAILABLE', False)
    def test_download_fails_without_transformers(self):
        """Test download fails when transformers not available"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        result = ner_model.download_spacy_from_hf()

        assert result is False

    @patch('app.model_scripts.ner_model.TRANSFORMERS_AVAILABLE', True)
    @patch('app.model_scripts.ner_model.snapshot_download')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_download_success(self, mock_open, mock_makedirs, mock_snapshot):
        """Test successful download from HuggingFace"""
        from app.model_scripts.ner_model import NERModel

        ner_model = NERModel()
        result = ner_model.download_spacy_from_hf()

        assert result is True
        mock_snapshot.assert_called_once()

    @patch('app.model_scripts.ner_model.TRANSFORMERS_AVAILABLE', True)
    @patch('app.model_scripts.ner_model.snapshot_download')
    @patch('os.makedirs')
    def test_download_handles_exception(self, mock_makedirs, mock_snapshot):
        """Test download handles exception"""
        from app.model_scripts.ner_model import NERModel

        mock_snapshot.side_effect = Exception("Download failed")

        ner_model = NERModel()
        result = ner_model.download_spacy_from_hf()

        assert result is False
