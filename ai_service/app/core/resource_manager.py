import asyncio
import logging
import psutil
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
import sys
import gc

logger = logging.getLogger(__name__)

# Optional torch import - gracefully handle if not available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - GPU monitoring disabled")

class GPUResourceManager:
    """Enhanced GPU resource manager with intelligent memory management"""
    
    def __init__(self, max_concurrent: int = 1, memory_threshold: float = 0.9):
        self.max_concurrent = max_concurrent
        self.memory_threshold = memory_threshold  # GPU memory usage threshold
        self.gpu_semaphore = asyncio.Semaphore(max_concurrent)
        self.active_requests: Dict[str, Dict] = {}
        self.request_counter = 0
        self.start_time = datetime.now()
        self.memory_stats = {"peak_usage": 0, "cleanups_performed": 0}
        
        logger.info(f"Enhanced GPU Resource Manager initialized with max_concurrent={max_concurrent}")
        logger.info(f"Memory threshold set to {memory_threshold*100}%")
        
        if not TORCH_AVAILABLE:
            logger.info("Running in CPU-only mode (PyTorch not available)")
    
    async def acquire_gpu(self, request_id: str) -> bool:
        """Acquire GPU access with enhanced memory management"""
        logger.info(f"Request {request_id} requesting GPU access")
        
        try:
            # Check memory before acquisition
            await self._ensure_memory_available()
            
            # Record request start
            self.active_requests[request_id] = {
                "start_time": datetime.now(),
                "status": "waiting",
                "memory_before": self._get_gpu_memory_usage()
            }
            
            # Wait for GPU access
            await self.gpu_semaphore.acquire()
            
            # Update status and record memory after acquisition
            self.active_requests[request_id]["status"] = "processing"
            self.active_requests[request_id]["gpu_acquired_time"] = datetime.now()
            self.active_requests[request_id]["memory_after_acquire"] = self._get_gpu_memory_usage()
            
            # Update peak memory tracking
            current_memory = self._get_gpu_memory_usage()
            if current_memory > self.memory_stats["peak_usage"]:
                self.memory_stats["peak_usage"] = current_memory
            
            logger.info(f"Request {request_id} acquired GPU access (Memory: {current_memory:.1f}%)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acquire GPU for request {request_id}: {e}")
            if request_id in self.active_requests:
                del self.active_requests[request_id]
            return False
    
    def release_gpu(self, request_id: str):
        """Release GPU access with memory cleanup"""
        try:
            # Perform memory cleanup before releasing
            self._cleanup_gpu_memory()
            
            self.gpu_semaphore.release()
            
            if request_id in self.active_requests:
                processing_time = datetime.now() - self.active_requests[request_id]["gpu_acquired_time"]
                memory_after_release = self._get_gpu_memory_usage()
                
                logger.info(f"Request {request_id} released GPU after {processing_time.total_seconds():.2f}s "
                           f"(Memory after cleanup: {memory_after_release:.1f}%)")
                
                # Store processing statistics for monitoring
                self.active_requests[request_id]["memory_after_release"] = memory_after_release
                self.active_requests[request_id]["processing_time"] = processing_time.total_seconds()
                
                del self.active_requests[request_id]
            
        except Exception as e:
            logger.error(f"Error releasing GPU for request {request_id}: {e}")
    
    async def _ensure_memory_available(self):
        """Ensure sufficient GPU memory is available"""
        if not TORCH_AVAILABLE:
            return
        
        max_attempts = 3
        for attempt in range(max_attempts):
            current_usage = self._get_gpu_memory_usage()
            
            if current_usage < self.memory_threshold:
                return  # Memory is available
            
            logger.warning(f"GPU memory usage high ({current_usage:.1f}%), performing cleanup (attempt {attempt + 1})")
            
            # Aggressive memory cleanup
            self._cleanup_gpu_memory()
            await asyncio.sleep(1)  # Give cleanup time to take effect
            
            # Check again
            new_usage = self._get_gpu_memory_usage()
            if new_usage < current_usage:
                logger.info(f"Memory cleanup reduced usage from {current_usage:.1f}% to {new_usage:.1f}%")
                self.memory_stats["cleanups_performed"] += 1
            
            if new_usage < self.memory_threshold:
                return
        
        logger.warning(f"Could not free sufficient GPU memory after {max_attempts} attempts")
    
    def _cleanup_gpu_memory(self):
        """Perform comprehensive GPU memory cleanup"""
        if not TORCH_AVAILABLE:
            return
        
        try:
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()  # Ensure all operations complete
            
            # Force garbage collection
            gc.collect()
            
            # Additional cleanup for potential memory leaks
            if hasattr(torch.cuda, 'reset_max_memory_allocated'):
                torch.cuda.reset_max_memory_allocated()
            
        except Exception as e:
            logger.warning(f"GPU memory cleanup failed: {e}")
    
    def _get_gpu_memory_usage(self) -> float:
        """Get current GPU memory usage as percentage"""
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return 0.0
        
        try:
            allocated = torch.cuda.memory_allocated(0)
            total = torch.cuda.get_device_properties(0).total_memory
            return (allocated / total) * 100
        except Exception:
            return 0.0
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get enhanced GPU status with memory analysis"""
        gpu_info = {
            "torch_available": TORCH_AVAILABLE,
            "gpu_available": False,
            "gpu_count": 0,
            "active_requests": len(self.active_requests),
            "max_concurrent": self.max_concurrent,
            "requests_in_queue": max(0, len(self.active_requests) - self.max_concurrent),
            "memory_management": {
                "threshold_percent": self.memory_threshold * 100,
                "peak_usage_percent": self.memory_stats["peak_usage"],
                "cleanups_performed": self.memory_stats["cleanups_performed"]
            }
        }
        
        if TORCH_AVAILABLE:
            try:
                gpu_info.update({
                    "gpu_available": torch.cuda.is_available(),
                    "gpu_count": torch.cuda.device_count(),
                })
                
                if torch.cuda.is_available():
                    current_memory_usage = self._get_gpu_memory_usage()
                    
                    gpu_info.update({
                        "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory,
                        "gpu_memory_allocated": torch.cuda.memory_allocated(0),
                        "gpu_memory_cached": torch.cuda.memory_reserved(0),
                        "gpu_memory_usage_percent": round(current_memory_usage, 2),
                        "gpu_name": torch.cuda.get_device_name(0),
                        "memory_status": (
                            "critical" if current_memory_usage > 90 else
                            "high" if current_memory_usage > 75 else
                            "normal"
                        )
                    })
            except Exception as e:
                logger.warning(f"Could not get GPU info: {e}")
                gpu_info["gpu_error"] = str(e)
        else:
            gpu_info["gpu_note"] = "PyTorch not installed - GPU monitoring unavailable"
        
        return gpu_info
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get enhanced system resource information"""
        memory = psutil.virtual_memory()
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            "process_count": len(psutil.pids())
        }
    
    def get_memory_recommendations(self) -> Dict[str, Any]:
        """Get memory optimization recommendations"""
        gpu_info = self.get_gpu_info()
        system_info = self.get_system_info()
        
        recommendations = {
            "gpu_recommendations": [],
            "system_recommendations": [],
            "priority": "normal"
        }
        
        # GPU recommendations
        if gpu_info.get("gpu_available", False):
            memory_usage = gpu_info.get("gpu_memory_usage_percent", 0)
            
            if memory_usage > 90:
                recommendations["gpu_recommendations"].extend([
                    "immediate_memory_cleanup_needed",
                    "consider_reducing_batch_sizes",
                    "enable_aggressive_memory_management"
                ])
                recommendations["priority"] = "critical"
            elif memory_usage > 75:
                recommendations["gpu_recommendations"].extend([
                    "monitor_memory_usage_closely",
                    "consider_model_optimization"
                ])
                recommendations["priority"] = "high"
            
            cleanup_ratio = self.memory_stats["cleanups_performed"] / max(1, len(self.active_requests) + self.memory_stats["cleanups_performed"])
            if cleanup_ratio > 0.3:
                recommendations["gpu_recommendations"].append("frequent_cleanups_detected_investigate_memory_leaks")
        
        # System recommendations
        if system_info["memory_percent"] > 90:
            recommendations["system_recommendations"].extend([
                "system_memory_critical",
                "restart_service_recommended"
            ])
            recommendations["priority"] = "critical"
        elif system_info["memory_percent"] > 80:
            recommendations["system_recommendations"].append("monitor_system_memory")
        
        return recommendations
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "issues": [],
            "warnings": []
        }
        
        # Check GPU health
        gpu_info = self.get_gpu_info()
        if gpu_info.get("gpu_available", False):
            memory_usage = gpu_info.get("gpu_memory_usage_percent", 0)
            if memory_usage > 95:
                health_status["issues"].append("gpu_memory_critical")
                health_status["overall_status"] = "unhealthy"
            elif memory_usage > 85:
                health_status["warnings"].append("gpu_memory_high")
                if health_status["overall_status"] == "healthy":
                    health_status["overall_status"] = "degraded"
        
        # Check system health
        system_info = self.get_system_info()
        if system_info["memory_percent"] > 95:
            health_status["issues"].append("system_memory_critical")
            health_status["overall_status"] = "unhealthy"
        elif system_info["memory_percent"] > 85:
            health_status["warnings"].append("system_memory_high")
            if health_status["overall_status"] == "healthy":
                health_status["overall_status"] = "degraded"
        
        # Check queue health
        if len(self.active_requests) > self.max_concurrent * 3:
            health_status["warnings"].append("high_queue_length")
            if health_status["overall_status"] == "healthy":
                health_status["overall_status"] = "degraded"
        
        # Add recommendations
        health_status["recommendations"] = self.get_memory_recommendations()
        
        return health_status

# Global resource manager instance with enhanced capabilities
resource_manager = GPUResourceManager(max_concurrent=1, memory_threshold=0.85)