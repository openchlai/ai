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

The classification model is configured through the central settings system:

```python
class Settings(BaseSettings):
    # Hugging Face configuration
    classifier_hf_repo_id: str = "openchs/cls-gbv-distilbert-v1"
    hf_classifier_model: str = "openchs/cls-gbv-distilbert-v1"
    use_hf_models: bool = True
    models_path: str = "./models"  # Auto-adjusted for Docker
```

The system automatically detects whether it's running in Docker or local development and adjusts paths accordingly.

### 2.2. Model Architecture

**Custom Multi-Task DistilBERT:**

The model uses a shared DistilBERT base with four separate classification heads:

```python
class MultiTaskDistilBert(DistilBertPreTrainedModel):
    def __init__(self, config, num_main, num_sub, num_interv, num_priority):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.pre_classifier = nn.Linear(config.dim, config.dim)
        
        # Four separate classification heads
        self.classifier_main = nn.Linear(config.dim, num_main)
        self.classifier_sub = nn.Linear(config.dim, num_sub)
        self.classifier_interv = nn.Linear(config.dim, num_interv)
        self.classifier_priority = nn.Linear(config.dim, num_priority)
```

**Category Configuration:**

The model loads category definitions from JSON files (main_categories.json, sub_categories.json, interventions.json, priorities.json) either from local storage or HuggingFace Hub.

### 2.3. Model Loading and Initialization

The model is loaded during FastAPI startup:

```python
class ClassifierModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = 256  # Model's maximum token limit
        self.hf_repo_id = "openchs/cls-gbv-distilbert-v1"
        
    def load(self) -> bool:
        """Load tokenizer, model weights, and category configs"""
        # Load category configs first
        self._load_category_configs()
        
        # Load model from Hugging Face Hub
        self.tokenizer = AutoTokenizer.from_pretrained(self.hf_repo_id)
        self.model = MultiTaskDistilBert.from_pretrained(
            self.hf_repo_id,
            num_main=len(self.main_categories),
            num_sub=len(self.sub_categories),
            num_interv=len(self.interventions),
            num_priority=len(self.priorities)
        )
        self.model.to(self.device)
        self.model.eval()
```

### 2.4. API Endpoints Layer

**Classification Endpoint:**

```python
@router.post("/classify", response_model=ClassifierResponse)
async def classify_narrative(request: ClassifierRequest):
    """Classify case narrative with automatic chunking"""
    
    # Check model readiness
    if not model_loader.is_model_ready("classifier_model"):
        raise HTTPException(status_code=503)
    
    # Get classifier and initialize chunker
    classifier = model_loader.models.get("classifier_model")
    chunker = ClassificationChunker(
        tokenizer_name="distilbert-base-uncased",
        max_tokens=512,
        overlap_tokens=150
    )
    
    # Check if chunking is needed
    token_count = chunker.count_tokens(request.narrative)
    
    if token_count <= 512:
        # Direct classification
        classification = classifier.classify(request.narrative)
    else:
        # Chunk, classify each chunk, then aggregate
        chunks = chunker.chunk_transcript(request.narrative)
        chunk_predictions = [classifier.classify(c['text']) for c in chunks]
        classification = aggregator.aggregate_case_classification(chunk_predictions)
```

**Other Endpoints:**
- `GET /classifier/info` - Get classifier model information
- `POST /classifier/demo` - Demo with sample narrative

### 2.5. Classification Chunking Strategy

**Why Chunking is Needed:**
- DistilBERT models have a maximum context length of 256 tokens
- Long helpline case narratives often exceed this limit
- Direct truncation would lose critical information
- Chunking with overlap preserves context across segments

**Key Implementation:**

```python
class ClassificationChunker:
    def chunk_transcript(self, text: str) -> List[Dict]:
        """Create overlapping chunks from text"""
        sentences = self._split_sentences(text)
        chunks = []
        
        for sentence in sentences:
            # Add sentence to current chunk
            # If chunk exceeds max_tokens, save it and start new chunk
            # Include overlap from previous chunk
            
        return chunks  # Each with metadata: text, token_count, position_ratio
```

The 150-token overlap ensures context preservation across segment boundaries.

### 2.6. Classification Aggregation Strategy

For multi-chunk classifications, the system uses **confidence-weighted voting**:

```python
class ClassificationAggregator:
    def aggregate_case_classification(self, chunk_predictions: List[Dict]) -> Dict:
        """Aggregate using confidence-weighted voting"""
        
        # Weight each prediction by its confidence score
        for pred in chunk_predictions:
            weight = pred['confidence_scores']['main_category']
            main_votes[pred['main_category']] += weight
            sub_votes[pred['sub_category']] += weight
            # ... same for intervention and priority
        
        # Get most voted predictions
        final_main = main_votes.most_common(1)[0][0]
        final_sub = sub_votes.most_common(1)[0][0]
        # ...
        
        # Apply priority escalation
        if 'urgent' in priorities_seen:
            final_priority = 'urgent'
        elif 'high' in priorities_seen:
            final_priority = 'high'
```

