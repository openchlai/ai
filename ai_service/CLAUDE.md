# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Start complete stack with Docker Compose
docker-compose up -d

# Start with streaming support
ENABLE_STREAMING=true docker-compose up -d

# Local development
python -m app.main

# Start with streaming enabled
python -m app.main --enable-streaming
```

### Testing
```bash
# Run core unit tests (must pass for PR)
./run_tests.sh

# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_classifier_model.py -v
python -m pytest -m unit -v
python -m pytest -m integration -v

# Test with coverage
python -m pytest --cov=app --cov-report=term-missing tests/
```

### Celery Task Management
```bash
# Start Celery worker
celery -A app.celery_app worker --loglevel=info -E --pool=solo

# Monitor tasks with Flower
celery -A app.celery_app flower --port=5555

# Check worker status
celery -A app.celery_app inspect ping
```

## Architecture Overview

### High-Level Structure
This is a production-ready AI pipeline for processing audio recordings into structured insights, specifically designed for child protection services and social services. The system uses a microservices architecture with FastAPI, Celery workers, and Redis.

### Core Components

**API Layer (`app/api/`):**
- FastAPI routers for different model endpoints
- Audio processing endpoints (`audio_routes.py`)
- Individual model endpoints (NER, classification, translation, etc.)
- Health monitoring and system status endpoints

**Task Processing (`app/tasks/`):**
- `audio_tasks.py` - Main audio processing pipeline
- `model_tasks.py` - Individual model inference tasks
- Celery-based async processing with GPU resource management

**Model Management (`app/model_scripts/`):**
- `model_loader.py` - Central model initialization and management
- Individual model wrappers for each AI service
- Support for both HuggingFace and local models

**Core Services (`app/core/`):**
- `resource_manager.py` - GPU/CPU resource monitoring and allocation
- `processing_strategy_manager.py` - Adaptive processing mode selection
- `celery_monitor.py` - Celery worker monitoring and health checks

**Streaming (`app/streaming/`):**
- Real-time audio processing via TCP and WebSocket
- `tcp_server.py` - Asterisk integration for live calls
- `progressive_processor.py` - Real-time transcription and analysis

### Processing Modes
The system supports three processing strategies:
1. **Real-time Processing** - Live call analysis with progressive updates
2. **Post-call Processing** - Complete pipeline after call completion
3. **Hybrid Mode** - Combines both approaches based on call characteristics

### Configuration Architecture
- Environment-based configuration via Pydantic Settings (`app/config/settings.py`)
- Separate configs for development, Docker, and production
- Model paths, processing modes, and resource limits configurable via `.env`

## Development Guidelines

### Adding New Models
1. Create model wrapper in `app/model_scripts/`
2. Add model loading logic to `model_loader.py`
3. Create API endpoints in `app/api/`
4. Add Celery tasks in `app/tasks/model_tasks.py`
5. Update routing in `app/celery_app.py`

### Model Integration Pattern
```python
# Model wrapper example
class NewModel:
    def load(self) -> bool:
        # HuggingFace or local model loading
        pass
    
    def process(self, input_data):
        # Model inference
        pass
    
    def get_model_info(self) -> Dict:
        # Model metadata for health checks
        pass
```

### Testing Strategy
- **Unit tests** for individual models and core logic (required for PR)
- **Integration tests** for API endpoints and full pipeline
- **Streaming tests** for real-time processing components
- Minimum 35% test coverage required
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`

### Resource Management
The system implements sophisticated resource management:
- GPU memory monitoring and task queuing
- Adaptive concurrency based on available resources
- Request timeout and retry mechanisms
- Health checks for all system components

### Deployment Modes
- **API Server Mode** (`ENABLE_MODEL_LOADING=false`) - Handles requests, delegates to workers
- **Worker Mode** (`ENABLE_MODEL_LOADING=true`) - Loads models and processes tasks
- **Streaming Mode** - Adds real-time processing capabilities

## Key Technical Decisions

### Why Celery + Redis
- Async task processing for long-running AI inference
- Resource isolation between API and model processing
- Built-in monitoring and retry mechanisms
- Horizontal scaling capabilities

### Model Loading Strategy
- Container-baked models for faster startup
- Lazy loading with resource management
- Support for both HuggingFace Hub and local models
- Fallback strategies for model failures

### Processing Pipeline Design
- Modular pipeline allowing selective component execution
- Streaming-first architecture with batch processing fallback
- Progressive result delivery for real-time use cases
- Comprehensive error handling and recovery

## Important Notes

### Security Considerations
- No external API calls - all processing happens locally
- Configurable data retention policies
- PII detection and handling in NER models
- Basic auth for notification endpoints

### Performance Optimization
- GPU resource pooling and queue management
- Audio preprocessing and format conversion
- Text chunking for long transcripts
- Caching for frequently accessed models

### Monitoring and Observability
- Comprehensive health checks at `/health/detailed`
- Celery worker monitoring via Flower
- Resource usage tracking and alerting
- Processing queue metrics and status