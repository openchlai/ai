import torch
import logging
import librosa
import tempfile
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
            
            # Calculate audio duration
            duration = len(audio_array) / sample_rate
            logger.info(f"🎙️ Audio duration: {duration:.1f} seconds")
            
            # Prepare pipeline kwargs - EXPLICITLY set task to transcribe
            generate_kwargs = {
                "task": "transcribe"  # Explicitly set to transcribe (not translate)
            }
            
            # Add language if specified
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            # For audio longer than 30 seconds, enable timestamps and chunking
            if duration > 30:
                logger.info("🎙️ Long audio detected (>30s) - using chunked transcription")
                result = self.pipe(
                    audio_array,
                    generate_kwargs=generate_kwargs,
                    return_timestamps=True,  # Required for long-form audio
                    chunk_length_s=30,      # Process in 30-second chunks
                    stride_length_s=5       # 5-second overlap between chunks
                )
            else:
                logger.info("🎙️ Short audio detected (≤30s) - using standard transcription")
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
            logger.error(f"❌ Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio from bytes (for uploaded files)"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            try:
                temp_file.write(audio_bytes)
                temp_file.flush()
                
                result = self.transcribe_audio_file(temp_file.name, language)
                return result
                
            finally:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
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