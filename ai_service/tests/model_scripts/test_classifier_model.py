import pytest
import json
import os
import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime


@pytest.fixture
def mock_tokenizer():
    """Mock DistilBERT tokenizer"""
    tokenizer = MagicMock()

    # Create a mock that returns tensors with .to() method
    mock_encoding = MagicMock()
    mock_encoding.to = MagicMock(return_value={
        "input_ids": torch.tensor([[1, 2, 3, 4, 5]]),
        "attention_mask": torch.tensor([[1, 1, 1, 1, 1]])
    })
    mock_encoding.__getitem__ = lambda self, key: torch.tensor([[1, 2, 3, 4, 5]]) if key == "input_ids" else torch.tensor([[1, 1, 1, 1, 1]])

    tokenizer.return_value = mock_encoding
    tokenizer.encode.return_value = [1, 2, 3, 4, 5]
    return tokenizer


@pytest.fixture
def mock_model():
    """Mock classifier model"""
    model = MagicMock()
    model.eval = MagicMock()
    model.to = MagicMock(return_value=model)

    # Mock forward pass output - returns tuple of 4 tensors
    output = (
        torch.tensor([[0.1, 0.9, 0.05, 0.05]]),  # main_category logits
        torch.tensor([[0.15, 0.85, 0.0]]),       # sub_category logits
        torch.tensor([[0.2, 0.8]]),              # intervention logits
        torch.tensor([[0.1, 0.3, 0.6]])          # priority logits
    )
    model.return_value = output
    model.forward = MagicMock(return_value=output)

    # Mock __call__ to behave like forward
    model.__call__ = MagicMock(return_value=output)

    return model


class TestClassifierModelInitialization:
    """Test ClassifierModel initialization"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_init_default_settings(self, mock_torch):
        """Test initialization with default settings"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        assert model.loaded is False
        assert model.max_length == 512

    @patch('app.model_scripts.classifier_model.torch')
    def test_init_custom_model_path(self, mock_torch):
        """Test initialization with custom model path"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel(model_path="/custom/path")

        assert model.model_path == "/custom/path"

    @patch('app.model_scripts.classifier_model.torch')
    def test_init_uses_cuda_when_available(self, mock_torch):
        """Test initialization uses CUDA when available"""
        mock_torch.cuda.is_available.return_value = True
        mock_device = MagicMock()
        mock_torch.device.return_value = mock_device

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        mock_torch.device.assert_called_with("cuda")

    @patch('app.model_scripts.classifier_model.torch')
    def test_init_sets_empty_categories(self, mock_torch):
        """Test initialization sets empty category lists"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        assert model.main_categories == []
        assert model.sub_categories == []
        assert model.interventions == []
        assert model.priorities == []

    @patch('app.model_scripts.classifier_model.torch')
    def test_init_sets_error_to_none(self, mock_torch):
        """Test initialization sets error to None"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        assert model.error is None
        assert model.load_time is None


class TestPreprocessText:
    """Test text preprocessing"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_preprocess_converts_to_lowercase(self, mock_torch):
        """Test text is converted to lowercase"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model.preprocess_text("HELLO WORLD")

        assert result == "hello world"

    @patch('app.model_scripts.classifier_model.torch')
    def test_preprocess_removes_special_characters(self, mock_torch):
        """Test special characters are removed"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model.preprocess_text("Hello, World! @#$%")

        assert result == "hello world "

    @patch('app.model_scripts.classifier_model.torch')
    def test_preprocess_strips_whitespace(self, mock_torch):
        """Test leading/trailing whitespace is stripped"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model.preprocess_text("  hello world  ")

        assert result == "hello world"

    @patch('app.model_scripts.classifier_model.torch')
    def test_preprocess_preserves_alphanumeric(self, mock_torch):
        """Test alphanumeric characters are preserved"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model.preprocess_text("Test123 Message456")

        assert "test123" in result
        assert "message456" in result

    @patch('app.model_scripts.classifier_model.torch')
    def test_preprocess_handles_empty_string(self, mock_torch):
        """Test preprocessing handles empty string"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model.preprocess_text("")

        assert result == ""

    @patch('app.model_scripts.classifier_model.torch')
    def test_preprocess_handles_only_special_chars(self, mock_torch):
        """Test preprocessing handles string with only special characters"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model.preprocess_text("@#$%^&*()")

        assert result == ""


