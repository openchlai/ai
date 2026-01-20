# API Reference

## Base URL
```
http://localhost:8125
```

## Authentication
- **Current**: No authentication (implement JWT as needed)
- **Planned**: JWT-based token authentication

## Response Format
All responses are JSON, with consistent error handling:

```json
{
  "status": "success|error",
  "data": {},
  "error": null,
  "timestamp": "2024-01-19T10:30:00Z"
}
```

---

## Audio Processing Endpoints

### 1. Process Audio (Complete Pipeline)
**POST** `/audio/process`

Process audio file through complete AI pipeline (all models).

**Request**:
```bash
curl -X POST \
  -F "audio=@call.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  -F "include_insights=true" \
  http://localhost:8125/audio/process
```

**Parameters**:
- `audio` (File, required): Audio file (WAV, MP3, FLAC, M4A, OGG)
- `language` (String, optional): Language code (default: auto-detect)
- `include_translation` (Boolean, optional): Include translation (default: true)
- `include_insights` (Boolean, optional): Include risk insights (default: true)
- `background` (Boolean, optional): Process in background (default: true)

**Response** (202 Accepted):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Audio processing started",
  "estimated_time": "15-45 seconds",
  "status_endpoint": "/audio/task/550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. Get Task Status
**GET** `/audio/task/{task_id}`

Check the status and results of a processing task.

**Request**:
```bash
curl http://localhost:8125/audio/task/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.65,
  "current_step": "Extracting entities...",
  "results": {
    "audio_info": {
      "filename": "call.wav",
      "duration": 300.5,
      "sample_rate": 16000
    },
    "transcript": "Msichana mdogo ana matatizo...",
    "translation": "A small girl has problems...",
    "entities": {},
    "classification": {}
  },
  "created_at": "2024-01-19T10:30:00Z",
  "completed_at": null
}
```

### 3. Get Active Tasks
**GET** `/audio/tasks/active`

Get list of all currently active audio processing tasks.

**Request**:
```bash
curl http://localhost:8125/audio/tasks/active?limit=10
```

**Query Parameters**:
- `limit` (optional): Maximum number of tasks to return (default: 50)
- `status` (optional): Filter by status (processing, queued)

**Response**:
```json
{
  "status": "success",
  "active_tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "processing",
      "progress": 0.65,
      "current_step": "Extracting entities...",
      "filename": "call.wav",
      "created_at": "2024-01-19T10:30:00Z",
      "elapsed_time": 12.5
    }
  ],
  "total_active": 1,
  "queue_length": 0
}
```

### 4. Cancel Task
**DELETE** `/audio/task/{task_id}`

Cancel an active task or delete task results.

**Request**:
```bash
curl -X DELETE http://localhost:8125/audio/task/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Task cancelled successfully",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 5. Get Queue Status
**GET** `/audio/queue/status`

Get detailed status of the audio processing queue.

**Request**:
```bash
curl http://localhost:8125/audio/queue/status
```

**Response**:
```json
{
  "status": "healthy",
  "queue": {
    "total_tasks": 5,
    "queued": 3,
    "processing": 2,
    "completed_today": 245,
    "failed_today": 2,
    "average_wait_time": 8.5,
    "average_processing_time": 12.3
  },
  "workers": {
    "active_workers": 4,
    "idle_workers": 2,
    "total_capacity": 6
  }
}
```

---

## Individual Model Endpoints

### Speech-to-Text (Whisper)

#### Transcribe Audio
**POST** `/whisper/transcribe`

**Request**:
```bash
curl -X POST \
  -F "audio=@call.wav" \
  -F "language=sw" \
  http://localhost:8125/whisper/transcribe
```

**Response**:
```json
{
  "status": "success",
  "transcript": "Msichana mdogo ana miaka 12...",
  "language": "sw",
  "confidence": 0.95,
  "duration": 120.5,
  "processing_time": 8.3
}
```

### Translation

#### Translate Text
**POST** `/translate/`

**Request**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Msichana mdogo ana matatizo",
    "source_language": "sw",
    "target_language": "en"
  }' \
  http://localhost:8125/translate/
```

