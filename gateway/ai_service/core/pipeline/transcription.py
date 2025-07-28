<<<<<<< HEAD
=======
# core/transcription.py

>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
import torch
import whisper
import logging
import os
import re
<<<<<<< HEAD
import time
import atexit
import signal
import psutil
from pathlib import Path
from typing import Optional, Dict, Any, Union
from threading import RLock
from contextlib import contextmanager
from .model_loader import load_model_config, resolve_model_path

# Configure robust logging
log_dir = '/app/logs/whisper' if os.path.exists('/app') else os.path.join(os.path.expanduser('~'), 'logs', 'whisper')
os.makedirs(log_dir, exist_ok=True)
# Configure logging with proper error handler setup
error_handler = logging.FileHandler(os.path.join(log_dir, 'whisper_errors.log'))
error_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(threadName)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'whisper_transcription.log')),
        error_handler
=======
from pathlib import Path
from typing import Optional, Dict, Any
from .model_loader import load_model_config, resolve_model_path




# Configure logging
log_dir = '/tmp/logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'whisper_transcription.log'))
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
    ]
)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# System configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_FP16 = DEVICE == "cuda"
torch.set_num_threads(1)  # Critical for CPU stability

logger.info(f"🖥️ System initialized | Device: {DEVICE} | FP16: {USE_FP16} | Torch threads: {torch.get_num_threads()}")

