from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from celery.result import AsyncResult
from datetime import datetime
import logging

from ..celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/task", tags=["tasks"])

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    result: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None
    progress: Optional[int] = None
    step: Optional[str] = None
    processing_time: Optional[float] = None
    timestamp: str

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of any inference task
    
    Parameters:
    - task_id: The Celery task ID returned from inference endpoints
    
    Returns:
    - TaskStatusResponse with current status and results
    """
    try:
        # Get task result from Celery
        task = AsyncResult(task_id, app=celery_app)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        # Determine status
        if task.ready():
            if task.successful():
                # Task completed successfully
                result = task.result
                
                return TaskStatusResponse(
                    task_id=task_id,
                    status="completed",
                    result=result,
                    processing_time=result.get("processing_time") if isinstance(result, dict) else None,
                    timestamp=datetime.now().isoformat()
                )
            else:
                # Task failed
                error_info = task.info
                error_message = str(error_info) if error_info else "Unknown error"
                
                # Extract error details if available
                processing_time = None
                if isinstance(error_info, dict):
                    error_message = error_info.get("error", str(error_info))
                    processing_time = error_info.get("processing_time")
                
                return TaskStatusResponse(
                    task_id=task_id,
                    status="failed",
                    error=error_message,
                    processing_time=processing_time,
                    timestamp=datetime.now().isoformat()
                )
        else:
            # Task is still processing
            task_info = task.info or {}
            
            # Extract progress information
            progress = task_info.get("progress", 0)
            step = task_info.get("step", "processing")
            
            return TaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=progress,
                step=step,
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get task status for {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task status: {str(e)}"
        )

@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running inference task
    
    Parameters:
    - task_id: The Celery task ID to cancel
    
    Returns:
    - Confirmation of cancellation
    """
    try:
        task = AsyncResult(task_id, app=celery_app)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        if task.ready():
            return {
                "task_id": task_id,
                "status": "already_completed",
                "message": "Task has already completed and cannot be cancelled"
            }
        
        # Revoke the task
        celery_app.control.revoke(task_id, terminate=True)
        
        logger.info(f"🚫 Cancelled task {task_id}")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task has been cancelled",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to cancel task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )

@router.get("/")
async def list_active_tasks():
    """
    List all active inference tasks
    
    Returns:
    - List of active task IDs and their basic status
    """
    try:
        inspect = celery_app.control.inspect()
        
        # Get active tasks from all workers
        active_tasks = inspect.active()
        
        if not active_tasks:
            return {
                "active_tasks": [],
                "total_active": 0,
                "message": "No active tasks or no workers available"
            }
        
        # Flatten tasks from all workers
        all_tasks = []
        for worker_name, tasks in active_tasks.items():
            for task_info in tasks:
                task_data = {
                    "task_id": task_info["id"],
                    "task_name": task_info["name"],
                    "worker": worker_name,
                    "args": task_info.get("args", []),
                    "kwargs": task_info.get("kwargs", {}),
                    "time_start": task_info.get("time_start"),
                }
                
                # Get additional status info if available
                task_result = AsyncResult(task_info["id"], app=celery_app)
                if task_result.info:
                    task_data["progress"] = task_result.info.get("progress", 0)
                    task_data["step"] = task_result.info.get("step", "unknown")
                
                all_tasks.append(task_data)
        
        return {
            "active_tasks": all_tasks,
            "total_active": len(all_tasks),
            "workers_online": len(active_tasks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list active tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list active tasks: {str(e)}"
        )

@router.get("/stats")
async def get_task_stats():
    """
    Get task execution statistics
    
    Returns:
    - Statistics about task execution and worker health
    """
    try:
        inspect = celery_app.control.inspect()
        
        # Get comprehensive worker stats
        stats = inspect.stats()
        active_tasks = inspect.active()
        reserved_tasks = inspect.reserved()
        
        if not stats:
            return {
                "status": "no_workers",
                "message": "No workers are currently online",
                "timestamp": datetime.now().isoformat()
            }
        
        # Count tasks by type
        task_counts = {}
        total_active = 0
        total_reserved = 0
        
        # Count active tasks
        if active_tasks:
            for worker, tasks in active_tasks.items():
                total_active += len(tasks)
                for task in tasks:
                    task_name = task.get("name", "unknown")
                    task_counts[task_name] = task_counts.get(task_name, 0) + 1
        
        # Count reserved tasks
        if reserved_tasks:
            for worker, tasks in reserved_tasks.items():
                total_reserved += len(tasks)
        
        # Worker health info
        worker_info = []
        for worker_name, worker_stats in stats.items():
            worker_info.append({
                "worker_name": worker_name,
                "status": "online",
                "pool": worker_stats.get("pool", {}),
                "rusage": worker_stats.get("rusage", {}),
                "total_tasks": worker_stats.get("total", {})
            })
        
        return {
            "status": "healthy",
            "workers_online": len(stats),
            "total_active_tasks": total_active,
            "total_reserved_tasks": total_reserved,
            "task_counts_by_type": task_counts,
            "worker_details": worker_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get task stats: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }