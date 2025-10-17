# Classifier Model Documentation

## 1. Model Overview

The **cls-gbv-distilbert-v1** classifier model is a multi-task DistilBERT-based model fine-tuned for **Gender-Based Violence (GBV) case classification** in the context of child helpline services. This model is specifically trained on conversations from the **116 Child Helpline in Tanzania**, making it domain-specific for sensitive topics including abuse, violence, emergency situations, and child welfare cases.

### Key Features
- **Architecture:** Multi-task DistilBERT with custom classification heads
- **Domain:** Child helpline GBV case classification
- **Deployment:** Available via AI Service API and Hugging Face Hub
- **Repository:** openchs/cls-gbv-distilbert-v1
- **Special Capabilities:** Multi-task classification, confidence-weighted aggregation, priority escalation, automatic chunking for long narratives

### Classification Tasks

The model performs four simultaneous classification tasks:

1. **Main Category:** Primary case type classification
2. **Sub Category:** Detailed case sub-classification
3. **Intervention:** Recommended intervention type
4. **Priority:** Case urgency level (low, medium, high, urgent)

### Integration in AI Service Pipeline

The classification model is a critical component of the BITZ AI Service pipeline:

```
Audio Input → Transcription → Translation → English Text → Classification Model → Categories + Priority
                                                                ↓
                                                          NER/Summarization/QA
```

The model receives English translations (from the translation model or Whisper) and outputs structured classification results with confidence scores for downstream decision-making, agent notifications, and case management.

---

## 2. Integration in AI Service Architecture

The classification model is deeply integrated into the AI service through multiple layers:

### 2.1. Configuration Layer

The classification model is configured through the central settings system (`app/config/settings.py`):

```python
class Settings(BaseSettings):
    # Hugging Face configuration
    hf_token: Optional[str] = None  # No token needed for public models
    classifier_hf_repo_id: Optional[str] = "openchs/cls-gbv-distilbert-v1"
    hf_classifier_model: str = "openchs/cls-gbv-distilbert-v1"
    
    # Model paths
    models_path: str = "./models"  # Auto-adjusted for Docker
    
    # Enable HuggingFace models
    use_hf_models: bool = True
```

**Configuration Helper Methods:**

```python
def get_model_path(self, model_name: str) -> str:
    """Get absolute path for a model"""
    return os.path.join(self.models_path, model_name)

def _get_hf_model_id(self, model_name: str) -> str:
    """Get HuggingFace model ID for classifier"""
    model_id_map = {
        "classifier": self.hf_classifier_model,
        # ... other models
    }
    return model_id_map.get(model_name, "")
```

**Environment Detection:**

The system automatically detects whether it's running in Docker or local development and adjusts paths accordingly:

```python
def initialize_paths(self):
    """Initialize paths - automatically detect Docker environment"""
    self.docker_container = os.getenv("DOCKER_CONTAINER") is not None or os.path.exists("/.dockerenv")
    
    if self.docker_container:
        self.models_path = "/app/models"
        self.logs_path = "/app/logs"
        self.temp_path = "/app/temp"
    else:
        # Use relative paths for local development
        self.models_path = "./models"
```

### 2.2. Model Architecture

**Custom Multi-Task DistilBERT Architecture:**

```python
class MultiTaskDistilBert(DistilBertPreTrainedModel):
    """Custom DistilBERT model for multi-task classification"""
    
    def __init__(self, config, num_main, num_sub, num_interv, num_priority):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.pre_classifier = nn.Linear(config.dim, config.dim)
        
        # Four separate classification heads
        self.classifier_main = nn.Linear(config.dim, num_main)
        self.classifier_sub = nn.Linear(config.dim, num_sub)
        self.classifier_interv = nn.Linear(config.dim, num_interv)
        self.classifier_priority = nn.Linear(config.dim, num_priority)
        
        self.dropout = nn.Dropout(config.dropout)
        self.init_weights()

    def forward(self, input_ids=None, attention_mask=None):
        # Get DistilBERT embeddings
        distilbert_output = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        hidden_state = distilbert_output.last_hidden_state 
        pooled_output = hidden_state[:, 0]  # CLS token
        
        # Shared pre-classifier layer
        pooled_output = self.pre_classifier(pooled_output) 
        pooled_output = nn.ReLU()(pooled_output)           
        pooled_output = self.dropout(pooled_output)        
        
        # Four classification heads
        logits_main = self.classifier_main(pooled_output)
        logits_sub = self.classifier_sub(pooled_output)
        logits_interv = self.classifier_interv(pooled_output)
        logits_priority = self.classifier_priority(pooled_output)
        
        return (logits_main, logits_sub, logits_interv, logits_priority)
```