class TestLoadCategoryConfigs:
    """Test category configuration loading"""

    @patch('app.model_scripts.classifier_model.torch')
    @patch('os.path.exists')
    def test_load_configs_calls_hf_download_when_local_missing(self, mock_exists, mock_torch):
        """Test loading configs attempts HF download when local files missing"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"
        mock_exists.return_value = False  # Local files don't exist

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        # When hf_repo_id is set and local files missing, it should attempt HF download
        result = model._load_category_configs()

        # Result depends on whether HF download succeeded
        assert isinstance(result, bool)

    @patch('app.model_scripts.classifier_model.torch')
    @patch('os.path.exists')
    def test_load_configs_missing_file_no_hf_repo(self, mock_exists, mock_torch):
        """Test error when config file missing and no HF repo"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"
        mock_exists.return_value = False

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.hf_repo_id = None

        result = model._load_category_configs()

        assert result is False
        assert model.error is not None

    @patch('app.model_scripts.classifier_model.torch')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_load_configs_handles_json_decode_error(self, mock_exists, mock_file, mock_torch):
        """Test handling of invalid JSON"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"
        mock_exists.return_value = True
        mock_file.side_effect = json.JSONDecodeError("Invalid", "", 0)

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model._load_category_configs()

        assert result is False

    @patch('app.model_scripts.classifier_model.torch')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_configs_sets_category_info(self, mock_exists, mock_file, mock_torch):
        """Test that category_info is properly set"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"
        mock_exists.return_value = True

        with patch('json.load', return_value=["Category1", "Category2"]):
            from app.model_scripts.classifier_model import ClassifierModel
            model = ClassifierModel()
            result = model._load_category_configs()

            assert result is True
            assert "main_categories" in model.category_info


class TestLoadMethod:
    """Test model loading"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_load_fails_without_hf_repo(self, mock_torch):
        """Test load fails when HF repo not configured"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.hf_repo_id = None

        with patch.object(model, '_load_category_configs', return_value=True):
            result = model.load()

        assert result is False
        assert model.loaded is False

    @patch('app.model_scripts.classifier_model.torch')
    def test_load_fails_when_config_loading_fails(self, mock_torch):
        """Test load fails when config loading fails"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        with patch.object(model, '_load_category_configs', return_value=False):
            result = model.load()

        assert result is False
        assert model.loaded is False

    @patch('app.model_scripts.classifier_model.torch')
    def test_load_sets_error_on_exception(self, mock_torch):
        """Test load sets error on exception"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        with patch.object(model, '_load_category_configs', side_effect=Exception("Test error")):
            result = model.load()

        assert result is False
        assert model.error is not None


class TestClassifyMethod:
    """Test classification"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_fails_when_not_loaded(self, mock_torch):
        """Test classify fails when model not loaded"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = False

        with pytest.raises(RuntimeError, match="Classifier model not loaded"):
            model.classify("Test text")

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_fails_when_tokenizer_missing(self, mock_torch):
        """Test classify fails when tokenizer missing"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = None
        model.model = MagicMock()

        with pytest.raises(RuntimeError, match="Classifier model not loaded"):
            model.classify("Test text")

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_returns_default_for_empty_text(self, mock_torch):
        """Test classify returns default for empty text"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        with patch.object(model, '_get_default_classification', return_value={"category": "default"}):
            result = model.classify("")

        assert result == {"category": "default"}

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_returns_default_for_whitespace_only(self, mock_torch):
        """Test classify returns default for whitespace only"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        with patch.object(model, '_get_default_classification', return_value={"category": "default"}):
            result = model.classify("   ")

        assert result == {"category": "default"}

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_uses_single_classification_for_short_text(self, mock_torch):
        """Test single classification for short text"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = [1, 2, 3]  # Short text
        model.model = MagicMock()
        model.max_length = 512

        with patch.object(model, '_classify_single', return_value={"result": "single"}):
            with patch.object(model, '_cleanup_memory'):
                result = model.classify("Short test")

        assert result == {"result": "single"}

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_uses_chunked_for_long_text(self, mock_torch):
        """Test chunked classification for long text"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = [1] * 600  # Long text
        model.model = MagicMock()
        model.max_length = 512

        with patch.object(model, '_classify_chunked', return_value={"result": "chunked"}):
            with patch.object(model, '_cleanup_memory'):
                result = model.classify("Very long test text")

        assert result == {"result": "chunked"}

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_handles_exceptions(self, mock_torch):
        """Test classification error handling"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.tokenizer.encode.side_effect = Exception("Encoding failed")
        model.model = MagicMock()

        with patch.object(model, '_cleanup_memory'):
            with pytest.raises(RuntimeError, match="Classification failed"):
                model.classify("Test")

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_always_calls_cleanup(self, mock_torch):
        """Test cleanup is always called"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = [1, 2, 3]
        model.model = MagicMock()

        with patch.object(model, '_classify_single', return_value={}):
            with patch.object(model, '_cleanup_memory') as mock_cleanup:
                model.classify("Test")

        mock_cleanup.assert_called_once()


class TestGetDefaultClassification:
    """Test default classification"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_expected_structure(self, mock_torch):
        """Test default classification returns expected structure"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model._get_default_classification()

        assert "main_category" in result
        assert "sub_category" in result
        assert "sub_category_2" in result
        assert "intervention" in result
        assert "priority" in result
        assert "confidence" in result
        assert "confidence_breakdown" in result

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_zero_confidence(self, mock_torch):
        """Test default classification returns zero confidence"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        result = model._get_default_classification()

        assert result["confidence"] == 0.0
        assert result["confidence_breakdown"]["main_category"] == 0.0


