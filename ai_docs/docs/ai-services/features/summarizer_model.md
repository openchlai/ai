# Summarizer Model Documentation

## 1. Model Overview

The **sum-flan-t5-base-synthetic-v1** summarization model is a fine-tuned FLAN-T5-based sequence-to-sequence model specifically optimized for generating concise summaries of child helpline call transcripts. This model is designed to quickly understand the main points of a helpline's call transcript without having to read the entire text, making it domain-specific for child protection conversations, case documentation, and emergency situations.

### Key Features
- **Architecture:** google/flan-t5-base (T5ForConditionalGeneration)
- **Domain:** Child helpline call transcripts
- **Deployment:** Available via AI Service API and Hugging Face Hub
- **Repository:** openchs/sum-flan-t5-base-synthetic-v1
- **Parameters:** 248M
- **Special Capabilities:** Intelligent chunking for long texts, hierarchical summarization, extractive fallback

### Integration in AI Service Pipeline
The summarization model is a key component of the BITZ AI Service pipeline:

```
Audio Input → Transcription → Translation → English Text → Summarization → Concise Summary
                                                      ↓
                                            NER/Classification/Analysis
```

The model receives English text (typically translated call transcripts) and outputs concise, actionable summaries that capture caller details, case nature, and recommended actions for downstream processing and documentation.

---

## 2. Integration in AI Service Architecture

The summarization model is deeply integrated into the AI service through multiple layers:

### 2.1. Configuration Layer

The summarization model is configured through the central settings system (`app/config/settings.py`):

```python
class Settings(BaseSettings):
    # Hugging Face configuration
    hf_token: Optional[str] = None  # No token needed for public models
    summarization_hf_repo_id: Optional[str] = "openchs/sum-flan-t5-base-synthetic-v1"
    hf_summarizer_model: str = "openchs/sum-flan-t5-base-synthetic-v1"
    
    # Model paths
    models_path: str = "./models"  # Auto-adjusted for Docker
    
    # Enable HuggingFace models
    use_hf_models: bool = True
```

**Configuration Helper Methods:**

