# Whisper Transcription Model Documentation

## 1. Model Overview

The **openchs/asr-whisper-helpline-sw-v1** transcription model is a Whisper large-v2 based automatic speech recognition (ASR) model fine-tuned for **Swahili transcription and translation** in the context of child helpline services. This model is specifically trained on conversations from the **116 Child Helpline in Tanzania**, making it domain-specific for sensitive topics including abuse reporting, emergency situations, emotional distress, trauma narratives, and general child welfare inquiries.

### Key Features
- **Architecture:** OpenAI Whisper large-v2 (fine-tuned)
- **Domain:** Child helpline conversations (Swahili focus)
- **Deployment:** Available via AI Service API and Hugging Face Hub
- **Repository:** openchs/asr-whisper-helpline-sw-v1
- **Dual Capability:** Supports both transcription (Swahili→Swahili) AND translation (Swahili→English)
- **Special Capabilities:** Handles code-switching, fragmented trauma narratives, emergency language, emotional distress expressions, and hallucination filtering
- **Language Support:** 99+ languages with explicit support for African languages (Swahili, Amharic, Luganda, Kinyarwanda, Somali, Yoruba, Igbo, Hausa, Zulu, Xhosa, Afrikaans, Chichewa)

### Integration in AI Service Pipeline
The Whisper model is the first component in the BITZ AI Service pipeline, converting audio input into text:

```
Audio Input → Whisper Transcription (Swahili) → Translation Model (English) → NER → Classification → Summarization
                  ↓ (optional)
           Whisper Translation (English) → NER → Classification
```

The model serves as the entry point for both:
- **Real-time processing**: Progressive transcription during live calls
- **Post-call processing**: Full audio file transcription after call completion

---

## 2. Integration in AI Service Architecture

The Whisper model is deeply integrated into the AI service through multiple layers:

### 2.1. Configuration Layer

The Whisper model is configured through the central settings system (`app/config/settings.py`):

```python
class Settings(BaseSettings):
    # Whisper Model Configuration
    whisper_model_variant: str = "large_v2"
    whisper_large_v2_path: str = "./models/whisper_large_v2"
    whisper_large_turbo_path: str = "./models/whisper_large_turbo"
    whisper_active_symlink: str = "./models/whisper"
    
    # HuggingFace Hub Configuration
    use_hf_models: bool = True
    hf_whisper_large_v2: str = "openchs/asr-whisper-helpline-sw-v1"
    hf_whisper_large_turbo: str = "openchs/asr-whisper-helpline-sw-v1"
    hf_token: Optional[str] = None  # No token needed for public models
    
    # Model paths
    models_path: str = "./models"  # Auto-adjusted for Docker
    
    # Enable HuggingFace models
    use_hf_models: bool = True
```

**Configuration Helper Methods:**

```python
def get_active_whisper_path(self) -> str:
    """Get path to the currently active whisper model"""
    ...

def get_hf_model_kwargs(self) -> Dict[str, Any]:
    """Get common kwargs for HuggingFace model loading - NO TOKEN for public models"""
    ...
```

**Environment Detection:**

The system automatically detects whether it's running in Docker or local development and adjusts paths accordingly.

### 2.2. Model Loading and Initialization

The Whisper model is loaded through the `WhisperModel` class during FastAPI application startup:

```python
class WhisperModel:
    """HuggingFace Whisper model supporting both transcription and translation"""
    
    def __init__(self, model_path: str = None, enable_translation: bool = True):
        from ..config.settings import settings
        
        self.settings = settings
        self.model_path = model_path or settings.get_model_path("whisper")
        self.enable_translation = enable_translation
        
        ...

        # Supported language codes for Whisper
        self.supported_languages = {
            "auto": "Auto-detect",
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi",
            "sw": "Swahili",
            "am": "Amharic",
            "lg": "Luganda",
            "rw": "Kinyarwanda",
            "so": "Somali",
            "yo": "Yoruba",
            "ig": "Igbo",
            "ha": "Hausa",
            "zu": "Zulu",
            "xh": "Xhosa",
            "af": "Afrikaans",
            "ny": "Chichewa"
        }
```

**Model Loading Implementation:**

```python
def load(self) -> bool:
    """Load Whisper model with HuggingFace Hub support - NO AUTHENTICATION"""
    try:
        ...
```

**Model Loader Integration:**

