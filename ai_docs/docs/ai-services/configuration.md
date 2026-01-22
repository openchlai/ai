# Configuration Guide

## Environment Variables

### Application Settings

```bash
# Application metadata
APP_NAME="AI Pipeline"
APP_VERSION="0.1.0"
APP_PORT=8125

# Debug and logging
DEBUG=false
LOG_LEVEL=INFO
```

### Database Configuration

```bash
# SQLite (default - development)
DATABASE_URL="sqlite:///./ai_service.db"

# PostgreSQL (recommended - production)
DATABASE_URL="postgresql://user:password@localhost/ai_service"

# MySQL (alternative)
DATABASE_URL="mysql://user:password@localhost/ai_service"
```

### Redis Configuration

```bash
# Redis connection
REDIS_URL="redis://localhost:6379/0"
REDIS_TASK_DB=1
REDIS_CACHE_DB=2
REDIS_PASSWORD=""

# Redis settings
REDIS_DECODE_RESPONSES=true
REDIS_SOCKET_CONNECT_TIMEOUT=5
```

### Resource Management

```bash
# GPU settings
MAX_CONCURRENT_GPU_REQUESTS=1
ENABLE_GPU=true
GPU_MEMORY_FRACTION=0.9
CUDA_VISIBLE_DEVICES=0

# Processing limits
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300
QUEUE_MONITOR_INTERVAL=30

# Cleanup settings
CLEANUP_INTERVAL=300
DATA_RETENTION_HOURS=24
```

### Model Configuration

```bash
# Model loading
ENABLE_MODEL_LOADING=true
MODEL_CACHE_SIZE=8192

# Model paths
WHISPER_MODEL_PATH="./models/whisper"
NER_MODEL_PATH="./models/ner"
CLASSIFIER_MODEL_PATH="./models/classifier"
TRANSLATOR_MODEL_PATH="./models/translator"
SUMMARIZER_MODEL_PATH="./models/summarizer"

# Model options
WHISPER_COMPUTE_TYPE="float16"
WHISPER_DEVICE="cuda"
BATCH_SIZE=1
```

### Security Settings

```bash
# Site identification
SITE_ID="production-001"

# Data privacy
ENABLE_PII_DETECTION=true
ANONYMIZE_RESULTS=false

# Authentication
ENABLE_AUTH=true
JWT_SECRET_KEY="your-secret-key"
JWT_ALGORITHM="HS256"
TOKEN_EXPIRY_MINUTES=60
```

### Streaming Configuration

```bash
# TCP Streaming (Asterisk)
ENABLE_ASTERISK_TCP=true
STREAMING_HOST="0.0.0.0"
STREAMING_PORT=8301
STREAMING_BUFFER_SIZE=320

# WebSocket
ENABLE_WEBSOCKET=true
WEBSOCKET_PATH="/audio/stream"
```

### SCP Configuration

```bash
# SCP settings for downloading audio files
ENABLE_SCP_DOWNLOAD=true
SCP_HOST="scp.server.com"
SCP_PORT=22
SCP_USERNAME="audio_user"
SCP_PASSWORD="password"
SCP_KEY_PATH="/path/to/private/key"
SCP_REMOTE_PATH="/var/audio/recordings"
SCP_TIMEOUT=300

# Mock mode (for testing)
MOCK_ENABLED=false
MOCK_AUDIO_FOLDER="./test_audio"
MOCK_SKIP_SCP_DOWNLOAD=true
```

### Processing Mode Configuration

```bash
# Default processing mode (realtime_only, postcall_only, hybrid, adaptive)
DEFAULT_PROCESSING_MODE="adaptive"

# Enable/disable specific processing modes
ENABLE_STREAMING_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true

# Real-time processing settings
REALTIME_PROCESSING_INTERVAL_SECONDS=5
REALTIME_MIN_WINDOW_CHARS=100
REALTIME_TARGET_WINDOW_CHARS=500
STREAMING_TRANSCRIPTION_INTERVAL=2.0

# Post-call processing delay
POSTCALL_PROCESSING_DELAY=10  # seconds

# Adaptive mode configuration
ADAPTIVE_SHORT_CALL_THRESHOLD=30  # seconds
ADAPTIVE_LONG_CALL_THRESHOLD=600  # seconds
```

### ML Model Configuration

```bash
# Enable HuggingFace Hub model loading
USE_HF_MODELS=true

# Speech-to-Text (Whisper)
HF_ASR_MODEL=openai/whisper-large-v3
POSTCALL_WHISPER_MODEL=large-v3

# Custom OpenChs Models
HF_CLASSIFIER_MODEL=openchs/multitask-classifier
HF_NER_MODEL=openchs/ner-model
HF_TRANSLATOR_MODEL=openchs/translation-model
HF_SUMMARIZER_MODEL=openchs/summarization-model
HF_QA_MODEL=openchs/qa-model
```

### Agent Notification Configuration

```bash
# Notification endpoints
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOK_URL="http://agent-service:8000/api/notifications"
NOTIFICATION_TIMEOUT=10
NOTIFICATION_RETRY_COUNT=3
NOTIFICATION_RETRY_DELAY=5  # seconds

# Notification types
ENABLE_REAL_TIME_ALERTS=true
ENABLE_SUMMARY_UPDATES=true
ENABLE_CASE_CLASSIFICATION_ALERTS=true
```

### Complete .env Example

```bash
# ============ APPLICATION ============
APP_NAME=AI_Pipeline
APP_VERSION=0.1.0
APP_PORT=8125
DEBUG=false
LOG_LEVEL=INFO
SITE_ID=production-001

# ============ DATABASE ============
DATABASE_URL=sqlite:///./ai_service.db

# ============ REDIS ============
REDIS_URL=redis://localhost:6379/0
REDIS_TASK_DB=1
REDIS_CACHE_DB=2

# ============ RESOURCES ============
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300
ENABLE_MODEL_LOADING=true

# ============ MODELS ============
WHISPER_COMPUTE_TYPE=float16
WHISPER_DEVICE=cuda
BATCH_SIZE=1

# ============ PROCESSING MODES ============
DEFAULT_PROCESSING_MODE=adaptive
ENABLE_STREAMING_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true
REALTIME_PROCESSING_INTERVAL_SECONDS=5
STREAMING_TRANSCRIPTION_INTERVAL=2.0

# ============ STREAMING ============
ENABLE_ASTERISK_TCP=true
STREAMING_HOST=0.0.0.0
STREAMING_PORT=8301

# ============ MOCK MODE ============
MOCK_ENABLED=false
MOCK_AUDIO_FOLDER=./test_audio

# ============ NOTIFICATIONS ============
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOK_URL=http://localhost:8000/api/notifications
```

## Configuration by Deployment Type

### Development Setup

```bash
# Minimal configuration for local development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./ai_service.db
REDIS_URL=redis://localhost:6379/0
ENABLE_MODEL_LOADING=true
WHISPER_COMPUTE_TYPE=float32
MOCK_ENABLED=false
```

### Production Setup

```bash
# Secure production configuration
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@prod-db:5432/ai_service
REDIS_URL=redis://:password@redis-cluster:6379/0
ENABLE_MODEL_LOADING=true
ENABLE_GPU=true
MAX_CONCURRENT_GPU_REQUESTS=2
ENABLE_AUTH=true
JWT_SECRET_KEY=<secure-key>
```

### Testing Setup

```bash
# Configuration for running tests
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///:memory:
REDIS_URL=redis://localhost:6379/1
MOCK_ENABLED=true
MOCK_AUDIO_FOLDER=./test_audio
NOTIFICATION_ENABLED=false
```
