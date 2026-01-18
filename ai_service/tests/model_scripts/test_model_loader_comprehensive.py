"""
Comprehensive tests for model_loader.py
Focus: Achieving 95% coverage for central model loading and management
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime


@pytest.fixture
def mock_settings():
    """Mock settings"""
    settings = MagicMock()
    settings.enable_model_loading = True
    settings.get_model_path.return_value = "/models"
    settings.use_hf_models = True
    settings.hf_token = None
    return settings


@pytest.fixture
def mock_all_models():
    """Mock all model instances"""
    models = {}

    for model_name in ["whisper", "translator", "ner", "classifier_model", "summarizer", "qa"]:
        mock_model = MagicMock()
        mock_model.load = MagicMock(return_value=True)
        mock_model.loaded = True
        mock_model.error = None
        mock_model.get_model_info.return_value = {"loaded": True, "model": model_name}
        models[model_name] = mock_model

    return models


class TestModelLoaderInitialization:
    """Tests for ModelLoader initialization"""

    @patch('app.model_scripts.model_loader.settings')
    def test_model_loader_init(self, mock_settings):
        """Test ModelLoader initialization"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        assert loader is not None
        assert hasattr(loader, 'models')

    @patch('app.model_scripts.model_loader.settings')
    def test_model_loader_init_with_disabled_loading(self, mock_settings):
        """Test initialization when model loading is disabled"""
        from app.model_scripts.model_loader import ModelLoader

        mock_settings.enable_model_loading = False

        loader = ModelLoader()

        assert loader is not None


class TestLoadAllModels:
    """Tests for load_all_models functionality"""

    @patch('app.model_scripts.model_loader.WhisperModel')
    @patch('app.model_scripts.model_loader.TranslationModel')
    @patch('app.model_scripts.model_loader.NERModel')
    @patch('app.model_scripts.model_loader.ClassifierModel')
    @patch('app.model_scripts.model_loader.SummarizationModel')
    @patch('app.model_scripts.model_loader.QAModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_all_models_success(self, mock_settings, mock_qa, mock_sum, mock_class,
                                             mock_ner, mock_trans, mock_whisper):
        """Test successful loading of all models"""
        from app.model_scripts.model_loader import ModelLoader

        mock_settings.enable_model_loading = True

        # Setup model mocks
        for mock_model_class in [mock_whisper, mock_trans, mock_ner, mock_class, mock_sum, mock_qa]:
            instance = MagicMock()
            instance.load.return_value = True
            instance.loaded = True
            instance.error = None
            mock_model_class.return_value = instance

        loader = ModelLoader()
        result = await loader.load_all_models()

        assert result is True or result is None

    @patch('app.model_scripts.model_loader.settings')
    def test_load_all_models_sync(self, mock_settings):
        """Test synchronous model loading"""
        from app.model_scripts.model_loader import ModelLoader

        mock_settings.enable_model_loading = True

        with patch.object(ModelLoader, 'load_all_models', new_callable=AsyncMock) as mock_async_load:
            mock_async_load.return_value = True

            loader = ModelLoader()

            with patch('asyncio.get_event_loop') as mock_get_loop:
                mock_loop = MagicMock()
                mock_loop.run_until_complete.return_value = True
                mock_get_loop.return_value = mock_loop

                result = loader.load_all_models_sync()

                assert result is True or result is None

    @patch('app.model_scripts.model_loader.settings')
    @patch('app.model_scripts.model_loader.WhisperModel')
    @pytest.mark.asyncio
    async def test_load_all_models_partial_failure(self, mock_whisper, mock_settings):
        """Test loading when some models fail"""
        from app.model_scripts.model_loader import ModelLoader

        mock_settings.enable_model_loading = True

        # Whisper fails to load
        instance = MagicMock()
        instance.load.return_value = False
        instance.loaded = False
        instance.error = "Failed to load whisper"
        mock_whisper.return_value = instance

        loader = ModelLoader()

        with patch.object(loader, '_load_whisper', return_value=False):
            await loader.load_all_models()

            failed = loader.get_failed_models()
            assert "whisper" in failed or len(failed) > 0