# Thread-safe model cache
_model_cache = {}
_model_cache_lock = RLock()

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds: int):
    """Timeout context manager"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

@atexit.register
def cleanup_resources():
    """Cleanup resources on exit"""
    with _model_cache_lock:
        _model_cache.clear()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("🧹 Cleaned up model cache and GPU memory")

def verify_system_requirements():
    """Verify critical system requirements"""
    try:
        # Memory check
        mem = psutil.virtual_memory()
        if mem.available < 2 * 1024**3:  # 2GB minimum
            raise RuntimeError(f"Insufficient memory: {mem.available/1024**3:.1f}GB available")
        
        # Disk check
        disk_usage = psutil.disk_usage('/')
        free = disk_usage.free
        if free < 1 * 1024**3:  # 1GB minimum
            raise RuntimeError(f"Insufficient disk space: {free/1024**3:.1f}GB free")
        
        # Torch version
        required_torch = "1.12.0"
        if torch.__version__ < required_torch:
            raise RuntimeError(f"PyTorch too old ({torch.__version__} < {required_torch})")
        
        logger.info("✅ System requirements verified")
    except Exception as e:
        logger.critical(f"System verification failed: {str(e)}")
        raise

verify_system_requirements()

def detect_hallucination(text: str, max_repetition_ratio: float = 0.4) -> bool:
    """Enhanced hallucination detection with pattern analysis"""
    if not text or len(text.strip()) < 50:
        return False
    
    # Multiple detection strategies
    sentences = [s.strip() for s in re.split(r'[.!?]+', text.lower()) if s.strip()]
    word_repeats = re.findall(r'\b(\w+)\b.*\b\1\b', text.lower())
    
    if len(sentences) < 3:
        return False
    
    counts = {}
    for s in sentences:
        counts[s] = counts.get(s, 0) + 1
    
    max_count = max(counts.values())
    repetition_ratio = max_count / len(sentences)
    
    if repetition_ratio > max_repetition_ratio or len(word_repeats) > 5:
        most_repeated = max(counts, key=counts.get)
        logger.warning(f"Hallucination detected | Ratio: {repetition_ratio:.2f} | Repeats: {word_repeats[:5]}")
        return True
    return False

def get_cached_whisper_model() -> whisper.Whisper:
    """Thread-safe model loading with memory monitoring"""
    cache_key = f"whisper_{DEVICE}"
    
    try:
        with _model_cache_lock:
            # Check cache first
            if cache_key in _model_cache:
                logger.info("♻️ Using cached model")
                return _model_cache[cache_key]
            
            # Memory diagnostics
            mem_before = psutil.virtual_memory()
            logger.info(f"💾 Memory before load | Available: {mem_before.available/1024**3:.1f}GB")
            
            # Load with timeout
            try:
                with time_limit(120):  # 2 minute timeout
                    model = load_whisper_model_from_config()
            except TimeoutException:
                logger.error("Model loading timed out")
                raise RuntimeError("Model loading timeout")
            
            # Verify model loaded correctly
            if not hasattr(model, 'transcribe'):
                raise RuntimeError("Loaded model is invalid - missing transcribe method")
            
            # Memory diagnostics
            mem_after = psutil.virtual_memory()
            logger.info(f"💾 Memory after load | Available: {mem_after.available/1024**3:.1f}GB | Used: {(mem_after.used - mem_before.used)/1024**2:.1f}MB")
            
            _model_cache[cache_key] = model
            return model
            
    except Exception as e:
        logger.exception("Failed to load cached model")
        raise

def load_whisper_model_from_config() -> whisper.Whisper:
    """Robust model loading with multiple fallbacks"""
    try:
        logger.info("📋 Loading model configuration...")
        config = load_model_config()
        model_path = resolve_model_path(config["transcription_model"]["path"])
        model_size = config["transcription_model"]["size"]
        
        logger.info(f"📂 Model path: {model_path} | Size: {model_size}")
        
        # Verify model directory
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        
        # Check if model files exist (flexible approach)
        potential_model_files = [
            os.path.join(model_path, 'tiny.pt'),
            os.path.join(model_path, 'model.bin'),
            os.path.join(model_path, f'{model_size}.pt'),
            os.path.join(model_path, 'pytorch_model.bin')
        ]
        
        model_file_found = False
        for filepath in potential_model_files:
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:  # At least 1KB
                model_file_found = True
                logger.info(f"Found model file: {filepath} ({os.path.getsize(filepath)} bytes)")
                break
        
        if not model_file_found:
            logger.warning("No suitable model files found, will attempt direct download")
        
        # Attempt loading strategies
        load_attempts = [
            lambda: whisper.load_model(os.path.join(model_path, "tiny.pt"), device=DEVICE),
            lambda: whisper.load_model(model_size, download_root=model_path, device=DEVICE, in_memory=True),
            lambda: whisper.load_model(model_size, device=DEVICE)  # Full download as last resort
        ]
        
        for i, attempt in enumerate(load_attempts, 1):
            try:
                logger.info(f"Attempt {i}/{len(load_attempts)} loading model...")
                model = attempt()
                logger.info(f"✅ Successfully loaded model via attempt {i}")
                return model
            except Exception as e:
                logger.warning(f"Attempt {i} failed: {str(e)}")
                if i == len(load_attempts):
                    raise
        
    except Exception as e:
        logger.exception("❌ All model loading attempts failed")
        raise RuntimeError(f"Failed to load model: {str(e)}")

class WhisperTranscriber:
    """Enhanced transcriber with retries and diagnostics"""
    
    def __init__(self):
        self.device = DEVICE
        self._verify_hardware()
        self.model = get_cached_whisper_model()
        logger.info("✅ Transcriber initialized")
    
    def _verify_hardware(self):
        """Verify GPU/CPU configuration"""
        logger.info(f"Torch config | Threads: {torch.get_num_threads()} | CUDA: {torch.cuda.is_available()}")
        
        if self.device == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA requested but not available")
            
            logger.info(f"GPU Info | Device: {torch.cuda.get_device_name(0)} | "
                       f"Memory: {torch.cuda.memory_allocated()/1024**2:.1f}MB allocated")
    
    def _validate_audio_path(self, audio_path: Union[str, Path]) -> Path:
        """Validate input audio file"""
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.mp4', '.mkv', '.avi'}
        if path.suffix.lower() not in supported_formats:
            logger.warning(f"⚠️ Unsupported audio format: {path.suffix}")
        
        # Verify file size
        min_size = 1024  # 1KB
        max_size = 100 * 1024**2  # 100MB
        file_size = path.stat().st_size
        
        if file_size < min_size:
            raise ValueError(f"File too small ({file_size} bytes)")
        if file_size > max_size:
            raise ValueError(f"File too large ({file_size/1024**2:.1f}MB)")
        
        return path
    
    def _get_transcription_params(self, attempt: int = 0) -> Dict[str, Any]:
        """Dynamic parameters based on attempt number"""
        base_params = {
            'fp16': USE_FP16,
            'verbose': None,  # Set to None to use our logging instead
            'word_timestamps': False,
            'condition_on_previous_text': False,
            'compression_ratio_threshold': 2.4,
            'logprob_threshold': -1.0,
            'no_speech_threshold': 0.6,
            'temperature': (0.0, 0.2, 0.4)[min(attempt, 2)],
            'best_of': (1, 3, 5)[min(attempt, 2)],
            'beam_size': (1, 5, 5)[min(attempt, 2)],
            'patience': (None, 1.0, 2.0)[min(attempt, 2)]
        }
        return base_params
    
    def _transcribe_with_retry(self, audio_path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Single transcription attempt with error handling"""
        try:
            start_time = time.time()
            logger.info(f"🎧 Starting transcription with params: {params}")
            
            result = self.model.transcribe(str(audio_path), **params)
            
            duration = time.time() - start_time
            logger.info(f"✅ Transcription completed in {duration:.1f}s | "
                       f"Text length: {len(result.get('text', ''))} chars")
            
            return result
        except torch.cuda.OutOfMemoryError:
            logger.warning("⚠️ CUDA OOM error - clearing cache")
            torch.cuda.empty_cache()
            raise
        except Exception as e:
            logger.warning(f"Transcription attempt failed: {str(e)}")
            raise
    
    def transcribe(self, audio_path: str, max_retries: int = 3) -> str:
        """Robust transcription with multiple fallback strategies"""
        path = self._validate_audio_path(audio_path)
        best_result = None
        best_score = float('inf')  # Lower is better
        
        for attempt in range(max_retries):
            try:
                params = self._get_transcription_params(attempt)
                result = self._transcribe_with_retry(path, params)
                text = result.get('text', '').strip()
                
                if not text:
                    continue
                
                # Quality assessment
                current_score = self._assess_quality(result)
                if current_score < best_score:
                    best_score = current_score
                    best_result = text
                
                # Early exit if quality is good
                if best_score < 0.3 and not detect_hallucination(text):
                    return text
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Max retries exhausted")
                    if best_result:
                        return best_result
                    raise RuntimeError("All transcription attempts failed") from e
                
                # Exponential backoff
                sleep_time = min(2 ** attempt, 10)
                logger.info(f"Waiting {sleep_time}s before retry...")
                time.sleep(sleep_time)
        
        return best_result or ""
    
    def _assess_quality(self, result: Dict[str, Any]) -> float:
        """Score transcription quality (0.0 = perfect, 1.0 = terrible)"""
        score = 0.0
        
        # No speech probability
        no_speech_prob = result.get('no_speech_prob', 0.5)
        score += no_speech_prob * 0.3
        
        # Compression ratio
        comp_ratio = result.get('compression_ratio', 1.0)
        score += max(0, abs(comp_ratio - 2.0)) * 0.2
        
        # Log probabilities
        avg_logprob = result.get('avg_logprob', -1.0)
        score += max(0, -1.0 - avg_logprob) * 0.5
        
        return min(score, 1.0)

