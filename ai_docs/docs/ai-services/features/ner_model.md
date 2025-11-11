# Named Entity Recognition Model Documentation

## 1. Model Overview

The **ner_distillbert** model is a DistilBERT-based Named Entity Recognition system fine-tuned for identifying sensitive entities in child helpline conversations. Built on DistilBERT architecture, it retains 97% of BERT's performance while being 60% smaller and faster, making it ideal for real-time production environments.

### Key Features
- **Architecture:** DistilBERT (distilled BERT)
- **Domain:** Child helpline and protection services
- **Deployment:** Available via AI Service API and Hugging Face Hub
- **Repository:** openchs/ner_distillbert_v1
- **Special Capabilities:** Identifies perpetrators, victims, locations, landmarks, contact information, and incident types in sensitive conversations

### Integration in AI Service Pipeline

The NER model is a core component of the BITZ AI Service pipeline:

```
Translated Text → NER Model → Entity Extraction → Structured Data → Analysis
```

The model receives English text (either direct input or from the translation model) and outputs structured entity information for downstream processing by classification, summarization components.

### Supported Entity Types

The model can identify the following entity types:

* **PERPETRATOR** - Individuals accused or suspected of committing harmful acts
* **VICTIM** - Individuals who have experienced harm or abuse
* **NAME** - General person names that don't fall into specific roles
* **LOCATION** - Geographic locations (cities, countries, regions)
* **LANDMARK** - Specific places or buildings (schools, hospitals, parks)
* **PHONE_NUMBER** - Telephone numbers
* **GENDER** - Gender identifiers
* **AGE** - Age-related information
* **INCIDENT_TYPE** - Types of incidents or events reported
* **O** - Outside of named entity (non-entity tokens)

---

## 2. Integration in AI Service Architecture

The NER model is deeply integrated into the AI service through multiple layers:

### 2.1. Configuration Layer

The NER model is configured through the central settings system (app/config/settings.py):

```python
class Settings(BaseSettings):
    # Hugging Face configuration
    hf_token: Optional[str] = None  
    ner_hf_repo_id: Optional[str] = "openchs/ner_distillbert_v1"
    hf_ner_model: str = "openchs/ner_distillbert_v1"
    
    # Model paths
    models_path: str = "./models" 
    
    # Fallback configuration
    ner_fallback_model: str = "en_core_web_lg"  # spaCy fallback
    
    # Enable HuggingFace models
    use_hf_models: bool = True
```

**Configuration Helper Methods:**