The Whisper model is managed by the central `model_loader` which handles:
- Startup initialization
- Readiness checks
- Dependency tracking
- Health monitoring

```python
# During FastAPI startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Whisper model via model_loader
    model_loader.load_model("whisper")
    yield
    # Cleanup on shutdown
```

### 2.3. API Endpoints Layer

Whisper functionality is exposed through FastAPI routes (`app/api/endpoints/whisper_routes.py`):

```python
router = APIRouter(prefix="/whisper", tags=["whisper"])

class TranscriptionRequest(BaseModel):
    language: Optional[str] = None  # e.g., "en", "sw", "fr", "auto"

class TranscriptionResponse(BaseModel):
    transcript: str
    language: Optional[str]
    processing_time: float
    model_info: Dict
    timestamp: str
    audio_info: Dict

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Transcribe uploaded audio file to text
    
    Parameters:
    - audio: Audio file (wav, mp3, flac, m4a, ogg, webm)
    - language: Language code (e.g., 'en', 'sw', 'fr') or 'auto' for auto-detection
    """
    ...
```

**Information Endpoints:**

```python
@router.get("/info")
async def get_whisper_info():
    """Get Whisper model information"""
    ...

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    if not model_loader.is_model_ready("whisper"):
        return {
            "error": "Whisper model not ready",
            "supported_languages": {}
        }
    
    whisper_model = model_loader.models.get("whisper")
    ...
```

### 2.4. Audio Processing Strategy

The `WhisperModel` class implements intelligent audio processing with automatic chunking and hallucination filtering:

**Why Audio Chunking is Needed:**
- Whisper models have optimal performance on 30-second audio segments
- Long helpline conversations often exceed this optimal length
- Direct processing of very long audio can cause memory issues
- Chunking with proper reconstruction preserves conversation continuity

**Core Transcription Method:**

```python
def transcribe_audio_file(self, audio_file_path: str, language: Optional[str] = None, task: str = "transcribe") -> str:
    """Transcribe or translate audio file to text with support for long audio"""
    if not self.is_loaded:
        raise RuntimeError("Whisper model not loaded")
    
    ...
```

**Hallucination Filtering:**

Whisper models can produce false outputs during silence or low-energy audio. The implementation includes filtering:

```python
def transcribe_pcm_audio(self, pcm_bytes: bytes, sample_rate: int = 16000, language: Optional[str] = None, task: str = "transcribe") -> str:
    """Transcribe or translate PCM audio data directly from bytes"""
    ...
```

**Dual-Task Processing Methods:**

The model provides methods for getting both transcription AND translation in a single call:

```python
def transcribe_and_translate(
    self,
    audio_file_path: str,
    language: Optional[str] = None
) -> Dict[str, str]:
    """
    Get both transcript (original language) AND translation (English) from audio file
    
    Args:
        audio_file_path: Path to audio file
        language: Source language code (e.g., "sw" for Swahili)
    
    Returns:
        Dict with keys:
            - 'transcript': Original language text
            - 'translation': English translation (or None if translation not enabled)
    """
    if not self.is_loaded:
        raise RuntimeError("Whisper model not loaded")
    
    ...

def process_audio_with_options(
    self,
    audio_file_path: str,
    language: Optional[str] = None,
    include_translation: bool = False
) -> Dict[str, Any]:
    """
    Flexible audio processing method that returns transcript and optional translation
    
    Args:
        audio_file_path: Path to audio file
        language: Source language code (e.g., "sw")
        include_translation: Whether to include English translation
    
    Returns:
        Dict with keys:
            - 'transcript': Original language text (ALWAYS present)
            - 'translation': English translation (only if include_translation=True)
            - 'language': Language code used
            - 'has_translation': Boolean indicating if translation was performed
    """
    ...
```

### 2.5. Health Monitoring

The Whisper model integrates with the AI service health monitoring system (`app/api/endpoints/health_routes.py`):

**Model Status Endpoint:**

```python
@router.get("/health/models")
async def models_health():
    """Get detailed model status with dependency info"""
    ...
```

**Model Readiness States:**

- **Ready:** Model loaded and available for transcription
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

**Model Info Method:**

```python
def get_model_info(self) -> Dict[str, Any]:
    """Get model information"""
   ...
```

**Health Check Example Response:**

