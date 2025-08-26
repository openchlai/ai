# test_resource_manager.py
import asyncio
import time
import sys
import os

# Add the parent directory to Python path so we can import app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.resource_manager import UnifiedResourceManager

async def test_resource_manager():
    print("🧪 Testing Unified Resource Manager...")
    
    # Initialize with small limits for testing
    rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
    
    # Test streaming acquisition
    print("\n--- Testing Streaming Resources ---")
    print("Acquiring 2 streaming slots...")
    success1 = await rm.acquire_streaming_gpu("stream_1")
    success2 = await rm.acquire_streaming_gpu("stream_2")
    print(f"✅ Stream 1 acquired: {success1}")
    print(f"✅ Stream 2 acquired: {success2}")
    
    # Check status
    status = rm.get_resource_status()
    print(f"📊 Streaming utilization: {status['streaming']['utilization_pct']:.1f}%")
    print(f"📊 Available streaming slots: {status['streaming']['available_slots']}")
    
    # Test resource limits
    print("\n--- Testing Resource Limits ---")
    print("Trying to acquire 3rd streaming slot (should wait)...")
    start_time = time.time()
    
    # This should wait because we're at capacity
    success3_task = asyncio.create_task(rm.acquire_streaming_gpu("stream_3"))
    
    # Wait a bit then release one slot
    await asyncio.sleep(1)
    print("🔓 Releasing stream_1...")
    rm.release_streaming_gpu("stream_1")
    
    # Now the waiting request should succeed
    success3 = await success3_task
    elapsed = time.time() - start_time
    print(f"✅ Stream 3 acquired after {elapsed:.2f}s wait: {success3}")
    
    # Test batch processing
    print("\n--- Testing Batch Resources ---")
    batch_success = await rm.acquire_batch_gpu("batch_1")
    print(f"✅ Batch 1 acquired: {batch_success}")
    
    # Test concurrent batch (should wait)
    print("Trying to acquire 2nd batch slot (should wait)...")
    start_time = time.time()
    batch2_task = asyncio.create_task(rm.acquire_batch_gpu("batch_2"))
    
    await asyncio.sleep(1)
    print("🔓 Releasing batch_1...")
    rm.release_batch_gpu("batch_1")
    
    batch2_success = await batch2_task
    elapsed = time.time() - start_time
    print(f"✅ Batch 2 acquired after {elapsed:.2f}s wait: {batch2_success}")
    
    # Final cleanup
    print("\n--- Cleanup ---")
    rm.release_streaming_gpu("stream_2")
    rm.release_streaming_gpu("stream_3")
    rm.release_batch_gpu("batch_2")
    
    # Final status
    final_status = rm.get_resource_status()
    print("\n📊 Final Status:")
    print(f"   Streaming: {final_status['streaming']['total_processed']} total processed")
    print(f"   Batch: {final_status['batch']['total_processed']} total processed")
    print(f"   Active requests: {len(final_status['active_request_ids']['streaming'])} streaming, {len(final_status['active_request_ids']['batch'])} batch")
    
    print("\n✅ Resource manager test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_resource_manager())