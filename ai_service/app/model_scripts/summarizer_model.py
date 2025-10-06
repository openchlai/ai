# app/models/summarizer_model.py

import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import os
from datetime import datetime
from typing import Dict, List, Optional
import gc

logger = logging.getLogger(__name__)

class SummarizationModel:
    """Summarization model with intelligent chunking and hierarchical summarization"""

    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.model_path = model_path or settings.get_model_path("summarization")
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        self.load_time = None
        self.error = None
        self.max_length = 512  # Model's maximum input token limit
        
        # Hugging Face repo support (hub-first)
        self.hf_repo_id = os.getenv("SUMMARIZATION_HF_REPO_ID") or getattr(settings, "summarization_hf_repo_id", None)

    def load(self) -> bool:
        try:
            logger.info(f"📦 Initializing summarization model loader")
            start_time = datetime.now()
            
            if not self.hf_repo_id:
                raise RuntimeError("SUMMARIZATION_HF_REPO_ID or settings.summarization_hf_repo_id must be set for hub loading")
            logger.info(f"📦 Loading summarization model from Hugging Face Hub: {self.hf_repo_id} (ignoring local path {self.model_path})")
            self.tokenizer = AutoTokenizer.from_pretrained(self.hf_repo_id, local_files_only=False)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.hf_repo_id, local_files_only=False)
            
            self.model.to(self.device)
            
            # Create pipeline
            self.pipeline = pipeline(
                "summarization", 
                model=self.model, 
                tokenizer=self.tokenizer, 
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.loaded = True
            self.load_time = datetime.now()
            load_duration = (self.load_time - start_time).total_seconds()
            
            logger.info(f"✅ Summarization model loaded from Hugging Face Hub ({self.hf_repo_id}) in {load_duration:.2f}s on {self.device}")
            return True
            
        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"❌ Failed to load summarization model: {e}")
            return False

    def summarize(self, text: str, max_length: int = 150, min_length: int = 40) -> str:
        """
        Summarize text with automatic chunking for long inputs
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Generated summary
        """
        if not self.loaded or self.pipeline is None:
            raise RuntimeError("Summarization model not loaded")

        if not text or not text.strip():
            return ""

        text = text.strip()
        
        try:
            # Check if text needs chunking
            token_count = len(self.tokenizer.encode(text, add_special_tokens=True))
            
            if token_count <= self.max_length - 50:  # Leave buffer
                # Single summarization
                return self._summarize_single(text, max_length, min_length)
            else:
                # Hierarchical summarization for long texts
                logger.info(f"🔄 Text too long ({token_count} tokens), using hierarchical summarization")
                return self._summarize_hierarchical(text, max_length, min_length)
                
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise RuntimeError(f"Summarization failed: {str(e)}")
        finally:
            # Clean up GPU memory
            self._cleanup_memory()

    def _summarize_single(self, text: str, max_length: int, min_length: int) -> str:
        """Summarize a single text chunk"""
        try:
            logger.debug(f"📝 Summarizing single text: {text[:100]}...")
            
            summary = self.pipeline(
                text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False,
                truncation=True
            )
            
            result = summary[0]['summary_text'].strip()
            logger.debug(f"✅ Single summary generated: {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Single summarization failed: {e}")
            raise

    def _summarize_hierarchical(self, text: str, max_length: int, min_length: int) -> str:
        """
        Perform hierarchical summarization for long texts:
        1. Split into chunks
        2. Summarize each chunk
        3. Combine chunk summaries
        4. Create final meta-summary
        """
        from ..core.text_chunker import text_chunker
        
        # Get chunks optimized for summarization (larger chunks)
        chunks = text_chunker.chunk_text(text, strategy="summarization")
        logger.info(f"🔄 Processing {len(chunks)} summarization chunks")
        
        # Step 1: Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            try:
                logger.debug(f"Summarizing chunk {i+1}/{len(chunks)} ({chunk.token_count} tokens)")
                
                # Adjust summary length based on chunk size
                chunk_max_length = min(max_length // 2, max(50, chunk.token_count // 4))
                chunk_min_length = min(min_length // 2, 20)
                
                chunk_summary = self._summarize_single(
                    chunk.text, 
                    chunk_max_length, 
                    chunk_min_length
                )
                
                chunk_summaries.append({
                    'summary': chunk_summary,
                    'chunk_id': chunk.chunk_id,
                    'original_length': chunk.token_count
                })
                
                # Clean up between chunks
                if i % 3 == 0:  # Every 3 chunks
                    self._cleanup_memory()
                    
            except Exception as e:
                logger.error(f"Failed to summarize chunk {i+1}: {e}")
                # Create fallback summary for failed chunk
                chunk_summaries.append({
                    'summary': self._create_fallback_summary(chunk.text),
                    'chunk_id': chunk.chunk_id,
                    'original_length': chunk.token_count
                })
        
        # Step 2: Create meta-summary from chunk summaries
        combined_summaries = ' '.join([cs['summary'] for cs in chunk_summaries])
        
        # Check if combined summaries need further summarization
        combined_tokens = len(self.tokenizer.encode(combined_summaries))
        
        if combined_tokens <= self.max_length - 50:
            # Final summarization of combined summaries
            try:
                final_summary = self._summarize_single(
                    combined_summaries, 
                    max_length, 
                    min_length
                )
                logger.info(f"✅ Hierarchical summarization completed: {len(final_summary)} characters")
                return final_summary
            except Exception as e:
                logger.warning(f"Final summarization failed: {e}, returning combined summaries")
                return self._optimize_combined_summaries(chunk_summaries, max_length)
        else:
            # Combined summaries are still too long, apply intelligent merging
            return self._optimize_combined_summaries(chunk_summaries, max_length)

    def _create_fallback_summary(self, text: str, max_sentences: int = 2) -> str:
        """Create a simple extractive summary as fallback"""
        sentences = text.split('. ')
        if len(sentences) <= max_sentences:
            return text
        
        # Take first and last sentences as a simple summary
        if len(sentences) >= 2:
            return f"{sentences[0]}. {sentences[-1]}"
        else:
            return sentences[0][:200] + "..." if len(sentences[0]) > 200 else sentences[0]

    def _optimize_combined_summaries(self, chunk_summaries: List[Dict], max_length: int) -> str:
        """Intelligently combine and optimize chunk summaries"""
        # Sort by importance (longer original chunks often more important)
        sorted_summaries = sorted(
            chunk_summaries, 
            key=lambda x: x['original_length'], 
            reverse=True
        )
        
        combined_text = ""
        total_length = 0
        
        for cs in sorted_summaries:
            summary_text = cs['summary']
            if total_length + len(summary_text) <= max_length * 4:  # Rough character estimate
                if combined_text:
                    combined_text += " " + summary_text
                else:
                    combined_text = summary_text
                total_length += len(summary_text)
            else:
                break
        
        # Ensure we don't exceed reasonable length
        if len(combined_text) > max_length * 6:  # Very rough estimate
            words = combined_text.split()
            combined_text = ' '.join(words[:max_length * 2])  # Conservative cut-off
        
        return combined_text.strip()

    def _cleanup_memory(self):
        """Clean up GPU memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def summarize_with_fallback(self, text: str, max_length: int = 150, 
                               min_length: int = 40, max_retries: int = 2) -> Optional[str]:
        """
        Summarize with fallback strategies for robust processing
        
        Args:
            text: Input text
            max_length: Maximum summary length
            min_length: Minimum summary length
            max_retries: Maximum number of retry attempts
            
        Returns:
            Summary text or fallback summary if all attempts fail
        """
        if not text or not text.strip():
            return ""
            
        for attempt in range(max_retries + 1):
            try:
                return self.summarize(text, max_length, min_length)
            except Exception as e:
                logger.warning(f"Summarization attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries:
                    logger.error(f"All summarization attempts failed for text length {len(text)}")
                    # Return extractive fallback
                    return self._create_fallback_summary(text, max_sentences=3)
                
                # Clean up before retry
                self._cleanup_memory()
        
        return self._create_fallback_summary(text, max_sentences=3)

    def estimate_summarization_time(self, text: str) -> float:
        """Estimate summarization time in seconds"""
        if not text:
            return 0.0
            
        from ..core.text_chunker import text_chunker
        
        token_count = len(self.tokenizer.encode(text)) if self.tokenizer else len(text) // 4
        
        if token_count <= self.max_length:
            return 3.0  # Single chunk
        else:
            chunks = text_chunker.chunk_text(text, strategy="summarization")
            # Hierarchical summarization takes longer due to multiple passes
            return text_chunker.estimate_processing_time(chunks, "summarization") * 1.5

    def get_summarization_strategy_info(self, text: str) -> Dict:
        """Get information about the summarization strategy that would be used"""
        if not text:
            return {"strategy": "none", "reason": "empty_text"}
        
        token_count = len(self.tokenizer.encode(text)) if self.tokenizer else len(text) // 4
        
        if token_count <= self.max_length - 50:
            return {
                "strategy": "single_pass",
                "token_count": token_count,
                "max_tokens": self.max_length,
                "estimated_time": 3.0
            }
        else:
            from ..core.text_chunker import text_chunker
            chunks = text_chunker.chunk_text(text, strategy="summarization")
            return {
                "strategy": "hierarchical",
                "token_count": token_count,
                "max_tokens": self.max_length,
                "chunk_count": len(chunks),
                "estimated_time": len(chunks) * 3.0 + 5.0  # Processing + meta-summary
            }

    def get_model_info(self) -> Dict:
        return {
            "model_path": self.model_path,
            "device": str(self.device),
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "error": self.error,
            "task": "text-summarization",
            "framework": "transformers",
            "max_length": self.max_length,
            "chunking_supported": True,
            "summarization_strategies": ["single_pass", "hierarchical"],
            "fallback_strategy": "extractive_summary"
        }

# Global instance
summarization_model = SummarizationModel()