import torch
import logging
import librosa
import tempfile
import os
import numpy as np
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
            
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
            
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
            
            # No longer using pipeline - we'll use direct model calls for better performance
            
            self.is_loaded = True
            self.error = None
            logger.info(f"✅ Whisper model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            # If local loading failed, try fallback
            if "local_files_only" in str(e) or "not found" in str(e).lower():
                try:
                    logger.info(f"🌐 Local loading failed, downloading from HuggingFace Hub: {self.fallback_model_id}")
                    
                    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.fallback_model_id, 
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    self.model.to(self.device)
                    
                    self.processor = AutoProcessor.from_pretrained(self.fallback_model_id)
                    
                    # No longer using pipeline - we'll use direct model calls for better performance
                    
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
            
            # Prepare generation kwargs
            generate_kwargs = {
                "task": "transcribe"  # Explicitly set to transcribe (not translate)
            }
            
            # Add language if specified
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            # Process audio using manual chunking for better control
            transcriptions = []
            
            # Chunk audio into 30-second segments for processing
            chunk_duration = 30  # seconds
            chunk_samples = chunk_duration * sample_rate
            audio_length = len(audio_array)
            
            if duration > 30:
                logger.info(f"🎙️ Long audio detected ({duration:.1f}s) - using chunked transcription")
                
                for i in range(0, audio_length, chunk_samples):
                    chunk_end = min(i + chunk_samples, audio_length)
                    audio_chunk = audio_array[i:chunk_end]
                    chunk_time = i / sample_rate
                    chunk_num = i // chunk_samples + 1
                    total_chunks = (audio_length + chunk_samples - 1) // chunk_samples
                    
                    logger.info(f"🎙️ Processing chunk {chunk_num}/{total_chunks} (time: {chunk_time:.1f}s)")
                    
                    # Process audio chunk
                    inputs = self.processor(audio_chunk, sampling_rate=sample_rate, return_tensors="pt")
                    input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
                    
                    # Create attention mask for this chunk
                    attention_mask = torch.ones(input_features.shape[:-1], dtype=torch.long, device=self.device)
                    
                    try:
                        with torch.no_grad():
                            predicted_ids = self.model.generate(
                                input_features,
                                attention_mask=attention_mask,
                                max_length=448,
                                num_beams=5,
                                repetition_penalty=1.1,
                                no_repeat_ngram_size=3,
                                **generate_kwargs
                            )
                        
                        # Decode the transcription
                        chunk_transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                        transcriptions.append(chunk_transcription.strip())
                        
                    except torch.cuda.OutOfMemoryError:
                        logger.warning("🎙️ CUDA out of memory, falling back to CPU for this chunk...")
                        # Move model to CPU temporarily
                        self.model.to("cpu")
                        input_features = input_features.to(device="cpu", dtype=torch.float32)
                        attention_mask = attention_mask.to("cpu")
                        
                        with torch.no_grad():
                            predicted_ids = self.model.generate(
                                input_features,
                                attention_mask=attention_mask,
                                max_length=448,
                                num_beams=5,
                                repetition_penalty=1.1,
                                no_repeat_ngram_size=3,
                                **generate_kwargs
                            )
                        
                        chunk_transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                        transcriptions.append(chunk_transcription.strip())
                        
                        # Move model back to original device
                        self.model.to(self.device)
                
                # Combine all transcriptions
                transcript = " ".join(transcriptions)
                
            else:
                logger.info("🎙️ Short audio detected (≤30s) - using standard transcription")
                
                # Process audio directly
                inputs = self.processor(audio_array, sampling_rate=sample_rate, return_tensors="pt")
                input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
                
                # Create attention mask
                attention_mask = torch.ones(input_features.shape[:-1], dtype=torch.long, device=self.device)
                
                try:
                    with torch.no_grad():
                        predicted_ids = self.model.generate(
                            input_features,
                            attention_mask=attention_mask,
                            max_length=448,
                            num_beams=5,
                            repetition_penalty=1.1,
                            no_repeat_ngram_size=3,
                            **generate_kwargs
                        )
                    
                    # Decode the transcription
                    transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                    
                except torch.cuda.OutOfMemoryError:
                    logger.warning("🎙️ CUDA out of memory, falling back to CPU...")
                    # Move model to CPU temporarily
                    self.model.to("cpu")
                    input_features = input_features.to(device="cpu", dtype=torch.float32)
                    attention_mask = attention_mask.to("cpu")
                    
                    with torch.no_grad():
                        predicted_ids = self.model.generate(
                            input_features,
                            attention_mask=attention_mask,
                            max_length=448,
                            num_beams=5,
                            repetition_penalty=1.1,
                            no_repeat_ngram_size=3,
                            **generate_kwargs
                        )
                    
                    transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                    
                    # Move model back to original device
                    self.model.to(self.device)
            
            logger.info(f"✅ Transcription completed: {len(transcript)} characters")
            
            return transcript
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio from bytes (for uploaded files or raw audio data)"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            logger.info(f"🎙️ Transcribing audio from bytes: {len(audio_bytes)} bytes")
            
            # Check if this looks like a complete audio file (WAV, MP3, etc.) or raw PCM data
            # WAV files start with "RIFF", MP3 files often start with "ID3" or have frame sync
            if audio_bytes[:4] in [b'RIFF', b'ID3\x03', b'ID3\x04'] or (len(audio_bytes) > 2 and audio_bytes[0:2] == b'\xff\xfb'):
                # This looks like a complete audio file format, use file-based approach
                logger.info("🎙️ Detected structured audio format (WAV/MP3), using file-based transcription")
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
            else:
                # This looks like raw audio data, use PCM transcription with default 16kHz
                logger.info("🎙️ Detected raw audio data, using PCM transcription")
                return self.transcribe_pcm_audio(audio_bytes, sample_rate=16000, language=language)
                
        except Exception as e:
            logger.error(f"❌ Audio bytes transcription failed: {e}")
            raise RuntimeError(f"Audio bytes transcription failed: {str(e)}")
    
    def transcribe_pcm_audio(self, audio_bytes: bytes, sample_rate: int = 16000, language: Optional[str] = None) -> str:
        """Transcribe raw PCM audio data for streaming applications
        
        Args:
            audio_bytes: Raw PCM audio data (16-bit signed integers)
            sample_rate: Sample rate in Hz (default: 16000)
            language: Source language for transcription (auto-detect if None)
        
        Returns:
            Transcribed text as string
        """
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            logger.info(f"🎙️ Transcribing PCM audio: {len(audio_bytes)} bytes @ {sample_rate}Hz")
            
            # Validate and normalize language
            validated_language = self._validate_language(language)
            if validated_language:
                logger.info(f"🎙️ Target language: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')})")
            else:
                logger.info("🎙️ Language: Auto-detect")
            
            # Convert PCM bytes to numpy array
            # Assuming 16-bit signed integers (most common PCM format)
            # Convert bytes to int16 array
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Handle stereo to mono conversion if needed
            if len(audio_array) % 2 == 0:
                # Check if this might be stereo by testing if reshaping makes sense
                try:
                    stereo_test = audio_array.reshape(-1, 2)
                    if stereo_test.shape[0] > 1000:  # Reasonable audio length
                        # Convert stereo to mono by averaging channels
                        audio_array = stereo_test.mean(axis=1).astype(np.int16)
                        logger.info("🎙️ Converted stereo PCM to mono")
                except:
                    pass  # Keep original mono data
            
            # Normalize to float32 in range [-1, 1]
            audio_array = audio_array.astype(np.float32) / 32768.0
            
            # Resample if needed (librosa.resample expects float input)
            if sample_rate != 16000:
                audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
                logger.info(f"🎙️ Resampled from {sample_rate}Hz to 16000Hz")
            
            # Calculate audio duration
            duration = len(audio_array) / 16000  # Now using 16kHz
            logger.info(f"🎙️ PCM audio duration: {duration:.1f} seconds")
            
            # Prepare generation kwargs
            generate_kwargs = {
                "task": "transcribe"  # Explicitly set to transcribe (not translate)
            }
            
            # Add language if specified
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            # Process audio using manual chunking for better control
            transcriptions = []
            
            # Chunk audio into 30-second segments for processing
            chunk_duration = 30  # seconds
            chunk_samples = chunk_duration * 16000  # 16kHz sample rate
            audio_length = len(audio_array)
            
            if duration > 30:
                logger.info(f"🎙️ Long PCM audio detected ({duration:.1f}s) - using chunked transcription")
                
                for i in range(0, audio_length, chunk_samples):
                    chunk_end = min(i + chunk_samples, audio_length)
                    audio_chunk = audio_array[i:chunk_end]
                    chunk_time = i / 16000
                    chunk_num = i // chunk_samples + 1
                    total_chunks = (audio_length + chunk_samples - 1) // chunk_samples
                    
                    logger.info(f"🎙️ Processing PCM chunk {chunk_num}/{total_chunks} (time: {chunk_time:.1f}s)")
                    
                    # Process audio chunk
                    inputs = self.processor(audio_chunk, sampling_rate=16000, return_tensors="pt")
                    input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
                    
                    # Create attention mask for this chunk
                    attention_mask = torch.ones(input_features.shape[:-1], dtype=torch.long, device=self.device)
                    
                    try:
                        with torch.no_grad():
                            predicted_ids = self.model.generate(
                                input_features,
                                attention_mask=attention_mask,
                                max_length=448,
                                num_beams=5,
                                repetition_penalty=1.1,
                                no_repeat_ngram_size=3,
                                **generate_kwargs
                            )
                        
                        # Decode the transcription
                        chunk_transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                        transcriptions.append(chunk_transcription.strip())
                        
                    except torch.cuda.OutOfMemoryError:
                        logger.warning("🎙️ CUDA out of memory, falling back to CPU for this PCM chunk...")
                        # Move model to CPU temporarily
                        self.model.to("cpu")
                        input_features = input_features.to(device="cpu", dtype=torch.float32)
                        attention_mask = attention_mask.to("cpu")
                        
                        with torch.no_grad():
                            predicted_ids = self.model.generate(
                                input_features,
                                attention_mask=attention_mask,
                                max_length=448,
                                num_beams=5,
                                repetition_penalty=1.1,
                                no_repeat_ngram_size=3,
                                **generate_kwargs
                            )
                        
                        chunk_transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                        transcriptions.append(chunk_transcription.strip())
                        
                        # Move model back to original device
                        self.model.to(self.device)
                
                # Combine all transcriptions
                transcript = " ".join(transcriptions)
                
            else:
                logger.info("🎙️ Short PCM audio detected (≤30s) - using standard transcription")
                
                # Process audio directly
                inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt")
                input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
                
                # Create attention mask
                attention_mask = torch.ones(input_features.shape[:-1], dtype=torch.long, device=self.device)
                
                try:
                    with torch.no_grad():
                        predicted_ids = self.model.generate(
                            input_features,
                            attention_mask=attention_mask,
                            max_length=448,
                            num_beams=5,
                            repetition_penalty=1.1,
                            no_repeat_ngram_size=3,
                            **generate_kwargs
                        )
                    
                    # Decode the transcription
                    transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                    
                except torch.cuda.OutOfMemoryError:
                    logger.warning("🎙️ CUDA out of memory, falling back to CPU for PCM audio...")
                    # Move model to CPU temporarily
                    self.model.to("cpu")
                    input_features = input_features.to(device="cpu", dtype=torch.float32)
                    attention_mask = attention_mask.to("cpu")
                    
                    with torch.no_grad():
                        predicted_ids = self.model.generate(
                            input_features,
                            attention_mask=attention_mask,
                            max_length=448,
                            num_beams=5,
                            repetition_penalty=1.1,
                            no_repeat_ngram_size=3,
                            **generate_kwargs
                        )
                    
                    transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                    
                    # Move model back to original device
                    self.model.to(self.device)
            
            logger.info(f"✅ PCM transcription completed: {len(transcript)} characters")
            
            return transcript
            
        except Exception as e:
            logger.error(f"❌ PCM transcription failed: {e}")
            raise RuntimeError(f"PCM transcription failed: {str(e)}")
    
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
        return self.is_loaded and self.model is not None and self.processor is not None

# Global instance following your pattern
whisper_model = WhisperModel()