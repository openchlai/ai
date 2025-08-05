from core.utils.path_resolver import resolve_model_path
import whisper
import torch
import logging
import socket
import threading
import time
import atexit
import os
from pathlib import Path
from typing import Tuple, Any, Dict, Optional
from core.pipeline.model_loader import load_model_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_FP16 = DEVICE == "cuda"
torch.set_num_threads(1)  # For CPU stability

# Global server control
_server_thread = None
_server_running = False
_server_socket = None

def initialize_whisper_components() -> Tuple[Any, Any, Dict, Dict]:
    """
    Initialize Whisper model components with persistent caching
    Returns:
        tuple: (model, processor, transcribe_options, decode_options)
    """
    try:
        logger.info("🔄 Initializing Whisper components...")
        
        config = load_model_config()
        model_size = config["transcription_model"]["size"]
        model_path = Path(resolve_model_path(config["transcription_model"]["path"]))
        
        # Ensure model directory exists
        model_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"⚙️ Loading {model_size} model from {model_path}")
        
        # Check if model exists
        model_file = model_path / f"{model_size}.pt"
        if not model_file.exists():
            logger.info(f"Model not found at {model_file}, downloading...")
        
        # Load model with explicit cache location
        model = whisper.load_model(
            model_size,
            device=DEVICE,
            download_root=str(model_path),
            in_memory=False  # Better for containerized environments
        )
        
        # Initialize processor
        processor = whisper.tokenizer.get_tokenizer(
            multilingual=True,
            language=config.get("language", "en")
        )
        
        # Default options
        transcribe_options = {
            'fp16': USE_FP16,
            'language': config.get("language", "en"),
            'task': 'transcribe',
            'verbose': False,
            'temperature': 0.0,
            'best_of': 5,
            'beam_size': 5,
            'patience': 1.0,
            'length_penalty': 1.0,
            'compression_ratio_threshold': 2.4,
            'logprob_threshold': -1.0,
            'no_speech_threshold': 0.6,
            'condition_on_previous_text': False
        }
        
        decode_options = {
            'fp16': USE_FP16,
            'language': config.get("language", "en"),
            'task': 'transcribe',
            'without_timestamps': True
        }
        
        logger.info("✅ Whisper components initialized successfully")
        return model, processor, transcribe_options, decode_options
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Whisper components: {str(e)}")
        raise

# Initialize components
try:
    model, processor, transcribe_options, decode_options = initialize_whisper_components()
except Exception as e:
    logger.critical("Failed to initialize Whisper server")
    raise

# [Rest of your existing code remains exactly the same...]
# transcribe(), handle_client(), start_socket_server(), 
# stop_socket_server(), cleanup_resources() functions stay identical
# Main block stays identical

# Add at the bottom of aii_server.py (before the if __name__ block)
def start_socket_server():
    """Public interface to start the socket server"""
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        logger.warning("Socket server already running")
        return
    
    _server_thread = threading.Thread(
        target=_start_socket_server_internal,  # Renamed from start_socket_server
        daemon=True
    )
    _server_thread.start()

def _start_socket_server_internal(host: str = '0.0.0.0', port: int = 8300):
    """Internal server implementation"""
    # ... rest of your existing start_socket_server code ...