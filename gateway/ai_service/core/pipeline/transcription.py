# core/transcription.py

import torch
import whisper
import logging
import os
import re
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
    ]
)
logger = logging.getLogger(__name__)

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
