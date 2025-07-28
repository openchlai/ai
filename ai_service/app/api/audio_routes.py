# app/api/audio_routes.py (Updated for Celery)
import asyncio
import json
from socket import socket
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import os

from ..tasks.audio_tasks import process_audio_task, process_audio_quick_task
from ..celery_app import celery_app
from ..core.celery_monitor import celery_monitor
from ..config.settings import redis_task_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audio", tags=["audio"])

# Response Models (keep your existing ones)
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: str
    status_endpoint: str

@router.post("/process", response_model=TaskResponse)
async def process_audio_complete(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    include_translation: bool = Form(True),
    include_insights: bool = Form(True),
    background: bool = Form(True)
):
    """
    Complete audio-to-insights pipeline with Celery
    """
    
    # Validate audio file
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    allowed_formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"]
    file_extension = os.path.splitext(audio.filename)[1].lower()
    if file_extension not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {file_extension}. Supported: {allowed_formats}"
        )
    
    max_size = 100 * 1024 * 1024  # 100MB
    audio_bytes = await audio.read()
    if len(audio_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {len(audio_bytes)/1024/1024:.1f}MB. Max: {max_size/1024/1024}MB"
        )
    
    try:
        if background:
            # Submit to Celery
            task = process_audio_task.delay(
                audio_bytes=audio_bytes,
                filename=audio.filename,
                language=language,
                include_translation=include_translation,
                include_insights=include_insights
            )
            
            logger.info(f"🎙️ Submitted audio processing task {task.id} for {audio.filename}")
            
            return TaskResponse(
                task_id=task.id,
                status="queued",
                message="Audio processing started. Check status at /audio/task/{task_id}",
                estimated_time="15-45 seconds",
                status_endpoint=f"/audio/task/{task.id}"
            )
        else:
            # Synchronous processing
            result = process_audio_task(
                audio_bytes=audio_bytes,
                filename=audio.filename,
                language=language,
                include_translation=include_translation,
                include_insights=include_insights
            )
            return result
            
    except Exception as e:
        logger.error(f"❌ Audio processing failed for {audio.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )

@router.post("/analyze", response_model=TaskResponse)
async def quick_audio_analysis(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    background: bool = Form(True)
):
    """
    Quick audio analysis with Celery
    """
    
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    allowed_formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"]
    file_extension = os.path.splitext(audio.filename)[1].lower()
    if file_extension not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {file_extension}")
    
    audio_bytes = await audio.read()
    max_size = 50 * 1024 * 1024  # 50MB
    if len(audio_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large for quick analysis: {len(audio_bytes)/1024/1024:.1f}MB. Max: 50MB"
        )
    
    try:
        if background:
            task = process_audio_quick_task.delay(
                audio_bytes=audio_bytes,
                filename=audio.filename,
                language=language
            )
            
            return TaskResponse(
                task_id=task.id,
                status="queued",
                message="Quick analysis started",
                estimated_time="10-20 seconds",
                status_endpoint=f"/audio/task/{task.id}"
            )
        else:
            result = process_audio_quick_task(
                audio_bytes=audio_bytes,
                filename=audio.filename,
                language=language
            )
            return result
            
    except Exception as e:
        logger.error(f"❌ Quick analysis failed for {audio.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get Celery task status with detailed progress"""
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "status": "queued",
                "progress": 0,
                "message": "Task is waiting to be processed"
            }
        elif task.state == "PROCESSING":
            response = {
                "task_id": task_id,
                "status": "processing",
                "progress": task.info.get("progress", 0),
                "current_step": task.info.get("step", "unknown"),
                "filename": task.info.get("filename", "unknown")
            }
        elif task.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "result": task.result,
                "processing_time": task.result.get("processing_time", 0) if task.result else 0
            }
        elif task.state == "FAILURE":
            response = {
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info),
                "filename": task.info.get("filename", "unknown") if isinstance(task.info, dict) else "unknown"
            }
        else:
            response = {
                "task_id": task_id,
                "status": task.state.lower(),
                "info": task.info
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving task status")

@router.get("/tasks/active")
async def get_active_tasks():
    """Get all active audio processing tasks"""
    try:
            # Try event-based monitoring first (most reliable)
            event_data = celery_monitor.get_active_tasks()
            
            # Filter for audio tasks only
            audio_tasks = [
                task for task in event_data["active_tasks"] 
                if task.get("name") in ["process_audio_task", "process_audio_quick_task"]
            ]
            
            # Add Redis fallback for additional reliability
            redis_active = redis_task_client.hgetall("active_audio_tasks")
            
            return {
                "active_tasks": audio_tasks,
                "total_active": len(audio_tasks),
                "data_sources": {
                    "celery_events": len(event_data["active_tasks"]),
                    "redis_backup": len(redis_active)
                },
                "note": "Workers may appear offline during intensive processing - this is normal"
            }
        
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        return {"active_tasks": [], "total_active": 0, "error": str(e), "note": "Monitoring may be temporarily unavailable during heavy load"}

@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a Celery task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} cancelled successfully"}
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error cancelling task")

