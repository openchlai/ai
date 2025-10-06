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
    
    def __init__(self, model_path: str = None, enable_translation: bool = True):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("whisper")
        self.enable_translation = enable_translation
        
        if enable_translation:
            self.fallback_model_id = "openai/whisper-large-v3"
            self.model_version = "large-v3"
        else:
            self.fallback_model_id = "openai/whisper-large-v3-turbo"
            self.model_version = "large-v3-turbo"
        
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
        
        required_files = ["config.json"]
        optional_files = ["model.safetensors", "pytorch_model.bin"]
        
        config_path = os.path.join(self.model_path, "config.json")
        if not os.path.exists(config_path):
            return False
        
        model_file_exists = any(
            os.path.exists(os.path.join(self.model_path, file)) 
            for file in optional_files
        )
        
        if not model_file_exists:
            logger.warning(f"Config found but no model files in {self.model_path}")
            return False
        
        logger.info(f"Local Whisper model files detected in {self.model_path}")
        return True
        
    def load(self) -> bool:
        """Load Whisper model with HuggingFace Hub support - NO AUTHENTICATION"""
        try:
            logger.info(f"Loading Whisper model...")
            
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
            
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            logger.info(f"Using device: {self.device}, dtype: {self.torch_dtype}")
            logger.info(f"Translation enabled: {self.enable_translation}, Target model: {self.model_version}")
            
            if self.settings.use_hf_models:
                # Use HuggingFace Hub models WITHOUT authentication
                model_id = self.settings.get_active_whisper_path()
                logger.info(f"Loading Whisper model from HuggingFace Hub (public): {model_id}")
                
                try:
                    # Load WITHOUT any authentication kwargs
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        model_id,
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    
                    self.processor = AutoProcessor.from_pretrained(model_id)
                    self.current_model_id = model_id
                    logger.info(f"HuggingFace Whisper model loaded successfully")
                    
                except Exception as e:
                    logger.warning(f"Failed to load HF model {model_id}: {e}")
                    logger.info(f"Falling back to default HuggingFace model: {self.fallback_model_id}")
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.fallback_model_id, 
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    self.processor = AutoProcessor.from_pretrained(self.fallback_model_id)
                    self.current_model_id = self.fallback_model_id
                    
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
                    logger.info(f"Local model not found, downloading from HuggingFace Hub: {self.fallback_model_id}")
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.fallback_model_id, 
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    
                    self.processor = AutoProcessor.from_pretrained(self.fallback_model_id)
                    self.current_model_id = self.fallback_model_id
            
            # Move model to device
            self.model.to(self.device)
            
            self.is_loaded = True
            self.error = None
            logger.info(f"Whisper model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            if "local_files_only" in str(e) or "not found" in str(e).lower():
                try:
                    logger.info(f"Local loading failed, downloading from HuggingFace Hub: {self.fallback_model_id}")
                    
                    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
                    
                    self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.fallback_model_id, 
                        torch_dtype=self.torch_dtype, 
                        low_cpu_mem_usage=True, 
                        use_safetensors=True
                    )
                    self.model.to(self.device)
                    
                    self.processor = AutoProcessor.from_pretrained(self.fallback_model_id)
                    self.current_model_id = self.fallback_model_id
                    
                    self.is_loaded = True
                    self.error = None
                    logger.info(f"Whisper model loaded from Hugging Face Hub via fallback on {self.device}")
                    return True
                    
                except Exception as fallback_error:
                    error_msg = f"Failed to load Whisper model (local and fallback): {fallback_error}"
                    logger.error(f"{error_msg}")
                    self.error = error_msg
                    self.is_loaded = False
                    return False
            else:
                error_msg = f"Failed to load Whisper model: {e}"
                logger.error(f"{error_msg}")
                self.error = error_msg
                self.is_loaded = False
                return False
    
    def _validate_language(self, language: Optional[str]) -> Optional[str]:
        """Validate and normalize language code"""
        if not language or language.lower() in ["auto", "none", ""]:
            return None
        
        lang_code = language.lower().strip()
        
        if lang_code in self.supported_languages:
            return lang_code
        
        for code, name in self.supported_languages.items():
            if name.lower() == lang_code:
                return code
        
        logger.warning(f"Language '{language}' not in known list, but will attempt transcription")
        return lang_code
    
    def transcribe_audio_file(self, audio_file_path: str, language: Optional[str] = None, task: str = "transcribe") -> str:
        """Transcribe or translate audio file to text with support for long audio"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            logger.info(f"Transcribing audio file: {Path(audio_file_path).name}")
            
            if task not in ["transcribe", "translate"]:
                raise ValueError(f"Task must be 'transcribe' or 'translate', got: {task}")
            
            if task == "translate" and not self.enable_translation:
                raise RuntimeError("Translation requested but model loaded without translation support. Use enable_translation=True.")
            
            validated_language = self._validate_language(language)
            if task == "transcribe":
                if validated_language:
                    logger.info(f"Transcribing in: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')})")
                else:
                    logger.info("Transcribing with auto-detected language")
            else:
                if validated_language:
                    logger.info(f"Translating from: {validated_language} ({self.supported_languages.get(validated_language, 'Unknown')}) to English")
                else:
                    logger.info("Translating from auto-detected language to English")
            
            audio_array, sample_rate = librosa.load(audio_file_path, sr=16000, mono=True)
            
            duration = len(audio_array) / sample_rate
            logger.info(f"Audio duration: {duration:.1f} seconds")
            
            generate_kwargs = {
                "task": task
            }
            
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            transcriptions = []
            
            chunk_duration = 30
            chunk_samples = chunk_duration * sample_rate
            audio_length = len(audio_array)
            
            if duration > 30:
                logger.info(f"Long audio detected ({duration:.1f}s) - using chunked transcription")
                
                for i in range(0, audio_length, chunk_samples):
                    chunk_end = min(i + chunk_samples, audio_length)
                    audio_chunk = audio_array[i:chunk_end]
                    chunk_time = i / sample_rate
                    chunk_num = i // chunk_samples + 1
                    total_chunks = (audio_length + chunk_samples - 1) // chunk_samples
                    
                    logger.info(f"Processing chunk {chunk_num}/{total_chunks} (time: {chunk_time:.1f}s)")
                    
                    inputs = self.processor(audio_chunk, sampling_rate=sample_rate, return_tensors="pt")
                    input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
                    
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
                        
                        chunk_transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
                        transcriptions.append(chunk_transcription.strip())
                        
                    except torch.cuda.OutOfMemoryError:
                        logger.warning("CUDA out of memory, falling back to CPU for this chunk...")
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
                        
                        self.model.to(self.device)
                
                transcript = " ".join(transcriptions)
                
            else:
                logger.info("Short audio detected (<=30s) - using standard transcription")
                
                inputs = self.processor(audio_array, sampling_rate=sample_rate, return_tensors="pt")
                input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
                
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
                    
                    transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                    
                except torch.cuda.OutOfMemoryError:
                    logger.warning("CUDA out of memory, falling back to CPU...")
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
                    
                    self.model.to(self.device)
            
            task_desc = "Transcription" if task == "transcribe" else "Translation"
            logger.info(f"{task_desc} completed: {len(transcript)} characters")
            
            return transcript
            
        except Exception as e:
            task_desc = "Transcription" if task == "transcribe" else "Translation"
            logger.error(f"{task_desc} failed: {e}")
            raise RuntimeError(f"{task_desc} failed: {str(e)}")
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None, task: str = "transcribe") -> str:
        """Transcribe or translate audio from bytes"""
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
        """Transcribe or translate PCM audio data directly from bytes"""
        if not self.is_loaded:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            if task not in ["transcribe", "translate"]:
                raise ValueError(f"Task must be 'transcribe' or 'translate', got: {task}")
            
            import numpy as np
            
            audio_array = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
            audio_array = audio_array / 32768.0
            
            audio_energy = np.mean(np.abs(audio_array))
            silence_threshold = 0.001
            
            if audio_energy < silence_threshold:
                return ""
            
            if sample_rate != 16000:
                audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
                sample_rate = 16000
            
            validated_language = self._validate_language(language)
            
            generate_kwargs = {
                "task": task
            }
            
            if validated_language:
                generate_kwargs["language"] = validated_language
            
            inputs = self.processor(audio_array, sampling_rate=sample_rate, return_tensors="pt")
            input_features = inputs.input_features.to(device=self.device, dtype=self.torch_dtype)
            
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
                        length_penalty=1.0,
                        early_stopping=True,
                        do_sample=False,
                        **generate_kwargs
                    )
                
                transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                
            except torch.cuda.OutOfMemoryError:
                logger.warning("CUDA out of memory, falling back to CPU...")
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
                
                self.model.to(self.device)
            
            common_hallucinations = [
                "Thank you.", "Thanks.", "Okay.", "OK.", "Hello.", "Hi.", 
                "Thank you for watching.", "Thanks for watching.",
                "Thank you for your attention.", "See you next time.",
                "Bye.", "Goodbye.", ""
            ]
            
            if audio_energy < 0.005 and transcript in common_hallucinations:
                logger.info(f"Filtered hallucination: '{transcript}'")
                return ""
            
            if transcript:
                logger.debug(f"PCM: {len(transcript)} chars")
            
            return transcript
            
        except Exception as e:
            task_desc = "Transcription" if task == "transcribe" else "Translation"
            logger.error(f"PCM {task_desc} failed: {e}")
            raise RuntimeError(f"PCM {task_desc} failed: {str(e)}")
    
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
whisper_model = WhisperModel(enable_translation=True)
whisper_translation_model = whisper_model