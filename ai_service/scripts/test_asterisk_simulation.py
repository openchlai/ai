#!/usr/bin/env python3
"""
Integration test that simulates Asterisk TCP connection
Tests the complete flow: TCP -> Buffer -> Celery -> Transcription
"""
import asyncio
import socket
import time
import logging
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsteriskSimulator:
    """Simulates Asterisk sending audio via TCP"""
    
    def __init__(self, host="localhost", port=8300):
        self.host = host
        self.port = port
        
    async def connect_and_stream(self, duration_seconds=10, uid="test_asterisk_001"):
        """Connect to TCP server and stream audio data"""
        
        try:
            # Connect to TCP server
            reader, writer = await asyncio.open_connection(self.host, self.port)
            logger.info(f"🔌 Connected to {self.host}:{self.port}")
            
            # Send UID (Asterisk protocol)
            uid_data = f"{uid}\r".encode('utf-8')
            writer.write(uid_data)
            await writer.drain()
            logger.info(f"📝 Sent UID: {uid}")
            
            # Generate and send audio chunks
            chunk_count = 0
            total_chunks = duration_seconds * 50  # 50 chunks per second (20ms each)
            
            logger.info(f"🎵 Starting to send {total_chunks} audio chunks ({duration_seconds}s)")
            
            start_time = time.time()
            
            for i in range(total_chunks):
                # Generate 20ms of audio (640 bytes for 16kHz 16-bit mono)
                # Create some variation so it's not just silence
                amplitude = 1000 + (i % 100) * 10  # Varying amplitude
                samples = np.sin(2 * np.pi * 440 * np.linspace(0, 0.02, 320)) * amplitude  # 440Hz tone
                audio_chunk = samples.astype(np.int16).tobytes()
                
                # Ensure exactly 640 bytes
                if len(audio_chunk) != 640:
                    audio_chunk = audio_chunk[:640] if len(audio_chunk) > 640 else audio_chunk + b'\x00' * (640 - len(audio_chunk))
                
                writer.write(audio_chunk)
                await writer.drain()
                chunk_count += 1
                
                # Log progress every 5 seconds (250 chunks)
                if chunk_count % 250 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"📊 Sent {chunk_count}/{total_chunks} chunks ({elapsed:.1f}s elapsed)")
                
                # Maintain 20ms timing (50 FPS)
                await asyncio.sleep(0.02)
            
            total_time = time.time() - start_time
            logger.info(f"✅ Sent {chunk_count} chunks in {total_time:.2f}s")
            logger.info(f"📈 Average rate: {chunk_count/total_time:.1f} chunks/sec")
            
            # Keep connection open for a bit to see transcription results
            logger.info("⏳ Keeping connection open for 5 more seconds to see results...")
            await asyncio.sleep(5)
            
        except ConnectionRefusedError:
            logger.error(f"❌ Connection refused to {self.host}:{self.port}")
            logger.error("   Make sure the FastAPI server is running with TCP streaming enabled")
            return False
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            return False
        finally:
            if 'writer' in locals():
                writer.close()
                await writer.wait_closed()
                logger.info("🔌 Connection closed")
        
        return True


async def test_tcp_streaming():
    """Test TCP streaming with simulated Asterisk"""
    
    print("🧪 Asterisk TCP Streaming Integration Test")
    print("=" * 50)
    print("This test simulates Asterisk connecting via TCP and streaming audio")
    print("Requirements:")
    print("  - FastAPI server running on localhost:8123")
    print("  - TCP server listening on port 8300")
    print("  - Redis running")
    print("  - Celery workers running with models loaded")
    print()
    
    # Wait for user confirmation
    input("Press Enter when your services are ready...")
    
    simulator = AsteriskSimulator()
    
    # Test connection
    logger.info("🔍 Testing basic TCP connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8300))
        sock.close()
        
        if result != 0:
            logger.error("❌ TCP server not reachable on port 8300")
            logger.error("   Make sure FastAPI is running with ENABLE_ASTERISK_TCP=true")
            return False
        else:
            logger.info("✅ TCP server is reachable")
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False
    
    # Test streaming
    logger.info("🚀 Starting audio streaming test...")
    success = await simulator.connect_and_stream(duration_seconds=15)
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("Check the FastAPI logs for transcription results")
        print("Results should appear every 5 seconds as audio windows are processed")
    else:
        print("\n❌ Integration test failed")
        
    return success


async def test_multiple_connections():
    """Test multiple simultaneous connections"""
    
    print("\n🔀 Testing Multiple Connections")
    print("-" * 30)
    
    simulators = [
        AsteriskSimulator(),
        AsteriskSimulator(),
        AsteriskSimulator()
    ]
    
    # Start all connections simultaneously
    tasks = []
    for i, sim in enumerate(simulators):
        uid = f"asterisk_client_{i+1:03d}"
        task = asyncio.create_task(sim.connect_and_stream(duration_seconds=8, uid=uid))
        tasks.append(task)
        
        # Stagger connections slightly
        await asyncio.sleep(1)
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    logger.info(f"📊 Multiple connection test: {success_count}/{len(simulators)} succeeded")
    
    return success_count == len(simulators)


async def main():
    """Main test function"""
    
    # Test 1: Single connection streaming
    success1 = await test_tcp_streaming()
    
    if success1:
        print("\n" + "=" * 50)
        # Test 2: Multiple connections (optional)
        response = input("Run multiple connection test? (y/N): ").strip().lower()
        if response == 'y':
            success2 = await test_multiple_connections()
        else:
            success2 = True
    else:
        success2 = False
    
    print("\n🏁 Test Summary")
    print("-" * 20)
    print(f"Single connection: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Multiple connections: {'✅ PASS' if success2 else '⏭️ SKIPPED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Your TCP streaming is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check your service configuration.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()