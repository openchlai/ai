import torch
import logging
import librosa
import numpy as np
import os
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WhisperModel:
    """HuggingFace Whisper Large V3 Turbo model for speech recognition"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.model_path = model_path or settings.get_model_path("whisper")
        self.fallback_model_id = "openai/whisper-large-v3-turbo"
        self.model = None
        self.processor = None
        self.pipe = None
        self.device = None
        self.torch_dtype = None
        self.is_loaded = False
        self.error = None
        
        # Supported language codes for Whisper
        self.supported_languages = {
            "auto": "Auto-detect",
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi",
            "sw": "Swahili",
            "am": "Amharic",
            "lg": "Luganda",
            "rw": "Kinyarwanda",
            "so": "Somali",
            "yo": "Yoruba",
            "ig": "Igbo",
            "ha": "Hausa",
            "zu": "Zulu",
            "xh": "Xhosa",
            "af": "Afrikaans",
            "ny": "Chichewa"
        }
        
    def _check_local_model_exists(self) -> bool:
        """Check if local model files exist"""
        if not os.path.exists(self.model_path):
            return False
        
        # Check for essential Whisper model files
        required_files = ["config.json"]
        optional_files = ["model.safetensors", "pytorch_model.bin"]
        
        # At least config.json must exist
        config_path = os.path.join(self.model_path, "config.json")
        if not os.path.exists(config_path):
            return False
        
        # At least one model file must exist
        model_file_exists = any(
            os.path.exists(os.path.join(self.model_path, file)) 
            for file in optional_files
        )
        
        if not model_file_exists:
            logger.warning(f"Config found but no model files in {self.model_path}")
            return False
        
        logger.info(f"✅ Local Whisper model files detected in {self.model_path}")
        return True
        
    def load(self) -> bool:
        """Load Whisper model with local-first approach"""
        try:
            logger.info(f"🎙️ Loading Whisper model...")
            
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
            
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            logger.info(f"🎙️ Using device: {self.device}, dtype: {self.torch_dtype}")
            
            # Try loading from local path first
            if self._check_local_model_exists():
                try:
                    logger.info(f"🎙️ Loading local Whisper model from {self.model_path}")
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.model_path,
                        local_files_only=True,  # Force local loading
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    
                    self.processor = AutoProcessor.from_pretrained(
                        self.model_path,
                        local_files_only=True  # Force local loading
                    )
                    
                    logger.info(f"✅ Local Whisper model loaded successfully")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load local model: {e}")
                    logger.info(f"🌐 Falling back to HuggingFace Hub download")
                    raise  # Re-raise to trigger fallback
                    
            else:
                # No local model, use fallback
                logger.info(f"🌐 Local model not found, downloading from HuggingFace Hub: {self.fallback_model_id}")
                
                self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    self.fallback_model_id, 
                    torch_dtype=self.torch_dtype, 
                    low_cpu_mem_usage=True, 
                    use_safetensors=True
                )
                
                self.processor = AutoProcessor.from_pretrained(self.fallback_model_id)
            
            # Move model to device
            self.model.to(self.device)
            
            # Create pipeline
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=self.torch_dtype,
                device=self.device,
            )
            
            self.is_loaded = True
            self.error = None
            logger.info(f"✅ Whisper model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            # If local loading failed, try fallback
            if "local_files_only" in str(e) or "not found" in str(e).lower():
                try:
                    logger.info(f"🌐 Local loading failed, downloading from HuggingFace Hub: {self.fallback_model_id}")
                    
                    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.fallback_model_id, 
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    self.model.to(self.device)
                    
                    self.processor = AutoProcessor.from_pretrained(self.fallback_model_id)
                    
                    self.pipe = pipeline(
                        "automatic-speech-recognition",
                        model=self.model,
                        tokenizer=self.processor.tokenizer,
                        feature_extractor=self.processor.feature_extractor,
                        torch_dtype=self.torch_dtype,
                        device=self.device,
                    )
                    
                    self.is_loaded = True
                    self.error = None
                    logger.info(f"✅ Whisper model loaded successfully via fallback on {self.device}")
                    return True
                    
                except Exception as fallback_error:
                    error_msg = f"Failed to load Whisper model (local and fallback): {fallback_error}"
                    logger.error(f"❌ {error_msg}")
                    self.error = error_msg
                    self.is_loaded = False
                    return False
            else:
                error_msg = f"Failed to load Whisper model: {e}"
                logger.error(f"❌ {error_msg}")
                self.error = error_msg
                self.is_loaded = False
                return False
    
    def _validate_language(self, language: Optional[str]) -> Optional[str]:
        """Validate and normalize language code"""
        if not language or language.lower() in ["auto", "none", ""]:
            return None  # Auto-detect
        
        # Normalize language code
        lang_code = language.lower().strip()
        
        # Check if it's a supported language
        if lang_code in self.supported_languages:
            return lang_code
        
        # Try to find by language name
        for code, name in self.supported_languages.items():
            if name.lower() == lang_code:
                return code
        
        # If not found, log warning but continue (Whisper supports many languages)
        logger.warning(f"⚠️ Language '{language}' not in known list, but will attempt transcription")
        return lang_code
    
    def _convert_pcm_bytes_to_array(self, audio_bytes: bytes, sample_rate: int = 16000) -> np.ndarray:
        """Convert raw PCM bytes (16-bit, mono) to normalized float32 numpy array"""
        # Convert bytes to int16 array
        audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Convert to float32 and normalize to [-1.0, 1.0] range
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        
        logger.info(f"🎙️ Converted PCM data: {len(audio_int16)} samples, {len(audio_int16)/sample_rate:.1f}s duration")
        
        return audio_float32
    
    def transcribe_audio_file(self, audio_file_path: str, language: Optional[str] = None) -> str:
        """Transcribe audio file to text with support for long audio"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            logger.info(f"🎙️ Transcribing audio file: {Path(audio_file_path).name}")
            
            # Validate and normalize language
            validated_language = self._validate_language(language)
            if validated_language:
                logger.info(f"🎙️ Target language: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')})")
            else:
                logger.info("🎙️ Language: Auto-detect")
            
            # Load audio with librosa (handles multiple formats)
            audio_array, sample_rate = librosa.load(audio_file_path, sr=16000, mono=True)
            
            # Use the shared transcription logic
            return self._transcribe_audio_array(audio_array, language, sample_rate)
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def _transcribe_audio_array(self, audio_array: np.ndarray, language: Optional[str] = None, sample_rate: int = 16000, enable_chunking: bool = True) -> str:
        """Core transcription logic for numpy audio arrays with enhanced chunking"""
        try:
            # Validate and normalize language
            validated_language = self._validate_language(language)
            if validated_language:
                logger.info(f"🎙️ Target language: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')})")
            else:
                logger.info("🎙️ Language: Auto-detect")
            
            # Calculate audio duration
            duration = len(audio_array) / sample_rate
            logger.info(f"🎙️ Audio duration: {duration:.1f} seconds")
            
            # Prepare pipeline kwargs - EXPLICITLY set task to transcribe
            generate_kwargs = {
                "task": "transcribe",  # Explicitly set to transcribe (not translate)
                "temperature": 0.0,    # Deterministic generation to reduce hallucinations
                "compression_ratio_threshold": 2.4,  # Detect audio compression issues
                "logprob_threshold": -1.0,  # Filter low-confidence outputs
                "no_speech_threshold": 0.6,  # Higher threshold to avoid transcribing silence
# Note: condition_on_previous_text not supported in transformers pipeline, controlled by chunk_length_s instead
            }
            
            # Add language if specified
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            # Enhanced chunking strategy based on audio duration
            if enable_chunking and duration > 10:  # Use chunking for audio > 10 seconds
                # Adaptive chunk size based on duration
                if duration > 30:
                    chunk_length = 30
                    stride_length = 5
                    logger.info(f"🎙️ Long audio ({duration:.1f}s) - using 30s chunks with 5s stride")
                elif duration > 15:
                    chunk_length = 20
                    stride_length = 4
                    logger.info(f"🎙️ Medium audio ({duration:.1f}s) - using 20s chunks with 4s stride")
                else:
                    chunk_length = 15
                    stride_length = 3
                    logger.info(f"🎙️ Short-medium audio ({duration:.1f}s) - using 15s chunks with 3s stride")
                
                result = self.pipe(
                    audio_array,
                    generate_kwargs=generate_kwargs,
                    return_timestamps=True,  # Required for chunked processing
                    chunk_length_s=chunk_length,
                    stride_length_s=stride_length
                )
            else:
                logger.info(f"🎙️ Short audio ({duration:.1f}s) - using standard transcription")
                result = self.pipe(
                    audio_array,
                    generate_kwargs=generate_kwargs,
                    return_timestamps=False
                )
            
            # Extract text from result
            if isinstance(result, dict):
                transcript = result["text"].strip()
            elif isinstance(result, list):
                # For chunked results, concatenate all text
                transcript = " ".join([chunk["text"] for chunk in result]).strip()
            else:
                transcript = str(result).strip()
            
            logger.info(f"✅ Transcription completed: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            logger.error(f"❌ Array transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio from raw PCM bytes (16-bit, 16kHz, mono)"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Convert raw PCM bytes to numpy array
            audio_array = self._convert_pcm_bytes_to_array(audio_bytes, sample_rate=16000)
            
            # Transcribe the audio array directly
            result = self._transcribe_audio_array(audio_array, language, sample_rate=16000)
            return result
            
        except Exception as e:
            logger.error(f"❌ Transcription from bytes failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def transcribe_pcm_audio(self, audio_bytes: bytes, sample_rate: int = 16000, language: Optional[str] = None, enable_chunking: bool = True) -> str:
        """Transcribe raw PCM audio bytes with specified sample rate and enhanced processing
        
        Args:
            audio_bytes: Raw PCM audio data (16-bit, mono)
            sample_rate: Sample rate in Hz (default: 16000, currently only 16000 is supported)
            language: Language code for transcription (optional, auto-detect if None)
            enable_chunking: Enable chunking for longer audio segments (default: True)
            
        Returns:
            Transcribed text
            
        Raises:
            RuntimeError: If model not loaded or transcription fails
            ValueError: If unsupported sample rate provided
        """
        # Validate sample rate
        if sample_rate != 16000:
            raise ValueError(f"Sample rate {sample_rate} not supported. Currently only 16000 Hz is supported.")
        
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Convert raw PCM bytes to numpy array
            audio_array = self._convert_pcm_bytes_to_array(audio_bytes, sample_rate=sample_rate)
            
            # Transcribe with enhanced chunking support
            result = self._transcribe_audio_array(audio_array, language, sample_rate=sample_rate, enable_chunking=enable_chunking)
            return result
            
        except Exception as e:
            logger.error(f"❌ Transcription from PCM bytes failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return self.supported_languages.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": "whisper",
            "model_path": self.model_path,
            "fallback_model_id": self.fallback_model_id,
            "model_type": "speech-to-text",
            "framework": "transformers",
            "device": str(self.device) if self.device else None,
            "torch_dtype": str(self.torch_dtype) if self.torch_dtype else None,
            "is_loaded": self.is_loaded,
            "error": self.error,
            "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"],
            "max_audio_length": "unlimited (chunked processing)",
            "sample_rate": "16kHz",
            "task": "transcribe",  # Explicitly transcribe only
            "languages": "multilingual (99+ languages)",
            "version": "large-v3-turbo",
            "long_form_support": True,
            "supported_language_codes": list(self.supported_languages.keys()),
            "local_model_available": self._check_local_model_exists()
        }
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.is_loaded and self.model is not None and self.pipe is not None

# Global instance following your pattern
whisper_model = WhisperModel()