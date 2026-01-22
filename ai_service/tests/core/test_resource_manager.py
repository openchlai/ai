
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.core.resource_manager import UnifiedResourceManager, resource_manager

class TestUnifiedResourceManager:
    
    @pytest.fixture
    def manager(self):
        return UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)

    def test_initialization(self, manager):
        assert manager.max_streaming_slots == 2
        assert manager.max_batch_slots == 1
        assert manager.streaming_semaphore._value == 2
        assert manager.batch_semaphore._value == 1
        assert len(manager.active_requests) == 0

    @pytest.mark.asyncio
    async def test_acquire_streaming_gpu_success(self, manager):
        success = await manager.acquire_streaming_gpu("req1")
        assert success is True
        assert "req1" in manager.streaming_requests
        assert manager.total_streaming_requests == 1
        assert manager.streaming_semaphore._value == 1 # 2 - 1 = 1

    @pytest.mark.asyncio
    async def test_acquire_batch_gpu_success(self, manager):
        success = await manager.acquire_batch_gpu("req2")
        assert success is True
        assert "req2" in manager.batch_requests
        assert manager.total_batch_requests == 1
        assert manager.batch_semaphore._value == 0 # 1 - 1 = 0

    @pytest.mark.asyncio
    async def test_release_streaming_gpu(self, manager):
        await manager.acquire_streaming_gpu("req1")
        manager.release_streaming_gpu("req1")
        
        assert "req1" not in manager.streaming_requests
        assert manager.streaming_semaphore._value == 2
        assert "req1" not in manager.active_requests

    @pytest.mark.asyncio
    async def test_release_batch_gpu(self, manager):
        await manager.acquire_batch_gpu("req2")
        manager.release_batch_gpu("req2")
        
        assert "req2" not in manager.batch_requests
        assert manager.batch_semaphore._value == 1

    @pytest.mark.asyncio
    async def test_acquire_streaming_full_wait(self, manager):
        # Fill slots
        await manager.acquire_streaming_gpu("req1")
        await manager.acquire_streaming_gpu("req2")
        assert manager.streaming_semaphore._value == 0
        
        # Third request should block/wait. To test without hanging, we can timeout or run concurrently.
        # We'll use asyncio.wait_for to ensure it waits effectively, but for unit test speed, 
        # we can just test that we can't acquire immediately if we checked semaphore.
        # But acquire_streaming_gpu waits.
        # Let's start a task to acquire, check it's not done, then release one slot.
        
        task = asyncio.create_task(manager.acquire_streaming_gpu("req3"))
        await asyncio.sleep(0.01) # Switch context
        assert not task.done()
        
        manager.release_streaming_gpu("req1")
        await asyncio.sleep(0.01)
        assert task.done()
        assert await task is True
        assert "req3" in manager.streaming_requests

    @pytest.mark.asyncio
    async def test_acquire_batch_full_wait(self, manager):
        await manager.acquire_batch_gpu("req1")
        
        task = asyncio.create_task(manager.acquire_batch_gpu("req2"))
        await asyncio.sleep(0.01)
        assert not task.done()
        
        manager.release_batch_gpu("req1")
        await asyncio.sleep(0.01)
        assert task.done()
        assert await task is True

    def test_release_non_existent(self, manager):
        # Should log warning but not crash
        manager.release_streaming_gpu("unknown")
        manager.release_batch_gpu("unknown")

    def test_resource_status(self, manager):
        manager.active_requests["s1"] = MagicMock()
        manager.streaming_requests.add("s1")
        # Manually decrement for test consistency if we didn't call acquire via async
        manager.streaming_semaphore._value = 1 
        
        status = manager.get_resource_status()
        assert status["streaming"]["active_requests"] == 1
        assert status["streaming"]["utilization_pct"] == 50.0
        assert "s1" in status["active_request_ids"]["streaming"]

    @pytest.mark.asyncio
    async def test_legacy_methods(self, manager):
        # acquire_gpu -> batch
        await manager.acquire_gpu("leg1")
        assert "leg1" in manager.batch_requests
        
        # release_gpu
        manager.release_gpu("leg1")
        assert "leg1" not in manager.batch_requests
        
        # release_gpu finding streaming
        await manager.acquire_streaming_gpu("leg2")
        manager.release_gpu("leg2")
        assert "leg2" not in manager.streaming_requests
        
        # release unknown
        manager.release_gpu("unknown") # Should verify warning log if strict, but safe execution is enough

    def test_get_system_info(self, manager):
        with patch('psutil.virtual_memory') as mock_mem, \
             patch('psutil.cpu_count', return_value=4), \
             patch('psutil.disk_usage') as mock_disk, \
             patch('platform.platform', return_value="Linux"):
            
            mock_mem.return_value.total = 1000
            mock_mem.return_value.available = 500
            mock_mem.return_value.percent = 50.0
            mock_disk.return_value.percent = 30.0
            
            info = manager.get_system_info()
            assert info["cpu_count"] == 4
            assert info["memory_total"] == 1000

    def test_get_gpu_info_torch_available(self, manager):
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.device_count', return_value=1), \
             patch('torch.cuda.current_device', return_value=0), \
             patch('torch.cuda.get_device_name', return_value="Tesla T4"), \
             patch('torch.cuda.memory_allocated', return_value=100), \
             patch('torch.cuda.memory_reserved', return_value=200), \
             patch('torch.cuda.get_device_properties') as mock_props:
            
            mock_props.return_value.total_memory = 1000
            
            info = manager.get_gpu_info()
            assert info["gpu_available"] is True
            assert info["device_name"] == "Tesla T4"

    def test_get_gpu_info_no_cuda(self, manager):
        with patch('torch.cuda.is_available', return_value=False):
            info = manager.get_gpu_info()
            assert info["gpu_available"] is False


    def test_get_gpu_info_import_error(self, manager):
        import sys
        # Temporarily hide torch from sys.modules
        with patch.dict(sys.modules, {'torch': None}):
            info = manager.get_gpu_info()
            assert info["gpu_available"] is False
            assert info["message"] == "PyTorch not available"

    @pytest.mark.asyncio
    async def test_acquire_exception_handling(self, manager):
        # Force exception during acquire logic
        manager.streaming_semaphore.acquire = MagicMock(side_effect=Exception("Semaphore Error"))
        
        success = await manager.acquire_streaming_gpu("fail1")
        assert success is False
        
        manager.batch_semaphore.acquire = MagicMock(side_effect=Exception("Semaphore Error"))
        success = await manager.acquire_batch_gpu("fail2")
        assert success is False

    def test_release_exception_handling(self, manager):
        # Force exception
        manager.streaming_requests.add("err1")
        manager.streaming_semaphore.release = MagicMock(side_effect=Exception("Release Error"))
        manager.release_streaming_gpu("err1") 
        # Should catch and log error, not raise

        manager.batch_requests.add("err2")
        manager.batch_semaphore.release = MagicMock(side_effect=Exception("Release Error"))
        manager.release_batch_gpu("err2")