```json
{
  "ready_models": ["whisper", "translator", "classifier", "ner"],
  "implementable_models": [],
  "blocked_models": [],
  "details": {
    "whisper": {
      "loaded": true,
      "device": "cuda:0",
      "current_model_id": "openchs/asr-whisper-helpline-sw-v1",
      "translation_enabled": true,
      "version": "large-v2",
      "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg", "webm"],
      "max_audio_length": "unlimited (chunked processing)"
    }
  }
}
```

### 2.6. Pipeline Integration

The Whisper model integrates into two processing modes:

#### Real-time Processing

For live calls, Whisper transcribes audio progressively:

```python
# Progressive transcription during active call
@router.get("/{call_id}/transcript")
async def get_call_transcript(call_id: str):
    """Get cumulative transcript for active call"""
    ...
```

**Real-time Flow:**
1. Audio stream → Whisper transcription (Swahili) in 30-second chunks
2. Optional: Whisper translation (English)
3. Translated/transcribed text → NER extraction
4. Entities + classification → Agent notifications

**Configuration for Real-time Mode:**

```python
# Settings control real-time behavior
realtime_enable_progressive_translation: bool = True
realtime_processing_interval_seconds: int = 30
realtime_enable_agent_notifications: bool = True
```

#### Post-call Processing

For completed calls, full audio file processing:

```python
# Complete pipeline after call ends
Audio File (SCP download) → Whisper Transcription (full file) → Optional Translation
→ NER → Classification → Summarization → Unified Insights
```

**Configuration for Post-call Mode:**

```python
# Settings control post-call processing
postcall_enable_full_pipeline: bool = True
postcall_enable_enhanced_transcription: bool = True
postcall_whisper_model: str = "large-v2"
postcall_enable_audio_quality_improvement: bool = True
postcall_enable_noise_reduction: bool = True
postcall_convert_to_wav: bool = True
```

**Audio Download and Processing:**

```python
# SCP Configuration for audio retrieval
scp_user: str = "helpline"
scp_server: str = "192.168.10.3"
scp_password: str = "h3lpl1n3"
scp_remote_path_template: str = "/home/dat/helpline/calls/{call_id}.gsm"
scp_timeout_seconds: int = 30

# Audio preprocessing
postcall_enable_noise_reduction: bool = True
postcall_convert_to_wav: bool = True
```

### 2.7. Memory Management

The Whisper model implements automatic GPU/CPU memory management:

**GPU Memory Handling:**

```python
# Automatic device management in transcription
try:
    with torch.no_grad():
        predicted_ids = self.model.generate(
            input_features,
            attention_mask=attention_mask,
            max_length=448,
            num_beams=5,
            **generate_kwargs
        )
except torch.cuda.OutOfMemoryError:
    logger.warning("CUDA out of memory, falling back to CPU...")
    self.model.to("cpu")
    input_features = input_features.to(device="cpu", dtype=torch.float32)
    attention_mask = attention_mask.to("cpu")
    
    # Retry on CPU
    with torch.no_grad():
        predicted_ids = self.model.generate(...)
    
    # Restore to GPU
    self.model.to(self.device)
```

**Memory Cleanup:**

- GPU cache cleared after processing
- Temporary audio files deleted after transcription
- Automatic garbage collection for long audio processing

---

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The Whisper model is deployed as part of the AI Service and accessible via REST API.

#### Endpoint
```
POST /whisper/transcribe
```

#### Request Format

**Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
- audio: file (required) - Audio file in supported format
- language: string (optional) - Language code (e.g., "sw", "en", "auto")
```

#### Response Format

**Success Response (200):**
```json
{
  "transcript": "string",
  "language": "string",
  "processing_time": 0,
  "model_info": {
    "model_name": "whisper",
    "model_path": "string",
    "fallback_model_id": "openchs/asr-whisper-helpline-sw-v1",
    "device": "cuda:0",
    "is_loaded": true,
    "translation_enabled": true,
    "version": "large-v2",
    "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg", "webm"]
  },
  "timestamp": "string",
  "audio_info": {
    "filename": "string",
    "file_size_mb": 0,
    "format": "string",
    "content_type": "string"
  }
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

#### Example cURL Requests

**Basic Transcription (Auto-detect language):**
```bash
curl -X POST "http://192.168.8.18:8123/whisper/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@sample.wav"
```

