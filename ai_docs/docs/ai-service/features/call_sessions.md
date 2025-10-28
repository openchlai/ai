# Call Sessions API — Documentation

Last updated: October 24, 2025
Version: 1.0.0
API Base URL: http://192.168.8.18:8123

## 1. API Endpoint Overview

The Call Sessions API provides endpoints to manage, monitor, and analyze call sessions in the BITZ AI pipeline. It enables:

- Real-time session monitoring and status updates
- Post-call processing (transcription, translation, NER, classification, summarization, QA)
- Progressive (realtime) analysis during calls
- Exporting call data in JSON or plain text for downstream systems
- Agent notification integration for alerts and completion notifications

Processing modes supported:

- postcall_only — process audio after call completion
- realtime — live streaming analysis during calls
- hybrid — realtime notifications plus post-call deep analysis

---

## 2. Architecture & Integration

### 2.1 System components

- Asterisk PBX — source of call audio
- Session Manager — tracks active calls and manages audio streams
- Real-time Processor (optional) — streaming transcription & analysis
- Post-call Pipeline — runs full AI pipeline on recorded audio
- Model Services — transcription (Whisper), translation (MarianMT), NER, classification, summarization, QA
- Agent Notification Service — sends notifications to agents
- Call Sessions API — provides access to session metadata, transcripts, exports, and processing status

### 2.2 Data flow

Active call flow:
1. Call initiated → session created in Session Manager
2. Audio streamed → real-time processor (if enabled)
3. Progressive transcription/translation → agent notifications (optional)
4. Call ends → post-call processing triggered
5. Post-call pipeline completes → analysis and exports available via API

Post-call processing flow:
- Audio pulled from PBX (SCP, S3, or other configured method)
- Transcription → translation → NER → classification → summarization → QA
- Unified insights produced and optionally pushed to agents or exported

### 2.3 Configuration

Configuration is provided via environment variables or a settings file. Avoid hardcoding secrets; use secret stores for credentials.

Example environment variables (redacted placeholders used for sensitive values):

```bash
# API
API_HOST=0.0.0.0
API_PORT=8123

# Audio retrieval
AUDIO_DOWNLOAD_METHOD=scp
SCP_USER=helpline
SCP_SERVER=192.168.10.3
SCP_PASSWORD=<REDACTED> # Use SSH keys or secret store instead of plain password
REMOTE_PATH_TEMPLATE=/home/dat/helpline/calls/{call_id}.gsm

# Processing options
ENABLE_FULL_PIPELINE=true
WHISPER_MODEL=openchs/asr-whisper-helpline-sw-v1
TRANSLATION_MODEL=openchs/sw-en-opus-mt-mul-en-v1
ENABLE_DIARIZATION=false
ENABLE_NOISE_REDUCTION=true
CONVERT_TO_WAV=true
ENABLE_INSIGHTS_GENERATION=true
ENABLE_QA_SCORING=true
NOTIFY_COMPLETION=true

# Paths and limits
MODELS_PATH=/app/models
TEMP_PATH=/app/temp
LOGS_PATH=/app/logs
DOWNLOAD_TIMEOUT_SECONDS=60
PROCESSING_TIMEOUT_SECONDS=300
MAX_CONCURRENT_PROCESSING=5
```

---

## 3. Endpoints Reference — conventions

- All endpoints return JSON by default unless otherwise noted.
- Error responses follow a standard format:

```json
{ "detail": "Error message description" }
```

- Validation errors follow this format:

```json
{
  "detail": [
    { "loc": ["path","call_id"], "msg": "Invalid call_id format", "type": "value_error" }
  ]
}
```

---

### 3.1 Get Active Calls

GET /api/v1/calls/active

Description: Returns currently active call sessions and their realtime status.

Response (200):