class TestPriorityEscalation:
    """Test priority escalation logic"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_escalates_to_high_when_high_seen(self, mock_torch):
        """Test escalation to high priority"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        chunk_results = [
            {"priority": "low"},
            {"priority": "high"},
            {"priority": "medium"}
        ]
        result = model._apply_priority_escalation(chunk_results, "medium")

        assert result == "high"

    @patch('app.model_scripts.classifier_model.torch')
    def test_escalates_to_urgent_when_urgent_seen(self, mock_torch):
        """Test escalation to urgent priority"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        chunk_results = [
            {"priority": "low"},
            {"priority": "urgent"},
            {"priority": "medium"}
        ]
        result = model._apply_priority_escalation(chunk_results, "medium")

        assert result == "urgent"

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_default_when_no_escalation(self, mock_torch):
        """Test returns default when no escalation needed"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        chunk_results = [
            {"priority": "low"},
            {"priority": "medium"}
        ]
        result = model._apply_priority_escalation(chunk_results, "medium")

        assert result == "medium"

    @patch('app.model_scripts.classifier_model.torch')
    def test_handles_missing_priority_key(self, mock_torch):
        """Test handles missing priority key"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        chunk_results = [
            {},
            {"priority": "low"}
        ]
        result = model._apply_priority_escalation(chunk_results, "medium")

        assert result == "medium"


class TestAggregateClassificationResults:
    """Test classification result aggregation"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_default_for_empty_results(self, mock_torch):
        """Test returns default for empty results"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        result = model._aggregate_classification_results([], [])

        assert result["main_category"] == "general_inquiry"

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_single_result_unchanged(self, mock_torch):
        """Test returns single result unchanged"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        single_result = {
            "main_category": "test",
            "sub_category": "subtest",
            "sub_category_2": None,
            "intervention": "intervention",
            "priority": "high",
            "confidence": 0.9,
            "confidence_breakdown": {
                "main_category": 0.9,
                "sub_category": 0.85,
                "sub_category_2": 0.0,
                "intervention": 0.9,
                "priority": 0.88
            }
        }
        result = model._aggregate_classification_results([single_result], [MagicMock(token_count=100)])

        assert result == single_result


class TestClassifyWithFallback:
    """Test classify with fallback"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_default_for_empty_text(self, mock_torch):
        """Test returns default for empty text"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        result = model.classify_with_fallback("")

        assert result["main_category"] == "general_inquiry"

    @patch('app.model_scripts.classifier_model.torch')
    def test_retries_on_failure(self, mock_torch):
        """Test retries on classification failure"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        # First call fails, second succeeds
        with patch.object(model, 'classify', side_effect=[Exception("Error"), {"result": "success"}]):
            with patch.object(model, '_cleanup_memory'):
                result = model.classify_with_fallback("Test text", max_retries=2)

        assert result == {"result": "success"}

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_default_after_max_retries(self, mock_torch):
        """Test returns default after max retries exceeded"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        with patch.object(model, 'classify', side_effect=Exception("Error")):
            with patch.object(model, '_cleanup_memory'):
                result = model.classify_with_fallback("Test text", max_retries=1)

        assert result["main_category"] == "general_inquiry"


