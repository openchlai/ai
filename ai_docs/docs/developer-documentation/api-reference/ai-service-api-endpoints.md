# AI Service API Endpoints

## Base URL
```
http://localhost:8123
```

## Authentication
By default, AI service endpoints don't require authentication for internal use. For production deployments with external access, see [Authentication Guide](authentication.md).

---

## Audio Processing Endpoints

### Complete Audio Processing Pipeline
Process audio through full AI pipeline (transcription, translation, classification).

**Endpoint:** `POST /audio/process`

**Request:** Multipart form data
```
audio: <binary audio file>
language: "sw" (optional, default: auto-detect)
include_translation: "true" (optional)
include_classification: "true" (optional)
```

**Example:**
```bash
curl -X POST http://localhost:8123/audio/process \
  -F "audio=@call_recording.wav" \
  -F "language=sw" \
  -F "include_translation=true"
```

**Response:**
```json
{
  "audio_info": {
    "filename": "call_recording.wav",
    "file_size_mb": 2.3,
    "duration_seconds": 127,
    "language_specified": "sw",
    "processing_time": 23.4
  },
  "transcript": "Msichana mdogo ana miaka kumi na mbili...",
  "translation": "A twelve-year-old girl...",
  "entities": {
    "PERSON": ["Maria Wanjiku"],
    "LOC": ["Nairobi", "Kibera"],
    "ORG": ["Kenyatta Hospital"],
    "AGE": ["12 years old"]
  },
  "classification": {
    "main_category": "child_protection",
    "sub_category": "physical_abuse",
    "priority": "high",
    "confidence": 0.94
  },
  "summary": "Emergency child protection case requiring immediate intervention",
  "insights": {
    "risk_assessment": {
      "risk_level": "high",
      "urgency": "immediate",
      "recommended_actions": [
        "immediate_intervention",
        "contact_child_services",
        "notify_supervisor"
      ]
    }
  }
}
```

---

### Streaming Audio Processing
Process audio with real-time progress updates.

**Endpoint:** `POST /audio/process-stream`

**Request:** Same as `/audio/process`

**Response:** Server-Sent Events stream
```
event: transcription_progress
data: {"progress": 25, "status": "processing"}

event: transcription_complete
data: {"text": "Transcribed text...", "confidence": 0.95}

event: translation_progress
data: {"progress": 50, "status": "translating"}

event: translation_complete
data: {"text": "Translated text..."}

event: classification_complete
data: {"category": "child_protection", "risk_level": "high"}
```

---

### Quick Audio Analysis
Faster analysis with essential features only.

**Endpoint:** `POST /audio/analyze`

**Request:** Multipart form data
```
audio: <binary audio file>
language: "sw"
```

**Response:**
```json
{
  "transcript": "Brief transcript...",
  "language_detected": "sw",
  "duration": 127,
  "risk_level": "high",
  "processing_time": 8.2
}
```

---

### Check Processing Status
Check status of async audio processing task.

**Endpoint:** `GET /audio/task/{task_id}`

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "processing",
  "progress": 65,
  "current_step": "translation",
  "estimated_completion": "2025-09-26T14:27:00Z",
  "result": null
}
```

**Status values:**
- `queued` - Waiting in queue
- `processing` - Currently processing
- `completed` - Finished successfully
- `failed` - Processing failed

---

## Transcription Endpoints

### Transcribe Audio
Convert speech to text using Whisper.

**Endpoint:** `POST /whisper/transcribe`

**Request:** Multipart form data
```
audio: <binary audio file>
language: "sw" (optional)
task: "transcribe" (or "translate" for translate-to-English)
```

**Example:**
```bash
curl -X POST http://localhost:8123/whisper/transcribe \
  -F "audio=@recording.wav" \
  -F "language=sw" \
  -F "task=transcribe"
