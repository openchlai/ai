# Asterisk Audio Stream Header Analysis

## Overview
This document describes how to analyze and extract call IDs from Asterisk TCP audio streams.

## Current Implementation (Updated)
Your TCP server handles a simple UID protocol:
- Asterisk sends a UID string terminated by `\r` (CR, byte 13)
- After the UID, raw PCM audio data follows (320 bytes per 10ms chunk)
- Audio format: 16kHz, 16-bit signed linear, mixed-mono (both parties on one channel)
- No WAV header - raw PCM samples only

## Header Inspection Setup

### 1. Enhanced TCP Server Logging
Added detailed packet inspection in `tcp_server.py`:
```python
# Logs first 10 packets with:
- Packet size and sequence number
- Hex dump (first 64 bytes)
- ASCII representation
- Pattern detection for CALL keywords and digits
```

### 2. Header Analysis Utility
Created `utils/header_analyzer.py` with capabilities to:
- Analyze packet structure (binary vs text)
- Extract potential call IDs using multiple methods
- Detect common patterns (UUIDs, numeric IDs, prefixed IDs)
- Generate analysis reports

## How to Inspect Headers

### Method 1: Live Stream Analysis
1. Start your FastAPI server with TCP enabled
2. Monitor logs when Asterisk connects - you'll see:
```
🔍 [header] Packet 1: 640 bytes
🔍 [header] Hex dump: 74657374...
🔍 [header] ASCII: test_call_123...
```

### Method 2: Programmatic Analysis
```python
from utils.header_analyzer import AsteriskHeaderAnalyzer, format_analysis_report

analyzer = AsteriskHeaderAnalyzer()

# Analyze single packet
analysis = analyzer.analyze_packet(packet_data)
print(format_analysis_report(analysis))

# Analyze stream start (multiple packets)
stream_analysis = analyzer.analyze_stream_start([packet1, packet2, packet3])
print(format_analysis_report(stream_analysis))
```

## Expected Header Formats

### Format 1: Simple UID Protocol (Current)
```
[UID_STRING]\r[AUDIO_DATA][AUDIO_DATA]...
```
- UID terminated by CR (0x0D)
- Followed by continuous 320-byte audio chunks (10ms each)
- Each chunk contains 160 samples (160 int16 values = 320 bytes)
- Mixed-mono: both caller and agent voices combined in one channel

### Format 2: Structured Headers (If Enhanced)
```
[HEADER_LENGTH][CALL_ID][CHANNEL][TIMESTAMP][AUDIO_DATA]...
```
- Binary length field (2-4 bytes)
- Fixed or variable-length call identifier
- Channel information
- Timestamp or sequence numbers

### Format 3: Text-Based Protocol
```
CALL:uuid-12345-67890\r\nCHANNEL:SIP/trunk-001\r\n[AUDIO_DATA]
```
- Key-value pairs
- Line-terminated fields
- Audio data follows headers

## Call ID Extraction Patterns

The analyzer looks for these patterns:

### 1. UUID Format
- `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`
- Example: `550e8400-e29b-41d4-a716-446655440000`

### 2. Numeric IDs
- 8+ digit sequences
- Example: `1234567890123`

### 3. Prefixed IDs
- `CALL:`, `ID:`, `UID:`, `CHANNEL:`
- Example: `CALL:ast_call_12345`

### 4. Channel Names
- `SIP/trunk-001`, `DAHDI/1-1`
- Asterisk channel naming conventions

## Integration Steps

### Step 1: Capture Sample Data
Run your current setup and collect the header inspection logs:
```bash
# Start services and trigger a call
# Check logs for 🔍 [header] entries
docker logs ai-pipeline-1 | grep "header"
```

### Step 2: Analyze Patterns
Use the header analyzer to understand the format:
```python
# Extract hex data from logs and analyze
hex_data = "74657374..."  # From logs
packet_data = bytes.fromhex(hex_data)
analysis = analyzer.analyze_packet(packet_data)
```

### Step 3: Implement Call ID Extraction
Once you identify the pattern, modify `tcp_server.py`:
```python
def extract_call_id(self, data: bytes) -> Optional[str]:
    """Extract call ID from packet data"""
    # Implement based on discovered pattern
    pass
```

### Step 4: Update Connection Tracking
Use extracted call IDs instead of connection-based IDs:
```python
# Instead of: connection_id = f"{client_addr[0]}:{client_addr[1]}:{timestamp}"
# Use: connection_id = extracted_call_id or fallback_id
```

## Testing Commands

### 1. Analyze Current Logs
```bash
# Extract header data from current logs
docker logs ai-pipeline-1 2>&1 | grep "🔍 \[header\]" > header_analysis.log
```

### 2. Test Header Analyzer
```bash
cd /home/franklin/ai-pipeline-containerized
python3 -c "
from utils.header_analyzer import AsteriskHeaderAnalyzer
analyzer = AsteriskHeaderAnalyzer()
# Test with sample data
sample = b'test_call_123\r' + b'\x00' * 627  # 640 bytes total
analysis = analyzer.analyze_packet(sample)
print('Call IDs found:', analysis['potential_call_ids'])
"
```

## Audio File Download Integration

After call completion, the system now downloads the complete audio file for comprehensive analysis:

### Download URL Format
```
https://{asterisk_server_ip}/helpline/api/calls/{call_id}?file=wav
```

### Integration Process
1. **Real-time processing**: 10ms chunks processed for immediate transcription
2. **Call end**: Complete audio file downloaded from Asterisk server
3. **Full pipeline**: Downloaded audio processed through `/audio/process` equivalent
4. **Enhanced results**: Better quality analysis from complete audio file

### Benefits
- **Dual processing**: Real-time + comprehensive analysis
- **Higher accuracy**: Full audio provides better transcription quality  
- **Complete context**: Both parties' audio for better insights
- **Fallback capability**: Streaming transcripts as backup

## Next Steps

1. **Capture Real Headers**: Run a test call and examine the header logs
2. **Identify Pattern**: Use the analyzer to understand the header structure  
3. **Extract Call ID**: Implement extraction logic based on discovered pattern
4. **Update Tracking**: Modify connection management to use call IDs
5. **Test Multiple Calls**: Verify different calls get different IDs
6. **Test Audio Download**: Verify complete audio files are downloaded and processed
7. **Configure Asterisk Server**: Set ASTERISK_SERVER_IP environment variable

## Troubleshooting

### No Headers Detected
- Check if Asterisk is sending headers at all
- Verify TCP connection is working
- Look for binary vs text data patterns

### Multiple Patterns Found
- Use confidence scores from analyzer
- Test with known call scenarios
- Prioritize UUID > prefixed > numeric patterns

### Headers Change Format
- Asterisk configuration might affect header format
- Check Asterisk dialplan and channel configuration
- Document different scenarios (inbound vs outbound calls)