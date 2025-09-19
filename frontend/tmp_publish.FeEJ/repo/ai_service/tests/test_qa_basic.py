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
            assert model.max_question_length == 512

    def test_qa_load_success(self):
        """Test successful QA loading"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForQuestionAnswering.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()
            
            from app.model_scripts.qa_model import QAModel
            model = QAModel()
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
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForQuestionAnswering.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tokenizer = MagicMock()
            mock_tokenizer.encode_plus.return_value = {
                'input_ids': [[1, 2, 3]],
                'attention_mask': [[1, 1, 1]]
            }
            mock_tokenizer.decode.return_value = "Answer text"
            mock_tok.return_value = mock_tokenizer
            
            mock_model_instance = MagicMock()
            mock_model_instance.return_value = MagicMock(start_logits=[1, 2, 3], end_logits=[1, 2, 3])
            mock_model.return_value = mock_model_instance
            
            from app.model_scripts.qa_model import QAModel
            model = QAModel()
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
        
        with pytest.raises(RuntimeError):
            model.answer_question("What is this?", "This is a test.")

    def test_qa_model_info(self):
        """Test getting QA model info"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForQuestionAnswering.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()
            
            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            model.load()
            
            info = model.get_model_info()
            assert isinstance(info, dict)
            assert "loaded" in info
            assert "model_name" in info

    def test_qa_empty_inputs(self):
        """Test QA with empty inputs"""
        with patch("transformers.AutoTokenizer.from_pretrained") as mock_tok, \
             patch("transformers.AutoModelForQuestionAnswering.from_pretrained") as mock_model, \
             patch("os.path.exists", return_value=True):
            
            mock_tok.return_value = MagicMock()
            mock_model.return_value = MagicMock()
            
            from app.model_scripts.qa_model import QAModel
            model = QAModel()
            model.load()
            
            # Test with empty question
            result = model.answer_question("", "Some context")
            assert result == ""
            
            # Test with empty context
            result = model.answer_question("What is this?", "")
            assert result == ""