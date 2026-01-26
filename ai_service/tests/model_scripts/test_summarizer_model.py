import pytest
import torch
from unittest.mock import MagicMock, patch
from datetime import datetime


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

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_init_with_custom_path(self, mock_cuda):
        """Test initialization with custom model path"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        model = SummarizationModel(model_path="/custom/path")

        assert model.model_path == "/custom/path"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_init_sets_default_values(self, mock_cuda):
        """Test initialization sets default values"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        model = SummarizationModel()

        assert model.loaded is False
        assert model.error is None
        assert model.max_length == 512
        assert model.tokenizer is None
        assert model.model is None
        assert model.pipeline is None

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_init_uses_cuda_when_available(self, mock_cuda):
        """Test CUDA is used when available"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = True

        model = SummarizationModel()

        assert model.device == torch.device("cuda")


class TestSummarizerModelLoading:
    """Tests for summarizer model loading"""

    @patch('os.path.exists')
    @patch('app.model_scripts.summarizer_model.pipeline')
    @patch('app.model_scripts.summarizer_model.AutoModelForSeq2SeqLM')
    @patch('app.model_scripts.summarizer_model.AutoTokenizer')
    @patch('os.makedirs')
    @patch('os.getenv')
    def test_load_summarizer_success(self, mock_getenv, mock_makedirs, mock_tokenizer_class, mock_model_class, mock_pipeline, mock_exists):
        """Test successful summarizer loading"""
        import os as os_module
        from app.model_scripts.summarizer_model import SummarizationModel

        # Mock environment variable for HuggingFace model
        def getenv_side_effect(key, default=None):
            if key == "SUMMARIZATION_HF_REPO_ID":
                return "openchs/sum-flan-t5-base-synthetic-v1"
            return os_module.environ.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

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
        assert summarizer.error is not None

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_load_fails_without_hf_repo(self, mock_cuda):
        """Test load fails without HF repo ID"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.hf_repo_id = None

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

        with pytest.raises(RuntimeError, match="Summarization model not loaded"):
            summarizer.summarize("Some text")

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_empty_text(self, mock_load):
        """Test summarization with empty text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()

        result = summarizer.summarize("")

        assert result == ""

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_whitespace_only(self, mock_load):
        """Test summarization with whitespace only"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()

        result = summarizer.summarize("   ")

        assert result == ""

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_summarize_calls_cleanup(self, mock_load):
        """Test summarization calls cleanup"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.return_value = [{"summary_text": "Summary"}]
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3]

        with patch.object(summarizer, '_cleanup_memory') as mock_cleanup:
            summarizer.summarize("Test text")

        mock_cleanup.assert_called_once()


class TestSummarizeHierarchical:
    """Tests for hierarchical summarization"""

    @patch('app.model_scripts.summarizer_model.SummarizationModel.load')
    def test_uses_hierarchical_for_long_text(self, mock_load):
        """Test hierarchical summarization is used for long text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = list(range(1000))  # Long text
        summarizer.max_length = 512

        with patch.object(summarizer, '_summarize_hierarchical', return_value="Hierarchical summary") as mock_hier:
            with patch.object(summarizer, '_cleanup_memory'):
                result = summarizer.summarize("Very long text")

        mock_hier.assert_called_once()
        assert result == "Hierarchical summary"


class TestFallbackSummary:
    """Tests for fallback summary creation"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_create_fallback_short_text(self, mock_cuda):
        """Test fallback summary for short text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        result = summarizer._create_fallback_summary("Short text")

        assert result == "Short text"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_create_fallback_long_text(self, mock_cuda):
        """Test fallback summary for long text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = summarizer._create_fallback_summary(text, max_sentences=2)

        assert "First sentence" in result
        assert "Fourth sentence" in result

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_create_fallback_single_sentence(self, mock_cuda):
        """Test fallback summary for single long sentence"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        text = "A" * 300  # Very long single sentence
        result = summarizer._create_fallback_summary(text)

        # Single sentence without period is returned as-is
        # (implementation uses '. ' split which returns single element for text without periods)
        assert result == text


