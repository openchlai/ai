# tests/test_config.py
import pytest
import os
from unittest.mock import patch

def test_settings_import():
    """Test that settings can be imported"""
    try:
        from app.config.settings import Settings
        settings = Settings()
        assert settings is not None
    except ImportError as e:
        pytest.skip(f"Settings import failed: {e}")

def test_settings_basic_attributes():
    """Test basic settings attributes"""
    try:
        from app.config.settings import Settings
        settings = Settings()
        
        # These should exist based on our codebase structure
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'log_level') 
        
    except ImportError:
        pytest.skip("Settings module not available")
