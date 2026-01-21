# QA Scoring Model Documentation

## 1. Model Overview

The **openchs/qa-helpline-distilbert-v1** model is a DistilBERT-based multi-head classifier fine-tuned for automated **quality assurance (QA) assessment** of helpline and call center transcripts. Developed by BITZ IT Consulting for child helplines and crisis support in East Africa, the model evaluates interactions across 6 core quality dimensions and 17 sub-metrics. Its mission is to provide scalable, objective QA feedback supporting consistent service standards, agent skill-building, and child protection initiatives.

### Key Features

- **Architecture**: Custom DistilBERT multi-head classifier (distilbert-base-uncased)
- **Domain**: Helpline/call center transcripts (child protection, crisis response)
- **Deployment**: Available via Hugging Face and AI Service API
- **Repository**: openchs/qa-helpline-distilbert-v1
- **Capabilities**: Binary predictions for use of call protocols, listening skills, proactiveness, solution clarity, proper hold procedures, and closing practices
- **Performance**: ~87% overall accuracy; exceptionally strong in closure and resolution detection

***

## 2. Integration in AI Service Architecture

### 2.1 Configuration Layer


### 2.1 Configuration Layer

Model and system configuration is handled in `settings.py`:

- Model paths (`models_path`), naming conventions, and GPU resource management are centrally defined via the `Settings` class.
- Use `settings.get_model_path()` to resolve model storage paths. Model-specific subdirs like all_qa_distilbert_v1 are standard.
- Paths are automatically initialized and created at run-time with `settings.initialize_paths()`.
- `enable_model_loading` can be set to disable all model loading globally (useful for debug or non-ML deployments).


```python
class Settings(BaseSettings):
    qa_hf_repo_id: Optional[str] = "openchs/qa-helpline-distilbert-v1"
    hf_qa_model: str = "openchs/qa-helpline-distilbert-v1"
    use_hf_models: bool = True
    models_path: str = "./models"
    ....
```

Helper methods to access model settings, similar to translation model helpers:

```python

def _get_hf_model_id(self, model_name: str) -> str:
        """Get HuggingFace model ID"""
        model_id_map = {
            "whisper_large_v3": self.hf_whisper_large_v3,
            "whisper_large_turbo": self.hf_whisper_large_turbo,
            "classifier": self.hf_classifier_model,
            "ner": self.hf_ner_model,
            "translator": self.hf_translator_model,
            "summarizer": self.hf_summarizer_model,
            "qa": self.hf_qa_model
        }
        
        model_id = model_id_map.get(model_name, "")
        
        if not model_id and self.hf_organization:
            model_id = f"{self.hf_organization}/{model_name.replace('_', '-')}"
        
        return model_id or "openchs/asr-whisper-helpline-sw-v1"
```

***

### 2.2 Model Loading and Management

Centralized model loading and lifecycle is managed by `model_loader.py`:

- The QA model is managed by the global instance `qa_model` (from model_scripts/qa_model.py).
- Model dependencies (PyTorch, transformers, numpy, etc.) are detected at runtime. If any required library is missing, QA loading is gracefully blocked and reported.
- Model is loaded at startup—`qa_model.load()` reads model weights (bin files) and tokenizer (DistilBERT) from the configured path, using device auto-detection for CUDA.
- Loading errors (missing files, init errors) are caught and surfaced via the API info endpoint for diagnostics.

Health endpoints (GET `/qa/info`, `/health/models`) report real-time QA model status, error state, and dependencies.

```python

class QAModel:
    """Manages the QA model for inference within the FastAPI application."""

    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("all_qa_distilbert_v1")
        ...
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
                    ...
```
***

### 2.3 API Endpoints

All QA API endpoints are implemented in `qa_route.py`:

- **POST `/qa/evaluate`**: Main scoring endpoint—accepts structured transcript, optional threshold, and a `return_raw` flag for detailed outputs.
  - Checks for model readiness.
  - Returns predictions and per-metric probability scores in a consistent API structure (fully validated by Pydantic QAResponse model), including details such as processing time and current model info.

- **GET `/qa/info`**: Returns live model status and metadata.

- **POST `/qa/demo`**: Runs a canonical sample transcript through the model for demonstration and debugging.

API response structure (QAResponse):
- `evaluations`: Dict of metric group → list of SubmetricResult objects (prediction, pass/fail, score, [probability]).
- `processing_time`: Seconds elapsed for inference.
- `model_info`: Dump of all key info, including load time, device, model path, and error state.
- `timestamp`: ISO8601 for traceability.

***


### 2.4 Model Logic and Runtime

