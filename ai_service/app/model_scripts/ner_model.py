import spacy
import logging
import os
from typing import Dict, List, Union, Optional
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

logger = logging.getLogger(__name__)

class NERModel:
    """Named Entity Recognition using spaCy"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.model_path = model_path or settings.get_model_path("ner")
        self.fallback_model_name = "en_core_web_md"
        self.nlp = None
        self.loaded = False
        self.load_time = None
        self.error = None
        # Hugging Face support
        self.hf_repo_id = getattr(settings, "ner_hf_repo_id", None)
        self.hf_token = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN") or getattr(settings, "hf_token", None))
        self.use_hf = False
        self.hf_pipeline = None
        
    def load(self) -> bool:
        """Load the spaCy NER model"""
        try:
            start_time = datetime.now()
            # Prefer HF hub if configured
            if self.hf_repo_id:
                logger.info(f"📦 Loading NER model from Hugging Face Hub: {self.hf_repo_id} (ignoring local path {self.model_path})")
                if self.hf_token:
                    logger.info("🔐 Using HF token for authenticated access")
                token_kwargs = {"use_auth_token": self.hf_token} if self.hf_token else {}
                self.hf_pipeline = pipeline(
                    "token-classification",
                    model=AutoModelForTokenClassification.from_pretrained(self.hf_repo_id, local_files_only=False, **token_kwargs),
                    tokenizer=AutoTokenizer.from_pretrained(self.hf_repo_id, local_files_only=False, **token_kwargs),
                    aggregation_strategy="simple"
                )
                self.use_hf = True
                self.loaded = True
                self.error = None
                self.load_time = datetime.now()
                load_duration = (self.load_time - start_time).total_seconds()
                logger.info(f"✅ NER model loaded from Hugging Face Hub ({self.hf_repo_id}) in {load_duration:.2f}s")
                return True

            logger.info(f"Loading spaCy model from path: {self.model_path}")
            start_time = datetime.now()
            
            # Try loading from local path first
            local_model_path = os.path.join(self.model_path, "en_core_web_md-3.8.0")
            
            if os.path.exists(local_model_path):
                logger.info(f"📝 Loading local spaCy model from {local_model_path}")
                self.nlp = spacy.load(local_model_path)
                logger.info("✅ Loaded local spaCy model successfully")
            else:
                # Fallback to installed spaCy model
                logger.info(f"🌐 Local model not found at {local_model_path}, using installed spaCy model: {self.fallback_model_name}")
                try:
                    self.nlp = spacy.load(self.fallback_model_name)
                    logger.info("✅ Loaded installed spaCy model successfully")
                except OSError as e:
                    logger.error(f"❌ Neither local nor installed spaCy model found. Install with: python -m spacy download en_core_web_md")
                    raise OSError(f"spaCy model not found. Error: {e}")
            
            # Test the model with a simple example
            test_doc = self.nlp("Test loading with Barack Obama in Washington.")
            if len(test_doc.ents) == 0:
                logger.warning("Model loaded but no entities detected in test")
            else:
                logger.info(f"Model test successful - detected {len(test_doc.ents)} entities")
            
            self.loaded = True
            self.load_time = datetime.now()
            load_duration = (self.load_time - start_time).total_seconds()
            
            logger.info(f"✅ spaCy NER model loaded successfully in {load_duration:.2f}s")
            return True
            
        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"❌ Failed to load spaCy model: {e}")
            return False
    
    def extract_entities(self, text: str, flat: bool = True) -> Union[Dict[str, List[str]], List[Dict[str, str]]]:
        """
        Extract named entities from text
        
        Args:
            text (str): Input text
            flat (bool): If True, return flat list. If False, return grouped by entity type
        
        Returns:
            Union[Dict, List]: Entities in requested format
        """
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
        """Get model information"""
        info = {
            "model_path": self.model_path,
            "fallback_model_name": self.fallback_model_name,
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "error": self.error
        }
        
        if self.loaded and self.nlp:
            info.update({
                "spacy_version": spacy.__version__,
                "model_version": self.nlp.meta.get("version", "unknown"),
                "language": self.nlp.meta.get("lang", "unknown"),
                "pipeline": list(self.nlp.pipe_names),
                "labels": list(self.nlp.get_pipe("ner").labels) if "ner" in self.nlp.pipe_names else []
            })
        
        return info
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.loaded and self.nlp is not None and self.error is None

# Global NER model instance
ner_model = NERModel()