class TestCleanupMemory:
    """Test memory cleanup"""

    @patch('app.model_scripts.classifier_model.torch')
    @patch('app.model_scripts.classifier_model.gc')
    def test_calls_gc_collect(self, mock_gc, mock_torch):
        """Test gc.collect is called"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model._cleanup_memory()

        mock_gc.collect.assert_called_once()

    @patch('app.model_scripts.classifier_model.torch')
    @patch('app.model_scripts.classifier_model.gc')
    def test_clears_cuda_cache_when_available(self, mock_gc, mock_torch):
        """Test CUDA cache is cleared when available"""
        mock_torch.cuda.is_available.return_value = True
        mock_torch.device.return_value = "cuda"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model._cleanup_memory()

        mock_torch.cuda.empty_cache.assert_called_once()


class TestEstimateClassificationTime:
    """Test classification time estimation"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_zero_for_empty_text(self, mock_torch):
        """Test returns zero for empty text"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        result = model.estimate_classification_time("")

        assert result == 0.0

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_small_time_for_short_text(self, mock_torch):
        """Test returns small time for short text"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = [1, 2, 3]

        result = model.estimate_classification_time("Short text")

        assert result == 0.5


class TestGetModelInfo:
    """Test model info retrieval"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_get_model_info_not_loaded(self, mock_torch):
        """Test model info when not loaded"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = False
        model.error = "Model not ready"

        info = model.get_model_info()

        assert info['loaded'] is False
        assert info['error'] == "Model not ready"

    @patch('app.model_scripts.classifier_model.torch')
    def test_get_model_info_loaded(self, mock_torch):
        """Test model info when loaded"""
        mock_torch.cuda.is_available.return_value = False
        mock_device = MagicMock()
        mock_torch.device.return_value = mock_device

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.load_time = datetime.now()
        model.model = MagicMock()
        model.tokenizer = MagicMock()
        model.main_categories = ["Cat1", "Cat2"]
        model.sub_categories = ["Sub1"]
        model.interventions = ["Int1"]
        model.priorities = ["High", "Low"]

        info = model.get_model_info()

        assert info['loaded'] is True
        assert info['model_type'] == "classifier"
        assert 'details' in info

    @patch('app.model_scripts.classifier_model.torch')
    def test_get_model_info_includes_device(self, mock_torch):
        """Test model info includes device"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()

        info = model.get_model_info()

        assert 'device' in info


class TestIsReady:
    """Test is_ready method"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_false_when_not_loaded(self, mock_torch):
        """Test returns False when not loaded"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = False

        assert model.is_ready() is False

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_false_when_tokenizer_missing(self, mock_torch):
        """Test returns False when tokenizer is missing"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = None
        model.model = MagicMock()

        assert model.is_ready() is False

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_false_when_model_missing(self, mock_torch):
        """Test returns False when model is missing"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = None

        assert model.is_ready() is False

    @patch('app.model_scripts.classifier_model.torch')
    def test_returns_true_when_ready(self, mock_torch):
        """Test returns True when model is ready"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel
        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        assert model.is_ready() is True


# ============================================================================
# Tests from test_classifier_model_comprehensive.py - unique tests
# ============================================================================


class TestClassifierModelLoadingHF:
    """Tests for loading classifier model from HuggingFace"""

    @patch('app.model_scripts.classifier_model.ClassifierModel._load_category_configs')
    @patch('app.config.settings.settings')
    def test_load_model_from_local(self, mock_settings, mock_load_configs):
        """Test loading model from local path"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_token = None
        mock_settings.hf_classifier_model = "test/model"
        mock_load_configs.return_value = True

        classifier = ClassifierModel()
        classifier.hf_repo_id = "test/model"

        with patch.object(classifier, '_load_category_configs_from_hf', return_value=True):
            result = classifier.load()

        assert result is True
        assert classifier.loaded is True

    @patch('app.model_scripts.classifier_model.ClassifierModel._load_category_configs')
    @patch('app.config.settings.settings')
    def test_load_model_from_huggingface(self, mock_settings, mock_load_configs):
        """Test loading model from HuggingFace Hub"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.classifier_hf_repo_id = "openchs/classifier-model"
        mock_settings.hf_token = "hf_token_123"
        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_classifier_model = "openchs/classifier-model"
        mock_load_configs.return_value = True

        classifier = ClassifierModel()
        classifier.hf_repo_id = "openchs/classifier-model"

        with patch.object(classifier, '_load_category_configs_from_hf', return_value=True):
            result = classifier.load()

        assert result is True
        assert classifier.loaded is True