- Model head configuration (QA_HEADS_CONFIG) is statically defined and covers all necessary QA dimensions.
- **Tokenization and Truncation**: Transcripts are tokenized (DistilBERTTokenizer, max 512 tokens), with truncation if needed. For longer calls, chunking must be performed externally.
- **Per-metric scoring**: Each model head (opening, listening, etc.) produces a set of probabilities and binary predictions against the defined threshold (default 0.5, customizable).
- **Memory management**: After inference, GPU memory cleanup is performed (`torch.cuda.empty_cache()`, `gc.collect()`) to prevent resource leaking in production.
- **Transcript Chunking Strategy**: Model accepts max 512 token input. Longer transcripts are chunked, analyzed, and predictions are aggregated.

Utility class for chunking:

```python
class QAChunker:
    def chunk_transcript(self, text, segment_length=450, overlap=50):
        ...
```

Chunking preserves context, boosts scoring accuracy for long calls, and ensures all sub-metrics are evaluated without truncation.

***

### 2.5 Model Loader System

- The `ModelLoader` in model_loader.py manages system-wide model readiness and dependencies. It checks, loads, and refreshes models, and exposes health, error, and readiness diagnostics to API endpoints.
- Models are only loaded if dependencies are satisfied, and all errors are reported with detailed messages for easier diagnostics.



### 2.6. Pipeline Integration

**Call Flow:**
```
Audio Input → ASR → English Transcript → NER/Classification/Summarization → Analytics → QA Scoring 
```
- QA metrics stored per call for agent feedback, service analytics, and child protection monitoring.

***

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The QA model is deployed as part of the AI Service and accessible via REST API. The API uses an **asynchronous task-based architecture** where QA evaluation requests are queued and processed by Celery workers, allowing the system to handle resource-intensive inference without blocking HTTP connections.

#### Workflow Overview

The QA evaluation API follows a **2-step asynchronous workflow**:

1. **Submit QA Evaluation Request** → Receive `task_id` (HTTP 202 Accepted)
2. **Poll Task Status** → Retrieve QA evaluation results when ready (HTTP 200 OK)

This architecture ensures reliable processing of long transcripts and prevents timeout issues during GPU-intensive QA scoring operations.

---

#### Step 1: Submit QA Evaluation Task

**Endpoint:**
```
POST /qa/evaluate
```

**Request Format:**
```json
{
  "transcript": "Hello, this is 116 sauti child helpline. My name is Jackson Kibwana, how can I help you today?",
  "threshold": 0.6,
  "return_raw": false
}
```

**Success Response (HTTP 202 Accepted):**
```json
{
  "task_id": "task_qa_a1b2c3d4e5f6",
  "status": "queued",
  "message": "QA evaluation task submitted successfully. Check status at /qa/task/{task_id}",
  "status_endpoint": "/qa/task/task_qa_a1b2c3d4e5f6",
  "estimated_time": "1-2 seconds"
}
```

**Response Fields:**
- `task_id` (string): Unique identifier for tracking the QA evaluation task
- `status` (string): Initial task state (`"queued"` or `"processing"`)
- `message` (string): Human-readable confirmation message
- `status_endpoint` (string): URL path for polling task status
- `estimated_time` (string): Expected processing duration

---

#### Step 2: Poll QA Evaluation Status

**Endpoint:**
```
GET /qa/task/{task_id}
```

**Response States:**

**1. Processing (HTTP 200 OK):**
```json
{
  "task_id": "task_qa_a1b2c3d4e5f6",
  "status": "processing",
  "message": "QA evaluation in progress. Please check again shortly."
}
```

