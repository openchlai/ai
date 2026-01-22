# Call Session Management API Documentation

**API Version:** 0.1.0
**Last Updated:** 2026-01-20
**Status:** Production

> **Note:** Response structures may vary slightly based on API version and configuration.
> This documentation reflects API version 0.1.0 running in production mode.

## Overview

The Call Session Management API provides comprehensive real-time call tracking, progressive transcription management, and AI-powered analysis for helpline calls. This API enables monitoring of active calls, retrieving transcripts, accessing progressive analysis results, and managing the call lifecycle.

**Base Path:** `/api/v1/calls`

---

## Quick Start

```bash
# Get all active calls
curl -X GET "http://localhost:8125/api/v1/calls/active"

# Get specific call details
curl -X GET "http://localhost:8125/api/v1/calls/{call_id}"

# Get call transcript with segments
curl -X GET "http://localhost:8125/api/v1/calls/{call_id}/transcript?include_segments=true"

# Get progressive analysis
curl -X GET "http://localhost:8125/api/v1/calls/{call_id}/progressive-analysis"

# Manually end a call
curl -X POST "http://localhost:8125/api/v1/calls/{call_id}/end"
```

---

## Core Features

### Real-Time Call Tracking
- Track active calls with cumulative transcripts
- Monitor call duration and segment counts
- View call status (active, completed, ended)

### Progressive Transcription
- Receive transcript segments as they arrive
- Access cumulative transcripts in real-time
- Paginate through historical segments

### Progressive AI Analysis
- Real-time translation as transcripts arrive
- Progressive entity extraction (NER)
- Evolving classification during calls
- Live QA scoring updates

### Call Lifecycle Management
- Manual call termination
- AI pipeline triggering
- Export capabilities for post-call analysis

---

## API Endpoints

### GET /api/v1/calls/active
Get all currently active call sessions.

**Response (200 OK):**
```json
[
  {
    "call_id": "1768919577.325299",
    "start_time": "2026-01-20T14:29:47.085694",
    "last_activity": "2026-01-20T14:29:47.085694",
    "connection_info": {
      "client_addr": ["192.168.10.3", 34490],
      "temp_connection_id": "192.168.10.3:34490:142946",
      "start_time": "2026-01-20T14:29:47.085683"
    },
    "transcript_segments": [],
    "cumulative_transcript": "",
    "total_audio_duration": 0.0,
    "segment_count": 0,
    "status": "active",
    "processing_mode": "post_call",
    "processing_plan": {
      "mode": "post_call",
      "streaming_enabled": false,
      "postcall_enabled": true,
      "streaming_config": null,
      "postcall_config": {
        "enable_insights": true,
        "enable_qa_scoring": true,
        "enable_summary": true,
        "processing_timeout": 300
      }
    }
  }
]
```

**Response Fields:**
- `call_id` (string): Unique call identifier (Asterisk call ID format)
- `start_time` (string): ISO-8601 timestamp when call session started
- `last_activity` (string): ISO-8601 timestamp of last activity
- `connection_info` (object): TCP connection details from Asterisk
  - `client_addr` (array): [IP address, port] of the connected client
  - `temp_connection_id` (string): Temporary connection identifier
  - `start_time` (string): Connection establishment timestamp
- `transcript_segments` (array): List of individual transcript segments
- `cumulative_transcript` (string): Combined transcript text
- `total_audio_duration` (float): Total audio duration in seconds
- `segment_count` (integer): Number of transcript segments received
- `status` (string): Call status (`active`, `connection_closed`, `completed`)
- `processing_mode` (string): Processing mode for this call (`realtime`, `post_call`, `hybrid`, `adaptive`)
- `processing_plan` (object): Detailed processing configuration
  - `mode` (string): Actual processing mode being used
  - `streaming_enabled` (boolean): Whether real-time streaming is enabled
  - `postcall_enabled` (boolean): Whether post-call processing is enabled
  - `streaming_config` (object/null): Configuration for streaming mode (if enabled)
  - `postcall_config` (object/null): Configuration for post-call mode (if enabled)

---

### GET /api/v1/calls/stats
Get aggregate statistics about all call sessions.

**Response (200 OK):**
```json
{
  "active_sessions": 6,
  "total_audio_duration": 0.0,
  "total_segments": 0,
  "average_duration_per_session": 0.0,
  "session_list": [
    "1768919428.325281",
    "1768919577.325299",
    "1768919584.325301"
  ]
}
```

**Response Fields:**
- `active_sessions` (integer): Number of currently active call sessions
- `total_audio_duration` (float): Total audio duration across all active sessions (seconds)
- `total_segments` (integer): Total transcript segments across all sessions
- `average_duration_per_session` (float): Average audio duration per session (seconds)
- `session_list` (array): List of active call IDs

**Note:** This endpoint returns statistics for currently active sessions only, not historical or completed calls.

---

### GET /api/v1/calls/{call_id}
Retrieve detailed information about a specific call.

**Path Parameters:**
- `call_id` (string, required): Unique call identifier

**Response (200 OK):**
```json
{
  "call_id": "call_123456",
  "status": "active",
  "cumulative_transcript": "Hello, this is 116 child helpline...",
  "total_audio_duration": 45.2,
  "segment_count": 12,
  "start_time": "2026-01-20T10:30:00",
  "last_activity": "2026-01-20T10:31:45"
}
```

**Error Responses:**
- `404`: Call session not found

---

### GET /api/v1/calls/{call_id}/transcript
Retrieve the transcript for a call, optionally with individual segments.