@router.get("/queue/status")
async def get_queue_status():
    """Get overall queue status from Celery"""
    try:
        inspect = celery_app.control.inspect(timeout=5.0)
        
        # Get stats from all workers
        stats = None
        for attempt in range(3):
            try:
                stats = inspect.stats()
                if stats:
                    break
                await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s backoff
            except Exception as e:
                logger.warning(f"Inspection attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # Last attempt
                    # Fallback to basic status
                    return {
                        "status": "inspection_timeout",
                        "message": "Workers busy - monitoring temporarily unavailable",
                        "workers": "unknown",
                        "note": "This is normal during heavy processing"
                    }
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        if not stats:
            return {
                "status": "no_workers",
                "message": "No Celery workers are running",
                "workers": 0
            }
        
        total_active = sum(len(tasks) for tasks in active.values()) if active else 0
        total_scheduled = sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0
        total_reserved = sum(len(tasks) for tasks in reserved.values()) if reserved else 0
        
        worker_info = []
        for worker_name, worker_stats in stats.items():
            worker_info.append({
                "name": worker_name,
                "status": "online",
                "total_tasks": worker_stats.get("total", {}),
                "current_load": len(active.get(worker_name, [])) if active else 0
            })
        
        return {
            "status": "healthy",
            "workers": len(stats),
            "worker_info": worker_info,
            "queue_stats": {
                "active_tasks": total_active,
                "scheduled_tasks": total_scheduled,
                "reserved_tasks": total_reserved,
                "total_pending": total_active + total_scheduled + total_reserved
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return {
            "status": "error",
            "message": str(e),
            "workers": 0
        }
        
@router.get("/workers/status")
async def get_worker_status():
    """Get worker status with explanation of 'offline' behavior"""
    try:
        # Get from event monitor
        worker_stats = celery_monitor.get_worker_stats()
        
        # Get from Celery inspection (with timeout)
        inspect = celery_app.control.inspect(timeout=2.0)
        try:
            celery_stats = inspect.stats()
            active_tasks = inspect.active()
        except Exception as e:
            celery_stats = None
            active_tasks = None
            logger.info(f"Worker inspection timeout (normal during processing): {e}")
        
        return {
            "event_monitoring": worker_stats,
            "celery_inspection": {
                "available": celery_stats is not None,
                "stats": celery_stats,
                "active": active_tasks
            },
            "explanation": {
                "offline_during_processing": "Normal - workers can't respond to pings during GPU-intensive tasks",
                "monitoring_reliability": "Event monitoring is more reliable than inspection during processing"
            }
        }
        
    except Exception as e:
        return {"error": str(e)}
    
@router.post("/process-stream")
async def process_audio_streaming(
   audio: UploadFile = File(...),
   language: Optional[str] = Form(None),
   include_translation: bool = Form(True),
   include_insights: bool = Form(True)
):
   """
   Process audio with real-time updates via Server-Sent Events (SSE)
   Eliminates the need for polling - server pushes updates to client
   """
   
   # Validate audio file
   if not audio.filename:
       raise HTTPException(status_code=400, detail="No audio file provided")
   
   allowed_formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"]
   file_extension = os.path.splitext(audio.filename)[1].lower()
   if file_extension not in allowed_formats:
       raise HTTPException(
           status_code=400,
           detail=f"Unsupported audio format: {file_extension}. Supported: {allowed_formats}"
       )
   
   max_size = 100 * 1024 * 1024  # 100MB
   audio_bytes = await audio.read()
   if len(audio_bytes) > max_size:
       raise HTTPException(
           status_code=400,
           detail=f"File too large: {len(audio_bytes)/1024/1024:.1f}MB. Max: {max_size/1024/1024}MB"
       )
   
   try:
       # Submit task to Celery
       task = process_audio_task.delay(
           audio_bytes=audio_bytes,
           filename=audio.filename,
           language=language,
           include_translation=include_translation,
           include_insights=include_insights
       )
       task_id = task.id
       
       logger.info(f"🎙️ Started SSE stream for task {task_id} - {audio.filename}")
       
       async def event_stream():
           """Stream real-time updates to client"""
           last_status = None
           last_progress = None
           start_time = datetime.now()
           max_duration = 300  # 5 minutes timeout
           heartbeat_interval = 10  # Send heartbeat every 10 seconds
           last_heartbeat = start_time
           
           # Send initial confirmation
           initial_update = {
               "task_id": task_id,
               "status": "submitted",
               "message": "Audio processing started",
               "filename": audio.filename,
               "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
               "estimated_time": "15-60 seconds",
               "timestamp": datetime.now().isoformat()
           }
           yield f"data: {json.dumps(initial_update)}\n\n"
           
           while True:
               try:
                   current_time = datetime.now()
                   elapsed_seconds = (current_time - start_time).total_seconds()
                   
                   # Check timeout
                   if elapsed_seconds > max_duration:
                       timeout_msg = {
                           "task_id": task_id,
                           "status": "timeout",
                           "error": "Processing timeout after 5 minutes",
                           "elapsed_time": elapsed_seconds,
                           "timestamp": current_time.isoformat()
                       }
                       yield f"data: {json.dumps(timeout_msg)}\n\n"
                       logger.warning(f"⏰ Task {task_id} timed out after {elapsed_seconds:.1f}s")
                       break
                   
                   # Get current task status
                   task_result = celery_app.AsyncResult(task_id)
                   current_status = task_result.status
                   current_info = task_result.info if task_result.info else {}
                   
                   # Determine if we should send an update
                   status_changed = current_status != last_status
                   progress_changed = False
                   need_heartbeat = (current_time - last_heartbeat).total_seconds() >= heartbeat_interval
                   
                   if isinstance(current_info, dict) and 'progress' in current_info:
                       progress_changed = current_info['progress'] != last_progress
                       last_progress = current_info['progress']
                   
                   should_send_update = status_changed or progress_changed or need_heartbeat
                   
                   if should_send_update:
                       update = {
                           "task_id": task_id,
                           "status": current_status,
                           "elapsed_time": round(elapsed_seconds, 1),
                           "timestamp": current_time.isoformat()
                       }
                       
                       # Add progress and step info if available
                       if isinstance(current_info, dict):
                           if 'progress' in current_info:
                               update["progress"] = current_info['progress']
                           if 'step' in current_info:
                               update["step"] = current_info['step']
                           if 'message' in current_info:
                               update["message"] = current_info['message']
                           if 'filename' in current_info:
                               update["filename"] = current_info['filename']
                       
                       # Add helpful status messages for different states
                       if current_status == "PENDING":
                           update["message"] = "Task queued, waiting for available worker"
                           update["progress"] = 0
                       elif current_status == "PROCESSING":
                           if 'step' not in update:
                               update["step"] = "processing"
                           if 'message' not in update:
                               step = update.get('step', 'processing')
                               update["message"] = f"Processing: {step}"
                       elif current_status == "RETRY":
                           update["message"] = "Task failed, retrying automatically"
                       
                       # Send heartbeat indicator
                       if need_heartbeat and not status_changed and not progress_changed:
                           update["heartbeat"] = True
                           last_heartbeat = current_time
                       
                       yield f"data: {json.dumps(update)}\n\n"
                       last_status = current_status
                   
                   # Handle completed states
                   if current_status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                       if current_status == 'SUCCESS':
                           final_result = {
                               "task_id": task_id,
                               "status": "completed",
                               "result": task_result.result,
                               "processing_time": round(elapsed_seconds, 2),
                               "timestamp": current_time.isoformat(),
                               "message": "Audio processing completed successfully"
                           }
                           logger.info(f"✅ SSE task {task_id} completed in {elapsed_seconds:.1f}s")
                           
                       elif current_status == 'FAILURE':
                           error_info = str(current_info) if current_info else "Unknown error"
                           final_result = {
                               "task_id": task_id,
                               "status": "failed", 
                               "error": error_info,
                               "processing_time": round(elapsed_seconds, 2),
                               "timestamp": current_time.isoformat(),
                               "message": "Audio processing failed"
                           }
                           logger.error(f"❌ SSE task {task_id} failed after {elapsed_seconds:.1f}s: {error_info}")
                           
                       elif current_status == 'REVOKED':
                           final_result = {
                               "task_id": task_id,
                               "status": "cancelled",
                               "processing_time": round(elapsed_seconds, 2),
                               "timestamp": current_time.isoformat(),
                               "message": "Audio processing was cancelled"
                           }
                           logger.info(f"🚫 SSE task {task_id} was cancelled after {elapsed_seconds:.1f}s")
                       
                       yield f"data: {json.dumps(final_result)}\n\n"
                       break
                   
                   # Wait before next check
                   await asyncio.sleep(2)
                   
               except Exception as e:
                   logger.error(f"❌ SSE stream error for task {task_id}: {e}")
                   error_update = {
                       "task_id": task_id,
                       "status": "stream_error",
                       "error": str(e),
                       "elapsed_time": (datetime.now() - start_time).total_seconds(),
                       "timestamp": datetime.now().isoformat(),
                       "message": "Streaming connection error"
                   }
                   yield f"data: {json.dumps(error_update)}\n\n"
                   break
           
           # Stream cleanup
           logger.info(f"🔚 SSE stream ended for task {task_id}")
       
       return StreamingResponse(
           event_stream(), 
           media_type="text/event-stream",
           headers={
               "Cache-Control": "no-cache",
               "Connection": "keep-alive",
               "X-Accel-Buffering": "no",  # Disable nginx buffering
               "Access-Control-Allow-Origin": "*",  # Enable CORS for SSE
               "Access-Control-Allow-Headers": "Cache-Control",
           }
       )
       
   except Exception as e:
       logger.error(f"❌ SSE audio processing failed for {audio.filename}: {e}")
       raise HTTPException(
           status_code=500, 
           detail=f"Failed to start audio processing: {str(e)}"
       )