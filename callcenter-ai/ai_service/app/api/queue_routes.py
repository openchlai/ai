from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..core.request_queue import request_queue

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/queue", tags=["queue"])

@router.get("/status")
async def get_queue_status():
    """Get current queue status"""
    return request_queue.get_queue_status()

@router.get("/status/{request_id}")
async def get_request_status(request_id: str):
    """Get status of a specific request"""
    status = request_queue.get_request_status(request_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return status

@router.get("/metrics")
async def get_queue_metrics():
    """Get queue performance metrics"""
    queue_status = request_queue.get_queue_status()
    
    # Calculate additional metrics
    total_requests = queue_status["total_requests"]
    completed_requests = queue_status["completed_requests"]
    failed_requests = queue_status["failed_requests"]
    
    success_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
    failure_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
    
    return {
        **queue_status,
        "success_rate_percent": round(success_rate, 2),
        "failure_rate_percent": round(failure_rate, 2),
        "queue_utilization_percent": round(queue_status["queue_size"] / queue_status["max_queue_size"] * 100, 2)
    }

@router.delete("/request/{request_id}")
async def cancel_request(request_id: str):
    """Cancel a queued request (if still in queue)"""
    status = request_queue.get_request_status(request_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if status["status"] == "processing":
        raise HTTPException(status_code=400, detail="Cannot cancel request that is already processing")
    
    if status["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Request already completed")
    
    # Mark as cancelled (you'll need to implement this in request_queue)
    request_queue.complete_request(request_id, error="Cancelled by user")
    
    return {"message": "Request cancelled successfully"}