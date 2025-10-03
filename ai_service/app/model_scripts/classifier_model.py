# app/models/classifier_model.py (Fixed)
import logging
from typing import Dict, List, Optional
from datetime import datetime
import torch
import re
import json
import os
from transformers import AutoTokenizer
from transformers import DistilBertPreTrainedModel, DistilBertModel
import torch.nn as nn
import gc
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class MultiTaskDistilBert(DistilBertPreTrainedModel):
    """Custom DistilBERT model for multi-task classification"""
    
    def __init__(self, config, num_main, num_sub, num_interv, num_priority):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.pre_classifier = nn.Linear(config.dim, config.dim)
        self.classifier_main = nn.Linear(config.dim, num_main)
        self.classifier_sub = nn.Linear(config.dim, num_sub)
        self.classifier_interv = nn.Linear(config.dim, num_interv)
        self.classifier_priority = nn.Linear(config.dim, num_priority)
        self.dropout = nn.Dropout(config.dropout)
        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None):
        distilbert_output = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        hidden_state = distilbert_output.last_hidden_state 
        pooled_output = hidden_state[:, 0]                 
        pooled_output = self.pre_classifier(pooled_output) 
        pooled_output = nn.ReLU()(pooled_output)           
        pooled_output = self.dropout(pooled_output)        
        
        logits_main = self.classifier_main(pooled_output)
        logits_sub = self.classifier_sub(pooled_output)
        logits_interv = self.classifier_interv(pooled_output)
        logits_priority = self.classifier_priority(pooled_output)
        
        return (logits_main, logits_sub, logits_interv, logits_priority)

