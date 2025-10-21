import logging
import os
from typing import Dict, List, Union, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional Hugging Face imports
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.info("Transformers not available - Hugging Face NER models disabled")

class NERModel:
    """Named Entity Recognition using Hugging Face models only"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("ner")
        self.hf_repo_id = settings.ner_hf_repo_id
        self.hf_token = settings.hf_token
        self.use_hf = False
        
        self.hf_pipeline = None
        self.model_type = None
        self.loaded = False
        self.load_time = None
        self.error = None
    
        
    def load(self) -> bool:
        """Load NER model from Hugging Face Hub only"""
        try:
            start_time = datetime.now()
            
            # Only load from HF hub if configured and repo_id is set
            if self.hf_repo_id and TRANSFORMERS_AVAILABLE:
                logger.info(f"Loading NER model from Hugging Face Hub: {self.hf_repo_id}")
                try:
                    # Load WITHOUT authentication
                    self.hf_pipeline = pipeline(
                        "token-classification",
                        model=AutoModelForTokenClassification.from_pretrained(self.hf_repo_id),
                        tokenizer=AutoTokenizer.from_pretrained(self.hf_repo_id),
                        aggregation_strategy="simple"
                    )
                    self.use_hf = True
                    self.model_type = "huggingface_transformers"
                    self.loaded = True
                    self.error = None
                    self.load_time = datetime.now()
                    load_duration = (self.load_time - start_time).total_seconds()
                    logger.info(f"✅ NER DistilBERT model loaded from Hugging Face Hub ({self.hf_repo_id}) in {load_duration:.2f}s")
                    return True
                except Exception as e:
                    self.error = str(e)
                    logger.error(f"Failed to load from HF Hub: {e}")
                    return False
            else:
                self.error = "No HF repo ID configured or transformers not available"
                logger.error(f"No HF repo ID configured or transformers not available")
                return False
            
        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"Failed to load NER model: {e}")
            return False
    
    
    def extract_entities(self, text: str, flat: bool = True) -> Union[Dict[str, List[str]], List[Dict[str, str]]]:
        """Extract named entities from text using Hugging Face model only"""
        if not self.loaded:
            raise RuntimeError("NER model not loaded. Call load() first.")
        
        if not text or not text.strip():
            return [] if flat else {}
        
        try:
            if not (self.use_hf and self.hf_pipeline is not None):
                raise RuntimeError("Hugging Face model not available")
            
            results = self.hf_pipeline(text.strip()) if text else []
            if flat:
                entities = []
                for r in results:
                    entities.append({
                        "text": r.get("word", ""),
                        "label": r.get("entity_group", r.get("entity", "")),
                        "start": int(r.get("start", 0)),
                        "end": int(r.get("end", 0)),
                        "confidence": float(r.get("score", 1.0))
                    })
                return entities
            else:
                grouped: Dict[str, List[str]] = {}
                for r in results:
                    label = r.get("entity_group", r.get("entity", ""))
                    grouped.setdefault(label, []).append(r.get("word", ""))
                return grouped
                
        except Exception as e:
            logger.error(f"NER processing failed: {e}")
            raise RuntimeError(f"NER processing failed: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        info = {
            "model_path": self.model_path,
            "hf_repo_id": self.hf_repo_id,
            "model_type": self.model_type,
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "error": self.error,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "use_hf": self.use_hf
        }
        
        return info
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.loaded and self.hf_pipeline is not None and self.error is None

# Global NER model instance
ner_model = NERModel()