import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
from datetime import datetime
from typing import Dict, List, Optional
import gc

logger = logging.getLogger(__name__)

class TranslationModel:
    """Translation model with intelligent chunking support"""

    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("translation")
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        self.load_time = None
        self.error = None
        self.max_length = 512  # Model's maximum token limit

    def load(self) -> bool:
        try:
            logger.info(f"Loading translation model...")
            start_time = datetime.now()
            
            # Get HuggingFace model loading kwargs
            hf_kwargs = self.settings.get_hf_model_kwargs()
            
            # Check if we should use HuggingFace Hub models
            if self.settings.use_hf_models and self.settings.hf_translator_model:
                # Use HuggingFace Hub model
                model_id = self.settings._get_hf_model_id("translator")
                logger.info(f"🌐 Loading translation model from HuggingFace Hub: {model_id}")
                
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(model_id, **hf_kwargs)
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id, **hf_kwargs)
                    logger.info(f"✅ HuggingFace translation model loaded successfully")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load HF translation model {model_id}: {e}")
                    logger.info("🔄 Falling back to local model loading")
                    # Fall through to local loading
                    
            if not self.model:  # Either use_hf_models=False or HF loading failed
                # Check if model path exists
                if not os.path.exists(self.model_path):
                    raise FileNotFoundError(f"Translation model path not found: {self.model_path}")
                
                # Check for required model files
                required_files = ["config.json"]
                for file in required_files:
                    file_path = os.path.join(self.model_path, file)
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Required model file not found: {file_path}")
                
                # Load tokenizer and model with local_files_only
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path,
                    local_files_only=True  # Force local loading
                )
                
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_path,
                    local_files_only=True  # Force local loading
            )
            
            self.model.to(self.device)
            self.loaded = True
            self.load_time = datetime.now()
            load_duration = (self.load_time - start_time).total_seconds()
            
            logger.info(f"✅ Translation model loaded successfully in {load_duration:.2f}s")
            return True
            
        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"❌ Failed to load translation model: {e}")
            return False

    def translate(self, text: str) -> str:
        """
        Translate text with automatic chunking for long inputs
        
        Args:
            text: Input text to translate
            
        Returns:
            Translated text
        """
        if not self.loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError("Translation model not loaded")

        if not text or not text.strip():
            return ""

        text = text.strip()
        
        try:
            # Check if text needs chunking
            token_count = len(self.tokenizer.encode(text, add_special_tokens=True))
            
            if token_count <= self.max_length - 50:  # Leave buffer for special tokens
                # Single translation
                return self._translate_single(text)
            else:
                # Chunked translation
                logger.info(f"🔄 Text too long ({token_count} tokens), using chunked translation")
                return self._translate_chunked(text)
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise RuntimeError(f"Translation failed: {str(e)}")
        finally:
            # Clean up GPU memory after translation
            self._cleanup_memory()

    def _translate_single(self, text: str) -> str:
        """Translate a single text chunk"""
        try:
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=self.max_length,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self.max_length,
                    num_beams=4,
                    length_penalty=0.6,
                    early_stopping=True,
                    do_sample=False
                )
            
            translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translated.strip()
            
        except Exception as e:
            logger.error(f"Single translation failed: {e}")
            raise

    def _translate_chunked(self, text: str) -> str:
        """Translate text using intelligent chunking"""
        from ..core.text_chunker import text_chunker
        
        # Get chunks optimized for translation
        chunks = text_chunker.chunk_text(text, strategy="translation")
        logger.info(f"🔄 Processing {len(chunks)} translation chunks")
        
        translated_parts = []
        
        for i, chunk in enumerate(chunks):
            try:
                logger.debug(f"Translating chunk {i+1}/{len(chunks)} ({chunk.token_count} tokens)")
                
                # Translate individual chunk
                chunk_translation = self._translate_single(chunk.text)
                
                # Handle overlap: if this chunk overlaps with previous, merge intelligently
                if chunk.overlap_with_previous and translated_parts:
                    chunk_translation = self._merge_overlapping_translations(
                        translated_parts[-1], chunk_translation, chunk
                    )
                    translated_parts[-1] = chunk_translation
                else:
                    translated_parts.append(chunk_translation)
                
                # Clean up between chunks
                if i % 5 == 0:  # Every 5 chunks
                    self._cleanup_memory()
                    
            except Exception as e:
                logger.error(f"Failed to translate chunk {i+1}: {e}")
                # Use original text as fallback for this chunk
                translated_parts.append(chunk.text)
        
        # Combine translated parts
        result = self._combine_translations(translated_parts, chunks)
        logger.info(f"✅ Chunked translation completed: {len(result)} characters")
        
        return result

    def _merge_overlapping_translations(self, prev_translation: str, current_translation: str, 
                                      current_chunk) -> str:
        """Intelligently merge overlapping translations"""
        # Simple strategy: take the longer translation or combine if they're similar
        prev_words = prev_translation.split()
        curr_words = current_translation.split()
        
        # If current translation is significantly longer, prefer it
        if len(curr_words) > len(prev_words) * 1.2:
            return current_translation
        
        # Otherwise, try to find overlap and merge
        # This is a simplified approach - in production, use more sophisticated NLP
        overlap_threshold = min(10, len(prev_words) // 4)
        
        for i in range(min(overlap_threshold, len(prev_words))):
            prev_suffix = ' '.join(prev_words[-i-1:])
            if current_translation.startswith(prev_suffix.split()[0]):
                # Found potential overlap, combine
                return prev_translation + " " + current_translation[len(prev_suffix):].strip()
        
        # No clear overlap found, just concatenate
        return prev_translation + " " + current_translation

    def _combine_translations(self, translated_parts: List[str], chunks) -> str:
        """Combine translated parts into final result"""
        if not translated_parts:
            return ""
        
        if len(translated_parts) == 1:
            return translated_parts[0]
        
        # Join with spaces, handling punctuation
        result_parts = []
        
        for i, part in enumerate(translated_parts):
            part = part.strip()
            if not part:
                continue
                
            # Add appropriate spacing/punctuation
            if i == 0:
                result_parts.append(part)
            else:
                # Check if previous part ends with sentence-ending punctuation
                prev_part = result_parts[-1] if result_parts else ""
                if prev_part and prev_part[-1] in '.!?':
                    result_parts.append(part)
                else:
                    # Add space if needed
                    if part and not part[0].isupper():
                        result_parts.append(" " + part)
                    else:
                        result_parts.append(" " + part)
        
        return ''.join(result_parts).strip()

    def _cleanup_memory(self):
        """Clean up GPU memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def translate_with_fallback(self, text: str, max_retries: int = 2) -> Optional[str]:
        """
        Translate with fallback strategies for robust processing
        
        Args:
            text: Input text
            max_retries: Maximum number of retry attempts
            
        Returns:
            Translated text or None if all attempts fail
        """
        if not text or not text.strip():
            return None
            
        for attempt in range(max_retries + 1):
            try:
                return self.translate(text)
            except Exception as e:
                logger.warning(f"Translation attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries:
                    logger.error(f"All translation attempts failed for text length {len(text)}")
                    return None
                
                # Clean up before retry
                self._cleanup_memory()
        
        return None

    def estimate_translation_time(self, text: str) -> float:
        """Estimate translation time in seconds"""
        if not text:
            return 0.0
            
        from ..core.text_chunker import text_chunker
        
        token_count = len(self.tokenizer.encode(text)) if self.tokenizer else len(text) // 4
        
        if token_count <= self.max_length:
            return 1.0  # Single chunk
        else:
            chunks = text_chunker.chunk_text(text, strategy="translation")
            return text_chunker.estimate_processing_time(chunks, "translation")

    def get_model_info(self) -> Dict:
        return {
            "model_path": self.model_path,
            "device": str(self.device),
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "error": self.error,
            "max_length": self.max_length,
            "chunking_supported": True,
            "fallback_strategies": ["chunked_translation", "memory_cleanup", "retry_logic"]
        }

# Global instance
translator_model = TranslationModel()