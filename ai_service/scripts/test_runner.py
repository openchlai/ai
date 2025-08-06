#!/usr/bin/env python3
"""
Test runner for real-time audio streaming
Orchestrates different types of tests
"""
import asyncio
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ FAILED - Exception: {e}")
        return False

async def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Integration Tests")
    print("=" * 50)
    
    # Check if services are running
    print("Checking service availability...")
    
    import socket
    import requests
    
    # Check FastAPI
    try:
        response = requests.get("http://localhost:8123/health", timeout=5)
        if 200 <= response.status_code < 300:
            print("✅ FastAPI server is running")
        else:
            print("⚠️ FastAPI server responded but may have issues")
    except:
        print("❌ FastAPI server not reachable on http://localhost:8123")
        print("   Start with: python -m app.main")
        return False
    
    # Check TCP port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8300))
        sock.close()
        
        if result == 0:
            print("✅ TCP server is listening on port 8300")
        else:
            print("❌ TCP server not reachable on port 8300")
            return False
    except:
        print("❌ Cannot test TCP port 8300")
        return False
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_timeout=2)
        r.ping()
        print("✅ Redis is running")
    except:
        print("❌ Redis not reachable")
        print("   Start with: redis-server")
        return False
    
    # Check Celery workers
    try:
        response = requests.get("http://localhost:8123/health/celery/status", timeout=5)
        if 200 <= response.status_code < 300:
            data = response.json()
            if data.get("workers_online", 0) > 0:
                print("✅ Celery workers are running")
            else:
                print("⚠️ No Celery workers online")
                print("   Start with: celery -A app.celery_app worker --loglevel=info")
        else:
            print("⚠️ Cannot check Celery status")
    except:
        print("⚠️ Cannot check Celery status")
    
    print("\n🚀 Running integration tests...")
    
    # Run existing streaming test
    success1 = run_command(
        "python tests/test_streaming.py",
        "HTTP SSE Streaming Test"
    )
    
    # Run TCP simulation test
    print("\n📡 TCP Streaming Test")
    print("This test will simulate Asterisk connecting via TCP")
    print("It will run automatically - watch for transcription results")
    
    try:
        from tests.test_asterisk_simulation import test_tcp_streaming
        success2 = await test_tcp_streaming()
        print(f"TCP streaming test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    except Exception as e:
        print(f"❌ TCP streaming test failed: {e}")
        success2 = False
    
    return success1 and success2

def main():
    """Main test orchestrator"""
    print("🎯 Real-time Audio Streaming Test Suite")
    print("=" * 60)
    print("This will run comprehensive tests for your streaming implementation")
    print()
    
    # Test menu
    print("Available tests:")
    print("1. Unit tests only (fast)")
    print("2. Integration tests only (requires services running)")
    print("3. All tests (unit + integration)")
    print("4. Quick service check")
    
    choice = input("\nChoose test type (1-4): ").strip()
    
    results = []
    
    if choice in ['1', '3']:  # Unit tests
        print("\n📦 Unit Tests")
        print("=" * 50)
        
        # Run pytest on streaming tests
        success = run_command(
            "python -m pytest tests/test_tcp_streaming.py -v",
            "TCP Streaming Unit Tests"
        )
        results.append(("Unit Tests", success))
        
        # Run existing tests
        success = run_command(
            "python -m pytest tests/ -v -k 'not test_asterisk_simulation'",
            "General Unit Tests"
        )
        results.append(("General Tests", success))
    
    if choice in ['2', '3']:  # Integration tests
        try:
            success = asyncio.run(run_integration_tests())
            results.append(("Integration Tests", success))
        except KeyboardInterrupt:
            print("\n⚠️ Integration tests interrupted")
            results.append(("Integration Tests", False))
    
    if choice == '4':  # Quick check
        print("\n🔍 Quick Service Check")
        print("=" * 50)
        
        import requests
        import socket
        
        services = {
            "FastAPI": ("http://localhost:8123/health", "HTTP"),
            "TCP Server": ("localhost:8300", "TCP"),
            "Redis": ("localhost:6379", "TCP")
        }
        
        for name, (addr, protocol) in services.items():
            try:
                if protocol == "HTTP":
                    response = requests.get(addr, timeout=3)
                    status = "✅ Running" if 200 <= response.status_code < 300 else "⚠️ Issues"
                else:
                    host, port = addr.split(':')
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((host, int(port)))
                    sock.close()
                    status = "✅ Running" if result == 0 else "❌ Down"
                    
                print(f"{name:12} {status}")
            except:
                print(f"{name:12} ❌ Down")
    
    # Summary
    if results:
        print("\n🏁 Test Summary")
        print("=" * 30)
        
        total_tests = len(results)
        passed_tests = sum(1 for _, success in results if success)
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name:20} {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Your streaming implementation is working correctly.")
            return 0
        else:
            print(f"\n⚠️ {total_tests - passed_tests} test suite(s) failed. Check the output above.")
            return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)