**Category Configuration:**

The model loads category definitions from JSON configuration files:

```python
def _load_category_configs(self):
    """Load classifier configuration files"""
    config_files = {
        "main_categories": "main_categories.json",
        "sub_categories": "sub_categories.json", 
        "interventions": "interventions.json",
        "priorities": "priorities.json"
    }
    
    # Load from local files or fetch from HuggingFace Hub
    for config_name, filename in config_files.items():
        # Try local path first
        config_file_path = os.path.join(self.model_path, filename)
        if os.path.exists(config_file_path):
            with open(config_file_path) as f:
                configs[config_name] = json.load(f)
        else:
            # Fetch from HuggingFace Hub
            from huggingface_hub import hf_hub_download
            download_path = hf_hub_download(
                repo_id=self.hf_repo_id,
                filename=filename
            )
            with open(download_path) as f:
                configs[config_name] = json.load(f)
```

### 2.3. Model Loading and Initialization

The classification model is loaded through the `ClassifierModel` class during FastAPI application startup:

```python
class ClassifierModel:
    """Multi-task classifier with intelligent chunking support"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("classifier")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.loaded = False
        self.max_length = 256  # Model's maximum token limit
        
        # Hugging Face repo configuration
        self.hf_repo_id = os.getenv("CLASSIFIER_HF_REPO_ID") or \
                         getattr(settings, "classifier_hf_repo_id", None)
        
        # Category lists - loaded during initialization
        self.main_categories = []
        self.sub_categories = []
        self.interventions = []
        self.priorities = []
        
    def load(self) -> bool:
        """Load tokenizer, model weights, and category configs"""
        try:
            # Load category configs first
            if not self._load_category_configs():
                return False
            
            # Load model from Hugging Face Hub
            logger.info(f"Loading classifier from HF Hub: {self.hf_repo_id}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.hf_repo_id,
                local_files_only=False
            )
            
            self.model = MultiTaskDistilBert.from_pretrained(
                self.hf_repo_id,
                num_main=len(self.main_categories),
                num_sub=len(self.sub_categories),
                num_interv=len(self.interventions),
                num_priority=len(self.priorities),
                local_files_only=False
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            self.load_time = datetime.now()
            
            logger.info(f" Classifier model loaded on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to load classifier: {e}")
            self.error = str(e)
            return False
```

**Model Loader Integration:**

```python
# During FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize classifier model via model_loader
    model_loader.load_model("classifier_model")
    yield
    # Cleanup on shutdown
```

### 2.4. API Endpoints Layer

Classification functionality is exposed through FastAPI routes (`app/api/endpoints/classifier_routes.py`):

