import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestQAModelBasic:
    """Basic tests for QA model"""

    def test_qa_initialization(self):
        """Test QA model can be initialized"""
        with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
            from app.model_scripts.qa_model import QAModel
            model = QAModel()

            assert model.model_path == "/fake/path"
            assert not model.loaded
            assert model.max_length == 512  # Correct attribute name

    def test_qa_load_success(self):
        """Test successful QA loading"""
        with patch("transformers.DistilBertTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.DistilBertModel.from_pretrained") as mock_distilbert, \
             patch("huggingface_hub.hf_hub_download") as mock_hf_download, \
             patch("torch.load") as mock_torch_load:

            mock_tok.return_value = MagicMock()
            mock_distilbert.return_value = MagicMock()
            mock_hf_download.return_value = "/fake/model/path.bin"
            mock_torch_load.return_value = {}

            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            # Mock the settings attribute directly
            model.settings.hf_qa_model = "openchs/qa-helpline-distilbert-v1"
            result = model.load()

            assert result is True
            assert model.loaded is True

    def test_qa_load_failure(self):
        """Test QA loading failure"""
        with patch("os.path.exists", return_value=False):
            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            result = model.load()
            
            assert result is False
            assert not model.loaded

    def test_qa_basic_methods(self):
        """Test basic QA methods"""
        with patch("transformers.DistilBertTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.DistilBertModel.from_pretrained") as mock_distilbert, \
             patch("huggingface_hub.hf_hub_download") as mock_hf_download, \
             patch("torch.load") as mock_torch_load:

            mock_tokenizer = MagicMock()
            mock_tokenizer.encode_plus.return_value = {
                'input_ids': [[1, 2, 3]],
                'attention_mask': [[1, 1, 1]]
            }
            mock_tokenizer.decode.return_value = "Answer text"
            mock_tok.return_value = mock_tokenizer

            mock_distilbert.return_value = MagicMock()
            mock_hf_download.return_value = "/fake/model/path.bin"
            mock_torch_load.return_value = {}

            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            # Mock the settings attribute directly
            model.settings.hf_qa_model = "openchs/qa-helpline-distilbert-v1"
            model.load()

            # Test is_ready
            assert model.is_ready() is True

            # Test get_model_info
            info = model.get_model_info()
            assert isinstance(info, dict)
            assert "loaded" in info

    def test_qa_not_loaded(self):
        """Test QA when not loaded"""
        from app.model_scripts.qa_model import QAModel
        model = QAModel()

        with pytest.raises(RuntimeError, match="QA model is not loaded"):
            model.score_transcript("This is a test.")  # Correct method name

    def test_qa_model_info(self):
        """Test getting QA model info"""
        with patch("app.model_scripts.qa_model.DistilBertTokenizer.from_pretrained") as mock_tok, \
             patch("app.model_scripts.qa_model.torch.load") as mock_load, \
             patch("os.path.exists", return_value=True):

            mock_tok.return_value = MagicMock()
            mock_load.return_value = {}

            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            model.loaded = True
            model.tokenizer = MagicMock()
            model.model = MagicMock()

            info = model.get_model_info()
            assert isinstance(info, dict)
            assert "loaded" in info
            # Actual QA model returns model_path, not model_name
            assert "model_path" in info

    def test_qa_empty_inputs(self):
        """Test QA with empty transcript"""
        with patch("app.model_scripts.qa_model.DistilBertTokenizer.from_pretrained") as mock_tok, \
             patch("app.model_scripts.qa_model.torch.load") as mock_load, \
             patch("os.path.exists", return_value=True):

            mock_tok.return_value = MagicMock()
            mock_load.return_value = {}

            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            model.loaded = True
            model.tokenizer = MagicMock()
            model.model = MagicMock()

            # Test with empty transcript - should return default score
            result = model.score_transcript("")
            assert isinstance(result, dict)
            assert "overall_qa_score" in result

            # Test with whitespace
            result = model.score_transcript("   ")
            assert isinstance(result, dict)