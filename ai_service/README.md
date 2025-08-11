# AI Pipeline Container - Multi-Modal Audio Processing System

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Celery](https://img.shields.io/badge/celery-5.5.3-37b24d.svg)](https://docs.celeryproject.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🛡️ Code Coverage

[![AI Service Coverage](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO_NAME/branch/main/graph/badge.svg?flag=ai-service)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO_NAME?flags%5B%5D=ai-service)
[![HelplineV1 Coverage](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO_NAME/branch/main/graph/badge.svg?flag=helplinev1-backend)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO_NAME?flags%5B%5D=helplinev1-backend)

**📊 Coverage Reports:**
- [**AI Service Coverage Report**](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO_NAME?flags%5B%5D=ai-service) - Click to view detailed AI service coverage
- [**HelplineV1 Coverage Report**](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO_NAME?flags%5B%5D=helplinev1-backend) - Click to view detailed HelplineV1 backend coverage
- [**GitHub Actions Artifacts**](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions) - Download HTML coverage reports from workflow runs

A production-ready, containerized AI pipeline for processing audio recordings into structured insights. Built for child protection organizations and social services to transform call recordings into actionable case analysis.

## 🎯 Overview

This system processes audio files through a complete AI pipeline:
**Audio → Transcription → Translation → NLP Analysis → Structured Insights**

### Key Capabilities

- **🎙️ Speech-to-Text**: Whisper Large V3 Turbo with 99+ language support
- **🌐 Translation**: Fine-tuned Swahili ↔ English translation
- **🧠 NLP Analysis**: Named Entity Recognition, Classification, Summarization
- **⚡ Real-time Processing**: GPU-accelerated with intelligent resource management
- **📊 Production Ready**: Comprehensive monitoring, error handling, and scalability

### Target Use Cases

- **Child Protection Services**: Analyze crisis calls and case recordings
- **Social Services**: Process client interviews and assessment calls
- **Healthcare**: Mental health crisis detection and triage
- **Emergency Services**: Rapid case classification and priority assessment

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Gateway                      │
├─────────────────────────────────────────────────────────┤
│  Audio Upload → Celery Queue → Worker Processing Pool   │
│                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │   Whisper   │ │ Translation │ │    NLP Models       ││
│  │ Transcribe  │ │   (Sw→En)   │ │ NER │ Class │ Summ ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
├─────────────────────────────────────────────────────────┤
│            Redis Queue + Resource Management            │
│         Real-time Status Updates + Monitoring           │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Framework** | FastAPI 0.116+ | Async REST API with automatic documentation |
| **Task Queue** | Celery + Redis | Distributed audio processing |
| **ML Framework** | PyTorch + Transformers | Model inference and GPU management |
| **Audio Processing** | Librosa + SoundFile | Audio format handling and preprocessing |
| **NLP Engine** | spaCy + Custom Models | Entity extraction and text analysis |
| **Containerization** | Docker + Docker Compose | Production deployment |
| **Monitoring** | Built-in health checks | Resource monitoring and alerting |

## 🚀 Quick Start

### Prerequisites

- **Hardware**: GPU recommended (16GB+ VRAM), 32GB+ RAM, 24+ CPU cores
- **Software**: Docker 20.10+, Docker Compose 2.0+, NVIDIA Container Runtime (for GPU)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-pipeline-containerized

# Copy environment template
cp .env.example .env

# Review and adjust configuration
nano .env
```

### 2. Start with Docker Compose

```bash
# Production deployment
docker-compose up -d

# Development with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 3. Verify Installation

```bash
# Check API health
curl http://localhost:8123/health/detailed

# Check worker status
curl http://localhost:8123/audio/workers/status

# Access API documentation
open http://localhost:8123/docs
```

### 4. Process Your First Audio File

```bash
# Upload and process audio file
curl -X POST \
  -F "audio=@sample.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  http://localhost:8123/audio/process

# Real-time streaming updates
curl -X POST \
  -F "audio=@sample.wav" \
  -F "language=sw" \
  http://localhost:8123/audio/process-stream
```

## 📋 API Documentation

### Core Endpoints

#### Audio Processing
```http
POST /audio/process          # Complete pipeline analysis
POST /audio/analyze          # Quick analysis (essentials only)
POST /audio/process-stream   # Real-time streaming updates
GET  /audio/task/{task_id}   # Check processing status
```

#### Individual Models
```http
POST /whisper/transcribe     # Audio transcription
POST /translate/             # Text translation
POST /ner/extract           # Named entity recognition
POST /classifier/classify    # Case classification
POST /summarizer/summarize   # Text summarization
```

#### System Monitoring
```http
GET /health/detailed         # Comprehensive system status
GET /health/models          # Model loading status
GET /audio/queue/status     # Processing queue status
GET /audio/workers/status   # Celery worker status
```

### Example Response

```json
{
  "audio_info": {
    "filename": "crisis_call.wav",
    "file_size_mb": 2.3,
    "language_specified": "sw",
    "processing_time": 23.4
  },
  "transcript": "Msichana mdogo ana miaka 12...",
  "translation": "A 12-year-old girl...",
  "entities": {
    "PERSON": ["Maria", "Dr. John"],
    "LOC": ["Nairobi", "Kibera"],
    "ORG": ["Hospital"]
  },
  "classification": {
    "main_category": "child_protection",
    "sub_category": "mental_health_crisis",
    "priority": "high",
    "confidence": 0.94
  },
  "summary": "12-year-old girl experiencing mental health crisis requiring immediate intervention and family support.",
  "insights": {
    "risk_assessment": {
      "risk_level": "high",
      "intervention_needed": "immediate_psychiatric_evaluation"
    }
  }
}
```

## ⚙️ Configuration

### Environment Variables

```bash
# Core Application
APP_NAME="AI Pipeline"
DEBUG=false
LOG_LEVEL=INFO

# Resource Management
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300

# Model Configuration
ENABLE_MODEL_LOADING=true
MODEL_CACHE_SIZE=8192

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TASK_DB=1

# Security
SITE_ID=production-001
DATA_RETENTION_HOURS=24
```

### Hardware Optimization

#### For GPU Servers (Recommended)
```yaml
# docker-compose.gpu.yml
services:
  ai-pipeline:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 32G
    environment:
      - MAX_CONCURRENT_GPU_REQUESTS=1
      - ENABLE_MODEL_LOADING=true
```

#### For CPU-Only Deployment
```yaml
# docker-compose.cpu.yml
services:
  ai-pipeline:
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
    environment:
      - MAX_CONCURRENT_GPU_REQUESTS=2
      - ENABLE_MODEL_LOADING=true
```

## 🔧 Production Deployment

### Docker Production Stack

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  ai-pipeline:
    build: .
    restart: unless-stopped
    depends_on:
      - redis
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    ports:
      - "8123:8123"

  celery-worker:
    build: .
    restart: unless-stopped
    depends_on:
      - redis
    command: celery -A app.celery_app worker --loglevel=info -E --pool=solo
    environment:
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    depends_on:
      - ai-pipeline
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

volumes:
  redis_data:
```

### Scaling Configuration

#### Horizontal Scaling
```bash
# Scale workers for higher throughput
docker-compose up --scale celery-worker=3

# Load balancer configuration
# Multiple API instances behind nginx
docker-compose up --scale ai-pipeline=2
```

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-pipeline
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-pipeline
  template:
    spec:
      containers:
      - name: ai-pipeline
        image: ai-pipeline:latest
        resources:
          requests:
            memory: "16Gi"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            nvidia.com/gpu: 1
```

## 📊 Monitoring & Observability

### Built-in Health Checks

```bash
# System health with detailed metrics
curl http://localhost:8123/health/detailed

# Model status and dependencies
curl http://localhost:8123/health/models

# Resource utilization
curl http://localhost:8123/health/resources

# Processing queue status
curl http://localhost:8123/audio/queue/status
```

### Logging Configuration

```python
# Production logging setup
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/app/logs/ai-pipeline.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "app": {"level": "INFO", "handlers": ["file"]},
        "celery": {"level": "WARNING", "handlers": ["file"]}
    }
}
```

### Prometheus Metrics (Optional)

```python
# Add to requirements.txt
prometheus-client==0.17.1

# Metrics endpoint
curl http://localhost:8123/metrics
```

## 🧪 Testing

### Unit Tests
```bash
# Run test suite
python -m pytest tests/ -v

# Test specific components
python -m pytest tests/test_text_chunker.py -v
python -m pytest tests/test_models.py -v

# Coverage report
python -m pytest --cov=app tests/
```

### Integration Tests
```bash
# Test complete audio pipeline
python -m pytest tests/test_integration.py

# Load testing
python scripts/load_test.py --concurrent-requests=10
```

### Model Validation
```bash
# Validate model outputs
python scripts/validate_models.py

# Benchmark performance
python scripts/benchmark_models.py
```

## 🛠️ Development

### Local Development Setup

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_md

# Start development server
python -m app.main
```

### Adding New Models

1. **Create Model Wrapper**
```python
# app/models/your_model.py
class YourModel:
    def load(self) -> bool:
        # Model loading logic
        pass
    
    def process(self, input_data):
        # Model inference logic
        pass
    
    def get_model_info(self) -> Dict:
        # Model metadata
        pass

your_model = YourModel()
```

2. **Register with Model Loader**
```python
# app/models/model_loader.py
self.model_dependencies["your_model"] = {
    "required": ["torch", "transformers"],
    "description": "Your model description"
}
```

3. **Add API Endpoints**
```python
# app/api/your_model_routes.py
@router.post("/your-model/process")
async def process_with_your_model(request: YourRequest):
    # API endpoint logic
    pass
```

### MLOps Best Practices Implemented

- **✅ Model Versioning**: Models loaded from versioned paths with metadata tracking
- **✅ Experiment Tracking**: Integration-ready for MLflow experiment tracking
- **✅ Resource Management**: GPU memory management and request queuing
- **✅ Error Handling**: Comprehensive error handling with fallback strategies
- **✅ Monitoring**: Built-in health checks and performance metrics
- **✅ Scalability**: Horizontal scaling with Celery workers
- **✅ CI/CD Ready**: Docker-based deployment with environment configuration

## 🔒 Security Considerations

### Data Privacy
- **Local Processing**: All audio processing happens offline
- **No External Calls**: No data sent to external APIs
- **Data Retention**: Configurable data retention policies
- **PII Handling**: Automatic detection and handling of sensitive information

### Production Security
```bash
# Secure configuration
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Rate limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_FILE_SIZE_MB=100

# Authentication (implement as needed)
ENABLE_AUTH=True
JWT_SECRET_KEY=your-secret-key
```

## 📈 Performance Benchmarks

### Typical Performance (GPU-enabled)
- **Audio Transcription**: 2-5 seconds per minute of audio
- **Complete Pipeline**: 15-45 seconds for 2-minute audio file
- **Throughput**: 10+ concurrent requests with queue management
- **Memory Usage**: ~8GB GPU VRAM, ~16GB system RAM

### Optimization Tips
```bash
# Model optimization
TORCH_DTYPE=float16          # Reduce memory usage
BATCH_SIZE=1                 # GPU memory management
ENABLE_CHUNKING=true         # Handle long audio files

# System optimization
OMP_NUM_THREADS=8            # CPU optimization
CUDA_VISIBLE_DEVICES=0       # GPU selection
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests: `python -m pytest tests/`
4. Commit changes: `git commit -m "Add amazing feature"`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open Pull Request

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **Tests**: Maintain >80% test coverage
- **Documentation**: Update README and API docs
- **Docker**: Test containerized deployment

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [MLOps Best Practices](https://ml-ops.org/)

### Model Information
- **Whisper Large V3 Turbo**: OpenAI's latest speech recognition model
- **Custom Translation**: Fine-tuned for Swahili-English translation
- **spaCy NER**: English language model for entity recognition
- **DistilBERT**: Fine-tuned for case classification

### Community
- **Issues**: Report bugs and request features
- **Discussions**: Technical discussions and use cases
- **Wiki**: Deployment guides and troubleshooting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper model
- Hugging Face for Transformers library
- spaCy team for NLP tools
- FastAPI and Celery communities

---

**Built for Social Impact** 🌍  
Designed to help child protection and social services organizations make faster, more informed decisions to protect vulnerable populations.

For support and questions, please open an issue or reach out to the development team.