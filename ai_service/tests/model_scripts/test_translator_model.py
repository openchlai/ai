import pytest
import torch
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestTranslatorModelInitialization:
    """Tests for TranslationModel initialization"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_translator_model_init(self, mock_cuda):
        """Test translator model initialization"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        model = TranslationModel()

        assert model is not None
        assert model.device == torch.device("cpu")

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_init_with_custom_path(self, mock_cuda):
        """Test initialization with custom model path"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        model = TranslationModel(model_path="/custom/path")

        assert model.model_path == "/custom/path"

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_init_sets_default_values(self, mock_cuda):
        """Test initialization sets default values"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        model = TranslationModel()

        assert model.loaded is False
        assert model.error is None
        assert model.max_length == 512
        assert model.tokenizer is None
        assert model.model is None
        assert model.target_language == "en"

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_init_uses_cuda_when_available(self, mock_cuda):
        """Test CUDA is used when available"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = True

        model = TranslationModel()

        assert model.device == torch.device("cuda")


class TestTranslatorModelLoading:
    """Tests for translator model loading"""

    @patch('app.model_scripts.translator_model.AutoTokenizer')
    @patch('app.model_scripts.translator_model.AutoModelForSeq2SeqLM')
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_load_translator_success(self, mock_getenv, mock_exists, mock_model_class, mock_tokenizer_class):
        """Test successful translator loading"""
        import os as os_module
        from app.model_scripts.translator_model import TranslationModel

        # Mock environment variable for HuggingFace model
        def getenv_side_effect(key, default=None):
            if key == "TRANSLATION_HF_REPO_ID":
                return "openchs/sw-en-opus-mt-mul-en-v1"
            return os_module.environ.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        mock_exists.return_value = True

        mock_tokenizer = MagicMock()
        mock_tokenizer.convert_tokens_to_ids.return_value = None
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.to = MagicMock(return_value=mock_model)
        mock_model_class.from_pretrained.return_value = mock_model

        translator = TranslationModel()
        result = translator.load()

        assert result is True
        assert translator.loaded is True

    @patch('app.model_scripts.translator_model.AutoTokenizer')
    def test_load_translator_failure(self, mock_tokenizer_class):
        """Test translator loading failure"""
        from app.model_scripts.translator_model import TranslationModel

        mock_tokenizer_class.from_pretrained.side_effect = Exception("Failed to load")

        translator = TranslationModel()
        result = translator.load()

        assert result is False
        assert translator.error is not None

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_load_fails_without_hf_repo(self, mock_cuda):
        """Test load fails without HF repo ID"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.hf_repo_id = None

        result = translator.load()

        assert result is False


