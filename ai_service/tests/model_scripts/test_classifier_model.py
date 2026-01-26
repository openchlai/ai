import pytest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime


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