```python
router = APIRouter(prefix="/classifier", tags=["classifier"])

class ClassifierRequest(BaseModel):
    narrative: str

class ConfidenceScores(BaseModel):
    main_category: float
    sub_category: float
    intervention: float
    priority: float

class ClassifierResponse(BaseModel):
    main_category: str
    sub_category: str
    intervention: str
    priority: str
    confidence_scores: ConfidenceScores
    chunks_processed: int
    chunk_predictions: Optional[List[ChunkPrediction]] = None
    processing_time: float
    model_info: dict
    timestamp: str

@router.post("/classify", response_model=ClassifierResponse)
async def classify_narrative(request: ClassifierRequest):
    """Classify case narrative with automatic chunking"""
    
    # Check model readiness
    if not model_loader.is_model_ready("classifier_model"):
        raise HTTPException(
            status_code=503,
            detail="Classifier model not ready. Check /health/models for status."
        )
    
    # Validate input
    if not request.narrative.strip():
        raise HTTPException(
            status_code=400,
            detail="Narrative input cannot be empty"
        )
    
    # Get classifier model
    classifier = model_loader.models.get("classifier_model")
    
    # Initialize chunker
    tokenizer_name = "distilbert-base-uncased"
    chunker = ClassificationChunker(
        tokenizer_name=tokenizer_name,
        max_tokens=512,
        overlap_tokens=150
    )
    
    # Count tokens and decide on chunking
    token_count = chunker.count_tokens(request.narrative)
    MAX_SOURCE_LENGTH = 512
    
    if token_count <= MAX_SOURCE_LENGTH:
        # Direct classification for short text
        classification = classifier.classify(request.narrative)
        
        aggregated_result = {
            'main_category': classification['main_category'],
            'sub_category': classification['sub_category'],
            'intervention': classification['intervention'],
            'priority': classification['priority'],
            'confidence_scores': classification.get('confidence_scores'),
            'chunks_processed': 1,
            'chunk_predictions': None
        }
    else:
        # Chunking needed for long text
        chunks = chunker.chunk_transcript(request.narrative)
        
        # Classify each chunk
        chunk_predictions = []
        for chunk_info in chunks:
            chunk_classification = classifier.classify(chunk_info['text'])
            chunk_predictions.append(chunk_classification)
        
        # Aggregate using confidence-weighted voting
        aggregator = ClassificationAggregator()
        aggregated_result = aggregator.aggregate_case_classification(
            chunk_predictions
        )
        aggregated_result['chunks_processed'] = len(chunks)
    
    return ClassifierResponse(
        main_category=aggregated_result['main_category'],
        sub_category=aggregated_result['sub_category'],
        intervention=aggregated_result['intervention'],
        priority=aggregated_result['priority'],
        confidence_scores=ConfidenceScores(
            **aggregated_result['confidence_scores']
        ),
        chunks_processed=aggregated_result['chunks_processed'],
        chunk_predictions=aggregated_result.get('chunk_predictions'),
        processing_time=processing_time,
        model_info=classifier.get_model_info(),
        timestamp=datetime.now().isoformat()
    )
```

**Information Endpoint:**

```python
@router.get("/info")
async def get_classifier_info():
    """Get classifier model information"""
    if not model_loader.is_model_ready("classifier_model"):
        return {
            "status": "not_ready",
            "message": "Classifier model not loaded"
        }
    
    classifier = model_loader.models.get("classifier_model")
    return {
        "status": "ready",
        "model_info": classifier.get_model_info()
    }
```

**Demo Endpoint:**

```python
@router.post("/demo")
async def classifier_demo():
    """Demo endpoint with sample narrative"""
    demo_narrative = (
        "On 2023-05-15 a girl (age 16) from District X called to report "
        "sexual abuse by her stepfather. She is currently 2 months pregnant "
        "and being forced to abort. The stepfather has threatened to kill "
        "her if she doesn't comply. Her mother is also being abused."
    )
    
    request = ClassifierRequest(narrative=demo_narrative)
    return await classify_narrative(request)
```

### 2.5. Classification Chunking Strategy

The `ClassificationChunker` utility handles automatic segmentation of long narratives to respect the model's 256-token limit:

**Why Chunking is Needed:**
- DistilBERT models have a maximum context length of 256 tokens
- Long helpline case narratives often exceed this limit
- Direct truncation would lose critical information
- Chunking with overlap preserves context across segments

**Chunking Implementation:**