class TestTranslatorModelTranslation:
    """Tests for translation functionality"""

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_simple_text(self, mock_load):
        """Test translation of simple text"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.device = torch.device("cpu")

        # Mock tokenizer to return a MagicMock with .to() method
        translator.tokenizer = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs
        translator.tokenizer.return_value = mock_inputs
        translator.tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # Short text
        translator.tokenizer.decode.return_value = "Translated text"

        translator.model = MagicMock()
        translator.model.generate.return_value = torch.tensor([[1, 2, 3]])

        result = translator.translate("Habari yako")

        assert result is not None
        assert isinstance(result, str)
        assert result == "Translated text"

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_empty_text(self, mock_load):
        """Test translation with empty text"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.model = MagicMock()
        translator.tokenizer = MagicMock()

        result = translator.translate("")

        assert result == ""

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_whitespace_only(self, mock_load):
        """Test translation with whitespace only"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.model = MagicMock()
        translator.tokenizer = MagicMock()

        result = translator.translate("   ")

        assert result == ""

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_model_not_loaded(self, mock_load):
        """Test translation when model not loaded"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = False

        with pytest.raises(RuntimeError, match="Translation model not loaded"):
            translator.translate("Some text")

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_long_text_chunking(self, mock_load):
        """Test translation with long text requiring chunking"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.max_length = 100
        translator.device = torch.device("cpu")

        # Mock tokenizer to return a MagicMock with .to() method
        translator.tokenizer = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs
        translator.tokenizer.return_value = mock_inputs
        translator.tokenizer.encode.return_value = [1, 2, 3]  # Short text (won't trigger chunking)
        translator.tokenizer.decode.return_value = "Translated"

        translator.model = MagicMock()
        translator.model.generate.return_value = torch.tensor([[1, 2]])

        long_text = "Habari " * 200

        result = translator.translate(long_text)

        assert result is not None
        assert result == "Translated"

    @patch('app.model_scripts.translator_model.TranslationModel.load')
    def test_translate_calls_cleanup(self, mock_load):
        """Test translation calls cleanup"""
        from app.model_scripts.translator_model import TranslationModel

        translator = TranslationModel()
        translator.loaded = True
        translator.device = torch.device("cpu")
        translator.tokenizer = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs
        translator.tokenizer.return_value = mock_inputs
        translator.tokenizer.encode.return_value = [1, 2, 3]
        translator.tokenizer.decode.return_value = "Result"
        translator.model = MagicMock()
        translator.model.generate.return_value = torch.tensor([[1, 2]])

        with patch.object(translator, '_cleanup_memory') as mock_cleanup:
            translator.translate("Test")

        mock_cleanup.assert_called_once()


class TestTranslateSingle:
    """Tests for single text translation"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_translate_single_adds_target_prefix(self, mock_cuda):
        """Test that target prefix token is added when available"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.loaded = True
        translator.device = torch.device("cpu")
        translator._target_prefix_token = ">>en<<"

        translator.tokenizer = MagicMock()
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs
        translator.tokenizer.return_value = mock_inputs
        translator.tokenizer.decode.return_value = "Translated"

        translator.model = MagicMock()
        translator.model.generate.return_value = torch.tensor([[1, 2]])

        result = translator._translate_single("Test text")

        # Verify tokenizer was called with prefix
        call_args = translator.tokenizer.call_args[0][0]
        assert ">>en<<" in call_args


class TestTranslateWithFallback:
    """Tests for translate with fallback"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_returns_none_for_empty_text(self, mock_cuda):
        """Test returns None for empty text"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        result = translator.translate_with_fallback("")

        assert result is None

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_retries_on_failure(self, mock_cuda):
        """Test retries on failure"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.loaded = True

        with patch.object(translator, 'translate', side_effect=[Exception("Error"), "Success"]):
            with patch.object(translator, '_cleanup_memory'):
                result = translator.translate_with_fallback("Test", max_retries=2)

        assert result == "Success"

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_returns_none_after_max_retries(self, mock_cuda):
        """Test returns None after max retries"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.loaded = True

        with patch.object(translator, 'translate', side_effect=Exception("Error")):
            with patch.object(translator, '_cleanup_memory'):
                result = translator.translate_with_fallback("Test", max_retries=1)

        assert result is None


class TestCombineTranslations:
    """Tests for combining translations"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_combine_empty_list(self, mock_cuda):
        """Test combining empty list"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        result = translator._combine_translations([], [])

        assert result == ""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_combine_single_item(self, mock_cuda):
        """Test combining single item"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        result = translator._combine_translations(["Single translation"], [MagicMock()])

        assert result == "Single translation"

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_combine_multiple_items(self, mock_cuda):
        """Test combining multiple items"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        result = translator._combine_translations(
            ["First part.", "Second part."],
            [MagicMock(), MagicMock()]
        )

        assert "First part" in result
        assert "Second part" in result


class TestMergeOverlappingTranslations:
    """Tests for merging overlapping translations"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_prefers_longer_translation(self, mock_cuda):
        """Test prefers longer translation"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        prev = "Short"
        current = "This is a much longer translation with more content"

        mock_chunk = MagicMock()
        result = translator._merge_overlapping_translations(prev, current, mock_chunk)

        assert result == current

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_concatenates_when_no_overlap(self, mock_cuda):
        """Test concatenates when no overlap found"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        prev = "First sentence"
        current = "Second sentence"

        mock_chunk = MagicMock()
        result = translator._merge_overlapping_translations(prev, current, mock_chunk)

        assert "First sentence" in result
        assert "Second sentence" in result


class TestCleanupMemory:
    """Tests for memory cleanup"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    @patch('app.model_scripts.translator_model.gc')
    def test_cleanup_calls_gc(self, mock_gc, mock_cuda):
        """Test cleanup calls gc.collect"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator._cleanup_memory()

        mock_gc.collect.assert_called_once()

    @patch('app.model_scripts.translator_model.torch')
    @patch('app.model_scripts.translator_model.gc')
    def test_cleanup_clears_cuda_cache(self, mock_gc, mock_torch):
        """Test cleanup clears CUDA cache when available"""
        from app.model_scripts.translator_model import TranslationModel

        mock_torch.cuda.is_available.return_value = True

        translator = TranslationModel()
        translator._cleanup_memory()

        mock_torch.cuda.empty_cache.assert_called_once()


class TestEstimateTranslationTime:
    """Tests for time estimation"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_returns_zero_for_empty(self, mock_cuda):
        """Test returns zero for empty text"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        result = translator.estimate_translation_time("")

        assert result == 0.0

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_returns_time_for_short_text(self, mock_cuda):
        """Test returns time estimate for short text"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.tokenizer = MagicMock()
        translator.tokenizer.encode.return_value = [1, 2, 3]

        result = translator.estimate_translation_time("Short text")

        assert result == 1.0


class TestTranslatorModelInfo:
    """Tests for translator model info"""

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_get_model_info_not_loaded(self, mock_cuda):
        """Test getting model info when not loaded"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.loaded = False
        translator.error = "Not loaded"

        info = translator.get_model_info()

        assert info is not None
        assert isinstance(info, dict)
        assert info["loaded"] is False
        assert info["error"] == "Not loaded"

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_get_model_info_loaded(self, mock_cuda):
        """Test getting model info when loaded"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.loaded = True
        translator.load_time = datetime.now()
        translator.model = MagicMock()
        translator.tokenizer = MagicMock()

        info = translator.get_model_info()

        assert info is not None
        assert info["loaded"] is True
        assert info["model_type"] == "translator"
        assert "details" in info

    @patch('app.model_scripts.translator_model.torch.cuda.is_available')
    def test_get_model_info_includes_target_language(self, mock_cuda):
        """Test model info includes target language"""
        from app.model_scripts.translator_model import TranslationModel

        mock_cuda.return_value = False

        translator = TranslationModel()
        translator.loaded = True
        translator.model = MagicMock()
        translator.tokenizer = MagicMock()

        info = translator.get_model_info()

        assert "details" in info
        assert info["details"]["target_language"] == "en"
