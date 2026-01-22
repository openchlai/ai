# Mock Asterisk Testing Guide

This guide walks you through testing the AI service using the mock Asterisk system without needing actual phone calls.

## Prerequisites

1. Audio files in WAV format (any sample rate, will be converted to 16kHz mono)
2. Running Redis server
3. Running Celery worker (for model processing)

## Setup

### Step 1: Prepare Test Audio Files

Copy your test audio files to the `test_audio` folder:

```bash
# Create folder if it doesn't exist
mkdir -p test_audio

# Copy your test audio files
cp /path/to/your/test_audio.wav test_audio/
```

**Supported formats**: WAV, MP3, GSM (requires ffmpeg)

### Step 2: Verify Your Audio Path

Check what audio files you have:

```bash
ls -lh test_audio/
```

---

## Testing Journey

## Journey 1: Real-Time Streaming Test

Test the real-time transcription and progressive analysis (simulates active call).

### 1.1 Configure for Real-Time Mode

Edit `.env` file:

```bash
# Processing Mode Configuration
DEFAULT_PROCESSING_MODE=dual
ENABLE_REALTIME_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true

# Streaming Configuration
ENABLE_STREAMING=true
STREAMING_PORT=8301

# Mock settings (keep disabled for now)
MOCK_ENABLED=false
```

### 1.2 Start the Services

**Terminal 1: Start Redis (if not running)**
```bash
redis-server
```

**Terminal 2: Start Celery Worker**
```bash
cd /home/k_nurf/ai_repo/ai/ai_service
celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery
```

**Terminal 3: Start FastAPI Server with Streaming**
```bash
cd /home/k_nurf/ai_repo/ai/ai_service
python -m app.main --enable-streaming
```

Wait for the server to start. You should see:
- `✅ Server started with TCP streaming enabled on port 8301`
- `🎧 Listening for Asterisk calls on 0.0.0.0:8301`

### 1.3 Run Mock Asterisk Client (Single Call)

**Terminal 4: Run Mock Client**
```bash
cd /home/k_nurf/ai_repo/ai/ai_service
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1
```

### 1.4 What to Observe

**In Terminal 3 (FastAPI Server):**
- Connection from mock client
- Call ID received
- Audio buffers filling up
- Every 5 seconds: transcription task submitted
- Progressive translation, NER, classification updates

**Look for logs like:**
```
🎙️  [client] Connection from 127.0.0.1:xxxxx
🆔 [client] call_id=1761627874.0
🎵 Submitted transcription task xxx for call 1761627874.0
📡 1761627874.0 1/5.0s: [transcribed text here]
```

**In Terminal 2 (Celery Worker):**
- Transcription tasks being processed
- Model inference happening
- Progressive analysis

**In Terminal 4 (Mock Client):**
- Connection successful
- Streaming progress (every 5 seconds)
- Completion status

### 1.5 Expected Result

✅ Call starts and creates session
✅ Audio chunks streamed every 10ms
✅ Transcription happens every 5 seconds
✅ Progressive analysis (translation, NER, classification) runs
✅ Call ends and triggers post-call processing (if enabled)

---

## Journey 2: Multiple Concurrent Calls Test

Test system handling multiple simultaneous calls.

### 2.1 Run Multiple Staggered Calls

**Terminal 4: Run 3 Calls with 15-second stagger**
```bash
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 3 --interval 15
```

### 2.2 What to Observe

- First call starts immediately
- After 15 seconds, second call starts (while first is still running)
- After 30 seconds, third call starts
- All calls process concurrently
- Each call has unique call_id (timestamp.0, timestamp.1, timestamp.2)

### 2.3 Monitor Active Sessions

While calls are running, check active sessions via API:

**Terminal 5:**
```bash
curl http://localhost:8123/api/v1/calls/active | jq
```

Should show all active call sessions with their status.

---

## Journey 3: Fast Mode Testing (Quick Iteration)

Speed up testing by streaming audio 10x faster than real-time.

### 3.1 Run in Fast Mode