```python
def get_ner_model_id(self) -> str:
    """Return the HuggingFace NER model id from configuration"""
    if self.hf_ner_model:
        return self.hf_ner_model
    return self._get_hf_model_id("ner")

def ner_backend(self) -> str:
    """Decide which backend should perform NER"""
    if self.use_hf_models and self.hf_ner_model:
        return "hf"
    return "spacy"  # Fallback to spaCy
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

### 2.2. Model Loading and Initialization

The NER model is loaded through the NERModel class during FastAPI application startup:

```python
class NERModel:
    """Named Entity Recognition model with confidence scoring"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        
        # Hugging Face repo support
        self.hf_repo_id = settings.ner_hf_repo_id
        
        # Fallback to spaCy if needed
        self.fallback_model_name = settings.ner_fallback_model
        self.nlp = None  # spaCy model
        
    def load(self) -> bool:
        """Load model from Hugging Face Hub with spaCy fallback"""
        try:
            logger.info(f"Loading NER model from HF Hub: {self.hf_repo_id}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.hf_repo_id, 
                local_files_only=False
            )
            self.model = AutoModelForTokenClassification.from_pretrained(
                self.hf_repo_id, 
                local_files_only=False
            )
            
            self.model.to(self.device)
            self.loaded = True
            
            logger.info(f"✓ NER model loaded on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to load NER model: {e}")
            logger.info(f"Attempting to load fallback spaCy model: {self.fallback_model_name}")
            
            try:
                self.nlp = spacy.load(self.fallback_model_name)
                self.loaded = True
                logger.info(f"✓ Fallback spaCy model loaded successfully")
                return True
            except Exception as spacy_error:
                logger.error(f"✗ Failed to load fallback model: {spacy_error}")
                return False
```

**Model Loader Integration:**

The NER model is managed by the central model_loader which handles:
- Startup initialization
- Readiness checks
- Dependency tracking
- Health monitoring

```python
# During FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize NER model via model_loader
    model_loader.load_model("ner")
    yield
    # Cleanup on shutdown
```

### 2.3. API Endpoints Layer

NER functionality is exposed through FastAPI routes (app/api/endpoints/ner_routes.py):

```python
router = APIRouter(prefix="/ner", tags=["ner"])

class NERRequest(BaseModel):
    text: str
    flat: bool = True

class EntityResponse(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float

class NERResponse(BaseModel):
    entities: List[EntityResponse]
    processing_time: float
    model_info: Dict
    timestamp: str

@router.post("/extract", response_model=NERResponse)
async def extract_entities(request: NERRequest):
    """Extract named entities from text with confidence scores"""
    
    # Check model readiness
    if not model_loader.is_model_ready("ner"):
        raise HTTPException(
            status_code=503,
            detail="NER model not ready. Check /health/models for status."
        )
    
    # Validate input
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    # Get NER model
    ner_model = model_loader.models.get("ner")
    
    # Extract entities
    start_time = time.time()
    entities = ner_model.extract_entities(request.text, flat=request.flat)
    processing_time = time.time() - start_time
    
    return NERResponse(
        entities=entities,
        processing_time=processing_time,
        model_info=ner_model.get_model_info(),
        timestamp=datetime.now().isoformat()
    )
```

**Information Endpoint:**

```python
@router.get("/info")
async def get_ner_info():
    """Get NER service information"""
    if not model_loader.is_model_ready("ner"):
        return {
            "status": "not_ready",
            "message": "NER model not loaded"
        }
    
    ner_model = model_loader.models.get("ner")
    return {
        "status": "ready",
        "model_info": ner_model.get_model_info(),
        "supported_entities": [
            "PERPETRATOR", "VICTIM", "NAME", "LOCATION", 
            "LANDMARK", "PHONE_NUMBER", "GENDER", "AGE", 
            "INCIDENT_TYPE"
        ]
    }
```

**Demo Endpoint:**

```python
@router.post("/demo")
async def demo_extraction():
    """Demonstrate NER extraction using sample text"""
    sample_text = "John reported an incident at Central Park. The victim was a 12-year-old girl. Contact number: 555-0123."
    
    if not model_loader.is_model_ready("ner"):
        raise HTTPException(status_code=503, detail="NER model not ready")
    
    ner_model = model_loader.models.get("ner")
    entities = ner_model.extract_entities(sample_text)
    
    return {
        "sample_text": sample_text,
        "entities": entities,
        "model_info": ner_model.get_model_info()
    }
```

### 2.4. Entity Extraction Strategy

The NER model implements intelligent entity extraction with confidence scoring:

**Why Confidence Scoring is Important:**
- Child protection contexts require high-confidence entity identification
- False positives can lead to inappropriate alerts or actions
- Confidence scores enable downstream filtering and prioritization
- Different entity types may require different confidence thresholds

**Extraction Implementation:**

```python
def extract_entities(self, text: str, flat: bool = True) -> List[Dict]:
    """
    Extract entities with confidence scores
    
    Args:
        text: Input text to analyze
        flat: If True, return flat list; if False, return grouped entities
        
    Returns:
        List of entity dictionaries with text, label, position, and confidence
    """
    if not self.loaded:
        return []
    
    # Use transformer model if available
    if self.model and self.tokenizer:
        return self._extract_with_transformers(text, flat)
    
    # Fallback to spaCy
    if self.nlp:
        return self._extract_with_spacy(text, flat)
    
    return []

def _extract_with_transformers(self, text: str, flat: bool) -> List[Dict]:
    """Extract entities using DistilBERT model"""
    inputs = self.tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        padding=True
    ).to(self.device)
    
    with torch.no_grad():
        outputs = self.model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_labels = torch.argmax(predictions, dim=-1)
    
    # Extract entities with confidence scores
    entities = []
    tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    
    for idx, (token, label_id, probs) in enumerate(zip(
        tokens, 
        predicted_labels[0], 
        predictions[0]
    )):
        if label_id != 0:  # Not 'O' (outside entity)
            entity_label = self.model.config.id2label[label_id.item()]
            confidence = probs[label_id].item()
            
            entities.append({
                "text": token,
                "label": entity_label,
                "start": idx,
                "end": idx + 1,
                "confidence": round(confidence, 4)
            })
    
    # Group consecutive entities if flat=False
    if not flat:
        entities = self._group_entities(entities)
    
    return entities
```

**Entity Grouping:**

The model can optionally group consecutive tokens into complete entities:

```python
def _group_entities(self, entities: List[Dict]) -> List[Dict]:
    """Group consecutive B- and I- tagged entities"""
    grouped = []
    current_entity = None
    
    for entity in entities:
        label = entity["label"]
        
        # Handle BIO tagging
        if label.startswith("B-"):
            # Start new entity
            if current_entity:
                grouped.append(current_entity)
            current_entity = entity.copy()
            current_entity["label"] = label[2:]  # Remove B- prefix
            
        elif label.startswith("I-") and current_entity:
            # Continue current entity
            current_entity["text"] += " " + entity["text"]
            current_entity["end"] = entity["end"]
            # Average confidence scores
            current_entity["confidence"] = (
                current_entity["confidence"] + entity["confidence"]
            ) / 2
        else:
            # Single token entity or O tag
            if current_entity:
                grouped.append(current_entity)
                current_entity = None
    
    if current_entity:
        grouped.append(current_entity)
    
    return grouped
```

### 2.5. Health Monitoring

The NER model integrates with the AI service health monitoring system (app/api/endpoints/health_routes.py):

**Model Status Endpoint:**

```python
@router.get("/health/models")
async def models_health():
    """Get detailed model status with dependency info"""
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

- **Ready:** Model loaded and available for entity extraction
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

**Health Check Example Response:**

```json
{
  "ready_models": ["ner", "translator", "classifier"],
  "details": {
    "ner": {
      "loaded": true,
      "device": "cuda",
      "hf_repo_id": "openchs/ner_distillbert_v1",
      "fallback_available": true,
      "fallback_model": "en_core_web_lg",
      "supported_entities": 9
    }
  }
}
```

### 2.6. Pipeline Integration

The NER model integrates into two processing modes:

#### Real-time Processing

For live calls, NER works progressively on translated text:

```python
# Progressive NER during active call
@router.get("/{call_id}/entities")
async def get_call_entities(call_id: str):
    """Get cumulative entities for active call"""
    analysis = progressive_processor.get_call_analysis(call_id)
    
    return {
        "call_id": call_id,
        "latest_entities": analysis.latest_entities,
        "entity_windows": len([w for w in analysis.windows if w.entities]),
        "high_confidence_entities": [
            e for e in analysis.latest_entities 
            if e["confidence"] > 0.85
        ]
    }
```

**Real-time Flow:**
1. Audio stream → Transcription → Translation (English)
2. Translated text → NER extraction
3. Entities (with confidence) → Classification
4. High-priority entities → Agent alerts

#### Post-call Processing

For completed calls, full pipeline execution:

```
Complete Transcript → Translation → NER → Entity Extraction
→ Classification → Summarization → Structured Report
```

**Configuration for Pipeline Modes:**

```python
# Settings control pipeline behavior
realtime_enable_ner: bool = True
postcall_enable_full_pipeline: bool = True
ner_confidence_threshold: float = 0.7  # Filter low-confidence entities
```

### 2.7. Memory Management

The NER model implements automatic GPU memory management:

```python
def _cleanup_memory(self):
    """Clean up GPU memory after extraction"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

