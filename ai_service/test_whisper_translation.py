#!/usr/bin/env python3
"""
Test script for Whisper Large-V3 translation functionality
Compares current translation model with Whisper translation
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.model_scripts.model_loader import ModelLoader
from app.model_scripts.whisper_model import whisper_model, whisper_translation_model

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_whisper_translation():
    """Test Whisper Large-V3 translation vs current translation model"""
    
    print("🧪 Testing Whisper Large-V3 Translation")
    print("=" * 50)
    
    # Sample Swahili text for testing
    test_transcript = "Habari ya asubuhi. Nina tatizo la ndoa na mume wangu. Anakunywa pombe sana na hakunitumia heshima. Siwezi kuvumilia hali hii tena. Je, unaweza kunisaidia?"
    
    try:
        # Initialize model loader
        logger.info("📦 Loading models...")
        model_loader = ModelLoader()
        await model_loader.load_all_models()
        
        # Check model availability
        ready_models = model_loader.get_ready_models()
        print(f"✅ Ready models: {ready_models}")
        
        # Test 1: Current translation model
        print("\n📝 Test 1: Current Translation Model")
        print("-" * 30)
        
        current_translation = None
        if "translator" in ready_models:
            try:
                translator_model = model_loader.models["translator"]
                current_translation = translator_model.translate(test_transcript)
                print(f"Original (Swahili): {test_transcript}")
                print(f"Translation (Current): {current_translation}")
            except Exception as e:
                print(f"❌ Current translation failed: {e}")
        else:
            print("❌ Current translation model not available")
        
        # Test 2: Whisper translation (if available)
        print("\n🎙️ Test 2: Whisper Large-V3 Translation")
        print("-" * 35)
        
        whisper_translation = None
        if whisper_translation_model.is_ready():
            try:
                # We need audio for Whisper translation, so we'll use a text-to-speech approach
                # or simulate this test with a sample Swahili audio file
                print("⚠️  Note: Whisper translation requires audio input")
                print("For proper testing, upload a Swahili audio file through the API")
                print(f"Whisper translation model info: {whisper_translation_model.get_model_info()}")
                
                # Test model configuration
                print(f"Translation enabled: {whisper_translation_model.enable_translation}")
                print(f"Model version: {whisper_translation_model.model_version}")
                print(f"Current model ID: {whisper_translation_model.current_model_id}")
                
            except Exception as e:
                print(f"❌ Whisper translation test failed: {e}")
        else:
            print("❌ Whisper translation model not ready")
            if whisper_translation_model.error:
                print(f"Error: {whisper_translation_model.error}")
        
        # Test 3: Compare quality (if both available)
        print("\n📊 Translation Quality Comparison")
        print("-" * 32)
        
        if current_translation and whisper_translation:
            print(f"Current model:  {current_translation}")
            print(f"Whisper model:  {whisper_translation}")
            print("\n✅ Both models available for comparison")
        elif current_translation:
            print("✅ Current translation model working")
            print("⚠️  Whisper translation needs audio input for testing")
        else:
            print("❌ No translation results available")
        
        # Test 4: Model configuration check
        print("\n⚙️  Model Configuration")
        print("-" * 20)
        
        # Check if whisper_translation is in model loader
        if "whisper_translation" in model_loader.models:
            whisper_trans_model = model_loader.models["whisper_translation"]
            print(f"✅ Whisper translation model loaded in model_loader")
            print(f"   - Ready: {whisper_trans_model.is_ready()}")
            print(f"   - Translation enabled: {whisper_trans_model.enable_translation}")
            print(f"   - Model version: {whisper_trans_model.model_version}")
        else:
            print("❌ Whisper translation model not found in model_loader")
        
        # Summary
        print("\n📋 Test Summary")
        print("-" * 12)
        print(f"✅ Models ready: {len(ready_models)}")
        print(f"✅ Current translation: {'✓' if current_translation else '✗'}")
        print(f"✅ Whisper translation setup: {'✓' if whisper_translation_model.is_ready() else '✗'}")
        
        if whisper_translation_model.is_ready():
            print("\n🚀 Whisper Large-V3 translation is ready!")
            print("   To test with audio:")
            print("   1. Upload Swahili audio via /audio/process endpoint")
            print("   2. The system will automatically use Whisper for translation")
            print("   3. Compare results with previous translations")
        else:
            print("\n⚠️  Whisper translation setup incomplete")
            print("   Check model loading and dependencies")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        print(f"❌ Test execution failed: {e}")

def run_test():
    """Synchronous wrapper to run the async test"""
    try:
        asyncio.run(test_whisper_translation())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test runner failed: {e}")

if __name__ == "__main__":
    print("🧪 Starting Whisper Large-V3 Translation Test")
    print("This will test the new translation functionality\n")
    run_test()