```json
[
  {
    "call_id": "string",
    "start_time": "ISO8601",
    "last_activity": "ISO8601",
    "connection_info": {
      "client_addr": ["ip", port],
      "temp_connection_id": "string",
      "start_time": "ISO8601"
    },
    "transcript_segments": [],
    "cumulative_transcript": "string",
    "total_audio_duration": 0,
    "segment_count": 0,
    "status": "active|connection_closed",
    "processing_mode": "postcall_only|realtime|hybrid",
    "processing_plan": {}
  }
]
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/active' -H 'Accept: application/json'
```

---

### 3.2 Get Call Stats

GET /api/v1/calls/stats

Description: Aggregated statistics for sessions.

Response (200):

```json
{
  "active_sessions": 0,
  "total_audio_duration": 0,
  "total_segments": 0,
  "average_duration_per_session": 0,
  "session_list": ["call_id1", "call_id2"]
}
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/stats' -H 'Accept: application/json'
```

---

### 3.3 Get Call Session

GET /api/v1/calls/{call_id}

Description: Get detailed info about a specific call.

Path parameter:
- call_id (string) — required

Response (200):

```json
{
  "call_id": "string",
  "start_time": "ISO8601",
  "last_activity": "ISO8601",
  "connection_info": {},
  "transcript_segments": [],
  "cumulative_transcript": "string",
  "total_audio_duration": 0,
  "segment_count": 0,
  "status": "string",
  "processing_mode": "string",
  "processing_plan": {}
}
```

Error responses:
- 404: Call session not found
- 422: Validation error

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887' -H 'Accept: application/json'
```

---

### 3.4 Get Call Transcript

GET /api/v1/calls/{call_id}/transcript

Query parameters:
- include_segments (boolean, default: false) — include individual transcript segments

Response (200):

```json
{
  "call_id": "string",
  "cumulative_transcript": "string",
  "language": "sw",
  "segment_count": 0,
  "total_duration": 0,
  "segments": [
    { "text": "string", "start_time": 0, "end_time": 0, "confidence": 0.0 }
  ]
}
```

Examples:

```bash
# With segments
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/transcript?include_segments=true' -H 'Accept: application/json'

# Without segments
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/transcript' -H 'Accept: application/json'
```

---

### 3.5 Manually End Call

POST /api/v1/calls/{call_id}/end

Query parameters:
- reason (string, default: "manual") — optional reason for ending the call

Response (200):

```json
"Call ended successfully"
```

Error responses:
- 404: Call session not found
- 422: Validation error

Example:

```bash
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/end?reason=manual' -H 'Accept: application/json'
```

---

### 3.6 Get Call Segments

GET /api/v1/calls/{call_id}/segments

Response (200):

```json
[
  {
    "segment_id": 0,
    "text": "string",
    "start_time": 0.0,
    "end_time": 0.0,
    "duration": 0.0,
    "confidence": 0.0,
    "speaker": "string"
  }
]
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/segments' -H 'Accept: application/json'
```

---

### 3.7 Export Call for AI Pipeline

GET /api/v1/calls/{call_id}/export

Query parameters:
- format (string, optional, default: json) — one of: json, text

Response (200) — JSON format (example):

```json
{
  "call_id": "string",
  "metadata": { "start_time": "ISO8601", "end_time": "ISO8601", "duration": 0, "status": "string" },
  "transcription": { "original": "string", "language": "sw" },
  "translation": { "translated": "string", "language": "en" },
  "entities": {},
  "classification": {},
  "summary": {},
  "insights": {},
  "processing_info": {}
}
```

Plain-text export example (abridged):

```
=== CALL EXPORT ===
Call ID: {call_id}
Date: {start_time}
Duration: {duration} seconds
Status: {status}

--- ORIGINAL TRANSCRIPT (Swahili) ---
{transcript_text}

--- ENGLISH TRANSLATION ---
{translation_text}

--- NAMED ENTITIES ---
Persons: {person_list}
Locations: {location_list}

--- SUMMARY ---
{summary_text}

