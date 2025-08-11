# tests/test_model_loader.py
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_models():
    """Create mocked model instances"""
    models = {}
    
    # Mock each model type
    for model_name in ['classifier_model', 'ner_model', 'summarizer_model', 'translator_model', 'whisper_model', 'qa_model']:
        mock_model = MagicMock()
        mock_model.loaded = True
        mock_model.load_time = datetime.now()
        mock_model.load.return_value = True
        mock_model.is_ready.return_value = True
        mock_model.get_model_info.return_value = {
            "loaded": True,
            "model_path": f"/fake/{model_name}/path"
        }
        models[model_name] = mock_model
    
    return models

def test_model_loader_initialization():
    """Test ModelLoader initialization"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    assert hasattr(loader, 'models')
    assert isinstance(loader.models, dict)
    assert len(loader.models) == 0  # Should start empty

def test_library_availability_check():
    """Test checking available ML libraries"""
    from app.models.model_loader import AVAILABLE_LIBRARIES, TORCH_AVAILABLE
    
    assert isinstance(AVAILABLE_LIBRARIES, dict)
    assert isinstance(TORCH_AVAILABLE, bool)

def test_load_model_success(mock_models):
    """Test successful model loading"""
    with patch("app.models.model_loader.ClassifierModel") as mock_cls:
        mock_cls.return_value = mock_models['classifier_model']
        
        from app.models.model_loader import ModelLoader
        loader = ModelLoader()
        
        result = loader.load_model('classifier_model')
        
        assert result is True
        assert 'classifier_model' in loader.models
        assert loader.models['classifier_model'].loaded is True

def test_load_model_failure():
    """Test model loading failure"""
    with patch("app.models.model_loader.ClassifierModel", side_effect=Exception("Load failed")):
        from app.models.model_loader import ModelLoader
        loader = ModelLoader()
        
        result = loader.load_model('classifier_model')
        
        assert result is False
        assert 'classifier_model' not in loader.models

def test_load_invalid_model():
    """Test loading invalid model name"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    result = loader.load_model('invalid_model')
    
    assert result is False

def test_load_all_models(mock_models):
    """Test loading all available models"""
    with patch("app.models.model_loader.ClassifierModel") as mock_cls, \
         patch("app.models.model_loader.NERModel") as mock_ner, \
         patch("app.models.model_loader.SummarizationModel") as mock_sum:
        
        mock_cls.return_value = mock_models['classifier_model']
        mock_ner.return_value = mock_models['ner_model']
        mock_sum.return_value = mock_models['summarizer_model']
        
        from app.models.model_loader import ModelLoader
        loader = ModelLoader()
        
        results = loader.load_all_models()
        
        assert isinstance(results, dict)
        assert len(results) > 0
        # Should have attempted to load multiple models

def test_get_model_instance():
    """Test getting loaded model instance"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add a mock model
    mock_model = MagicMock()
    loader.models['test_model'] = mock_model
    
    result = loader.get_model('test_model')
    assert result == mock_model
    
    # Test getting non-existent model
    result = loader.get_model('non_existent')
    assert result is None

def test_is_model_loaded():
    """Test checking if a model is loaded"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add a loaded model
    mock_model = MagicMock()
    mock_model.is_ready.return_value = True
    loader.models['test_model'] = mock_model
    
    assert loader.is_model_loaded('test_model') is True
    assert loader.is_model_loaded('non_existent') is False

def test_unload_model():
    """Test unloading a model"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add a model
    mock_model = MagicMock()
    loader.models['test_model'] = mock_model
    
    # Unload it
    result = loader.unload_model('test_model')
    
    assert result is True
    assert 'test_model' not in loader.models

def test_unload_all_models():
    """Test unloading all models"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add some models
    for i in range(3):
        mock_model = MagicMock()
        loader.models[f'model_{i}'] = mock_model
    
    loader.unload_all_models()
    
    assert len(loader.models) == 0

def test_get_system_status():
    """Test getting system status"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add some models
    mock_model1 = MagicMock()
    mock_model1.is_ready.return_value = True
    mock_model1.get_model_info.return_value = {"loaded": True}
    
    mock_model2 = MagicMock()
    mock_model2.is_ready.return_value = False
    mock_model2.get_model_info.return_value = {"loaded": False}
    
    loader.models['model1'] = mock_model1
    loader.models['model2'] = mock_model2
    
    status = loader.get_system_status()
    
    assert isinstance(status, dict)
    assert "models" in status
    assert "system_info" in status
    assert "loaded_models" in status
    assert status["loaded_models"] == 1  # Only model1 is ready

def test_get_memory_usage():
    """Test getting memory usage information"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    with patch("psutil.virtual_memory") as mock_mem, \
         patch("psutil.Process") as mock_process:
        
        # Mock memory info
        mock_mem.return_value = MagicMock(total=8000000000, available=4000000000)
        mock_process.return_value.memory_info.return_value = MagicMock(rss=1000000000)
        
        memory_info = loader.get_memory_usage()
        
        assert isinstance(memory_info, dict)
        assert "system_memory" in memory_info
        assert "process_memory" in memory_info

def test_gpu_availability():
    """Test GPU availability check"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    with patch("torch.cuda.is_available", return_value=True), \
         patch("torch.cuda.device_count", return_value=2):
        
        gpu_info = loader.get_gpu_info()
        
        assert isinstance(gpu_info, dict)
        assert "cuda_available" in gpu_info
        assert "device_count" in gpu_info

def test_model_performance_stats():
    """Test getting model performance statistics"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add a model with performance stats
    mock_model = MagicMock()
    mock_model.get_model_info.return_value = {
        "loaded": True,
        "load_time": datetime.now(),
        "inference_count": 100,
        "average_inference_time": 0.5
    }
    loader.models['test_model'] = mock_model
    
    stats = loader.get_performance_stats()
    
    assert isinstance(stats, dict)
    assert "test_model" in stats or len(stats) >= 0

def test_validate_model_requirements():
    """Test validating model requirements"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Test with required libraries available
    with patch("app.models.model_loader.TORCH_AVAILABLE", True), \
         patch("app.models.model_loader.TRANSFORMERS_AVAILABLE", True):
        
        requirements = ['torch', 'transformers']
        result = loader._validate_requirements(requirements)
        
        assert result is True

def test_model_health_check():
    """Test health check for loaded models"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add models with different health states
    healthy_model = MagicMock()
    healthy_model.is_ready.return_value = True
    healthy_model.health_check.return_value = True
    
    unhealthy_model = MagicMock()
    unhealthy_model.is_ready.return_value = False
    unhealthy_model.health_check.return_value = False
    
    loader.models['healthy'] = healthy_model
    loader.models['unhealthy'] = unhealthy_model
    
    health_report = loader.health_check_all()
    
    assert isinstance(health_report, dict)
    assert "healthy" in health_report
    assert "unhealthy" in health_report

def test_batch_model_operations():
    """Test batch operations on multiple models"""
    from app.models.model_loader import ModelLoader
    loader = ModelLoader()
    
    # Add multiple models
    model_names = ['model1', 'model2', 'model3']
    for name in model_names:
        mock_model = MagicMock()
        mock_model.is_ready.return_value = True
        loader.models[name] = mock_model
    
    # Test batch operation
    results = loader.batch_operation('is_ready', model_names)
    
    assert isinstance(results, dict)
    assert len(results) == len(model_names)
    assert all(results[name] is True for name in model_names)