**Query Parameters:**
- `include_segments` (boolean, optional, default: false)

**Response (200 OK):**
```json
{
  "call_id": "call_123456",
  "cumulative_transcript": "Complete transcript text...",
  "total_duration": 45.2,
  "segment_count": 12,
  "status": "active",
  "start_time": "2026-01-20T10:30:00",
  "last_activity": "2026-01-20T10:31:45"
}
```

---

### POST /api/v1/calls/{call_id}/end
Manually terminate an active call session.

**Query Parameters:**
- `reason` (string, optional, default: "manual")

**Response (200 OK):**
```json
{
  "message": "Call session call_123456 ended successfully",
  "final_transcript": "Complete final transcript...",
  "total_duration": 120.5,
  "segment_count": 35
}
```

---

### GET /api/v1/calls/{call_id}/segments
Retrieve transcript segments with pagination.

**Query Parameters:**
- `limit` (integer, optional, default: 50, range: 1-1000)
- `offset` (integer, optional, default: 0)

**Response (200 OK):**
```json
{
  "call_id": "call_123456",
  "segments": [
    {
      "segment_id": 1,
      "text": "Hello, this is 116...",
      "timestamp": "2026-01-20T10:30:05",
      "duration": 3.5
    }
  ],
  "total_segments": 150,
  "offset": 0,
  "limit": 50,
  "has_more": true
}
```

---

### GET /api/v1/calls/{call_id}/progressive-analysis
Retrieve progressive AI analysis results.

**Response (200 OK):**
```json
{
  "call_id": "call_123456",
  "cumulative_translation": "Children need help urgently...",
  "latest_entities": [
    {
      "text": "Central Park",
      "label": "LANDMARK",
      "confidence": 0.92
    }
  ],
  "latest_classification": {
    "main_category": "VANE",
    "sub_category": "Physical Abuse",
    "priority": "high",
    "confidence": 0.87
  },
  "processing_stats": {
    "windows_processed": 5,
    "total_entities": 12,
    "classifications_made": 3
  }
}
```

---

### GET /api/v1/calls/{call_id}/entity-evolution
Track how extracted entities evolved during the call.

**Response (200 OK):**
```json
[
  {
    "window_id": 1,
    "timestamp": "2026-01-20T10:30:10",
    "text_window": "Hello, this is 116...",
    "entities": [
      {"text": "116", "label": "PHONE_NUMBER", "confidence": 0.95}
    ]
  }
]
```

---

### GET /api/v1/calls/{call_id}/classification-evolution
Track how case classification changed during the call.

**Response (200 OK):**
```json
[
  {
    "window_id": 1,
    "timestamp": "2026-01-20T10:30:15",
    "classification": {
      "main_category": "Information",
      "sub_category": "General Inquiry",
      "priority": "low",
      "confidence": 0.75
    }
  }
]
```

---

## Progressive Analysis Explained

### How It Works

As transcript segments arrive during a call, the system:

1. **Accumulates Text**: Builds cumulative transcript
2. **Creates Windows**: Groups text into analysis windows (150-300 chars)
3. **Translates**: English translation for each window
4. **Extracts Entities**: NER on translated text
5. **Classifies**: Case classification with confidence
6. **Notifies Agents**: Real-time alerts on critical entities or high-priority cases

### Analysis Windows Configuration

- Min window size: 150 characters
- Target window size: 300 characters
- Overlap: 50 characters
- Processing interval: 30 seconds

---

## Integration Examples

### Python Example

```python
import requests

class CallSessionClient:
    def __init__(self, base_url="http://localhost:8125"):
        self.base_url = base_url

    def get_active_calls(self):
        response = requests.get(f"{self.base_url}/api/v1/calls/active")
        response.raise_for_status()
        return response.json()

    def get_progressive_analysis(self, call_id):
        response = requests.get(
            f"{self.base_url}/api/v1/calls/{call_id}/progressive-analysis"
        )
        response.raise_for_status()
        return response.json()

# Usage
client = CallSessionClient()
active_calls = client.get_active_calls()

for call in active_calls:
    analysis = client.get_progressive_analysis(call['call_id'])
    if analysis['latest_classification']['priority'] == 'high':
        print(f"⚠️ HIGH PRIORITY: {call['call_id']}")
```

### JavaScript Example

```javascript
async function monitorActiveCalls() {
    const response = await fetch('http://localhost:8125/api/v1/calls/active');
    const calls = await response.json();

    for (const call of calls) {
        const analysisResponse = await fetch(
            `http://localhost:8125/api/v1/calls/${call.call_id}/progressive-analysis`
        );
        const analysis = await analysisResponse.json();

        if (analysis.latest_classification.priority === 'high') {
            console.warn(`⚠️ HIGH PRIORITY: ${call.call_id}`);
        }
    }
}

// Poll every 10 seconds
setInterval(monitorActiveCalls, 10000);
```

---

## Best Practices

### 1. Polling Strategy
- Poll active calls every 5-10 seconds for transcript updates
- Poll progressive analysis every 15-30 seconds
- Use pagination for calls with many segments

### 2. Error Handling
Always handle 404 errors gracefully - calls may end during polling.

### 3. Priority Detection
Monitor classification evolution for priority escalation and trigger alerts.

### 4. Export Before Cleanup
Always export call data before any cleanup operations.

---

## Related Documentation

- [Notifications API](notifications.md)
- [Agent Feedback API](agent_feedback.md)
- [Processing Mode API](processing_mode.md)
- [Streaming API](streaming.md)

---