=== END OF EXPORT ===
```

Examples:

```bash
# JSON export
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/export?format=json' -H 'Accept: application/json' -o call_export.json

# Text export
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/export?format=text' -H 'Accept: application/json' -o call_export.txt
```

---

### 3.8 Trigger AI Pipeline Processing

POST /api/v1/calls/{call_id}/trigger-ai-pipeline

Response (200):

```json
"AI pipeline processing triggered successfully"
```

Error responses:
- 404: Call session not found
- 422: Validation error
- 503: Service unavailable

Example:

```bash
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/trigger-ai-pipeline' -H 'Accept: application/json'
```

---

### 3.9 Get Progressive Analysis

GET /api/v1/calls/{call_id}/progressive-analysis

Response (200):

```json
{
  "call_id": "string",
  "cumulative_translation": "string",
  "translation_windows": 0,
  "latest_entities": {},
  "latest_classification": {},
  "evolution_data": {}
}
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/progressive-analysis' -H 'Accept: application/json'
```

---

### 3.10 Get Call Translation

GET /api/v1/calls/{call_id}/translation

Response (200):

```json
{
  "call_id": "string",
  "cumulative_translation": "string",
  "language": "en",
  "source_language": "sw"
}
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/translation' -H 'Accept: application/json'
```

---

### 3.11 Get Entity Evolution

GET /api/v1/calls/{call_id}/entity-evolution

Response (200): array of timestamped windows showing entity discovery and cumulative entities.

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/entity-evolution' -H 'Accept: application/json'
```

---

### 3.12 Get Classification Evolution

GET /api/v1/calls/{call_id}/classification-evolution

Response (200): array of classification snapshots with change indicators.

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/classification-evolution' -H 'Accept: application/json'
```

---

### 3.13 Get Agent Service Health

GET /api/v1/calls/agent-service/health

Response (200):

```json
{
  "status": "healthy|unhealthy",
  "service_name": "agent_notification_service",
  "timestamp": "ISO8601",
  "checks": { "api_connectivity": true, "authentication": true },
  "details": {}
}
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/agent-service/health' -H 'Accept: application/json'
```

---

### 3.14 Test Agent Auth

POST /api/v1/calls/agent-service/test-auth

Response (200):

```json
{ "status": "success|failed", "token_obtained": true, "token_expires_in": 3600 }
```

Example:

```bash
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/agent-service/test-auth' -H 'Accept: application/json'
```

---

### 3.15 Test Agent Notification

POST /api/v1/calls/agent-service/test-notification?call_id={call_id}

Response (200):

```json
{ "status": "success|failed", "notification_sent": true, "agent_response_code": 200 }
```

Example:

```bash
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/agent-service/test-notification?call_id=test_123' -H 'Accept: application/json'
```

---

### 3.16 Get Processing Status

GET /api/v1/calls/processing/status

Response (200): global processing overview.

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/processing/status' -H 'Accept: application/json'
```

---

### 3.17 Get Call Processing Status

GET /api/v1/calls/{call_id}/processing

Response (200):

```json
{
  "call_id": "string",
  "processing_status": "pending|in_progress|completed|failed",
  "current_stage": "string",
  "stages_completed": [],
  "stages_remaining": [],
  "progress_percentage": 0.0,
  "started_at": "ISO8601",
  "estimated_completion": "ISO8601",
  "errors": [],
  "pipeline_config": {}
}
```

Example:

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/processing' -H 'Accept: application/json'
```

---

## 4. Usage Examples

### 4.1 Monitoring Active Calls

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/stats' -H 'Accept: application/json'
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/active' -H 'Accept: application/json'
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887' -H 'Accept: application/json'
```

### 4.2 Processing Complete Calls

```bash
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/trigger-ai-pipeline' -H 'Accept: application/json'
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/processing' -H 'Accept: application/json'
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/processing/status' -H 'Accept: application/json'
```

