import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RequestStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PARTIAL_SUCCESS = "partial_success"  # New status for chunking scenarios

class QueuedRequest:
    def __init__(self, request_id: str, request_type: str, priority: int = 5):
        self.request_id = request_id
        self.request_type = request_type
        self.priority = priority
        self.status = RequestStatus.QUEUED
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.result: Optional[Dict] = None
        
        # Enhanced tracking for chunked processing
        self.processing_info: Dict[str, Any] = {
            "chunking_applied": False,
            "chunks_processed": 0,
            "total_chunks": 0,
            "fallback_strategies_used": [],
            "partial_results": {}
        }

class RequestQueue:
    """Enhanced request queue with chunking and partial success support"""
    
    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.requests: Dict[str, QueuedRequest] = {}
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.processing_requests: Dict[str, QueuedRequest] = {}
        
        # Enhanced metrics
        self.metrics = {
            "total_processed": 0,
            "successful_completions": 0,
            "partial_successes": 0,
            "failures": 0,
            "chunking_usage": 0,
            "average_processing_time": 0.0
        }
        
        logger.info(f"Enhanced Request Queue initialized with max_size={max_size}")
    
    async def add_request(self, request_type: str, priority: int = 5) -> str:
        """Add a new request to the queue"""
        if self.queue.full():
            raise RuntimeError("Queue is full. Please try again later.")
        
        request_id = str(uuid.uuid4())
        queued_request = QueuedRequest(request_id, request_type, priority)
        
        self.requests[request_id] = queued_request
        await self.queue.put(queued_request)
        
        logger.info(f"Added request {request_id} to queue (type: {request_type})")
        return request_id
    
    async def get_next_request(self) -> Optional[QueuedRequest]:
        """Get the next request from the queue"""
        try:
            request = await self.queue.get()
            request.status = RequestStatus.PROCESSING
            request.started_at = datetime.now()
            self.processing_requests[request.request_id] = request
            
            logger.info(f"Started processing request {request.request_id}")
            return request
            
        except asyncio.QueueEmpty:
            return None
    
    def update_request_status(self, request_id: str, status: RequestStatus):
        """Update request status (for background processing)"""
        if request_id in self.requests:
            self.requests[request_id].status = status
            logger.debug(f"Updated request {request_id} status to {status}")
    
    def update_processing_info(self, request_id: str, info_updates: Dict[str, Any]):
        """Update processing information for chunked requests"""
        if request_id in self.requests:
            self.requests[request_id].processing_info.update(info_updates)
            logger.debug(f"Updated processing info for request {request_id}: {info_updates}")
    
    def complete_request(self, request_id: str, result: Dict = None, error: str = None, 
                        partial_success: bool = False):
        """Mark a request as completed with enhanced status tracking"""
        if request_id in self.processing_requests:
            request = self.processing_requests[request_id]
            request.completed_at = datetime.now()
            
            # Determine final status
            if error:
                request.status = RequestStatus.FAILED
                request.error_message = error
                self.metrics["failures"] += 1
            elif partial_success:
                request.status = RequestStatus.PARTIAL_SUCCESS
                request.result = result
                self.metrics["partial_successes"] += 1
            else:
                request.status = RequestStatus.COMPLETED
                request.result = result
                self.metrics["successful_completions"] += 1
            
            # Update metrics
            self.metrics["total_processed"] += 1
            if request.processing_info.get("chunking_applied", False):
                self.metrics["chunking_usage"] += 1
            
            # Calculate processing time
            if request.started_at and request.completed_at:
                processing_time = (request.completed_at - request.started_at).total_seconds()
                self._update_average_processing_time(processing_time)
            
            del self.processing_requests[request_id]
            logger.info(f"Completed request {request_id} with status {request.status}")
    
    def _update_average_processing_time(self, new_time: float):
        """Update rolling average processing time"""
        current_avg = self.metrics["average_processing_time"]
        total_processed = self.metrics["total_processed"]
        
        if total_processed == 1:
            self.metrics["average_processing_time"] = new_time
        else:
            # Weighted average with more emphasis on recent requests
            weight = min(0.1, 1.0 / total_processed)
            self.metrics["average_processing_time"] = (
                current_avg * (1 - weight) + new_time * weight
            )
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced status of a specific request"""
        if request_id not in self.requests:
            return None
        
        request = self.requests[request_id]
        
        status_info = {
            "request_id": request_id,
            "status": request.status,
            "request_type": request.request_type,
            "created_at": request.created_at.isoformat(),
            "queue_position": self._get_queue_position(request_id) if request.status == RequestStatus.QUEUED else None,
            "processing_info": request.processing_info
        }
        
        if request.started_at:
            status_info["started_at"] = request.started_at.isoformat()
            # Add estimated completion time for processing requests
            if request.status == RequestStatus.PROCESSING:
                estimated_completion = self._estimate_completion_time(request)
                if estimated_completion:
                    status_info["estimated_completion"] = estimated_completion.isoformat()
        
        if request.completed_at:
            status_info["completed_at"] = request.completed_at.isoformat()
            status_info["processing_time"] = (request.completed_at - request.started_at).total_seconds()
        
        if request.error_message:
            status_info["error"] = request.error_message
        
        if request.result:
            status_info["result"] = request.result
        
        # Add chunking-specific information
        if request.processing_info.get("chunking_applied", False):
            status_info["chunking_info"] = {
                "chunks_processed": request.processing_info.get("chunks_processed", 0),
                "total_chunks": request.processing_info.get("total_chunks", 0),
                "progress_percent": self._calculate_chunk_progress(request),
                "fallback_strategies": request.processing_info.get("fallback_strategies_used", [])
            }
        
        return status_info
    
    def _estimate_completion_time(self, request: QueuedRequest) -> Optional[datetime]:
        """Estimate completion time based on processing history and chunking info"""
        if not request.started_at:
            return None
        
        avg_time = self.metrics["average_processing_time"]
        if avg_time <= 0:
            return None
        
        # Adjust estimate based on chunking
        estimated_time = avg_time
        if request.processing_info.get("chunking_applied", False):
            total_chunks = request.processing_info.get("total_chunks", 1)
            chunks_processed = request.processing_info.get("chunks_processed", 0)
            
            if total_chunks > 1 and chunks_processed > 0:
                # Calculate based on chunk progress
                time_per_chunk = (datetime.now() - request.started_at).total_seconds() / chunks_processed
                remaining_chunks = total_chunks - chunks_processed
                estimated_time = time_per_chunk * remaining_chunks
        
        return request.started_at + timedelta(seconds=estimated_time)
    
    def _calculate_chunk_progress(self, request: QueuedRequest) -> float:
        """Calculate processing progress as percentage for chunked requests"""
        chunks_processed = request.processing_info.get("chunks_processed", 0)
        total_chunks = request.processing_info.get("total_chunks", 0)
        
        if total_chunks <= 0:
            return 0.0
        
        return min(100.0, (chunks_processed / total_chunks) * 100)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get enhanced queue status with chunking metrics"""
        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.max_size,
            "processing_count": len(self.processing_requests),
            "total_requests": len(self.requests),
            "metrics": self.metrics.copy(),
            "chunking_stats": {
                "chunking_usage_rate": (
                    (self.metrics["chunking_usage"] / max(1, self.metrics["total_processed"])) * 100
                ),
                "partial_success_rate": (
                    (self.metrics["partial_successes"] / max(1, self.metrics["total_processed"])) * 100
                ),
                "overall_success_rate": (
                    ((self.metrics["successful_completions"] + self.metrics["partial_successes"]) / 
                     max(1, self.metrics["total_processed"])) * 100
                )
            }
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get detailed processing statistics"""
        current_time = datetime.now()
        
        # Analyze current processing requests
        processing_stats = {
            "active_chunked_requests": 0,
            "active_simple_requests": 0,
            "average_chunks_per_request": 0.0,
            "longest_running_request": None
        }
        
        total_chunks = 0
        chunked_requests = 0
        longest_duration = 0
        longest_request_id = None
        
        for request in self.processing_requests.values():
            if request.processing_info.get("chunking_applied", False):
                processing_stats["active_chunked_requests"] += 1
                total_chunks += request.processing_info.get("total_chunks", 0)
                chunked_requests += 1
            else:
                processing_stats["active_simple_requests"] += 1
            
            # Find longest running request
            if request.started_at:
                duration = (current_time - request.started_at).total_seconds()
                if duration > longest_duration:
                    longest_duration = duration
                    longest_request_id = request.request_id
        
        if chunked_requests > 0:
            processing_stats["average_chunks_per_request"] = total_chunks / chunked_requests
        
        if longest_request_id:
            processing_stats["longest_running_request"] = {
                "request_id": longest_request_id,
                "duration_seconds": longest_duration
            }
        
        return processing_stats
    
    def _get_queue_position(self, request_id: str) -> int:
        """Get position of request in queue (1-based)"""
        if request_id in self.requests:
            request = self.requests[request_id]
            if request.status == RequestStatus.QUEUED:
                # Count requests created before this one that are still queued
                position = 1
                for other_request in self.requests.values():
                    if (other_request.status == RequestStatus.QUEUED and 
                        other_request.created_at < request.created_at):
                        position += 1
                return position
        return 0
    
    def cleanup_old_requests(self, max_age_hours: int = 24):
        """Clean up old completed requests to prevent memory buildup"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_requests = []
        
        for request_id, request in self.requests.items():
            if (request.status in [RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.PARTIAL_SUCCESS] and
                request.completed_at and request.completed_at < cutoff_time):
                old_requests.append(request_id)
        
        for request_id in old_requests:
            del self.requests[request_id]
        
        if old_requests:
            logger.info(f"Cleaned up {len(old_requests)} old requests")
        
        return len(old_requests)

# Global enhanced queue instance
request_queue = RequestQueue(max_size=20)