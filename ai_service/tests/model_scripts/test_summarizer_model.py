"""
Comprehensive tests for Summarizer Model
"""
import pytest
import torch
from unittest.mock import MagicMock, patch


class TestSummarizerModelInitialization:
    """Tests for SummarizationModel initialization"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarizer_model_init(self, mock_cuda):
        """Test summarizer model initialization"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        model = SummarizationModel()

        assert model is not None
        assert model.device == torch.device("cpu")


class TestSummarizerModelLoading:
    """Tests for summarizer model loading"""

    @patch('os.path.exists')
    @patch('app.model_scripts.summarizer_model.pipeline')
    @patch('app.model_scripts.summarizer_model.AutoModelForSeq2SeqLM')
    @patch('app.model_scripts.summarizer_model.AutoTokenizer')
    @patch('os.makedirs')
    def test_load_summarizer_success(self, mock_makedirs, mock_tokenizer_class, mock_model_class, mock_pipeline, mock_exists):
        """Test successful summarizer loading"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_exists.return_value = True

        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.to = MagicMock(return_value=mock_model)
        mock_model_class.from_pretrained.return_value = mock_model

        # Mock pipeline creation
        mock_pipeline.return_value = MagicMock()

        summarizer = SummarizationModel()
        result = summarizer.load()

        assert result is True
        assert summarizer.loaded is True

    @patch('app.model_scripts.summarizer_model.AutoTokenizer')
    def test_load_summarizer_failure(self, mock_tokenizer_class):
        """Test summarizer loading failure"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_tokenizer_class.from_pretrained.side_effect = Exception("Failed to load")

        summarizer = SummarizationModel()
        result = summarizer.load()

        assert result is False


class TestSummarizerModelSummarization:
    """Tests for summarization functionality"""

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_simple_text(self, mock_load):
        """Test summarization of simple text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True

        # Mock pipeline and tokenizer
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.return_value = [{"summary_text": "This is a summary"}]

        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # Short text

        result = summarizer.summarize("Long text to summarize")

        assert result is not None
        assert isinstance(result, str)
        assert result == "This is a summary"

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_with_max_length(self, mock_load):
        """Test summarization with custom max length"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True

        # Mock pipeline and tokenizer
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.return_value = [{"summary_text": "Summary"}]

        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3]  # Short text

        result = summarizer.summarize("Text", max_length=100)

        assert result is not None
        assert result == "Summary"

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_model_not_loaded(self, mock_load):
        """Test summarization when model not loaded"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = False

        with pytest.raises(Exception):
            summarizer.summarize("Some text")


class TestSummarizerModelInfo:
    """Tests for summarizer model info"""

    def test_get_model_info(self):
        """Test getting summarizer model info"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True

        info = summarizer.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