class ClassifierModel:
    """Multi-task classifier with intelligent chunking support"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.model_path = model_path or settings.get_model_path("classifier")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.loaded = False
        self.load_time = None
        self.error = None
        self.max_length = 256  # Model's maximum token limit
        
        # Hugging Face repo configuration (hub-first, no local model loading)
        from ..config.settings import settings as _settings
        self.hf_repo_id = os.getenv("CLASSIFIER_HF_REPO_ID") or getattr(_settings, "classifier_hf_repo_id", None)
        # Token can be provided via env or settings.hf_token
        self.hf_token = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN") or 
                         getattr(_settings, "hf_token", None))
        
        # Category configs - will be loaded in load() method
        self.category_info = {}
        self.main_categories = []
        self.sub_categories = []
        self.interventions = []
        self.priorities = []

    def _load_category_configs(self):
        """Load classifier configuration files"""
        try:
            config_files = {
                "main_categories": "main_categories.json",
                "sub_categories": "sub_categories.json", 
                "interventions": "interventions.json",
                "priorities": "priorities.json"
            }
            
            configs = {}
            for config_name, filename in config_files.items():
                config_file_path = os.path.join(self.model_path, filename)
                if os.path.exists(config_file_path):
                    with open(config_file_path) as f:
                        configs[config_name] = json.load(f)
                else:
                    # Attempt to fetch from Hugging Face repo if configured
                    if not self.hf_repo_id:
                        raise FileNotFoundError(f"Config file not found: {config_file_path}")
                    try:
                        from huggingface_hub import hf_hub_download
                        download_path = hf_hub_download(
                            repo_id=self.hf_repo_id,
                            filename=filename,
                            token=self.hf_token,
                        )
                        with open(download_path) as f:
                            configs[config_name] = json.load(f)
                    except Exception as hf_err:
                        raise FileNotFoundError(f"Failed to fetch {filename} from HF repo {self.hf_repo_id}: {hf_err}")
            
            # Set the category lists
            self.main_categories = configs["main_categories"]
            self.sub_categories = configs["sub_categories"]
            self.interventions = configs["interventions"]
            self.priorities = configs["priorities"]
            
            self.category_info = {
                "main_categories": self.main_categories,
                "sub_categories": self.sub_categories,
                "interventions": self.interventions,
                "priorities": self.priorities
            }
            
            logger.info(f"✅ Loaded classifier configs: {len(self.main_categories)} main categories, {len(self.sub_categories)} sub categories")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load classifier configs: {e}")
            self.error = f"Config loading failed: {str(e)}"
            return False

    def load(self) -> bool:
        """Load model and tokenizer"""
        try:
            logger.info(f"📦 Initializing classifier model loader")
            start_time = datetime.now()
            
            # First load the category configs
            if not self._load_category_configs():
                return False
            
            # Hub-first: require HF repo id and download using auth token
            if not self.hf_repo_id:
                raise RuntimeError("CLASSIFIER_HF_REPO_ID or settings.classifier_hf_repo_id must be set for hub loading")
            logger.info(f"📦 Loading classifier model from Hugging Face Hub: {self.hf_repo_id} (ignoring local path {self.model_path})")
            if self.hf_token:
                logger.info("🔐 Using HF token for authenticated access")
            token_kwargs = {}
            if self.hf_token:
                token_kwargs = {"use_auth_token": self.hf_token}
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.hf_repo_id,
                local_files_only=False,
                **token_kwargs
            )
            
            self.model = MultiTaskDistilBert.from_pretrained(
                self.hf_repo_id,
                num_main=len(self.main_categories),
                num_sub=len(self.sub_categories),
                num_interv=len(self.interventions),
                num_priority=len(self.priorities),
                local_files_only=False,
                **token_kwargs
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            self.load_time = datetime.now()
            load_duration = (self.load_time - start_time).total_seconds()
            logger.info(f"✅ Classifier model loaded from Hugging Face Hub ({self.hf_repo_id}) in {load_duration:.2f}s on {self.device}")
            return True
            
        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"❌ Failed to load classifier model: {e}")
            return False

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        text = text.lower().strip()
        return re.sub(r'[^a-z0-9\s]', '', text)
    
    def classify(self, narrative: str) -> Dict[str, str]:
        """
        Classify case narrative with automatic chunking for long inputs
        
        Args:
            narrative: Input case description
            
        Returns:
            Dict: Classification results with confidence scores
        """
        if not self.loaded or not self.tokenizer or not self.model:
            raise RuntimeError("Classifier model not loaded. Call load() first.")
        
        if not narrative or not narrative.strip():
            return self._get_default_classification()
        
        narrative = narrative.strip()
        
        try:
            # Check if text needs chunking
            clean_text = self.preprocess_text(narrative)
            token_count = len(self.tokenizer.encode(clean_text, add_special_tokens=True))
            
            if token_count <= self.max_length - 10:  # Leave buffer
                # Single classification
                return self._classify_single(clean_text)
            else:
                # Chunked classification with aggregation
                logger.info(f"🔄 Text too long ({token_count} tokens), using chunked classification")
                return self._classify_chunked(clean_text)
                
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise RuntimeError(f"Classification failed: {str(e)}")
        finally:
            # Clean up GPU memory
            self._cleanup_memory()

    def _classify_single(self, text: str) -> Dict[str, str]:
        """Classify a single text chunk"""
        try:
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=self.max_length,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                logits = self.model(**inputs)
                logits_main, logits_sub, logits_interv, logits_priority = logits
            
            # Get predictions
            preds_main = torch.argmax(logits_main, dim=1).item()
            preds_sub = torch.argmax(logits_sub, dim=1).item()
            preds_interv = torch.argmax(logits_interv, dim=1).item()
            preds_priority = torch.argmax(logits_priority, dim=1).item()
            
            # Calculate confidence scores
            main_conf = torch.softmax(logits_main, dim=1).max().item()
            sub_conf = torch.softmax(logits_sub, dim=1).max().item()
            interv_conf = torch.softmax(logits_interv, dim=1).max().item()
            priority_conf = torch.softmax(logits_priority, dim=1).max().item()
            
            return {
                "main_category": self.main_categories[preds_main],
                "sub_category": self.sub_categories[preds_sub],
                "intervention": self.interventions[preds_interv],
                "priority": str(self.priorities[preds_priority]),
                "confidence": round((main_conf + sub_conf + interv_conf + priority_conf) / 4, 3),
                "confidence_breakdown": {
                    "main_category": round(main_conf, 3),
                    "sub_category": round(sub_conf, 3),
                    "intervention": round(interv_conf, 3),
                    "priority": round(priority_conf, 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Single classification failed: {e}")
            raise

    def _classify_chunked(self, text: str) -> Dict[str, str]:
        """Classify text using intelligent chunking and result aggregation"""
        from ..core.text_chunker import text_chunker
        
        # Get chunks optimized for classification
        chunks = text_chunker.chunk_text(text, strategy="classification")
        logger.info(f"🔄 Processing {len(chunks)} classification chunks")
        
        chunk_results = []
        
        for i, chunk in enumerate(chunks):
            try:
                logger.debug(f"Classifying chunk {i+1}/{len(chunks)} ({chunk.token_count} tokens)")
                
                # Classify individual chunk
                chunk_result = self._classify_single(chunk.text)
                chunk_results.append(chunk_result)
                
                # Clean up between chunks
                if i % 5 == 0:  # Every 5 chunks
                    self._cleanup_memory()
                    
            except Exception as e:
                logger.error(f"Failed to classify chunk {i+1}: {e}")
                # Use default classification for failed chunk
                chunk_results.append(self._get_default_classification())
        
        # Aggregate results from all chunks
        aggregated_result = self._aggregate_classification_results(chunk_results, chunks)
        logger.info(f"✅ Chunked classification completed with {len(chunk_results)} chunks")
        
        return aggregated_result

    def _aggregate_classification_results(self, chunk_results: List[Dict], chunks) -> Dict[str, str]:
        """Aggregate classification results from multiple chunks"""
        if not chunk_results:
            return self._get_default_classification()
        
        if len(chunk_results) == 1:
            return chunk_results[0]
        
        # Collect all predictions with weights based on chunk size and confidence
        main_votes = Counter()
        sub_votes = Counter()
        interv_votes = Counter()
        priority_votes = Counter()
        
        total_weight = 0
        confidence_scores = []
        
        for i, result in enumerate(chunk_results):
            # Weight by chunk size and confidence
            chunk_weight = chunks[i].token_count * result.get("confidence", 0.5)
            total_weight += chunk_weight
            
            main_votes[result["main_category"]] += chunk_weight
            sub_votes[result["sub_category"]] += chunk_weight
            interv_votes[result["intervention"]] += chunk_weight
            priority_votes[result["priority"]] += chunk_weight
            
            confidence_scores.append(result.get("confidence", 0.5))
        
        # Get most common predictions
        final_main = main_votes.most_common(1)[0][0]
        final_sub = sub_votes.most_common(1)[0][0]
        final_interv = interv_votes.most_common(1)[0][0]
        final_priority = priority_votes.most_common(1)[0][0]
        
        # Calculate aggregated confidence
        final_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Apply business logic for priority escalation
        final_priority = self._apply_priority_escalation(chunk_results, final_priority)
        
        return {
            "main_category": final_main,
            "sub_category": final_sub,
            "intervention": final_interv,
            "priority": final_priority,
            "confidence": round(final_confidence, 3),
            "aggregation_info": {
                "chunks_processed": len(chunk_results),
                "aggregation_method": "weighted_voting",
                "total_weight": round(total_weight, 2)
            }
        }

    def _apply_priority_escalation(self, chunk_results: List[Dict], default_priority: str) -> str:
        """Apply priority escalation logic for critical cases"""
        # If any chunk indicates high priority, escalate
        priorities_seen = [result.get("priority", "medium") for result in chunk_results]
        
        if "high" in priorities_seen:
            return "high"
        elif "urgent" in priorities_seen:
            return "urgent"
        else:
            return default_priority

    def _get_default_classification(self) -> Dict[str, str]:
        """Return default classification for edge cases"""
        return {
            "main_category": "general_inquiry",
            "sub_category": "assessment_needed",
            "intervention": "initial_assessment",
            "priority": "medium",
            "confidence": 0.0
        }

    def _cleanup_memory(self):
        """Clean up GPU memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def classify_with_fallback(self, narrative: str, max_retries: int = 2) -> Optional[Dict[str, str]]:
        """
        Classify with fallback strategies for robust processing
        
        Args:
            narrative: Input case description
            max_retries: Maximum number of retry attempts
            
        Returns:
            Classification result or default if all attempts fail
        """
        if not narrative or not narrative.strip():
            return self._get_default_classification()
            
        for attempt in range(max_retries + 1):
            try:
                return self.classify(narrative)
            except Exception as e:
                logger.warning(f"Classification attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries:
                    logger.error(f"All classification attempts failed for text length {len(narrative)}")
                    return self._get_default_classification()
                
                # Clean up before retry
                self._cleanup_memory()
        
        return self._get_default_classification()

    def estimate_classification_time(self, text: str) -> float:
        """Estimate classification time in seconds"""
        if not text:
            return 0.0
            
        from ..core.text_chunker import text_chunker
        
        token_count = len(self.tokenizer.encode(text)) if self.tokenizer else len(text) // 4
        
        if token_count <= self.max_length:
            return 0.5  # Single chunk
        else:
            chunks = text_chunker.chunk_text(text, strategy="classification")
            return text_chunker.estimate_processing_time(chunks, "classification")

    def get_model_info(self) -> Dict:
        info = {
            "model_path": self.model_path,
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "device": str(self.device),
            "error": self.error,
            "max_length": self.max_length,
            "chunking_supported": True,
            "aggregation_strategy": "weighted_voting",
            "priority_escalation": True,
            "num_categories": {
                "main": len(self.main_categories),
                "sub": len(self.sub_categories),
                "intervention": len(self.interventions),
                "priority": len(self.priorities)
            }
        }
        
        if self.loaded and self.model:
            info.update({
                "model_type": type(self.model).__name__,
                "tokenizer": type(self.tokenizer).__name__
            })
        
        return info
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.loaded and self.tokenizer is not None and self.model is not None

# Global classifier model instance
classifier_model = ClassifierModel()