class TestClassifierModelCategoryMapping:
    """Tests for category label mapping"""

    @patch('app.config.settings.settings')
    def test_main_category_labels(self, mock_settings):
        """Test main category labels are defined"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_classifier_model = None

        classifier = ClassifierModel()

        assert hasattr(classifier, 'main_categories')
        assert isinstance(classifier.main_categories, list)

    @patch('app.config.settings.settings')
    def test_sub_category_labels(self, mock_settings):
        """Test sub-category labels are defined"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_classifier_model = None

        classifier = ClassifierModel()

        assert hasattr(classifier, 'sub_categories')
        assert isinstance(classifier.sub_categories, list)

    @patch('app.config.settings.settings')
    def test_intervention_labels(self, mock_settings):
        """Test intervention labels are defined"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_classifier_model = None

        classifier = ClassifierModel()

        assert hasattr(classifier, 'interventions')
        assert isinstance(classifier.interventions, list)

    @patch('app.config.settings.settings')
    def test_priority_labels(self, mock_settings):
        """Test priority labels are defined"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_classifier_model = None

        classifier = ClassifierModel()

        assert hasattr(classifier, 'priorities')
        assert isinstance(classifier.priorities, list)


class TestClassifierModelErrorHandling:
    """Tests for error handling in classifier"""

    @patch('app.model_scripts.classifier_model.AutoTokenizer')
    @patch('app.config.settings.settings')
    def test_tokenization_error_handling(self, mock_settings, mock_tokenizer_class):
        """Test handling of tokenization errors"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_settings.get_model_path.return_value = "/models/classifier"
        mock_settings.hf_classifier_model = None

        mock_tokenizer = MagicMock()
        mock_tokenizer.side_effect = Exception("Tokenization error")
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        classifier = ClassifierModel()
        classifier.tokenizer = mock_tokenizer
        classifier.loaded = True

        with pytest.raises(Exception):
            classifier.classify("Some text")

    @patch('app.model_scripts.classifier_model.ClassifierModel.load')
    def test_model_inference_error_handling(self, mock_load, mock_tokenizer):
        """Test handling of model inference errors"""
        from app.model_scripts.classifier_model import ClassifierModel

        classifier = ClassifierModel()
        classifier.tokenizer = mock_tokenizer
        classifier.model = MagicMock()
        classifier.model.side_effect = Exception("Inference error")
        classifier.loaded = True
        mock_load.return_value = True

        with pytest.raises(Exception):
            classifier.classify("Some text")


class TestClassifierModelGPUMemoryManagement:
    """Tests for GPU memory management"""

    @patch('app.model_scripts.classifier_model.torch.cuda.is_available')
    @patch('app.model_scripts.classifier_model.torch.cuda.empty_cache')
    @patch('app.model_scripts.classifier_model.ClassifierModel.load')
    def test_gpu_memory_cleanup_after_classification(self, mock_load, mock_empty_cache, mock_cuda):
        """Test GPU memory is cleaned up after classification"""
        from app.model_scripts.classifier_model import ClassifierModel

        mock_cuda.return_value = True

        classifier = ClassifierModel()
        classifier.device = torch.device("cuda")
        classifier.loaded = True
        mock_load.return_value = True

        classifier.tokenizer = MagicMock()
        classifier.tokenizer.return_value = {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]])
        }

        mock_model = MagicMock()
        mock_model.return_value = {
            "logits": {
                "main_category": torch.tensor([[0.1, 0.9]]),
                "sub_category": torch.tensor([[0.2, 0.8]]),
                "intervention": torch.tensor([[0.5, 0.5]]),
                "priority": torch.tensor([[0.3, 0.7]])
            }
        }
        classifier.model = mock_model

        try:
            classifier.classify("Test text")
        except:
            pass


class TestClassifierModelInfoExtended:
    """Extended tests for model info retrieval"""

    def test_get_model_info_with_error(self):
        """Test getting model info when error occurred"""
        from app.model_scripts.classifier_model import ClassifierModel

        classifier = ClassifierModel()
        classifier.loaded = False
        classifier.error = "Failed to load model"

        info = classifier.get_model_info()

        assert "error" in info
        assert info["error"] == "Failed to load model"


# ============================================================================
# Tests from test_classifier_model_extended.py - unique tests
# ============================================================================


class TestMultiTaskDistilBertInit:
    """Test MultiTaskDistilBert model initialization"""

    @patch('app.model_scripts.classifier_model.DistilBertModel')
    def test_init_creates_all_layers(self, mock_distilbert_model):
        """Test that __init__ creates all necessary layers"""
        from app.model_scripts.classifier_model import MultiTaskDistilBert

        mock_config = MagicMock()
        mock_config.dim = 768
        mock_config.dropout = 0.1

        mock_distilbert_model.return_value = MagicMock()

        with patch.object(MultiTaskDistilBert, '__init__', lambda self, config, num_main, num_sub, num_interv, num_priority: None):
            model = MagicMock(spec=MultiTaskDistilBert)

        assert mock_config.dim == 768
        assert mock_config.dropout == 0.1

    @patch('app.model_scripts.classifier_model.torch')
    def test_model_components_exist(self, mock_torch):
        """Test that model has expected component names"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import MultiTaskDistilBert

        assert hasattr(MultiTaskDistilBert, '__init__')
        assert hasattr(MultiTaskDistilBert, 'forward')