**2. Completed Successfully (HTTP 200 OK):**
```json
{
  "task_id": "task_qa_a1b2c3d4e5f6",
  "status": "completed",
  "result": {
    "evaluations": {
      "opening": [
        {
          "submetric": "Use of call opening phrase",
          "prediction": true,
          "score": "✓",
          "probability": 0.9567105174064636
        }
      ],
      "listening": [
        {
          "submetric": "Caller was not interrupted",
          "prediction": true,
          "score": "✓",
          "probability": 0.7852196097373962
        },
        {
          "submetric": "Empathizes with the caller",
          "prediction": false,
          "score": "✗",
          "probability": 0.5563325881958008
        },
        {
          "submetric": "Paraphrases or rephrases the issue",
          "prediction": false,
          "score": "✗",
          "probability": 0.3898620903491974
        },
        {
          "submetric": "Uses 'please' and 'thank you'",
          "prediction": true,
          "score": "✓",
          "probability": 0.6255266070365906
        },
        {
          "submetric": "Does not hesitate or sound unsure",
          "prediction": true,
          "score": "✓",
          "probability": 0.6388158202171326
        }
      ],
      "proactiveness": [
        {
          "submetric": "Willing to solve extra issues",
          "prediction": false,
          "score": "✗",
          "probability": 0.4224390387535095
        },
        {
          "submetric": "Confirms satisfaction with action points",
          "prediction": false,
          "score": "✗",
          "probability": 0.32597222924232483
        },
        {
          "submetric": "Follows up on case updates",
          "prediction": false,
          "score": "✗",
          "probability": 0.08417876809835434
        }
      ],
      "resolution": [
        {
          "submetric": "Gives accurate information",
          "prediction": false,
          "score": "✗",
          "probability": 0.5878533720970154
        },
        {
          "submetric": "Correct language use",
          "prediction": true,
          "score": "✓",
          "probability": 0.7913471460342407
        },
        {
          "submetric": "Consults if unsure",
          "prediction": false,
          "score": "✗",
          "probability": 0.2499508112668991
        },
        {
          "submetric": "Follows correct steps",
          "prediction": false,
          "score": "✗",
          "probability": 0.574279248714447
        },
        {
          "submetric": "Explains solution process clearly",
          "prediction": false,
          "score": "✗",
          "probability": 0.4905984699726105
        }
      ],
      "hold": [
        {
          "submetric": "Explains before placing on hold",
          "prediction": false,
          "score": "✗",
          "probability": 0.1048022210597992
        },
        {
          "submetric": "Thanks caller for holding",
          "prediction": false,
          "score": "✗",
          "probability": 0.18482911586761475
        }
      ],
      "closing": [
        {
          "submetric": "Proper call closing phrase used",
          "prediction": false,
          "score": "✗",
          "probability": 0.15396814048290253
        }
      ]
    },
    "processing_time": 0.008944,
    "model_info": {
      "model_path": "/home/rogendo/Work/New/ai/ai_service/models/all_qa_distilbert_v1",
      "loaded": true,
      "load_time": "2025-10-17T17:20:37.541899",
      "device": "cuda",
      "error": null,
      "max_length": 512,
      "model_type": "MultiHeadQAClassifier",
      "qa_heads": [
        "opening",
        "listening",
        "proactiveness",
        "resolution",
        "hold",
        "closing"
      ]
    },
    "timestamp": "2025-10-17T19:22:46.853704"
  }
}
```

**3. Failed (HTTP 200 OK with error details):**
```json
{
  "task_id": "task_qa_a1b2c3d4e5f6",
  "status": "failed",
  "error": "QA evaluation failed due to invalid input format"
}
```

---

#### cURL Examples

**Step 1: Submit QA Evaluation Task**
```bash
curl -X POST "https://your-api-domain.com/qa/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Hello, this is 116 sauti child helpline. My name is Jackson Kibwana, how can I help you today?",
    "threshold": 0.6,
    "return_raw": false
  }'
```

**Response:**
```json
{
  "task_id": "task_qa_a1b2c3d4e5f6",
  "status": "queued",
  "message": "QA evaluation task submitted successfully. Check status at /qa/task/task_qa_a1b2c3d4e5f6",
  "status_endpoint": "/qa/task/task_qa_a1b2c3d4e5f6",
  "estimated_time": "1-2 seconds"
}
```

**Step 2: Poll for Results**
```bash
curl -X GET "https://your-api-domain.com/qa/task/task_qa_a1b2c3d4e5f6"
```

---

#### Python Client Example

```python
import requests
import time
from typing import Dict

class QAClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def evaluate(self, transcript: str, threshold: float = 0.5, return_raw: bool = False) -> Dict:
        """
        Submit QA evaluation request and wait for results.

        Args:
            transcript: Call transcript text to evaluate
            threshold: Classification threshold for QA metrics
            return_raw: Whether to return raw probabilities

        Returns:
            QA evaluation results dictionary

        Raises:
            ValueError: For validation errors (400)
            RuntimeError: For server errors
        """
        # Step 1: Submit task
        response = requests.post(
            f"{self.base_url}/qa/evaluate",
            json={
                "transcript": transcript,
                "threshold": threshold,
                "return_raw": return_raw
            },
            timeout=10
        )

        if response.status_code == 202:
            task_data = response.json()
            task_id = task_data["task_id"]
        else:
            response.raise_for_status()

        # Step 2: Poll for results
        start_time = time.time()
        poll_interval = 0.5

        while time.time() - start_time < self.timeout:
            response = requests.get(
                f"{self.base_url}/qa/task/{task_id}",
                timeout=10
            )
            response.raise_for_status()

            task_status = response.json()

            if task_status["status"] == "completed":
                return task_status["result"]
            elif task_status["status"] == "failed":
                raise RuntimeError(f"QA evaluation failed: {task_status.get('error', 'Unknown error')}")

            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, 3.0)

        raise TimeoutError(f"QA evaluation did not complete within {self.timeout} seconds")

# Usage example
client = QAClient("https://your-api-domain.com")

try:
    result = client.evaluate(
        transcript="Hello, this is 116 sauti child helpline. My name is Jackson Kibwana...",
        threshold=0.6
    )

    print(f"QA Evaluation Results:")
    for metric, submetrics in result['evaluations'].items():
        print(f"\n{metric.upper()}:")
        for item in submetrics:
            print(f"  {item['submetric']}: {item['score']} ({item['probability']:.3f})")

except Exception as e:
    print(f"Error: {e}")
```

