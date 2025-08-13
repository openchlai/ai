# Whisper Hallucination Fix - Configuration Guide

## Quick Setup

The TCP server now automatically uses the enhanced configuration from `main.py`. Here's how to configure it:

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Asterisk TCP Server Configuration (Whisper Hallucination Fixes)
ENABLE_ASTERISK_TCP=true
ASTERISK_WINDOW_DURATION=15.0          # 15s windows (vs original 5s) - CRITICAL FIX
ASTERISK_ENABLE_OVERLAPPING=true       # 25% overlap for better context
ASTERISK_DEBUG_SAVE_AUDIO=true         # Save debug chunks to /tmp/debug_audio_chunks/
ASTERISK_ENABLE_VAD=true               # Voice Activity Detection preprocessing
ASTERISK_ENABLE_AUTO_LANGUAGE=false    # Keep false for Swahili calls
```

### 2. Server Startup

The server will automatically use these settings when started:

```bash
# Start your application - it will log the configuration:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected logs:**
```
🎙️ TCP server config: 15.0s windows, overlapping: True
🎙️ Asterisk TCP listener started on port 8300 - waiting for connections
```

### 3. Runtime Configuration

**For testing different configurations without restart:**

```python
# In code (for testing)
tcp_server = AsteriskTCPServer(
    window_duration=30.0,      # Test 30-second windows
    enable_overlapping=True    # Keep overlap enabled
)
```

## Configuration Options Explained

### ASTERISK_WINDOW_DURATION (Default: 15.0)

**What it does**: Controls how long audio segments are before sending to Whisper

- `5.0` = Original (causes hallucinations)
- `15.0` = **Recommended** (eliminates most hallucinations)  
- `30.0` = Optimal quality but higher latency

**Impact**:
- Shorter = Faster response, more hallucinations
- Longer = Better accuracy, higher latency

### ASTERISK_ENABLE_OVERLAPPING (Default: true)

**What it does**: Creates 25% overlap between audio windows for better context

- `true` = **Recommended** (provides context between segments)
- `false` = No overlap (may lose speech at boundaries)

### ASTERISK_DEBUG_SAVE_AUDIO (Default: true)

**What it does**: Saves all audio chunks to `/tmp/debug_audio_chunks/` for analysis

- `true` = **Recommended for debugging** (enables audio quality analysis)
- `false` = Disable to save disk space

### ASTERISK_ENABLE_VAD (Default: true) 

**What it does**: Voice Activity Detection preprocessing

- `true` = **Recommended** (filters silence, improves accuracy)
- `false` = Process all audio (may transcribe silence as speech)

### ASTERISK_ENABLE_AUTO_LANGUAGE (Default: false)

**What it does**: Auto-detect language instead of using Swahili

- `false` = **Recommended for Swahili** (consistent language)
- `true` = Auto-detect (for mixed-language calls)

## Monitoring and Troubleshooting

### Key Log Messages

**✅ Good patterns:**
```
🎙️ TCP server config: 15.0s windows, overlapping: True
🎤 VAD preprocessing for call_123: 15.0s → 12.3s
🎙️ Medium audio (15.2s) - using 20s chunks with 4s stride
✅ Processed window 1 for call call_123 in 2.45s
```

**⚠️ Warning patterns:**
```
🚫 VAD rejected audio for call_123: voice ratio 0.02% < 5.0%
⚠️ VAD preprocessing failed for call_123, using original audio
📊 [fragmentation] Unusual chunk sizes detected  
```

### Quick Diagnostics

1. **Check current config:**
   ```bash
   # Look for this log on startup
   grep "TCP server config" logs/app.log
   ```

2. **Monitor VAD activity:**
   ```bash
   # Count VAD rejections (should be low)
   grep "VAD rejected" logs/app.log | wc -l
   ```

3. **Analyze debug audio:**
   ```bash
   # Run audio analysis
   python -m utils.audio_debug --debug-dir /tmp/debug_audio_chunks
   ```

### Performance Tuning

**For real-time performance:**
```bash
ASTERISK_WINDOW_DURATION=15.0     # Good balance
ASTERISK_ENABLE_OVERLAPPING=true  # Better accuracy
ASTERISK_ENABLE_VAD=true          # Filter silence
```

**For maximum accuracy:**
```bash
ASTERISK_WINDOW_DURATION=30.0     # Longer context
ASTERISK_ENABLE_OVERLAPPING=true  # Keep overlap
ASTERISK_ENABLE_VAD=true          # Keep preprocessing
```

**For debugging issues:**
```bash
ASTERISK_DEBUG_SAVE_AUDIO=true    # Enable audio saving
ASTERISK_ENABLE_VAD=false         # Disable VAD to test raw audio
```

## Testing the Fixes

### Run Comprehensive Tests
```bash
python scripts/test_whisper_fixes.py --verbose --output test_results.json
```

### Test Specific Configuration
```bash
# Set environment variables and restart
export ASTERISK_WINDOW_DURATION=30.0
export ASTERISK_ENABLE_OVERLAPPING=false

# Run your application
python -m uvicorn app.main:app --reload
```

## Expected Results

With default configuration (`15.0s windows, overlapping=true, VAD=true`):

- ✅ **Eliminate "kwa kwa kwa" hallucinations**
- ✅ **Meaningful speech transcription** 
- ✅ **Better silence handling** (shows "[SILENCE_DETECTED]" for silent segments)
- ✅ **Faster processing** (VAD filters silence)
- ✅ **Debug capabilities** (audio files saved for analysis)

## Rollback Plan

If issues occur, revert to original behavior:

```bash
ASTERISK_WINDOW_DURATION=5.0      # Original setting
ASTERISK_ENABLE_OVERLAPPING=false # Original setting  
ASTERISK_ENABLE_VAD=false         # Disable preprocessing
ASTERISK_DEBUG_SAVE_AUDIO=false   # Disable debugging
```

The system will work exactly as before, but hallucinations may return.