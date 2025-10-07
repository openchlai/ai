import logging
import os
import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertModel
from typing import Dict, List, Optional
from datetime import datetime
import gc
import numpy as np

logger = logging.getLogger(__name__)

# --- Model Configuration ---
QA_HEADS_CONFIG = {
    "opening": 1,
    "listening": 5,
    "proactiveness": 3,
    "resolution": 5,
    "hold": 2,
    "closing": 1
}

HEAD_SUBMETRIC_LABELS = {
    "opening": ["Use of call opening phrase"],
    "listening": [
        "Caller was not interrupted", "Empathizes with the caller",
        "Paraphrases or rephrases the issue", "Uses 'please' and 'thank you'",
        "Does not hesitate or sound unsure"
    ],
    "proactiveness": [
        "Willing to solve extra issues", "Confirms satisfaction with action points",
        "Follows up on case updates"
    ],
    "resolution": [
        "Gives accurate information", "Correct language use", "Consults if unsure",
        "Follows correct steps", "Explains solution process clearly"
    ],
    "hold": ["Explains before placing on hold", "Thanks caller for holding"],
    "closing": ["Proper call closing phrase used"]
}

# --- PyTorch Model Definition ---
class MultiHeadQAClassifier(nn.Module):
    """Multi-head QA classifier model for call center transcript evaluation."""
    
    def __init__(self, model_name="distilbert-base-uncased", heads_config=QA_HEADS_CONFIG, dropout=0.2, hf_token: Optional[str] = None):
        super().__init__()
        token_kwargs = {"token": hf_token.strip()} if isinstance(hf_token, str) and hf_token.strip() else {}
        self.bert = DistilBertModel.from_pretrained(model_name, **token_kwargs)
        hidden_size = self.bert.config.hidden_size
        self.dropout = nn.Dropout(dropout)
        self.heads = nn.ModuleDict({
            head: nn.Linear(hidden_size, output_dim)
            for head, output_dim in heads_config.items()
        })

    def forward(self, input_ids, attention_mask):
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = self.dropout(output.last_hidden_state[:, 0])  # [CLS] token
        logits = {
            head_name: torch.sigmoid(head_layer(pooled_output))
            for head_name, head_layer in self.heads.items()
        }
        return {"logits": logits}