```

**Response:**
```json
{
  "text": "Msichana mdogo ana miaka kumi na mbili, yupo katika hatari...",
  "language": "sw",
  "confidence": 0.94,
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.2,
      "text": "Msichana mdogo ana miaka kumi na mbili",
      "confidence": 0.95
    }
  ],
  "duration": 127.3,
  "processing_time": 8.4
}
```

---

### Transcribe with Timestamps
Get detailed word-level timestamps.

**Endpoint:** `POST /whisper/transcribe-detailed`

**Request:** Same as `/whisper/transcribe` plus:
```
word_timestamps: "true"
```

**Response:**
```json
{
  "text": "Full transcription...",
  "words": [
    {
      "word": "Msichana",
      "start": 0.0,
      "end": 0.8,
      "confidence": 0.96
    },
    {
      "word": "mdogo",
      "start": 0.9,
      "end": 1.3,
      "confidence": 0.94
    }
  ]
}
```

---

## Translation Endpoints

### Translate Text
Translate between Swahili and English.

**Endpoint:** `POST /translate/`

**Request:**
```json
{
  "text": "Msichana mdogo ana miaka kumi na mbili",
  "source_language": "sw",
  "target_language": "en"
}
```

**Response:**
```json
{
  "original_text": "Msichana mdogo ana miaka kumi na mbili",
  "translated_text": "A young girl is twelve years old",
  "source_language": "sw",
  "target_language": "en",
  "confidence": 0.92,
  "model_version": "v1.2.0"
}
```

---

### Batch Translation
Translate multiple texts at once.

**Endpoint:** `POST /translate/batch`

**Request:**
```json
{
  "texts": [
    "Msichana mdogo ana hatari",
    "Anahitaji msaada haraka"
  ],
  "source_language": "sw",
  "target_language": "en"
}
```

**Response:**
```json
{
  "translations": [
    {
      "original": "Msichana mdogo ana hatari",
      "translated": "Young girl in danger",
      "confidence": 0.93
    },
    {
      "original": "Anahitaji msaada haraka",
      "translated": "Needs help urgently",
      "confidence": 0.95
    }
  ]
}
```

---

## NLP Analysis Endpoints

### Named Entity Recognition
Extract entities from text.

**Endpoint:** `POST /ner/extract`

**Request:**
```json
{
  "text": "Maria Wanjiku lives in Nairobi near Kenyatta Hospital. She is 12 years old."
}
```

**Response:**
```json
{
  "entities": {
    "PERSON": ["Maria Wanjiku"],
    "LOC": ["Nairobi"],
    "ORG": ["Kenyatta Hospital"],
    "AGE": ["12 years old"]
  },
  "entity_details": [
    {
      "text": "Maria Wanjiku",
      "label": "PERSON",
      "start": 0,
      "end": 13,
      "confidence": 0.99
    },
    {
      "text": "Nairobi",
      "label": "LOC",
      "start": 23,
      "end": 30,
      "confidence": 0.98
    }
  ]
}
```

---

### Text Classification
Classify case category and urgency.

**Endpoint:** `POST /classifier/classify`

**Request:**
```json
{
  "text": "Child reports physical abuse from caregiver. Immediate danger.",
  "return_probabilities": true
}
```

**Response:**
```json
{
  "main_category": "child_protection",
  "sub_category": "physical_abuse",
  "priority": "critical",
  "confidence": 0.96,
  "all_probabilities": {
    "child_protection": 0.96,
    "mental_health": 0.02,
    "education": 0.01,
    "other": 0.01
  }
}
```

---

### Text Summarization
Generate summary of case details.

**Endpoint:** `POST /summarizer/summarize`

**Request:**
```json
{
  "text": "Long case description with multiple paragraphs...",
  "max_length": 100,
  "min_length": 30
}
```

**Response:**
```json
{
  "summary": "12-year-old girl experiencing abuse. Immediate intervention required. Family support needed.",
  "original_length": 487,
  "summary_length": 82,
  "compression_ratio": 0.17
}
```

---

## System Monitoring Endpoints

### Health Check
Basic health check.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-26T14:30:00Z"
}
```

---

### Detailed Health Check
Comprehensive system status.

