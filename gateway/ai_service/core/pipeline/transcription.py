import torch
import whisper
import logging
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any

# Create logs directory if it doesn't exist
log_dir = '/tmp/logs'
os.makedirs(log_dir, exist_ok=True)

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'whisper_transcription.log'))
    ]
)
logger = logging.getLogger(__name__)

# Determine device and precision - prioritize GPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
if DEVICE == "cpu":
    logger.warning("GPU not available - falling back to CPU. This will be significantly slower.")
USE_FP16 = DEVICE == "cuda"

# Force CUDA if available
if torch.cuda.is_available():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')

logger.info(f"Using device: {DEVICE} with fp16={USE_FP16}")

def detect_hallucination(text: str, max_repetition_ratio: float = 0.4) -> bool:
    """
    Detect if the transcription contains hallucinations (excessive repetition).
    
    Args:
        text: Transcribed text to analyze
        max_repetition_ratio: Maximum allowed ratio of repeated content
        
    Returns:
        True if hallucination detected, False otherwise
    """
    if not text or len(text.strip()) < 50:
        return False
    
    # Split into sentences/phrases
    sentences = re.split(r'[.!?]+', text.lower())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 3:
        return False
    
    # Count repeated sentences
    sentence_counts = {}
    for sentence in sentences:
        sentence_counts[sentence] = sentence_counts.get(sentence, 0) + 1
    
    # Find most repeated sentence
    max_count = max(sentence_counts.values())
    total_sentences = len(sentences)
    repetition_ratio = max_count / total_sentences
    
    # Check for excessive repetition
    if repetition_ratio > max_repetition_ratio:
        most_repeated = max(sentence_counts.keys(), key=lambda x: sentence_counts[x])
        logger.warning(f"Hallucination detected: '{most_repeated}' repeated {max_count}/{total_sentences} times ({repetition_ratio:.2%})")
        return True
    
    return False

