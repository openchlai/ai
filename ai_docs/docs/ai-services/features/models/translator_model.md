# Translator Model Documentation

## 1. Model Overview

The **opus-mt-sw-en-finetuned** translation model is a MarianMT-based sequence-to-sequence model fine-tuned for **Swahili-to-English translation** in the context of child helpline services. This model is specifically trained on conversations from the **116 Child Helpline in Tanzania**, making it domain-specific for sensitive topics including abuse reporting, emergency situations, emotional distress, and general child welfare inquiries.

### Key Features
- **Architecture:** Helsinki-NLP/opus-mt-mul-en (MarianMT)
- **Domain:** Child helpline conversations
- **Deployment:** Available via AI Service API and Hugging Face Hub
- **Repository:** openchs/sw-en-opus-mt-mul-en-v1
- **Special Capabilities:** Handles code-switching, fragmented trauma narratives, emergency language, and emotional distress expressions

### Integration in AI Service Pipeline
The translation model is a core component of the BITZ AI Service pipeline:

```
Audio Input → Transcription Model → Swahili Text → Translation Model → English Text → NER/Classification/Summarization
```

The model receives Swahili transcripts from the transcription model and outputs English translations for downstream processing by Named Entity Recognition, classification, and other analysis components.

---

## 2. Integration in AI Service Architecture

The translation model is deeply integrated into the AI service through multiple layers:

### 2.1. Configuration Layer

The translation model is configured through the central settings system (`app/config/settings.py`):

```python
class Settings(BaseSettings):
    # Hugging Face configuration
    hf_token: Optional[str] = None  # No token needed for public models
    translation_hf_repo_id: Optional[str] = "openchs/sw-en-opus-mt-mul-en-v1"
    hf_translator_model: str = "openchs/sw-en-opus-mt-mul-en-v1"
    
    # Model paths
    models_path: str = "./models"  # Auto-adjusted for Docker
    
    # Enable HuggingFace models
    use_hf_models: bool = True
```

**Configuration Helper Methods:**