```python
class ClassificationChunker:
    """Utility for chunking long texts for classification"""
    
    def __init__(self, tokenizer_name: str, max_tokens: int = 512, 
                 overlap_tokens: int = 150):
        self.tokenizer_name = tokenizer_name
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text, add_special_tokens=True))
    
    def chunk_transcript(self, text: str) -> List[Dict]:
        """
        Create overlapping chunks from text
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries with metadata
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = self.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > self.max_tokens:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'token_count': current_tokens,
                    'sentence_count': len(current_chunk),
                    'chunk_index': len(chunks),
                    'position_ratio': i / len(sentences)
                })
                
                # Start new chunk with overlap
                overlap_size = self.overlap_tokens
                current_chunk = current_chunk[-2:] if len(current_chunk) >= 2 else []
                current_tokens = sum(self.count_tokens(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'token_count': current_tokens,
                'sentence_count': len(current_chunk),
                'chunk_index': len(chunks),
                'position_ratio': 1.0
            })
        
        return chunks
```

**Overlap Strategy:**

The 150-token overlap between chunks ensures:
- Context preservation across segment boundaries
- Better handling of case narratives that span multiple segments
- Improved classification accuracy for complex cases

### 2.6. Classification Aggregation Strategy

The `ClassificationAggregator` implements confidence-weighted voting to combine predictions from multiple chunks:

```python
class ClassificationAggregator:
    """Aggregate classification results from multiple chunks"""
    
    def aggregate_case_classification(self, 
                                     chunk_predictions: List[Dict]) -> Dict:
        """
        Aggregate chunk predictions using confidence-weighted voting
        
        Args:
            chunk_predictions: List of classification results from chunks
            
        Returns:
            Aggregated classification with confidence scores
        """
        if not chunk_predictions:
            return self._get_default_classification()
        
        if len(chunk_predictions) == 1:
            return chunk_predictions[0]
        
        # Confidence-weighted voting for each task
        main_votes = Counter()
        sub_votes = Counter()
        interv_votes = Counter()
        priority_votes = Counter()
        
        total_weight = 0
        
        for pred in chunk_predictions:
            # Weight by confidence
            weight = pred.get('confidence_scores', {}).get('main_category', 0.5)
            total_weight += weight
            
            main_votes[pred['main_category']] += weight
            sub_votes[pred['sub_category']] += weight
            interv_votes[pred['intervention']] += weight
            priority_votes[pred['priority']] += weight
        
        # Get most common predictions
        final_main = main_votes.most_common(1)[0][0]
        final_sub = sub_votes.most_common(1)[0][0]
        final_interv = interv_votes.most_common(1)[0][0]
        final_priority = priority_votes.most_common(1)[0][0]
        
        # Apply priority escalation logic
        final_priority = self._apply_priority_escalation(
            chunk_predictions, 
            final_priority
        )
        
        # Calculate aggregated confidence scores
        confidence_scores = {
            'main_category': main_votes[final_main] / total_weight,
            'sub_category': sub_votes[final_sub] / total_weight,
            'intervention': interv_votes[final_interv] / total_weight,
            'priority': priority_votes[final_priority] / total_weight
        }
        
        return {
            'main_category': final_main,
            'sub_category': final_sub,
            'intervention': final_interv,
            'priority': final_priority,
            'confidence_scores': confidence_scores
        }
    
    def _apply_priority_escalation(self, 
                                   chunk_predictions: List[Dict], 
                                   default_priority: str) -> str:
        """Apply priority escalation for critical cases"""
        priorities_seen = [pred.get('priority', 'medium') 
                          for pred in chunk_predictions]
        
        # Escalate if any chunk indicates high priority
        if 'urgent' in priorities_seen:
            return 'urgent'
        elif 'high' in priorities_seen:
            return 'high'
        else:
            return default_priority
```

**Aggregation Features:**

1. **Confidence-Weighted Voting:** Each chunk's prediction is weighted by its confidence score
2. **Priority Escalation:** If any chunk detects high/urgent priority, the final classification is escalated
3. **Multi-Task Coordination:** All four classification tasks are aggregated independently

### 2.7. Health Monitoring

The classification model integrates with the AI service health monitoring system:

**Model Status Endpoint:**

```python
@router.get("/health/models")
async def models_health():
    """Get detailed model status"""
    model_status = model_loader.get_model_status()
    ready_models = model_loader.get_ready_models()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(model_status),
            "ready": len(ready_models)
        },
        "ready_models": ready_models,
        "details": model_status
    }
```

**Model Readiness States:**