# --- Service Class ---
class QAModel:
    """Manages the QA model for inference within the FastAPI application."""

    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("all_qa_distilbert_v1")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.loaded = False
        self.load_time = None
        self.error = None
        self.max_length = 512

    def load(self) -> bool:
        """Load the QA model and tokenizer - NO AUTHENTICATION"""
        try:
            logger.info(f"Loading QA model...")
            start_time = datetime.now()

            # Try HuggingFace Hub first if configured
            model_id = getattr(self.settings, "qa_hf_repo_id", None) or getattr(self.settings, "hf_qa_model", None)
            if model_id:
                logger.info(f"Loading QA model from HuggingFace Hub: {model_id}")
                
                try:
                    # Build optional auth kwargs (token only if provided)
                    hf_token = getattr(self.settings, "hf_token", None)
                    tok_kwargs = {"token": hf_token.strip()} if isinstance(hf_token, str) and hf_token.strip() else {}

                    # Load tokenizer
                    self.tokenizer = DistilBertTokenizer.from_pretrained(model_id, **tok_kwargs)
                    
                    # Load base model with optional token
                    self.model = MultiHeadQAClassifier(model_name=model_id, hf_token=hf_token)
                    
                    # Try to load state dict from HF Hub
                    try:
                        from huggingface_hub import hf_hub_download
                        hub_kwargs = {"token": hf_token.strip()} if isinstance(hf_token, str) and hf_token.strip() else {}
                        model_state_path = hf_hub_download(repo_id=model_id, filename="pytorch_model.bin", **hub_kwargs)
                        state_dict = torch.load(model_state_path, map_location=self.device)
                        self.model.load_state_dict(state_dict)
                    except Exception as state_error:
                        logger.warning(f"Could not load state dict from HF Hub: {state_error}")
                        # Model will use pre-trained DistilBERT weights
                    
                    self.model.to(self.device)
                    self.model.eval()
                    
                    self.loaded = True
                    self.load_time = datetime.now()
                    duration = (self.load_time - start_time).total_seconds()
                    logger.info(f"QA model loaded from HF Hub in {duration:.2f}s on {self.device}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Failed to load HF QA model {model_id}: {e}")
                    logger.info("Falling back to local model loading")

            # Local model loading
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"QA model directory not found at: {self.model_path}")

            # Load tokenizer from local path
            self.tokenizer = DistilBertTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True
            )

            # Load model from local path
            self.model = MultiHeadQAClassifier(model_name=self.model_path)
            
            # Load state dict
            model_state_path = os.path.join(self.model_path, "pytorch_model.bin")
            if not os.path.exists(model_state_path):
                model_state_path = os.path.join(self.model_path, "all_qa_distilbert_v1.bin")
                if not os.path.exists(model_state_path):
                    raise FileNotFoundError(f"Model state file not found in {self.model_path}")
            
            state_dict = torch.load(model_state_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()

            self.loaded = True
            self.load_time = datetime.now()
            duration = (self.load_time - start_time).total_seconds()
            logger.info(f"QA model loaded locally in {duration:.2f}s on {self.device}")
            return True

        except Exception as e:
            self.error = str(e)
            self.load_time = datetime.now()
            logger.error(f"Failed to load QA model: {e}")
            return False

    def score_transcript(self, transcript: str, threshold: float = 0.5) -> Dict:
        """Score a transcript against QA metrics and calculate an overall score."""
        if not self.is_ready():
            raise RuntimeError("QA model is not loaded. Call load() first.")

        if not transcript or not transcript.strip():
            return self._get_default_score()
            
        try:
            # Tokenize input
            encoding = self.tokenizer(
                transcript,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=self.max_length
            )
            input_ids = encoding["input_ids"].to(self.device)
            attention_mask = encoding["attention_mask"].to(self.device)

            # Get model predictions
            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs["logits"]

            # Process results
            detailed_scores = {}
            category_scores = []

            for head, probs in logits.items():
                probs_np = probs.cpu().numpy()[0]
                preds = (probs_np > threshold)
                submetrics = HEAD_SUBMETRIC_LABELS.get(head, [])

                # Calculate score for this category
                category_score = (sum(preds) / len(preds)) * 100 if len(preds) > 0 else 0
                category_scores.append(category_score)

                # Format submetric results
                detailed_scores[head] = {
                    "score_percent": round(category_score, 2),
                    "submetrics": [
                        {
                            "metric": label,
                            "passed": bool(pred),
                            "probability": round(float(prob), 4)
                        } for label, pred, prob in zip(submetrics, preds, probs_np)
                    ]
                }
            
            # Calculate final weighted score
            overall_score = sum(category_scores) / len(category_scores) if category_scores else 0
            
            self._cleanup_memory()

            return {
                "overall_qa_score": round(overall_score, 2),
                "detailed_scores": detailed_scores
            }

        except Exception as e:
            logger.error(f"QA scoring failed: {e}")
            raise RuntimeError(f"QA scoring failed: {str(e)}")

    def format_qa_response(self, raw_results: Dict) -> dict:
        """Convert raw multi-head QA results into structured response."""
        metrics = []

        # Flatten predictions into a single list
        for metric_name, submetrics in raw_results.items():
            for submetric in submetrics:
                metrics.append({
                    "submetric": submetric["submetric"],
                    "prediction": bool(submetric["prediction"]),
                    "score": submetric["score"],
                    "probability": submetric["probability"]
                })

        # Compute overall score (mean of probabilities)
        overall_score_value = float(np.mean([m["probability"] for m in metrics])) if metrics else 0.0

        overall_score = [{
            "submetric": "Overall QA Score",
            "prediction": bool(overall_score_value >= 0.5),
            "score": f"{overall_score_value:.2f}",
            "probability": overall_score_value
        }]

        return {
            "overall_score": overall_score,
            "metrics": metrics
        }

    def predict(self, text: str, threshold: float = 0.5, return_raw: bool = False) -> Dict:
        """Predict QA metrics for a given transcript."""
        if not self.is_ready():
            raise RuntimeError("QA model is not loaded. Call load() first.")
            
        threshold = 0.5 if threshold is None else float(threshold)

        # Tokenize input
        encoding = self.tokenizer(
            text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=self.max_length
        )
        
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)
        
        # Forward pass
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs["logits"]
        
        # Process results
        results = {}
        for head, probs in logits.items():
            if probs is None:
                # Infer output size dynamically
                num_outputs = len(HEAD_SUBMETRIC_LABELS.get(head, []))
                probs_np = np.zeros(num_outputs)
            else:
                probs_np = np.nan_to_num(probs.cpu().numpy()[0], nan=0.0)

            preds = (probs_np > threshold).astype(int)
            submetrics = HEAD_SUBMETRIC_LABELS.get(head, [f"Submetric {i+1}" for i in range(len(probs_np))])
            
            head_results = []
            for i, (label, prob, pred) in enumerate(zip(submetrics, probs_np, preds)):
                result_item = {
                    "submetric": label,
                    "prediction": bool(pred),
                    "score": "✓" if pred else "✗",
                    "probability": float(prob if prob is not None else 0.0)
                }
                head_results.append(result_item)
            
            results[head] = head_results
        
        return results

    def _get_default_score(self) -> Dict:
        """Return a default score for empty or invalid input."""
        return {"overall_qa_score": 0.0, "detailed_scores": {}}

    def _cleanup_memory(self):
        """Clean up GPU memory after inference."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def get_model_info(self) -> Dict:
        """Return information about the loaded QA model."""
        return {
            "model_path": self.model_path,
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "device": str(self.device),
            "error": self.error,
            "max_length": self.max_length,
            "model_type": type(self.model).__name__ if self.model else None,
            "qa_heads": list(QA_HEADS_CONFIG.keys())
        }
        
    def is_ready(self) -> bool:
        """Check if the model is loaded and ready for inference."""
        return self.loaded and self.model is not None and self.tokenizer is not None


# Global QA model instance
qa_model = QAModel()