# Cleanup occurs:
# - After each extraction request
# - During batch processing
# - Before fallback attempts
```

---

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The NER model is deployed as part of the AI Service and accessible via REST API.

#### Endpoint

```
POST /ner/extract
```

#### Request Format

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "string",
  "flat": true
}
```

**Parameters:**
- `text` (required, string): The input text to analyze for named entities
- `flat` (optional, boolean): Controls output format. If `true`, returns individual tokens; if `false`, groups consecutive entities. Default: `true`

#### Response Format

**Success Response (200):**
```json
{
  "entities": [
    {
      "text": "string",
      "label": "string",
      "start": 0,
      "end": 0,
      "confidence": 0.95
    }
  ],
  "processing_time": 0,
  "model_info": {
    "model_path": "string",
    "hf_repo_id": "openchs/ner_distillbert_v1",
    "device": "cuda",
    "loaded": true,
    "fallback_model_name": "en_core_web_lg",
    "use_hf": true
  },
  "timestamp": "string"
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

#### Example cURL Request

**Basic Entity Extraction:**
```bash
curl -X POST "https://your-api-domain.com/ner/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John reported an incident at Central Park. The victim was a 12-year-old girl. Contact number: 555-0123."
  }'
```

**Response:**
```json
{
  "entities": [
    {
      "text": "John",
      "label": "NAME",
      "start": 0,
      "end": 4,
      "confidence": 0.92
    },
    {
      "text": "Central Park",
      "label": "LANDMARK",
      "start": 30,
      "end": 42,
      "confidence": 0.88
    },
    {
      "text": "12-year-old",
      "label": "AGE",
      "start": 61,
      "end": 72,
      "confidence": 0.85
    },
    {
      "text": "girl",
      "label": "GENDER",
      "start": 73,
      "end": 77,
      "confidence": 0.79
    },
    {
      "text": "555-0123",
      "label": "PHONE_NUMBER",
      "start": 95,
      "end": 103,
      "confidence": 0.94
    }
  ],
  "processing_time": 0.156,
  "model_info": {
    "hf_repo_id": "openchs/ner_distillbert_v1",
    "device": "cuda",
    "loaded": true
  },
  "timestamp": "2025-10-17T15:45:30.123456"
}
```

**Grouped Entity Extraction:**
```bash
curl -X POST "https://your-api-domain.com/ner/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Maria Garcia lives in New York City and works at Children Hospital.",
    "flat": false
  }'