- **Ready:** Model loaded and available for classification
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

**Health Check Example Response:**

```json
{
  "ready_models": ["classifier_model", "translator", "ner"],
  "details": {
    "classifier_model": {
      "loaded": true,
      "device": "cuda",
      "hf_repo_id": "openchs/cls-gbv-distilbert-v1",
      "max_length": 256,
      "chunking_supported": true,
      "aggregation_strategy": "weighted_voting",
      "priority_escalation": true,
      "num_categories": {
        "main": 12,
        "sub": 48,
        "intervention": 8,
        "priority": 4
      }
    }
  }
}
```

### 2.8. Pipeline Integration

The classification model integrates into two processing modes:

#### Real-time Processing

For live calls, classification works progressively:

```python
# Progressive classification during active call
@router.get("/{call_id}/classification")
async def get_call_classification(call_id: str):
    """Get progressive classification for active call"""
    analysis = progressive_processor.get_call_analysis(call_id)
    
    return {
        "call_id": call_id,
        "latest_classification": analysis.latest_classification,
        "classification_windows": len([w for w in analysis.windows 
                                       if w.classification]),
        "priority": analysis.latest_classification.get('priority'),
        "confidence": analysis.latest_classification.get('confidence')
    }
```

**Real-time Flow:**
1. Audio stream → Whisper transcription
2. Transcript → Translation (if needed)
3. Translated text → Classification
4. Classification → Agent notifications (if high priority)

#### Post-call Processing

For completed calls, full pipeline execution:

```python
# Complete pipeline after call ends
Audio File → Transcription → Translation → Classification (chunked if needed)
→ Priority-based routing → NER → Summarization → QA Scoring → Insights
```

**Configuration for Pipeline Modes:**

```python
# Settings control pipeline behavior
realtime_enable_progressive_classification: bool = True
postcall_enable_full_pipeline: bool = True
```

### 2.9. Memory Management

The classification model implements automatic GPU memory management:

```python
def _cleanup_memory(self):
    """Clean up GPU memory after classification"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

# Cleanup occurs:
# - After each classification request
# - Every 5 chunks during long classifications
# - Before retry attempts
```

---

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The classification model is deployed as part of the AI Service and accessible via REST API.

#### Endpoint
```
POST /classifier/classify
```

#### Request Format

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "narrative": "string"
}
```

#### Response Format

**Success Response (200):**
```json
{
  "main_category": "string",
  "sub_category": "string",
  "intervention": "string",
  "priority": "string",
  "confidence_scores": {
    "main_category": 0.95,
    "sub_category": 0.89,
    "intervention": 0.92,
    "priority": 0.88
  },
  "chunks_processed": 1,
  "chunk_predictions": null,
  "processing_time": 0.45,
  "model_info": {
    "model_path": "string",
    "hf_repo_id": "openchs/cls-gbv-distilbert-v1",
    "device": "cuda",
    "loaded": true,
    "max_length": 256,
    "chunking_supported": true
  },
  "timestamp": "2025-10-17T10:30:45Z"
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "narrative"],
      "msg": "Narrative input cannot be empty",
      "type": "value_error"
    }
  ]
}
```

#### Example cURL Request

**Basic Classification:**
```bash
curl -X POST "https://your-api-domain.com/classifier/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "A 16-year-old girl called to report sexual abuse by her stepfather. She is pregnant and being threatened. Immediate intervention needed."
  }'
