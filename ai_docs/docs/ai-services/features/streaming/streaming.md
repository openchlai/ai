# Real-Time Streaming API Documentation

**API Version:** 0.1.0
**Last Updated:** 2026-01-20
**Status:** Production

> **Note:** Response structures may vary slightly based on API version and configuration.
> This documentation reflects API version 0.1.0 running in production mode.

## Overview

The Streaming API provides two approaches for receiving real-time progress updates during audio processing: **Server-Sent Events (SSE)** for standard HTTP streaming and **Redis Pub/Sub** for ultra-low latency partial results.

---

## Table of Contents

1. [Streaming Approaches](#streaming-approaches)
2. [Server-Sent Events (SSE)](#server-sent-events-sse)
3. [Redis Pub/Sub Streaming](#redis-pubsub-streaming)
4. [Integration Examples](#integration-examples)
5. [Best Practices](#best-practices)

---

## Streaming Approaches

### When to Use Which?

| Feature | SSE (`/audio/process-stream`) | Redis Pub/Sub (`/audio/process-stream-realtime`) |
|---------|-------------------------------|---------------------------------------------------|
| **Latency** | Standard (2-5s updates) | Ultra-low (real-time) |
| **Complexity** | Simple (standard HTTP) | Moderate (requires Redis) |
| **Partial Results** | Progress updates only | Transcription chunks, partial translations |
| **Overhead** | Low | Higher (Redis infrastructure) |
| **Use Case** | Most production scenarios | Real-time agent assistance |

---

## Server-Sent Events (SSE)

### Endpoint: POST /audio/process-stream

**Description:** Process audio with real-time updates via Server-Sent Events. No polling required - server pushes updates to client.

**Request:**
```bash
curl -X POST "http://localhost:8125/audio/process-stream" \
  -F "audio=@call_recording.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  -F "include_insights=true"
```

**Supported Audio Formats:** WAV, MP3, FLAC, M4A, OGG, WEBM
**Max File Size:** 100MB

---

### Event Stream Structure

The SSE stream sends events in this format:
```
data: {JSON_OBJECT}\n\n
```

---

### Event Types

#### 1. Submitted Event
```json
{
  "task_id": "abc123...",
  "status": "submitted",
  "message": "Audio processing started",
  "filename": "call_recording.wav",
  "file_size_mb": 2.34,
  "estimated_time": "15-60 seconds",
  "timestamp": "2026-01-20T10:30:00"
}
```

#### 2. Progress Events
```json
{
  "task_id": "abc123...",
  "status": "PROCESSING",
  "progress": 35,
  "step": "transcription",
  "message": "Processing: transcription",
  "elapsed_time": 12.5,
  "timestamp": "2026-01-20T10:30:12"
}
```

**Possible Steps:**
- `transcription` - Converting audio to text
- `translation` - Translating to English
- `entity_extraction` - Running NER model
- `classification` - Classifying case
- `qa_evaluation` - Running QA model
- `summarization` - Generating summary

#### 3. Heartbeat Events
```json
{
  "task_id": "abc123...",
  "status": "PROCESSING",
  "heartbeat": true,
  "elapsed_time": 25.0,
  "timestamp": "2026-01-20T10:30:25"
}
```

**Note:** Sent every 10 seconds to keep connection alive.

#### 4. Completed Event
```json
{
  "task_id": "abc123...",
  "status": "completed",
  "result": {
    "transcription": "Hello, this is 116 child helpline...",
    "translation": "Hello, this is 116 child helpline...",
    "entities": [...],
    "classification": {...},
    "qa_evaluations": {...},
    "summary": "...",
    "processing_time": 45.2
  },
  "processing_time": 45.2,
  "timestamp": "2026-01-20T10:30:45",
  "message": "Audio processing completed successfully"
}
```

#### 5. Failed Event
```json
{
  "task_id": "abc123...",
  "status": "failed",
  "error": "Model loading error: classifier_model not ready",
  "processing_time": 15.3,
  "timestamp": "2026-01-20T10:30:15",
  "message": "Audio processing failed"
}
```

#### 6. Timeout Event
```json
{
  "task_id": "abc123...",
  "status": "timeout",
  "error": "Processing timeout after 5 minutes",
  "elapsed_time": 300.0,
  "timestamp": "2026-01-20T10:35:00"
}
```

---

### Client Implementation Examples

#### Python (requests + sseclient-py)

```python
import json
import requests
from sseclient import SSEClient

def process_audio_streaming(audio_file_path, language="sw"):
    """Process audio with SSE streaming"""

    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {
            'language': language,
            'include_translation': 'true',
            'include_insights': 'true'
        }

        response = requests.post(
            'http://localhost:8125/audio/process-stream',
            files=files,
            data=data,
            stream=True
        )

        client = SSEClient(response)

        for event in client.events():
            data = json.loads(event.data)
            
            status = data.get('status')
            print(f"Status: {status}")

            if 'progress' in data:
                print(f"Progress: {data['progress']}% - {data.get('step', 'processing')}")

            if status == 'completed':
                print("\n Processing complete!")
                print(f"Transcript: {data['result']['transcription'][:100]}...")
                return data['result']

            elif status == 'failed':
                print(f"\n Processing failed: {data['error']}")
                return None

# Usage
result = process_audio_streaming('call_recording.wav', language='sw')
```

**Install dependencies:**
```bash
pip install requests sseclient-py
```

---

#### JavaScript (Fetch API)

```javascript
async function processAudioStreaming(audioFile, language = 'sw') {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('language', language);
    formData.append('include_translation', 'true');
    formData.append('include_insights', 'true');

    const response = await fetch('http://localhost:8125/audio/process-stream', {
        method: 'POST',
        body: formData
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = '';

    while (true) {
        const {value, done} = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, {stream: true});

        // Split by double newline (SSE message delimiter)
        const messages = buffer.split('\n\n');
        buffer = messages.pop(); // Keep incomplete message in buffer

        for (const message of messages) {
            if (!message.trim()) continue;

            // Parse SSE format: "data: {json}"
            if (message.startsWith('data: ')) {
                const jsonData = message.slice(6);
                const data = JSON.parse(jsonData);

                console.log(`Status: ${data.status}`);

                if (data.progress) {
                    console.log(`Progress: ${data.progress}% - ${data.step || 'processing'}`);
                }

                if (data.status === 'completed') {
                    console.log('\n Processing complete!');
                    console.log('Transcript:', data.result.transcription.substring(0, 100) + '...');
                    return data.result;
                }

                if (data.status === 'failed') {
                    console.error(`\n Processing failed: ${data.error}`);
                    return null;
                }
            }
        }
    }
}

// Usage (in browser)
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    const result = await processAudioStreaming(file, 'sw');
});
```

---

#### cURL (Basic Testing)

```bash
# Note: cURL will show raw SSE stream
curl -X POST "http://localhost:8125/audio/process-stream" \
  -F "audio=@call_recording.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  -F "include_insights=true" \
  -N  # Disable buffering to see real-time output
```

---

## Redis Pub/Sub Streaming

### Endpoint: POST /audio/process-stream-realtime

**Description:** Process audio with REAL-TIME Redis pub/sub streaming. Streams partial results as they're generated (transcription chunks, partial translations, etc.).

**Request:**
```bash
curl -X POST "http://localhost:8125/audio/process-stream-realtime" \
  -F "audio=@call_recording.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  -F "include_insights=true"
```

---

### Event Stream Structure

Same SSE format as standard streaming, but with additional granular events:

#### Partial Transcription Events
```json
{
  "task_id": "abc123...",
  "step": "transcription_partial",
  "progress": 15,
  "partial_result": {
    "transcript_chunk": "Hello, this is 116 child helpline",
    "chunk_index": 1,
    "total_chunks_so_far": 1
  },
  "timestamp": "2026-01-20T10:30:05"
}
```

#### Partial Translation Events
```json
{
  "task_id": "abc123...",
  "step": "translation_partial",
  "progress": 45,
  "partial_result": {
    "translation_chunk": "Hello, this is 116 child helpline",
    "cumulative_translation": "Hello, this is 116 child helpline. How can I help you today?"
  },
  "timestamp": "2026-01-20T10:30:15"
}
```

---

### Client Implementation (Python)

```python
import json
import requests
from sseclient import SSEClient

def process_audio_realtime(audio_file_path, language="sw"):
    """Process audio with Redis pub/sub streaming"""

    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {
            'language': language,
            'include_translation': 'true',
            'include_insights': 'true'
        }

        response = requests.post(
            'http://localhost:8125/audio/process-stream-realtime',
            files=files,
            data=data,
            stream=True
        )

        client = SSEClient(response)
        
        cumulative_transcript = ""
        cumulative_translation = ""

        for event in client.events():
            data = json.loads(event.data)
            
            step = data.get('step')

            # Handle partial transcription
            if step == 'transcription_partial':
                chunk = data['partial_result']['transcript_chunk']
                cumulative_transcript += " " + chunk
                print(f" Transcript: {cumulative_transcript}")

            # Handle partial translation
            elif step == 'translation_partial':
                cumulative_translation = data['partial_result']['cumulative_translation']
                print(f" Translation: {cumulative_translation}")

            # Handle completion
            elif step == 'completed':
                print("\n Processing complete!")
                return data.get('result')

            # Handle failure
            elif step == 'failed':
                print(f"\n Failed: {data.get('error')}")
                return None

# Usage
result = process_audio_realtime('call_recording.wav', language='sw')
```

---

## Integration Examples

### React Component (SSE)

```jsx
import React, { useState } from 'react';

function AudioProcessor() {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('idle');
    const [result, setResult] = useState(null);

    async function processAudio(file) {
        setStatus('processing');
        setProgress(0);

        const formData = new FormData();
        formData.append('audio', file);
        formData.append('language', 'sw');
        formData.append('include_translation', 'true');
        formData.append('include_insights', 'true');

        const response = await fetch('http://localhost:8125/audio/process-stream', {
            method: 'POST',
            body: formData
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const {value, done} = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, {stream: true});
            const messages = buffer.split('\n\n');
            buffer = messages.pop();

            for (const message of messages) {
                if (message.startsWith('data: ')) {
                    const data = JSON.parse(message.slice(6));

                    if (data.progress) {
                        setProgress(data.progress);
                    }

                    if (data.status === 'completed') {
                        setStatus('completed');
                        setResult(data.result);
                        return;
                    }

                    if (data.status === 'failed') {
                        setStatus('failed');
                        return;
                    }
                }
            }
        }
    }

    return (
        <div>
            <input type="file" onChange={(e) => processAudio(e.target.files[0])} />
            {status === 'processing' && <progress value={progress} max="100" />}
            {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
        </div>
    );
}
```

---

## Best Practices

### 1. Connection Management
- Set appropriate timeouts (5 minutes default)
- Handle reconnection logic for network failures
- Close connections properly when done

### 2. Error Handling
```python
try:
    result = process_audio_streaming(audio_file)
except requests.exceptions.ConnectionError:
    print("Connection lost, retrying...")
except requests.exceptions.Timeout:
    print("Request timed out")
```

### 3. Progress Visualization
Always show progress to users:
- Display progress percentage
- Show current processing step
- Estimate remaining time (based on elapsed_time)

### 4. Heartbeat Handling
Filter out heartbeat events in your UI to avoid unnecessary updates.

### 5. Large File Handling
For files > 50MB:
- Consider using Redis Pub/Sub for better chunk handling
- Show file upload progress before processing
- Warn users about longer processing times

---

## Comparison with Polling

### Polling Approach (OLD)
```python
# Submit task
response = requests.post('/audio/process', files={'audio': file})
task_id = response.json()['task_id']

# Poll for status
while True:
    status = requests.get(f'/audio/task/{task_id}').json()
    if status['status'] == 'completed':
        break
    time.sleep(2)
```

**Issues:**
- Wastes bandwidth with repeated requests
- Fixed polling interval causes delays
- Server load from constant polling

### Streaming Approach (NEW)
```python
# Single connection, server pushes updates
for event in stream:
    # Receive updates as they happen
    handle_event(event)
```

**Benefits:**
- No wasted requests
- Real-time updates
- Lower server load
- Better user experience

---

## Related Documentation

- [Audio Processing API](audio-api-reference.md) - Standard polling-based approach
- [Call Sessions API](call_sessions.md) - WebSocket streaming for live calls
- [Deployment Guide](../deployment/ai-service-deployment.md)

---
