#!/usr/bin/env python3
"""
Simulate Asterisk call with TCP audio streaming to test progressive transcription
"""

import socket
import time
import struct
import numpy as np
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class AsteriskCallSimulator:
    """Simulates Asterisk sending audio data via TCP"""
    
    def __init__(self, server_host="localhost", server_port=None):
        self.server_host = server_host
        
        # Get port from settings or use default
        if server_port is None:
            try:
                from app.config.settings import settings
                self.server_port = settings.streaming_port
                print(f"📍 Using streaming port from settings: {self.server_port}")
            except ImportError:
                self.server_port = int(os.getenv('STREAMING_PORT', '8300'))
                print(f"📍 Using streaming port from env/default: {self.server_port}")
        else:
            self.server_port = server_port
            
        self.call_id = f"1754051771.{int(time.time())}"
        
    def generate_audio_chunk(self, duration_seconds=5.0, sample_rate=16000):
        """Generate fake PCM audio data (silence with some noise)"""
        num_samples = int(duration_seconds * sample_rate)
        
        # Generate some random noise to simulate audio
        audio_data = np.random.randint(-1000, 1000, num_samples, dtype=np.int16)
        
        # Convert to bytes
        return audio_data.tobytes()
    
    def create_uid_header(self):
        """Create UID header with call ID (as Asterisk does)"""
        uid_data = self.call_id.encode('utf-8')
        # Pad to make it recognizable
        return uid_data + b'\x00' * (40 - len(uid_data))
    
    async def simulate_call(self, duration_minutes=2):
        """Simulate a complete call with progressive audio chunks"""
        print(f"🔗 Connecting to TCP server at {self.server_host}:{self.server_port}")
        print(f"📞 Simulating call ID: {self.call_id}")
        
        try:
            # Connect to TCP server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_host, self.server_port))
            print("✅ Connected to TCP server")
            
            # Send UID header first (call ID)
            uid_header = self.create_uid_header()
            sock.send(uid_header)
            print(f"📤 Sent call ID header: {self.call_id}")
            
            # Calculate total chunks
            chunk_duration = 5.0  # 5 seconds per chunk
            total_chunks = int((duration_minutes * 60) / chunk_duration)
            
            print(f"🎵 Sending {total_chunks} audio chunks ({chunk_duration}s each)")
            
            # Send audio chunks progressively
            for chunk_num in range(total_chunks):
                # Generate audio chunk
                audio_data = self.generate_audio_chunk(chunk_duration)
                
                # Send chunk
                sock.send(audio_data)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] 📤 Sent chunk {chunk_num + 1}/{total_chunks} "
                      f"({len(audio_data)} bytes)")
                
                # Wait before next chunk (simulate real-time)
                time.sleep(chunk_duration)
            
            print("✅ Finished sending all audio chunks")
            
            # Keep connection open briefly then close
            time.sleep(2)
            sock.close()
            print("🔌 Connection closed")
            
        except Exception as e:
            print(f"❌ Error during call simulation: {e}")
    
    def run_simulation(self, duration_minutes=2):
        """Run the call simulation"""
        print("🚀 Starting Asterisk call simulation...")
        print("="*50)
        
        import asyncio
        asyncio.run(self.simulate_call(duration_minutes))

if __name__ == "__main__":
    import sys
    
    # Get duration from command line or use default
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    
    simulator = AsteriskCallSimulator()
    simulator.run_simulation(duration)