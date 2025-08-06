#!/usr/bin/env python3
"""
WebSocket test client for Asterisk audio streaming
Tests the new WebSocket endpoint at ws://localhost:8123/audio/stream
"""
import asyncio
import websockets
import numpy as np
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsteriskWebSocketSimulator:
    """Simulates Asterisk sending audio via WebSocket"""
    
    def __init__(self, uri="ws://localhost:8123/audio/stream"):
        self.uri = uri
        
    async def connect_and_stream(self, duration_seconds=10, uid="test_ws_asterisk_001"):
        """Connect to WebSocket and stream audio data"""
        
        try:
            # Connect to WebSocket
            async with websockets.connect(self.uri) as websocket:
                logger.info(f"🔌 Connected to {self.uri}")
                
                # Send UID (Asterisk protocol - same as TCP)
                uid_data = f"{uid}\r".encode('utf-8')
                await websocket.send(uid_data)
                logger.info(f"📝 Sent UID: {uid}")
                
                # Generate and send audio chunks
                chunk_count = 0
                total_chunks = duration_seconds * 50  # 50 chunks per second (20ms each)
                
                logger.info(f"🎵 Starting to send {total_chunks} audio chunks ({duration_seconds}s)")
                
                start_time = asyncio.get_event_loop().time()
                
                for i in range(total_chunks):
                    # Generate 20ms of audio (640 bytes for 16kHz 16-bit mono)
                    # Create some variation so it's not just silence
                    amplitude = 1000 + (i % 100) * 10  # Varying amplitude
                    samples = np.sin(2 * np.pi * 440 * np.linspace(0, 0.02, 320)) * amplitude  # 440Hz tone
                    audio_chunk = samples.astype(np.int16).tobytes()
                    
                    # Ensure exactly 640 bytes
                    if len(audio_chunk) != 640:
                        audio_chunk = audio_chunk[:640] if len(audio_chunk) > 640 else audio_chunk + b'\x00' * (640 - len(audio_chunk))
                    
                    await websocket.send(audio_chunk)
                    chunk_count += 1
                    
                    # Log progress every 5 seconds (250 chunks)
                    if chunk_count % 250 == 0:
                        elapsed = asyncio.get_event_loop().time() - start_time
                        logger.info(f"📊 Sent {chunk_count}/{total_chunks} chunks ({elapsed:.1f}s elapsed)")
                    
                    # Maintain 20ms timing (50 FPS)
                    await asyncio.sleep(0.02)
                
                total_time = asyncio.get_event_loop().time() - start_time
                logger.info(f"✅ Sent {chunk_count} chunks in {total_time:.2f}s")
                logger.info(f"📈 Average rate: {chunk_count/total_time:.1f} chunks/sec")
                
                # Keep connection open for a bit to see transcription results
                logger.info("⏳ Keeping connection open for 5 more seconds to see results...")
                await asyncio.sleep(5)
                
        except websockets.exceptions.ConnectionRefused:
            logger.error(f"❌ Connection refused to {self.uri}")
            logger.error("   Make sure the FastAPI server is running on localhost:8123")
            return False
        except Exception as e:
            logger.error(f"❌ WebSocket streaming error: {e}")
            return False
        
        logger.info("🔌 WebSocket connection closed")
        return True


async def test_websocket_streaming():
    """Test WebSocket streaming with simulated Asterisk"""
    
    print("🧪 Asterisk WebSocket Streaming Test")
    print("=" * 50)
    print("This test simulates Asterisk connecting via WebSocket and streaming audio")
    print("Requirements:")
    print("  - FastAPI server running on localhost:8123")
    print("  - WebSocket endpoint /audio/stream available")
    print("  - Redis running")
    print("  - Celery workers running with models loaded")
    print()
    
    # Wait for user confirmation
    input("Press Enter when your services are ready...")
    
    simulator = AsteriskWebSocketSimulator()
    
    # Test WebSocket streaming
    logger.info("🚀 Starting WebSocket audio streaming test...")
    success = await simulator.connect_and_stream(duration_seconds=15)
    
    if success:
        print("\n✅ WebSocket streaming test completed successfully!")
        print("Check the FastAPI logs for transcription results")
        print("Results should appear every 5 seconds as audio windows are processed")
    else:
        print("\n❌ WebSocket streaming test failed")
        
    return success


async def test_multiple_websocket_connections():
    """Test multiple simultaneous WebSocket connections"""
    
    print("\n🔀 Testing Multiple WebSocket Connections")
    print("-" * 40)
    
    simulators = [
        AsteriskWebSocketSimulator(),
        AsteriskWebSocketSimulator(),
        AsteriskWebSocketSimulator()
    ]
    
    # Start all connections simultaneously
    tasks = []
    for i, sim in enumerate(simulators):
        uid = f"ws_asterisk_client_{i+1:03d}"
        task = asyncio.create_task(sim.connect_and_stream(duration_seconds=8, uid=uid))
        tasks.append(task)
        
        # Stagger connections slightly
        await asyncio.sleep(1)
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    logger.info(f"📊 Multiple WebSocket connection test: {success_count}/{len(simulators)} succeeded")
    
    return success_count == len(simulators)


async def main():
    """Main test function"""
    
    # Test 1: Single WebSocket connection streaming
    success1 = await test_websocket_streaming()
    
    if success1:
        print("\n" + "=" * 50)
        # Test 2: Multiple connections (optional)
        response = input("Run multiple WebSocket connection test? (y/N): ").strip().lower()
        if response == 'y':
            success2 = await test_multiple_websocket_connections()
        else:
            success2 = True
    else:
        success2 = False
    
    print("\n🏁 WebSocket Test Summary")
    print("-" * 25)
    print(f"Single connection: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Multiple connections: {'✅ PASS' if success2 else '⏭️ SKIPPED'}")
    
    if success1 and success2:
        print("\n🎉 All WebSocket tests passed! Your WebSocket streaming is working correctly.")
        print(f"\n📋 Asterisk WebSocket URL: ws://192.168.8.18:8123/audio/stream")
    else:
        print("\n⚠️ Some WebSocket tests failed. Check your service configuration.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ WebSocket test interrupted by user")
    except Exception as e:
        print(f"\n❌ WebSocket test failed with error: {e}")
        import traceback
        traceback.print_exc()