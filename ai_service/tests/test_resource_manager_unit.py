# tests/test_resource_manager_unit.py
import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.resource_manager import UnifiedResourceManager

class TestUnifiedResourceManager:
    """Unit tests for the UnifiedResourceManager"""

    def test_initialization(self):
        """Test resource manager initialization"""
        rm = UnifiedResourceManager(max_streaming_slots=3, max_batch_slots=2)
        
        assert rm.max_streaming_slots == 3
        assert rm.max_batch_slots == 2
        assert rm.streaming_semaphore._value == 3
        assert rm.batch_semaphore._value == 2
        assert len(rm.active_streaming_requests) == 0
        assert len(rm.active_batch_requests) == 0

    def test_initialization_with_defaults(self):
        """Test resource manager initialization with default values"""
        rm = UnifiedResourceManager()
        
        assert rm.max_streaming_slots == 4  # Default
        assert rm.max_batch_slots == 2      # Default

    @pytest.mark.asyncio
    async def test_acquire_streaming_gpu_success(self):
        """Test successful streaming GPU acquisition"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
        
        request_id = "stream_001"
        result = await rm.acquire_streaming_gpu(request_id)
        
        assert result is True
        assert request_id in rm.active_streaming_requests
        assert len(rm.active_streaming_requests) == 1

    @pytest.mark.asyncio
    async def test_acquire_streaming_gpu_capacity_limit(self):
        """Test streaming GPU acquisition when at capacity"""
        rm = UnifiedResourceManager(max_streaming_slots=1, max_batch_slots=1)
        
        # First acquisition should succeed
        result1 = await rm.acquire_streaming_gpu("stream_001")
        assert result1 is True
        
        # Second acquisition should wait (we'll use a timeout to test this)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                rm.acquire_streaming_gpu("stream_002"), 
                timeout=0.1
            )

    @pytest.mark.asyncio
    async def test_release_streaming_gpu(self):
        """Test releasing streaming GPU"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
        
        request_id = "stream_001"
        await rm.acquire_streaming_gpu(request_id)
        
        # Release the GPU
        rm.release_streaming_gpu(request_id)
        
        assert request_id not in rm.active_streaming_requests
        assert rm.streaming_semaphore._value == 2  # Back to full capacity

    @pytest.mark.asyncio
    async def test_acquire_batch_gpu_success(self):
        """Test successful batch GPU acquisition"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=2)
        
        request_id = "batch_001"
        result = await rm.acquire_batch_gpu(request_id)
        
        assert result is True
        assert request_id in rm.active_batch_requests
        assert len(rm.active_batch_requests) == 1

    @pytest.mark.asyncio
    async def test_acquire_batch_gpu_capacity_limit(self):
        """Test batch GPU acquisition when at capacity"""
        rm = UnifiedResourceManager(max_streaming_slots=1, max_batch_slots=1)
        
        # First acquisition should succeed
        result1 = await rm.acquire_batch_gpu("batch_001")
        assert result1 is True
        
        # Second acquisition should wait
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                rm.acquire_batch_gpu("batch_002"), 
                timeout=0.1
            )

    @pytest.mark.asyncio
    async def test_release_batch_gpu(self):
        """Test releasing batch GPU"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=2)
        
        request_id = "batch_001"
        await rm.acquire_batch_gpu(request_id)
        
        # Release the GPU
        rm.release_batch_gpu(request_id)
        
        assert request_id not in rm.active_batch_requests
        assert rm.batch_semaphore._value == 2  # Back to full capacity

    def test_get_resource_status(self):
        """Test getting resource status information"""
        rm = UnifiedResourceManager(max_streaming_slots=3, max_batch_slots=2)
        
        status = rm.get_resource_status()
        
        assert isinstance(status, dict)
        assert "streaming" in status
        assert "batch" in status
        assert "active_request_ids" in status
        
        # Check streaming status
        streaming_status = status["streaming"]
        assert streaming_status["total_slots"] == 3
        assert streaming_status["available_slots"] == 3
        assert streaming_status["utilization_pct"] == 0.0
        
        # Check batch status
        batch_status = status["batch"]
        assert batch_status["total_slots"] == 2
        assert batch_status["available_slots"] == 2
        assert batch_status["utilization_pct"] == 0.0

    @pytest.mark.asyncio
    async def test_resource_status_with_active_requests(self):
        """Test resource status with active requests"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
        
        # Acquire some resources
        await rm.acquire_streaming_gpu("stream_001")
        await rm.acquire_batch_gpu("batch_001")
        
        status = rm.get_resource_status()
        
        # Check updated status
        assert status["streaming"]["available_slots"] == 1
        assert status["streaming"]["utilization_pct"] == 50.0
        assert status["batch"]["available_slots"] == 0
        assert status["batch"]["utilization_pct"] == 100.0
        
        # Check active request IDs
        assert "stream_001" in status["active_request_ids"]["streaming"]
        assert "batch_001" in status["active_request_ids"]["batch"]

    def test_release_nonexistent_request(self):
        """Test releasing a request that doesn't exist"""
        rm = UnifiedResourceManager()
        
        # This should not raise an error
        rm.release_streaming_gpu("nonexistent_001")
        rm.release_batch_gpu("nonexistent_002")
        
        # Status should remain unchanged
        status = rm.get_resource_status()
        assert status["streaming"]["available_slots"] == rm.max_streaming_slots
        assert status["batch"]["available_slots"] == rm.max_batch_slots

    @pytest.mark.asyncio
    async def test_concurrent_acquisitions(self):
        """Test concurrent resource acquisitions"""
        rm = UnifiedResourceManager(max_streaming_slots=3, max_batch_slots=2)
        
        # Start multiple acquisitions concurrently
        tasks = [
            asyncio.create_task(rm.acquire_streaming_gpu(f"stream_{i}"))
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed within limits
        assert all(results)
        assert len(rm.active_streaming_requests) == 3

    @pytest.mark.asyncio
    async def test_request_queuing(self):
        """Test that requests queue properly when at capacity"""
        rm = UnifiedResourceManager(max_streaming_slots=1, max_batch_slots=1)
        
        # First request acquires the slot
        await rm.acquire_streaming_gpu("stream_001")
        
        # Start a second request (will wait)
        waiting_task = asyncio.create_task(rm.acquire_streaming_gpu("stream_002"))
        
        # Give it time to start waiting
        await asyncio.sleep(0.01)
        assert not waiting_task.done()
        
        # Release the first slot
        rm.release_streaming_gpu("stream_001")
        
        # The waiting request should now complete
        result = await waiting_task
        assert result is True
        assert "stream_002" in rm.active_streaming_requests

    def test_statistics_tracking(self):
        """Test that statistics are tracked correctly"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
        
        initial_status = rm.get_resource_status()
        initial_streaming_processed = initial_status["streaming"]["total_processed"]
        initial_batch_processed = initial_status["batch"]["total_processed"]
        
        # This test would need the actual implementation to track statistics
        # For now, we just verify the structure exists
        assert "total_processed" in initial_status["streaming"]
        assert "total_processed" in initial_status["batch"]

    @pytest.mark.asyncio
    async def test_error_handling_in_acquisition(self):
        """Test error handling during resource acquisition"""
        rm = UnifiedResourceManager()
        
        # Test with None request_id
        result = await rm.acquire_streaming_gpu(None)
        assert result is False
        
        # Test with empty string
        result = await rm.acquire_streaming_gpu("")
        assert result is False

    @pytest.mark.asyncio
    async def test_duplicate_request_id_handling(self):
        """Test handling of duplicate request IDs"""
        rm = UnifiedResourceManager(max_streaming_slots=2)
        
        request_id = "duplicate_test"
        
        # First acquisition
        result1 = await rm.acquire_streaming_gpu(request_id)
        assert result1 is True
        
        # Second acquisition with same ID should handle gracefully
        result2 = await rm.acquire_streaming_gpu(request_id)
        # Implementation dependent - could succeed or fail
        # The important thing is it doesn't crash
        assert isinstance(result2, bool)

    def test_resource_limits_validation(self):
        """Test validation of resource limits during initialization"""
        # Valid initialization
        rm1 = UnifiedResourceManager(max_streaming_slots=4, max_batch_slots=2)
        assert rm1.max_streaming_slots == 4
        assert rm1.max_batch_slots == 2
        
        # Zero values should be handled
        rm2 = UnifiedResourceManager(max_streaming_slots=0, max_batch_slots=0)
        assert rm2.max_streaming_slots == 0
        assert rm2.max_batch_slots == 0

    @pytest.mark.asyncio
    async def test_cleanup_operations(self):
        """Test cleanup and shutdown operations"""
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
        
        # Acquire some resources
        await rm.acquire_streaming_gpu("stream_001")
        await rm.acquire_batch_gpu("batch_001")
        
        # Test that we can release all resources
        rm.release_streaming_gpu("stream_001")
        rm.release_batch_gpu("batch_001")
        
        status = rm.get_resource_status()
        assert len(status["active_request_ids"]["streaming"]) == 0
        assert len(status["active_request_ids"]["batch"]) == 0