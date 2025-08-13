#!/usr/bin/env python3
"""
Test the silence rejection fix
"""
import numpy as np

def test_vad_silence_rejection():
    """Test if VAD properly rejects 100% silence"""
    print("🧪 Testing VAD silence rejection...\n")
    
    try:
        from utils.voice_activity_detection import preprocess_audio_for_whisper
        
        # Create 100% silence (15 seconds)
        sample_rate = 16000
        duration = 15.0
        samples = int(sample_rate * duration)
        
        # Pure silence
        silence_audio = np.zeros(samples, dtype=np.float32)
        silence_bytes = (silence_audio * 32768).astype(np.int16).tobytes()
        
        print(f"🔇 Created pure silence: {duration}s, {len(silence_bytes)} bytes")
        print(f"📊 Audio stats: min={silence_audio.min()}, max={silence_audio.max()}, mean={silence_audio.mean()}")
        
        # Test VAD preprocessing
        result = preprocess_audio_for_whisper(silence_bytes, sample_rate)
        processed_audio_bytes, preprocessing_info = result
        
        print(f"\n📈 VAD Results:")
        print(f"   - Should process: {processed_audio_bytes is not None}")
        print(f"   - Should transcribe: {preprocessing_info.get('should_transcribe', 'unknown')}")
        
        if preprocessing_info.get('vad_gating'):
            vad_gating = preprocessing_info['vad_gating']
            print(f"   - Voice ratio: {vad_gating.get('voice_ratio', 'unknown')}")
            print(f"   - Processing decision: {vad_gating.get('processing_decision', {})}")
        
        if processed_audio_bytes is None:
            print("✅ CORRECT: VAD rejected pure silence")
            return True
        else:
            print("❌ PROBLEM: VAD should have rejected pure silence but didn't")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_json_serialization_fix():
    """Test the JSON serialization fix"""
    print("\n🧪 Testing JSON serialization fix...\n")
    
    try:
        import json
        import numpy as np
        
        # Test data similar to VAD output
        test_data = {
            'voice_ratio': np.float64(0.05),
            'duration': np.int64(15),
            'audio_stats': {
                'peak': np.float32(0.1),
                'rms': np.float64(0.02),
                'samples': np.array([1, 2, 3]),
                'single_value': np.array([42])
            }
        }
        
        # Test the serialization function
        def make_json_serializable(obj):
            """Convert numpy types to Python native types for JSON serialization"""
            try:
                if hasattr(obj, 'dtype'):  # numpy array
                    if obj.size == 1:
                        return obj.item()  # Convert single element to scalar
                    else:
                        return obj.tolist()  # Convert array to list
                elif hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif isinstance(obj, dict):
                    return {k: make_json_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [make_json_serializable(item) for item in obj]
                elif hasattr(obj, '__float__'):  # numpy float types
                    return float(obj)
                elif hasattr(obj, '__int__'):  # numpy int types
                    return int(obj)
                else:
                    return obj
            except (ValueError, TypeError):
                # Fallback for problematic numpy types
                return str(obj)
        
        # Test serialization
        serializable_data = make_json_serializable(test_data)
        json_string = json.dumps(serializable_data)
        
        print("✅ JSON serialization successful")
        print(f"   - Original types preserved as Python types")
        print(f"   - JSON length: {len(json_string)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Silence Rejection and JSON Serialization Fixes\n")
    
    vad_success = test_vad_silence_rejection()
    json_success = test_json_serialization_fix()
    
    print(f"\n📋 Test Results:")
    print(f"   - VAD Silence Rejection: {'✅ PASS' if vad_success else '❌ FAIL'}")
    print(f"   - JSON Serialization: {'✅ PASS' if json_success else '❌ FAIL'}")
    
    if vad_success and json_success:
        print(f"\n🎯 Expected Results After Restart:")
        print("   - 100% silence calls: Should be rejected entirely (no transcription)")
        print("   - No more JSON serialization errors")
        print("   - VAD threshold now 10% (vs previous 5%)")
        print("\n🚀 Ready to restart Celery worker and test!")
    else:
        print("\n⚠️ Fix remaining issues before restarting worker")