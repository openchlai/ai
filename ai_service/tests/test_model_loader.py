# tests/test_model_loader.py
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

from app.model_scripts.model_loader import (
    ModelLoader,
    ModelStatus,
    AVAILABLE_LIBRARIES,
    TORCH_AVAILABLE,
    TRANSFORMERS_AVAILABLE,
    SPACY_AVAILABLE,
    LIBROSA_AVAILABLE,
    SOUNDFILE_AVAILABLE,
    SKLEARN_AVAILABLE,
    NUMPY_AVAILABLE
)


@pytest.fixture
def model_loader():
    """Create a fresh ModelLoader instance for testing"""
    return ModelLoader()


class TestModelLoaderInitialization:
    """Test ModelLoader initialization and setup"""

    def test_initialization(self, model_loader):
        """Test that ModelLoader initializes correctly"""
        assert hasattr(model_loader, 'models')
        assert hasattr(model_loader, 'model_status')
        assert hasattr(model_loader, 'model_dependencies')
        assert isinstance(model_loader.models, dict)
        assert isinstance(model_loader.model_status, dict)

    def test_model_dependencies_defined(self, model_loader):
        """Test that all expected models have dependency definitions"""
        expected_models = ['whisper', 'ner', 'classifier_model', 'translator', 'summarizer', 'qa']

        for model_name in expected_models:
            assert model_name in model_loader.model_dependencies
            assert 'required' in model_loader.model_dependencies[model_name]
            assert 'description' in model_loader.model_dependencies[model_name]

    def test_model_status_initialization(self, model_loader):
        """Test that all models have initialized status"""
        expected_models = ['whisper', 'ner', 'classifier_model', 'translator', 'summarizer', 'qa']

        for model_name in expected_models:
            assert model_name in model_loader.model_status
            status = model_loader.model_status[model_name]
            assert isinstance(status, ModelStatus)
            assert status.name == model_name
            assert status.loaded == False
            assert isinstance(status.dependencies_available, bool)
            assert isinstance(status.missing_dependencies, list)


class TestLibraryAvailability:
    """Test library availability checking"""

    def test_available_libraries_is_dict(self):
        """Test that AVAILABLE_LIBRARIES is a dictionary"""
        assert isinstance(AVAILABLE_LIBRARIES, dict)

    def test_library_flags_are_boolean(self):
        """Test that all library availability flags are boolean"""
        assert isinstance(TORCH_AVAILABLE, bool)
        assert isinstance(TRANSFORMERS_AVAILABLE, bool)
        assert isinstance(SPACY_AVAILABLE, bool)
        assert isinstance(LIBROSA_AVAILABLE, bool)
        assert isinstance(SOUNDFILE_AVAILABLE, bool)
        assert isinstance(SKLEARN_AVAILABLE, bool)
        assert isinstance(NUMPY_AVAILABLE, bool)

    def test_available_libraries_have_versions(self):
        """Test that available libraries have version info"""
        for _, version in AVAILABLE_LIBRARIES.items():
            assert isinstance(version, str)
            assert len(version) > 0


class TestDependencyChecking:
    """Test model dependency checking"""

    def test_check_model_dependencies(self, model_loader):
        """Test dependency checking for all models"""
        for model_name in model_loader.model_dependencies.keys():
            status = model_loader.model_status[model_name]

            # Status should have dependency info
            assert hasattr(status, 'dependencies_available')
            assert hasattr(status, 'missing_dependencies')

            # If dependencies available, missing should be empty
            if status.dependencies_available:
                assert len(status.missing_dependencies) == 0
            else:
                assert len(status.missing_dependencies) > 0

    def test_whisper_dependencies(self, model_loader):
        """Test Whisper model dependency requirements"""
        whisper_deps = model_loader.model_dependencies['whisper']['required']
        assert 'torch' in whisper_deps
        assert 'transformers' in whisper_deps
        assert 'librosa' in whisper_deps
        assert 'soundfile' in whisper_deps

    def test_qa_dependencies(self, model_loader):
        """Test QA model dependency requirements"""
        qa_deps = model_loader.model_dependencies['qa']['required']
        assert 'torch' in qa_deps
        assert 'transformers' in qa_deps
        assert 'numpy' in qa_deps