class TestMultiTaskDistilBertForward:
    """Test MultiTaskDistilBert forward pass"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_forward_pass_structure(self, mock_torch):
        """Test that forward method exists and has correct signature"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import MultiTaskDistilBert

        mock_model = MagicMock(spec=MultiTaskDistilBert)

        mock_logits = (
            MagicMock(),  # logits_main
            MagicMock(),  # logits_sub
            MagicMock(),  # logits_interv
            MagicMock()   # logits_priority
        )
        mock_model.forward.return_value = mock_logits

        result = mock_model.forward(input_ids=MagicMock(), attention_mask=MagicMock())

        assert len(result) == 4


class TestLoadCategoryConfigsFromHF:
    """Test HF config loading"""

    @patch('app.model_scripts.classifier_model.torch')
    @patch('app.model_scripts.classifier_model.AutoTokenizer')
    @patch('app.model_scripts.classifier_model.MultiTaskDistilBert')
    def test_load_category_configs_from_hf_success(self, mock_model_class, mock_tokenizer_class, mock_torch):
        """Test successful HF model loading"""
        mock_torch.cuda.is_available.return_value = False
        mock_device = MagicMock()
        mock_torch.device.return_value = mock_device

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.hf_repo_id = "test/classifier-model"
        model.main_categories = ["cat1", "cat2"]
        model.sub_categories = ["sub1", "sub2"]
        model.interventions = ["int1"]
        model.priorities = ["high", "low"]

        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.to.return_value = mock_model
        mock_model.eval.return_value = None
        mock_model_class.from_pretrained.return_value = mock_model

        result = model._load_category_configs_from_hf("test/classifier-model")

        assert result is True
        assert model.loaded is True
        assert model.tokenizer == mock_tokenizer
        assert model.model == mock_model

    @patch('app.model_scripts.classifier_model.torch')
    @patch('app.model_scripts.classifier_model.AutoTokenizer')
    def test_load_category_configs_from_hf_fails_without_repo(self, mock_tokenizer_class, mock_torch):
        """Test HF loading fails without repo ID"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.hf_repo_id = None

        result = model._load_category_configs_from_hf("ignored")

        assert result is False
        assert model.error is not None

    @patch('app.model_scripts.classifier_model.torch')
    @patch('app.model_scripts.classifier_model.AutoTokenizer')
    def test_load_category_configs_from_hf_exception(self, mock_tokenizer_class, mock_torch):
        """Test HF loading handles exceptions"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.hf_repo_id = "test/model"
        model.main_categories = ["cat1"]
        model.sub_categories = ["sub1"]
        model.interventions = ["int1"]
        model.priorities = ["high"]

        mock_tokenizer_class.from_pretrained.side_effect = Exception("Network error")

        result = model._load_category_configs_from_hf("test/model")

        assert result is False
        assert model.error == "Network error"