---


**Info Endpoint:**
Request URL
```bash
http://192.168.10.6:8123/qa/info
```


```bash
curl -X 'GET' \
  'http://192.168.10.6:8123/qa/info' \
  -H 'accept: application/json'
```  


```json
Response body

{
  "status": "ready",
  "model_info": {
    "model_path": "/home/rogendo/Work/New/ai/ai_service/models/all_qa_distilbert_v1",
    "loaded": true,
    "load_time": "2025-10-17T17:20:37.541899",
    "device": "cuda",
    "error": null,
    "max_length": 512,
    "model_type": "MultiHeadQAClassifier",
    "qa_heads": [
      "opening",
      "listening",
      "proactiveness",
      "resolution",
      "hold",
      "closing"
    ]
  }
}
```


Status code
```bash
200
```

Validation Error
 - Media type ```application/json```
```json
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```
Status code
```bash
422
```

### 3.2. Via Hugging Face Hub

**Repository:** [openchs/qa-helpline-distilbert-v1](https://huggingface.co/openchs/qa-helpline-distilbert-v1)

**Installation:**
```bash
pip install transformers torch
```

**Model classes:**
```python
import torch
import torch.nn as nn
from transformers import DistilBertModel, DistilBertPreTrainedModel, AutoTokenizer

class MultiHeadQAClassifier(DistilBertPreTrainedModel):
    """
    Multi-head QA classifier for call center quality assessment.
    Each head corresponds to a different QA metric with specific sub-metrics.
    """
    
    def __init__(self, config):
        super().__init__(config)
        
        # QA heads configuration
        self.heads_config = getattr(config, 'heads_config', {
            "opening": 1,
            "listening": 5,
            "proactiveness": 3,
            "resolution": 5,
            "hold": 2,
            "closing": 1
        })
        
        self.bert = DistilBertModel(config)
        classifier_dropout = getattr(config, 'classifier_dropout', 0.1)
        self.dropout = nn.Dropout(classifier_dropout)

        # Multiple classification heads
        self.classifiers = nn.ModuleDict({
            head_name: nn.Linear(config.hidden_size, num_labels)
            for head_name, num_labels in self.heads_config.items()
        })
        
        # Initialize weights
        self.post_init()

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = self.dropout(outputs.last_hidden_state[:, 0])  # [CLS] token

        logits = {}
        losses = {}
        total_loss = 0

        for head_name, classifier in self.classifiers.items():
            head_logits = classifier(pooled_output)
            logits[head_name] = torch.sigmoid(head_logits)  # Convert to probabilities

            # Calculate loss if labels provided
            if labels is not None and head_name in labels:
                loss_fn = nn.BCEWithLogitsLoss()
                loss = loss_fn(head_logits, labels[head_name])
                losses[head_name] = loss.item()
                total_loss += loss

        return {
            "logits": logits,
            "loss": total_loss if labels is not None else None,
            "losses": losses if labels is not None else None
        }

```
**Inference:**

```python

def predict_qa_metrics(text: str, model, tokenizer, threshold: float = 0.5, device=None):
    """
    Predict QA metrics for a helpline transcript with beautiful output formatting.
    
    Args:
        text: Input transcript text
        model: Loaded MultiHeadQAClassifier model
        tokenizer: DistilBERT tokenizer
        threshold: Classification threshold (default: 0.5)
        device: Device to use for inference
    
    Returns:
        Dictionary with predictions and probabilities for each QA metric
    """
    if device is None:
        device = next(model.parameters()).device
    
    model.eval()
    
    # Sub-metric labels for formatted output
    HEAD_SUBMETRIC_LABELS = {
        "opening": ["Use of call opening phrase"],
        "listening": [
            "Caller was not interrupted",
            "Empathizes with the caller", 
            "Paraphrases or rephrases the issue",
            "Uses 'please' and 'thank you'",
            "Does not hesitate or sound unsure"
        ],
        "proactiveness": [
            "Willing to solve extra issues",
            "Confirms satisfaction with action points",
            "Follows up on case updates"
        ],
        "resolution": [
            "Gives accurate information",
            "Correct language use",
            "Consults if unsure",
            "Follows correct steps",
            "Explains solution process clearly"
        ],
        "hold": [
            "Explains before placing on hold",
            "Thanks caller for holding"
        ],
        "closing": ["Proper call closing phrase used"]
    }

    # Tokenize input
    encoding = tokenizer(
        text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )
    
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)
    
    # Forward pass
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs["logits"]
    
    # Format results
    results = {}
    print(f"📞 Transcript: {text}\n")
    
    total_positive = 0
    total_metrics = 0
    
    for head_name, probs in logits.items():
        probs_np = probs.cpu().numpy()[0]
        submetrics = HEAD_SUBMETRIC_LABELS.get(head_name, [f"Submetric {i+1}" for i in range(len(probs_np))])
        
        print(f"🔹 {head_name.upper()}:")
        head_results = []
        
        for prob, submetric in zip(probs_np, submetrics):
            prediction = prob > threshold
            indicator = "✓" if prediction else "✗"
            
            if prediction:
                total_positive += 1
            total_metrics += 1
            
            result_item = {
                "submetric": submetric,
                "probability": float(prob),
                "prediction": bool(prediction),
                "indicator": indicator
            }
            head_results.append(result_item)
            
            print(f"  ➤ {submetric}: P={prob:.3f} → {indicator}")
        
        results[head_name] = head_results
    
    # Overall summary
    overall_accuracy = (total_positive / total_metrics) * 100
    print(f"\n Overall Score: {total_positive}/{total_metrics} ({overall_accuracy:.1f}%)")
    
    results["summary"] = {
        "total_positive": total_positive,
        "total_metrics": total_metrics,
        "accuracy": overall_accuracy
    }
    
    return results


from transformers import AutoTokenizer
import torch

# Load model and tokenizer
MODEL_NAME = "openchs/qa-helpline-distilbert-v1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = MultiHeadQAClassifier.from_pretrained(MODEL_NAME)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Example helpline transcript
transcript = """
Hello, thank you for calling our child helpline. My name is Sarah, how can I help you today? 
I understand your concern completely and I want to help you through this difficult situation. 
Let me check what resources we have available for you. Please hold for just a moment while I 
look into this. Thank you for holding. I've found several support options that can help. 
Is there anything else I can assist you with today? Thank you for reaching out to us, 
and please don't hesitate to call again if you need further support.
"""

# Run prediction
results = predict_qa_metrics(transcript, model, tokenizer, threshold=0.5, device=device)

# Access specific results
opening_results = results["opening"]
listening_results = results["listening"]
overall_summary = results["summary"]


```

***

## 4. Production Considerations

- **Maximum Input Length:** 512 tokens per segment (auto-chunked)
- **Segment Overlap:** Standard 50 tokens
- **Domain:** English helpline/call-center conversations
- **Error Handling:** API returns standard errors for unavailable model, empty input, or health check failures

***

## 5. Model Limitations

- **Context Limit**: 512 tokens; chunking required for longer dialogues
- **Domain Specificity**: Tuned for helpline QA, not general text classification
- **Model Performance**: Near-perfect on closure/resolution, weaker on nuanced listening behaviors
- **Language Bias**: English-only; not suitable for other languages
- **Ethical Use**: Must complement—not replace—human review in sensitive situations, strict evaluations as is trained on a synthetic data
- **Small training datasets**: The model was finetuned on a small set of data, with about 105 synthetically labeled sample records

***

## 6. Citation

If you use this model, cite:

```bibtex
@model{qa_helpline_distilbert_2025,
  title={QA Multi-Head DistilBERT for Helpline Quality Assessment},
  author={BITZ IT Consulting Team},
  year={2025},
  publisher={Hugging Face},
  journal={Hugging Face Model Hub},
  howpublished={https://huggingface.co/openchs/qa-helpline-distilbert-v1}
}
```

***

## 7. Support and Contact

- **Email:** info@bitz-itc.com
- **Hugging Face:** openchs organization

For bugs, improvements, or domain expansions, contact BITZ IT Consulting.


### Contributing
For dataset contributions, model improvements, or bug reports, please contact the BITZ AI Team at info@bitz-itc.com.

***

## 8. License

**Apache 2.0 License**—free for commercial/non-commercial use with proper attribution.

***