class TestModelStatus:
    """Test ModelStatus class"""

    def test_model_status_creation(self):
        """Test creating a ModelStatus instance"""
        status = ModelStatus("test_model")

        assert status.name == "test_model"
        assert status.loaded == False
        assert status.error is None
        assert status.load_time is None
        assert isinstance(status.model_info, dict)
        assert status.dependencies_available == False
        assert isinstance(status.missing_dependencies, list)

    def test_model_status_update(self):
        """Test updating ModelStatus fields"""
        status = ModelStatus("test_model")

        status.loaded = True
        status.error = "Test error"
        status.load_time = datetime.now()
        status.model_info = {"key": "value"}
        status.dependencies_available = True
        status.missing_dependencies = ["dep1"]

        assert status.loaded == True
        assert status.error == "Test error"
        assert status.load_time is not None
        assert status.model_info["key"] == "value"
        assert status.dependencies_available == True
        assert "dep1" in status.missing_dependencies


class TestModelLoaderQueries:
    """Test ModelLoader query methods"""

    def test_is_model_ready_when_loaded(self, model_loader):
        """Test is_model_ready returns True for loaded models"""
        # Mock a loaded model
        model_loader.model_status['test_model'] = ModelStatus('test_model')
        model_loader.model_status['test_model'].loaded = True
        model_loader.model_status['test_model'].error = None

        assert model_loader.is_model_ready('test_model') == True

    def test_is_model_ready_when_not_loaded(self, model_loader):
        """Test is_model_ready returns False for unloaded models"""
        model_loader.model_status['test_model'] = ModelStatus('test_model')
        model_loader.model_status['test_model'].loaded = False

        assert model_loader.is_model_ready('test_model') == False

    def test_is_model_ready_when_has_error(self, model_loader):
        """Test is_model_ready returns False when model has error"""
        model_loader.model_status['test_model'] = ModelStatus('test_model')
        model_loader.model_status['test_model'].loaded = True
        model_loader.model_status['test_model'].error = "Load error"

        assert model_loader.is_model_ready('test_model') == False

    def test_is_model_ready_nonexistent_model(self, model_loader):
        """Test is_model_ready returns False for non-existent model"""
        assert model_loader.is_model_ready('nonexistent_model') == False

    def test_can_implement_model(self, model_loader):
        """Test can_implement_model checks dependency availability"""
        # All real models should have dependency info
        for model_name in model_loader.model_status.keys():
            result = model_loader.can_implement_model(model_name)
            assert isinstance(result, bool)
            assert result == model_loader.model_status[model_name].dependencies_available

    def test_get_implementable_models(self, model_loader):
        """Test get_implementable_models returns list of available models"""
        implementable = model_loader.get_implementable_models()

        assert isinstance(implementable, list)
        # All returned models should have dependencies available
        for model_name in implementable:
            assert model_loader.model_status[model_name].dependencies_available == True

    def test_get_blocked_models(self, model_loader):
        """Test get_blocked_models returns models missing dependencies"""
        blocked = model_loader.get_blocked_models()

        assert isinstance(blocked, list)
        # All returned models should be missing dependencies
        for model_name in blocked:
            assert model_loader.model_status[model_name].dependencies_available == False

    def test_get_missing_dependencies_summary(self, model_loader):
        """Test get_missing_dependencies_summary returns dependency info"""
        summary = model_loader.get_missing_dependencies_summary()

        assert isinstance(summary, dict)
        # All entries should be for models missing dependencies
        for model_name, missing_deps in summary.items():
            assert isinstance(missing_deps, list)
            assert len(missing_deps) > 0
            assert model_loader.model_status[model_name].dependencies_available == False


class TestGetModelStatus:
    """Test get_model_status method"""

    def test_get_model_status_structure(self, model_loader):
        """Test that get_model_status returns proper structure"""
        status = model_loader.get_model_status()

        assert isinstance(status, dict)

        # Check all expected models are present
        expected_models = ['whisper', 'ner', 'classifier_model', 'translator', 'summarizer', 'qa']
        for model_name in expected_models:
            assert model_name in status

    def test_get_model_status_fields(self, model_loader):
        """Test that each model status has required fields"""
        status = model_loader.get_model_status()

        for _, model_info in status.items():
            assert 'loaded' in model_info
            assert 'error' in model_info
            assert 'load_time' in model_info
            assert 'dependencies_available' in model_info
            assert 'missing_dependencies' in model_info
            assert 'info' in model_info
            assert 'description' in model_info

            # Type checks
            assert isinstance(model_info['loaded'], bool)
            assert isinstance(model_info['dependencies_available'], bool)
            assert isinstance(model_info['missing_dependencies'], list)