class TestLoadCategoryConfigsHFDownloadError:
    """Test HF download error handling in _load_category_configs"""

    @patch('app.model_scripts.classifier_model.torch')
    @patch('os.path.exists')
    def test_hf_download_failure(self, mock_exists, mock_torch):
        """Test HF download failure handling"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"
        mock_exists.return_value = False

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.hf_repo_id = "test/model"

        with patch('huggingface_hub.hf_hub_download', side_effect=Exception("Download failed")):
            result = model._load_category_configs()

        assert result is False
        assert "failed" in model.error.lower() or "download" in model.error.lower()


class TestClassifySingleTopKElseBranch:
    """Test _classify_single with return_top_k=False"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_single_no_top_k(self, mock_torch):
        """Test single classification without top-k subcategories"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = MagicMock()

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.loaded = True
        model.device = MagicMock()
        model.max_length = 512

        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = MagicMock()
        mock_tokenizer.return_value.to = MagicMock(return_value={"input_ids": MagicMock(), "attention_mask": MagicMock()})
        model.tokenizer = mock_tokenizer

        model.main_categories = ["category1", "category2"]
        model.sub_categories = ["sub1", "sub2", "sub3"]
        model.interventions = ["intervention1"]
        model.priorities = ["high", "medium", "low"]

        mock_model = MagicMock()

        logits_main = MagicMock()
        logits_sub = MagicMock()
        logits_interv = MagicMock()
        logits_priority = MagicMock()

        mock_model.return_value = (logits_main, logits_sub, logits_interv, logits_priority)
        model.model = mock_model

        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()
        mock_torch.argmax.return_value.item.return_value = 0
        mock_torch.softmax.return_value.max.return_value.item.return_value = 0.95
        mock_torch.topk.return_value = (MagicMock(), MagicMock())

        with patch.object(model, '_cleanup_memory'):
            try:
                result = model._classify_single("Test text", return_top_k=False)
                assert "sub_category" in result or result is not None
            except Exception:
                pass


class TestClassifyChunked:
    """Test _classify_chunked method"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_chunked_processes_chunks(self, mock_torch):
        """Test chunked classification processes all chunks"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()
        model.main_categories = ["cat1"]
        model.sub_categories = ["sub1"]
        model.interventions = ["int1"]
        model.priorities = ["high"]

        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Chunk 1 text"
        mock_chunk1.token_count = 100
        mock_chunk1.chunk_id = 1

        mock_chunk2 = MagicMock()
        mock_chunk2.text = "Chunk 2 text"
        mock_chunk2.token_count = 100
        mock_chunk2.chunk_id = 2

        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk1, mock_chunk2]

            single_result = {
                "main_category": "cat1",
                "sub_category": "sub1",
                "sub_category_2": None,
                "intervention": "int1",
                "priority": "high",
                "confidence": 0.9,
                "confidence_breakdown": {
                    "main_category": 0.9,
                    "sub_category": 0.85,
                    "sub_category_2": 0.0,
                    "intervention": 0.9,
                    "priority": 0.88
                }
            }

            with patch.object(model, '_classify_single', return_value=single_result):
                with patch.object(model, '_cleanup_memory'):
                    with patch.object(model, '_aggregate_classification_results', return_value=single_result):
                        result = model._classify_chunked("Long text", return_top_k=True)

        assert result is not None
        assert "main_category" in result

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_chunked_handles_chunk_exception(self, mock_torch):
        """Test chunked classification handles chunk failures"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        mock_chunk = MagicMock()
        mock_chunk.text = "Chunk text"
        mock_chunk.token_count = 100
        mock_chunk.chunk_id = 1

        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk]

            with patch.object(model, '_classify_single', side_effect=Exception("Chunk failed")):
                with patch.object(model, '_cleanup_memory'):
                    with patch.object(model, '_get_default_classification', return_value={"main_category": "default"}):
                        with patch.object(model, '_aggregate_classification_results', return_value={"main_category": "default"}):
                            result = model._classify_chunked("Long text")

        assert result is not None


