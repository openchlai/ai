from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict
import logging
from datetime import datetime
import os

from ..model_scripts.model_loader import model_loader

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

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None)  # Use Form to accept both file and text data
):
    """
    Transcribe uploaded audio file to text
    
    Parameters:
    - audio: Audio file (wav, mp3, flac, m4a, ogg, webm)
    - language: Language code (e.g., 'en', 'sw', 'fr') or 'auto' for auto-detection
    """
    
    # Check if Whisper model is loaded
    if not model_loader.is_model_ready("whisper"):
        raise HTTPException(
            status_code=503, 
            detail="Whisper model not ready. Check /health/models for status."
        )
    
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
    
    try:
        start_time = datetime.now()
        
        # Get the loaded Whisper model
        whisper_model = model_loader.models.get("whisper")
        if not whisper_model:
            raise HTTPException(
                status_code=503,
                detail="Whisper model not available"
            )
        
        # Transcribe audio with language specification
        transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Get model info
        model_info = whisper_model.get_model_info()
        
        # Audio info
        audio_info = {
            "filename": audio.filename,
            "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
            "format": file_extension,
            "content_type": audio.content_type
        }
        
        logger.info(f"🎙️ Transcribed {audio.filename} ({audio_info['file_size_mb']}MB) in {processing_time:.2f}s")
        
        return TranscriptionResponse(
            transcript=transcript,
            language=language,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat(),
            audio_info=audio_info
        )
        
    except Exception as e:
        logger.error(f"❌ Transcription failed for {audio.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

@router.get("/info")
async def get_whisper_info():
    """Get Whisper model information"""
    if not model_loader.is_model_ready("whisper"):
        return {
            "status": "not_ready",
            "message": "Whisper model not loaded"
        }
    
    whisper_model = model_loader.models.get("whisper")
    if whisper_model:
        model_info = whisper_model.get_model_info()
        return {
            "status": "ready",
            "model_info": model_info
        }
    else:
        return {
            "status": "error",
            "message": "Whisper model not found",
            "model_info": {"error": "Model instance not found"}
        }

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    if not model_loader.is_model_ready("whisper"):
        return {
            "error": "Whisper model not ready",
            "supported_languages": {}
        }
    
    whisper_model = model_loader.models.get("whisper")
    if whisper_model:
        return {
            "supported_languages": whisper_model.get_supported_languages(),
            "total_supported": "99+ languages",
            "note": "Whisper supports many more languages beyond this list",
            "usage": "Pass language code in request: language='sw' for Swahili"
        }
    else:
        return {
            "error": "Whisper model not available",
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
            "optional": "language parameter",
            "examples": {
                "auto_detect": "curl -X POST -F 'audio=@sample.wav' http://localhost:8123/whisper/transcribe",
                "swahili": "curl -X POST -F 'audio=@sample.wav' -F 'language=sw' http://localhost:8123/whisper/transcribe",
                "english": "curl -X POST -F 'audio=@sample.wav' -F 'language=en' http://localhost:8123/whisper/transcribe"
            },
            "supported_formats": [".wav", ".mp3", ".flac", ".m4a", ".ogg", ".webm"],
            "max_file_size": "100MB",
            "task": "transcribe (not translate)",
            "language_detection": "Auto-detect or specify language code"
        },
        "model_status": await get_whisper_info(),
        "supported_languages": await get_supported_languages()
    }