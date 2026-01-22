#!/usr/bin/env python3
"""
Check configuration settings for the agent notification system
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_configuration():
    """Check that all configuration is properly loaded"""
    
    print("🔧 Checking Configuration Settings")
    print("="*50)
    
    # Check .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file found: {env_file}")
        
        # Read and check for ASTERISK_SERVER_IP
        with open(env_file, 'r') as f:
            content = f.read()
            if 'ASTERISK_SERVER_IP' in content:
                print("✅ ASTERISK_SERVER_IP found in .env file")
            else:
                print("❌ ASTERISK_SERVER_IP not found in .env file")
    else:
        print(f"❌ .env file not found: {env_file}")
    
    # Check environment variable
    env_ip = os.getenv('ASTERISK_SERVER_IP')
    if env_ip:
        print(f"✅ Environment variable ASTERISK_SERVER_IP: {env_ip}")
    else:
        print("⚠️ Environment variable ASTERISK_SERVER_IP not set")
    
    # Check settings import
    try:
        print("\n📦 Testing settings import...")
        from app.config.settings import settings
        
        print(f"✅ Settings imported successfully")
        print(f"📍 Asterisk Server IP: {settings.asterisk_server_ip}")
        print(f"🔌 Streaming Port: {settings.streaming_port}")
        print(f"🌐 Streaming Host: {settings.streaming_host}")
        
        # Check enhanced notification service
        print("\n🤖 Testing enhanced notification service...")
        from app.services.enhanced_notification_service import enhanced_notification_service

        print(f"✅ Enhanced notification service imported")
        print(f"📡 Auth endpoint: {enhanced_notification_service.auth_endpoint_url}")
        print(f"📤 Message endpoint: {enhanced_notification_service.endpoint_url}")
        print(f"🔧 Use Base64: {enhanced_notification_service.use_base64}")
        print(f"🏢 Site ID: {enhanced_notification_service.site_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        return False

if __name__ == "__main__":
    success = check_configuration()
    
    if success:
        print("\n🎉 Configuration check passed!")
        print("All settings are properly configured.")
    else:
        print("\n⚠️ Configuration issues detected.")
        print("Please check the .env file and imports.")