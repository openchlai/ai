# core/pipeline/classifier.py

import re
import torch
import numpy as np
<<<<<<< HEAD
import json
import logging
from pathlib import Path
from .model_loader import load_hf_model_and_tokenizer

logger = logging.getLogger(__name__)

# Global classifier state
_classifier_cache = None
_classifier_lock = None

def get_classifier():
    """Get cached classifier instance"""
    global _classifier_cache, _classifier_lock
    
    if _classifier_cache is None:
        import threading
        if _classifier_lock is None:
            _classifier_lock = threading.Lock()
            
        with _classifier_lock:
            if _classifier_cache is None:
                logger.info("🧠 Loading classifier model...")
                _classifier_cache = CaseClassifier()
                logger.info("📦 Classifier cached successfully")
                
    return _classifier_cache

class CaseClassifier:
    def __init__(self):
        """Initialize the case classifier with model and label mappings"""
        try:
            # Load model and tokenizer
            self.model, self.tokenizer, self.device, self.label_maps = load_hf_model_and_tokenizer("multitask_distilbert")
            logger.info(f"✅ Classifier initialized on device: {self.device}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize classifier: {e}")
            # Fallback initialization
            self.model = None
            self.tokenizer = None
            self.device = torch.device("cpu")
            self.label_maps = {
                "main_categories": ["general"],
                "sub_categories": ["unspecified"],
                "interventions": ["basic_support"],
                "priorities": ["medium"]
            }
    
    def classify(self, narrative: str) -> dict:
        """Classify a case narrative"""
        if self.model is None:
            logger.warning("⚠️ Classifier model not loaded, returning default classification")
            return {
                "main_category": "general",
                "sub_category": "unspecified",
                "intervention": "basic_support",
                "priority": "medium"
            }
        
        try:
            return self._classify_with_model(narrative)
        except Exception as e:
            logger.error(f"❌ Classification failed: {e}")
            return {
                "main_category": "general",
                "sub_category": "unspecified", 
                "intervention": "basic_support",
                "priority": "medium"
            }
    
    def _classify_with_model(self, narrative: str) -> dict:
        """Internal method to classify using the loaded model"""
        text = narrative.lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=256,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Handle different model output formats
        if hasattr(outputs, 'logits'):
            logits = outputs.logits
        elif isinstance(outputs, tuple):
            if len(outputs) == 4:
                # Multi-head model with separate outputs for each task
                logits_main, logits_sub, logits_interv, logits_priority = outputs
                return {
                    "main_category": self.label_maps["main_categories"][np.argmax(logits_main.cpu().numpy())],
                    "sub_category": self.label_maps["sub_categories"][np.argmax(logits_sub.cpu().numpy())],
                    "intervention": self.label_maps["interventions"][np.argmax(logits_interv.cpu().numpy())],
                    "priority": self.label_maps["priorities"][np.argmax(logits_priority.cpu().numpy())]
                }
            else:
                # Single output tuple
                logits = outputs[0]
        else:
            # Direct tensor output
            logits = outputs
            
        # Handle single-output model by splitting logits
        try:
            logits_np = logits.cpu().numpy()
            if logits_np.ndim > 1:
                logits_np = logits_np[0]  # Remove batch dimension
            
            # Split logits based on label map sizes
            main_size = len(self.label_maps["main_categories"])
            sub_size = len(self.label_maps["sub_categories"]) 
            interv_size = len(self.label_maps["interventions"])
            priority_size = len(self.label_maps["priorities"])
            
            expected_size = main_size + sub_size + interv_size + priority_size
            if len(logits_np) < expected_size:
                logger.warning(f"⚠️ Logits size {len(logits_np)} < expected {expected_size}, using defaults")
                return {
                    "main_category": self.label_maps["main_categories"][0] if self.label_maps["main_categories"] else "general",
                    "sub_category": self.label_maps["sub_categories"][0] if self.label_maps["sub_categories"] else "unspecified",
                    "intervention": self.label_maps["interventions"][0] if self.label_maps["interventions"] else "basic_support",
                    "priority": self.label_maps["priorities"][0] if self.label_maps["priorities"] else "medium"
                }
            
            # Split the logits into sections
            main_logits = logits_np[:main_size]
            sub_logits = logits_np[main_size:main_size + sub_size]
            interv_logits = logits_np[main_size + sub_size:main_size + sub_size + interv_size]
            priority_logits = logits_np[main_size + sub_size + interv_size:main_size + sub_size + interv_size + priority_size]
            
            # Safe argmax with fallback
            def safe_argmax(arr, labels, default_idx=0):
                if len(arr) == 0 or len(labels) == 0:
                    return labels[0] if labels else "unknown"
                try:
                    idx = np.argmax(arr)
                    return labels[idx] if idx < len(labels) else labels[0]
                except (IndexError, ValueError):
                    return labels[0]
            
            return {
                "main_category": safe_argmax(main_logits, self.label_maps["main_categories"]),
                "sub_category": safe_argmax(sub_logits, self.label_maps["sub_categories"]),
                "intervention": safe_argmax(interv_logits, self.label_maps["interventions"]),
                "priority": safe_argmax(priority_logits, self.label_maps["priorities"])
            }
        except Exception as e:
            logger.error(f"❌ Error processing classification logits: {e}")
            return {
                "main_category": "general",
                "sub_category": "unspecified",
                "intervention": "basic_support",
                "priority": "medium"
            }

# Public interface functions
def classify_case(narrative: str) -> dict:
    """Classify a case narrative using the cached classifier"""
    classifier = get_classifier()
    return classifier.classify(narrative)

# Legacy function for backwards compatibility
def classify_case_with_params(narrative, model, tokenizer, device, label_maps):
    """Legacy function that takes all parameters directly"""
=======

def classify_case(narrative, model, tokenizer, device, label_maps):
>>>>>>> 94764d3335752e5b86366a5dff43db0766aa9299
    text = narrative.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)

    inputs = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=256,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        logits_main, logits_sub, logits_interv, logits_priority = model(**inputs)

    return {
        "main_category": label_maps["main_categories"][np.argmax(logits_main.cpu().numpy())],
        "sub_category": label_maps["sub_categories"][np.argmax(logits_sub.cpu().numpy())],
        "intervention": label_maps["interventions"][np.argmax(logits_interv.cpu().numpy())],
        "priority": label_maps["priorities"][np.argmax(logits_priority.cpu().numpy())]
    }
