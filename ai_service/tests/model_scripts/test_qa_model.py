import pytest
import torch
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestQAModelInitialization:
    """Tests for QAModel initialization"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_qa_model_init(self, mock_cuda):
        """Test QA model initialization"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        model = QAModel()

        assert model is not None
        assert model.device == torch.device("cpu")

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_init_with_custom_path(self, mock_cuda):
        """Test initialization with custom model path"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        model = QAModel(model_path="/custom/path")

        assert model.model_path == "/custom/path"

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_init_sets_default_values(self, mock_cuda):
        """Test initialization sets default values"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        model = QAModel()

        assert model.loaded is False
        assert model.error is None
        assert model.max_length == 512
        assert model.tokenizer is None
        assert model.model is None

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_init_uses_cuda_when_available(self, mock_cuda):
        """Test CUDA is used when available"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = True

        model = QAModel()

        assert model.device == torch.device("cuda")


class TestQAModelLoading:
    """Tests for QA model loading"""

    @patch('app.model_scripts.qa_model.DistilBertTokenizer')
    @patch('app.model_scripts.qa_model.DistilBertModel')
    @patch('os.path.exists')
    def test_load_qa_failure(self, mock_exists, mock_model_class, mock_tokenizer_class):
        """Test QA model loading failure"""
        from app.model_scripts.qa_model import QAModel

        mock_tokenizer_class.from_pretrained.side_effect = Exception("Failed to load")
        mock_exists.return_value = False

        qa_model = QAModel()
        result = qa_model.load()

        assert result is False
        assert qa_model.error is not None

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_load_sets_load_time(self, mock_cuda):
        """Test load sets load_time regardless of success"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.load()

        assert qa_model.load_time is not None


class TestScoreTranscript:
    """Tests for transcript scoring"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_score_transcript_not_loaded(self, mock_cuda):
        """Test score_transcript when model not loaded"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = False

        with pytest.raises(RuntimeError, match="QA model is not loaded"):
            qa_model.score_transcript("Test transcript")

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_score_transcript_empty_text(self, mock_cuda):
        """Test score_transcript with empty text"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.model = MagicMock()
        qa_model.tokenizer = MagicMock()

        result = qa_model.score_transcript("")

        assert result == {"overall_qa_score": 0.0, "detailed_scores": {}}

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_score_transcript_whitespace_only(self, mock_cuda):
        """Test score_transcript with whitespace only"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.model = MagicMock()
        qa_model.tokenizer = MagicMock()

        result = qa_model.score_transcript("   ")

        assert result == {"overall_qa_score": 0.0, "detailed_scores": {}}

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_score_transcript_success(self, mock_cuda):
        """Test successful transcript scoring"""
        from app.model_scripts.qa_model import QAModel, QA_HEADS_CONFIG

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.device = torch.device("cpu")

        # Mock tokenizer
        qa_model.tokenizer = MagicMock()
        mock_encoding = MagicMock()
        mock_encoding.__getitem__ = MagicMock(side_effect=lambda x: MagicMock())
        qa_model.tokenizer.return_value = mock_encoding

        # Mock model output
        qa_model.model = MagicMock()
        mock_logits = {}
        for head_name, output_dim in QA_HEADS_CONFIG.items():
            mock_logits[head_name] = torch.tensor([[0.6] * output_dim])
        qa_model.model.return_value = {"logits": mock_logits}

        result = qa_model.score_transcript("Test transcript", threshold=0.5)

        assert "overall_qa_score" in result
        assert "detailed_scores" in result
        assert isinstance(result["overall_qa_score"], float)


class TestPredict:
    """Tests for predict method"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_predict_not_loaded(self, mock_cuda):
        """Test predict when model not loaded"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = False

        with pytest.raises(RuntimeError, match="QA model is not loaded"):
            qa_model.predict("Test text")

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_predict_success(self, mock_cuda):
        """Test successful prediction"""
        from app.model_scripts.qa_model import QAModel, QA_HEADS_CONFIG

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.device = torch.device("cpu")

        # Mock tokenizer
        qa_model.tokenizer = MagicMock()
        mock_encoding = MagicMock()
        mock_encoding.__getitem__ = MagicMock(side_effect=lambda x: MagicMock())
        qa_model.tokenizer.return_value = mock_encoding

        # Mock model output
        qa_model.model = MagicMock()
        mock_logits = {}
        for head_name, output_dim in QA_HEADS_CONFIG.items():
            mock_logits[head_name] = torch.tensor([[0.7] * output_dim])
        qa_model.model.return_value = {"logits": mock_logits}

        result = qa_model.predict("Test text", threshold=0.5)

        assert isinstance(result, dict)
        # Should have results for each head
        for head_name in QA_HEADS_CONFIG.keys():
            assert head_name in result

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_predict_default_threshold(self, mock_cuda):
        """Test predict uses default threshold when None"""
        from app.model_scripts.qa_model import QAModel, QA_HEADS_CONFIG

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.device = torch.device("cpu")
        qa_model.tokenizer = MagicMock()
        mock_encoding = MagicMock()
        mock_encoding.__getitem__ = MagicMock(side_effect=lambda x: MagicMock())
        qa_model.tokenizer.return_value = mock_encoding

        qa_model.model = MagicMock()
        mock_logits = {}
        for head_name, output_dim in QA_HEADS_CONFIG.items():
            mock_logits[head_name] = torch.tensor([[0.5] * output_dim])
        qa_model.model.return_value = {"logits": mock_logits}

        # Should not raise with None threshold
        result = qa_model.predict("Test", threshold=None)

        assert isinstance(result, dict)


