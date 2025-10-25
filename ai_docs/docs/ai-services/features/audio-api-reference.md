# Audio API Reference

## Overview

The Audio API provides audio processing endpoints for transcription, translation, entity extraction, classification, and insights generation. This API is part of the OpenCHS AI Service platform designed for the 116 Child Helpline.

**Base URL**: `/audio`

**Key Features**:
- Asynchronous and synchronous processing
- Real-time streaming updates
- Task-based workflow with status tracking
- Specialized Swahili-English translation
- Comprehensive NLP analysis

---

## Table of Contents

1. [Audio Processing Endpoints](#audio-processing-endpoints)
   - [POST /audio/process](#post-audioprocess)
   - [POST /audio/analyze](#post-audioanalyze)
   - [POST /audio/process-stream](#post-audioprocess-stream)
2. [Task Management Endpoints](#task-management-endpoints)
   - [GET /audio/task/{task_id}](#get-audiotasktask_id)
   - [DELETE /audio/task/{task_id}](#delete-audiotasktask_id)
   - [GET /audio/tasks/active](#get-audiotasksactive)
3. [System Monitoring Endpoints](#system-monitoring-endpoints)
   - [GET /audio/queue/status](#get-audiqueuestatus)
   - [GET /audio/workers/status](#get-audioworkersstatus)
4. [Complete Examples](#complete-examples)
5. [Error Handling](#error-handling)

---

## Audio Processing Endpoints

### POST /audio/process

**Description**: Process audio files through the complete AI pipeline with transcription, translation, NER, classification, summarization, and insights generation.

**Endpoint**: `POST /audio/process`

**Content-Type**: `multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `audio` | file | **Yes** | - | Audio file to process |
| `language` | string | No | `null` | Language code (e.g., 'sw', 'en') or 'auto' for detection |
| `include_translation` | boolean | No | `true` | Include translation in output |
| `include_insights` | boolean | No | `true` | Generate comprehensive insights |
| `background` | boolean | No | `true` | Process asynchronously (true) or synchronously (false) |

#### Supported Audio Formats

- `.wav` - WAV audio
- `.mp3` - MP3 audio
- `.flac` - FLAC lossless
- `.m4a` - MPEG-4 audio
- `.ogg` - Ogg Vorbis
- `.webm` - WebM audio

#### File Size Limits

- **Maximum**: 100MB
- **Recommended**: Under 50MB for optimal performance

#### Processing Time

- **Estimated**: 15-45 seconds
- **Factors**: File size, audio length, system load

#### Response (Asynchronous - background=true)

**Status Code**: `200 OK`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Audio processing started. Check status at /audio/task/{task_id}",
  "estimated_time": "15-45 seconds",
  "status_endpoint": "/audio/task/550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response (Synchronous - background=false)

**Status Code**: `200 OK`

Returns complete processing result immediately (see [Complete Result Structure](#complete-result-structure) below).

#### Example Requests

**cURL (Asynchronous)**:
```bash
curl -X POST "http://localhost:8123/audio/process" \
  -F "audio=@recording.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  -F "include_insights=true" \
  -F "background=true"
```

**cURL (Synchronous)**:
```bash
curl -X POST "http://localhost:8123/audio/process" \
  -F "audio=@recording.wav" \
  -F "language=sw" \
  -F "background=false"
```

**Python (Asynchronous)**:
```python
import requests

with open('recording.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8123/audio/process',
        files={'audio': audio_file},
        data={
            'language': 'sw',
            'include_translation': True,
            'include_insights': True,
            'background': True
        }
    )

task_data = response.json()
task_id = task_data['task_id']
print(f"Task submitted: {task_id}")
```

**Python (Synchronous)**:
```python
import requests

with open('recording.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8123/audio/process',
        files={'audio': audio_file},
        data={
            'language': 'sw',
            'background': False
        }
    )

result = response.json()
print(f"Transcript: {result['result']['transcript']}")
```

#### Complete Result Structure

When processing completes, the result includes:

```json
{
  "audio_info": {
    "filename": "recording.wav",
    "file_size_mb": 2.3,
    "language_specified": "sw",
    "processing_time": 23.4
  },
  "transcript": "Msichana mdogo ana miaka 12...",
  "translation": "A 12-year-old girl...",
  "nlp_processing_info": {
    "text_used_for_nlp": "translated_text",
    "nlp_text_length": 1234
  },
  "entities": {
    "PERSON": ["Maria", "Dr. John"],
    "LOC": ["Nairobi", "Kibera"],
    "ORG": ["Hospital", "Police Department"],
    "DATE": ["2025-01-15"],
    "GPE": ["Kenya"]
  },
  "classification": {
    "main_category": "child_protection",
    "sub_category": "mental_health_crisis",
    "priority": "high",
    "confidence": 0.94,
    "intervention": "immediate_action_required"
  },
  "qa_scores": {
    "empathy_score": 0.87,
    "professionalism_score": 0.92,
    "problem_resolution_score": 0.78,
    "overall_quality": 0.86
  },
  "summary": "Emergency call regarding a 12-year-old girl...",
  "insights": {
    "case_overview": {
      "primary_language": "multilingual",
      "key_entities": {
        "people_mentioned": 3,
        "locations_mentioned": 2,
        "organizations_mentioned": 1,
        "dates_mentioned": 1
      },
      "case_complexity": "high"
    },
    "risk_assessment": {
      "risk_indicators_found": 2,
      "risk_level": "high",
      "priority": "urgent",
      "confidence": 0.94
    },
    "key_information": {
      "main_category": "child_protection",
      "sub_category": "mental_health_crisis",
      "intervention_needed": "immediate"
    }
  },
  "processing_steps": {
    "transcription": {
      "duration": 8.2,
      "status": "completed"
    },
    "translation": {
      "duration": 2.1,
      "status": "completed"
    },
    "ner": {
      "duration": 1.5,
      "status": "completed",
      "entities_found": 11
    },
    "classification": {
      "duration": 0.8,
      "status": "completed",
      "confidence": 0.94
    },
    "summarization": {
      "duration": 2.3,
      "status": "completed",
      "summary_length": 245
    }
  },
  "pipeline_info": {
    "total_time": 23.4,
    "models_used": [
      "whisper",
      "translator",
      "ner",
      "classifier",
      "summarizer",
      "all_qa_distilbert_v1"
    ],
    "text_flow": "transcript → translated_text → nlp_models",
    "timestamp": "2025-10-25T10:30:45.123456",
    "processed_by": "celery_worker"
  }
}
```

#### Error Responses

**400 Bad Request - No File**:
```json
{
  "detail": "No audio file provided"
}
```

**400 Bad Request - Unsupported Format**:
```json
{
  "detail": "Unsupported audio format: .txt. Supported: ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm']"
}
```

**400 Bad Request - File Too Large**:
```json
{
  "detail": "File too large: 105.3MB. Max: 100MB"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Audio processing failed: [error details]"
}
```

**503 Service Unavailable**:
```json
{
  "detail": "Whisper model not ready. Check /health/models for status."
}
```

---

### POST /audio/analyze

**Description**: Quick audio analysis with transcription, classification, and summary without translation or detailed insights. Faster than full processing.

**Endpoint**: `POST /audio/analyze`

**Content-Type**: `multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `audio` | file | **Yes** | - | Audio file to analyze |
| `language` | string | No | `null` | Language code or 'auto' |
| `background` | boolean | No | `true` | Process asynchronously or synchronously |

#### Supported Audio Formats

Same as `/audio/process`

#### File Size Limits

- **Maximum**: 50MB (smaller than full processing)
- **Recommended**: Under 20MB

#### Processing Time

- **Estimated**: 10-20 seconds
- **Faster than**: Full processing (no translation or insights)

#### Response (Asynchronous)

**Status Code**: `200 OK`

```json
{
  "task_id": "analyze-abc123",
  "status": "queued",
  "message": "Quick analysis started",
  "estimated_time": "10-20 seconds",
  "status_endpoint": "/audio/task/analyze-abc123"
}
```

#### Quick Analysis Result

```json
{
  "transcript": "Full transcription text...",
  "summary": "Brief summary of the content...",
  "main_category": "child_protection",
  "priority": "high",
  "risk_level": "medium",
  "processing_time": 12.5
}
```

#### Use Cases

- Quick validation before full processing
- Fast transcription when translation not needed
- Preliminary analysis for triage
- Low-latency requirements

#### Example Requests

**cURL**:
```bash
curl -X POST "http://localhost:8123/audio/analyze" \
  -F "audio=@quick_check.wav" \
  -F "language=en" \
  -F "background=true"
```

**Python**:
```python
import requests

with open('quick_check.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8123/audio/analyze',
        files={'audio': audio_file},
        data={'language': 'en', 'background': True}
    )

task_data = response.json()
print(f"Quick analysis task: {task_data['task_id']}")
```

#### Error Responses

**400 Bad Request - File Too Large**:
```json
{
  "detail": "File too large for quick analysis: 55.3MB. Max: 50MB"
}
```

Other errors same as `/audio/process`

---

### POST /audio/process-stream

**Description**: Process audio with real-time progress updates via Server-Sent Events (SSE). Get progressive results as processing occurs.

**Endpoint**: `POST /audio/process-stream`

**Content-Type**: `multipart/form-data`

**Response Type**: `text/event-stream`

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `audio` | file | **Yes** | - | Audio file to process |
| `language` | string | No | `null` | Language code or 'auto' |
| `include_translation` | boolean | No | `true` | Include translation |
| `include_insights` | boolean | No | `true` | Generate insights |

#### Supported Audio Formats

Same as `/audio/process`

#### File Size Limits

- **Maximum**: 100MB

#### Stream Event Format

Events are sent as JSON objects with `data:` prefix:

```
data: {"task_id": "abc123", "status": "submitted", "message": "Processing started", "timestamp": "2025-10-25T10:30:45"}

data: {"task_id": "abc123", "status": "processing", "step": "transcription", "progress": 35, "message": "Transcribing audio..."}

data: {"task_id": "abc123", "status": "processing", "step": "translation", "progress": 45, "message": "Translating text...", "partial_result": {"transcript": "..."}}

data: {"task_id": "abc123", "status": "completed", "progress": 100, "message": "Processing complete", "result": {...}}
```

#### Processing Steps

Steps are emitted in this order with progress percentages:

| Step | Progress | Description |
|------|----------|-------------|
| `submitted` | 0% | Task submitted to queue |
| `transcription` | 0-40% | Converting audio to text |
| `translation` | 40-50% | Translating text (if enabled) |
| `nlp_analysis` | 50-55% | Starting NLP processing |
| `ner` | 55-65% | Extracting named entities |
| `classification` | 65-75% | Classifying content |
| `summarization` | 75-85% | Generating summary |
| `qa_scoring` | 85-90% | Quality assessment |
| `insights` | 90-95% | Generating insights (if enabled) |
| `completed` | 100% | Processing finished |

#### Stream Status Values

| Status | Description |
|--------|-------------|
| `submitted` | Initial confirmation |
| `processing` | Task in progress |
| `completed` | Successfully finished |
| `failed` | Processing error |
| `timeout` | Exceeded 5 minute limit |
| `stream_error` | Connection error |

#### Timeout

- **Maximum Duration**: 5 minutes (300 seconds)
- **Behavior**: Stream closes with timeout message

#### Example Requests

**cURL**:
```bash
curl -X POST "http://localhost:8123/audio/process-stream" \
  -F "audio=@recording.wav" \
  -F "language=sw" \
  -N  # Enable streaming
```

**Python**:
```python
import requests
import json

response = requests.post(
    'http://localhost:8123/audio/process-stream',
    files={'audio': open('recording.wav', 'rb')},
    data={'language': 'sw'},
    stream=True
)

for line in response.iter_lines():
    if line:
        # Lines are prefixed with "data: "
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            
            print(f"Progress: {data.get('progress', 0)}%")
            print(f"Step: {data.get('step', 'N/A')}")
            print(f"Message: {data.get('message', '')}")
            
            # Check for partial results
            if 'partial_result' in data:
                print(f"Partial: {data['partial_result']}")
            
            # Check for completion
            if data.get('status') == 'completed':
                print("Final result:", data.get('result'))
                break
            elif data.get('status') in ['failed', 'timeout', 'stream_error']:
                print(f"Error: {data.get('error', data.get('message'))}")
                break
```

**JavaScript (Browser)**:
```javascript
const formData = new FormData();
formData.append('audio', audioFile);
formData.append('language', 'sw');

const eventSource = new EventSource('/audio/process-stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  console.log(`Progress: ${data.progress}%`);
  console.log(`Step: ${data.step}`);
  
  if (data.status === 'completed') {
    console.log('Result:', data.result);
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('Stream error:', error);
  eventSource.close();
};
```

#### Use Cases

- Real-time UI progress indicators
- Live transcription display
- Dashboard monitoring
- Progressive result display

#### Error Responses

Stream errors are sent as SSE events:

```
data: {"task_id": "abc123", "status": "failed", "error": "Processing failed: Model not available"}

data: {"task_id": "abc123", "status": "timeout", "error": "Processing timeout after 5 minutes"}

data: {"task_id": "abc123", "status": "stream_error", "error": "Connection lost"}
```

---

## Task Management Endpoints

### GET /audio/task/{task_id}

**Description**: Retrieve the status and results of a processing task.

**Endpoint**: `GET /audio/task/{task_id}`

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | **Yes** | Unique task identifier from submission |

#### Response Status States

The task can be in one of several states:

##### 1. Pending/Queued

**Status Code**: `200 OK`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Task is queued for processing"
}
```

##### 2. Processing

**Status Code**: `200 OK`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "current_step": "transcription",
  "progress": 35,
  "filename": "recording.wav"
}
```

##### 3. Completed

**Status Code**: `200 OK`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "audio_info": { ... },
    "transcript": "...",
    "translation": "...",
    "entities": { ... },
    "classification": { ... },
    "summary": "...",
    "insights": { ... },
    "processing_steps": { ... },
    "pipeline_info": { ... }
  },
  "processing_time": 23.4
}
```

##### 4. Failed

**Status Code**: `200 OK`

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "error": "Model loading failed: NER model not available",
  "filename": "recording.wav"
}
```

#### Example Requests

**cURL**:
```bash
curl -X GET "http://localhost:8123/audio/task/550e8400-e29b-41d4-a716-446655440000"
```

**Python**:
```python
import requests

task_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(f'http://localhost:8123/audio/task/{task_id}')

status_data = response.json()
print(f"Status: {status_data['status']}")

if status_data['status'] == 'completed':
    result = status_data['result']
    print(f"Transcript: {result['transcript']}")
```

#### Polling Strategy

**Recommended Approach**:
```python
import time
import requests

def poll_task_status(task_id, max_wait=300):
    """Poll task status with exponential backoff"""
    intervals = [2, 2, 4, 4, 8, 8, 15, 15, 30]
    elapsed = 0
    
    for interval in intervals:
        if elapsed > max_wait:
            return None
        
        response = requests.get(f'http://localhost:8123/audio/task/{task_id}')
        status_data = response.json()
        
        if status_data['status'] in ['completed', 'failed']:
            return status_data
        
        print(f"Status: {status_data['status']}, waiting {interval}s...")
        time.sleep(interval)
        elapsed += interval
    
    return None
```

#### Error Responses

**404 Not Found**:
```json
{
  "detail": "Error retrieving task status"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Error retrieving task status"
}
```

---

### DELETE /audio/task/{task_id}

**Description**: Cancel an active or pending processing task.

**Endpoint**: `DELETE /audio/task/{task_id}`

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | **Yes** | Task identifier to cancel |

#### Response

**Status Code**: `200 OK`

```json
{
  "message": "Task 550e8400-e29b-41d4-a716-446655440000 cancelled successfully"
}
```

#### Behavior

- **Pending tasks**: Removed from queue immediately
- **Processing tasks**: Terminated as soon as possible
- **Completed tasks**: Cannot be cancelled (returns success anyway)
- **Already cancelled**: Returns success (idempotent)

#### Use Cases

- User cancellation from UI
- Timeout handling
- Resource cleanup during high load
- Batch operation management

#### Example Requests

**cURL**:
```bash
curl -X DELETE "http://localhost:8123/audio/task/550e8400-e29b-41d4-a716-446655440000"
```

**Python**:
```python
import requests

task_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.delete(f'http://localhost:8123/audio/task/{task_id}')

if response.status_code == 200:
    print("Task cancelled successfully")
```

#### Error Responses

**500 Internal Server Error**:
```json
{
  "detail": "Error cancelling task"
}
```

---

### GET /audio/tasks/active

**Description**: Retrieve all currently active audio processing tasks across all workers.

**Endpoint**: `GET /audio/tasks/active`

#### Response

**Status Code**: `200 OK`

```json
{
  "active_tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "process_audio_task",
      "worker": "worker1@hostname.local",
      "started": "2025-10-25T10:30:45.123456",
      "args": ["recording.wav"]
    },
    {
      "task_id": "def456uvw-789-012",
      "name": "process_audio_quick_task",
      "worker": "worker2@hostname.local",
      "started": "2025-10-25T10:31:12.987654",
      "args": ["quick_check.wav"]
    }
  ],
  "total_active": 2,
  "data_sources": {
    "celery_events": 2,
    "redis_backup": 2
  },
  "note": "Workers may appear offline during intensive processing - this is normal"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `active_tasks` | array | List of active task objects |
| `total_active` | integer | Total number of active tasks |
| `data_sources` | object | Sources of task information |
| `note` | string | System behavior notes |

#### Task Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Unique task identifier |
| `name` | string | Task type (process_audio_task or process_audio_quick_task) |
| `worker` | string | Worker hostname processing the task |
| `started` | string | ISO timestamp when task started |
| `args` | array | Task arguments (typically filename) |

#### Use Cases

- System monitoring dashboards
- Load balancing decisions
- Capacity planning
- Debugging and troubleshooting
- User task tracking

#### Example Requests

**cURL**:
```bash
curl -X GET "http://localhost:8123/audio/tasks/active"
```

**Python**:
```python
import requests

response = requests.get('http://localhost:8123/audio/tasks/active')
data = response.json()

print(f"Total active tasks: {data['total_active']}")
for task in data['active_tasks']:
    print(f"- {task['task_id']}: {task['name']} on {task['worker']}")
```

#### Error Responses

**200 OK with Error**:
```json
{
  "active_tasks": [],
  "total_active": 0,
  "error": "Error message",
  "note": "Monitoring may be temporarily unavailable during heavy load"
}
```

---

## System Monitoring Endpoints

### GET /audio/queue/status

**Description**: Check the current status of the Celery processing queue and worker availability.

**Endpoint**: `GET /audio/queue/status`

#### Response (Healthy System)

**Status Code**: `200 OK`

```json
{
  "status": "healthy",
  "workers": 2,
  "worker_info": [
    {
      "name": "worker1@hostname.local",
      "status": "online",
      "total_tasks": {
        "process_audio_task": 45,
        "process_audio_quick_task": 23
      },
      "current_load": 1
    },
    {
      "name": "worker2@hostname.local",
      "status": "online",
      "total_tasks": {
        "process_audio_task": 38,
        "process_audio_quick_task": 19
      },
      "current_load": 0
    }
  ],
  "queue_stats": {
    "active_tasks": 2,
    "scheduled_tasks": 0,
    "reserved_tasks": 1,
    "total_pending": 3
  }
}
```

#### Response (No Workers)

**Status Code**: `200 OK`

```json
{
  "status": "no_workers",
  "message": "No Celery workers are running",
  "workers": 0
}
```

#### Response (System Busy)

**Status Code**: `200 OK`

```json
{
  "status": "inspection_timeout",
  "message": "Workers busy - monitoring temporarily unavailable",
  "workers": "unknown",
  "note": "This is normal during heavy processing"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | System status: healthy, no_workers, inspection_timeout, error |
| `workers` | integer/string | Number of workers or "unknown" |
| `worker_info` | array | Detailed worker information |
| `queue_stats` | object | Queue statistics |

#### Worker Info Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Worker hostname |
| `status` | string | Worker status (online) |
| `total_tasks` | object | Task counts by type |
| `current_load` | integer | Currently processing tasks |

#### Queue Stats Fields

| Field | Type | Description |
|-------|------|-------------|
| `active_tasks` | integer | Currently being processed |
| `scheduled_tasks` | integer | Scheduled for future |
| `reserved_tasks` | integer | Reserved by workers |
| `total_pending` | integer | Sum of all pending |

#### Use Cases

- Health checks before batch submission
- Capacity monitoring
- Alert triggers for worker failures
- Load balancing decisions

#### Example Requests

**cURL**:
```bash
curl -X GET "http://localhost:8123/audio/queue/status"
```

**Python**:
```python
import requests

response = requests.get('http://localhost:8123/audio/queue/status')
data = response.json()

if data['status'] == 'healthy':
    print(f"System healthy: {data['workers']} workers online")
    print(f"Pending tasks: {data['queue_stats']['total_pending']}")
else:
    print(f"System status: {data['status']}")
    print(f"Message: {data.get('message', 'N/A')}")
```

#### Error Responses

**200 OK with Error**:
```json
{
  "status": "error",
  "message": "Error message details",
  "workers": 0
}
```

---

### GET /audio/workers/status

**Description**: Monitor the status and health of Celery audio processing workers.

**Endpoint**: `GET /audio/workers/status`

#### Response

**Status Code**: `200 OK`

```json
{
  "workers": {
    "worker1@hostname.local": {
      "last_heartbeat": "2025-10-25T10:30:45.123456",
      "status": "online"
    },
    "worker2@hostname.local": {
      "last_heartbeat": "2025-10-25T10:30:43.987654",
      "status": "online"
    }
  },
  "total_workers": 2,
  "monitoring_status": "connected"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `workers` | object | Dictionary of worker information keyed by hostname |
| `total_workers` | integer | Total number of workers detected |
| `monitoring_status` | string | Event monitoring connection status |

#### Worker Fields

| Field | Type | Description |
|-------|------|-------------|
| `last_heartbeat` | string | ISO timestamp of last heartbeat |
| `status` | string | Worker status (online) |

#### Monitoring Status Values

| Value | Description |
|-------|-------------|
| `connected` | Event monitoring active, receiving heartbeats |
| `waiting_for_worker` | Monitoring initialized, waiting for workers |
| `monitoring_unavailable` | Event monitoring system error |

#### Important Notes

- Workers send periodic heartbeats to indicate they're alive
- Workers may appear "offline" during intensive processing - **this is normal**
- Missing heartbeat doesn't necessarily mean worker is down
- Check `/audio/queue/status` for comprehensive worker information

#### Use Cases

- Worker health monitoring
- Heartbeat verification
- Event monitoring status
- Infrastructure health checks

#### Example Requests

**cURL**:
```bash
curl -X GET "http://localhost:8123/audio/workers/status"
```

**Python**:
```python
import requests

response = requests.get('http://localhost:8123/audio/workers/status')
data = response.json()

print(f"Total workers: {data['total_workers']}")
print(f"Monitoring: {data['monitoring_status']}")

for worker_name, worker_info in data['workers'].items():
    print(f"- {worker_name}: {worker_info['status']}")
    print(f"  Last heartbeat: {worker_info['last_heartbeat']}")
```

#### Error Responses

**200 OK with Error**:
```json
{
  "workers": {},
  "total_workers": 0,
  "monitoring_status": "monitoring_unavailable",
  "error": "Error details"
}
```

---

## Complete Examples

### Example 1: Basic Asynchronous Processing

```python
import requests
import time

# Step 1: Submit audio for processing
with open('recording.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8123/audio/process',
        files={'audio': audio_file},
        data={
            'language': 'sw',
            'include_translation': True,
            'include_insights': True,
            'background': True
        }
    )

task_data = response.json()
task_id = task_data['task_id']
print(f"Task submitted: {task_id}")

# Step 2: Poll for completion
max_attempts = 30
attempt = 0
wait_time = 2

while attempt < max_attempts:
    response = requests.get(f'http://localhost:8123/audio/task/{task_id}')
    status_data = response.json()
    
    status = status_data['status']
    print(f"Attempt {attempt + 1}: Status = {status}")
    
    if status == 'completed':
        result = status_data['result']
        print("\nProcessing complete!")
        print(f"Transcript: {result['transcript'][:100]}...")
        print(f"Translation: {result['translation'][:100]}...")
        print(f"Category: {result['classification']['main_category']}")
        print(f"Priority: {result['classification']['priority']}")
        break
    elif status == 'failed':
        print(f"Processing failed: {status_data.get('error')}")
        break
    
    time.sleep(wait_time)
    attempt += 1
    
    # Exponential backoff
    if attempt % 5 == 0:
        wait_time = min(wait_time * 2, 15)
```

### Example 2: Batch Processing with Queue Monitoring

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_queue_capacity():
    """Check if queue can accept more tasks"""
    response = requests.get('http://localhost:8123/audio/queue/status')
    data = response.json()
    
    if data['status'] != 'healthy':
        return False
    
    pending = data['queue_stats']['total_pending']
    return pending < 10  # Don't submit if more than 10 pending

def submit_audio(file_path):
    """Submit a single audio file"""
    with open(file_path, 'rb') as audio_file:
        response = requests.post(
            'http://localhost:8123/audio/process',
            files={'audio': audio_file},
            data={'language': 'sw', 'background': True}
        )
    return response.json()['task_id']

def wait_for_task(task_id):
    """Wait for task completion"""
    for _ in range(60):
        response = requests.get(f'http://localhost:8123/audio/task/{task_id}')
        status_data = response.json()
        
        if status_data['status'] == 'completed':
            return status_data['result']
        elif status_data['status'] == 'failed':
            return None
        
        time.sleep(5)
    return None

# Main batch processing
audio_files = ['file1.wav', 'file2.wav', 'file3.wav', 'file4.wav', 'file5.wav']
task_ids = []

# Submit with queue monitoring
for file_path in audio_files:
    # Wait for queue capacity
    while not check_queue_capacity():
        print("Queue full, waiting...")
        time.sleep(10)
    
    task_id = submit_audio(file_path)
    task_ids.append((file_path, task_id))
    print(f"Submitted {file_path}: {task_id}")
    time.sleep(1)  # Rate limiting

# Wait for all tasks
results = {}
for file_path, task_id in task_ids:
    result = wait_for_task(task_id)
    results[file_path] = result
    if result:
        print(f"✓ {file_path} completed")
    else:
        print(f"✗ {file_path} failed")

print(f"\nCompleted {len([r for r in results.values() if r])} out of {len(audio_files)} files")
```

### Example 3: Real-time Streaming with Progress Bar

```python
import requests
import json
from tqdm import tqdm

def process_with_progress(audio_path):
    """Process audio with real-time progress bar"""
    
    with open(audio_path, 'rb') as audio_file:
        response = requests.post(
            'http://localhost:8123/audio/process-stream',
            files={'audio': audio_file},
            data={'language': 'sw'},
            stream=True
        )
    
    progress_bar = tqdm(total=100, desc="Processing", unit="%")
    last_progress = 0
    
    for line in response.iter_lines():
        if line and line.startswith(b'data: '):
            data = json.loads(line[6:])
            
            # Update progress bar
            current_progress = data.get('progress', 0)
            progress_bar.update(current_progress - last_progress)
            last_progress = current_progress
            
            # Update description with current step
            step = data.get('step', '')
            if step:
                progress_bar.set_description(f"Processing ({step})")
            
            # Check for completion
            if data.get('status') == 'completed':
                progress_bar.close()
                return data['result']
            elif data.get('status') in ['failed', 'timeout', 'stream_error']:
                progress_bar.close()
                print(f"Error: {data.get('error', data.get('message'))}")
                return None
    
    progress_bar.close()
    return None

# Usage
result = process_with_progress('recording.wav')
if result:
    print(f"\nTranscript: {result['transcript'][:200]}...")
```

### Example 4: Error Handling and Retry Logic

```python
import requests
import time
from requests.exceptions import RequestException

def robust_audio_processing(file_path, max_retries=3):
    """Process audio with comprehensive error handling and retries"""
    
    for attempt in range(max_retries):
        try:
            # Check system health first
            health_response = requests.get(
                'http://localhost:8123/audio/queue/status',
                timeout=10
            )
            health_data = health_response.json()
            
            if health_data['status'] != 'healthy':
                print(f"System not healthy: {health_data['status']}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None, "System unhealthy"
            
            # Submit audio
            with open(file_path, 'rb') as audio_file:
                submit_response = requests.post(
                    'http://localhost:8123/audio/process',
                    files={'audio': audio_file},
                    data={'language': 'sw', 'background': True},
                    timeout=30
                )
            
            submit_response.raise_for_status()
            task_id = submit_response.json()['task_id']
            print(f"Task submitted: {task_id}")
            
            # Poll for result
            max_polls = 60  # 5 minutes with 5s intervals
            for poll in range(max_polls):
                try:
                    status_response = requests.get(
                        f'http://localhost:8123/audio/task/{task_id}',
                        timeout=10
                    )
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    
                    if status_data['status'] == 'completed':
                        return status_data['result'], None
                    elif status_data['status'] == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        
                        # Don't retry on certain errors
                        if 'File too large' in error or 'Unsupported format' in error:
                            return None, error
                        
                        # Retry on model errors
                        if 'model' in error.lower() and attempt < max_retries - 1:
                            print(f"Model error, will retry: {error}")
                            break
                        
                        return None, error
                    
                    time.sleep(5)
                    
                except RequestException as e:
                    if poll < max_polls - 1:
                        continue
                    raise
            
            # Timeout - cancel task
            try:
                requests.delete(f'http://localhost:8123/audio/task/{task_id}')
            except:
                pass
            
            if attempt < max_retries - 1:
                print("Processing timeout, retrying...")
                continue
            else:
                return None, "Processing timeout after 5 minutes"
                
        except RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Request failed (attempt {attempt + 1}): {e}")
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return None, f"Failed after {max_retries} attempts: {e}"
    
    return None, "Maximum retries exceeded"

# Usage
result, error = robust_audio_processing('recording.wav')
if result:
    print("Success!")
    print(f"Category: {result['classification']['main_category']}")
    print(f"Priority: {result['classification']['priority']}")
else:
    print(f"Failed: {error}")
```

### Example 5: Task Cancellation

```python
import requests
import time
import threading

def cancel_task_after_timeout(task_id, timeout_seconds):
    """Cancel task if it runs too long"""
    time.sleep(timeout_seconds)
    
    # Check if task is still running
    response = requests.get(f'http://localhost:8123/audio/task/{task_id}')
    status_data = response.json()
    
    if status_data['status'] in ['pending', 'processing']:
        print(f"Task {task_id} timeout, cancelling...")
        requests.delete(f'http://localhost:8123/audio/task/{task_id}')
        return True
    
    return False

# Submit task
with open('recording.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8123/audio/process',
        files={'audio': audio_file},
        data={'language': 'sw', 'background': True}
    )

task_id = response.json()['task_id']
print(f"Task submitted: {task_id}")

# Start timeout watcher in background
timeout_thread = threading.Thread(
    target=cancel_task_after_timeout,
    args=(task_id, 60)  # 60 second timeout
)
timeout_thread.daemon = True
timeout_thread.start()

# Poll for result
for _ in range(30):
    response = requests.get(f'http://localhost:8123/audio/task/{task_id}')
    status_data = response.json()
    
    if status_data['status'] == 'completed':
        print("Task completed!")
        break
    elif status_data['status'] == 'failed':
        print(f"Task failed: {status_data.get('error')}")
        break
    
    time.sleep(2)
```

---

## Error Handling

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input (missing file, wrong format, file too large) |
| 404 | Not Found | Task not found |
| 422 | Validation Error | Missing or invalid parameters |
| 500 | Internal Server Error | Server processing error |
| 503 | Service Unavailable | Required models not loaded |

### Common Error Scenarios

#### 1. File Validation Errors

**No File Provided**:
```json
{
  "detail": "No audio file provided"
}
```

**Unsupported Format**:
```json
{
  "detail": "Unsupported audio format: .txt. Supported: ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.webm']"
}
```

**File Too Large (Process)**:
```json
{
  "detail": "File too large: 105.3MB. Max: 100MB"
}
```

**File Too Large (Analyze)**:
```json
{
  "detail": "File too large for quick analysis: 55.3MB. Max: 50MB"
}
```

#### 2. Model/Service Errors

**Model Not Ready**:
```json
{
  "detail": "Whisper model not ready. Check /health/models for status."
}
```

**Translation Model Unavailable**:
```json
{
  "detail": "Translator model not available"
}
```

**NER Model Error**:
```json
{
  "detail": "NER model not available"
}
```

#### 3. Task Errors

**Task Not Found**:
```json
{
  "detail": "Error retrieving task status"
}
```

**Task Failed During Processing**:
```json
{
  "task_id": "abc123",
  "status": "failed",
  "error": "Processing failed: Model inference error",
  "filename": "recording.wav"
}
```

#### 4. System Errors

**Worker Unavailable**:
```json
{
  "status": "no_workers",
  "message": "No Celery workers are running",
  "workers": 0
}
```

**System Overloaded**:
```json
{
  "status": "inspection_timeout",
  "message": "Workers busy - monitoring temporarily unavailable",
  "workers": "unknown"
}
```

### Error Handling Best Practices

**1. Always Check HTTP Status**:
```python
response = requests.post(url, ...)
if response.status_code != 200:
    print(f"Error: HTTP {response.status_code}")
    print(response.json())
```

**2. Handle Validation Errors**:
```python
try:
    response = requests.post(url, ...)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Validation error:", e.response.json()['detail'])
    elif e.response.status_code == 503:
        print("Service unavailable, check system health")
```

**3. Implement Retry Logic**:
```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.post(url, ...)
```

**4. Handle Task Failures**:
```python
status_data = response.json()
if status_data['status'] == 'failed':
    error = status_data.get('error', 'Unknown error')
    
    # Check if error is retryable
    if 'model' in error.lower():
        # Retry after checking system health
        pass
    elif 'File too large' in error:
        # Don't retry, file is invalid
        pass
```

**5. Monitor System Health**:
```python
def is_system_ready():
    try:
        response = requests.get('http://localhost:8123/audio/queue/status')
        data = response.json()
        return data['status'] == 'healthy'
    except:
        return False

if not is_system_ready():
    print("System not ready, waiting...")
    time.sleep(10)
```

---

## Additional Resources

### Related Documentation

- **Health Endpoints**: `/health/detailed`, `/health/models`
- **Individual Models**: `/whisper`, `/translate`, `/ner`, `/classifier`, `/summarizer`
- **API Documentation**: `/docs` (Swagger UI)
- **System Information**: `/info`

### Model Information

- **Translation Model**: [openchs/sw-en-opus-mt-mul-en-v1](https://huggingface.co/openchs/sw-en-opus-mt-mul-en-v1)
- **Whisper**: OpenAI Whisper Large V3 Turbo
- **License**: Apache 2.0

### Support

For technical support or questions:
- **Email**: info@bitz-itc.com
- **Organization**: OpenCHS (Open Child Helpline Services)

---

*Documentation version: 1.0  
Last updated: October 25, 2025  
API Base: `/audio`*