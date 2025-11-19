---
layout: doc
title: Quick Start for Developers
---

# Quick Start for Developers

Welcome to the **openCHS open-source project**! This guide will help you contribute to the core technical components: the **AI Service** and **REST API**. These are the backbone of the openCHS platform, backed by UNICEF Venture Fund.

## About the Project

**openCHS (Open Child Helpline System)** is an AI-enhanced platform that helps child protection services manage crisis calls and cases. Your contributions help organizations respond faster, break language barriers, and save lives.

### Project Information

- **Organization**: BITZ IT Consulting LTD (Nairobi, Kenya)
- **Funding**: UNICEF Venture Fund
- **Website**: [openchs.com](https://www.openchs.com)
- **GitHub**: [github.com/openchlai](https://github.com/openchlai)
- **License**: MIT

## Core Repositories

### 1. AI Service - [voice_recognition](https://github.com/openchlai/voice_recognition)

**Multi-modal audio processing pipeline** - Python/FastAPI ML service

**Technology Stack:**
- FastAPI 0.116+ (async REST API)
- PyTorch + Transformers (ML inference)
- Celery + Redis (distributed task queue)
- Whisper Large V3 Turbo (speech-to-text)
- Custom fine-tuned models (Swahili↔English translation)
- spaCy (NLP analysis)

**Key Capabilities:**
- 🎙️ Speech-to-text transcription (99+ languages)
- 🌐 Swahili ↔ English translation
- 🧠 NLP analysis (NER, classification, summarization)
- ⚡ GPU-accelerated real-time processing
- 📊 Production-ready with comprehensive monitoring

**Contributions Needed:**
- Model accuracy improvements
- Performance optimization
- New language support
- Enhanced NLP features
- Bug fixes and testing

### 2. REST API - [rest_api](https://github.com/openchlai/rest_api)

**Helpline backend service** - PHP/MySQL case management API

**Technology Stack:**
- PHP 8.2+
- MySQL 8.0+
- Nginx
- RESTful architecture

**Key Features:**
- Case management CRUD operations
- User authentication & authorization
- Database schema for helpline operations
- Integration endpoints for AI service

**Contributions Needed:**
- API endpoint development
- Database optimization
- Security enhancements
- Performance improvements
- Documentation

## Getting Started with AI Service

### Repository Structure

The AI service has a well-organized structure:

```
voice_recognition/
├── app/
│   ├── api/                    # FastAPI route definitions
│   │   ├── audio_routes.py     # Audio processing endpoints
│   │   ├── whisper_routes.py   # Transcription endpoints
│   │   ├── translate_routes.py # Translation endpoints
│   │   ├── ner_routes.py       # NER extraction endpoints
│   │   ├── classifier_routes.py # Classification endpoints
│   │   └── summarizer_routes.py # Summarization endpoints
│   ├── models/                 # ML model wrappers
│   │   ├── whisper_model.py    # Whisper STT model
│   │   ├── translation_model.py # Translation model
│   │   ├── ner_model.py        # Named entity recognition
│   │   ├── classifier_model.py  # Case classification
│   │   ├── summarizer_model.py  # Text summarization
│   │   └── model_loader.py     # Model management
│   ├── services/               # Business logic
│   │   ├── audio_processor.py  # Audio file handling
│   │   └── text_chunker.py     # Text processing utilities
│   ├── utils/                  # Helper functions
│   ├── celery_app.py          # Celery worker configuration
│   └── main.py                # FastAPI application entry
├── tests/                      # Test suite
│   ├── test_models.py
│   ├── test_text_chunker.py
│   └── test_integration.py
├── models/                     # Pre-trained model files (gitignored)
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # Project documentation
```

### Prerequisites

**Hardware Requirements:**
- CPU: 8+ cores (24+ for production)
- RAM: 16GB minimum (32GB+ recommended)
- GPU: NVIDIA GPU with 8GB+ VRAM (optional but recommended)
- Storage: 50GB+ free space

**Software Requirements:**
- Python 3.11+
- Docker & Docker Compose (for containerized development)
- Git
- NVIDIA Container Runtime (if using GPU)

### Setup Development Environment

#### Option 1: Docker Development (Recommended)

**Quick Start:**

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/voice_recognition.git
cd voice_recognition

# Add upstream remote
git remote add upstream https://github.com/openchlai/voice_recognition.git

# Copy environment configuration
cp .env.example .env

# Edit configuration for local development
nano .env
```

**Configure `.env`:**

```bash
# Core Application
APP_NAME="openCHS AI Pipeline - Development"
DEBUG=true
LOG_LEVEL=DEBUG

# Resource Management
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=10
REQUEST_TIMEOUT=300

# Model Configuration
ENABLE_MODEL_LOADING=true
MODEL_CACHE_SIZE=8192

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_TASK_DB=1

# Development Settings
RELOAD=true
```

**Start Development Services:**

```bash
# Start all services with hot reload
docker-compose up

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f ai-pipeline
docker-compose logs -f celery-worker

# Stop services
docker-compose down
```

#### Option 2: Native Python Development

For direct Python development with debugger access:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Install spaCy language model
python -m spacy download en_core_web_md

# Start Redis (required)
docker run -d --name openchs-redis -p 6379:6379 redis:7-alpine

# Set environment variables
export REDIS_URL=redis://localhost:6379/0
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8383

# In another terminal, start Celery worker
celery -A app.celery_app worker --loglevel=debug -E --pool=solo
```

### Verify Installation

```bash
# Check API health
curl http://localhost:8383/health/detailed

# Check model loading status
curl http://localhost:8383/health/models

# Check Celery worker status
curl http://localhost:8383/audio/workers/status

# Access API documentation
open http://localhost:8383/docs  # Swagger UI
open http://localhost:8383/redoc  # ReDoc
```

## Contributing to AI Service

### Understanding the AI Pipeline

The AI service processes audio through multiple stages:

```
Audio File → Transcription → Translation → NLP Analysis → Structured Output
    ↓              ↓              ↓              ↓              ↓
 Format      Whisper       Translation   NER/Classify/    JSON
Validation  Large V3          Model      Summarize      Response
```

### Key Components

#### 1. API Layer (`app/api/`)

**Purpose**: FastAPI endpoints for external services

**Main Endpoints:**
- `/audio/process` - Complete pipeline
- `/audio/analyze` - Quick analysis
- `/audio/process-stream` - Real-time streaming
- `/whisper/transcribe` - Just transcription
- `/translate/` - Just translation
- `/ner/extract` - Entity extraction
- `/classifier/classify` - Case classification
- `/summarizer/summarize` - Text summarization

**Example Contribution - Adding New Endpoint:**

```python
# app/api/sentiment_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.model_loader import model_loader

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    label: str  # POSITIVE, NEGATIVE, NEUTRAL
    score: float  # Confidence 0-1

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Analyze emotional tone of call transcript"""
    try:
        # Get sentiment model from loader
        sentiment = model_loader.models.get("sentiment")
        if not sentiment or not sentiment.loaded:
            raise HTTPException(
                status_code=503, 
                detail="Sentiment model not loaded"
            )
        
        # Run inference
        result = sentiment.analyze(request.text)
        return SentimentResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Models Layer (`app/models/`)

**Purpose**: ML model wrappers for inference

**Existing Models:**
- `whisper_model.py` - Speech-to-text (Whisper Large V3 Turbo)
- `translation_model.py` - Swahili↔English translation
- `ner_model.py` - Named entity recognition (spaCy)
- `classifier_model.py` - Case classification (DistilBERT)
- `summarizer_model.py` - Text summarization (BART)

**Model Interface Pattern:**

Every model follows this structure:

```python
class YourModel:
    def __init__(self):
        self.model = None
        self.loaded = False
    
    def load(self) -> bool:
        """Load model into memory"""
        try:
            # Load your model here
            self.model = load_your_model()
            self.loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def process(self, input_data):
        """Run inference"""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        return self.model(input_data)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata"""
        return {
            "name": "Your Model",
            "version": "1.0",
            "loaded": self.loaded
        }

# Create singleton instance
your_model = YourModel()
```

**Register in `model_loader.py`:**

```python
from app.models.your_model import your_model

class ModelLoader:
    def __init__(self):
        self.models = {
            "whisper": whisper_model,
            "translation": translation_model,
            "ner": ner_model,
            "classifier": classifier_model,
            "summarizer": summarizer_model,
            "your_model": your_model,  # Add here
        }
```

#### 3. Services Layer (`app/services/`)

**Purpose**: Business logic and utilities

**Key Services:**
- `audio_processor.py` - Audio file handling, format validation
- `text_chunker.py` - Text splitting for long documents

**Example - Improving Text Chunker:**

```python
# app/services/text_chunker.py
def chunk_text_semantic(text: str, max_length: int = 500) -> List[str]:
    """
    Split text into chunks at sentence boundaries
    Improvement: Use semantic similarity to keep related sentences together
    """
    import spacy
    nlp = spacy.load("en_core_web_md")
    
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sent in doc.sents:
        sent_text = sent.text.strip()
        sent_length = len(sent_text)
        
        if current_length + sent_length > max_length and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sent_text]
            current_length = sent_length
        else:
            current_chunk.append(sent_text)
            current_length += sent_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks
```

#### 4. Celery Workers (`app/celery_app.py`)

**Purpose**: Async task queue for long-running audio processing

**Task Example:**

```python
from celery import Celery
from app.celery_app import celery_app

@celery_app.task(bind=True)
def process_audio_async(self, audio_path: str, options: dict):
    """
    Async task for complete audio processing
    """
    try:
        # Update task state
        self.update_state(state='PROCESSING', meta={'status': 'transcribing'})
        
        # Run pipeline
        result = run_full_pipeline(audio_path, options)
        
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise
```

### Testing Your Changes

#### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage report
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/
open htmlcov/index.html
```

#### Writing Tests

```python
# tests/test_your_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_your_endpoint():
    """Test your new endpoint"""
    response = client.post(
        "/your/endpoint",
        json={"text": "test input"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data

def test_your_model():
    """Test your model directly"""
    from app.models.your_model import your_model
    
    # Load model if needed
    if not your_model.loaded:
        assert your_model.load()
    
    # Test inference
    result = your_model.process("test input")
    assert result is not None
```

### Code Quality

**Format code:**
```bash
black app/
```

**Check style:**
```bash
flake8 app/
```

**Type checking:**
```bash
mypy app/
```

## Getting Started with REST API

### Repository Structure

```
rest_api/
├── api/
│   ├── index.php              # Main API entry point
│   ├── auth.php               # Authentication
│   ├── cases.php              # Case management
│   ├── users.php              # User management
│   └── reports.php            # Reporting endpoints
├── database/
│   ├── schema.sql             # Database schema
│   └── migrations/            # Schema migrations
├── config/
│   ├── database.php           # Database configuration
│   └── constants.php          # Application constants
├── includes/
│   ├── functions.php          # Helper functions
│   └── validators.php         # Input validation
└── README.md
```

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/rest_api.git
cd rest_api

# Add upstream remote
git remote add upstream https://github.com/openchlai/rest_api.git

# Install dependencies
composer install

# Set up database
mysql -u root -p
CREATE DATABASE helpline_dev;
exit

# Import schema
mysql -u root -p helpline_dev < database/schema.sql

# Configure environment
cp config/database.example.php config/database.php
nano config/database.php

# Start development server
php -S localhost:8000 -t api/
```

### Testing REST API

```bash
# Run PHP tests
./vendor/bin/phpunit

# Test endpoints
curl http://localhost:8000/api/cases
```

## Contribution Workflow

### 1. Find or Create an Issue

**Finding Issues:**
- Check [AI Service Issues](https://github.com/openchlai/voice_recognition/issues)
- Check [REST API Issues](https://github.com/openchlai/rest_api/issues)
- Look for labels: `good first issue`, `help wanted`, `bug`

### 2. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Changes

Follow best practices:
- Write clean, documented code
- Add tests for new features
- Follow existing code style
- Keep commits focused and atomic

### 4. Commit with Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat(api): add sentiment analysis endpoint"
git commit -m "fix(whisper): resolve GPU memory leak"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(integration): add audio pipeline tests"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Fill out the PR template completely
```

### 6. PR Review Process

- Maintainers review your code
- Address feedback promptly
- Update your branch as needed
- Be professional and collaborative

## Important Guidelines

### Data Privacy

**CRITICAL**: This platform handles child protection data

- ❌ **Never use real case data** in development
- ✅ **Use synthetic/dummy data** only
- ✅ **Sanitize logs** - no PII in logs
- ✅ **Report data leaks** immediately

### Security

- Never commit credentials or API keys
- Use environment variables
- Follow OWASP security guidelines
- Report vulnerabilities privately

### UNICEF Requirements

As a UNICEF Venture Fund project:
- ✅ MIT License compliance
- ✅ 80%+ test coverage required
- ✅ Comprehensive documentation
- ✅ Accessible to global developers

## Resources

### Documentation

- **Project Website**: [openchs.com](https://openchs.com)
- **API Docs**: http://localhost:8383/docs (when running)
- **GitHub Repos**: [github.com/openchlai](https://github.com/openchlai)

### Learning Resources

**FastAPI:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Async Python Guide](https://realpython.com/async-io-python/)

**Machine Learning:**
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

**PHP:**
- [PHP Documentation](https://www.php.net/docs.php)
- [PHP The Right Way](https://phptherightway.com/)

### Getting Help

- **GitHub Issues**: Technical questions
- **Pull Request Comments**: Code-specific discussions
- **Email**: For security issues or private matters

## Recognition

All contributors are recognized:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contribution graph
- Project credits

## Next Steps

Ready to contribute?

1. ⭐ **Star the repositories** you'll work on
2. 👀 **Watch** them for updates
3. 🔍 **Browse existing issues** to find work
4. 🍴 **Fork and clone** the repository
5. 💻 **Set up your dev environment**
6. 🚀 **Start coding!**

---

**Thank you for contributing to openCHS!**

Your work helps protect vulnerable children and supports frontline workers across Africa. Every contribution makes a real difference.

**Questions?** Open an issue in the relevant repository.

**Welcome to the team!** 