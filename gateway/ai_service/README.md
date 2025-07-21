# 🧠 Django-based AI Service Pipeline Documentation

## Overview

This Django-based AI service processes **audio files** and generates **insightful, structured summaries** by combining transcription (Whisper), translation (MarianMT), named entity recognition (NER), classification, and summarization. The system supports multilingual voice input and outputs decision-ready summaries with annotations, specifically designed for trauma-informed case management.

---

## 🔁 Pipeline Workflow

![AI Service Flow](ai_service/ai_service_flow.png)

## 📁 Django Project Structure (Implemented)

```bash
ai_service/
├── ai_service/                 # Django project config
│   ├── settings.py             # Django settings
│   ├── celery.py               # Celery configuration
│   ├── cli.py                  # Command line interface
│   ├── urls.py                 # URL routing
│   └── config/                 # Model configurations
│       ├── models.yaml         # AI model config
│       └── model_config.yaml   # Model paths
├── core/                       # Core app for pipeline logic
│   ├── models.py               # AudioFile model with JSON insights
│   ├── views.py                # API views with async processing
│   ├── serializers.py          # DRF serializers
│   ├── tasks.py                # Celery async tasks
│   ├── websocket.py            # WebSocket client for live audio
│   ├── pipeline/               # Core processing logic
│   │   ├── transcription.py    # Whisper transcription with hallucination detection
│   │   ├── translation.py      # MarianMT translation
│   │   ├── ner.py              # spaCy NER with auto-download
│   │   ├── classifier.py       # Multi-task classification
│   │   ├── summarizer.py       # HuggingFace summarization
│   │   ├── insights.py         # Trauma-informed case insights
│   │   └── model_loader.py     # Model loading utilities
│   └── utils/                  # Helper functions
│       ├── highlighter.py      # Text highlighting
│       ├── path_resolver.py    # Path resolution
│       └── env.py              # Environment utilities
├── tests/                      # Comprehensive test suite
│   ├── core/                   # Core functionality tests
│   └── pipeline/               # Pipeline component tests
├── docs/                       # Documentation
│   └── audio_pipeline_system_design.md
├── fixtures/                   # Test data and utilities
├── models/                     # AI model storage
├── audio_files/                # Uploaded audio files
├── docker-compose.yml          # Docker deployment config
├── Dockerfile                  # Container definition
├── install.sh                  # Installation script
├── manage.py                   # Django management
└── requirements.txt            # Python dependencies
```

## 🔧 Pipeline Component Descriptions

### 1. Transcription (Whisper) ✅ IMPLEMENTED
- **Library**: OpenAI Whisper (git+https://github.com/openai/whisper.git)
- **Features**: 
  - Hallucination detection with retry logic
  - Adaptive parameter tuning (temperature, beam search)
  - Multi-format audio support (mp3, wav, m4a, flac, etc.)
  - CUDA acceleration when available
  - Configurable model loading from YAML
- **Input**: Audio file path
- **Output**: Clean transcript text

### 2. Translation (MarianMT) ✅ IMPLEMENTED
- **Library**: HuggingFace MarianMT model
- **Features**:
  - Configurable model path via YAML
  - GPU acceleration support
  - Beam search generation
  - Automatic tokenization and decoding
- **Input**: Transcript in source language
- **Output**: English-translated text

### 3. Named Entity Recognition (NER) ✅ IMPLEMENTED
- **Library**: spaCy with en_core_web_md model
- **Features**:
  - Automatic model download if missing
  - Support for multiple entity types (PERSON, ORG, GPE, LOC, DATE, TIME, MONEY, EVENT)
  - Flat and nested entity extraction
  - Robust error handling
- **Input**: Translated text
- **Output**: Structured entity dictionary or flat list

### 4. Classification ✅ IMPLEMENTED
- **Features**:
  - Multi-task classification (main category, sub-category, intervention, priority)
  - Custom tokenization and preprocessing
  - Configurable label mappings
  - GPU acceleration support
- **Input**: Processed narrative text
- **Output**: Structured classification results

### 5. Annotation ✅ IMPLEMENTED
- **Features**:
  - Entity-based text highlighting
  - Custom markup generation
  - Integration with NER results
- **Input**: Original text + extracted entities
- **Output**: Annotated HTML markup

### 6. Summarization ✅ IMPLEMENTED
- **Library**: HuggingFace Transformers (T5-based)
- **Features**:
  - Configurable summary length
  - Beam search generation
  - GPU acceleration
  - Robust error handling
- **Input**: Translated text
- **Output**: Concise summary

### 7. Insights Generation ✅ IMPLEMENTED
- **Features**:
  - Trauma-informed case analysis
  - Integration with external LLM (Mistral)
  - Comprehensive case management recommendations
  - JSON-structured output with safety planning, psychosocial support, legal protocols
- **Input**: Summary + entities + classification
- **Output**: Detailed case insights JSON

## 🧪 Example Input & Output

### 📥 Input
- File: voice_note_001.wav
- Language: Luganda

### 📤 Output (JSON)
```json
{
  "transcript": "Omwana wange anyanyasibwa ku ssomero...",
  "translation": "My child is being abused at school...",
  "entities": [
    {"text": "child", "label": "PERSON"},
    {"text": "school", "label": "LOCATION"}
  ],
  "classification": {
    "category": "Child Abuse",
    "sentiment": "negative",
    "urgency": "high"
  },
  "annotated_text": "<mark class='person'>child</mark> is being abused at <mark class='location'>school</mark>.",
  "summary": "High-urgency child abuse report from school. Escalation required."
}
```

## 🧰 Django REST Framework API ✅ IMPLEMENTED

|| Endpoint | Method | Description |
||----------|--------|-------------|
|| `/api/upload/` | POST | Upload audio file and start async processing |
|| `/api/task_status/<task_id>/` | GET | Check Celery task status |
|| `/health/` | GET | Health check endpoint |

### Example Usage

**Upload Audio File:**
```bash
curl -X POST -F "audio=@voice_note.wav" http://localhost:8000/api/upload/
```

**Response:**
```json
{
  "message": "Audio uploaded and processing started.",
  "audio_id": 123,
  "task_id": "abc123-def456-ghi789",
  "status_check_url": "/api/task_status/abc123-def456-ghi789/"
}
```

**Check Task Status:**
```bash
curl http://localhost:8000/api/task_status/abc123-def456-ghi789/
```

**Response (Success):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "result": {
    "transcript": "...",
    "translated": "...",
    "summary": "...",
    "entities": [...],
    "classification": {...},
    "insights": {...},
    "annotated": "..."
  }
}
```

## 🛡️ Data Protection
- Storage: Uploaded audio and processed data stored under /media/
- Privacy: GDPR & child protection compliant
- Redaction: Optional entity masking or redaction before storage/export

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended) ✅ IMPLEMENTED
```bash
# Clone the repository
cd /path/to/ai_service

