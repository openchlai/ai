# Model Loading and Configuration Guide

This document explains the AI service's model loading system, configuration management, and operational modes.

## Table of Contents

- [Overview](#overview)
- [Model Loading System](#model-loading-system)
- [Configuration Management](#configuration-management)
- [Processing Modes](#processing-modes)
- [Notification System](#notification-system)
- [Whisper Model Management](#whisper-model-management)
- [Environment Variables](#environment-variables)

## Overview

The AI service supports flexible model loading with dynamic switching capabilities and comprehensive configuration management through environment variables and settings.

## Model Loading System

### Architecture

The system uses a centralized `ModelLoader` class that manages all AI models:

- **Location**: `app/model_scripts/model_loader.py`
- **Singleton Pattern**: Single global instance manages all models
- **GPU Management**: Automatic GPU memory management and cleanup
- **Dynamic Loading**: Models loaded on-demand with caching

### Supported Models

| Model Type | Purpose | Configuration Key |
|------------|---------|-------------------|
| Whisper | Speech transcription | `whisper_model_variant` |
| Translation | Language translation | `translation_strategy` |
| NER | Named entity recognition | `enable_model_loading` |
| Classification | Call classification | `enable_model_loading` |
| Summarization | Text summarization | `enable_model_loading` |
| QA Analysis | Quality analysis | `enable_model_loading` |


### Dynamic Model Switching

The system supports runtime model switching without service restart:

```python
# Example: Switch Whisper model variant
from app.core.whisper_model_manager import whisper_model_manager

# Switch to large-v3 with built-in translation
await whisper_model_manager.switch_model_variant(
    WhisperVariant.LARGE_V3,
    TranslationStrategy.WHISPER_BUILTIN
)

# Switch to large-turbo with custom translation
await whisper_model_manager.switch_model_variant(
    WhisperVariant.LARGE_TURBO, 
    TranslationStrategy.CUSTOM_MODEL
)
```

## Configuration Management

### Settings Architecture

- **Base Class**: `pydantic_settings.BaseSettings`
- **Environment Loading**: Automatic `.env` file loading
- **Type Validation**: Pydantic validation for all settings
- **Runtime Access**: Global `settings` instance

### Key Configuration Categories

#### 1. Application Settings
```bash
APP_NAME=AI Pipeline
APP_VERSION=0.1.0
DEBUG=true
LOG_LEVEL=INFO
SITE_ID=dev-site-001
```

#### 2. Resource Management
```bash
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300
MODEL_CACHE_SIZE=8192
```

#### 3. Model Configuration
```bash
ENABLE_MODEL_LOADING=false        # API server vs worker mode
WHISPER_MODEL_VARIANT=large_turbo # large_v3, large_turbo
TRANSLATION_STRATEGY=custom_model # whisper_builtin, custom_model
```

#### 4. Path Configuration
```bash
LOGS_PATH=./logs                 # Auto-detected in Docker
TEMP_PATH=./temp                 # Auto-detected in Docker
```

## Processing Modes

### Available Modes

The system supports four distinct processing modes:

#### 1. Real-time Only (`realtime_only`)
- Processes audio streams in real-time
- Immediate transcript and analysis
- Lower latency, reduced accuracy
- Uses lightweight models

#### 2. Post-call Only (`postcall_only`)
- Processes complete audio files after call ends
- Full pipeline with enhanced models
- Higher accuracy, increased latency
- Audio downloaded via SCP/HTTP

#### 3. Hybrid (`hybrid`)
- Combines real-time and post-call processing
- Real-time for immediate feedback
- Post-call for comprehensive analysis
- Best of both approaches

#### 4. Adaptive (`adaptive`)
- Intelligently selects mode based on call characteristics
- Short calls: real-time only
- Long calls: hybrid processing
- Priority keywords: immediate post-call

### Configuration Example

```bash
# Processing Mode Configuration
DEFAULT_PROCESSING_MODE=hybrid
ENABLE_REALTIME_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true
ENABLE_SCP_AUDIO_DOWNLOAD=true

# Real-time Settings
REALTIME_MIN_WINDOW_CHARS=150
REALTIME_TARGET_WINDOW_CHARS=300
REALTIME_PROCESSING_INTERVAL_SECONDS=30

# Post-call Settings
POSTCALL_AUDIO_DOWNLOAD_METHOD=scp
POSTCALL_WHISPER_MODEL=large-v3
POSTCALL_CONVERT_TO_WAV=true
```

## Notification System

### Overview

Selective notification system with four filtering modes:

- **All**: Send all notifications (progress + results)
- **Results Only**: Only notifications with actual results *(default)*
- **Critical Only**: Only call start/end and final results  
- **Disabled**: No notifications sent

### Configuration

```bash
# Agent Notification Configuration
ENABLE_AGENT_NOTIFICATIONS=true
NOTIFICATION_MODE=results_only
NOTIFICATION_ENDPOINT_URL=https://your.server.ip/api/msg/
NOTIFICATION_AUTH_ENDPOINT_URL=https://your.server.ip/api/
NOTIFICATION_BASIC_AUTH=your_base64_encoded_credentials
NOTIFICATION_REQUEST_TIMEOUT=10
NOTIFICATION_MAX_RETRIES=3
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/notifications/status` | GET | System status |
| `/api/v1/notifications/configure` | POST | Update mode |
| `/api/v1/notifications/statistics` | GET | Filtering metrics |
| `/api/v1/notifications/test` | POST | Test scenarios |

## Whisper Model Management

### Model Variants

#### Large-v3
- **Purpose**: High accuracy transcription with built-in translation
- **Languages**: 99+ languages with translation to English
- **Performance**: Slower, higher accuracy
- **Translation**: Built-in multilingual translation
- **Use Case**: Post-call processing, high-accuracy requirements

#### Large-Turbo  
- **Purpose**: Fast transcription, English-focused
- **Languages**: Optimized for English, some multilingual support
- **Performance**: Faster, good accuracy
- **Translation**: Requires separate translation model
- **Use Case**: Real-time processing, English-heavy workloads

### Dynamic Switching

The `WhisperModelManager` handles model switching:

```python
# File: app/core/whisper_model_manager.py

class WhisperModelManager:
    async def switch_model_variant(self, 
                                 new_variant: WhisperVariant,
                                 new_strategy: TranslationStrategy = None):
        # Unload current model
        await self._unload_current_model()
        
        # Load new model variant
        success = await self._load_model_variant(new_variant)
        
        # Update symlink for backward compatibility
        await self._update_symlink(new_variant)
        
        return success
```

### Memory Management

- **GPU Cache Clearing**: Automatic CUDA cache cleanup
- **Sequential Loading**: Only one Whisper model in memory
- **Garbage Collection**: Explicit cleanup before switching
- **Memory Monitoring**: Resource usage tracking

## Environment Variables

### Complete Reference

#### Core Application
```bash
# Application Identity
APP_NAME=AI Pipeline
APP_VERSION=0.1.0
DEBUG=true
LOG_LEVEL=INFO
SITE_ID=dev-site-001

# Resource Management  
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300
QUEUE_MONITOR_INTERVAL=30

# Performance
ENABLE_QUEUE_METRICS=true
ALERT_QUEUE_SIZE=15
ALERT_MEMORY_USAGE=90
```

#### Model Configuration
```bash
# Model Loading
ENABLE_MODEL_LOADING=false
MODEL_CACHE_SIZE=8192
CLEANUP_INTERVAL=3600

# Whisper Models
WHISPER_MODEL_VARIANT=large_turbo
TRANSLATION_STRATEGY=custom_model

```

#### Processing Modes
```bash
# Mode Selection
DEFAULT_PROCESSING_MODE=hybrid
ENABLE_REALTIME_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true
ENABLE_SCP_AUDIO_DOWNLOAD=true

# Real-time Configuration
REALTIME_MIN_WINDOW_CHARS=150
REALTIME_TARGET_WINDOW_CHARS=300
REALTIME_OVERLAP_CHARS=50
REALTIME_PROCESSING_INTERVAL_SECONDS=30
REALTIME_ENABLE_PROGRESSIVE_TRANSLATION=true
REALTIME_ENABLE_PROGRESSIVE_ENTITIES=true
REALTIME_ENABLE_PROGRESSIVE_CLASSIFICATION=true
REALTIME_ENABLE_AGENT_NOTIFICATIONS=true

# Post-call Configuration
POSTCALL_AUDIO_DOWNLOAD_METHOD=scp
POSTCALL_ENABLE_FULL_PIPELINE=true
POSTCALL_ENABLE_ENHANCED_TRANSCRIPTION=true
POSTCALL_WHISPER_MODEL=large-v3
POSTCALL_CONVERT_TO_WAV=true
POSTCALL_DOWNLOAD_TIMEOUT_SECONDS=60
```

#### Audio Download (SCP)
```bash
# SCP Configuration
SCP_USER=your_scp_username
SCP_SERVER=your.scp.server.ip
SCP_PASSWORD=your_scp_password
SCP_REMOTE_PATH_TEMPLATE=/path/to/calls/{call_id}.gsm
SCP_TIMEOUT_SECONDS=30
```

#### Adaptive Processing
```bash
# Adaptive Rules
ADAPTIVE_SHORT_CALL_THRESHOLD_SECONDS=30
ADAPTIVE_LONG_CALL_THRESHOLD_SECONDS=600
ADAPTIVE_HIGH_PRIORITY_KEYWORDS=emergency,urgent,critical,suicide,violence,accident,medical,police,fire,ambulance
```

#### Notification System
```bash
# Notification Configuration
ENABLE_AGENT_NOTIFICATIONS=true
NOTIFICATION_MODE=results_only
NOTIFICATION_ENDPOINT_URL=https://your.server.ip/api/msg/
NOTIFICATION_AUTH_ENDPOINT_URL=https://your.server.ip/api/
NOTIFICATION_BASIC_AUTH=your_base64_encoded_credentials
NOTIFICATION_REQUEST_TIMEOUT=10
NOTIFICATION_MAX_RETRIES=3
```

#### Infrastructure
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TASK_DB=1
REDIS_STREAMING_DB=2
REDIS_STREAMING_CHANNEL_PREFIX=ai_streaming

# Streaming Configuration
ENABLE_STREAMING=true
MAX_STREAMING_SLOTS=2
MAX_BATCH_SLOTS=1
STREAMING_PORT=8300
STREAMING_HOST=0.0.0.0

# Asterisk Integration
ASTERISK_SERVER_IP=192.168.8.13
```

### Environment-Specific Settings

#### Development
```bash
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_MODEL_LOADING=true
REDIS_URL=redis://localhost:6379/0
```

#### Production
```bash
DEBUG=false
LOG_LEVEL=INFO
ENABLE_MODEL_LOADING=false
REDIS_URL=redis://redis:6379/0
```

#### Docker
```bash
MODELS_PATH=/app/models
LOGS_PATH=/app/logs
TEMP_PATH=/app/temp
REDIS_URL=redis://redis:6379/0
```

## Usage Examples

### 1. API Server Mode
```bash
# Run as API server (no model loading)
ENABLE_MODEL_LOADING=false
uvicorn app.main:app --host 0.0.0.0 --port 8123
```

### 2. Worker Mode  
```bash
# Run as worker with model loading
ENABLE_MODEL_LOADING=true
celery -A app.celery_app worker --loglevel=info
```

### 3. Switching Processing Modes
```bash
# Real-time only for low latency
DEFAULT_PROCESSING_MODE=realtime_only
ENABLE_POSTCALL_PROCESSING=false

# Post-call only for high accuracy
DEFAULT_PROCESSING_MODE=postcall_only
ENABLE_REALTIME_PROCESSING=false
```

### 4. Model Configuration
```bash
# High accuracy setup
WHISPER_MODEL_VARIANT=large_v3
TRANSLATION_STRATEGY=whisper_builtin
POSTCALL_WHISPER_MODEL=large-v3

# Fast processing setup
WHISPER_MODEL_VARIANT=large_turbo
TRANSLATION_STRATEGY=custom_model
WHISPER_STREAMING_MODEL=base


# HuggingFace Model IDs (using openchs organization models)
HF_ASR_MODEL=openchs/asr-whisper-large-v4
HF_CLASSIFIER_MODEL=openchs/cls-gbv-distilbert-v1
HF_NER_MODEL=openchs/ner_distillbert_v1
HF_TRANSLATOR_MODEL=openchs/sw-en-opus-mult-en-ccalligned
HF_SUMMARIZER_MODEL=openchs/sum-flan-t5-base-synthetic-v1
HF_QA_MODEL=openchs/qa-helpline-distilbert-v1


```

## Best Practices

### 1. Resource Management
- Set appropriate `MAX_CONCURRENT_GPU_REQUESTS` based on GPU memory
- Monitor `MODEL_CACHE_SIZE` for memory usage
- Use `CLEANUP_INTERVAL` to prevent memory leaks

### 2. Processing Mode Selection
- Use `adaptive` mode for varied workloads
- Use `realtime_only` for low-latency requirements
- Use `postcall_only` for accuracy-critical applications

### 3. Model Selection
- Use `large_v3` for multilingual or high-accuracy needs
- Use `large_turbo` for English-focused or real-time processing
- Switch models based on language detection results

### 4. Security
- Never commit real credentials to `.env.example`
- Use base64 encoding for basic auth credentials
- Rotate notification tokens regularly

### 5. Performance Optimization
- Adjust processing window sizes based on call patterns
- Configure adaptive thresholds for your use case
- Monitor notification filtering efficiency

## Troubleshooting

### Common Issues


#### Configuration Issues
```bash
# Validate settings
python -c "from app.config.settings import settings; print(settings.get_processing_mode_config())"

# Check environment loading
python -c "import os; print(os.getenv('WHISPER_MODEL_VARIANT'))"
```

#### Memory Issues
```bash
# Monitor GPU memory
nvidia-smi
watch -n 1 nvidia-smi

# Clear model cache
curl -X POST http://localhost:8123/health/models/clear_cache
```

## API Reference

### Configuration Endpoints

#### Get Current Configuration
```http
GET /api/v1/processing-mode/status
```

#### Update Processing Mode
```http
POST /api/v1/processing-mode/configure
Content-Type: application/json

{
  "mode": "adaptive",
  "realtime_enabled": true,
  "postcall_enabled": true
}
```

#### Switch Whisper Model
```http
POST /api/v1/whisper-model/switch
Content-Type: application/json

{
  "variant": "large_v3",
  "translation_strategy": "whisper_builtin"
}
```

#### Notification Configuration
```http
POST /api/v1/notifications/configure
Content-Type: application/json

{
  "mode": "results_only"
}
```

## Migration Guide

### From Hardcoded Models
1. Move model files to organized directory structure
2. Update configuration to use environment variables
3. Test model switching functionality
4. Update deployment scripts

### From Single Processing Mode
1. Configure desired processing modes in environment
2. Test different mode combinations
3. Update client applications for new notification structure
4. Monitor performance with new configuration

---