```

**Response:**
```json
{
  "main_category": "sexual_abuse",
  "sub_category": "child_sexual_abuse",
  "intervention": "emergency_response",
  "priority": "urgent",
  "confidence_scores": {
    "main_category": 0.96,
    "sub_category": 0.93,
    "intervention": 0.95,
    "priority": 0.97
  },
  "chunks_processed": 1,
  "chunk_predictions": null,
  "processing_time": 0.52,
  "model_info": {
    "hf_repo_id": "openchs/cls-gbv-distilbert-v1",
    "device": "cuda",
    "loaded": true,
    "max_length": 256,
    "chunking_supported": true
  },
  "timestamp": "2025-10-17T10:30:45Z"
}
```

#### Getting Classifier Info

**Endpoint:**
```
GET /classifier/info
```

**Response:**
```json
{
  "status": "ready",
  "model_info": {
    "hf_repo_id": "openchs/cls-gbv-distilbert-v1",
    "device": "cuda",
    "loaded": true,
    "max_length": 256,
    "chunking_supported": true,
    "aggregation_strategy": "weighted_voting",
    "priority_escalation": true,
    "num_categories": {
      "main": 12,
      "sub": 48,
      "intervention": 8,
      "priority": 4
    }
  }
}
```

#### Demo Endpoint

**Endpoint:**
```
POST /classifier/demo
```

**Response:**
Returns classification for a pre-configured sample narrative demonstrating the model's capabilities.

#### Features
- **Automatic Chunking:** Long narratives are automatically chunked to handle extended case descriptions
- **Segment Processing:** 150-token overlap between chunks for context preservation
- **Confidence-Weighted Aggregation:** Multiple chunk predictions combined using confidence scores
- **Priority Escalation:** Automatic escalation if any chunk detects high/urgent priority
- **GPU Memory Management:** Automatic cleanup between requests

---

### 3.2. Via Hugging Face Hub

The model is publicly available on Hugging Face for direct inference and fine-tuning.

#### Model Repository
- **Organization:** [openchs](https://huggingface.co/openchs)
- **Model:** [openchs/cls-gbv-distilbert-v1](https://huggingface.co/openchs/cls-gbv-distilbert-v1)

#### Installation

```bash
pip install transformers torch
```

#### Inference Example

**Using the Model Directly:**
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer
model_name = "openchs/cls-gbv-distilbert-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Prepare input
narrative = """A 16-year-old girl called to report sexual abuse by her 
stepfather. She is currently 2 months pregnant and being forced to abort. 
The stepfather has threatened to kill her if she doesn't comply."""

inputs = tokenizer(
    narrative, 
    return_tensors="pt", 
    padding=True, 
    truncation=True,
    max_length=256
)

# Generate predictions
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits

# Get predictions
predictions = torch.argmax(logits, dim=1)
confidences = torch.softmax(logits, dim=1)

print(f"Main Category: {predictions[0].item()}")
print(f"Confidence: {confidences[0][predictions[0]].item():.3f}")
```

**Note:** When using the model directly from Hugging Face, you'll need to:
1. Load the category configuration files separately
2. Implement your own chunking logic for narratives longer than 256 tokens
3. Handle multi-task output parsing

The AI Service API handles all of this automatically.

#### Batch Classification
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "openchs/cls-gbv-distilbert-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

narratives = [
    "Child reports emotional abuse at home",
    "Emergency - child in immediate danger",
    "General inquiry about helpline services"
]

inputs = tokenizer(
    narratives,
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=256
)

with torch.no_grad():
    outputs = model(**inputs)

for i, narrative in enumerate(narratives):
    prediction = torch.argmax(outputs.logits[i])
    confidence = torch.softmax(outputs.logits[i], dim=0)[prediction]
    print(f"{narrative[:50]}... → Category: {prediction.item()} "
          f"(confidence: {confidence:.3f})")
