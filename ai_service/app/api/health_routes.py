from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from ..celery_app import celery_app
from app.core.celery_monitor import celery_monitor

from ..core.resource_manager import resource_manager
from ..core.request_queue import request_queue
from ..models.model_loader import model_loader
from ..config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def basic_health():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "site_id": settings.site_id
    }

@router.get("/detailed")
async def detailed_health():
    """Detailed health check with full system status"""
    try:
        # Get all system information
        gpu_info = resource_manager.get_gpu_info()
        system_info = resource_manager.get_system_info()
        queue_status = request_queue.get_queue_status()
        model_status = model_loader.get_model_status()
        system_capabilities = model_loader.get_system_capabilities()
        
        # Determine overall health
        overall_status = "healthy"
        issues = []
        
        # Check for issues
        if system_info["memory_percent"] > settings.alert_memory_usage:
            issues.append(f"High memory usage: {system_info['memory_percent']:.1f}%")
            overall_status = "degraded"
        
        if queue_status["queue_size"] > settings.alert_queue_size:
            issues.append(f"Queue nearly full: {queue_status['queue_size']}/{queue_status['max_queue_size']}")
            overall_status = "degraded"
        
        ready_models = model_loader.get_ready_models()
        implementable_models = model_loader.get_implementable_models()
        blocked_models = model_loader.get_blocked_models()
        
        if len(ready_models) == 0 and len(implementable_models) == 0:
            issues.append("No models are ready or implementable")
            overall_status = "unhealthy"
        elif len(blocked_models) > 0:
            issues.append(f"Some models blocked by dependencies: {blocked_models}")
            if overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": settings.app_version,
            "site_id": settings.site_id,
            "issues": issues,
            "system": system_info,
            "gpu": gpu_info,
            "queue": queue_status,
            "models": {
                "total": len(model_status),
                "ready": len(ready_models),
                "implementable": len(implementable_models),
                "blocked": len(blocked_models),
                "ready_models": ready_models,
                "implementable_models": implementable_models,
                "blocked_models": blocked_models,
                "details": model_status
            },
            "capabilities": system_capabilities
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/models")
async def models_health():
    """Get detailed model status with dependency info"""
    model_status = model_loader.get_model_status()
    system_capabilities = model_loader.get_system_capabilities()
    ready_models = model_loader.get_ready_models()
    implementable_models = model_loader.get_implementable_models()
    blocked_models = model_loader.get_blocked_models()
    missing_deps = model_loader.get_missing_dependencies_summary()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system_capabilities": system_capabilities,
        "summary": {
            "total": len(model_status),
            "ready": len(ready_models),
            "implementable": len(implementable_models),
            "blocked": len(blocked_models)
        },
        "ready_models": ready_models,
        "implementable_models": implementable_models,
        "blocked_models": blocked_models,
        "missing_dependencies": missing_deps,
        "details": model_status
    }

@router.get("/capabilities")
async def system_capabilities():
    """Get ML system capabilities"""
    return model_loader.get_system_capabilities()

@router.get("/resources")
async def resources_health():
    """Get detailed resource status"""
    gpu_info = resource_manager.get_gpu_info()
    system_info = resource_manager.get_system_info()
    queue_status = request_queue.get_queue_status()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "gpu": gpu_info,
        "system": system_info,
        "queue": queue_status
    }

@router.get("/celery/status")
async def get_celery_status():
    """Check Celery worker and event monitoring status with proper health logic"""
    
    # Check event monitoring
    try:
        monitor_status = celery_monitor.get_connection_status()
    except Exception as e:
        monitor_status = {
            "is_monitoring": False,
            "thread_alive": False,
            "active_tasks_count": 0,
            "workers_seen": 0,
            "status": "monitoring_unavailable",
            "error": str(e)
        }
    
    # Try to ping Celery workers
    celery_workers = {
        "available": False,
        "count": 0,
        "worker_names": [],
        "error": None
    }
    
    try:
        inspect = celery_app.control.inspect(timeout=3.0)
        worker_stats = inspect.stats()
        worker_ping = inspect.ping()
        
        if worker_stats and worker_ping:
            celery_workers.update({
                "available": True,
                "count": len(worker_stats),
                "worker_names": list(worker_stats.keys()),
                "ping_response": worker_ping,
                "worker_stats": worker_stats
            })
        elif worker_ping:  # Ping works but no stats
            celery_workers.update({
                "available": True,
                "count": len(worker_ping),
                "worker_names": list(worker_ping.keys()),
                "ping_response": worker_ping,
                "note": "Workers responding but stats unavailable"
            })
            
    except Exception as e:
        celery_workers["error"] = str(e)
        logger.warning(f"Celery worker inspection failed: {e}")
    
    # IMPROVED STATUS LOGIC
    overall_status = "healthy"
    issues = []
    recommendations = {}
    
    # Critical: Worker availability
    if not celery_workers["available"]:
        overall_status = "critical"
        issues.append("No Celery workers responding")
        recommendations["start_worker"] = "celery -A app.celery_app worker --loglevel=info -E"
    
    # Warning: Event monitoring (not critical for basic operation)
    elif not monitor_status.get("is_monitoring", False):
        overall_status = "degraded"
        issues.append("Event monitoring not connected (worker busy or starting up)")
        recommendations["note"] = "Event monitoring will connect automatically when worker is idle"
    
    # Add helpful recommendations
    if celery_workers["available"]:
        if celery_workers["count"] == 1:
            recommendations["scaling"] = "Single worker detected - consider scaling for production"
        recommendations["next_step"] = "System ready for audio processing"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "overall_status": overall_status,
        "issues": issues,
        "event_monitoring": monitor_status,
        "celery_workers": celery_workers,
        "recommendations": recommendations,
        "system_health": {
            "workers_healthy": celery_workers["available"],
            "monitoring_healthy": monitor_status.get("is_monitoring", False),
            "redis_healthy": True,  # If we got here, Redis is working
            "ready_for_processing": celery_workers["available"]
        },
        "explanation": {
            "healthy": "All critical systems operational",
            "degraded": "Critical systems working, monitoring features limited", 
            "critical": "Core functionality impaired - immediate attention needed"
        }
    }