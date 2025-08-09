#!/usr/bin/env python3
"""
Simple test client for Redis pub/sub streaming
Tests the new /audio/process-stream-realtime endpoint
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_streaming_endpoint():
    """Test the real-time streaming endpoint"""
    
    # Create a minimal WAV file for testing (this will likely fail audio processing but should trigger streaming)
    # 44-byte WAV header with minimal audio data
    wav_header = (
        b'RIFF'  # ChunkID
        b'\x2c\x00\x00\x00'  # ChunkSize 
        b'WAVE'  # Format
        b'fmt '  # Subchunk1ID  
        b'\x10\x00\x00\x00'  # Subchunk1Size
        b'\x01\x00'  # AudioFormat (PCM)
        b'\x01\x00'  # NumChannels (mono)
        b'\x40\x1f\x00\x00'  # SampleRate (8000)
        b'\x80\x3e\x00\x00'  # ByteRate
        b'\x02\x00'  # BlockAlign  
        b'\x10\x00'  # BitsPerSample (16)
        b'data'  # Subchunk2ID
        b'\x08\x00\x00\x00'  # Subchunk2Size
        b'\x00\x00\x00\x00\x00\x00\x00\x00'  # 8 bytes of silence
    )
    test_audio_data = wav_header
    
    print("📝 Note: Using minimal WAV file - may trigger processing errors (this is expected for testing)")
    
    # Prepare form data
    data = aiohttp.FormData()
    data.add_field('audio', test_audio_data, filename='test.wav', content_type='audio/wav')
    data.add_field('language', 'en')
    data.add_field('include_translation', 'true')
    data.add_field('include_insights', 'true')
    
    print(f"🧪 Starting streaming test at {datetime.now()}")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the real-time streaming endpoint
            async with session.post(
                'http://localhost:8123/audio/process-stream-realtime',
                data=data
            ) as response:
                
                if response.status != 200:
                    print(f"❌ Request failed with status {response.status}")
                    text = await response.text()
                    print(f"Error: {text}")
                    return
                
                print(f"✅ Stream connected (status: {response.status})")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print("📡 Receiving stream data...")
                print("-" * 30)
                
                message_count = 0
                start_time = datetime.now()
                
                # Read streaming data
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        message_count += 1
                        json_data = line[6:]  # Remove 'data: ' prefix
                        
                        try:
                            update = json.loads(json_data)
                            timestamp = update.get('timestamp', 'no-timestamp')
                            step = update.get('step', 'unknown')
                            progress = update.get('progress', 0)
                            message = update.get('message', 'no message')
                            
                            print(f"[{message_count:02d}] {timestamp[:19]} | {step:20} | {progress:3d}% | {message}")
                            
                            # Show error information if present
                            if 'error' in update:
                                print(f"     ❌ Error: {update['error']}")
                            
                            # Show status information
                            status = update.get('status', 'unknown')
                            if status in ['stream_error', 'timeout', 'failed']:
                                print(f"     🚨 Status: {status}")
                            
                            # Show partial results if available
                            partial_result = update.get('partial_result')
                            if partial_result:
                                if 'transcript' in partial_result:
                                    transcript_preview = partial_result['transcript'][:50]
                                    is_final = partial_result.get('is_final', False)
                                    status = "FINAL" if is_final else "partial"
                                    print(f"     🎤 Transcript ({status}): {transcript_preview}...")
                                
                                if 'translation' in partial_result:
                                    translation_preview = partial_result['translation'][:50]
                                    is_final = partial_result.get('is_final', False)
                                    status = "FINAL" if is_final else "partial"
                                    print(f"     🌐 Translation ({status}): {translation_preview}...")
                                
                                if 'entities' in partial_result:
                                    entities = partial_result['entities']
                                    entity_count = len(entities) if entities else 0
                                    print(f"     🏷️  Entities: {entity_count} types found")
                                
                                if 'classification' in partial_result:
                                    classification = partial_result['classification']
                                    category = classification.get('main_category', 'unknown')
                                    confidence = classification.get('confidence', 0)
                                    print(f"     📊 Classification: {category} (confidence: {confidence:.2f})")
                                
                                if 'summary' in partial_result:
                                    summary = partial_result['summary']
                                    summary_preview = summary[:80] if summary else "none"
                                    print(f"     📝 Summary: {summary_preview}...")
                            
                            # Check for completion
                            if step in ['completed', 'failed', 'timeout', 'stream_error']:
                                elapsed = (datetime.now() - start_time).total_seconds()
                                print(f"\n🏁 Stream ended: {step} (received {message_count} messages in {elapsed:.1f}s)")
                                
                                if step == 'completed' and partial_result:
                                    print("\n📋 Final Results Summary:")
                                    print(f"   📁 File: {partial_result.get('audio_info', {}).get('filename', 'unknown')}")
                                    print(f"   ⏱️  Processing time: {partial_result.get('audio_info', {}).get('processing_time', 0):.2f}s")
                                    print(f"   🎤 Transcript length: {len(partial_result.get('transcript', ''))}")
                                    if partial_result.get('translation'):
                                        print(f"   🌐 Translation length: {len(partial_result.get('translation', ''))}")
                                    print(f"   🏷️  Entity types: {len(partial_result.get('entities', {}))}")
                                    classification = partial_result.get('classification', {})
                                    if classification:
                                        print(f"   📊 Category: {classification.get('main_category', 'unknown')}")
                                
                                break
                            
                            # Add timeout check to prevent hanging
                            elapsed = (datetime.now() - start_time).total_seconds()
                            if elapsed > 30:  # 30 second timeout for testing
                                print(f"\n⏰ Test timeout after {elapsed:.1f}s (received {message_count} messages)")
                                print("This suggests the Celery task may not be processing or publishing updates")
                                break
                        
                        except json.JSONDecodeError as e:
                            print(f"❌ Invalid JSON: {e}")
                            print(f"   Raw data: {json_data[:100]}...")
    
    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🚀 Redis Pub/Sub Streaming Test")
    print("Testing /audio/process-stream-realtime endpoint")
    print("Make sure your FastAPI server is running on http://localhost:8123")
    print("Make sure Redis and Celery workers are running")
    print()
    
    # Wait a moment for user to read
    await asyncio.sleep(2)
    
    await test_streaming_endpoint()
    
    print("\n✅ Test completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)