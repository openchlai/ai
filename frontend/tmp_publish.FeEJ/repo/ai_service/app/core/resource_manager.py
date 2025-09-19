import asyncio
import time
import logging
from typing import Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    STREAMING = "streaming"
    BATCH = "batch"

@dataclass
class ResourceRequest:
    request_id: str
    mode: ProcessingMode
    timestamp: datetime
    estimated_duration: float = 0.0

class UnifiedResourceManager:
    """
    Extended resource manager supporting both streaming and batch processing modes
    with intelligent resource allocation and monitoring.
    """
    
    def __init__(self, max_streaming_slots: int = 2, max_batch_slots: int = 1):
        # Separate semaphores for different processing types
        self.streaming_semaphore = asyncio.Semaphore(max_streaming_slots)
        self.batch_semaphore = asyncio.Semaphore(max_batch_slots)
        
        # Active request tracking
        self.active_requests: Dict[str, ResourceRequest] = {}
        self.streaming_requests: Set[str] = set()
        self.batch_requests: Set[str] = set()
        
        # Configuration
        self.max_streaming_slots = max_streaming_slots
        self.max_batch_slots = max_batch_slots
        
        # Metrics
        self.total_streaming_requests = 0
        self.total_batch_requests = 0
        self.streaming_wait_times = []
        self.batch_wait_times = []
        
        logger.info(f"🔧 Unified Resource Manager initialized: "
                   f"{max_streaming_slots} streaming slots, {max_batch_slots} batch slots")

    async def acquire_streaming_gpu(self, request_id: str, estimated_duration: float = 5.0) -> bool:
        """
        Acquire GPU resources for streaming processing (lighter weight, faster turnaround)
        """
        start_time = time.time()
        request = ResourceRequest(
            request_id=request_id,
            mode=ProcessingMode.STREAMING,
            timestamp=datetime.now(),
            estimated_duration=estimated_duration
        )
        
        try:
            logger.info(f"🎙️ [{request_id}] Requesting streaming GPU access...")
            
            # Check if we have available streaming slots
            available_slots = self.streaming_semaphore._value
            if available_slots == 0:
                logger.warning(f"⏳ [{request_id}] Streaming queue full, waiting...")
            
            # Acquire semaphore (this will wait if no slots available)
            await self.streaming_semaphore.acquire()
            
            # Track the request
            self.active_requests[request_id] = request
            self.streaming_requests.add(request_id)
            self.total_streaming_requests += 1
            
            wait_time = time.time() - start_time
            self.streaming_wait_times.append(wait_time)
            
            logger.info(f"✅ [{request_id}] Streaming GPU acquired in {wait_time:.2f}s "
                       f"({len(self.streaming_requests)}/{self.max_streaming_slots} slots used)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ [{request_id}] Failed to acquire streaming GPU: {e}")
            return False

    async def acquire_batch_gpu(self, request_id: str, estimated_duration: float = 60.0) -> bool:
        """
        Acquire GPU resources for batch processing (full pipeline, longer duration)
        """
        start_time = time.time()
        request = ResourceRequest(
            request_id=request_id,
            mode=ProcessingMode.BATCH,
            timestamp=datetime.now(),
            estimated_duration=estimated_duration
        )
        
        try:
            logger.info(f"📦 [{request_id}] Requesting batch GPU access...")
            
            # Check queue status
            available_slots = self.batch_semaphore._value
            if available_slots == 0:
                logger.warning(f"⏳ [{request_id}] Batch queue full, waiting...")
                # Estimate wait time based on active requests
                active_batch_requests = [r for r in self.active_requests.values() 
                                       if r.mode == ProcessingMode.BATCH]
                if active_batch_requests:
                    estimated_wait = min(r.estimated_duration for r in active_batch_requests)
                    logger.info(f"⏳ [{request_id}] Estimated wait time: {estimated_wait:.1f}s")
            
            # Acquire semaphore
            await self.batch_semaphore.acquire()
            
            # Track the request
            self.active_requests[request_id] = request
            self.batch_requests.add(request_id)
            self.total_batch_requests += 1
            
            wait_time = time.time() - start_time
            self.batch_wait_times.append(wait_time)
            
            logger.info(f"✅ [{request_id}] Batch GPU acquired in {wait_time:.2f}s "
                       f"({len(self.batch_requests)}/{self.max_batch_slots} slots used)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ [{request_id}] Failed to acquire batch GPU: {e}")
            return False

    def release_streaming_gpu(self, request_id: str):
        """Release streaming GPU resources"""
        try:
            if request_id in self.streaming_requests:
                self.streaming_requests.remove(request_id)
                self.active_requests.pop(request_id, None)
                self.streaming_semaphore.release()
                
                logger.info(f"🔓 [{request_id}] Streaming GPU released "
                           f"({len(self.streaming_requests)}/{self.max_streaming_slots} slots used)")
            else:
                logger.warning(f"⚠️ [{request_id}] Attempted to release non-existent streaming GPU")
                
        except Exception as e:
            logger.error(f"❌ [{request_id}] Error releasing streaming GPU: {e}")

    def release_batch_gpu(self, request_id: str):
        """Release batch GPU resources"""
        try:
            if request_id in self.batch_requests:
                self.batch_requests.remove(request_id)
                self.active_requests.pop(request_id, None)
                self.batch_semaphore.release()
                
                logger.info(f"🔓 [{request_id}] Batch GPU released "
                           f"({len(self.batch_requests)}/{self.max_batch_slots} slots used)")
            else:
                logger.warning(f"⚠️ [{request_id}] Attempted to release non-existent batch GPU")
                
        except Exception as e:
            logger.error(f"❌ [{request_id}] Error releasing batch GPU: {e}")

    def get_resource_status(self) -> Dict:
        """Get current resource utilization status"""
        return {
            "streaming": {
                "active_requests": len(self.streaming_requests),
                "max_slots": self.max_streaming_slots,
                "available_slots": self.streaming_semaphore._value,
                "utilization_pct": (len(self.streaming_requests) / self.max_streaming_slots) * 100,
                "total_processed": self.total_streaming_requests,
                "avg_wait_time": sum(self.streaming_wait_times[-10:]) / len(self.streaming_wait_times[-10:]) if self.streaming_wait_times else 0
            },
            "batch": {
                "active_requests": len(self.batch_requests),
                "max_slots": self.max_batch_slots,
                "available_slots": self.batch_semaphore._value,
                "utilization_pct": (len(self.batch_requests) / self.max_batch_slots) * 100,
                "total_processed": self.total_batch_requests,
                "avg_wait_time": sum(self.batch_wait_times[-10:]) / len(self.batch_wait_times[-10:]) if self.batch_wait_times else 0
            },
            "active_request_ids": {
                "streaming": list(self.streaming_requests),
                "batch": list(self.batch_requests)
            }
        }

    # Legacy methods for backward compatibility
    async def acquire_gpu(self, request_id: str) -> bool:
        """Legacy method - defaults to batch processing"""
        return await self.acquire_batch_gpu(request_id)
    
    def release_gpu(self, request_id: str):
        """Legacy method - tries to release from both pools"""
        if request_id in self.batch_requests:
            self.release_batch_gpu(request_id)
        elif request_id in self.streaming_requests:
            self.release_streaming_gpu(request_id)
        else:
            logger.warning(f"⚠️ [{request_id}] Request not found in any resource pool")
    
    def get_gpu_info(self):
        """Get GPU information - backward compatibility method"""
        try:
            import torch
            if torch.cuda.is_available():
                return {
                    "gpu_available": True,
                    "gpu_count": torch.cuda.device_count(),
                    "current_device": torch.cuda.current_device(),
                    "device_name": torch.cuda.get_device_name(),
                    "memory_allocated": torch.cuda.memory_allocated(),
                    "memory_reserved": torch.cuda.memory_reserved(),
                    "memory_available": torch.cuda.get_device_properties(0).total_memory
                }
            else:
                return {
                    "gpu_available": False,
                    "message": "CUDA not available"
                }
        except ImportError:
            return {
                "gpu_available": False,
                "message": "PyTorch not available"
            }

    def get_system_info(self):
        """Get system information - backward compatibility method"""
        import psutil
        import platform
        
        memory = psutil.virtual_memory()
        return {
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": memory.total,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_usage": psutil.disk_usage('/').percent
        }

# Create a global instance
unified_resource_manager = UnifiedResourceManager()

# Maintain backward compatibility
resource_manager = unified_resource_manager