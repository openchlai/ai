---
layout: doc
title: AI Service Architecture
---

# Architecture

This document describes the high-level system design and component architecture of the OpenCHS AI Service.

## High-Level System Design

```
┌──────────────────────────────────────────────────────────────┐
│                     Load Balancer (NGINX)                    │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Gateway (Port 8125)                │
│  • Health checks                                             │
│  • Request routing                                           │
│  • WebSocket connections                                     │
│  • Streaming endpoints                                       │
│  • API documentation (Swagger UI)                            │
└──────────────────────────────────────────────────────────────┘
                              ↓
         ┌────────────────────┴─────────────────────┐
         ↓                                          ↓
┌────────────────────────┐            ┌──────────────────────┐
│  Celery Task Queue     │            │   Redis Store        │
│  (model_processing)    │            │  • Task results      │
│  • Model inference     │            │  • Session state     │
│  • Async processing    │            │  • Caching           │
│  • Retry logic         │            │  • Rate limiting     │
└────────────────────────┘            └──────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│                    Celery Workers Pool                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ GPU Worker  │  │ CPU Worker  │  │ CPU Worker  │  ...     │
│  │             │  │             │  │             │          │
│  │ • Whisper   │  │ • NER       │  │ • QA        │          │
│  │ • Translate │  │ • Classify  │  │ • Summarize │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────────────────────────────────────────┘
                              ↓
                   ┌──────────────────┐
                   │  ML Models       │
                   │  • Whisper v3    │
                   │  • Transformers  │
                   │  • spaCy         │
                   │  • Custom Models │
                   └──────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│               Streaming Layer (TCP + WebSocket)              │
│  • Asterisk Integration (Port 8301)                          │
│  • Real-time transcription                                   │
│  • Progressive result delivery                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Layers

### 1. API Layer (`app/api/`)

The REST and WebSocket interface for the service. Handles:

| Responsibility | Description |
|----------------|-------------|
| Audio file uploads | Accept and validate audio files for processing |
| Batch processing | Queue multiple files for background processing |
| Real-time streaming | WebSocket connections for live transcription |
| Individual model endpoints | Direct access to specific AI models |
| Health monitoring | System health and readiness checks |

**Key Files:**
- `audio_routes.py` - Audio processing endpoints
- `whisper_routes.py` - Transcription endpoints
- `translator_routes.py` - Translation endpoints
- `classifier_route.py` - Classification endpoints
- `health_routes.py` - Health check endpoints
- `call_session_routes.py` - Live call management

---

### 2. Task Processing Layer (`app/tasks/`)

Asynchronous task execution via Celery:

| Component | Purpose |
|-----------|---------|
| Audio preprocessing | Validate and normalize audio files |
| Model inference scheduling | Queue tasks for GPU/CPU workers |
| Progressive result updates | Stream partial results as processing continues |
| Error handling and retries | Automatic retry with exponential backoff |

**Key Files:**
- `audio_tasks.py` - Audio processing tasks
- `model_tasks.py` - Model inference tasks
- `health_tasks.py` - Health check tasks

---

### 3. Model Layer (`app/model_scripts/`)

ML model management and inference:

| Component | Purpose |
|-----------|---------|
| Model loading | Initialize models on startup or on-demand |
| GPU/CPU resource management | Allocate compute resources efficiently |
| Batch and streaming inference | Support both batch and real-time processing |
| Model versioning and caching | Cache loaded models for fast inference |

**Key Files:**
- `model_loader.py` - Central model management
- `whisper_model.py` - Speech-to-text model
- `translator_model.py` - Translation model
- `ner_model.py` - Named entity recognition
- `classifier_model.py` - Case classification
- `summarizer_model.py` - Text summarization
- `qa_model.py` - Question answering

---

### 4. Core Services (`app/core/`)

Infrastructure services that support the application:

| Service | Purpose |
|---------|---------|
| **Resource Manager** | GPU/CPU monitoring and allocation |
| **Processing Strategy Manager** | Mode selection (real-time vs batch) |
| **Celery Monitor** | Worker health and task monitoring |
| **Notification Manager** | Send alerts to agent dashboards |
| **Metrics** | Prometheus metrics collection |

**Key Files:**
- `resource_manager.py` - GPU/CPU management
- `celery_monitor.py` - Celery monitoring
- `notification_manager.py` - Notification system
- `processing_strategy_manager.py` - Processing mode logic
- `metrics.py` - Prometheus metrics

---

### 5. Streaming Layer (`app/streaming/`)

Real-time audio processing for live calls:

| Component | Purpose |
|-----------|---------|
| **TCP Server** | Asterisk PBX integration for live calls (Port 8301) |
| **WebSocket Server** | Browser-based real-time updates |
| **Audio Buffer** | Manage streaming audio chunks |
| **Call Session Manager** | Track live call state and metadata |
| **Progressive Processor** | Run NLP analysis on partial transcripts |

**Key Files:**
- `tcp_server.py` - Asterisk TCP integration
- `websocket_server.py` - WebSocket server
- `call_session_manager.py` - Call state management
- `audio_buffer.py` - Audio buffering
- `progressive_processor.py` - Progressive analysis

---

### 6. Data Layer (`app/db/`)

Data persistence and storage:

| Component | Purpose |
|-----------|---------|
| SQLAlchemy ORM | Database abstraction |
| Session management | Database connection pooling |
| Call history storage | Persist call records and transcripts |
| Agent feedback tracking | Store agent corrections and ratings |

**Key Files:**
- `session.py` - Database session management
- `models.py` - SQLAlchemy models
- `repositories/feedback_repository.py` - Feedback CRUD operations

---

## Data Flow

### Batch Processing Flow

```
1. Client uploads audio file via POST /audio/process
2. API validates file format and size
3. Task queued to Celery with unique task_id
4. Client receives 202 Accepted with task_id
5. Celery worker picks up task
6. Worker runs pipeline: Whisper → Translation → NER → Classification → Summary
7. Results stored in Redis
8. Client polls GET /audio/task/{task_id} for results
```

### Real-time Processing Flow

```
1. Asterisk sends audio stream via TCP (port 8301)
2. TCP Server receives audio chunks
3. Audio buffered until chunk threshold
4. Whisper transcribes chunk (every 5 seconds)
5. Progressive NLP runs on accumulated transcript (every 30 seconds)
6. Results pushed via WebSocket to agent dashboard
7. Call ends → trigger post-call processing (optional)
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **API Framework** | FastAPI 0.116+ |
| **Task Queue** | Celery 5.5+ |
| **Message Broker** | Redis 7.0+ |
| **ML Framework** | PyTorch 2.7+, Transformers 4.53+ |
| **Speech-to-Text** | OpenAI Whisper (faster-whisper) |
| **NLP** | spaCy 3.8+, Custom Transformers |
| **Database** | SQLAlchemy 2.0+ (SQLite/PostgreSQL/MySQL) |
| **Monitoring** | Prometheus, Grafana |
| **Container** | Docker 20.10+, Kubernetes |
| **Load Balancer** | NGINX 1.20+ |

