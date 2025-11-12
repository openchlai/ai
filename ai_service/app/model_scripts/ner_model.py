import spacy
import logging
import os
from typing import Dict, List, Union, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Optional Hugging Face imports
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    from huggingface_hub import snapshot_download
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.info("Transformers not available - Hugging Face NER models disabled")

class NERModel:
    """Named Entity Recognition using spaCy or Hugging Face models"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("ner")
        self.fallback_model_name = "en_core_web_lg"
        self.hf_model_name = "spacy/en_core_web_lg"
        
        # Initialize missing attributes that were causing the error
        self.hf_repo_id = settings.hf_ner_model
        self.hf_token = settings.hf_token
        self.use_hf = False
        
        self.nlp = None
        self.hf_pipeline = None
        self.model_type = None
        self.loaded = False
        self.load_time = None
        self.error = None
    
    def download_spacy_from_hf(self) -> bool:
        """Download spaCy model from Hugging Face"""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers not available - cannot download from Hugging Face")
            return False
            
        local_model_dir = os.path.join(self.model_path, "en_core_web_lg-hf")
        
        try:
            logger.info(f"Downloading spaCy model {self.hf_model_name} from Hugging Face to {local_model_dir}")
            os.makedirs(self.model_path, exist_ok=True)
            
            # Get HF authentication kwargs
            from ..config.settings import settings
            hf_kwargs = settings.get_hf_model_kwargs()
            
            snapshot_download(
                repo_id=self.hf_model_name,
                local_dir=local_model_dir,
                local_dir_use_symlinks=False,
                **hf_kwargs
            )
            
            with open(os.path.join(local_model_dir, "download_info.txt"), "w") as f:
                f.write(f"model_name: {self.hf_model_name}\n")
                f.write(f"downloaded_at: {datetime.now().isoformat()}\n")
                f.write(f"source: huggingface\n")
            
            logger.info(f"Downloaded spaCy model from Hugging Face: {self.hf_model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download spaCy model from Hugging Face: {e}")
            return False
        
    def load(self) -> bool:
        """Load NER model - NO AUTHENTICATION for public models"""
        try:
            start_time = datetime.now()
            
            # Prefer HF hub if configured and repo_id is set
            if self.hf_repo_id and TRANSFORMERS_AVAILABLE:
                logger.info(f"Loading NER model from Hugging Face Hub (public): {self.hf_repo_id}")
                try:
                    # Get HF authentication kwargs
                    from ..config.settings import settings
                    hf_kwargs = settings.get_hf_model_kwargs()
                    
                    self.hf_pipeline = pipeline(
                        "token-classification",
                        model=AutoModelForTokenClassification.from_pretrained(self.hf_repo_id, **hf_kwargs),
                        tokenizer=AutoTokenizer.from_pretrained(self.hf_repo_id, **hf_kwargs),
                        aggregation_strategy="simple"
                    )
                    self.use_hf = True
                    self.loaded = True
                    self.error = None
                    self.load_time = datetime.now()
                    load_duration = (self.load_time - start_time).total_seconds()
                    logger.info(f"NER model loaded from Hugging Face Hub ({self.hf_repo_id}) in {load_duration:.2f}s")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to load from HF Hub: {e}, falling back to spaCy")

            # Fall back to spaCy
            logger.info(f"Loading spaCy model from path: {self.model_path}")
            
            # Try loading from Hugging Face downloaded model first
            hf_model_path = os.path.join(self.model_path, "en_core_web_lg-hf")
            if os.path.exists(hf_model_path):
                logger.info(f"Loading spaCy model downloaded from Hugging Face: {hf_model_path}")
                self.nlp = spacy.load(hf_model_path)
                self.model_type = "spacy_from_hf"
                logger.info("Loaded Hugging Face downloaded spaCy model successfully")
            else:
                # Try loading from local path
                local_model_path = os.path.join(self.model_path, "en_core_web_lg-3.8.0")
                
                if os.path.exists(local_model_path):
                    logger.info(f"Loading local spaCy model from {local_model_path}")
                    self.nlp = spacy.load(local_model_path)
                    self.model_type = "spacy_local"
                    logger.info("Loaded local spaCy model successfully")
                else:
                    # Try to download from Hugging Face
                    if TRANSFORMERS_AVAILABLE:
                        logger.info(f"No local model found. Downloading from Hugging Face: {self.hf_model_name}")
                        if self.download_spacy_from_hf():
                            logger.info(f"Loading newly downloaded spaCy model from {hf_model_path}")
                            self.nlp = spacy.load(hf_model_path)
                            self.model_type = "spacy_from_hf"
                            logger.info("Loaded newly downloaded Hugging Face spaCy model successfully")
                        else:
                            return self._load_fallback()
                    else:
                        return self._load_fallback()
            
            # Test the model
            test_doc = self.nlp("Test loading with Barack Obama in Washington.")
            if len(test_doc.ents) == 0:
                logger.warning("Model loaded but no entities detected in test")
            else:
                logger.info(f"Model test successful - detected {len(test_doc.ents)} entities")
            
            self.loaded = True
            self.load_time = datetime.now()
            load_duration = (self.load_time - start_time).total_seconds()
            
            logger.info(f"spaCy NER model loaded successfully in {load_duration:.2f}s")
            return True
            
        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"Failed to load spaCy model: {e}")
            return False
    
    def _load_fallback(self) -> bool:
        """Load installed spaCy model as fallback"""
        logger.info(f"Using installed spaCy model fallback: {self.fallback_model_name}")
        try:
            self.nlp = spacy.load(self.fallback_model_name)
            self.model_type = "spacy_fallback"
            logger.info("Loaded installed spaCy model successfully")
            return True
        except OSError as e:
            logger.error(f"Neither local nor installed spaCy model found. Install with: python -m spacy download en_core_web_lg")
            raise OSError(f"spaCy model not found. Error: {e}")
    
    def extract_entities(self, text: str, flat: bool = True) -> Union[Dict[str, List[str]], List[Dict[str, str]]]:
        """Extract named entities from text"""
        if not self.loaded:
            raise RuntimeError("NER model not loaded. Call load() first.")
        
        if not text or not text.strip():
            return [] if flat else {}
        
        try:
            if self.use_hf and self.hf_pipeline is not None:
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
            
            # spaCy path
            if self.nlp is None:
                raise RuntimeError("spaCy model not initialized")
            
            doc = self.nlp(text.strip())
            
            if flat:
                entities = []
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": getattr(ent, 'confidence', 1.0)
                    })
                return entities
            else:
                entity_dict = {}
                for ent in doc.ents:
                    if ent.label_ not in entity_dict:
                        entity_dict[ent.label_] = []
                    entity_dict[ent.label_].append(ent.text)
                return entity_dict
                
        except Exception as e:
            logger.error(f"NER processing failed: {e}")
            raise RuntimeError(f"NER processing failed: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """Get standardized model information"""
        
        # Basic information
        info = {
            "model_type": "ner",
            "model_path": self.model_path,
            "hf_repo_id": self.hf_repo_id,
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "device": "cpu",  # spaCy models typically run on CPU
            "error": self.error,
        }

        # Detailed model-specific information
        details = {
            "fallback_model_name": self.fallback_model_name,
            "hf_model_name": self.hf_model_name,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "use_hf_pipeline": self.use_hf,
            "model_backend": self.model_type,
        }

        if self.loaded:
            if self.nlp:
                details.update({
                    "spacy_version": spacy.__version__,
                    "model_version": self.nlp.meta.get("version", "unknown"),
                    "language": self.nlp.meta.get("lang", "unknown"),
                    "pipeline_components": list(self.nlp.pipe_names),
                    "entity_labels": list(self.nlp.get_pipe("ner").labels) if "ner" in self.nlp.pipe_names else []
                })
            elif self.hf_pipeline:
                details.update({
                    "hf_pipeline_task": self.hf_pipeline.task,
                    "hf_model_name_or_path": self.hf_pipeline.model.name_or_path,
                    "hf_tokenizer_name_or_path": self.hf_pipeline.tokenizer.name_or_path,
                })
        
        info["details"] = details
        return info
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.loaded and (self.nlp is not None or self.hf_pipeline is not None) and self.error is None

# Global NER model instance
ner_model = NERModel()