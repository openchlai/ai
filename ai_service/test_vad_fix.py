#!/usr/bin/env python3
"""
Test script to verify VAD import fix works correctly
"""
import sys
import os
from pathlib import Path

# Add project root to path (simulate Celery worker environment)
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_vad_import():
    """Test VAD import with fallback logic"""
    print("🧪 Testing VAD import with fallback logic...")
    
    try:
        # Test the exact same import logic as in audio_tasks.py
        try:
            from utils.voice_activity_detection import preprocess_audio_for_whisper
            print("✅ Direct import successful")
        except ImportError as e1:
            print(f"⚠️ Direct import failed: {e1}")
            print("🔄 Trying fallback import...")
            
            # Fallback: add project root to path and retry
            project_root = Path(__file__).parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from utils.voice_activity_detection import preprocess_audio_for_whisper
            print("✅ Fallback import successful")
        
        print("✅ VAD preprocessing function is accessible")
        return True
        
    except Exception as e:
        print(f"❌ VAD import completely failed: {e}")
        return False

def test_audio_processing():
    """Test audio processing simulation"""
    print("\n🎧 Testing audio processing simulation...")
    
    try:
        from utils.voice_activity_detection import preprocess_audio_for_whisper
        import numpy as np
        
        # Create test audio with high silence (like your 89.1% case)
        sample_rate = 16000
        duration = 15.0  # 15 seconds
        samples = int(sample_rate * duration)
        
        # Create audio with mostly silence (89% silence)
        audio_array = np.zeros(samples, dtype=np.float32)
        # Add some speech in the middle 11%
        speech_start = int(samples * 0.45)  # Start at 45%
        speech_end = int(samples * 0.55)    # End at 55% (10% speech)
        audio_array[speech_start:speech_end] = np.random.normal(0, 0.1, speech_end - speech_start)
        
        # Convert to PCM bytes (16-bit)
        audio_bytes = (audio_array * 32768).astype(np.int16).tobytes()
        
        print(f"🎵 Created test audio: {duration}s, {len(audio_bytes)} bytes")
        print(f"📊 Simulated silence ratio: ~89%")
        
        # Test VAD preprocessing
        result = preprocess_audio_for_whisper(audio_bytes, sample_rate)
        processed_audio_bytes, preprocessing_info = result
        
        print(f"📈 VAD Results:")
        print(f"   - Voice ratio: {preprocessing_info.get('voice_ratio', 'unknown')}")
        print(f"   - Should process: {processed_audio_bytes is not None}")
        print(f"   - Preprocessing info: {list(preprocessing_info.keys())}")
        
        if processed_audio_bytes is None:
            print("✅ VAD correctly rejected high-silence audio (would prevent hallucination)")
        else:
            print("ℹ️ VAD passed audio for transcription")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processing test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing VAD Import Fix for Celery Worker Compatibility\n")
    
    # Test 1: Import functionality
    import_success = test_vad_import()
    
    # Test 2: Audio processing functionality
    if import_success:
        processing_success = test_audio_processing()
    else:
        processing_success = False
    
    print(f"\n📋 Test Results:")
    print(f"   - VAD Import: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   - Audio Processing: {'✅ PASS' if processing_success else '❌ FAIL'}")
    
    if import_success and processing_success:
        print("\n🎯 Ready to restart Celery worker - VAD fix should work!")
        print("   Run: celery -A app.celery_app worker --loglevel=info -E --pool=solo")
    else:
        print("\n⚠️ Need to fix remaining issues before restarting Celery worker")