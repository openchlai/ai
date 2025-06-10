from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import gc
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def cleanup_gpu_memory():
    """Comprehensive GPU memory cleanup for translation models."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        gc.collect()
        logger.info("GPU memory cleanup completed for translator")

def get_gpu_memory_usage():
    """Get current GPU memory usage."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        cached = torch.cuda.memory_reserved() / 1024**3
        return allocated, cached
    return 0, 0

@contextmanager
def gpu_memory_manager():
    """Context manager for GPU memory management during translation."""
    try:
        if torch.cuda.is_available():
            allocated_before, cached_before = get_gpu_memory_usage()
            logger.info(f"Translation GPU memory before: {allocated_before:.2f}GB allocated, {cached_before:.2f}GB cached")
        
        yield
        
    finally:
        cleanup_gpu_memory()
        
        if torch.cuda.is_available():
            allocated_after, cached_after = get_gpu_memory_usage()
            logger.info(f"Translation GPU memory after cleanup: {allocated_after:.2f}GB allocated, {cached_after:.2f}GB cached")

def translate(text, target_lang="eng_Latn"):
    """Translate text using the NLLB-200 1.3B model with GPU if available, otherwise CPU."""
    logger.info(f"Starting translation to {target_lang}")

    # Detect device: prefer GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # Use memory management context
    with gpu_memory_manager():
        tokenizer = None
        model = None
        
        try:
            # Load tokenizer and model
            logger.info("Loading NLLB-200-1.3B tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B")
            tokenizer.src_lang = "eng_Latn"  # Adjust if your input is not English
            
            logger.info("Loading NLLB-200-1.3B model...")
            model = AutoModelForSeq2SeqLM.from_pretrained(
                "facebook/nllb-200-1.3B",
                torch_dtype=torch.float16 if device.type == "cuda" else torch.float32
            ).to(device)

            # Tokenize input and move tensors to device
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=1024
            ).to(device)

            # Translate
            with torch.no_grad():  # Ensure no gradients are tracked
                translated = model.generate(
                    **inputs,
                    forced_bos_token_id=tokenizer.convert_tokens_to_ids(target_lang),
                    max_length=1024,
                    num_beams=4
                )

            # Decode and return
            result = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
            
            # Clean up intermediate tensors
            del inputs, translated
            
            logger.info("Translation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise RuntimeError(f"Translation failed: {str(e)}")
            
        finally:
            # CRITICAL: Always clean up model and tokenizer
            if model is not None:
                logger.info("Cleaning up translation model...")
                # Move model to CPU first to free GPU memory
                model.cpu()
                del model
                
            if tokenizer is not None:
                del tokenizer
            
            # Force GPU cleanup
            cleanup_gpu_memory()
            logger.info("Translation model cleanup completed")

def force_cleanup():
    """Force cleanup of all translation GPU resources."""
    cleanup_gpu_memory()
    logger.info("Forced translation cleanup completed")

# Alternative implementation with class-based approach for better control
class NLLBTranslator:
    """Class-based translator with explicit lifecycle management."""
    
    def __init__(self, model_name="facebook/nllb-200-1.3B"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        
    def _load_model(self):
        """Load the translation model."""
        if self.model is None:
            logger.info(f"Loading {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.tokenizer.src_lang = "eng_Latn"
            
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            ).to(self.device)
            
            logger.info("Translation model loaded successfully")
    
    def _unload_model(self):
        """Unload the translation model and free memory."""
        if self.model is not None:
            logger.info("Unloading translation model...")
            self.model.cpu()
            del self.model
            self.model = None
            
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
            
        cleanup_gpu_memory()
        logger.info("Translation model unloaded")
    
    def translate(self, text, target_lang="eng_Latn"):
        """Translate text with automatic model management."""
        with gpu_memory_manager():
            try:
                self._load_model()
                
                # Tokenize input
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=1024
                ).to(self.device)

                # Translate
                with torch.no_grad():
                    translated = self.model.generate(
                        **inputs,
                        forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(target_lang),
                        max_length=1024,
                        num_beams=4
                    )

                # Decode result
                result = self.tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
                
                # Clean up intermediate tensors
                del inputs, translated
                
                return result
                
            finally:
                # Always unload model after use
                self._unload_model()
    
    def __del__(self):
        """Ensure cleanup on deletion."""
        self._unload_model()

# Function that uses the class-based approach (recommended)
def translate_with_cleanup(text, target_lang="eng_Latn"):
    """Translation function that guarantees cleanup."""
    translator = NLLBTranslator()
    try:
        return translator.translate(text, target_lang)
    finally:
        del translator
        force_cleanup()

# Example usage
if __name__ == "__main__":
    # Test translation
    test_text = "Hello, how are you today?"
    
    try:
        # Method 1: Direct function (with cleanup)
        result1 = translate(test_text)
        print("Direct function result:", result1)
        
        # Method 2: Class-based approach (recommended)
        result2 = translate_with_cleanup(test_text)
        print("Class-based result:", result2)
        
    except Exception as e:
        logger.error(f"Translation test failed: {str(e)}")