# Start all services
docker compose up -d

# Check service status
docker compose ps
```

**Services:**
- **web**: Django application (port 8000)
- **celery**: Background task processing
- **redis**: Message broker and cache

### Option 2: Manual Installation
```bash
# Run installation script
./install.sh

# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Option 3: CLI Tool ✅ IMPLEMENTED
```bash
# Install and run via CLI
pip install -e .
openchs  # Starts the service automatically
```

## 📋 Implementation Status

### ✅ **COMPLETED**
- [x] Django project structure
- [x] Database models (AudioFile with JSON insights)
- [x] REST API endpoints with async processing
- [x] Celery task queue integration
- [x] Whisper transcription with hallucination detection
- [x] MarianMT translation pipeline
- [x] spaCy NER with auto-model download
- [x] Multi-task classification system
- [x] HuggingFace summarization
- [x] Trauma-informed insights generation
- [x] Text annotation and highlighting
- [x] Docker deployment configuration
- [x] Comprehensive test suite
- [x] WebSocket client for live audio
- [x] Installation scripts and CLI
- [x] Model configuration management
- [x] Health check endpoints
- [x] Service monitoring scripts

### 🛠️ **IN PROGRESS**
- [ ] Performance optimization
- [ ] Enhanced error handling
- [ ] Additional model configurations
- [ ] Advanced audio preprocessing

### 🗓️ **PLANNED**
- [ ] Real-time streaming support
- [ ] Multi-language model support
- [ ] Advanced analytics dashboard
- [ ] Integration with external case management systems

## 📦 Dependencies (Implemented)
```txt
Django==5.2.1
djangorestframework==3.16.0
celery==5.5.3
redis==6.2.0
openai-whisper @ git+https://github.com/openai/whisper.git
transformers==4.29.2
torch==2.2.2
spacy==3.8.0
en_core_web_md @ https://github.com/explosion/spacy-models/releases/...
scikit-learn==1.6.1
psycopg2-binary==2.9.10
gunicorn==20.1.0
django-cors-headers==4.7.0
PyYAML==6.0.2
pydub==0.25.1
websockets==15.0.1
requests==2.32.3
```

## 📊 Monitoring & Health Checks

### Service Status
```bash
# Check all services
docker compose ps

# View logs
docker compose logs -f

# Health check
curl http://localhost:8000/health/
```

### Performance Monitoring
```bash
# Monitor Celery tasks
docker compose exec celery celery -A ai_service inspect active

# Redis status
docker compose exec redis redis-cli info

# Container resources
docker stats
```

## 📝 Additional Documentation

- **System Design**: `docs/audio_pipeline_system_design.md`
- **Service Status**: `SERVICE_STATUS_CHECK.md`
- **Pipeline Components**: `core/pipeline/README.md`