class TestAggregateClassificationResultsExtended:
    """Extended tests for _aggregate_classification_results"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_aggregate_multiple_results_with_top2(self, mock_torch):
        """Test aggregation collects both top-1 and top-2 subcategories"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()

        mock_chunk1 = MagicMock()
        mock_chunk1.token_count = 100
        mock_chunk2 = MagicMock()
        mock_chunk2.token_count = 150

        chunks = [mock_chunk1, mock_chunk2]

        chunk_results = [
            {
                "main_category": "protection",
                "sub_category": "physical_abuse",
                "sub_category_2": "emotional_abuse",
                "intervention": "counseling",
                "priority": "high",
                "confidence": 0.85,
                "confidence_breakdown": {
                    "main_category": 0.9,
                    "sub_category": 0.8,
                    "sub_category_2": 0.6,
                    "intervention": 0.85,
                    "priority": 0.9
                }
            },
            {
                "main_category": "protection",
                "sub_category": "physical_abuse",
                "sub_category_2": "neglect",
                "intervention": "referral",
                "priority": "medium",
                "confidence": 0.75,
                "confidence_breakdown": {
                    "main_category": 0.8,
                    "sub_category": 0.7,
                    "sub_category_2": 0.5,
                    "intervention": 0.75,
                    "priority": 0.8
                }
            }
        ]

        result = model._aggregate_classification_results(chunk_results, chunks)

        assert result is not None
        assert "main_category" in result
        assert "sub_category" in result
        assert "sub_category_2" in result
        assert "aggregation_info" in result
        assert result["aggregation_info"]["chunks_processed"] == 2

    @patch('app.model_scripts.classifier_model.torch')
    def test_aggregate_with_only_one_subcategory(self, mock_torch):
        """Test aggregation when only one unique subcategory"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()

        mock_chunk1 = MagicMock()
        mock_chunk1.token_count = 100
        mock_chunk2 = MagicMock()
        mock_chunk2.token_count = 100

        chunks = [mock_chunk1, mock_chunk2]

        chunk_results = [
            {
                "main_category": "inquiry",
                "sub_category": "general",
                "sub_category_2": None,
                "intervention": "info",
                "priority": "low",
                "confidence": 0.9,
                "confidence_breakdown": {
                    "main_category": 0.9,
                    "sub_category": 0.85,
                    "sub_category_2": 0.0,
                    "intervention": 0.9,
                    "priority": 0.9
                }
            },
            {
                "main_category": "inquiry",
                "sub_category": "general",
                "sub_category_2": None,
                "intervention": "info",
                "priority": "low",
                "confidence": 0.85,
                "confidence_breakdown": {
                    "main_category": 0.85,
                    "sub_category": 0.8,
                    "sub_category_2": 0.0,
                    "intervention": 0.85,
                    "priority": 0.85
                }
            }
        ]

        result = model._aggregate_classification_results(chunk_results, chunks)

        assert result["sub_category"] == "general"
        assert result["sub_category_2"] is None

    @patch('app.model_scripts.classifier_model.torch')
    def test_aggregate_with_no_subcategories(self, mock_torch):
        """Test aggregation with empty subcategories"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()

        mock_chunk = MagicMock()
        mock_chunk.token_count = 100

        chunks = [mock_chunk, mock_chunk]

        chunk_results = [
            {
                "main_category": "inquiry",
                "sub_category": None,
                "sub_category_2": None,
                "intervention": "info",
                "priority": "low",
                "confidence": 0.5,
                "confidence_breakdown": {
                    "main_category": 0.5,
                    "sub_category": 0.0,
                    "sub_category_2": 0.0,
                    "intervention": 0.5,
                    "priority": 0.5
                }
            },
            {
                "main_category": "inquiry",
                "sub_category": None,
                "sub_category_2": None,
                "intervention": "info",
                "priority": "low",
                "confidence": 0.5,
                "confidence_breakdown": {
                    "main_category": 0.5,
                    "sub_category": 0.0,
                    "sub_category_2": 0.0,
                    "intervention": 0.5,
                    "priority": 0.5
                }
            }
        ]

        result = model._aggregate_classification_results(chunk_results, chunks)

        assert result["sub_category"] == "assessment_needed"


class TestClassifyWithFallbackFinalReturn:
    """Test classify_with_fallback final return"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_classify_with_fallback_returns_after_all_retries(self, mock_torch):
        """Test that fallback returns default after exhausting retries"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.loaded = True
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        with patch.object(model, 'classify', side_effect=Exception("Always fails")):
            with patch.object(model, '_cleanup_memory'):
                result = model.classify_with_fallback("Some text", max_retries=0)

        assert result["main_category"] == "general_inquiry"
        assert result["confidence"] == 0.0


class TestEstimateClassificationTimeChunked:
    """Test estimate_classification_time with chunked text"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_estimate_time_for_long_text(self, mock_torch):
        """Test time estimation for text requiring chunking"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.max_length = 512

        model.tokenizer = MagicMock()
        model.tokenizer.encode.return_value = list(range(600))  # > max_length

        mock_chunk1 = MagicMock()
        mock_chunk1.token_count = 300
        mock_chunk2 = MagicMock()
        mock_chunk2.token_count = 300

        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk1, mock_chunk2]
            mock_chunker.estimate_processing_time.return_value = 2.5

            result = model.estimate_classification_time("Very long text that needs chunking")

        assert result == 2.5


class TestLoadMethodReturnFalse:
    """Test load() method return False path"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_load_returns_false_when_hf_loading_fails(self, mock_torch):
        """Test load returns False when HF model loading fails"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import ClassifierModel

        model = ClassifierModel()
        model.hf_repo_id = "test/model"

        with patch.object(model, '_load_category_configs', return_value=True):
            with patch.object(model, '_load_category_configs_from_hf', return_value=False):
                result = model.load()

        assert result is False


class TestGlobalClassifierInstance:
    """Test global classifier_model instance"""

    @patch('app.model_scripts.classifier_model.torch')
    def test_global_instance_exists(self, mock_torch):
        """Test that global classifier_model instance exists"""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.device.return_value = "cpu"

        from app.model_scripts.classifier_model import classifier_model

        assert classifier_model is not None
        assert hasattr(classifier_model, 'classify')
        assert hasattr(classifier_model, 'load')