---

## Scalability Considerations

### Horizontal Scaling

- **API Servers**: Scale horizontally behind load balancer
- **Celery Workers**: Add workers to increase throughput
- **Redis**: Use Redis Cluster for high availability
- **GPU Workers**: Add GPU nodes for faster inference

### Vertical Scaling

- **GPU Memory**: Larger GPUs allow larger models and batch sizes
- **CPU Cores**: More cores for parallel CPU-bound tasks
- **RAM**: More memory for model caching

### Bottleneck Analysis

| Component | Bottleneck | Solution |
|-----------|------------|----------|
| Whisper | GPU memory | Use smaller model or batch processing |
| Redis | Memory | Configure eviction policy, use Redis Cluster |
| Database | Connection pool | Increase pool size, use read replicas |
| Network | Bandwidth | CDN for audio files, compression |

---

## Security Architecture

### Network Security

- HTTPS/TLS for all API traffic
- Internal services communicate via private network
- Redis protected by authentication
- Firewall rules limit exposed ports

### Data Security

- PII detection and masking
- Encryption at rest (database, files)
- Encryption in transit (TLS)
- Audit logging for all operations

### Access Control

- JWT-based authentication (configurable)
- Role-based access control
- API rate limiting
- Request validation and sanitization

---

## Next Steps

- [Quick Start Guide](./quick-start.md) - Get the service running
- [Installation Options](./installation/docker-compose.md) - Detailed deployment guides
- [API Reference](./api-reference/audio-processing.md) - Complete API documentation