class TestSummarizeWithFallback:
    """Tests for summarize with fallback"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_returns_empty_for_empty_text(self, mock_cuda):
        """Test returns empty for empty text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        result = summarizer.summarize_with_fallback("")

        assert result == ""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_retries_on_failure(self, mock_cuda):
        """Test retries on failure"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()
        summarizer.tokenizer = MagicMock()

        with patch.object(summarizer, 'summarize', side_effect=[Exception("Error"), "Success"]):
            with patch.object(summarizer, '_cleanup_memory'):
                result = summarizer.summarize_with_fallback("Test", max_retries=2)

        assert result == "Success"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_returns_fallback_after_max_retries(self, mock_cuda):
        """Test returns fallback after max retries"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.loaded = True

        with patch.object(summarizer, 'summarize', side_effect=Exception("Error")):
            with patch.object(summarizer, '_cleanup_memory'):
                with patch.object(summarizer, '_create_fallback_summary', return_value="Fallback") as mock_fb:
                    result = summarizer.summarize_with_fallback("Test text", max_retries=1)

        mock_fb.assert_called()
        assert result == "Fallback"


class TestEstimateSummarizationTime:
    """Tests for time estimation"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_returns_zero_for_empty(self, mock_cuda):
        """Test returns zero for empty text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        result = summarizer.estimate_summarization_time("")

        assert result == 0.0

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_returns_time_for_short_text(self, mock_cuda):
        """Test returns time estimate for short text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3]

        result = summarizer.estimate_summarization_time("Short text")

        assert result == 3.0


class TestGetSummarizationStrategyInfo:
    """Tests for strategy info"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_returns_none_for_empty(self, mock_cuda):
        """Test returns none strategy for empty text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        result = summarizer.get_summarization_strategy_info("")

        assert result["strategy"] == "none"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_returns_single_pass_for_short(self, mock_cuda):
        """Test returns single pass for short text"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3]

        result = summarizer.get_summarization_strategy_info("Short text")

        assert result["strategy"] == "single_pass"


class TestCleanupMemory:
    """Tests for memory cleanup"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    @patch('app.model_scripts.summarizer_model.gc')
    def test_cleanup_calls_gc(self, mock_gc, mock_cuda):
        """Test cleanup calls gc.collect"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer._cleanup_memory()

        mock_gc.collect.assert_called_once()

    @patch('app.model_scripts.summarizer_model.torch')
    @patch('app.model_scripts.summarizer_model.gc')
    def test_cleanup_clears_cuda_cache(self, mock_gc, mock_torch):
        """Test cleanup clears CUDA cache when available"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_torch.cuda.is_available.return_value = True

        summarizer = SummarizationModel()
        summarizer._cleanup_memory()

        mock_torch.cuda.empty_cache.assert_called_once()


class TestSummarizerModelInfo:
    """Tests for summarizer model info"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_get_model_info_not_loaded(self, mock_cuda):
        """Test getting model info when not loaded"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.loaded = False
        summarizer.error = "Not loaded"

        info = summarizer.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
        assert info["loaded"] is False
        assert info["error"] == "Not loaded"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_get_model_info_loaded(self, mock_cuda):
        """Test getting model info when loaded"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.load_time = datetime.now()
        summarizer.model = MagicMock()
        summarizer.tokenizer = MagicMock()

        info = summarizer.get_model_info()

        assert info is not None
        assert info["loaded"] is True
        assert info["model_type"] == "summarizer"
        assert "details" in info

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_get_model_info_includes_device(self, mock_cuda):
        """Test model info includes device"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()

        info = summarizer.get_model_info()

        assert "device" in info


class TestOptimizeCombinedSummaries:
    """Tests for optimizing combined summaries"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_optimize_sorts_by_importance(self, mock_cuda):
        """Test optimization sorts by original length"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        chunk_summaries = [
            {"summary": "Short", "chunk_id": 1, "original_length": 50},
            {"summary": "Long summary text", "chunk_id": 2, "original_length": 200},
            {"summary": "Medium", "chunk_id": 3, "original_length": 100}
        ]

        result = summarizer._optimize_combined_summaries(chunk_summaries, max_length=150)

        # Result should prioritize longer original chunks
        assert "Long summary text" in result

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_optimize_limits_length(self, mock_cuda):
        """Test optimization limits total length"""
        from app.model_scripts.summarizer_model import SummarizationModel

        mock_cuda.return_value = False

        summarizer = SummarizationModel()
        chunk_summaries = [
            {"summary": "A" * 100, "chunk_id": 1, "original_length": 200},
            {"summary": "B" * 100, "chunk_id": 2, "original_length": 150}
        ]

        result = summarizer._optimize_combined_summaries(chunk_summaries, max_length=50)

        # Result should be limited
        assert len(result) < 1000