def load_whisper_model(model_size_or_path: str = "large") -> whisper.Whisper:
    """
    Load a Whisper model from either a predefined size or a custom path.
    
    Args:
        model_size_or_path: Predefined model size (e.g., "tiny", "base") or path to custom model
    
    Returns:
        Loaded Whisper model
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    # Show GPU memory if available
    if device == "cuda":
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"GPU memory available: {gpu_memory:.1f} GB")

    try:
        # Check if user passed a path instead of a model name
        if os.path.exists(model_size_or_path):
            logger.info(f"Loading custom Whisper model from path: {model_size_or_path}")
            model = whisper.load_model(model_size_or_path, device=device)
        else:
            logger.info(f"Loading Whisper model size: {model_size_or_path}")
            model = whisper.load_model(model_size_or_path, device=device)
        
        logger.info(f"Successfully loaded model: {model_size_or_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {str(e)}")
        raise RuntimeError(f"Could not load Whisper model '{model_size_or_path}': {str(e)}")

class WhisperTranscriber:
    def __init__(self, model_size: str = "large"):
        """
        Initialize the transcriber with model size or custom model path.
        """
        logger.info(f"Initializing WhisperTranscriber with model: {model_size}")
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Whisper model with error handling."""
        try:
            self.model = load_whisper_model(self.model_size)
            logger.info("WhisperTranscriber initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WhisperTranscriber: {str(e)}")
            raise

    def _validate_audio_path(self, audio_path: str) -> Path:
        """
        Validate the audio file path.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Validated Path object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file extension is not supported
        """
        path = Path(audio_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        logger.info(f"Audio file size: {file_size_mb:.2f} MB")
        
        # Supported audio formats by Whisper
        supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.mp4', '.mkv', '.avi'}
        if path.suffix.lower() not in supported_formats:
            logger.warning(f"File extension '{path.suffix}' may not be supported. Supported formats: {supported_formats}")
        
        return path

    def _get_anti_hallucination_params(self, attempt: int = 0) -> Dict[str, Any]:
        """
        Get transcription parameters optimized to reduce hallucinations.
        
        Args:
            attempt: Retry attempt number (0-based)
            
        Returns:
            Dictionary of transcription parameters
        """
        base_params = {
            'fp16': self.device == "cuda",
            'verbose': False,
            'word_timestamps': False,
            'condition_on_previous_text': False,
            'compression_ratio_threshold': 2.0,
            'logprob_threshold': -1.0,
            'no_speech_threshold': 0.6,
        }
        
        if attempt == 0:
            params = {
                **base_params,
                'temperature': 0.0,
                'best_of': 1,
                'beam_size': 1,
            }
        elif attempt == 1:
            params = {
                **base_params,
                'temperature': [0.0, 0.2],
                'best_of': 3,
                'beam_size': 5,
                'patience': 2.0,
            }
        else:
            params = {
                **base_params,
                'temperature': [0.0, 0.2, 0.4, 0.6, 0.8],
                'best_of': 5,
                'beam_size': 5,
                'patience': 2.0,
                'length_penalty': 1.0,
            }
        
        logger.info(f"Attempt {attempt + 1} parameters: {params}")
        return params

    def transcribe(self, audio_path: str, max_retries: int = 3, detect_language: bool = True, **kwargs) -> str:
        """
        Transcribe audio file using Whisper with hallucination detection and mitigation.
        
        Args:
            audio_path: Path to audio file
            max_retries: Maximum number of retry attempts
            detect_language: Whether to auto-detect language
            **kwargs: Additional parameters for whisper.transcribe()
            
        Returns:
            Transcribed text
        """
        logger.info(f"Starting transcription of: {audio_path}")
        
        try:
            validated_path = self._validate_audio_path(audio_path)
            
            if self.model is None:
                logger.error("Model not loaded. Attempting to reload...")
                self._load_model()
            
            best_result = None
            best_score = float('inf')
            
            for attempt in range(max_retries):
                logger.info(f"Transcription attempt {attempt + 1}/{max_retries}")
                
                try:
                    transcribe_params = self._get_anti_hallucination_params(attempt)
                    transcribe_params.update(kwargs)
                    
                    result = self.model.transcribe(str(validated_path), **transcribe_params)
                    transcribed_text = result["text"].strip()
                    detected_language = result.get("language", "unknown")
                    
                    logger.info(f"Detected language: {detected_language}")
                    logger.info(f"Text length: {len(transcribed_text)} characters")
                    
                    if not detect_hallucination(transcribed_text):
                        logger.info("Transcription completed successfully without hallucinations")
                        return transcribed_text
                    
                    logger.warning(f"Attempt {attempt + 1}: Hallucination detected")
                    sentences = re.split(r'[.!?]+', transcribed_text.lower())
                    sentences = [s.strip() for s in sentences if s.strip()]
                    
                    if sentences:
                        sentence_counts = {}
                        for sentence in sentences:
                            sentence_counts[sentence] = sentence_counts.get(sentence, 0) + 1
                        max_repetitions = max(sentence_counts.values())
                        hallucination_score = max_repetitions / len(sentences)
                        
                        if hallucination_score < best_score:
                            best_score = hallucination_score
                            best_result = transcribed_text
                    
                    if attempt == max_retries - 1:
                        return best_result if best_result is not None else transcribed_text
                    
                except torch.cuda.OutOfMemoryError as e:
                    logger.error(f"GPU out of memory during attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        torch.cuda.empty_cache()
                        continue
                    raise RuntimeError("GPU out of memory. Try using a smaller model or CPU.")
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
            
            raise RuntimeError("All transcription attempts failed")
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'model_loaded': self.model is not None
        }

def transcribe_audio(audio_path: str, model_size: str = "large", **kwargs) -> str:
    """
    Transcribe audio with automatic hallucination mitigation.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size to use
        **kwargs: Additional parameters for transcription
        
    Returns:
        Transcribed text
    """
    logger.info(f"Transcribing audio: {audio_path}")
    transcriber = WhisperTranscriber(model_size="tiny")
    return transcriber.transcribe(audio_path, **kwargs)