**Endpoint:** `GET /health/detailed`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-26T14:30:00Z",
  "components": {
    "api": {
      "status": "healthy",
      "uptime_seconds": 86400
    },
    "redis": {
      "status": "healthy",
      "ping_response_ms": 1.2
    },
    "gpu": {
      "status": "healthy",
      "available": true,
      "memory_used_gb": 8.2,
      "memory_total_gb": 16.0
    },
    "models": {
      "whisper": "loaded",
      "translation": "loaded",
      "ner": "loaded",
      "classifier": "loaded"
    }
  },
  "performance": {
    "avg_response_time_ms": 234,
    "requests_per_minute": 12,
    "success_rate": 0.98
  }
}
```

---

### Model Status
Check AI model loading status.

**Endpoint:** `GET /health/models`

**Response:**
```json
{
  "models": {
    "whisper": {
      "loaded": true,
      "version": "large-v3-turbo",
      "memory_usage_mb": 3072,
      "supported_languages": 99,
      "load_time_seconds": 12.3
    },
    "translation": {
      "loaded": true,
      "version": "v1.2.0",
      "language_pairs": ["sw-en", "en-sw"]
    },
    "ner": {
      "loaded": true,
      "model": "en_core_web_md",
      "entities": ["PERSON", "LOC", "ORG", "DATE", "TIME"]
    },
    "classifier": {
      "loaded": true,
      "categories": ["child_protection", "mental_health", "education", "health"]
    }
  }
}
```

---

### Queue Status
Check processing queue status.

**Endpoint:** `GET /audio/queue/status`

**Response:**
```json
{
  "queue_length": 5,
  "active_tasks": 2,
  "completed_today": 147,
  "failed_today": 3,
  "avg_processing_time_seconds": 23.4,
  "estimated_wait_time_seconds": 120
}
```

---

### Worker Status
Check Celery worker status.

**Endpoint:** `GET /audio/workers/status`

**Response:**
```json
{
  "workers": {
    "celery@worker1": {
      "status": "online",
      "active_tasks": 1,
      "processed_tasks": 523,
      "failed_tasks": 7,
      "pool_size": 1
    }
  },
  "total_workers": 1,
  "total_active_tasks": 1,
  "queue_length": 5
}
```

---

## Utility Endpoints

### Get Available Models
List all available AI models.

**Endpoint:** `GET /models`

**Response:**
```json
{
  "models": [
    {
      "id": "whisper-large-v3-turbo",
      "name": "Whisper Large V3 Turbo",
      "type": "transcription",
      "languages": 99,
      "status": "available"
    },
    {
      "id": "sw-en-translation",
      "name": "Swahili-English Translation",
      "type": "translation",
      "status": "available"
    }
  ]
}
```

---

### Get Supported Languages
List supported transcription languages.

**Endpoint:** `GET /languages`

**Response:**
```json
{
  "languages": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English",
      "transcription": true,
      "translation": true
    },
    {
      "code": "sw",
      "name": "Swahili",
      "native_name": "Kiswahili",
      "transcription": true,
      "translation": true
    }
  ],
  "total_count": 99
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-26T14:30:00Z"
}
```

**Common Error Codes:**
- `INVALID_AUDIO_FORMAT` (400) - Audio file format not supported
- `FILE_TOO_LARGE` (413) - Audio file exceeds size limit
- `PROCESSING_FAILED` (500) - AI processing failed
- `MODEL_NOT_LOADED` (503) - Required model not available
- `QUEUE_FULL` (429) - Processing queue at capacity

---

## Rate Limiting

See [API Rate Limiting](api-rate-limiting-throttling.md) for details.

**Default Limits:**
- 50 requests per hour per IP
- 10 concurrent processing tasks
- Maximum file size: 100 MB

---

## Examples

### Complete Workflow Example

```python
import requests

# Process audio file
with open('call_recording.wav', 'rb') as audio:
    response = requests.post(
        'http://localhost:8123/audio/process',
        files={'audio': audio},
        data={
            'language': 'sw',
            'include_translation': 'true',
            'include_classification': 'true'
        }
    )

result = response.json()

# Extract results
transcript = result['transcript']
translation = result['translation']
risk_level = result['classification']['priority']

print(f"Risk Level: {risk_level}")
print(f"Transcript: {transcript}")
print(f"Translation: {translation}")

# Additional analysis
entities_response = requests.post(
    'http://localhost:8123/ner/extract',
    json={'text': translation}
)

entities = entities_response.json()['entities']
print(f"People mentioned: {entities['PERSON']}")
print(f"Locations: {entities['LOC']}")
```

---

## Performance Tips

1. **Use appropriate endpoints:**
   - `/audio/analyze` for quick results
   - `/audio/process` for comprehensive analysis
   - `/audio/process-stream` for real-time updates

2. **Batch operations:**
   - Use `/translate/batch` for multiple texts
   - Process multiple files asynchronously

3. **Optimize audio files:**
   - Convert to WAV/MP3 before upload
   - Compress large files
   - Trim silence from recordings

4. **Monitor queue status:**
   - Check `/audio/queue/status` before submitting
   - Implement retry logic for queue-full errors

For integration examples, see [Integrating with External Systems](../integrations-extensions/integrating-with-external-systems.md).