#!/usr/bin/env python3
"""
Test script to validate HuggingFace model loading configuration
"""

import os
import sys
sys.path.append('.')

from app.config.settings import settings

def test_hf_configuration():
    """Test HuggingFace configuration setup"""
    print("🧪 Testing HuggingFace Model Configuration")
    print("=" * 50)
    
    # Test settings
    print(f"USE_HF_MODELS: {settings.use_hf_models}")
    print(f"HF_ORGANIZATION: {settings.hf_organization}")
    print(f"HF_TOKEN configured: {'Yes' if settings.hf_token else 'No'}")
    print()
    
    # Test model ID resolution
    print("🎯 Model ID Resolution:")
    print(f"Whisper Large V3: {settings._get_hf_model_id('whisper_large_v3')}")
    print(f"Whisper Large Turbo: {settings._get_hf_model_id('whisper_large_turbo')}")
    print(f"Classifier: {settings._get_hf_model_id('classifier')}")
    print(f"Translator: {settings._get_hf_model_id('translator')}")
    print()
    
    # Test active whisper path
    print("🎙️ Active Whisper Model:")
    print(f"Current variant: {settings.whisper_model_variant}")
    print(f"Active path/ID: {settings.get_active_whisper_path()}")
    print()
    
    # Test HF kwargs
    print("🔑 HuggingFace Kwargs:")
    hf_kwargs = settings.get_hf_model_kwargs()
    print(f"Token included: {'token' in hf_kwargs}")
    print(f"Kwargs: {hf_kwargs}")
    print()

def test_model_loading():
    """Test actual model loading (basic validation)"""
    print("🔄 Testing Model Loading...")
    print("=" * 50)
    
    try:
        # Test Whisper model initialization (don't actually load to save time)
        from app.model_scripts.whisper_model import WhisperModel
        whisper = WhisperModel()
        print(f"✅ Whisper model initialized")
        print(f"   - Model path/ID: {whisper.model_path}")
        print(f"   - Fallback ID: {whisper.fallback_model_id}")
        
        # Test Classifier model initialization
        from app.model_scripts.classifier_model import ClassifierModel
        classifier = ClassifierModel()
        print(f"✅ Classifier model initialized")
        print(f"   - Model path: {classifier.model_path}")
        
        # Test Translator model initialization
        from app.model_scripts.translator_model import TranslationModel
        translator = TranslationModel()
        print(f"✅ Translator model initialized")
        print(f"   - Model path: {translator.model_path}")
        
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")

def main():
    """Main test function"""
    print("🚀 HuggingFace Model Configuration Test")
    print("=" * 50)
    
    # Initialize settings paths
    settings.initialize_paths()
    
    test_hf_configuration()
    test_model_loading()
    
    print("✅ Configuration test completed!")
    print()
    print("📝 Next Steps:")
    print("1. Set your HF_ORGANIZATION in .env")
    print("2. Set your HF_TOKEN for private models in .env") 
    print("3. Update HF_*_MODEL variables with your model IDs")
    print("4. Test actual model loading with your models")

if __name__ == "__main__":
    main()