def transcribe_audio(audio_path: str, **kwargs) -> str:
    """Public API for transcription"""
    try:
        transcriber = WhisperTranscriber()
        return transcriber.transcribe(audio_path, **kwargs)
    except Exception as e:
        logger.exception(f"Transcription failed for {audio_path}")
        raise RuntimeError(f"Transcription error: {str(e)}") from e

# Test function for manual verification
def test_transcription():
    """Run a test transcription"""
    test_file = "test_audio.wav"
    if not os.path.exists(test_file):
        logger.warning(f"Test file {test_file} not found")
        return
    
    logger.info("Starting test transcription...")
    start = time.time()
    
    try:
        result = transcribe_audio(test_file)
        duration = time.time() - start
        logger.info(f"Test completed in {duration:.1f}s")
        logger.info(f"Test result (first 100 chars): {result[:100]}...")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_transcription()
=======
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
USE_FP16 = DEVICE == "cuda"

logger.info(f"🖥️ Using device: {DEVICE}, FP16: {USE_FP16}")

def detect_hallucination(text: str, max_repetition_ratio: float = 0.4) -> bool:
    if not text or len(text.strip()) < 50:
        return False
    sentences = re.split(r'[.!?]+', text.lower())
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 3:
        return False
    counts = {}
    for s in sentences:
        counts[s] = counts.get(s, 0) + 1
    max_count = max(counts.values())
    repetition_ratio = max_count / len(sentences)
    if repetition_ratio > max_repetition_ratio:
        most_repeated = max(counts, key=counts.get)
        logger.warning(f"Hallucination detected: '{most_repeated}' repeated {max_count}/{len(sentences)}")
        return True
    return False