class TestGetSystemCapabilities:
    """Test get_system_capabilities method"""

    def test_get_system_capabilities_structure(self, model_loader):
        """Test system capabilities return structure"""
        capabilities = model_loader.get_system_capabilities()

        assert isinstance(capabilities, dict)
        assert 'available_libraries' in capabilities
        assert 'models_path' in capabilities
        assert 'total_models' in capabilities
        assert 'loaded_models' in capabilities
        assert 'ready_for_implementation' in capabilities
        assert 'missing_dependencies' in capabilities
        assert 'ml_capabilities' in capabilities

    def test_system_capabilities_ml_capabilities(self, model_loader):
        """Test ML capabilities section"""
        capabilities = model_loader.get_system_capabilities()
        ml_caps = capabilities['ml_capabilities']

        assert 'gpu_processing' in ml_caps
        assert 'transformer_models' in ml_caps
        assert 'audio_processing' in ml_caps
        assert 'nlp_processing' in ml_caps
        assert 'classical_ml' in ml_caps
        assert 'numerical_computing' in ml_caps

        # All should be boolean
        for _, value in ml_caps.items():
            assert isinstance(value, bool)

    def test_system_capabilities_counts(self, model_loader):
        """Test that model counts are accurate"""
        capabilities = model_loader.get_system_capabilities()

        # Total models should match expected
        assert capabilities['total_models'] == len(model_loader.model_status)

        # Counts should be non-negative
        assert capabilities['loaded_models'] >= 0
        assert capabilities['ready_for_implementation'] >= 0
        assert capabilities['missing_dependencies'] >= 0

        # Sum should equal total
        total = capabilities['ready_for_implementation'] + capabilities['missing_dependencies']
        assert total == capabilities['total_models']


class TestLoadAllModels:
    """Test load_all_models async functionality"""

    @pytest.mark.asyncio
    async def test_load_all_models_runs(self, model_loader):
        """Test that load_all_models executes without error"""
        # Mock all model loading to avoid actual model downloads
        with patch.object(model_loader, '_load_model', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = None

            await model_loader.load_all_models()

            # Should have attempted to load all models
            assert mock_load.call_count == len(model_loader.model_status)

    @pytest.mark.asyncio
    async def test_load_model_skips_missing_dependencies(self, model_loader):
        """Test that _load_model skips models with missing dependencies"""
        # Find a model with missing dependencies
        blocked_models = model_loader.get_blocked_models()

        if len(blocked_models) > 0:
            model_name = blocked_models[0]

            # Should skip loading
            await model_loader._load_model(model_name)

            # Model should not be loaded
            assert model_loader.model_status[model_name].loaded == False

    def test_load_all_models_sync(self, model_loader):
        """Test synchronous wrapper for load_all_models"""
        with patch.object(model_loader, 'load_all_models', new_callable=AsyncMock) as mock_async:
            mock_async.return_value = None

            result = model_loader.load_all_models_sync()

            # Should return boolean
            assert isinstance(result, bool)


class TestIntegration:
    """Integration tests for ModelLoader"""

    def test_dependency_checking_consistency(self, model_loader):
        """Test that dependency checking is consistent"""
        # Blocked models should all be in missing dependencies summary
        blocked = model_loader.get_blocked_models()
        missing_summary = model_loader.get_missing_dependencies_summary()

        assert set(blocked) == set(missing_summary.keys())

    def test_implementable_and_blocked_are_disjoint(self, model_loader):
        """Test that implementable and blocked models don't overlap"""
        implementable = set(model_loader.get_implementable_models())
        blocked = set(model_loader.get_blocked_models())

        # Sets should be disjoint
        assert len(implementable.intersection(blocked)) == 0

    def test_all_models_categorized(self, model_loader):
        """Test that all models are either implementable or blocked"""
        all_models = set(model_loader.model_status.keys())
        implementable = set(model_loader.get_implementable_models())
        blocked = set(model_loader.get_blocked_models())

        # Union should equal all models
        assert implementable.union(blocked) == all_models
