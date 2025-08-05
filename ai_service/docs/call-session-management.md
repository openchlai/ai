# Call Session Management System

## Overview
The Call Session Management System tracks multiple simultaneous Asterisk calls, maintains cumulative transcriptions for each call, and integrates with the AI pipeline for complete call analysis.

## Key Features

- **Multiple Call Tracking**: Handle multiple simultaneous calls using Asterisk call IDs
- **Cumulative Transcription**: Build growing transcripts per call session
- **Smart Concatenation**: Intelligent merging of transcript segments with overlap detection
- **Redis Persistence**: Store call sessions in Redis for reliability
- **AI Pipeline Integration**: Automatic trigger of full AI processing when calls end
- **REST API**: Complete API for managing and retrieving call data
- **Automatic Cleanup**: Timeout inactive sessions automatically

## Architecture

### Components

1. **CallSessionManager** (`app/streaming/call_session_manager.py`)
   - Manages all active call sessions
   - Handles transcription accumulation
   - Triggers AI pipeline processing
   - Provides cleanup and timeout management

2. **Updated TCP Server** (`app/streaming/tcp_server.py`)
   - Uses Asterisk call IDs instead of connection IDs
   - Integrates with CallSessionManager
   - Handles call session lifecycle

3. **Enhanced Celery Task** (`app/tasks/audio_tasks.py`)
   - Updates call sessions with new transcriptions
   - Provides enhanced logging with session context

4. **Call Session API** (`app/api/call_session_routes.py`)
   - REST endpoints for call management
   - Export functionality for AI pipeline
   - WebSocket support for real-time updates

## Call Session Lifecycle

### 1. Call Start
```
Asterisk connects → TCP server extracts call_id → CallSessionManager.start_session()
```

### 2. Audio Processing
```
Audio chunks → Transcription → CallSessionManager.add_transcription() → Cumulative transcript
```

### 3. Call End
```
Connection closes → CallSessionManager.end_session() → AI pipeline trigger → Cleanup
```

## Usage Examples

### API Endpoints

#### Get All Active Calls
```bash
curl http://localhost:8123/api/v1/calls/active
```

#### Get Specific Call Transcript
```bash
curl http://localhost:8123/api/v1/calls/1754051771.12/transcript
```

#### Get Call Statistics
```bash
curl http://localhost:8123/api/v1/calls/stats
```

#### Export Call for AI Processing
```bash
curl http://localhost:8123/api/v1/calls/1754051771.12/export?format=json
```

#### Manually End a Call
```bash
curl -X POST http://localhost:8123/api/v1/calls/1754051771.12/end
```

### Response Examples

#### Active Call Response
```json
{
  "call_id": "1754051771.12",
  "start_time": "2025-08-01T12:36:11.445000",
  "last_activity": "2025-08-01T12:38:15.120000",
  "cumulative_transcript": "kwa hanyamu kwa hanyamu...",
  "total_audio_duration": 25.5,
  "segment_count": 5,
  "status": "active"
}
```

#### Call Statistics Response
```json
{
  "active_sessions": 3,
  "total_audio_duration": 127.8,
  "total_segments": 23,
  "average_duration_per_session": 42.6,
  "session_list": ["1754051771.12", "1754051772.13", "1754051773.14"]
}
```

## Configuration

### Environment Variables
```bash
# Redis configuration (existing)
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# Call session settings
CALL_SESSION_TIMEOUT=30  # minutes
CLEANUP_INTERVAL=300     # seconds
MIN_TRANSCRIPT_LENGTH=50 # characters for AI pipeline trigger
```

### Call Session Settings
```python
# In call_session_manager.py
session_timeout = timedelta(minutes=30)  # Timeout inactive sessions
cleanup_interval = 300  # Cleanup every 5 minutes
```

## Smart Transcription Concatenation

The system intelligently merges transcript segments:

### Overlap Detection
```python
# Example: Removes redundant words at segment boundaries
existing: "Hello world how are you"
new: "how are you today"
result: "Hello world how are you today"  # "how are you" overlap removed
```

### Benefits
- Eliminates duplicate phrases from audio window overlaps
- Maintains natural conversation flow
- Handles Whisper model repetitions gracefully

## Integration with AI Pipeline

### Automatic Processing
When a call ends, if the transcript is substantial (>50 characters), the system automatically:

1. Triggers `process_audio_task` with full AI pipeline
2. Stores task reference in Redis
3. Processes transcript through:
   - Translation (if enabled)
   - NER (Named Entity Recognition)
   - Classification
   - Summarization
   - Insights generation

### Manual Processing
You can also manually trigger AI processing:
```bash
curl -X POST http://localhost:8123/api/v1/calls/1754051771.12/trigger-ai-pipeline
```

## Monitoring and Debugging

### Enhanced Logging
The system provides detailed logging:

```
📞 [session] Started call session: 1754051771.12
📝 [session] Added segment 3 to call 1754051771.12
📝 [session] Transcript length: 245 chars
📊 Call 1754051771.12: 15.0s total, 245 chars
🤖 [session] Triggered AI pipeline for call 1754051771.12, task: abc123
📞 [session] Ended call session: 1754051771.12 (reason: connection_closed)
```

### Call Status Monitoring
```bash
# Check Asterisk server status (includes call sessions)
curl http://localhost:8123/asterisk/status

# Get detailed call statistics
curl http://localhost:8123/api/v1/calls/stats
```

## Error Handling

### Session Recovery
- Sessions are stored in Redis for persistence
- Server restarts can recover active sessions
- Automatic cleanup handles orphaned sessions

### Fallback Behavior
- If session management fails, transcription still logs normally
- Individual transcript segments remain available
- Manual session creation possible via API

### Timeout Management
- Inactive sessions automatically cleaned up after 30 minutes
- Configurable timeout settings
- Graceful session ending with AI pipeline trigger

## Performance Considerations

### Redis Storage
- Sessions stored as JSON in Redis with expiration
- Efficient key structure: `call_session:{call_id}`
- Active sessions tracked in Redis set

### Memory Management
- In-memory cache of active sessions
- Periodic cleanup removes stale sessions
- Redis acts as persistent backup

### Scalability
- Each call session is independent
- Horizontal scaling possible with shared Redis
- Celery workers handle transcription load

## Migration from Old System

### What Changed
- Connection IDs → Call IDs (Asterisk format)
- Individual transcripts → Cumulative transcripts
- No session tracking → Full session management
- Manual AI triggers → Automatic pipeline integration

### Backward Compatibility
- Existing transcription endpoints still work
- Enhanced logging maintains same format
- Additional session information available

## Testing

### Local Testing
```bash
# Start services
docker-compose up

# Run call simulation
python tests/test_asterisk_simulation.py

# Check call sessions
curl http://localhost:8123/api/v1/calls/active
```

### Multiple Call Testing
The test suite supports multiple simultaneous calls to verify session isolation and proper tracking.

## Future Enhancements

### Planned Features
- WebSocket real-time transcript streaming
- Call recording storage integration
- Advanced analytics and reporting
- Call quality metrics
- Speaker diarization support
- Custom AI pipeline workflows per call type

### Integration Possibilities
- CRM system integration
- Call center dashboards
- Automated call classification
- Real-time intervention triggers
- Call quality scoring