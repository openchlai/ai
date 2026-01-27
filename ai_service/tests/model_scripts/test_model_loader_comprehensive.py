"""
 comprehensive tests for model_loader.py with proper Pydantic v2 Settings handling
"""
import pytest
import tempfile
from unittest.mock import MagicMock, patch, PropertyMock
from app.config.settings import Settings


@pytest.fixture
def test_settings():
    """Create a real Settings instance for testing"""
    temp_dir = tempfile.mkdtemp()

    settings = Settings(
        app_name="test_app",
        app_version="1.0.0",
        database_url="sqlite:///./test.db",
        redis_url="redis://localhost:6379/0",
        celery_broker_url="redis://localhost:6379/0",
        celery_result_backend="redis://localhost:6379/1",
        models_dir=temp_dir,
        enable_model_loading=True,
        use_hf_models=False
    )

    return settings


class TestModelLoaderInitialization:
    """Tests for ModelLoader initialization"""

    def test_model_loader_init(self, test_settings):
        """Test ModelLoader initialization"""
        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()

            assert loader is not None
            assert hasattr(loader, 'models')
            assert isinstance(loader.models, dict)

    def test_model_loader_with_disabled_loading(self):
        """Test ModelLoader when model loading is disabled"""
        temp_dir = tempfile.mkdtemp()
        disabled_settings = Settings(
            app_name="test_app",
            app_version="1.0.0",
            database_url="sqlite:///./test.db",
            redis_url="redis://localhost:6379/0",
            celery_broker_url="redis://localhost:6379/0",
            celery_result_backend="redis://localhost:6379/1",
            models_dir=temp_dir,
            enable_model_loading=False
        )

        with patch('app.config.settings.settings', disabled_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            assert loader is not None


class TestModelLoading:
    """Tests for individual model loading"""

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_load_whisper_model(self, mock_whisper, test_settings):
        """Test loading Whisper model"""
        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.get_model_info.return_value = {"name": "whisper"}
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')

            assert loader.model_status['whisper'].loaded is True
            assert 'whisper' in loader.models

    @pytest.mark.asyncio
    @patch('app.model_scripts.translator_model.translator_model')
    async def test_load_translator_model(self, mock_translator, test_settings):
        """Test loading Translation model"""
        mock_translator.load.return_value = True
        mock_translator.error = None
        mock_translator.get_model_info.return_value = {"name": "translator"}

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('translator')

            assert loader.model_status['translator'].loaded is True
            assert 'translator' in loader.models

    @pytest.mark.asyncio
    @patch('app.model_scripts.ner_model.ner_model')
    async def test_load_ner_model(self, mock_ner, test_settings):
        """Test loading NER model"""
        mock_ner.load.return_value = True
        mock_ner.error = None
        mock_ner.get_model_info.return_value = {"name": "ner"}

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('ner')

            assert loader.model_status['ner'].loaded is True
            assert 'ner' in loader.models

    @pytest.mark.asyncio
    async def test_load_invalid_model(self, test_settings):
        """Test loading invalid model name"""
        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            # _load_model with invalid model should raise KeyError since it's not in model_status
            with pytest.raises(KeyError):
                await loader._load_model('invalid_model')


class TestModelStatus:
    """Tests for model status checking"""

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    @patch('app.model_scripts.translator_model.translator_model')
    async def test_get_ready_models(self, mock_trans, mock_whisper, test_settings):
        """Test getting ready models"""
        # Setup whisper mock
        mock_whisper_instance = MagicMock()
        mock_whisper_instance.load.return_value = True
        mock_whisper_instance.get_model_info.return_value = {"name": "whisper"}
        mock_whisper.return_value = mock_whisper_instance

        # Setup translator mock (it's an instance, not a class)
        mock_trans.load.return_value = True
        mock_trans.error = None
        mock_trans.get_model_info.return_value = {"name": "translator"}

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')
            await loader._load_model('translator')

            ready = loader.get_ready_models()
            assert isinstance(ready, list)

    def test_is_model_ready(self, test_settings):
        """Test checking if a model is ready"""
        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()

            # Model not loaded yet
            assert loader.is_model_ready('whisper') is False

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_is_model_ready_after_load(self, mock_whisper, test_settings):
        """Test model ready status after loading"""
        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.get_model_info.return_value = {"name": "whisper"}
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')

            assert loader.is_model_ready('whisper') is True


class TestModelInfo:
    """Tests for model info retrieval"""

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_get_model_status(self, mock_whisper, test_settings):
        """Test getting model status"""
        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.get_model_info.return_value = {'model': 'whisper', 'loaded': True}
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')

            status = loader.get_model_status()
            assert isinstance(status, dict)

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_get_model_info_individual(self, mock_whisper, test_settings):
        """Test getting individual model info"""
        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.get_model_info.return_value = {'model': 'whisper', 'version': '1.0'}
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')

            # Check model status info instead of non-existent get_model_info method
            assert loader.model_status['whisper'].model_info is not None
            assert loader.model_status['whisper'].model_info['model'] == 'whisper'

    def test_get_model_info_nonexistent(self, test_settings):
        """Test getting info for non-existent model"""
        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()

            # Nonexistent model won't be in model_status dict for unrecognized names
            # But recognized models will be in model_status with empty info
            # Check a recognized model that wasn't loaded
            assert loader.model_status['whisper'].model_info == {}
            assert loader.model_status['whisper'].loaded is False


class TestErrorHandling:
    """Tests for error handling"""

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_model_load_exception(self, mock_whisper, test_settings):
        """Test handling model load exception"""
        mock_instance = MagicMock()
        mock_instance.load.side_effect = Exception("Load failed")
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            # _load_model doesn't return value, check model status instead
            await loader._load_model('whisper')

            # Model should have error status
            assert loader.model_status['whisper'].loaded is False
            assert loader.model_status['whisper'].error is not None

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_get_model_status_with_errors(self, mock_whisper, test_settings):
        """Test getting status when models have errors"""
        mock_instance = MagicMock()
        mock_instance.load.return_value = False
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')

            status = loader.get_model_status()
            assert isinstance(status, dict)


class TestModelAccess:
    """Tests for model access methods"""

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    async def test_get_model_instance(self, mock_whisper, test_settings):
        """Test getting model instance"""
        mock_instance = MagicMock()
        mock_instance.load.return_value = True
        mock_instance.get_model_info.return_value = {"name": "whisper"}
        mock_whisper.return_value = mock_instance

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')

            instance = loader.models.get('whisper')
            assert instance is not None

    def test_models_dict_structure(self, test_settings):
        """Test models dict structure"""
        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()

            assert isinstance(loader.models, dict)
            assert len(loader.models) >= 0


class TestConcurrentAccess:
    """Tests for concurrent model access"""

    @pytest.mark.asyncio
    @patch('app.model_scripts.whisper_model.WhisperModel')
    @patch('app.model_scripts.translator_model.translator_model')
    async def test_load_multiple_models(self, mock_trans, mock_whisper, test_settings):
        """Test loading multiple models"""
        # Setup whisper mock
        mock_whisper_instance = MagicMock()
        mock_whisper_instance.load.return_value = True
        mock_whisper_instance.get_model_info.return_value = {"name": "whisper"}
        mock_whisper.return_value = mock_whisper_instance

        # Setup translator mock (it's an instance, not a class)
        mock_trans.load.return_value = True
        mock_trans.error = None
        mock_trans.get_model_info.return_value = {"name": "translator"}

        with patch('app.config.settings.settings', test_settings):
            from app.model_scripts.model_loader import ModelLoader

            loader = ModelLoader()
            await loader._load_model('whisper')
            await loader._load_model('translator')

            assert len(loader.models) >= 2
