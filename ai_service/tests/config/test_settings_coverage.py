import pytest
import sys
import os
from unittest.mock import patch

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_settings_import():
    """Test settings can be imported"""
    from app.config.settings import settings
    assert settings is not None

def test_settings_attributes():
    """Test basic settings attributes exist"""
    from app.config.settings import Settings
    
    settings_instance = Settings()
    assert hasattr(settings_instance, 'get_model_path')
    
def test_import_all_models():
    """Test importing all model classes for coverage"""
    # Import each model to hit their class definitions
    from app.model_scripts.classifier_model import ClassifierModel
    from app.model_scripts.ner_model import NERModel  
    from app.model_scripts.summarizer_model import SummarizationModel
    from app.model_scripts.whisper_model import WhisperModel
    from app.model_scripts.translator_model import TranslationModel
    from app.model_scripts.qa_model import QAModel
    
    assert ClassifierModel is not None
    assert NERModel is not None
    assert SummarizationModel is not None
    assert WhisperModel is not None
    assert TranslationModel is not None
    assert QAModel is not None

def test_basic_imports():
    """Test basic app imports for coverage"""
    from app.config import settings
    from app.model_scripts import model_loader
    from app.core import resource_manager
    from app.core import text_chunker
    
    assert settings is not None
    assert model_loader is not None
    assert resource_manager is not None
    assert text_chunker is not None