### 4.3 Exporting Call Data

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/export?format=json' -H 'Accept: application/json' -o call_export.json
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/export?format=text' -H 'Accept: application/json' -o call_export.txt
```

### 4.4 Progressive Analysis

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/progressive-analysis' -H 'Accept: application/json'
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/translation' -H 'Accept: application/json'
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/1761295415.12887/entity-evolution' -H 'Accept: application/json'
```

### 4.5 Agent Service Testing

```bash
curl -X GET 'http://192.168.8.18:8123/api/v1/calls/agent-service/health' -H 'Accept: application/json'
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/agent-service/test-auth' -H 'Accept: application/json'
curl -X POST 'http://192.168.8.18:8123/api/v1/calls/agent-service/test-notification?call_id=test_123' -H 'Accept: application/json'
```

---

## 5. Data Models

### 5.1 Call Session Object

```json
{
  "call_id": "string",
  "start_time": "ISO8601",
  "last_activity": "ISO8601",
  "connection_info": { "client_addr": ["ip", port], "temp_connection_id": "string" },
  "transcript_segments": [],
  "cumulative_transcript": "string",
  "total_audio_duration": 0,
  "segment_count": 0,
  "status": "active|connection_closed|completed|failed",
  "processing_mode": "postcall_only|realtime|hybrid",
  "processing_plan": {}
}
```

### 5.2 Transcript Segment Object

```json
{
  "segment_id": 0,
  "text": "string",
  "start_time": 0.0,
  "end_time": 0.0,
  "duration": 0.0,
  "confidence": 0.0,
  "speaker": "string"
}
```

### 5.3 Translation Object

```json
{
  "call_id": "string",
  "cumulative_translation": "string",
  "language": "en",
  "source_language": "sw",
  "translation_model": "openchs/sw-en-opus-mt-mul-en-v1"
}
```

(Additional model examples omitted for brevity — follow same JSON style.)

---

## 6. Production Considerations

### Performance
- Active calls listing: < 100ms (target)
- Transcript retrieval: < 200ms (target)
- Export generation: depends on size (500ms — 2s typical)

Processing time estimates (approximate):
- Transcription: ~15–30s per minute of audio (model-dependent)
- Translation / NER / classification: per-call times vary by model/length

### Rate limiting and best practices
- GET: 100 req/min per client (recommended)
- POST: 20 req/min per client (recommended)
- Use exponential backoff and caches for frequent requests

### Security
- Use HTTPS in production
- Store secrets in a secret manager (do not commit credentials)
- Restrict API to internal network or authorized IPs

### Data retention
- Active sessions: memory while call is active
- Completed sessions: configurable (example: 24 hours in-memory, then archive)
- Audio retention: configurable (default example: 30 days)

---

## 7. Troubleshooting

Common checks:
- Verify call exists via `/api/v1/calls/active` and `/api/v1/calls/stats`
- Check processing status endpoints before requesting exports
- Use health endpoints to validate model readiness: `/health/models` and `/health/detailed`

Logs:
- Application logs: `./logs/app.log` or `/app/logs/app.log` (container)
- Processing logs: `/app/logs/processing.log`

---

## 8. API Versioning

- Current: v1
- Version format: `/api/v{version}/`
- Deprecation policy: deprecated endpoints supported for 6 months with migration notes

---

## 9. Support and Contact

- Email: info@bitz-itc.com
- For bugs: include call_id, endpoint, request/response, timestamp, and relevant logs

---

## 10. Changelog

### v1.0.0 — Initial release
- Active call monitoring
- Post-call processing pipeline
- Progressive analysis endpoints
- Export functionality and agent notifications

Planned features: WebSocket realtime updates, batch processing API, webhooks, advanced filtering.

---

## 11. License

This documentation is proprietary to BITZ ITC and provided for authorized users only.

© 2025 BITZ ITC. All rights reserved.

---

**Documentation Version:** 1.0.0  
**Last Updated:** October 28, 2025  
**API Base URL:** http://192.168.8.18:8123