**Response:**
```json
{
  "transcript": "Mbukweli, kaitike vipi? Nukuanasema. Kikozana na baba mdo...",
  "language": null,
  "processing_time": 63.396394,
  "model_info": {
    "model_name": "whisper",
    "device": "cuda:0",
    "translation_enabled": true,
    "version": "large-v2"
  },
  "timestamp": "2025-10-21T12:05:27.726046",
  "audio_info": {
    "filename": "sample.wav",
    "file_size_mb": 1.97,
    "format": ".wav",
    "content_type": "audio/wav"
  }
}
```

**Swahili Transcription (Specify language):**
```bash
curl -X POST "http://192.168.8.18:8123/whisper/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@helpline_call.wav" \
  -F "language=sw"
```

**English Transcription:**
```bash
curl -X POST "http://192.168.8.18:8123/whisper/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@english_audio.mp3" \
  -F "language=en"
```

**Long Audio File (Automatic chunking):**
```bash
curl -X POST "http://192.168.8.18:8123/whisper/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@long_call_5_minutes.wav" \
  -F "language=sw"
```

#### Getting Whisper Model Info

**Endpoint:**
```
GET /whisper/info
```

**Response:**
```json
{
  "status": "ready",
  "model_info": {
    "model_name": "whisper",
    "current_model_id": "openchs/asr-whisper-helpline-sw-v1",
    "device": "cuda:0",
    "is_loaded": true,
    "translation_enabled": true,
    "version": "large-v2",
    "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg", "webm"],
    "max_audio_length": "unlimited (chunked processing)",
    "sample_rate": "16kHz",
    "tasks_supported": "transcribe, translate",
    "languages": "multilingual (99+ languages)"
  }
}
```

#### Getting Supported Languages

**Endpoint:**
```
GET /whisper/languages
```

**Response:**
```json
{
  "supported_languages": {
    "auto": "Auto-detect",
    "en": "English",
    "sw": "Swahili",
    "am": "Amharic",
    "lg": "Luganda",
    "rw": "Kinyarwanda",
    "so": "Somali",
    "yo": "Yoruba",
    "ig": "Igbo",
    "ha": "Hausa",
    "zu": "Zulu",
    "xh": "Xhosa",
    "af": "Afrikaans",
    "ny": "Chichewa"
  },
  "total_supported": "99+ languages",
  "note": "Whisper supports many more languages beyond this list",
  "usage": "Pass language code in request: language='sw' for Swahili"
}
```

#### Features
- **Automatic Language Detection:** Pass `language=null` or `language=auto` for auto-detection
- **Format Flexibility:** Supports wav, mp3, flac, m4a, ogg, webm
- **Large File Handling:** Automatic chunking for files >30 seconds
- **File Size Limit:** 100MB maximum
- **GPU Acceleration:** Automatic CUDA utilization with CPU fallback
- **Hallucination Filtering:** Removes false transcriptions from silence

---

### 3.2. Via Hugging Face Hub

The model is publicly available on Hugging Face for direct inference and fine-tuning.

