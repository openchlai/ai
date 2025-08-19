from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import logging
from datetime import datetime
import os
from celery.exceptions import TimeoutError as CeleryTimeoutError

from ..tasks.inference_tasks import whisper_transcribe_inference, whisper_get_info, whisper_get_languages

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whisper", tags=["whisper"])

class TranscriptionRequest(BaseModel):
    language: Optional[str] = None  # e.g., "en", "sw", "fr", "auto"

class TranscriptionResponse(BaseModel):
    transcript: str
    language: Optional[str]
    processing_time: float
    model_info: Dict
    timestamp: str
    audio_info: Dict

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),  # Use Form to accept both file and text data
    task_type: Optional[str] = Form("transcribe")  # "transcribe" or "translate"
):
    """
    Transcribe uploaded audio file to text using hybrid sync/async pattern
    
    Parameters:
    - audio: Audio file (wav, mp3, flac, m4a, ogg, webm)
    - language: Language code (e.g., 'en', 'sw', 'fr') or 'auto' for auto-detection
    - task_type: "transcribe" (same language) or "translate" (to English)
    
    Returns:
    - 200 OK: Immediate result if processing completes within 10 seconds
    - 202 Accepted: Task started, use /task/{task_id} to check status
    """
    
    # Validate audio file
    if not audio.filename:
        raise HTTPException(
            status_code=400,
            detail="No audio file provided"
        )
    
    # Check file format
    allowed_formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"]
    file_extension = os.path.splitext(audio.filename)[1].lower()
    if file_extension not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {file_extension}. Supported: {allowed_formats}"
        )
    
    # Check file size (100MB limit)
    max_size = 100 * 1024 * 1024  # 100MB
    audio_bytes = await audio.read()
    if len(audio_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {len(audio_bytes)/1024/1024:.1f}MB. Max: {max_size/1024/1024}MB"
        )
    
    # Validate task_type
    if task_type not in ["transcribe", "translate"]:
        raise HTTPException(
            status_code=400,
            detail="task_type must be 'transcribe' or 'translate'"
        )
    
    try:
        # Start Celery task
        task = whisper_transcribe_inference.delay(audio_bytes, language, task_type)
        
        try:
            # Try to get result quickly (10 second timeout)
            result = task.get(timeout=10)
            
            # Add original filename and format info to result
            result["audio_info"].update({
                "filename": audio.filename,
                "format": file_extension,
                "content_type": audio.content_type
            })
            
            logger.info(f"🎙️ Transcribed {audio.filename} immediately in {result['processing_time']:.2f}s")
            
            # Return immediate success (200 OK)
            return TranscriptionResponse(**result)
            
        except CeleryTimeoutError:
            # System is busy, return task ID for async polling (202 Accepted)
            logger.info(f"⏰ Transcription queued for {audio.filename}, task_id: {task.id}")
            
            return JSONResponse(
                status_code=202,
                content={
                    "status": "processing",
                    "task_id": task.id,
                    "message": "System busy, processing in background",
                    "polling_url": f"/task/{task.id}",
                    "estimated_time": "30-60 seconds",
                    "audio_info": {
                        "filename": audio.filename,
                        "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
                        "format": file_extension,
                        "task_type": task_type,
                        "language": language
                    },
                    "instructions": {
                        "check_status": f"GET /task/{task.id}",
                        "cancel_task": f"DELETE /task/{task.id}",
                        "list_all_tasks": "GET /task/"
                    }
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Transcription task failed for {audio.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start transcription task: {str(e)}"
        )

@router.get("/info")
async def get_whisper_info():
    """Get Whisper model information from Celery workers"""
    try:
        # Start task to get model info
        task = whisper_get_info.delay()
        
        try:
            # Try to get result quickly (5 second timeout)
            result = task.get(timeout=5)
            return result
            
        except CeleryTimeoutError:
            # Workers are busy, return task ID
            return JSONResponse(
                status_code=202,
                content={
                    "status": "processing",
                    "task_id": task.id,
                    "message": "Retrieving model info from workers",
                    "polling_url": f"/task/{task.id}"
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get Whisper info: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve model info: {str(e)}"
        }

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages from Celery workers"""
    try:
        # Start task to get languages
        task = whisper_get_languages.delay()
        
        try:
            # Try to get result quickly (3 second timeout)
            result = task.get(timeout=3)
            
            # Add usage information
            if "supported_languages" in result:
                result["usage"] = "Pass language code in request: language='sw' for Swahili"
                result["translation_usage"] = "Use task_type='translate' to translate to English"
            
            return result
            
        except CeleryTimeoutError:
            # Workers are busy, return task ID
            return JSONResponse(
                status_code=202,
                content={
                    "status": "processing", 
                    "task_id": task.id,
                    "message": "Retrieving supported languages from workers",
                    "polling_url": f"/task/{task.id}"
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Failed to get supported languages: {e}")
        return {
            "error": f"Failed to retrieve supported languages: {str(e)}",
            "supported_languages": {}
        }

@router.post("/demo")
async def whisper_demo():
    """Demo endpoint - returns model info and usage example"""
    return {
        "demo_info": {
            "endpoint": "/whisper/transcribe",
            "method": "POST",
            "required": "audio file (multipart/form-data)",
            "optional": ["language parameter", "task_type parameter"],
            "hybrid_behavior": {
                "fast_response": "Results returned immediately if processed within 10 seconds (200 OK)",
                "busy_system": "Task queued for background processing (202 Accepted with task_id)",
                "polling": "Use GET /task/{task_id} to check status of queued tasks"
            },
            "examples": {
                "transcribe_auto": "curl -X POST -F 'audio=@sample.wav' http://localhost:8123/whisper/transcribe",
                "transcribe_swahili": "curl -X POST -F 'audio=@sample.wav' -F 'language=sw' http://localhost:8123/whisper/transcribe",
                "translate_swahili_to_english": "curl -X POST -F 'audio=@sample.wav' -F 'language=sw' -F 'task_type=translate' http://localhost:8123/whisper/transcribe",
                "check_task_status": "curl -X GET http://localhost:8123/task/{task_id}"
            },
            "supported_formats": [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"],
            "max_file_size": "100MB",
            "tasks_supported": ["transcribe (same language)", "translate (to English)"],
            "language_detection": "Auto-detect or specify language code"
        },
        "model_status": await get_whisper_info(),
        "supported_languages": await get_supported_languages()
    }