import torch
import logging
import librosa
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WhisperModel:
    """HuggingFace Whisper model supporting both transcription and translation"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.model_path = model_path or settings.get_model_path("whisper")
        # self.enable_translation = enable_translation
        
        # if enable_translation:
        #     # Use configured HF whisper large v3 as fallback (do not reference OpenAI)
        #     model_id = (
        #         self.settings.hf_asr_model
        #         if getattr(self.settings, "hf_asr_model", None)
        #         else self.settings.get_active_whisper_path()
        #     )
        #     self.model_version = "large-v3"
        # else:
        #     # Use configured HF whisper large turbo as fallback (do not reference OpenAI)
        #     model_id = (
        #         self.settings.hf_whisper_large_turbo
        #         if getattr(self.settings, "hf_whisper_large_turbo", None)
        #         else self.settings.get_active_whisper_path()
        #     )
        #     self.model_version = "large-v3-turbo"
        
        self.model = None
        self.processor = None
        self.device = None
        self.torch_dtype = None
        self.is_loaded = False
        self.error = None
        self.current_model_id = None
        
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
            
            logger.info(f"Using device: {self.device}, dtype: {self.torch_dtype}")
            # logger.info(f"Translation enabled: {self.enable_translation}, Target model: {self.model_version}")
            
            if self.settings.use_hf_models:
                # Use HuggingFace Hub models WITHOUT authentication
                model_id = self.settings.get_asr_model_id()
                logger.info(f"Loading Whisper model from HuggingFace Hub (public): {model_id}")
                
                try:
                    # Load with authentication kwargs from settings
                    hf_kwargs = self.settings.get_hf_model_kwargs()
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
                    
                    self.current_model_id = self.model_path
                    logger.info(f"✅ Local Whisper model loaded successfully")
                    
                except Exception as e:
                    logger.warning(f"Failed to load HF model {model_id}: {e}")
                    # logger.info(f"Falling back to default HuggingFace model: {model_id}")
                    
                    # hf_kwargs = self.settings.get_hf_model_kwargs()
                    # self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    #     model_id, 
                    #     torch_dtype=self.torch_dtype, 
                    #     low_cpu_mem_usage=True, 
                    #     use_safetensors=True,
                    #     **hf_kwargs
                    # )
                    # self.processor = AutoProcessor.from_pretrained(model_id, **hf_kwargs)
                    # self.current_model_id = model_id
                    
            else:
                # Use local models with fallback to HuggingFace
                if self._check_local_model_exists():
                    try:
                        logger.info(f"Loading local Whisper model from {self.model_path}")
                        
                        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                            self.model_path,
                            local_files_only=True,
                            torch_dtype=self.torch_dtype, 
                            low_cpu_mem_usage=True, 
                            use_safetensors=True
                        )
                        
                        self.processor = AutoProcessor.from_pretrained(
                            self.model_path,
                            local_files_only=True
                        )
                        
                        self.current_model_id = self.model_path
                        logger.info(f"Local Whisper model loaded successfully")
                        
                    except Exception as e:
                        logger.warning(f"Failed to load local model: {e}")
                        logger.info(f"Falling back to HuggingFace Hub download")
                        raise
                        
                else:
                    logger.info(f"Local model not found, downloading from HuggingFace Hub: {model_id}")
                    
                    # hf_kwargs = self.settings.get_hf_model_kwargs()
                    # self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    #     model_id, 
                    #     torch_dtype=self.torch_dtype, 
                    #     low_cpu_mem_usage=True, 
                    #     use_safetensors=True,
                    #     **hf_kwargs
                    # )
                    
                    # self.processor = AutoProcessor.from_pretrained(model_id, **hf_kwargs)
                    # self.current_model_id = model_id
            
            # Move model to device
            self.model.to(self.device)
            
            # No pipeline - use direct model calls for better quality control
            # Pipeline abstracts away important generation parameters needed for quality
            
            self.is_loaded = True
            self.error = None
            logger.info(f"✅ Whisper model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            # If local loading failed, try fallback
            if "local_files_only" in str(e) or "not found" in str(e).lower():
                try:
                    logger.info(f"Local loading failed, downloading from HuggingFace Hub: {model_id}")
                    
                    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        model_id, 
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    self.model.to(self.device)
                    
                    # self.processor = AutoProcessor.from_pretrained(model_id, **hf_kwargs)
                    # self.current_model_id = model_id
                    
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
    
    def transcribe_audio_file(self, audio_file_path: str, language: Optional[str] = None, task: str = "transcribe") -> str:
        """Transcribe or translate audio file to text with support for long audio"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            logger.info(f"🎙️ Transcribing audio file: {Path(audio_file_path).name}")
            
            # if task not in ["transcribe", "translate"]:
            #     raise ValueError(f"Task must be 'transcribe' or 'translate', got: {task}")
            
            # if task == "translate" and not self.enable_translation:
            #     raise RuntimeError("Translation requested but model loaded without translation support. Use enable_translation=True.")
            
            # Validate and normalize language
            validated_language = self._validate_language(language)
            if task == "transcribe":
                if validated_language:
                    logger.info(f"🎙️ Transcribing in: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')})")
                else:
                    logger.info("🎙️ Transcribing with auto-detected language")
            else:  # translate
                if validated_language:
                    logger.info(f"🎙️ Translating from: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')}) → English")
                else:
                    logger.info("🎙️ Translating from auto-detected language → English")
            
            # Load audio with librosa (handles multiple formats)
            audio_array, sample_rate = librosa.load(audio_file_path, sr=16000, mono=True)
            
            # Calculate audio duration
            duration = len(audio_array) / sample_rate
            logger.info(f"🎙️ Audio duration: {duration:.1f} seconds")
            
            # Prepare generation kwargs with task selection
            generate_kwargs = {
                "task": task  # "transcribe" or "translate"
            }
            
            # Add language if specified
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            # Process audio using manual chunking for better control (like scp-fix branch)
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
                    
                    # Process audio chunk using direct model calls (like scp-fix)
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
                                num_beams=5,                # QUALITY: Beam search
                                repetition_penalty=1.1,    # QUALITY: Avoid repetition
                                no_repeat_ngram_size=3,     # QUALITY: Avoid n-gram repetition
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
                
                # Process audio directly using direct model calls
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
                            num_beams=5,                # QUALITY: Beam search
                            repetition_penalty=1.1,    # QUALITY: Avoid repetition
                            no_repeat_ngram_size=3,     # QUALITY: Avoid n-gram repetition
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
                            length_penalty=1.0,
                            early_stopping=True,
                            do_sample=False,
                            **generate_kwargs
                        )
                    
                    transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                    
                    # Move model back to original device
                    self.model.to(self.device)
            
            task_desc = "Transcription" if task == "transcribe" else "Translation"
            logger.info(f"✅ {task_desc} completed: {len(transcript)} characters")
            
            return transcript
            
        except Exception as e:
            task_desc = "Transcription" if task == "transcribe" else "Translation"
            logger.error(f"❌ {task_desc} failed: {e}")
            raise RuntimeError(f"{task_desc} failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None, task: str = "transcribe") -> str:
        """Transcribe or translate audio from bytes (for uploaded files)"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            try:
                temp_file.write(audio_bytes)
                temp_file.flush()
                
                result = self.transcribe_audio_file(temp_file.name, language, task)
                return result
                
            finally:
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def transcribe_pcm_audio(self, pcm_bytes: bytes, sample_rate: int = 16000, language: Optional[str] = None, task: str = "transcribe") -> str:
        """Transcribe or translate PCM audio data directly from bytes
        
        Args:
            pcm_bytes: Raw PCM audio data as bytes
            sample_rate: Sample rate of the audio data (default: 16000)
            language: Source language for transcription, or source language for translation (auto-detect if None)
            task: Either "transcribe" (same language) or "translate" (to English)
        """
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Validate task
            if task not in ["transcribe", "translate"]:
                raise ValueError(f"Task must be 'transcribe' or 'translate', got: {task}")
            
            # Convert PCM bytes to numpy array
            import numpy as np
            
            # PCM data is typically 16-bit signed integers
            audio_array = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
            
            # Normalize to [-1, 1] range
            audio_array = audio_array / 32768.0
            
            # Check for silent/empty audio to prevent hallucinations
            audio_energy = np.mean(np.abs(audio_array))
            silence_threshold = 0.001  # Very low threshold for silence detection
            
            if audio_energy < silence_threshold:
                return ""  # Return empty string for silent audio
            
            # Resample if necessary (Whisper expects 16kHz)
            if sample_rate != 16000:
                audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
                sample_rate = 16000
            
            # Calculate audio duration
            duration = len(audio_array) / sample_rate
            
            # Minimal logging for streaming chunks
            validated_language = self._validate_language(language)
            
            # Use direct model calls instead of pipeline for better quality
            # Prepare generation kwargs with task selection
            generate_kwargs = {
                "task": task
            }
            
            # Add language if specified
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            # Process using direct model calls for quality (like scp-fix branch)
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
                        num_beams=5,                # QUALITY: Beam search
                        repetition_penalty=1.1,    # QUALITY: Avoid repetition
                        no_repeat_ngram_size=3,     # QUALITY: Avoid n-gram repetition
                        length_penalty=1.0,        # QUALITY: Balanced length preference
                        early_stopping=True,       # QUALITY: Stop when appropriate
                        do_sample=False,           # QUALITY: Deterministic for consistency
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
                        length_penalty=1.0,
                        early_stopping=True,
                        do_sample=False,
                        **generate_kwargs
                    )
                
                transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                
                # Move model back to original device
                self.model.to(self.device)
            
            # Filter out common Whisper hallucinations for low-quality/silent audio
            common_hallucinations = [
                "Thank you.", "Thanks.", "Okay.", "OK.", "Hello.", "Hi.", 
                "Thank you for watching.", "Thanks for watching.",
                "Thank you for your attention.", "See you next time.",
                "Bye.", "Goodbye.", ""
            ]
            
            # If audio energy was low and result is a common hallucination, return empty
            if audio_energy < 0.005 and transcript in common_hallucinations:
                logger.info(f"🚫 Filtered hallucination: '{transcript}'")
                return ""
            
            # Only log non-empty results for streaming  
            if transcript:
                logger.debug(f"✅ PCM: {len(transcript)} chars")
            
            return transcript
            
        except Exception as e:
            task_desc = "Transcription" if task == "transcribe" else "Translation"
            logger.error(f"❌ PCM {task_desc} failed: {e}")
            raise RuntimeError(f"PCM {task_desc} failed: {str(e)}")
    
    # ============================================================================
    # NEW METHODS: Ensure both transcript and translation are returned
    # ============================================================================
    
    # def transcribe_and_translate(
    #     self,
    #     audio_file_path: str,
    #     language: Optional[str] = None
    # ) -> Dict[str, str]:
    #     """
    #     Get both transcript (original language) AND translation (English) from audio file
        
    #     This method ensures you always get both outputs instead of just one.
        
    #     Args:
    #         audio_file_path: Path to audio file
    #         language: Source language code (e.g., "sw" for Swahili)
        
    #     Returns:
    #         Dict with keys:
    #             - 'transcript': Original language text
    #             - 'translation': English translation (or None if translation not enabled)
        
    #     Example:
    #         result = whisper_model.transcribe_and_translate("audio.wav", language="sw")
    #         print(result['transcript'])   # "Mimi nina tatizo..."
    #         print(result['translation'])  # "I have a problem..."
    #     """
    #     if not self.is_loaded:
    #         raise RuntimeError("Whisper model not loaded")
        
    #     logger.info(f"📝 Processing audio for both transcription and translation")
        
    #     result = {
    #         "transcript": None,
    #         "translation": None
    #     }
        
    #     try:
    #         # STEP 1: Always get original language transcript first
    #         logger.info(f"  Step 1: Transcribing in {language or 'auto-detected language'}...")
    #         result["transcript"] = self.transcribe_audio_file(
    #             audio_file_path=audio_file_path,
    #             language=language,
    #             task="transcribe"  # ALWAYS transcribe first
    #         )
    #         logger.info(f"✅ Transcript complete: {len(result['transcript'])} characters")
            
    #         # STEP 2: Get English translation
    #         if self.enable_translation:
    #             logger.info(f"  Step 2: Translating to English...")
    #             result["translation"] = self.transcribe_audio_file(
    #                 audio_file_path=audio_file_path,
    #                 language=language,
    #                 task="translate"  # Now get English translation
    #             )
    #             logger.info(f"✅ Translation complete: {len(result['translation'])} characters")
    #         else:
    #             logger.warning("⚠️ Translation skipped (model loaded without enable_translation=True)")
    #             result["translation"] = None
            
    #         return result
            
    #     except Exception as e:
    #         logger.error(f"❌ Transcription and translation failed: {e}")
    #         raise RuntimeError(f"Transcription and translation failed: {str(e)}")
    
    # def transcribe_and_translate_bytes(
    #     self,
    #     audio_bytes: bytes,
    #     language: Optional[str] = None
    # ) -> Dict[str, str]:
    #     """
    #     Get both transcript and translation from audio bytes
        
    #     Args:
    #         audio_bytes: Audio data as bytes
    #         language: Source language code (e.g., "sw")
        
    #     Returns:
    #         Dict with 'transcript' and 'translation' keys
    #     """
    #     if not self.is_loaded:
    #         raise RuntimeError("Whisper model not loaded")
        
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
    #         try:
    #             temp_file.write(audio_bytes)
    #             temp_file.flush()
                
    #             result = self.transcribe_and_translate(temp_file.name, language)
    #             return result
                
    #         finally:
    #             try:
    #                 os.unlink(temp_file.name)
    #             except:
    #                 pass
    
    def process_audio_with_options(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        include_translation: bool = False
    ) -> Dict[str, Any]:
        """
        Flexible audio processing method that returns transcript and optional translation
        
        This is the main method you should use in your endpoints.
        
        Args:
            audio_file_path: Path to audio file
            language: Source language code (e.g., "sw")
            include_translation: Whether to include English translation
        
        Returns:
            Dict with keys:
                - 'transcript': Original language text (ALWAYS present)
                - 'translation': English translation (only if include_translation=True)
                - 'language': Language code used
                - 'has_translation': Boolean indicating if translation was performed
        
        Example:
            # Just transcription
            result = whisper_model.process_audio_with_options("audio.wav", "sw", False)
            # Returns: {'transcript': '...', 'translation': None, ...}
            
            # Transcription + translation
            result = whisper_model.process_audio_with_options("audio.wav", "sw", True)
            # Returns: {'transcript': '...', 'translation': '...', ...}
        """
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        logger.info(f"🎤 Processing audio: {Path(audio_file_path).name}")
        logger.info(f"   Language: {language or 'auto-detect'}")
        logger.info(f"   Include translation: {include_translation}")
        
        result = {
            "transcript": None,
            "translation": None,
            "language": language,
            "has_translation": False
        }
        
        try:
            # ALWAYS get transcript first
            result["transcript"] = self.transcribe_audio_file(
                audio_file_path=audio_file_path,
                language=language,
                task="transcribe"
            )
            logger.info(f"✅ Transcript: {len(result['transcript'])} chars")
            
            # Optionally get translation
            if include_translation:
                if self.enable_translation:
                    result["translation"] = self.transcribe_audio_file(
                        audio_file_path=audio_file_path,
                        language=language,
                        task="translate"
                    )
                    result["has_translation"] = True
                    logger.info(f"✅ Translation: {len(result['translation'])} chars")
                else:
                    logger.warning("⚠️ Translation requested but model doesn't support it")
                    result["translation"] = None
                    result["has_translation"] = False
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Audio processing failed: {e}")
            raise RuntimeError(f"Audio processing failed: {str(e)}")
    
    # ============================================================================
    # End of new methods
    # ============================================================================
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return self.supported_languages.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": "whisper",
            "model_path": self.model_path,
            "hf_repo_id": self.current_model_id, # Using model_id as the primary HF identifier
            "loaded": self.is_loaded,
            "load_time": None, # Whisper model doesn't track load_time explicitly
            "device": str(self.device) if self.device else None,
            "torch_dtype": str(self.torch_dtype) if self.torch_dtype else None,
            "is_loaded": self.is_loaded,
            "error": self.error,
            "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"],
            "max_audio_length": "unlimited (chunked processing)",
            "sample_rate": "16kHz",
            "tasks_supported": "transcribe" if not self.enable_translation else "transcribe, translate",
            "languages": "multilingual (99+ languages)",
            "version": self.model_version,
            "current_model_id": self.current_model_id,
            "translation_enabled": self.enable_translation,
            "long_form_support": True,
            "supported_language_codes": list(self.supported_languages.keys()),
            "local_model_available": self._check_local_model_exists()
        }
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.is_loaded and self.model is not None and self.processor is not None

# Global instances
whisper_model = WhisperModel()
# whisper_translation_model = whisper_model