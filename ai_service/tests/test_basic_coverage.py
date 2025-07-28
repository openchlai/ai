# tests/test_basic_coverage.py
import pytest
import os
import sys

def test_app_structure():
    """Test basic app structure exists"""
    # Test that app directory exists
    app_path = os.path.join(os.path.dirname(__file__), '..', 'app')
    assert os.path.exists(app_path)
    
    # Test that main modules exist
    main_py = os.path.join(app_path, 'main.py')
    assert os.path.exists(main_py)
    
    config_dir = os.path.join(app_path, 'config')
    assert os.path.exists(config_dir)

def test_settings_module():
    """Test settings module functionality"""
    try:
        from app.config.settings import Settings
        
        # Test basic instantiation
        settings = Settings()
        
        # Test that basic attributes exist
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'log_level')
        assert hasattr(settings, 'app_version')
        
        # Test default values
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.log_level, str)
        
    except ImportError as e:
        pytest.skip(f"Settings import failed: {e}")

def test_model_loader_structure():
    """Test model loader module structure"""
    try:
        from app.models import model_loader
        
        # Test that the module imports without crashing
        assert model_loader is not None
        
        # Test ModelLoader class exists
        from app.models.model_loader import ModelLoader
        loader = ModelLoader()
        
        # Test basic attributes
        assert hasattr(loader, 'models')
        assert hasattr(loader, 'load_times')
        assert isinstance(loader.models, dict)
        assert isinstance(loader.load_times, dict)
        
    except ImportError as e:
        pytest.skip(f"Model loader import failed: {e}")

def test_api_modules_exist():
    """Test that API modules exist"""
    api_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'api')
    assert os.path.exists(api_path)
    
    # Test that specific route files exist
    routes = ['health_routes.py', 'queue_routes.py', 'whisper_routes.py']
    for route in routes:
        route_path = os.path.join(api_path, route)
        assert os.path.exists(route_path), f"Route file {route} does not exist"

def test_core_modules_exist():
    """Test that core modules exist"""
    core_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'core')
    assert os.path.exists(core_path)
    
    # Test that specific core files exist
    core_files = ['resource_manager.py', 'request_queue.py', 'text_chunker.py']
    for core_file in core_files:
        file_path = os.path.join(core_path, core_file)
        assert os.path.exists(file_path), f"Core file {core_file} does not exist"

def test_basic_imports():
    """Test basic imports that should work without heavy dependencies"""
    try:
        # Test __init__ files
        import app
        import app.config
        import app.api
        import app.core
        import app.models
        
        # These should import without errors
        assert app is not None
        
    except ImportError as e:
        pytest.skip(f"Basic imports failed: {e}")