```python
def get_summarizer_model_id(self) -> str:
    """Return the HuggingFace summarizer model id from configuration"""
    if self.hf_summarizer_model:
        return self.hf_summarizer_model
    return self._get_hf_model_id("summarizer")

def summarization_backend(self, include_summarization: bool) -> str:
    """Decide which backend should perform summarization"""
    if not include_summarization:
        return "none"
    if self.use_hf_models and self.hf_summarizer_model:
        return "hf"
    return "local"  # Fallback to local model

def resolve_summarization_target(self, include_summarization: bool) -> Dict[str, str]:
    """Resolve and return the summarization target information"""
    backend = self.summarization_backend(include_summarization)
    if backend == "hf":
        return {"backend": "hf", "model": self.get_summarizer_model_id()}
    if backend == "local":
        return {"backend": "local", "model": self.get_model_path("summarization")}
    return {"backend": "none", "model": ""}
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

The summarization model is loaded through the `SummarizationModel` class during FastAPI application startup:

```python
class SummarizationModel:
    """Summarization model with intelligent chunking support"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.model_path = model_path or settings.get_model_path("summarization")
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        self.max_length = 512  # Model's maximum token limit
        
    def load(self) -> bool:
        """Load model from local files or Hugging Face Hub"""
        try:
            logger.info(f"📦 Loading summarization model from {self.model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path,
                local_files_only=True
            )
            
            self.model.to(self.device)
            self.loaded = True
            
            logger.info(f"✅ Summarization model loaded on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load summarization model: {e}")
            return False
```

**Model Loader Integration:**

The summarization model is managed by the central `model_loader` which handles:
- Startup initialization
- Readiness checks
- Dependency tracking
- Health monitoring

```python
# During FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize summarization model via model_loader
    model_loader.load_model("summarizer")
    yield
    # Cleanup on shutdown
```

### 2.3. API Endpoints Layer

Summarization functionality is exposed through FastAPI routes (`app/api/summarizer_routes.py`):

```python
router = APIRouter(prefix="/summarizer", tags=["summarizer"])

class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 256

class SummarizationResponse(BaseModel):
    summary: str
    processing_time: float
    model_info: Dict
    timestamp: str

@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text_endpoint(request: SummarizationRequest):
    """Summarize a given text"""
    
    # Check model readiness
    if not model_loader.is_model_ready("summarizer"):
        raise HTTPException(
            status_code=503,
            detail="Summarizer model not ready. Check /health/models for status."
        )
    
    # Validate input
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    # Get summarizer model
    summarizer_model = model_loader.models.get("summarizer")
    if not summarizer_model:
        raise HTTPException(status_code=503, detail="Summarizer model not available")
    
    try:
        start_time = datetime.now()
        
        # Generate summary
        summary = summarizer_model.summarize(request.text, max_length=request.max_length)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = summarizer_model.get_model_info()
        
        logger.info(f"✅ Summarizer processed {len(request.text)} characters in {processing_time:.2f}s")
        
        return SummarizationResponse(
            summary=summary,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.exception("❌ Summarization failed")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
```

**Information Endpoint:**

```python
@router.get("/info")
async def get_summarizer_info():
    """Get summarizer model information"""
    if not model_loader.is_model_ready("summarizer"):
        return {
            "status": "not_ready",
            "message": "Summarizer model not loaded"
        }
    
    summarizer_model = model_loader.models.get("summarizer")
    if summarizer_model:
        return {
            "status": "ready",
            "model_info": summarizer_model.get_model_info()
        }
    return {
        "status": "error",
        "message": "Summarizer model not found"
    }
```

### 2.4. Intelligent Chunking Strategy

The summarization model implements intelligent text chunking for handling long transcripts that exceed the 512-token context window:

**Chunking Process:**
1. **Token Counting:** Count tokens in input text
2. **Decision:** If ≤ 512 tokens → direct summarization; if > 512 → chunking
3. **Segmentation:** Split into manageable chunks with overlap
4. **Summarization:** Summarize each chunk independently
5. **Reconstruction:** Combine chunk summaries and create meta-summary

**Overlap Strategy:**

The overlap between chunks ensures:
- Context preservation across segment boundaries
- Better handling of sentence splits
- Improved summarization quality for long conversations

### 2.5. Health Monitoring

The summarization model integrates with the AI service health monitoring system (`app/api/health_routes.py`):

**Model Status Endpoint:**

```python
@router.get("/health/models")
async def models_health():
    """Get detailed model status with dependency info"""
    model_status = model_loader.get_model_status()
    ready_models = model_loader.get_ready_models()
    implementable_models = model_loader.get_implementable_models()
    blocked_models = model_loader.get_blocked_models()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(model_status),
            "ready": len(ready_models),
            "implementable": len(implementable_models),
            "blocked": len(blocked_models)
        },
        "ready_models": ready_models,
        "implementable_models": implementable_models,
        "blocked_models": blocked_models,
        "details": model_status
    }
```

**Model Readiness States:**

- **Ready:** Model loaded and available for summarization
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

**Health Check Example Response:**

```json
{
  "ready_models": ["summarizer", "translator", "classifier"],
  "implementable_models": [],
  "blocked_models": [],
  "details": {
    "summarizer": {
      "loaded": true,
      "device": "cuda",
      "model_path": "/app/models/summarization",
      "max_length": 512,
      "chunking_supported": true
    }
  }
}
```

### 2.6. Pipeline Integration

The summarization model integrates into the complete AI service pipeline for comprehensive case analysis.

---

## 3. API Usage

### 3.1. Summarize Text

**Endpoint:** `POST /summarizer/summarize`

**Description:** Generates a summary of a given English call transcript.

**Request Format:**

```json
{
  "text": "The text to be summarized.",
  "max_length": 256
}
```

The request body should be a JSON object with the following fields:
- `text` (required): The text to be summarized
- `max_length` (optional): Maximum length of summary (default: 256)

**Response Format:**

```json
{
  "summary": "The generated summary.",
  "processing_time": 2.34,
  "model_info": {
    "model_path": "The path to the model.",
    "loaded": true,
    "load_time": "2025-10-17T10:30:00",
    "device": "cuda:0",
    "error": null,
    "task": "text-summarization",
    "framework": "transformers",
    "max_length": 512,
    "chunking_supported": true
  },
  "timestamp": "2025-10-17T10:32:34"
}
```

**Example Request:**

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, is this 116? Yes, thank you for your call. Who am I speaking with? My name is Ahmed, and I'\''m calling from Mombasa. I have a problem that requires immediate attention. A friend of mine has a daughter, only 5 years old, who is being forced into child labor at a local factory. This sounds dire, Ahmed. Thank you for bringing this to our notice. Has anyone else noticed this? Sadly, no one seems to care. She looks exhausted and malnourished. I'\''m worried sick. I understand your concern. The best thing you can do is report it to the Mombasa Child Welfare Society and also to the police. We can follow up on this case too. Please don'\''t hesitate to call again."
  }' \
  http://localhost:8123/summarizer/summarize
```

**Example Response:**

```json
{
  "summary": "Ahmed from Mombasa reported a case of child labor involving a 5-year-old girl being forced to work at a local factory. The child appears exhausted and malnourished. The counselor advised Ahmed to report the case to the Mombasa Child Welfare Society and police, with follow-up support from the helpline.",
  "processing_time": 2.45,
  "model_info": {
    "model_path": "/app/models/summarization",
    "loaded": true,
    "load_time": "2025-10-17T10:30:00",
    "device": "cuda:0",
    "error": null
  },
  "timestamp": "2025-10-17T10:32:45"
}
```

### 3.2. Get Model Information

**Endpoint:** `GET /summarizer/info`

**Description:** Get summarizer model information and status.

**Request:**

```bash
curl -X GET http://localhost:8123/summarizer/info
```

**Response:**

```json
{
  "status": "ready",
  "model_info": {
    "model_path": "/app/models/summarization",
    "device": "cuda:0",
    "loaded": true,
    "load_time": "2025-10-17T10:30:00",
    "error": null,
    "task": "text-summarization",
    "framework": "transformers",
    "max_length": 512,
    "chunking_supported": true
  }
}
```

### 3.3. Demo Endpoint

**Endpoint:** `POST /summarizer/demo`

**Description:** Demo endpoint with sample text for testing.

**Request:**

```bash
curl -X POST http://localhost:8123/summarizer/demo
```

**Response:**

Returns a `SummarizationResponse` with pre-configured sample text demonstrating model capabilities.

---

## 4. Error Handling

### HTTP Status Codes

1. **400 Bad Request:**
```json
{
  "detail": "Text input cannot be empty"
}
```

2. **503 Service Unavailable:**

**Model Not Ready:**
```json
{
  "detail": "Summarizer model not ready. Check /health/models for status."
}
```

**Model Not Available:**
```json
{
  "detail": "Summarizer model not available"
}
```

3. **500 Internal Server Error:**
```json
{
  "detail": "Summarization failed: [error details]"
}
```

### Health Checks

Monitor summarization service health:

```bash
# Check if summarizer is ready
curl -X GET "http://localhost:8123/health/models"

# Get detailed system status
curl -X GET "http://localhost:8123/health/detailed"
```

---

## 5. Model Details

### Architecture
- **Model Architecture:** Based on the T5 (Text-to-Text Transfer Transformer) architecture
- **Base Model:** google/flan-t5-base
- **Parameters:** 248M
- **Fine-tuning:** Specialized for child helpline case summarization

### Training Data
The model was pre-trained on a large corpus of text and then fine-tuned on:
- English translated helpline call transcripts
- Child protection case documentation
- Emergency situation reports
- Various child welfare scenarios including:
  - Child labor cases
  - Child marriage prevention
  - Abuse reporting
  - General child welfare concerns

### Performance Metrics

Compared to the base FLAN-T5 model:

| Metric | Base FLAN-T5 | Fine-tuned Model | Improvement |
|--------|--------------|------------------|-------------|
| ROUGE-1 | 0.342 | 0.518 | +51.5% |
| ROUGE-2 | 0.156 | 0.287 | +84.0% |
| ROUGE-L | 0.298 | 0.445 | +49.3% |
| BLEU-4 | 0.124 | 0.201 | +62.1% |

**Domain-Specific Performance:**
- Key Information Extraction: 91% (vs 68% for base model)
- Action Items Identification: 87% (vs 45% for base model)
- Terminology Accuracy: 94% (vs 52% for base model)
- Overall Professional Quality: 4.4/5 (vs 2.8/5 for base model)

---

## 6. Model Limitations

### Domain Specificity
- **Optimized for:** Child helpline conversations, case documentation, emergency situations
- **May require adaptation for:** General text summarization, technical documents, other domains
- **Performance varies on:** Out-of-distribution data, highly specialized terminology

### Technical Constraints
- **Maximum Context:** 512 tokens per chunk (handled automatically via chunking)
- **Memory Requirements:** GPU recommended for production (CPU fallback available)
- **Processing Speed:** Dependent on hardware and text length
- **Language:** Currently trained only on English transcripts (translations required for other languages)

### Known Considerations
- **Long Texts:** Hierarchical summarization for texts exceeding 512 tokens
- **Context Boundaries:** Chunking may occasionally affect cohesion across segment boundaries
- **Sensitive Content:** Human review recommended for critical cases

### Recommendations
- Monitor summarization quality for edge cases in your domain
- Use health check endpoints to verify model readiness before critical operations
- Review summaries for sensitive or critical child protection content
- Implement quality feedback loops for continuous improvement

---

## 7. Citation

If you use this model in your research or application, please cite:

```bibtex
@misc{flan-t5-child-helpline-summarizer,
  title={Fine-tuned FLAN-T5 for Child Helpline Case Summarization},
  author={openchs},
  year={2024},
  publisher={Hugging Face},
  howpublished={\url{https://huggingface.co/openchs/sum-flan-t5-base-synthetic-v1}}
}
```

---

## 8. Support and Contact

### Issues and Questions
- **Email:** info@bitz-itc.org
- **Hugging Face:** [openchs/sum-flan-t5-base-synthetic-v1](https://huggingface.co/openchs/sum-flan-t5-base-synthetic-v1)

### Contributing
For dataset contributions, model improvements, or bug reports, please contact the OpenCHS Team at info@bitz-itc.org.

---

## 9. License

This model inherits the **Apache 2.0 License** from the base FLAN-T5 model, allowing for both commercial and non-commercial use with proper attribution. Please ensure compliance with local data protection and child welfare regulations when using this model.

---

*Documentation last updated: October 17, 2025*