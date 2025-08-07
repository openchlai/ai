#!/usr/bin/env python3
"""
Test connectivity to the agent endpoint
"""

import requests
import json
import base64
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_agent_connectivity():
    """Test connectivity to agent endpoints"""
    
    print("🔍 Testing Agent Endpoint Connectivity")
    print("="*50)
    
    # Get configuration from settings
    try:
        from app.config.settings import settings
        server_ip = settings.asterisk_server_ip
        print(f"📍 Using server IP from settings: {server_ip}")
    except ImportError:
        # Fallback to environment variable or default
        server_ip = os.getenv('ASTERISK_SERVER_IP', '192.168.8.13')
        print(f"📍 Using server IP from env/default: {server_ip}")
    
    auth_endpoint = f"https://{server_ip}/helpline/api/"
    msg_endpoint = f"https://{server_ip}/helpline/api/msg/"
    basic_auth = "dGVzdDpwQHNzdzByZA=="  # test:p@ssw0rd
    
    # Test 1: Basic connectivity
    print("1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"https://{server_ip}", verify=False, timeout=10)
        print(f"✅ Server reachable: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Server unreachable: {e}")
        return False
    
    # Test 2: Auth endpoint
    print("\n2️⃣ Testing auth endpoint...")
    try:
        headers = {"Authorization": f"Basic {basic_auth}"}
        response = requests.get(auth_endpoint, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth endpoint accessible: HTTP {response.status_code}")
            
            # Parse token
            if "ss" in data and isinstance(data["ss"], list) and len(data["ss"]) > 0:
                token = data["ss"][0][0] if len(data["ss"][0]) > 0 else None
                if token:
                    print(f"🔑 Token found: {token[:8]}...")
                    
                    # Test 3: Message endpoint with token
                    print("\n3️⃣ Testing message endpoint...")
                    return test_message_endpoint(msg_endpoint, token)
                else:
                    print("❌ No token found in response")
            else:
                print("❌ Invalid response structure")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Auth endpoint failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Auth endpoint error: {e}")
    
    return False

def test_message_endpoint(endpoint, token):
    """Test message endpoint with token"""
    try:
        # Create test message
        test_payload = {
            "update_type": "connectivity_test",
            "timestamp": "2025-08-01T12:00:00",
            "message": "Testing connectivity from AI pipeline"
        }
        
        # Encode message
        json_message = json.dumps(test_payload, ensure_ascii=False)
        encoded_message = base64.b64encode(json_message.encode('utf-8')).decode('utf-8')
        
        # Build request
        request_body = {
            "channel": "aii", 
            "session_id": "test_connectivity_123",
            "message_id": "test_msg_001",
            "timestamp": "2025-08-01T12:00:00",
            "from": "gateway",
            "mime": "application/json",
            "message": encoded_message
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            endpoint, 
            json=request_body, 
            headers=headers, 
            verify=False, 
            timeout=10
        )
        
        if 200 <= response.status_code < 300:  # Accept all 2xx success codes
            print(f"✅ Message endpoint working: HTTP {response.status_code}")
            print(f"📤 Test message sent successfully")
            return True
        else:
            print(f"❌ Message endpoint failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Message endpoint error: {e}")
        return False

if __name__ == "__main__":
    # Disable SSL warnings for self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    success = test_agent_connectivity()
    
    if success:
        print("\n🎉 All connectivity tests passed!")
        print("The agent notification system should work correctly.")
    else:
        print("\n⚠️ Connectivity issues detected.")
        print("Check network connectivity and endpoint configuration.")