**Key Features:**
1. **Confidence-Weighted Voting:** High-confidence chunks have more influence
2. **Priority Escalation:** Any "urgent" chunk escalates the entire classification
3. **Independent Task Aggregation:** Each of the 4 tasks aggregated separately

### 2.7. Health Monitoring

The classification model integrates with the health monitoring system at `/health/models`.

**Model Readiness States:**
- **Ready:** Model loaded and available for classification
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

### 2.8. Pipeline Integration

The classification model integrates into two processing modes:

#### Real-time Processing
For live calls, classification works progressively on text windows as they arrive. High/urgent priority classifications trigger immediate agent notifications.

#### Post-call Processing
For completed calls, full pipeline execution with chunked classification if needed:
```
Audio → Transcription → Translation → Classification → Priority Routing → NER/QA/Summarization
```

### 2.9. Memory Management

The classification model implements automatic GPU memory cleanup after each request and every 5 chunks during long classifications to prevent memory issues.

---

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The classification model is deployed as part of the AI Service and accessible via REST API.

#### Endpoint
```
POST /classifier/classify
```

#### Request Format

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
  "processing_time": 0.52,
  "timestamp": "2025-10-17T10:30:45Z"
}
```

#### Example cURL Request

```bash
curl -X POST "https://your-api-domain.com/classifier/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "A 16-year-old girl called to report sexual abuse by her stepfather. She is pregnant and being threatened. Immediate intervention needed."
  }'
```

#### Additional Endpoints

**Get Classifier Info:**
```
GET /classifier/info
```

Returns model status, configuration, and category counts.

**Demo Endpoint:**
```
POST /classifier/demo
```
Returns classification for a pre-configured sample narrative.

#### Features
- **Automatic Chunking:** Long narratives handled automatically with 150-token overlap
- **Confidence-Weighted Aggregation:** Multiple chunk predictions combined intelligently
- **Priority Escalation:** Automatic escalation for high/urgent cases
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

#### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer
model_name = "openchs/cls-gbv-distilbert-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Prepare input
narrative = "A 16-year-old girl called to report sexual abuse..."
inputs = tokenizer(narrative, return_tensors="pt", truncation=True, max_length=256)

# Get predictions
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=1)
    confidences = torch.softmax(outputs.logits, dim=1)

print(f"Category: {predictions[0].item()}, Confidence: {confidences[0].max():.3f}")
```

**Note:** When using the model directly from Hugging Face, you'll need to:
- Load the category configuration files separately (main_categories.json, etc.)
- Implement your own chunking logic for narratives longer than 256 tokens
- Handle multi-task output parsing (4 separate classification heads)

The AI Service API handles all of this automatically.

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

Times vary based on GPU availability, narrative complexity, and system load.

### Automatic Chunking
The API automatically handles long narratives through:
1. Token counting and limit checking
2. Sentence-based segmentation with overlap
3. Independent chunk classification
4. Confidence-weighted aggregation

### Confidence Scores

- **High Confidence (> 0.85):** Reliable classification, safe for automated routing
- **Medium Confidence (0.60-0.85):** Good classification, consider human review for critical cases
- **Low Confidence (< 0.60):** Manual review recommended

### Priority Escalation

Automatic escalation occurs when:
- Any chunk predicts "urgent" priority
- Multiple chunks predict "high" priority
- Main category indicates emergency situation

### Error Handling

**Common errors:**
- Empty narrative (400 error)
- Model not ready (503 error)
- Service unavailable (500 error)

Check `/health/models` endpoint for model status.

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
- **Multi-Task Learning:** Individual task performance may vary
- **Long Narratives:** Chunking may occasionally affect classification consistency
- **Cultural Context:** Trained on Tanzanian helpline data; may need calibration for other regions
- **Priority Escalation:** May over-escalate in ambiguous cases (by design for safety)

### Recommendations
- Monitor classification accuracy for edge cases
- Implement human-in-the-loop review for high-stakes decisions
- Use confidence scores to route low-confidence cases for manual review
- Consider fine-tuning for specific organizational needs
- Regularly evaluate priority escalation rules

---

## 6. Classification Categories

### Main Categories (12)
Sexual Abuse, Physical Abuse, Emotional Abuse, Neglect, General Inquiry, Emergency, Child Protection Concern, Family Issues, Educational Issues, Health Issues, Economic Issues, Other

### Sub-Categories (48)
Multiple detailed sub-categories under each main category for granular case classification.

### Intervention Types (8)
Emergency Response, Immediate Assessment, Standard Assessment, Counseling Support, Referral to Services, Information Provision, Follow-up Required, Case Monitoring

### Priority Levels (4)
- **Urgent:** Immediate life-threatening situation
- **High:** Serious case requiring rapid response
- **Medium:** Standard case requiring timely response
- **Low:** General inquiry or information request

---

## 7. Citation

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
For dataset contributions, model improvements, or bug reports, contact the BITZ AI Team at info@bitz-itc.com.

---

## 9. License

This model is released under the **Apache 2.0 License**, allowing for both commercial and non-commercial use with proper attribution.

---

*Documentation last updated: October 17, 2025*