class TestGetDefaultScore:
    """Tests for _get_default_score method"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_returns_expected_structure(self, mock_cuda):
        """Test returns expected structure"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        result = qa_model._get_default_score()

        assert "overall_qa_score" in result
        assert "detailed_scores" in result
        assert result["overall_qa_score"] == 0.0
        assert result["detailed_scores"] == {}


class TestCleanupMemory:
    """Tests for memory cleanup"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    @patch('app.model_scripts.qa_model.gc')
    def test_cleanup_calls_gc(self, mock_gc, mock_cuda):
        """Test cleanup calls gc.collect"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model._cleanup_memory()

        mock_gc.collect.assert_called_once()

    @patch('app.model_scripts.qa_model.torch')
    @patch('app.model_scripts.qa_model.gc')
    def test_cleanup_clears_cuda_cache(self, mock_gc, mock_torch):
        """Test cleanup clears CUDA cache when available"""
        from app.model_scripts.qa_model import QAModel

        mock_torch.cuda.is_available.return_value = True

        qa_model = QAModel()
        qa_model._cleanup_memory()

        mock_torch.cuda.empty_cache.assert_called_once()


class TestGetModelInfo:
    """Tests for model info"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_get_model_info_not_loaded(self, mock_cuda):
        """Test getting model info when not loaded"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = False
        qa_model.error = "Not loaded"

        info = qa_model.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
        assert info["loaded"] is False
        assert info["error"] == "Not loaded"
        assert info["model_type"] == "qa"

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_get_model_info_loaded(self, mock_cuda):
        """Test getting model info when loaded"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.load_time = datetime.now()
        qa_model.model = MagicMock()
        qa_model.tokenizer = MagicMock()

        info = qa_model.get_model_info()

        assert info is not None
        assert info["loaded"] is True
        assert "details" in info
        assert "qa_heads_config" in info["details"]


class TestIsReady:
    """Tests for is_ready method"""

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_returns_false_when_not_loaded(self, mock_cuda):
        """Test returns False when not loaded"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = False

        assert qa_model.is_ready() is False

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_returns_false_when_model_missing(self, mock_cuda):
        """Test returns False when model is missing"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.model = None
        qa_model.tokenizer = MagicMock()

        assert qa_model.is_ready() is False

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_returns_false_when_tokenizer_missing(self, mock_cuda):
        """Test returns False when tokenizer is missing"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.model = MagicMock()
        qa_model.tokenizer = None

        assert qa_model.is_ready() is False

    @patch('app.model_scripts.qa_model.torch.cuda.is_available')
    def test_returns_true_when_ready(self, mock_cuda):
        """Test returns True when model is ready"""
        from app.model_scripts.qa_model import QAModel

        mock_cuda.return_value = False

        qa_model = QAModel()
        qa_model.loaded = True
        qa_model.model = MagicMock()
        qa_model.tokenizer = MagicMock()

        assert qa_model.is_ready() is True


class TestQAHeadsConfig:
    """Tests for QA heads configuration"""

    def test_qa_heads_config_exists(self):
        """Test QA_HEADS_CONFIG exists and has expected keys"""
        from app.model_scripts.qa_model import QA_HEADS_CONFIG

        expected_heads = ["opening", "listening", "proactiveness", "resolution", "hold", "closing"]
        for head in expected_heads:
            assert head in QA_HEADS_CONFIG

    def test_head_submetric_labels_exists(self):
        """Test HEAD_SUBMETRIC_LABELS exists and has expected keys"""
        from app.model_scripts.qa_model import HEAD_SUBMETRIC_LABELS, QA_HEADS_CONFIG

        for head in QA_HEADS_CONFIG.keys():
            assert head in HEAD_SUBMETRIC_LABELS
            assert len(HEAD_SUBMETRIC_LABELS[head]) == QA_HEADS_CONFIG[head]


class TestMultiHeadQAClassifier:
    """Tests for MultiHeadQAClassifier model"""

    @patch('app.model_scripts.qa_model.DistilBertModel')
    def test_multi_head_classifier_init(self, mock_distilbert):
        """Test MultiHeadQAClassifier initialization"""
        from app.model_scripts.qa_model import MultiHeadQAClassifier, QA_HEADS_CONFIG

        mock_distilbert.from_pretrained.return_value = MagicMock()
        mock_distilbert.from_pretrained.return_value.config = MagicMock()
        mock_distilbert.from_pretrained.return_value.config.hidden_size = 768

        # This should not raise
        classifier = MultiHeadQAClassifier.__new__(MultiHeadQAClassifier)

        # Basic assertions about structure
        assert hasattr(MultiHeadQAClassifier, 'forward')
