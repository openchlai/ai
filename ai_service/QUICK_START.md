# Quick Start: Testing with Mock Asterisk

Get started testing the AI service in **5 minutes** without needing actual phone calls.

## Prerequisites Checklist

- [ ] Audio files in WAV format (you mentioned you have a folder with audio files)
- [ ] Redis running (`redis-server`)
- [ ] Python environment active
- [ ] Port 8301 available for TCP server

## Step-by-Step Guide

### 1️⃣ Add Your Audio Files

Copy your test audio files to the `test_audio` folder:

```bash
# Navigate to project
cd /home/k_nurf/ai_repo/ai/ai_service

# Copy your audio files
cp /your/path/to/audio/*.wav ./test_audio/

# Verify files are there
ls -lh test_audio/
```

### 2️⃣ Start Redis (if not running)

```bash
# Terminal 1
redis-server
```

### 3️⃣ Start Celery Worker

```bash
# Terminal 2
cd /home/k_nurf/ai_repo/ai/ai_service
celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery
```

Wait for: `✅ celery@... ready`

### 4️⃣ Start AI Service Server

```bash
# Terminal 3
cd /home/k_nurf/ai_repo/ai/ai_service
python -m app.main --enable-streaming
```

Wait for:
- `✅ Server started with TCP streaming enabled on port 8301`
- `🎧 Listening for Asterisk calls`

### 5️⃣ Run Mock Test

Choose one:

**Option A: Using Quick Test Script (Recommended)**
```bash
# Terminal 4
cd /home/k_nurf/ai_repo/ai/ai_service
./scripts/quick_test_mock.sh realtime 1
```

**Option B: Using Mock Script Directly**
```bash
# Terminal 4
cd /home/k_nurf/ai_repo/ai/ai_service
python scripts/mock_asterisk.py --audio-folder ./test_audio --count 1
```

### 6️⃣ Watch the Magic Happen! ✨

**In Terminal 3 (Server):**
```
🎙️  [client] Connection from 127.0.0.1:xxxxx
🆔 [client] call_id=1761627874.0
🎵 Submitted transcription task for call 1761627874.0
📡 1761627874.0 1/5.0s: [your transcribed audio]
```

**In Terminal 2 (Celery):**
```
[INFO] Received task: process_streaming_audio_task
[INFO] Transcription: [your audio text]
```

**In Terminal 4 (Mock Client):**
```
Connected to localhost:8301
Sent call ID: 1761627874.0
Streaming sample.wav: 120.5s (1205 chunks, 1.0x speed)
  Progress: 5.0s / 120.5s
  Progress: 10.0s / 120.5s
  ...
Finished streaming
```

---

## What You Should See

### During Call (Real-Time)
- ✅ Connection established
- ✅ Call ID sent (Asterisk format: `timestamp.sequence`)
- ✅ Audio streaming every 10ms (320-byte chunks)
- ✅ Transcription every 5 seconds
- ✅ Progressive translation, NER, classification

### After Call Ends
- ✅ Call session finalized
- ✅ Post-call processing triggered (if enabled)
- ✅ Full AI pipeline execution
- ✅ Results stored in database

---

## Quick Tests

### Test 1: Single Call (2 minutes)
```bash
./scripts/quick_test_mock.sh realtime 1
```

### Test 2: Fast Mode (12 seconds for 2-min audio)
```bash
./scripts/quick_test_mock.sh fast 1
```

### Test 3: Multiple Concurrent Calls
```bash
./scripts/quick_test_mock.sh realtime 3 15
# 3 calls, start each 15 seconds apart
```

---

## Enable Post-Call Mock Mode

To test post-call processing with local audio files instead of SCP:

### 1. Edit `.env` file:
```bash
nano .env
```

Change these lines:
```env
MOCK_ENABLED=true
MOCK_AUDIO_FOLDER=./test_audio
MOCK_SKIP_SCP_DOWNLOAD=true
```

### 2. Restart server (Terminal 3):
```bash
# Press Ctrl+C to stop
python -m app.main --enable-streaming
```

You should see:
```
ℹ️  [config] Mock mode enabled
ℹ️  [config] Mock audio folder: ./test_audio
```

### 3. Run test:
```bash
./scripts/quick_test_mock.sh realtime 1
```

Now when the call ends, instead of trying SCP download, it will:
- Use local files from `./test_audio`
- Match by call_id or use any available file
- Run full AI pipeline with the audio

---

## Verify It's Working

### Check Active Calls
```bash
curl http://localhost:8123/api/v1/calls/active | jq
```

### Check System Health
```bash
curl http://localhost:8123/health/detailed | jq
```

### Check Specific Call Session
```bash
# Replace with your call_id from logs
curl "http://localhost:8123/api/v1/calls/1761627874.0" | jq
```

---

## Troubleshooting

### No audio files found
```bash
# Check folder
ls -la test_audio/

# Add files
cp /path/to/audio.wav test_audio/
```

### Connection refused
```bash
# Check server is running
curl http://localhost:8123/health

# Check port
grep STREAMING_PORT .env
# Should be 8301 (or your configured port)
```

### Mock mode not working
```bash
# Verify settings
curl http://localhost:8123/health/detailed | jq '.settings.mock_enabled'

# Should return: true
# If false, edit .env and restart server
```

### Tasks not processing
```bash
# Check Celery worker is running with correct queues
celery -A app.celery_app inspect active_queues

# Should show: model_processing and celery queues
```

---

## Next Steps

📖 **Full Guide**: See [MOCK_TESTING_GUIDE.md](MOCK_TESTING_GUIDE.md) for complete testing scenarios

🎯 **Test Audio Info**: See [test_audio/README.md](test_audio/README.md) for audio requirements

⚙️ **Configuration**: Check [.env](.env) for all available settings

---

## Summary of What Was Created

✅ **Scripts**:
- `scripts/mock_asterisk.py` - Full mock Asterisk client
- `scripts/quick_test_mock.sh` - Quick test helper script

✅ **Configuration**:
- `.env` - Updated with mock settings
- `.env.example` - Template with mock settings

✅ **Code Changes**:
- `app/config/settings.py` - Added mock settings
- `app/utils/scp_audio_downloader.py` - Enhanced local file support
- `app/streaming/call_session_manager.py` - Added mock mode check

✅ **Documentation**:
- `MOCK_TESTING_GUIDE.md` - Complete testing guide
- `QUICK_START.md` - This quick start guide
- `test_audio/README.md` - Audio folder usage guide

---

## Your Testing Path

**Where's your audio folder?** 👈 Start here!

Once you provide the path:
```bash
# Copy your audio files
cp /your/audio/folder/*.wav ./test_audio/

# Run quick test
./scripts/quick_test_mock.sh realtime 1
```

That's it! The system will handle the rest. 🚀