**Response**:
```json
{
  "status": "success",
  "original_text": "Msichana mdogo ana matatizo",
  "translated_text": "A small girl has problems",
  "confidence": 0.92
}
```

### Named Entity Recognition

#### Extract Entities
**POST** `/ner/extract`

**Request**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Maria lives in Nairobi and works at the hospital"
  }' \
  http://localhost:8125/ner/extract
```

**Response**:
```json
{
  "status": "success",
  "entities": {
    "PERSON": [{"text": "Maria", "start": 0, "end": 5}],
    "LOC": [{"text": "Nairobi", "start": 16, "end": 23}],
    "ORG": [{"text": "hospital", "start": 41, "end": 49}]
  }
}
```

### Case Classification

#### Classify Case
**POST** `/classifier/classify`

**Request**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text": "12-year-old girl experiencing suicidal thoughts...",
    "threshold": 0.5
  }' \
  http://localhost:8125/classifier/classify
```

**Response**:
```json
{
  "status": "success",
  "classification": {
    "main_category": "mental_health",
    "main_category_confidence": 0.94,
    "sub_category": "suicidal_ideation",
    "priority": "high",
    "intervention_type": "immediate_psychiatric_evaluation"
  }
}
```

### Text Summarization

#### Summarize Text
**POST** `/summarizer/summarize`

**Request**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long transcript here...",
    "max_length": 150,
    "min_length": 50
  }' \
  http://localhost:8125/summarizer/summarize
```

**Response**:
```json
{
  "status": "success",
  "summary": "12-year-old girl experiencing mental health crisis...",
  "summary_length": 120,
  "compression_ratio": 0.048
}
```

### Question-Answering

#### Ask Question
**POST** `/qa/predict`

**Request**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "context": "The girl lives with her aunt in Kibera...",
    "question": "Where does the girl live?",
    "threshold": 0.5
  }' \
  http://localhost:8125/qa/predict
```

**Response**:
```json
{
  "status": "success",
  "answer": "Kibera",
  "confidence": 0.87,
  "start_position": 35,
  "end_position": 41
}
```

---

## Call Session Endpoints

### Get All Active Calls
**GET** `/api/v1/calls/active`

```json
{
  "status": "success",
  "active_calls": [
    {
      "call_id": "1705669200.1",
      "caller_id": "+254712345678",
      "start_time": "2024-01-19T10:30:00Z",
      "duration": 245,
      "status": "in_progress"
    }
  ]
}
```

### Get Call Details
**GET** `/api/v1/calls/{call_id}`

```json
{
  "status": "success",
  "call": {
    "call_id": "1705669200.1",
    "caller_id": "+254712345678",
    "start_time": "2024-01-19T10:30:00Z",
    "end_time": "2024-01-19T10:35:00Z",
    "duration": 300,
    "transcript": "...",
    "translation": "...",
    "classification": {},
    "entities": {}
  }
}
```

### Get Call Transcript
**GET** `/api/v1/calls/{call_id}/transcript`

Get the full transcript for a call with timestamps.

### End Call Session
**POST** `/api/v1/calls/{call_id}/end`

Manually end a call session and trigger post-call processing.

### Get Call Segments
**GET** `/api/v1/calls/{call_id}/segments`

Get transcript segments with speaker diarization and timestamps.

### Get Classification Evolution
**GET** `/api/v1/calls/{call_id}/classification-evolution`

Track how call classification changes throughout the conversation.

---

## Health & Status Endpoints

### Service Health
**GET** `/health`

Check overall service health.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-19T10:35:00Z"
}
```

### Detailed Health
**GET** `/health/detailed`

Check detailed health of all components.

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "api": "healthy",
    "redis": "healthy",
    "models": "loaded",
    "workers": "active"
  }
}
```

### Model Status
**GET** `/health/models`

Check status of all ML models.

**Response**:
```json
{
  "status": "success",
  "models": {
    "whisper": "loaded",
    "translator": "loaded",
    "ner": "loaded",
    "classifier": "loaded",
    "summarizer": "loaded"
  }
}
```