```bash
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1 --speed 10
```

This will:
- Stream 10x faster (10ms chunks every 1ms instead of every 10ms)
- Complete a 2-minute audio in ~12 seconds
- Useful for rapid testing and debugging

---

## Journey 4: Post-Call Mock Mode Test

Test post-call processing using local audio files instead of SCP download.

### 4.1 Enable Mock Mode

Edit `.env`:

```bash
# Mock/Debug Audio Settings
MOCK_ENABLED=true
MOCK_AUDIO_FOLDER=./test_audio
MOCK_USE_FOLDER_FILES=true
MOCK_SKIP_SCP_DOWNLOAD=true

# Processing Mode Configuration
DEFAULT_PROCESSING_MODE=post_call
ENABLE_REALTIME_PROCESSING=false
ENABLE_POSTCALL_PROCESSING=true
```

### 4.2 Restart Services

**Stop and restart Terminal 3 (FastAPI server):**
```bash
# Ctrl+C to stop, then:
python -m app.main --enable-streaming
```

You should see in logs:
```
[mock] Mock mode enabled
[mock] Mock audio folder: ./test_audio
```

### 4.3 Test Mock Audio Download

**Option A: Via API Call**

Create a test to trigger post-call processing directly:

```bash
# Manually end a session (which triggers audio download)
curl -X POST "http://localhost:8123/api/v1/calls/test_call_123/end"
```

**Option B: Via Mock Streaming**

Run the mock client - it will stream the call, and when it ends, the system will:
1. Try to download audio via SCP
2. Detect `MOCK_ENABLED=true`
3. Switch to local file download
4. Find audio in `./test_audio` folder
5. Run full AI pipeline

```bash
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1
```

### 4.4 What to Observe

**In Terminal 3 (Server logs):**
```
[mock] Mock mode active - using local audio files for call 1761627874.0
[mock] Mock audio folder: ./test_audio
[mock] Loading audio for call 1761627874.0 from mock folder: ./test_audio
[mock] No file matching call_id=1761627874.0, using: ./test_audio/your_audio.wav
[local] Loaded 2.5MB audio file (wav): your_audio.wav
✅ [download] Successfully downloaded 2.5MB for call 1761627874.0
```

**In Terminal 2 (Celery worker):**
Full AI pipeline execution:
- Transcription
- Translation
- NER
- Classification
- QA Scoring
- Insights generation

### 4.5 Check Results

**Call session data:**
```bash
curl "http://localhost:8123/api/v1/calls/1761627874.0" | jq
```

**Mock notification output:**
```bash
# View the notification markdown file
cat mock_notifications/1761627874.0.md

# Or open in editor
code mock_notifications/1761627874.0.md
```

The markdown file contains all notifications with:
- Full transcript
- Full translation
- Classification details
- Extracted entities
- QA scoring results
- Processing summary

---

## Journey 5: End-to-End Test (Real-Time + Post-Call)

Test DUAL mode - both real-time streaming AND post-call processing.

### 5.1 Configure DUAL Mode

Edit `.env`:

```bash
# Processing Mode
DEFAULT_PROCESSING_MODE=dual
ENABLE_REALTIME_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true

# Mock mode
MOCK_ENABLED=true
MOCK_AUDIO_FOLDER=./test_audio
MOCK_SKIP_SCP_DOWNLOAD=true
```

### 5.2 Restart and Run

Restart FastAPI server (Terminal 3), then run:

```bash
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1
```

### 5.3 What to Observe

**During Call (Real-Time):**
- Progressive transcription every 5 seconds
- Progressive translation, NER, classification updates
- Streaming notifications to agent

**After Call (Post-Call):**
- Mock audio download from `./test_audio`
- Full AI pipeline with high-quality models
- Complete analysis with QA scoring and insights

---

## Troubleshooting

### Issue 1: "No audio files found"

**Problem**: Mock script can't find audio files