```

---

## 4. Production Considerations

### Token Limits
- **Maximum Input Length:** 256 tokens per chunk
- **Recommended Chunk Size:** 200-250 tokens for optimal performance
- **Chunk Overlap:** 150 tokens between segments

### Processing Time
- **Short narratives (< 100 tokens):** ~0.3-0.5 seconds
- **Medium narratives (100-250 tokens):** ~0.5-1.0 seconds
- **Long narratives (> 250 tokens):** ~1.0-3.0 seconds (with chunking)

Processing times vary based on:
- GPU availability (CUDA vs CPU)
- Narrative length and complexity
- Number of chunks required
- System load

### Automatic Chunking
The API automatically handles long narratives by:
1. **Token Counting:** Checking if input exceeds 256 tokens
2. **Sentence-Based Segmentation:** Creating chunks at sentence boundaries
3. **Overlap Management:** Including 150-token overlap between chunks
4. **Classification:** Processing each segment independently
5. **Aggregation:** Combining results using confidence-weighted voting

### Confidence Scores

The model returns confidence scores for each classification task:
- **High Confidence (> 0.85):** Reliable classification, safe for automated routing
- **Medium Confidence (0.60-0.85):** Good classification, consider human review for critical cases
- **Low Confidence (< 0.60):** Manual review recommended

### Priority Escalation

The system automatically escalates priority when:
- Any chunk predicts "urgent" priority
- Multiple chunks predict "high" priority
- Main category indicates emergency situation
- Sub-category suggests immediate danger

### Error Handling

**Common Error Scenarios:**

1. **Empty Narrative:**
```json
{
  "detail": [
    {
      "loc": ["body", "narrative"],
      "msg": "Narrative input cannot be empty",
      "type": "value_error"
    }
  ]
}
```

2. **Model Not Ready:**
```json
{
  "detail": "Classifier model not ready. Check /health/models for status."
}
```

3. **Service Unavailable:**
```json
{
  "detail": "Classifier model not available"
}
```

### Health Checks

Monitor classification service health:

```bash
# Check if classifier is ready
curl -X GET "https://your-api-domain.com/health/models"

# Get detailed system status
curl -X GET "https://your-api-domain.com/health/detailed"
```

---

## 5. Model Limitations

### Domain Specificity
- **Optimized for:** GBV cases, child abuse, emergency situations in helpline context
- **May require adaptation for:** General case management, non-GBV cases, different cultural contexts
- **Performance varies on:** Out-of-distribution data, highly specialized case types

### Technical Constraints
- **Maximum Context:** 256 tokens per chunk (handled automatically via chunking)
- **Memory Requirements:** GPU recommended for production (CPU fallback available)
- **Processing Speed:** Dependent on hardware and narrative length

### Known Considerations
- **Multi-Task Learning:** While generally accurate, individual task performance may vary
- **Long Narratives:** Chunking may occasionally affect classification consistency across segments
- **Cultural Context:** Model trained on Tanzanian helpline data; may need calibration for other regions
- **Priority Escalation:** Errs on the side of caution - may over-escalate in ambiguous cases

### Recommendations
- Monitor classification accuracy for edge cases in your domain
- Implement human-in-the-loop review for high-stakes decisions
- Use confidence scores to route low-confidence cases for manual review
- Consider fine-tuning for specific organizational needs
- Regularly evaluate priority escalation rules against operational requirements

---

## 6. Classification Categories

### Main Categories (12)
- Sexual Abuse
- Physical Abuse
- Emotional Abuse
- Neglect
- General Inquiry
- Emergency
- Child Protection Concern
- Family Issues
- Educational Issues
- Health Issues
- Economic Issues
- Other

### Sub-Categories (48)
Multiple detailed sub-categories under each main category, providing granular case classification.

### Intervention Types (8)
- Emergency Response
- Immediate Assessment
- Standard Assessment
- Counseling Support
- Referral to Services
- Information Provision
- Follow-up Required
- Case Monitoring

### Priority Levels (4)
- **Urgent:** Immediate life-threatening situation
- **High:** Serious case requiring rapid response
- **Medium:** Standard case requiring timely response
- **Low:** General inquiry or information request

---

## 7. Citation

If you use this model in your research or application, please cite:

```bibtex
@misc{cls_gbv_distilbert_v1,
  title={cls-gbv-distilbert-v1: Multi-task Classification for GBV Cases},
  author={OpenCHS Team},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/openchs/cls-gbv-distilbert-v1}
}
```

---

## 8. Support and Contact

### Issues and Questions
- **Email:** info@bitz-itc.com
- **Hugging Face:** [openchs organization](https://huggingface.co/openchs)

### Contributing
For dataset contributions, model improvements, or bug reports, please contact the BITZ AI Team at info@bitz-itc.com.

---

## 9. License

This model is released under the **Apache 2.0 License**, allowing for both commercial and non-commercial use with proper attribution.

---

*Documentation last updated: October 17, 2025*