def load_whisper_model_from_config() -> whisper.Whisper:
    try:
        config = load_model_config()
        model_path = resolve_model_path(config["transcription_model"]["path"])
        model_size = config["transcription_model"]["size"]  # 'tiny'
        logger.info(f"🧠 Loading Whisper model from: {model_path}")
        return whisper.load_model(model_size, download_root=model_path, device=DEVICE)

        # model_path = resolve_model_path(config["transcription_model"]["path"])
        # return whisper.load_model(model_path, device=DEVICE)
    except Exception as e:
        logger.exception("❌ Failed to load Whisper model from config")
        raise RuntimeError(f"Failed to load Whisper model: {e}")


class WhisperTranscriber:
    def __init__(self):
        self.device = DEVICE
        self.model = load_whisper_model_from_config()
        logger.info("✅ WhisperTranscriber initialized")

    def _validate_audio_path(self, audio_path: str) -> Path:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.mp4', '.mkv', '.avi'}
        if path.suffix.lower() not in supported_formats:
            logger.warning(f"Unsupported audio format: {path.suffix}")
        return path

    def _get_params(self, attempt: int = 0) -> Dict[str, Any]:
        base = {
            'fp16': self.device == "cuda",
            'verbose': False,
            'word_timestamps': False,
            'condition_on_previous_text': False,
            'compression_ratio_threshold': 2.0,
            'logprob_threshold': -1.0,
            'no_speech_threshold': 0.6,
        }
        if attempt == 0:
            return {**base, 'temperature': 0.0, 'best_of': 1, 'beam_size': 1}
        if attempt == 1:
            return {**base, 'temperature': [0.0, 0.2], 'best_of': 3, 'beam_size': 5, 'patience': 2.0}
        return {**base, 'temperature': [0.0, 0.2, 0.4, 0.6], 'best_of': 5, 'beam_size': 5, 'patience': 2.0}

    def transcribe(self, audio_path: str, max_retries: int = 3, **kwargs) -> str:
        path = self._validate_audio_path(audio_path)
        best_result, best_score = None, float("inf")

        for attempt in range(max_retries):
            try:
                logger.info(f"🎧 Transcription attempt {attempt + 1}")
                params = self._get_params(attempt)
                params.update(kwargs)
                result = self.model.transcribe(str(path), **params)
                text = result["text"].strip()
                if not detect_hallucination(text):
                    return text
                score = self._hallucination_score(text)
                if score < best_score:
                    best_score = score
                    best_result = text
            except Exception as e:
                logger.warning(f"Transcription error (attempt {attempt + 1}): {e}")
                if isinstance(e, torch.cuda.OutOfMemoryError):
                    torch.cuda.empty_cache()
                if attempt == max_retries - 1:
                    raise RuntimeError("Max transcription attempts failed") from e

        return best_result or ""

    def _hallucination_score(self, text: str) -> float:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text.lower()) if s.strip()]
        counts = {s: sentences.count(s) for s in set(sentences)}
        return max(counts.values()) / len(sentences) if sentences else 1.0

    def get_model_info(self) -> dict:
        return {
            'device': self.device,
            'model_loaded': self.model is not None
        }

def transcribe_audio(audio_path: str, **kwargs) -> str:
    transcriber = WhisperTranscriber()
    return transcriber.transcribe(audio_path, **kwargs)
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