**Solution**:
```bash
# Check folder exists and has files
ls -la test_audio/

# Make sure path is correct
python scripts/mock_asterisk.py --audio-folder $(pwd)/test_audio --count 1
```

### Issue 2: "Connection refused to port 8301"

**Problem**: TCP server not running

**Solution**:
```bash
# Make sure server started with streaming enabled
python -m app.main --enable-streaming

# Check port in .env matches
grep STREAMING_PORT .env
```

### Issue 3: Mock mode not working

**Problem**: System still trying SCP even with mock enabled

**Solution**:
```bash
# Verify settings are loaded
curl http://localhost:8123/health/detailed | jq '.settings'

# Make sure to restart server after changing .env
# Ctrl+C and restart: python -m app.main --enable-streaming
```

### Issue 4: "Tasks stay in PENDING state"

**Problem**: Celery worker not processing tasks

**Solution**:
```bash
# Make sure worker is running with correct queues
celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery

# Check worker status
celery -A app.celery_app inspect ping
```

### Issue 5: Audio conversion errors

**Problem**: "ffmpeg not found" or conversion fails

**Solution**:
```bash
# Install ffmpeg
sudo apt-get install ffmpeg

# Or use WAV files directly (no conversion needed)
```

---

## Quick Reference Commands

### Check System Status
```bash
# Health check
curl http://localhost:8123/health/detailed | jq

# Active calls
curl http://localhost:8123/api/v1/calls/active | jq

# Celery worker status
celery -A app.celery_app inspect active
```

### Mock Client Commands
```bash
# Single call, real-time speed
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1

# 5 concurrent calls with 15s stagger
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 5 --interval 15

# Fast mode (10x speed)
python scripts/mock_asterisk.py --audio-folder ./test_audio --speed 10

# Different server
python scripts/mock_asterisk.py --audio-folder ./test_audio --host 192.168.1.100 --port 8301
```

### Enable/Disable Mock Mode
```bash
# Enable mock mode
sed -i 's/MOCK_ENABLED=false/MOCK_ENABLED=true/' .env

# Disable mock mode
sed -i 's/MOCK_ENABLED=true/MOCK_ENABLED=false/' .env

# Restart server to apply changes
```

---

## Expected Output Examples

### Successful Real-Time Call Log:
```
🎙️  [client] Connection from 127.0.0.1:45678
🆔 [client] call_id=1761627874.0
📥 [session] Started session for call 1761627874.0 (mode: dual)
🎵 Submitted transcription task abc-123 for call 1761627874.0
📡 1761627874.0 1/5.0s: Hello, how can I help you?
📡 1761627874.0 2/10.0s: I need assistance with...
🔄 [progressive] Processing window 1 for call 1761627874.0
✅ [progressive] Translation: "Hello, how can I help..."
✅ [progressive] Entities: {"PERSON": ["caller"], ...}
📡 1761627874.0 3/15.0s: ...continuing transcript...
🔌 [session] Call 1761627874.0 ended (connection_closed)
📥 [download] Starting audio download for call 1761627874.0 using method: mock
[mock] Loading audio for call 1761627874.0 from mock folder: ./test_audio
✅ [download] Successfully downloaded 2.5MB for call 1761627874.0
🚀 [pipeline] Starting AI pipeline for call 1761627874.0
```

### Successful Mock Audio Download:
```
[mock] Mock mode active - using local audio files for call 1761627874.0
[mock] Loading audio for call 1761627874.0 from mock folder: ./test_audio
[mock] No file matching call_id=1761627874.0, using: ./test_audio/sample.wav
[local] Accessing local audio file: ./test_audio/sample.wav
[local] Loaded 2.48MB audio file (wav): sample.wav
✅ [download] Successfully downloaded 2.48MB for call 1761627874.0
```

---

## What You Provided

You mentioned having a folder with test audio. Make sure to:

1. **Copy audio files** to `./test_audio/` folder
2. **Verify formats** (WAV is best, MP3/GSM need ffmpeg)
3. **Check file sizes** (larger files take longer to stream)

Then follow **Journey 1** for your first test!
