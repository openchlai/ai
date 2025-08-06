#!/usr/bin/env python3
"""
Test script for progressive transcription and agent notification system
"""

import asyncio
import json
import time
import requests
import os
import sys
from datetime import datetime
from typing import List, Dict

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class ProgressiveSystemTester:
    """Comprehensive tester for the progressive transcription system"""
    
    def __init__(self, base_url: str = "http://localhost:8123"):
        self.base_url = base_url
        self.test_call_id = f"test_call_{int(time.time())}"
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    async def test_agent_service_health(self):
        """Test 1: Agent notification service health"""
        self.log("🔍 Testing agent notification service health...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/calls/agent-service/health")
            if 200 <= response.status_code < 300:
                data = response.json()
                self.log(f"✅ Agent service health: {data['status']}")
                if data.get('token_status', {}).get('has_token'):
                    self.log(f"🔑 Token: {data['token_status']['token_preview']}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            return False
    
    async def test_auth_token_fetch(self):
        """Test 2: Authentication token fetching"""
        self.log("🔑 Testing authentication token fetching...")
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/calls/agent-service/test-auth")
            if 200 <= response.status_code < 300:
                data = response.json()
                success = data.get('success', False)
                self.log(f"{'✅' if success else '❌'} Auth token fetch: {data.get('message')}")
                if success:
                    self.log(f"🔑 Token preview: {data.get('token_preview')}")
                return success
            else:
                self.log(f"❌ Auth test failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Auth test error: {e}")
            return False
    
    async def test_notification_sending(self):
        """Test 3: Send test notification to agent"""
        self.log("📤 Testing notification sending...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/calls/agent-service/test-notification",
                params={"call_id": self.test_call_id}
            )
            if 200 <= response.status_code < 300:
                data = response.json()
                success = data.get('success', False)
                self.log(f"{'✅' if success else '❌'} Notification send: {data.get('message')}")
                return success
            else:
                self.log(f"❌ Notification test failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Notification test error: {e}")
            return False
    
    async def simulate_progressive_call(self):
        """Test 4: Simulate a complete call with progressive transcription"""
        self.log("📞 Simulating progressive call session...")
        
        # Sample transcript segments (simulating real call)
        transcript_segments = [
            "Hello, I need help with my medical emergency.",
            "I have been experiencing severe chest pain for the last two hours.",
            "The pain is very intense and I'm having trouble breathing.",
            "I think I might be having a heart attack. Can you send an ambulance?",
            "My name is John Smith and I live at 123 Main Street.",
            "Please hurry, the pain is getting worse.",
            "Thank you for your help. I'll wait for the ambulance."
        ]
        
        try:
            # Test getting call stats before starting
            response = requests.get(f"{self.base_url}/api/v1/calls/stats")
            if 200 <= response.status_code < 300:
                stats = response.json()
                self.log(f"📊 Initial active calls: {stats['active_sessions']}")
            
            # Simulate call session with progressive updates
            from app.streaming.call_session_manager import call_session_manager
            
            # Start session
            connection_info = {
                "client_ip": "192.168.1.100",
                "timestamp": datetime.now().isoformat(),
                "test_mode": True
            }
            
            session = await call_session_manager.start_session(self.test_call_id, connection_info)
            self.log(f"🎯 Started call session: {self.test_call_id}")
            
            # Add transcript segments progressively
            cumulative_transcript = ""
            for i, segment in enumerate(transcript_segments, 1):
                cumulative_transcript += " " + segment
                
                # Add transcription to session
                await call_session_manager.add_transcription(
                    call_id=self.test_call_id,
                    transcript=segment,
                    audio_duration=5.0,  # 5 seconds per segment
                    metadata={"segment_number": i, "test_mode": True}
                )
                
                self.log(f"📝 Added segment {i}: '{segment[:50]}...'")
                
                # Test API endpoints during call
                if i == 3:  # After 3 segments, test progressive analysis
                    await self.test_progressive_analysis_endpoints()
                
                # Wait between segments (simulate real-time)
                await asyncio.sleep(2)
            
            # End the call session
            final_session = await call_session_manager.end_session(
                self.test_call_id, 
                reason="completed"
            )
            
            if final_session:
                self.log(f"✅ Call completed - Final transcript: {len(final_session.cumulative_transcript)} chars")
                self.log(f"📊 Total segments: {final_session.segment_count}")
                self.log(f"⏱️ Total duration: {final_session.total_audio_duration:.1f}s")
                return True
            else:
                self.log("❌ Failed to end call session")
                return False
                
        except Exception as e:
            self.log(f"❌ Progressive call simulation error: {e}")
            return False
    
    async def test_progressive_analysis_endpoints(self):
        """Test 5: Progressive analysis API endpoints"""
        self.log("🧠 Testing progressive analysis endpoints...")
        
        endpoints = [
            f"/api/v1/calls/{self.test_call_id}/progressive-analysis",
            f"/api/v1/calls/{self.test_call_id}/translation", 
            f"/api/v1/calls/{self.test_call_id}/entity-evolution",
            f"/api/v1/calls/{self.test_call_id}/classification-evolution"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if 200 <= response.status_code < 300:
                    data = response.json()
                    endpoint_name = endpoint.split('/')[-1]
                    self.log(f"✅ {endpoint_name}: Retrieved data successfully")
                elif response.status_code == 404:
                    self.log(f"⚠️ {endpoint.split('/')[-1]}: No data yet (expected for early call)")
                else:
                    self.log(f"❌ {endpoint.split('/')[-1]}: HTTP {response.status_code}")
            except Exception as e:
                self.log(f"❌ {endpoint.split('/')[-1]}: {e}")
    
    async def test_call_management_endpoints(self):
        """Test 6: Call management endpoints"""
        self.log("📋 Testing call management endpoints...")
        
        try:
            # Get active calls
            response = requests.get(f"{self.base_url}/api/v1/calls/active")
            if 200 <= response.status_code < 300:
                calls = response.json()
                self.log(f"✅ Active calls: {len(calls)} found")
            
            # Get call stats
            response = requests.get(f"{self.base_url}/api/v1/calls/stats")
            if 200 <= response.status_code < 300:
                stats = response.json()
                self.log(f"✅ Call stats: {stats['active_sessions']} active sessions")
                
            return True
        except Exception as e:
            self.log(f"❌ Call management test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        self.log("🚀 Starting comprehensive progressive transcription tests...")
        self.log(f"🆔 Test call ID: {self.test_call_id}")
        
        results = []
        
        # Test sequence
        tests = [
            ("Agent Service Health", self.test_agent_service_health),
            ("Auth Token Fetch", self.test_auth_token_fetch), 
            ("Notification Sending", self.test_notification_sending),
            ("Call Management", self.test_call_management_endpoints),
            ("Progressive Call Simulation", self.simulate_progressive_call)
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                result = await test_func()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                self.log(f"{status}: {test_name}")
            except Exception as e:
                self.log(f"❌ FAILED: {test_name} - {e}")
                results.append((test_name, False))
        
        # Summary
        self.log("\n" + "="*50)
        self.log("📊 TEST SUMMARY")
        self.log("="*50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status}: {test_name}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        self.log(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total

# Main execution
async def main():
    """Run the test suite"""
    tester = ProgressiveSystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Progressive transcription system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())