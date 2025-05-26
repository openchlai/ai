import torch
import whisper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_whisper_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    model = whisper.load_model("medium", device=device)
    return model


class WhisperTranscriber:
    def __init__(self):
        self.model = load_whisper_model()

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio using Whisper with tiny model."""
        logger.info(f"Starting transcription of {audio_path}")
        try:
            result = self.model.transcribe(
                audio_path,
                fp16=False,  # Using CPU
                temperature=0.2,  # Less random output
                best_of=3,  # More stable results
                beam_size=5  # Better decoding
            )
            logger.info("Transcription completed successfully")
            return result["text"]
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise RuntimeError(f"Transcription failed: {str(e)}")


# Create a global instance of the transcriber
transcriber = WhisperTranscriber()

def transcribe(audio_path: str) -> str:
    """Global function to transcribe audio."""
    return transcriber.transcribe(audio_path)