```

#### Getting NER Info

**Endpoint:**
```
GET /ner/info
```

**Response:**
```json
{
  "status": "ready",
  "model_info": {
    "hf_repo_id": "openchs/ner_distillbert_v1",
    "device": "cuda",
    "loaded": true,
    "fallback_available": true
  },
  "supported_entities": [
    "PERPETRATOR",
    "VICTIM",
    "NAME",
    "LOCATION",
    "LANDMARK",
    "PHONE_NUMBER",
    "GENDER",
    "AGE",
    "INCIDENT_TYPE"
  ]
}
```

#### Demo Endpoint

**Endpoint:**
```
POST /ner/demo
```

**Response:**
```json
{
  "sample_text": "John reported an incident at Central Park...",
  "entities": [...],
  "model_info": {...}
}
```

#### Features
- **Confidence Scoring:** Every entity includes a confidence score (0-1)
- **Flexible Output:** Flat or grouped entity formats
- **Fallback Support:** Automatic fallback to spaCy if transformer model unavailable
- **Real-time Processing:** Optimized for low-latency extraction

---

### 3.2. Via Hugging Face Hub

The model is publicly available on Hugging Face for direct inference and fine-tuning.

#### Model Repository
- **Organization:** [openchs](https://huggingface.co/openchs)
- **Model:** [openchs/ner_distillbert_v1](https://huggingface.co/openchs/ner_distillbert_v1)

#### Installation

```bash
pip install transformers torch
```

#### Inference Example

**Using Pipeline (Recommended):**
```python
from transformers import pipeline

# Load the NER pipeline
ner = pipeline(
    "ner",
    model="openchs/ner_distillbert_v1",
    aggregation_strategy="simple"
)

# Extract entities
text = "John reported an incident at Central Park. The victim was a 12-year-old girl."
entities = ner(text)

for entity in entities:
    print(f"{entity['word']} -> {entity['entity_group']} (confidence: {entity['score']:.2f})")
```

**Using Model and Tokenizer Directly:**
```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# Load model and tokenizer
model_name = "openchs/ner_distillbert_v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Prepare input
text = "Maria lives in Nairobi and called 0712345678 for help."
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

# Get predictions
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=-1)

# Decode predictions
tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
predicted_labels = [model.config.id2label[p.item()] for p in predictions[0]]

# Display results
for token, label in zip(tokens, predicted_labels):
    if label != "O":
        print(f"{token} -> {label}")
```

#### Batch Processing
```python
from transformers import pipeline

ner = pipeline("ner", model="openchs/ner_distillbert_v1")

