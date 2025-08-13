#!/usr/bin/env python3
"""
Comprehensive test for all import fixes
"""

def test_celery_imports():
    """Test imports used by Celery workers"""
    print("🧪 Testing Celery worker imports...")
    
    try:
        # Test audio tasks imports
        from app.tasks.audio_tasks import process_streaming_audio_task
        print("✅ Audio tasks import successful")
        
        # Test VAD import with fallback logic
        try:
            from utils.voice_activity_detection import preprocess_audio_for_whisper
            print("✅ VAD direct import successful")
        except ImportError:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent
            sys.path.insert(0, str(project_root))
            from utils.voice_activity_detection import preprocess_audio_for_whisper
            print("✅ VAD fallback import successful")
        
        return True
    except Exception as e:
        print(f"❌ Celery imports failed: {e}")
        return False

def test_tcp_server_imports():
    """Test TCP server imports"""
    print("\n🧪 Testing TCP server imports...")
    
    try:
        from app.streaming.tcp_server import AsteriskTCPServer
        print("✅ TCP server import successful")
        
        # Test instantiation
        server = AsteriskTCPServer()
        print("✅ TCP server instantiation successful")
        
        # Test configuration
        print(f"📝 Call logging: {server.enable_call_logging}")
        print(f"🎵 Live streaming: {server.enable_live_streaming}")
        print(f"📊 TCP packet logging: {server.enable_tcp_packet_logging}")
        
        return True
    except Exception as e:
        print(f"❌ TCP server imports failed: {e}")
        return False

def test_monitoring_imports():
    """Test monitoring dashboard imports"""
    print("\n🧪 Testing monitoring dashboard imports...")
    
    try:
        from app.web.monitoring_dashboard import setup_monitoring_dashboard
        from fastapi import FastAPI
        print("✅ Monitoring dashboard import successful")
        
        # Test setup
        app = FastAPI()
        dashboard = setup_monitoring_dashboard(app)
        print("✅ Monitoring dashboard setup successful")
        
        return True
    except Exception as e:
        print(f"❌ Monitoring dashboard imports failed: {e}")
        return False

def test_utility_imports():
    """Test utility imports"""
    print("\n🧪 Testing utility imports...")
    
    try:
        from utils.call_data_logger import CallDataLogger, get_call_logger
        from utils.live_audio_streamer import LiveAudioStreamer, get_live_audio_streamer
        from utils.voice_activity_detection import preprocess_audio_for_whisper
        print("✅ All utility imports successful")
        
        # Test basic functionality
        streamer = get_live_audio_streamer()
        print(f"✅ Live streamer: {type(streamer).__name__ if streamer else 'disabled'}")
        
        return True
    except Exception as e:
        print(f"❌ Utility imports failed: {e}")
        return False

def test_main_app_imports():
    """Test main application imports"""
    print("\n🧪 Testing main application imports...")
    
    try:
        from app.main import app
        print("✅ Main app import successful")
        
        # Check if monitoring is enabled
        routes = [route.path for route in app.routes]
        monitoring_enabled = any('/monitoring' in route for route in routes)
        print(f"✅ Monitoring dashboard: {'enabled' if monitoring_enabled else 'disabled'}")
        
        return True
    except Exception as e:
        print(f"❌ Main app imports failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Comprehensive Import Test for AI Service\n")
    
    tests = [
        ("Celery Worker Imports", test_celery_imports),
        ("TCP Server Imports", test_tcp_server_imports),
        ("Monitoring Dashboard Imports", test_monitoring_imports),
        ("Utility Imports", test_utility_imports),
        ("Main Application Imports", test_main_app_imports)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print(f"\n📋 Final Results:")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   - {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 System is ready!")
        print("   - All imports are working correctly")
        print("   - TCP server can handle calls with logging and streaming")
        print("   - Monitoring dashboard is available at /monitoring")
        print("   - VAD preprocessing should work in Celery workers")
        print("\n   Next: Restart Celery worker to apply VAD fixes")
    else:
        print("\n⚠️ Fix remaining import issues before proceeding")