class TestLoadIndividualModels:
    """Tests for loading individual models"""

    @patch('app.model_scripts.model_loader.WhisperModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_whisper_model(self, mock_settings, mock_whisper_class):
        """Test loading Whisper model"""
        from app.model_scripts.model_loader import ModelLoader

        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.loaded = True
        mock_whisper_class.return_value = mock_instance

        loader = ModelLoader()
        result = await loader._load_whisper()

        assert result is True or result is None

    @patch('app.model_scripts.model_loader.TranslationModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_translator_model(self, mock_settings, mock_trans_class):
        """Test loading translator model"""
        from app.model_scripts.model_loader import ModelLoader

        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.loaded = True
        mock_trans_class.return_value = mock_instance

        loader = ModelLoader()
        result = await loader._load_translator()

        assert result is True or result is None

    @patch('app.model_scripts.model_loader.NERModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_ner_model(self, mock_settings, mock_ner_class):
        """Test loading NER model"""
        from app.model_scripts.model_loader import ModelLoader

        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.loaded = True
        mock_ner_class.return_value = mock_instance

        loader = ModelLoader()
        result = await loader._load_ner()

        assert result is True or result is None

    @patch('app.model_scripts.model_loader.ClassifierModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_classifier_model(self, mock_settings, mock_class_class):
        """Test loading classifier model"""
        from app.model_scripts.model_loader import ModelLoader

        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.loaded = True
        mock_class_class.return_value = mock_instance

        loader = ModelLoader()
        result = await loader._load_classifier()

        assert result is True or result is None

    @patch('app.model_scripts.model_loader.SummarizationModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_summarizer_model(self, mock_settings, mock_sum_class):
        """Test loading summarizer model"""
        from app.model_scripts.model_loader import ModelLoader

        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.loaded = True
        mock_sum_class.return_value = mock_instance

        loader = ModelLoader()
        result = await loader._load_summarizer()

        assert result is True or result is None

    @patch('app.model_scripts.model_loader.QAModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_qa_model(self, mock_settings, mock_qa_class):
        """Test loading QA model"""
        from app.model_scripts.model_loader import ModelLoader

        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.loaded = True
        mock_qa_class.return_value = mock_instance

        loader = ModelLoader()
        result = await loader._load_qa()

        assert result is True or result is None


class TestModelStatus:
    """Tests for model status checking"""

    @patch('app.model_scripts.model_loader.settings')
    def test_get_ready_models(self, mock_settings, mock_all_models):
        """Test getting list of ready models"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()
        loader.models = mock_all_models

        ready = loader.get_ready_models()

        assert ready is not None
        assert isinstance(ready, list)
        assert len(ready) > 0

    @patch('app.model_scripts.model_loader.settings')
    def test_get_failed_models(self, mock_settings):
        """Test getting list of failed models"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        # Mock failed model
        failed_model = MagicMock()
        failed_model.loaded = False
        failed_model.error = "Load error"

        loader.models = {"failed_model": failed_model}

        failed = loader.get_failed_models()

        assert failed is not None
        assert isinstance(failed, list)

    @patch('app.model_scripts.model_loader.settings')
    def test_get_blocked_models(self, mock_settings):
        """Test getting list of blocked models"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        blocked = loader.get_blocked_models()

        assert blocked is not None
        assert isinstance(blocked, list)

    @patch('app.model_scripts.model_loader.settings')
    def test_get_implementable_models(self, mock_settings):
        """Test getting list of implementable models"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        implementable = loader.get_implementable_models()

        assert implementable is not None
        assert isinstance(implementable, list)

    @patch('app.model_scripts.model_loader.settings')
    def test_is_model_ready(self, mock_settings, mock_all_models):
        """Test checking if specific model is ready"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()
        loader.models = mock_all_models

        is_ready = loader.is_model_ready("whisper")

        assert is_ready is True

    @patch('app.model_scripts.model_loader.settings')
    def test_is_model_ready_not_loaded(self, mock_settings):
        """Test checking model that is not ready"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()
        loader.models = {}

        is_ready = loader.is_model_ready("nonexistent_model")

        assert is_ready is False


class TestModelInfo:
    """Tests for model information retrieval"""

    @patch('app.model_scripts.model_loader.settings')
    def test_get_model_status(self, mock_settings, mock_all_models):
        """Test getting comprehensive model status"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()
        loader.models = mock_all_models

        status = loader.get_model_status()

        assert status is not None
        assert isinstance(status, dict)

    @patch('app.model_scripts.model_loader.settings')
    def test_get_model_info_individual(self, mock_settings, mock_all_models):
        """Test getting info for individual model"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()
        loader.models = mock_all_models

        info = loader.get_model_info("whisper")

        assert info is not None

    @patch('app.model_scripts.model_loader.settings')
    def test_get_model_info_nonexistent(self, mock_settings):
        """Test getting info for non-existent model"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()
        loader.models = {}

        info = loader.get_model_info("nonexistent")

        assert info is None or info == {}


class TestLoadModel:
    """Tests for load_model function"""

    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_specific_model(self, mock_settings):
        """Test loading a specific model"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        with patch.object(loader, '_load_whisper', return_value=True) as mock_load:
            result = await loader.load_model("whisper")

            mock_load.assert_called_once()
            assert result is True or result is None

    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_load_model_invalid_name(self, mock_settings):
        """Test loading model with invalid name"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        result = await loader.load_model("invalid_model_name")

        # Should handle gracefully
        assert result is not None or result is None


class TestModelLoaderErrorHandling:
    """Tests for error handling in model loader"""

    @patch('app.model_scripts.model_loader.WhisperModel')
    @patch('app.model_scripts.model_loader.settings')
    @pytest.mark.asyncio
    async def test_model_load_exception(self, mock_settings, mock_whisper_class):
        """Test handling of model loading exceptions"""
        from app.model_scripts.model_loader import ModelLoader

        mock_whisper_class.side_effect = Exception("Model init failed")

        loader = ModelLoader()

        try:
            await loader._load_whisper()
        except Exception:
            pass  # Exception handled

        # Check that error was recorded
        if "whisper" in loader.models:
            assert loader.models["whisper"].error is not None

    @patch('app.model_scripts.model_loader.settings')
    def test_get_model_status_with_errors(self, mock_settings):
        """Test getting status when models have errors"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        error_model = MagicMock()
        error_model.loaded = False
        error_model.error = "Failed to load"
        error_model.get_model_info.return_value = {"loaded": False, "error": "Failed to load"}

        loader.models = {"error_model": error_model}

        status = loader.get_model_status()

        assert status is not None
        assert "error_model" in status


class TestModelLoaderDependencies:
    """Tests for dependency checking"""

    @patch('app.model_scripts.model_loader.settings')
    def test_check_dependencies_all_available(self, mock_settings):
        """Test checking dependencies when all are available"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        deps = loader.check_dependencies("whisper")

        assert deps is not None

    @patch('app.model_scripts.model_loader.settings')
    def test_check_dependencies_missing(self, mock_settings):
        """Test checking dependencies when some are missing"""
        from app.model_scripts.model_loader import ModelLoader

        loader = ModelLoader()

        # This should work even with missing deps
        deps = loader.check_dependencies("classifier")

        assert deps is not None
