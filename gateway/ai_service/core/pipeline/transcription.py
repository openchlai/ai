import torch
import whisper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

def load_whisper_model():
    # Use a larger model since you have 16GB VRAM
    model_size = "large"
    logger.info(f"Loading Whisper model: {model_size}")
    return whisper.load_model(model_size, device=DEVICE)


class WhisperTranscriber:
    def __init__(self):
        self.model = load_whisper_model()

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio using Whisper with optimized GPU settings."""
        logger.info(f"Starting transcription of {audio_path}")
        try:
            result = self.model.transcribe(
                audio_path,
                fp16=USE_FP16,
                temperature=0.2,
                best_of=3,
                beam_size=5
            )
            logger.info("Transcription completed successfully")
            return result["text"]
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise RuntimeError(f"Transcription failed: {str(e)}")


# Global transcriber instance
transcriber = WhisperTranscriber()

def transcribe(audio_path: str) -> str:
    """Global wrapper for audio transcription."""
    return transcriber.transcribe(audio_path)