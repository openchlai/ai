from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import logging
import asyncio
import json
import time
import threading
from datetime import datetime
import base64

from ..models.model_loader import model_loader
from ..core.resource_manager import resource_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/realtime", tags=["realtime"])

# Global model instance - initialize once and share across connections
_realtime_model = None
_model_lock = asyncio.Lock()


class RealtimeConnectionManager:
    """Manages WebSocket connections for realtime transcription"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_buffers: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Initialize buffer for this connection
        self.connection_buffers[websocket] = {
            "audio_buffer": bytearray(),
            "offset": 0,
            "session_id": f"session_{int(time.time())}_{len(self.active_connections)}",
            "start_time": time.time(),
            "total_bytes": 0
        }
        
        logger.info(f"WebSocket connection established. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_buffers:
            del self.connection_buffers[websocket]
        logger.info(f"WebSocket connection closed. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")

# Global connection manager
connection_manager = RealtimeConnectionManager()

async def initialize_realtime_model():
    """Initialize the realtime model using the existing model_loader"""
    global _realtime_model

    async with _model_lock:
        if _realtime_model is None:
            try:
                logger.info("Initializing realtime transcription model...")
                start_time = time.time()
                
                # Check if whisper model is available via model_loader
                if not model_loader.is_model_ready("whisper"):
                    logger.info("Loading whisper model via model_loader...")
                    await model_loader._load_model("whisper")
                
                if not model_loader.is_model_ready("whisper"):
                    raise HTTPException(status_code=500, detail="Whisper model not available via model_loader")
                
                # Try to import and load the realtime components
                try:
                    from ..core.realtime.aii import load_model as realtime_load_model
                    from ..core.realtime.aii import transcribe as realtime_transcribe
                    
                    # Load the realtime model components
                    model, tokenizer, transcribe_options, decode_options = realtime_load_model()
                    
                    _realtime_model = {
                        "model": model,
                        "tokenizer": tokenizer,
                        "transcribe_options": transcribe_options,
                        "decode_options": decode_options,
                        "transcribe_func": realtime_transcribe,
                        "loaded_at": datetime.now().isoformat(),
                        "load_time": time.time() - start_time,
                        "type": "realtime_native"
                    }
                    
                    logger.info(f"Realtime model loaded successfully in {_realtime_model['load_time']:.2f}s")
                    
                except ImportError as import_error:
                    logger.warning(f"Could not load realtime components, falling back to regular whisper: {import_error}")
                    
                    # Fallback to using the regular whisper model from model_loader
                    whisper_model = model_loader.models.get("whisper")
                    
                    _realtime_model = {
                        "model": whisper_model,
                        "tokenizer": None,
                        "transcribe_options": None,
                        "decode_options": None,
                        "transcribe_func": None,
                        "loaded_at": datetime.now().isoformat(),
                        "load_time": time.time() - start_time,
                        "type": "fallback_whisper"
                    }
                    
                    logger.info(f"Fallback whisper model ready in {_realtime_model['load_time']:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to load realtime model: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to initialize realtime model: {str(e)}")
    
    return _realtime_model

# Response Models
class RealtimeStatusResponse(BaseModel):
    status: str
    model_loaded: bool
    active_connections: int
    model_info: Optional[Dict[str, Any]]
    system_info: Dict[str, Any]

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    tokens: Optional[List[int]] = None

class RealtimeTranscriptionResponse(BaseModel):
    session_id: str
    segments: List[TranscriptionSegment]
    processing_time: float
    buffer_info: Dict[str, Any]
    timestamp: str

# REST Endpoints
@router.get("/status", response_model=RealtimeStatusResponse)
async def get_realtime_status():
    """Get the status of the realtime transcription service"""
    
    global _realtime_model
    model_loaded = _realtime_model is not None
    
    model_info = None
    if model_loaded:
        model_info = {
            "loaded_at": _realtime_model["loaded_at"],
            "load_time": _realtime_model["load_time"],
            "type": _realtime_model["type"]
        }
        
        # Add additional info if available
        if _realtime_model["type"] == "realtime_native" and _realtime_model["model"]:
            model_info.update({
                "device": str(_realtime_model["model"].device),
                "is_multilingual": getattr(_realtime_model["model"], "is_multilingual", True),
                "num_languages": getattr(_realtime_model["model"], "num_languages", 99)
            })
    
    return RealtimeStatusResponse(
        status="ready" if model_loaded else "not_ready",
        model_loaded=model_loaded,
        active_connections=len(connection_manager.active_connections),
        model_info=model_info,
        system_info=resource_manager.get_system_info()
    )

@router.post("/initialize")
async def initialize_model():
    """Manually initialize the realtime model"""
    try:
        model_info = await initialize_realtime_model()
        return {
            "status": "success",
            "message": "Realtime model initialized successfully",
            "model_info": {
                "loaded_at": model_info["loaded_at"],
                "load_time": model_info["load_time"],
                "type": model_info["type"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to initialize realtime model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@router.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription
    
    Expected message format:
    {
        "type": "audio_data",
        "data": "<base64_encoded_audio>",
        "format": "pcm_s16le",
        "sample_rate": 16000,
        "language": "en"
    }
    
    Or for configuration:
    {
        "type": "config",
        "language": "en",
        "initial_prompt": "",
        "temperature": 0.0
    }
    """
    
    await connection_manager.connect(websocket)
    buffer_info = connection_manager.connection_buffers[websocket]
    
    try:
        # Initialize model if not loaded
        if _realtime_model is None:
            await initialize_realtime_model()
        
        model_data = _realtime_model
        
        # Send initial connection message
        model_info = {
            "type": model_data["type"],
            "loaded_at": model_data["loaded_at"]
        }
        
        if model_data["type"] == "realtime_native" and model_data["model"]:
            model_info.update({
                "device": str(model_data["model"].device),
                "is_multilingual": getattr(model_data["model"], "is_multilingual", True),
                "num_languages": getattr(model_data["model"], "num_languages", 99)
            })
        
        await connection_manager.send_personal_message({
            "type": "connection_established",
            "session_id": buffer_info["session_id"],
            "model_info": model_info,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "audio_data":
                    # Process audio data
                    await process_audio_message(websocket, message, model_data, buffer_info)
                
                elif message_type == "config":
                    # Update configuration
                    await process_config_message(websocket, message, model_data)
                
                elif message_type == "ping":
                    # Respond to ping
                    await connection_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                else:
                    await connection_manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }, websocket)
                    
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": f"Processing error: {str(e)}"
                }, websocket)
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info(f"Client disconnected: {buffer_info['session_id']}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)

async def process_audio_message(websocket: WebSocket, message: Dict, model_data: Dict, buffer_info: Dict):
    """Process incoming audio data and perform transcription"""
    
    try:
        # Decode audio data
        audio_data_b64 = message.get("data", "")
        audio_bytes = base64.b64decode(audio_data_b64)
        
        # Add to buffer
        buffer_info["audio_buffer"].extend(audio_bytes)
        buffer_info["total_bytes"] += len(audio_bytes)
        
        buffer_length = len(buffer_info["audio_buffer"])
        
        # Process if we have enough data (equivalent to 5 seconds at 16kHz, 16-bit)
        # 5 seconds * 16000 samples/sec * 2 bytes/sample = 160000 bytes
        chunk_size = 160000
        
        if (buffer_length - buffer_info["offset"]) >= chunk_size:
            
            start_time = time.time()
            
            # Choose transcription method based on model type
            if model_data["type"] == "realtime_native" and model_data["transcribe_func"]:
                # Use the realtime transcribe function
                processing_chunk = buffer_info["audio_buffer"][buffer_info["offset"]:]
                
                segments = model_data["transcribe_func"](
                    model_data["model"],
                    model_data["tokenizer"], 
                    model_data["transcribe_options"],
                    model_data["decode_options"],
                    processing_chunk
                )
                
                # Convert segments to response format
                response_segments = []
                for segment in segments:
                    response_segments.append({
                        "start": segment["start"],
                        "end": segment["end"], 
                        "text": segment["text"],
                        "tokens": segment.get("tokens", [])
                    })
                
            else:
                # Fallback: use regular whisper model
                # For now, just return a placeholder response
                response_segments = [{
                    "start": 0.0,
                    "end": 5.0,
                    "text": f"[Fallback] Received {len(audio_bytes)} bytes of audio data",
                    "tokens": []
                }]
            
            processing_time = time.time() - start_time
            
            # Send transcription result
            response = {
                "type": "transcription",
                "session_id": buffer_info["session_id"],
                "segments": response_segments,
                "processing_time": processing_time,
                "buffer_info": {
                    "buffer_length_bytes": buffer_length,
                    "buffer_length_seconds": buffer_length / 32000,  # Assuming 16kHz, 16-bit
                    "total_bytes_received": buffer_info["total_bytes"],
                    "session_duration": time.time() - buffer_info["start_time"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await connection_manager.send_personal_message(response, websocket)
            
            # Update offset
            buffer_info["offset"] += chunk_size
            
            # Clear buffer if it gets too large (30 seconds worth = 960000 bytes)
            if buffer_length >= 960000:
                buffer_info["audio_buffer"].clear()
                buffer_info["offset"] = 0
                logger.debug(f"Buffer cleared for session {buffer_info['session_id']}")
        
        # Send buffer status
        await connection_manager.send_personal_message({
            "type": "buffer_status",
            "buffer_length": buffer_length,
            "bytes_needed": max(0, chunk_size - (buffer_length - buffer_info["offset"])),
            "ready_for_processing": (buffer_length - buffer_info["offset"]) >= chunk_size
        }, websocket)
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": f"Audio processing error: {str(e)}"
        }, websocket)

async def process_config_message(websocket: WebSocket, message: Dict, model_data: Dict):
    """Process configuration update message"""
    
    try:
        # Store configuration updates
        config_updates = {}
        
        if "language" in message:
            config_updates["language"] = message["language"]
        
        if "initial_prompt" in message:
            config_updates["initial_prompt"] = message["initial_prompt"]
            
        if "temperature" in message:
            config_updates["temperature"] = message["temperature"]
        
        # Apply updates if using realtime native model
        if model_data["type"] == "realtime_native":
            if model_data["decode_options"] and "language" in config_updates:
                model_data["decode_options"]["language"] = config_updates["language"]
            
            if model_data["transcribe_options"]:
                if "initial_prompt" in config_updates:
                    model_data["transcribe_options"]["initial_prompt"] = config_updates["initial_prompt"]
                if "temperature" in config_updates:
                    temp = config_updates["temperature"]
                    if isinstance(temp, (int, float)):
                        model_data["transcribe_options"]["temperature"] = (temp,)
        
        await connection_manager.send_personal_message({
            "type": "config_updated",
            "message": "Configuration updated successfully",
            "config_updates": config_updates,
            "model_type": model_data["type"]
        }, websocket)
        
    except Exception as e:
        await connection_manager.send_personal_message({
            "type": "error", 
            "message": f"Configuration error: {str(e)}"
        }, websocket)

# Add HTTP GET endpoint for the same path to provide helpful information
@router.get("/transcribe")
async def websocket_info():
    """
    Information about the WebSocket endpoint
    This endpoint provides information about how to connect to the WebSocket
    """
    return {
        "message": "This is a WebSocket endpoint, not an HTTP endpoint",
        "websocket_url": "ws://localhost:8000/realtime/transcribe",
        "protocol": "WebSocket",
        "usage": {
            "connection": "Connect using WebSocket protocol",
            "message_format": "JSON messages with 'type' field",
            "supported_types": ["audio_data", "config", "ping"],
            "example_message": {
                "type": "audio_data",
                "data": "<base64_encoded_audio>",
                "format": "pcm_s16le",
                "sample_rate": 16000,
                "language": "en"
            }
        },
        "documentation": "See REALTIME_WEBSOCKET_USAGE.md for detailed instructions",
        "test_connection": "Use WebSocket client or run: python test_websocket_simple.py"
    }