```python
def get_translator_model_id(self) -> str:
    """Return the HuggingFace translator model id from configuration"""
    if self.hf_translator_model:
        return self.hf_translator_model
    return self._get_hf_model_id("translator")

def translation_backend(self, include_translation: bool) -> str:
    """Decide which backend should perform translation"""
    if not include_translation:
        return "none"
    if self.use_hf_models and self.hf_translator_model:
        return "hf"
    return "whisper"  # Fallback to Whisper built-in

def resolve_translation_target(self, include_translation: bool) -> Dict[str, str]:
    """Resolve and return the translation target information"""
    backend = self.translation_backend(include_translation)
    if backend == "hf":
        return {"backend": "hf", "model": self.get_translator_model_id()}
    if backend == "whisper":
        return {"backend": "whisper", "model": self.whisper_model_variant}
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

The translation model is loaded through the `TranslationModel` class during FastAPI application startup:

```python
class TranslationModel:
    """Translation model with intelligent chunking support"""
    
    def __init__(self, model_path: str = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        self.max_length = 512  # Model's maximum token limit
        
        # Hugging Face repo support
        self.hf_repo_id = settings.translation_hf_repo_id
        
    def load(self) -> bool:
        """Load model from Hugging Face Hub"""
        try:
            logger.info(f"Loading translation model from HF Hub: {self.hf_repo_id}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.hf_repo_id, 
                local_files_only=False
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.hf_repo_id, 
                local_files_only=False
            )
            
            self.model.to(self.device)
            self.loaded = True
            
            logger.info(f" Translation model loaded on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to load translation model: {e}")
            return False
```

**Model Loader Integration:**

The translation model is managed by the central `model_loader` which handles:
- Startup initialization
- Readiness checks
- Dependency tracking
- Health monitoring

```python
# During FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize translation model via model_loader
    model_loader.load_model("translator")
    yield
    # Cleanup on shutdown
```

### 2.3. API Endpoints Layer

Translation functionality is exposed through FastAPI routes (`app/api/endpoints/translator_routes.py`):

```python
router = APIRouter(prefix="/translate", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    translated: str
    processing_time: float
    model_info: Dict
    timestamp: str

@router.post("/", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text with automatic chunking for long inputs"""
    
    # Check model readiness
    if not model_loader.is_model_ready("translator"):
        raise HTTPException(
            status_code=503,
            detail="Translation model not ready. Check /health/models for status."
        )
    
    # Validate input
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )
    
    # Get translator model
    translator_model = model_loader.models.get("translator")
    
    # Initialize chunker
    tokenizer_name = "openchs/sw-en-opus-mt-mul-en-v1"
    chunker = TranslationChunker(
        tokenizer_name=tokenizer_name,
        max_tokens=512
    )
    
    # Count tokens and decide on chunking
    token_count = chunker.count_tokens(request.text)
    MAX_SOURCE_LENGTH = 512
    
    if token_count <= MAX_SOURCE_LENGTH:
        # Direct translation for short text
        translated = translator_model.translate(request.text)
    else:
        # Chunking needed for long text
        chunks = chunker.chunk_transcript(request.text)
        
        # Translate each chunk
        translated_chunks = []
        for chunk_info in chunks:
            chunk_translated = translator_model.translate(chunk_info['text'])
            translated_chunks.append(chunk_translated)
        
        # Reconstruct final translation
        translated = chunker.reconstruct_translation(translated_chunks)
    
    return TranslationResponse(
        translated=translated,
        processing_time=processing_time,
        model_info=translator_model.get_model_info(),
        timestamp=datetime.now().isoformat()
    )
```

**Information Endpoint:**

```python
@router.get("/info")
async def get_translation_info():
    """Get translation service information"""
    if not model_loader.is_model_ready("translator"):
        return {
            "status": "not_ready",
            "message": "Translation model not loaded"
        }
    
    translator_model = model_loader.models.get("translator")
    return {
        "status": "ready",
        "model_info": translator_model.get_model_info()
    }
```

### 2.4. Translation Chunking Strategy

The `TranslationChunker` utility handles automatic segmentation of long texts to respect the model's 512-token limit:

**Why Chunking is Needed:**
- MarianMT models have a maximum context length of 512 tokens
- Long helpline conversations often exceed this limit
- Direct truncation would lose critical information
- Chunking with overlap preserves context across segments

**Chunking Implementation:**

```python
class TranslationChunker:
    """Utility for chunking long texts for translation"""
    
    def __init__(self, tokenizer_name: str, max_tokens: int = 512):
        self.tokenizer_name = tokenizer_name
        self.max_tokens = max_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text, add_special_tokens=True))
    
    def chunk_transcript(self, text: str, segment_length: int = 450, 
                        overlap: int = 50) -> List[Dict]:
        """
        Create overlapping chunks from text
        
        Args:
            text: Input text to chunk
            segment_length: Target tokens per segment (default: 450)
            overlap: Token overlap between segments (default: 50)
            
        Returns:
            List of chunk dictionaries with 'text' and 'tokens' keys
        """
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + segment_length, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            
            chunks.append({
                'text': chunk_text,
                'tokens': len(chunk_tokens)
            })
            
            # Move start forward, accounting for overlap
            start = end - overlap if end < len(tokens) else end
        
        return chunks
    
    def reconstruct_translation(self, translated_chunks: List[str]) -> str:
        """
        Reconstruct complete translation from chunks
        
        Args:
            translated_chunks: List of translated chunk strings
            
        Returns:
            Combined translation as single string
        """
        return " ".join(chunk.strip() for chunk in translated_chunks if chunk.strip())
```

**Chunking Process Flow:**

1. **Token Counting:** Count tokens in input text
2. **Decision:** If ≤ 512 tokens → direct translation; if > 512 → chunking
3. **Segmentation:** Split into 450-token segments with 50-token overlap
4. **Translation:** Translate each chunk independently
5. **Reconstruction:** Combine translated chunks with intelligent spacing

**Overlap Strategy:**

The 50-token overlap between chunks ensures:
- Context preservation across segment boundaries
- Better handling of sentence splits
- Improved translation quality for long conversations

### 2.5. Health Monitoring

The translation model integrates with the AI service health monitoring system (`app/api/endpoints/health_routes.py`):

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

- **Ready:** Model loaded and available for translation
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

**Health Check Example Response:**

```json
{
  "ready_models": ["translator", "classifier", "ner"],
  "implementable_models": [],
  "blocked_models": [],
  "details": {
    "translator": {
      "loaded": true,
      "device": "cuda",
      "hf_repo_id": "openchs/sw-en-opus-mt-mul-en-v1",
      "max_length": 512,
      "chunking_supported": true
    }
  }
}
```

### 2.6. Pipeline Integration

The translation model integrates into two processing modes:

#### Real-time Processing

For live calls, translation works progressively:

```python
# Progressive translation during active call
@router.get("/{call_id}/translation")
async def get_call_translation(call_id: str):
    """Get cumulative translation for active call"""
    analysis = progressive_processor.get_call_analysis(call_id)
    
    return {
        "call_id": call_id,
        "cumulative_translation": analysis.cumulative_translation,
        "translation_windows": len([w for w in analysis.windows if w.translation]),
        "latest_entities": analysis.latest_entities,
        "latest_classification": analysis.latest_classification
    }
```

**Real-time Flow:**
1. Audio stream → Whisper transcription (Swahili)
2. Transcript chunks → Translation (English)
3. Translated text → NER extraction
4. Entities + classification → Agent notifications

#### Post-call Processing

For completed calls, full pipeline execution:

```python
# Complete pipeline after call ends
Audio File → Transcription (full) → Translation (chunked if needed) 
→ NER → Classification → Summarization → Insights
```

**Configuration for Pipeline Modes:**

```python
# Settings control pipeline behavior
realtime_enable_progressive_translation: bool = True
postcall_enable_full_pipeline: bool = True
```

### 2.7. Memory Management

The translation model implements automatic GPU memory management:

```python
def _cleanup_memory(self):
    """Clean up GPU memory after translation"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

# Cleanup occurs:
# - After each translation request
# - Every 5 chunks during long translations
# - Before retry attempts
```

---

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The translation model is deployed as part of the AI Service and accessible via REST API. The API uses an **asynchronous task-based architecture** where translation requests are queued and processed by Celery workers, allowing the system to handle resource-intensive translation without blocking HTTP connections.

#### Workflow Overview

The translation API follows a **2-step asynchronous workflow**:

1. **Submit Translation Request** → Receive `task_id` (HTTP 202 Accepted)
2. **Poll Task Status** → Retrieve translation results when ready (HTTP 200 OK)

This architecture ensures reliable processing of long texts and prevents timeout issues during GPU-intensive translation operations.

---

#### Step 1: Submit Translation Task

**Endpoint:**
```
POST /translate/
```

**Request Format:**

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "string"
}
```

**Request Fields:**
- `text` (required, string): The Swahili text to be translated to English

**Success Response (HTTP 202 Accepted):**
```json
{
  "task_id": "task_trans_a1b2c3d4e5f6",
  "status": "queued",
  "message": "Translation started. Check status at /translate/task/{task_id}",
  "estimated_time": "5-20 seconds",
  "status_endpoint": "/translate/task/task_trans_a1b2c3d4e5f6"
}
```

**Response Fields:**
- `task_id` (string): Unique identifier for tracking the translation task
- `status` (string): Initial task state (`"queued"` or `"processing"`)
- `message` (string): Human-readable confirmation message
- `estimated_time` (string): Expected processing duration
- `status_endpoint` (string): URL path for polling task status

---

#### Step 2: Poll Translation Status

**Endpoint:**
```
GET /translate/task/{task_id}
```

**Response States:**

**1. Pending (HTTP 200 OK):**
```json
{
  "task_id": "task_trans_a1b2c3d4e5f6",
  "status": "pending",
  "progress": {
    "message": "Task is queued"
  }
}
```

**2. Processing (HTTP 200 OK):**
```json
{
  "task_id": "task_trans_a1b2c3d4e5f6",
  "status": "processing",
  "progress": {
    "message": "Translation in progress..."
  }
}
```

**3. Completed Successfully (HTTP 200 OK):**
```json
{
  "task_id": "task_trans_a1b2c3d4e5f6",
  "status": "success",
  "result": {
    "translated": "Children need help urgently. There is a big problem here.",
    "processing_time": 1.23,
    "model_info": {
      "model_path": "./models/translation",
      "hf_repo_id": "openchs/sw-en-opus-mt-mul-en-v1",
      "device": "cuda",
      "loaded": true,
      "max_length": 512,
      "chunking_supported": true
    },
    "timestamp": "2025-10-15T10:30:45.123456"
  }
}
```

**4. Failed (HTTP 200 OK with error details):**
```json
{
  "task_id": "task_trans_a1b2c3d4e5f6",
  "status": "failed",
  "error": "Translation failed due to invalid input format"
}
```

---

#### cURL Examples

**Step 1: Submit Translation Task**
```bash
curl -X POST "https://your-api-domain.com/translate/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Watoto wanahitaji msaada wa haraka. Kuna tatizo kubwa hapa."
  }'
```

**Response:**
```json
{
  "task_id": "task_trans_a1b2c3d4e5f6",
  "status": "queued",
  "message": "Translation started. Check status at /translate/task/{task_id}",
  "estimated_time": "5-20 seconds",
  "status_endpoint": "/translate/task/task_trans_a1b2c3d4e5f6"
}
```

**Step 2: Poll for Results**
```bash
curl -X GET "https://your-api-domain.com/translate/task/task_trans_a1b2c3d4e5f6"
```

---

#### Python Client Example

```python
import requests
import time
from typing import Dict

class TranslatorClient:
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def translate(self, text: str) -> Dict:
        """
        Submit translation request and wait for results.

        Args:
            text: Swahili text to be translated

        Returns:
            Translation results dictionary

        Raises:
            ValueError: For validation errors (400)
            RuntimeError: For server errors
        """
        # Step 1: Submit task
        response = requests.post(
            f"{self.base_url}/translate/",
            json={"text": text},
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
                f"{self.base_url}/translate/task/{task_id}",
                timeout=10
            )
            response.raise_for_status()

            task_status = response.json()

            if task_status["status"] == "success":
                return task_status["result"]
            elif task_status["status"] == "failed":
                raise RuntimeError(f"Translation failed: {task_status.get('error', 'Unknown error')}")

            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, 3.0)

        raise TimeoutError(f"Translation did not complete within {self.timeout} seconds")

# Usage example
client = TranslatorClient("https://your-api-domain.com")

try:
    result = client.translate(
        text="Watoto wanahitaji msaada wa haraka. Kuna tatizo kubwa hapa."
    )

    print(f"Translated: {result['translated']}")
    print(f"Processing time: {result['processing_time']:.2f}s")

except Exception as e:
    print(f"Error: {e}")
```

---

#### Getting Translation Info

**Endpoint:**
```
GET /translate/info
```

**Response:**
```json
{
  "status": "api_server_mode",
  "message": "Translation model available on Celery workers",
  "mode": "api_server",
  "model_info": {
    "name": "Translation Model",
    "location": "celery_workers",
    "note": "Model loaded on worker nodes"
  }
}
```

#### Demo Endpoint

For a quick demonstration of the translation capabilities, you can use the demo endpoint.

- **Endpoint:** `POST /translate/demo`
- **Description:** Runs a demo of the translation model with a sample text.
- **Response:**
  - A `TaskResponse` object with details about the enqueued demo task.

**Example `curl` command:**

```bash
curl -X POST "http://192.168.10.6:8125/translate/demo"
```

---

#### Features
- **Automatic Chunking:** Long inputs are automatically chunked to handle conversations without truncation
- **Segment Processing:** Configured with 450 max tokens per segment with 50 token overlap
- **Intelligent Reconstruction:** Translated chunks are combined with proper spacing and punctuation handling
- **GPU Memory Management:** Automatic cleanup between requests and during long translations
- **Async Processing:** Non-blocking task-based architecture via Celery workers

---

### 3.2. Via Hugging Face Hub

The model is publicly available on Hugging Face for direct inference and fine-tuning.

#### Model Repository
- **Organization:** [openchs](https://huggingface.co/openchs)
- **Model:** [openchs/sw-en-opus-mt-mul-en-v1](https://huggingface.co/openchs/sw-en-opus-mt-mul-en-v1)

#### Installation

```bash
pip install transformers torch
```

#### Inference Example

**Using Pipeline (Recommended):**
```python
from transformers import pipeline

# Load the translation pipeline
translator = pipeline(
    "translation",
    model="openchs/sw-en-opus-mt-mul-en-v1"
)

# Translate Swahili to English
text = "Ninajisikia vibaya sana. Nahitaji mtu wa kuongea naye."
result = translator(text)

print(result[0]["translation_text"])
# Output: "I feel very bad. I need someone to talk to."
```

**Using Model and Tokenizer Directly:**
```python
from transformers import MarianMTModel, MarianTokenizer

# Load model and tokenizer
model_name = "openchs/sw-en-opus-mt-mul-en-v1"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Prepare input
text = ["Mtoto wangu amepotea. Tafadhali nisaidieni."]
inputs = tokenizer(text, return_tensors="pt", padding=True)

# Generate translation
translated = model.generate(**inputs)
output = tokenizer.decode(translated[0], skip_special_tokens=True)

print(output)
# Output: "My child is missing. Please help me."
```

#### Batch Translation
```python
from transformers import pipeline

translator = pipeline(
    "translation",
    model="openchs/sw-en-opus-mt-mul-en-v1"
)

texts = [
    "Habari za asubuhi",
    "Ninahitaji usaidizi",
    "Je, mnaweza kunisaidia?"
]

results = translator(texts)

for original, result in zip(texts, results):
    print(f"{original} → {result['translation_text']}")
```

**Note:** When using the model directly from Hugging Face, you'll need to implement your own chunking logic for texts longer than 512 tokens. The AI Service API handles this automatically.

---

## 4. Production Considerations

### Token Limits
- **Maximum Input Length:** 512 tokens
- **Segment Size:** 450 tokens per segment (for automatic chunking)
- **Segment Overlap:** 50 tokens between segments

### Processing Time
- **Short texts (< 50 tokens):** ~0.5-1.0 seconds
- **Medium texts (50-200 tokens):** ~1.0-2.5 seconds
- **Long texts (> 200 tokens):** ~2.5-5.0 seconds (with chunking)

Processing times vary based on:
- GPU availability (CUDA vs CPU)
- Text length and complexity
- Number of chunks required
- System load

### Automatic Chunking
The API automatically handles long conversations by:
1. **Token Counting:** Checking if input exceeds 512 tokens
2. **Segmentation:** Creating 450-token chunks with 50-token overlap
3. **Translation:** Processing each segment independently
4. **Reconstruction:** Combining translations with intelligent spacing

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
  "detail": "Translation model not ready. Check /health/models for status."
}
```

3. **Service Unavailable:**
```json
{
  "detail": "Translator model not available"
}
```

### Health Checks

Monitor translation service health:

```bash
# Check if translator is ready
curl -X GET "https://your-api-domain.com/health/models"

# Get detailed system status
curl -X GET "https://your-api-domain.com/health/detailed"
```

---

## 5. Model Limitations

### Domain Specificity
- **Optimized for:** Child helpline conversations, emotional support language, emergency situations
- **May require adaptation for:** General Swahili-English translation, formal documents, technical content
- **Performance varies on:** Out-of-distribution data, highly specialized terminology

### Technical Constraints
- **Maximum Context:** 512 tokens (handled automatically via chunking)
- **Memory Requirements:** GPU recommended for production (CPU fallback available)
- **Processing Speed:** Dependent on hardware and text length

### Known Considerations
- **Code-Switching:** While generally successful, complex code-switching patterns may reduce accuracy
- **Cultural Context:** Some culturally-specific Tanzanian expressions may not translate perfectly
- **Long Conversations:** Chunking may occasionally affect cohesion across segment boundaries

### Recommendations
- Monitor translation quality for edge cases in your domain
- Use health check endpoints to verify model readiness before critical operations
- Consider implementing translation quality feedback loops
- Review translations for sensitive or critical content

---

## 6. Citation

If you use this model in your research or application, please cite:

```bibtex
@misc{opus_mt_sw_en_finetuned,
  title={opus-mt-sw-en-finetuned},
  author={OpenCHS Team},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/openchs/sw-en-opus-mt-mul-en-v1}
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