#### Model Repository
- **Organization:** [openchs](https://huggingface.co/openchs)
- **Model:** [openchs/asr-whisper-helpline-sw-v1](https://huggingface.co/openchs/asr-whisper-helpline-sw-v1)

#### Installation

```bash
pip install transformers torch librosa
```

#### Inference Examples

**Using Pipeline (Recommended for Transcription):**
```python
from transformers import pipeline
import torch

# Load the ASR pipeline

transcriber = pipeline(
    "automatic-speech-recognition",
    model="openchs/asr-whisper-helpline-sw-v1",
    device=device,
    torch_dtype=torch_dtype
)

# Transcribe audio file (Swahili)
result = transcriber("helpline_call.wav")
print(result["text"])
# Output: "Ninajisikia vibaya sana. Nahitaji mtu wa kuongea naye."

# With language specification
result = transcriber(
    "helpline_call.wav",
    generate_kwargs={"language": "sw", "task": "transcribe"}
)
print(result["text"])
```

**Using Model and Processor Directly (For Translation):**
```python
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import torch
import librosa

# Load model and processor
model_id = "openchs/asr-whisper-helpline-sw-v1"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

# Load audio
audio_array, sample_rate = librosa.load("helpline_call.wav", sr=16000, mono=True)

# Process audio
inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt")
input_features = inputs.input_features.to(device, dtype=torch_dtype)

# Generate transcription
with torch.no_grad():
    predicted_ids = model.generate(
        input_features,
        language="sw",
        task="transcribe"
    )

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
print(transcription)
```

**Translation Example (Swahili to English):**
```python
model_id = "openchs/asr-whisper-helpline-sw-v1"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

# Load audio
audio_array, sample_rate = librosa.load("swahili_audio.wav", sr=16000, mono=True)

# Process audio
inputs = processor(audio_array, sampling_rate=16000, return_tensors="pt")
input_features = inputs.input_features.to(device, dtype=torch_dtype)

# Generate translation to English
with torch.no_grad():
    predicted_ids = model.generate(
        input_features,
        language="sw",
        task="translate"  # Translate to English
    )

translation = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
print(translation)
# Output: "I feel very bad. I need someone to talk to."
```

**Batch Transcription:**
```python

transcriber = pipeline(
    "automatic-speech-recognition",
    model="openchs/asr-whisper-helpline-sw-v1",
    device=device,
    torch_dtype=torch_dtype,
    batch_size=8  # Process multiple files at once
)

audio_files = [
    "call_001.wav",
    "call_002.wav",
    "call_003.wav"
]

results = transcriber(audio_files)

for audio_file, result in zip(audio_files, results):
    print(f"{audio_file}: {result['text']}")
```

**Long Audio Processing (Chunking):**
```python

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

# Load long audio file
audio_array, sample_rate = librosa.load("long_helpline_call.wav", sr=16000, mono=True)

# Calculate chunks (30-second segments)
chunk_duration = 30
chunk_samples = chunk_duration * sample_rate
audio_length = len(audio_array)

transcriptions = []

for i in range(0, audio_length, chunk_samples):
    chunk_end = min(i + chunk_samples, audio_length)
    audio_chunk = audio_array[i:chunk_end]
    
    # Process chunk
    inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")
    input_features = inputs.input_features.to(device, dtype=torch_dtype)
    
    with torch.no_grad():
        predicted_ids = model.generate(
            input_features,
            language="sw",
            task="transcribe",
            max_length=448,
            num_beams=5
        )
    
    chunk_transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    transcriptions.append(chunk_transcript.strip())
    
    print(f"Processed chunk {i//chunk_samples + 1}/{(audio_length + chunk_samples - 1)//chunk_samples}")

# Combine all chunks
full_transcript = " ".join(transcriptions)
print("\nFull transcript:")
print(full_transcript)
```

**Note:** When using the model directly from Hugging Face, you'll need to implement your own chunking logic for audio files longer than 30 seconds. The AI Service API handles this automatically.

---

## 4. Production Considerations

### Audio File Limits
- **Maximum File Size:** 100MB
- **Supported Formats:** wav, mp3, flac, m4a, ogg, webm
- **Sample Rate:** Automatically resampled to 16kHz
- **Optimal Chunk Size:** 30 seconds per segment
- **Maximum Audio Length:** Unlimited (automatic chunking)

### Processing Time
- **Short audio (< 10 seconds):** ~0.5-2 seconds
- **Medium audio (10-60 seconds):** ~2-10 seconds
- **Long audio (> 60 seconds):** ~10-60 seconds (depends on length)
- **Very long audio (> 5 minutes):** ~1-5 minutes with chunking

Processing times vary based on:
- GPU availability (CUDA vs CPU)
- Audio file length and quality
- Number of chunks required
- System load and available memory
- Language (Swahili is optimized)

### Automatic Chunking
The API automatically handles long audio files by:
1. **Duration Check:** Detecting if audio > 30 seconds
2. **Segmentation:** Creating 30-second chunks
3. **Processing:** Transcribing each chunk independently
4. **Reconstruction:** Combining transcriptions with proper spacing
5. **Memory Management:** Cleaning up between chunks

### Error Handling

**Common Error Scenarios:**

1. **No Audio File:**
```json
{
  "detail": [
    {
      "loc": ["body", "audio"],
      "msg": "No audio file provided",
      "type": "value_error"
    }
  ]
}
```

2. **Unsupported Format:**
```json
{
  "detail": "Unsupported audio format: .avi. Supported: ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm']"
}
```

3. **File Too Large:**
```json
{
  "detail": "File too large: 105.3MB. Max: 100MB"
}
```

4. **Model Not Ready:**
```json
{
  "detail": "Whisper model not ready. Check /health/models for status."
}
```

5. **Service Unavailable:**
```json
{
  "detail": "Whisper model not available"
}
```

6. **Processing Failure:**
```json
{
  "detail": "Transcription failed: [error details]"
}
```

### Health Checks

Monitor Whisper service health:

```bash
# Check if Whisper is ready
curl -X GET "http://192.168.8.18:8123/whisper/info"

# Get detailed model status
curl -X GET "http://192.168.8.18:8123/health/models"

# Get supported languages
curl -X GET "http://192.168.8.18:8123/whisper/languages"
```

### GPU Memory Management

The model automatically:
- Uses CUDA when available (float16 precision)
- Falls back to CPU on OOM errors (float32 precision)
- Cleans up GPU cache between chunks
- Restores GPU after CPU fallback

**Memory Requirements:**
- **GPU (CUDA):** ~3-4GB VRAM for large-v2
- **CPU:** ~6-8GB RAM for large-v2
- **Disk:** ~3GB for model weights

### Hallucination Mitigation

The model implements several strategies to reduce false transcriptions:

1. **Silence Detection:** Filters outputs from near-silent audio
2. **Energy Threshold:** Checks audio energy before processing
3. **Common Phrase Filtering:** Removes known hallucinations like "Thank you", "Goodbye", etc.
4. **Confidence Scoring:** Uses beam search with high beam count (5)

### Language Optimization

While the model supports 99+ languages, it is specifically optimized for:
- **Swahili** (primary training language)
- **English** (translation target)
- **Code-switching** (Swahili-English mixed speech)
- **African Languages** (Somali, Luganda, Kinyarwanda, etc.)

For best results with non-Swahili languages, consider testing on sample audio first.

---

## 5. Model Limitations

### Domain Specificity
- **Optimized for:** Child helpline conversations, emotional support language, emergency situations, trauma narratives
- **May require adaptation for:** General Swahili transcription, formal speeches, technical content, non-helpline domains
- **Performance varies on:** Out-of-distribution data, highly specialized terminology, studio-quality recordings

### Technical Constraints
- **Maximum File Size:** 100MB per request
- **Optimal Audio Length:** 30-second segments (longer audio is chunked)
- **Memory Requirements:** GPU recommended for production (CPU fallback available but slower)
- **Processing Speed:** Dependent on hardware, audio length, and quality
- **Supported Formats:** Limited to wav, mp3, flac, m4a, ogg, webm

### Audio Quality Considerations
- **Background Noise:** May reduce transcription accuracy
- **Multiple Speakers:** Works best with single speaker or clear alternating speakers
- **Audio Encoding:** GSM, low-bitrate formats may have reduced quality
- **Sample Rate:** Automatically resampled to 16kHz (may affect very high-quality recordings)
- **Silence/Low Volume:** May produce hallucinations (filtered automatically)

### Known Considerations
- **Code-Switching:** Generally successful, but complex patterns may reduce accuracy
- **Cultural Context:** Some culturally-specific Tanzanian expressions may not transcribe perfectly
- **Emotion Recognition:** Optimized for emotional distress language, may vary on neutral speech
- **Accents:** Fine-tuned on Tanzanian Swahili, may vary on other regional accents
- **Long Audio:** Chunking may occasionally affect cohesion at segment boundaries

### Translation Limitations
- **Translation Quality:** Swahili→English translation is generally good but may lose nuance
- **Cultural Context:** Some cultural references may not translate well
- **Idiomatic Expressions:** May translate literally rather than idiomatically
- **Proper Nouns:** May be inconsistently translated or transliterated

### Recommendations
- Monitor transcription quality for edge cases in your domain
- Use health check endpoints to verify model readiness before critical operations
- Consider implementing quality feedback loops for continuous improvement
- Review transcriptions for sensitive or critical content
- Test with sample audio from your specific use case before production deployment
- For non-Swahili languages, validate accuracy with ground truth data
- Use the API's automatic chunking rather than pre-segmenting long audio

---

## 6. Citation

If you use this model in your research or application, please cite:

```bibtex
@misc{asr_whisper_helpline_sw_v1,
  title={ASR Whisper Helpline Swahili v1},
  author={OpenCHS Team},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/openchs/asr-whisper-helpline-sw-v1},
  note={Fine-tuned Whisper large-v2 for child helpline transcription}
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

*Documentation last updated: October 21, 2025*