texts = [
    "John reported abuse at school.",
    "The victim is a 10-year-old boy from Nairobi.",
    "Contact emergency services at 999."
]

results = ner(texts)

for text, entities in zip(texts, results):
    print(f"\nText: {text}")
    for entity in entities:
        print(f"  {entity['word']} -> {entity['entity']}")
```

**Note:** When using the model directly from Hugging Face, you'll need to implement your own entity grouping and post-processing logic. The AI Service API handles this automatically with the `flat` parameter.

---

## 4. Production Considerations

### Confidence Thresholds
- **High Priority Entities (PERPETRATOR, VICTIM):** Recommend threshold ≥ 0.8
- **Contact Information (PHONE_NUMBER):** Recommend threshold ≥ 0.85
- **General Entities (NAME, LOCATION):** Recommend threshold ≥ 0.7
- **Contextual Entities (AGE, GENDER):** Recommend threshold ≥ 0.6

### Processing Time
- **Short texts (< 50 tokens):** ~0.1-0.3 seconds
- **Medium texts (50-200 tokens):** ~0.3-0.8 seconds
- **Long texts (> 200 tokens):** ~0.8-1.5 seconds

Processing times vary based on:
- GPU availability (CUDA vs CPU)
- Text length and entity density
- Flat vs grouped output format
- System load

### Entity Extraction Strategy

**For Sensitive Content:**
1. **Initial Extraction:** Extract all entities with confidence scores
2. **Filtering:** Apply domain-specific confidence thresholds
3. **Validation:** Cross-reference high-priority entities (PERPETRATOR, VICTIM)
4. **Alerting:** Trigger alerts only for high-confidence critical entities

**For General Content:**
1. Use lower confidence thresholds
2. Accept more entity types
3. Apply post-processing validation

### Error Handling

**Common Error Scenarios:**

1. **Empty Input:**
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "Text input cannot be empty",
      "type": "value_error"
    }
  ]
}
```

2. **Model Not Ready:**
```json
{
  "detail": "NER model not ready. Check /health/models for status."
}
```

3. **Service Unavailable:**
```json
{
  "detail": "NER model not loaded"
}
```

### Health Checks

Monitor NER service health:

```bash
# Check if NER is ready
curl -X GET "https://your-api-domain.com/health/models"

# Get detailed system status
curl -X GET "https://your-api-domain.com/health/detailed"

# Test with demo endpoint
curl -X POST "https://your-api-domain.com/ner/demo"
```

---

## 5. Model Limitations

### Domain Specificity
- **Optimized for:** Child protection conversations, abuse reporting, helpline transcripts
- **May require adaptation for:** General NER tasks, formal documents, non-English text
- **Performance varies on:** Out-of-distribution data, highly technical terminology

### Technical Constraints
- **Maximum Context:** 512 tokens (DistilBERT limit)
- **Memory Requirements:** GPU recommended for production (CPU fallback available)
- **Processing Speed:** Dependent on hardware and text complexity

### Known Considerations
- **Entity Ambiguity:** Some names may be misclassified (e.g., NAME vs PERPETRATOR)
- **Context Dependency:** Entity types depend on surrounding context
- **Overlapping Entities:** Model may struggle with entities spanning multiple categories
- **Code-Switching:** Mixed-language text may reduce accuracy

### Recommendations
- Monitor confidence scores and adjust thresholds based on your use case
- Use health check endpoints to verify model readiness before critical operations
- Implement entity validation for high-stakes scenarios (e.g., perpetrator identification)
- Consider human review for entities with confidence scores below 0.8 in sensitive contexts
- Review extractions for false positives in PERPETRATOR and VICTIM categories

---

## 6. Citation

If you use this model in your research or application, please cite:

```bibtex
@misc{ner_distillbert_1,
  title={ner_distillbert},
  author={BITZ-AI TEAM},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/openchs/ner_distillbert_v1}
}
```

---

## 7. Support and Contact

### Issues and Questions
- **Email:** info@bitz-itc.com
- **Hugging Face:** [openchs organization](https://huggingface.co/openchs)

### Contributing
For dataset contributions, model improvements, or bug reports, please contact the BITZ AI Team at info@bitz-itc.com.

---

## 8. License

This model is released under the **Apache 2.0 License**, allowing for both commercial and non-commercial use with proper attribution.

---
