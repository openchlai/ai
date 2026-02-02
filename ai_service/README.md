# AI Pipeline Container - Multi-Modal Audio Processing System

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Celery](https://img.shields.io/badge/celery-5.5.3-37b24d.svg)](https://docs.celeryproject.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Integration Status](https://img.shields.io/badge/integration-complete-brightgreen.svg)](#integration-status)

A production-ready, containerized AI pipeline for processing audio recordings into structured insights. Built for child protection organizations and social services to transform call recordings into actionable case analysis.

## Integration Status

### Unified End-to-End Service

This system provides a fully integrated AI pipeline combining **speech-to-text transcription**, **multilingual translation**, and **case prediction triage** into a single unified service. The pipeline processes voice and text inputs seamlessly through all stages, producing:

- **Transcription outputs** from audio input via Whisper Large V3
- **Translated content** through fine-tuned Swahili-English translation models
- **Automated case triage predictions** using BERT-based classification

The service integrates directly with helpline case management systems, enabling **AI-assisted triage as part of the operational case workflow**. End-to-end functional testing confirms reliable operation across all pipeline stages.

### Optimized Data Flow

Data flows seamlessly across the transcription, translation, and case prediction triage modules with reliable handoffs between each pipeline stage:

- **Seamless data transfer** across modules with no loss of information
- **Zero processing gaps** or workflow interruptions
- **Real-time handoffs** with validated latency and performance characteristics
- **Stable interoperability** confirmed through system logs and data flow validation

The complete pipeline flow ensures that outputs from transcription feed correctly into translation and downstream case triage prediction in real time, demonstrating stable end-to-end interoperability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED PIPELINE - FULLY INTEGRATED                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Audio/Voice Input                                                          │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────────┐                                                        │
│   │  TRANSCRIPTION  │  Whisper Large V3 (99+ languages)                     │
│   │   (Complete)    │  Real-time streaming or batch processing               │
│   └────────┬────────┘                                                        │
│            │ ← Seamless handoff, no data loss                                │
│            ▼                                                                 │
│   ┌─────────────────┐                                                        │
│   │   TRANSLATION   │  Fine-tuned Swahili ↔ English                         │
│   │   (Complete)    │  Context-aware chunking with overlap                   │
│   └────────┬────────┘                                                        │
│            │ ← Optimized data flow, zero gaps                                │
│            ▼                                                                 │
│   ┌─────────────────────────────────────────────┐                            │
│   │            CASE TRIAGE PREDICTION            │                           │
│   │               (Complete)                     │                           │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │                           │
│   │  │   NER    │ │ Classify │ │  Summarize   │ │                           │
│   │  │ (spaCy)  │ │ (BERT)   │ │  (BART/T5)   │ │                           │
│   │  └──────────┘ └──────────┘ └──────────────┘ │                           │
│   └────────┬────────────────────────────────────┘                            │
│            │ ← Real-time updates during calls                                │
│            ▼                                                                 │
│   ┌─────────────────┐                                                        │
│   │ STRUCTURED      │  Risk assessment, priority, recommendations            │
│   │ INSIGHTS        │  Integrated with helpline case management              │
│   └─────────────────┘                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Status

| Component | Status | Details |
|-----------|--------|---------|
| Speech-to-Text Transcription | Operational | Whisper Large V3, 99+ languages |
| Multilingual Translation | Operational | Fine-tuned Swahili ↔ English |
| Case Prediction Triage | Operational | BERT-based classification with NER |
| Data Flow | Optimized | Seamless handoffs, zero data loss |
| Helpline Integration | Operational | Real-time and post-call processing |

---

## Overview

This system processes audio files through a complete AI pipeline:
**Audio → Transcription → Translation → NLP Analysis → Structured Insights**

### Key Capabilities

- **🎙️ Speech-to-Text**: Whisper Large V3 Turbo with 99+ language support, streaming and batch modes
- **🌐 Translation**: Fine-tuned Swahili ↔ English translation with context-aware chunking
- **🧠 NLP Analysis**: Named Entity Recognition, Classification, Summarization - all integrated
- **🔗 Unified Pipeline**: Single workflow processing from audio input to case triage output
- **⚡ Real-time Processing**: GPU-accelerated with optimized data flow between modules
- **📊 Production Ready**: Comprehensive monitoring, error handling, and horizontal scalability
- **🏥 Helpline Integration**: Directly integrated with case management systems for operational triage

### Target Use Cases

- **Helpline Case Management**: AI-assisted triage integrated directly into operational workflows
- **Child Protection Services**: Analyze crisis calls and case recordings with automated prioritization
- **Social Services**: Process client interviews and assessment calls with structured insights
- **Healthcare**: Mental health crisis detection, triage, and intervention recommendations
- **Emergency Services**: Rapid case classification, priority assessment, and risk analysis

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Gateway (Port 8125)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────────┐ │
│  │ Audio Upload     │   │ Asterisk Stream  │   │ SCP/HTTP Download        │ │
│  │ (HTTP POST)      │   │ (TCP Port 8301)  │   │ (Post-Call)              │ │
│  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────────────┘ │
│           │                      │                      │                    │
│           └──────────────────────┼──────────────────────┘                    │
│                                  ▼                                           │
│                    ┌─────────────────────────┐                               │
│                    │    Celery Task Queue    │                               │
│                    │   (Redis Broker)        │                               │
│                    └───────────┬─────────────┘                               │
│                                │                                             │
├────────────────────────────────┼────────────────────────────────────────────┤
│                    INTEGRATED PROCESSING PIPELINE                            │
│                                ▼                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────────┐   │
│   │   Whisper   │ → │ Translation │ → │       Case Triage Models        │   │
│   │ Transcribe  │   │   (Sw↔En)   │   │   NER  │  Classify  │  Summarize│   │
│   └─────────────┘   └─────────────┘   └─────────────────────────────────┘   │
│         │                  │                         │                       │
│         └──────────────────┼─────────────────────────┘                       │
│                            ▼                                                 │
│                  ┌─────────────────────┐                                     │
│                  │  Structured Output   │                                    │
│                  │  + Notifications     │                                    │
│                  └─────────────────────┘                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│              Redis Queue + GPU Resource Management + Monitoring              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Processing Modes

The integrated pipeline supports three processing modes for different operational needs:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Real-time Streaming** | Progressive updates every 5-30 seconds during live calls | Live call assistance, immediate agent support |
| **Post-Call Processing** | Complete pipeline analysis after call ends | Detailed case analysis, quality review |
| **Adaptive/Dual Mode** | Intelligent selection based on call characteristics | Balanced approach for production environments |

**Real-time Data Flow:**
- Audio chunks received every 10ms (320 bytes SLIN format)
- Transcription updates every 5 seconds
- Translation and NER/Classification updates every 30 seconds
- Agent notifications sent progressively during call
- Cumulative transcript maintained throughout session

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

## Data Pipeline & MLOps Infrastructure

> **Data-Centric ML Approach**: The AI Pipeline's performance improvements stem from incorporating domain-specific Tanzanian telephony data through a privacy-compliant processing pipeline. Version 2.0 achieved substantial gains over Version 1.0 by addressing the domain mismatch between open-source training datasets and real-world telephony audio characteristics.

The AI Pipeline Container is supported by three specialized repositories that implement a complete data processing lifecycle—from raw audio quality control through privacy-preserving annotation to training-ready dataset preparation. These systems collectively ensure GDPR compliance, UNICEF data protection standards, and child safeguarding requirements while enabling high-quality model training.

### Supporting Repositories

#### 1. VAD Audio Preprocessor
**Repository**: [vad-audio-preprocessor](https://github.com/BITZ-IT-Consulting-LTD/vad-audio-preprocessor)

**Purpose**: Privacy-by-design audio quality filtering system that preprocesses raw telephony recordings into clean, anonymized audio chunks suitable for transcription and model training.

**Key Features**:
- **Two-Stage Quality Filtering**: 
  - Stage 1: File-level filtering using speech ratio and VAD SNR thresholds
  - Stage 2: Segment-level filtering for optimal 10-30 second chunks
- **SHA256 Anonymization**: Content-based hashing eliminates traceable identifiers
- **SQLite Audit Logging**: Complete traceability with Write-Ahead Logging (WAL) mode
- **Export Tracking**: Full batch processing history and quality metrics
- **Silero VAD Integration**: State-of-the-art voice activity detection for accurate speech segmentation

**Privacy Impact**:
- Removes all PII and path information from processed audio
- Generates anonymous chunk identifiers derived from audio content
- Implements data minimization principles at the preprocessing stage
- Creates comprehensive audit trails for compliance verification

**Integration Point**: Feeds quality-controlled, anonymized audio chunks into the annotation platform, ensuring only high-SNR speech segments proceed to human transcription.

**Technologies**: Python, Silero VAD, SQLite with WAL, SHA256 hashing, batch processing pipeline

**Data Flow Output**: Filtered audio chunks with quality metrics (speech ratio, VAD SNR, duration) stored in structured SQLite database

---

#### 2. Audio Annotation Platform
**Repository**: [audio-annotation-platform](https://github.com/BITZ-IT-Consulting-LTD/audio-annotation-platform)

**Purpose**: Distributed transcription management system that connects Tanzanian transcription agents to Label Studio for secure, controlled audio annotation workflows.

**Key Features**:
- **FastAPI Middleware**: RESTful API for task assignment and transcription submission
- **Redis-Based Task Locking**: Atomic distributed locking prevents duplicate transcriptions
- **API Key Authentication**: X-API-Key header validation for secure agent access
- **Label Studio Integration**: Seamless project and task management through Label Studio API
- **Agent Pseudonymization**: Agent identifiers decoupled from personal information
- **PostgreSQL Async ORM**: High-performance database with SQLAlchemy async operations
- **Systemd Security Hardening**: PrivateTmp, NoNewPrivileges, and resource isolation
- **Audit Trail**: Complete Redis-based logging of all agent actions with timestamps

**Privacy Impact**:
- Role-Based Access Control (RBAC) ensures agents only access assigned tasks
- No transcription content stored in middleware—passes through to Label Studio only
- Agent statistics aggregated without linking to identifiable information
- VPN-secured connectivity (WireGuard) between Kenya infrastructure and Tanzania agents

**Integration Point**: Manages the human-in-the-loop transcription process, converting anonymized audio chunks into ground-truth transcriptions stored in Label Studio for dataset preparation.

**Technologies**: FastAPI, PostgreSQL, Redis, Label Studio API, systemd, WireGuard VPN, Python asyncio

**Deployment**: CentOS 7 production server with systemd service management, deployed in Nairobi with secure VPN access for remote agents

**Data Flow Output**: Completed transcriptions with session metadata (duration, timestamp, task completion status) stored in PostgreSQL

---

#### 3. ASR Data Augmentation Pipeline
**Repository**: [asr-data-augmentation-pipeline](https://github.com/BITZ-IT-Consulting-LTD/asr-data-augmentation-pipeline)

**Purpose**: Privacy-preserving dataset preparation pipeline that transforms annotated audio into training-ready datasets with reproducible splits, deduplication, and MLflow experiment tracking.

**Key Features**:
- **Data Deduplication**: Removes duplicate transcriptions to prevent data inflation and overfitting
- **Reproducible Train/Test Splitting**: Fixed random seeds (42) ensure consistent dataset splits across experiments
- **MLflow Experiment Tracking**: Comprehensive logging of dataset versions, augmentation parameters, and split statistics
- **Path Sanitization**: Removes absolute paths and sensitive location information
- **Configurable Augmentation**: YAML-driven pipeline configuration for flexible data processing
- **TSV Output Format**: Standard format compatible with Hugging Face datasets and training frameworks
- **Quality Metrics Logging**: Tracks dataset statistics (duration distribution, transcription length, vocabulary size)

**Privacy Impact**:
- No PII retained in final training datasets—only audio paths and transcriptions
- Internal path references only (no absolute filesystem paths)
- Reproducible splits enable deletion of source data while maintaining training consistency
- MLflow tracking provides audit trail without storing sensitive content

**Integration Point**: Consumes Label Studio exports and produces versioned, training-ready datasets in TSV format for Whisper fine-tuning, translation model training, and downstream NLP tasks.

**Technologies**: Python, MLflow, pandas, PyYAML, configurable augmentation strategies

**Data Flow Output**: 
- `train.tsv`, `dev.tsv`, `test.tsv` with columns: `path`, `transcription`, `duration`
- MLflow experiment runs with dataset versioning and quality metrics
- Reproducible splits documented in experiment metadata

---

### Integrated Data Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRIVACY-COMPLIANT DATA PIPELINE                           │
└─────────────────────────────────────────────────────────────────────────────┘

Raw Telephony Audio (PBX/Asterisk)
         │
         ▼
┌──────────────────────┐
│  VAD Audio           │  • Two-stage quality filtering (SNR, speech ratio)
│  Preprocessor        │  • 10-30 second chunk segmentation
│                      │  • SHA256 anonymization
└──────────┬───────────┘  • SQLite audit logging
           │              
           │ Quality-filtered, anonymized chunks
           ▼
┌──────────────────────┐
│  Audio Annotation    │  • Label Studio task distribution
│  Platform            │  • Redis task locking (prevents duplicates)
│                      │  • API key authentication + RBAC
└──────────┬───────────┘  • PostgreSQL session tracking
           │              
           │ Human-transcribed audio + ground truth
           ▼
┌──────────────────────┐
│  ASR Data            │  • Deduplication
│  Augmentation        │  • Reproducible train/test splits (seed=42)
│  Pipeline            │  • Path sanitization
└──────────┬───────────┘  • MLflow versioning
           │              
           │ Training-ready datasets (TSV)
           ▼
┌──────────────────────┐
│  AI Pipeline         │  • Whisper fine-tuning (14hrs domain data)
│  Container           │  • Translation model training (NLLB)
│  (This Repository)   │  • NLP model fine-tuning (BERT, spaCy)
└──────────────────────┘  • Production inference pipeline
```

### Privacy & Compliance Framework

The three supporting repositories implement privacy-by-design principles throughout the data lifecycle:

| Privacy Control | Implementation | Repository |
|-----------------|----------------|------------|
| **Data Minimization** | Two-stage filtering removes low-quality audio | VAD Audio Preprocessor |
| **Anonymization** | SHA256-based chunk identifiers, no traceable PII | VAD Audio Preprocessor |
| **Access Control** | API key authentication, agent pseudonymization | Audio Annotation Platform |
| **Audit Trails** | SQLite WAL logging, Redis action logs, MLflow tracking | All three repositories |
| **Storage Limitation** | Defined retention periods (90 days - 36 months) | Audio Annotation Platform |
| **Security Hardening** | Systemd isolation, VPN encryption, TLS | Audio Annotation Platform |
| **Reproducibility** | Fixed random seeds, versioned splits | ASR Data Augmentation Pipeline |
| **Path Sanitization** | Internal paths only, no filesystem exposure | ASR Data Augmentation Pipeline |

**Compliance Standards**: GDPR Articles 5, 25, 32 | UNICEF Data Protection Principles 3-8 | Child Safeguarding Requirements

### Technology Stack Updates

The complete technology stack across the data pipeline and inference system:

| Layer | Technology | Purpose | Repository |
|-------|------------|---------|------------|
| **Audio Quality Control** | Silero VAD, SQLite WAL | Voice activity detection, audit logging | VAD Audio Preprocessor |
| **Annotation Management** | FastAPI, PostgreSQL, Redis | Task distribution, locking, sessions | Audio Annotation Platform |
| **Dataset Preparation** | MLflow, pandas, PyYAML | Versioning, deduplication, splitting | ASR Data Augmentation |
| **Model Training** | Hugging Face Transformers, PyTorch | Fine-tuning Whisper, NLLB, BERT | (Training scripts - separate) |
| **Inference Pipeline** | FastAPI, Celery, Redis | Production API, async processing | AI Pipeline Container (This Repo) |
| **Privacy Infrastructure** | SHA256, RBAC, systemd hardening | Anonymization, access control | All repositories |

### MLOps Best Practices - Extended

Building on the core MLOps practices in the inference pipeline, the supporting repositories add:

- **✅ Privacy-by-Design**: Data processing pipelines with built-in anonymization and minimal data retention
- **✅ Data Versioning**: SHA256 content addressing, MLflow experiment tracking, and reproducible splits
- **✅ Audit Trails**: Comprehensive logging across SQLite, PostgreSQL, and Redis for compliance verification
- **✅ Reproducible Pipelines**: Fixed random seeds, documented configurations, version-controlled preprocessing
- **✅ Quality Metrics**: VAD SNR, speech ratio tracking, transcription quality monitoring
- **✅ Distributed Processing**: Redis-based task locking for scalable annotation workflows
- **✅ Security Hardening**: Systemd isolation, VPN encryption, API key authentication

### Dataset Statistics (January 2025)

**Production Data Pipeline Performance**:
- **Processed Audio Files**: 246 files through annotation pipeline
- **Quality-Filtered Chunks**: ~1,000+ chunks (10-30 seconds each)
- **Domain-Specific Data**: 14 hours of Tanzanian telephony recordings
- **Annotation Coverage**: Real-world child helpline conversations in Swahili
- **Training Dataset**: Reproducible train/dev/test splits with fixed seed=42

**Impact on Model Performance**: 
Version 2.0 models trained on domain-specific data demonstrated substantial improvements over Version 1.0 (trained on Common Voice Swahili), particularly in reducing ASR hallucinations and handling Tanzanian accents in telephony conditions.

---

### Getting Started with the Data Pipeline

For teams looking to replicate the data processing workflow:

1. **Clone the supporting repositories**:
```bash
git clone https://github.com/BITZ-IT-Consulting-LTD/vad-audio-preprocessor
git clone https://github.com/BITZ-IT-Consulting-LTD/audio-annotation-platform
git clone https://github.com/BITZ-IT-Consulting-LTD/asr-data-augmentation-pipeline
```

2. **Follow the privacy-compliant workflow**:
   - Start with VAD Audio Preprocessor for quality filtering and anonymization
   - Use Audio Annotation Platform for secure, distributed transcription
   - Apply ASR Data Augmentation Pipeline for dataset preparation
   - Train models using the prepared datasets
   - Deploy trained models in this AI Pipeline Container for inference

3. **Refer to individual repository READMEs** for detailed setup instructions, configuration options, and deployment guides.

### Documentation & Compliance

For comprehensive privacy and compliance documentation, see:
- **Data Privacy Strategy**: [Internal compliance documentation](path-to-compliance-docs)
- **Entity Relationship Diagrams**: Data schemas across all three systems
- **Data Flow Documentation**: Complete lifecycle from raw audio to production models
- **GDPR Compliance Mapping**: Article-by-article compliance verification
- **UNICEF Data Protection**: Alignment with child protection standards

---

**Related Repositories**:
- [VAD Audio Preprocessor](https://github.com/BITZ-IT-Consulting-LTD/vad-audio-preprocessor) - Audio quality filtering
- [Audio Annotation Platform](https://github.com/BITZ-IT-Consulting-LTD/audio-annotation-platform) - Transcription management
- [ASR Data Augmentation Pipeline](https://github.com/BITZ-IT-Consulting-LTD/asr-data-augmentation-pipeline) - Dataset preparation

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

### Example Response - Integrated Pipeline Output

The unified pipeline produces comprehensive, structured output combining all stages:

```json
{
  "status": "completed",
  "call_id": "CALL-2024-001234",
  "processing_mode": "post_call",
  "audio_info": {
    "filename": "crisis_call.wav",
    "file_size_mb": 2.3,
    "duration_seconds": 145.2,
    "language_detected": "sw",
    "processing_time_seconds": 23.4
  },
  "transcription": {
    "text": "Msichana mdogo ana miaka 12 na ana matatizo ya akili...",
    "language": "sw",
    "confidence": 0.96,
    "segments": [
      {"start": 0.0, "end": 5.2, "text": "Msichana mdogo ana miaka 12..."}
    ]
  },
  "translation": {
    "source_language": "sw",
    "target_language": "en",
    "translated_text": "A 12-year-old girl is experiencing mental health issues...",
    "chunk_count": 3
  },
  "entities": {
    "PERSON": ["Maria", "Dr. John Omondi"],
    "LOC": ["Nairobi", "Kibera"],
    "ORG": ["Kenyatta Hospital"],
    "DATE": ["yesterday", "two weeks ago"],
    "AGE": ["12 years old"]
  },
  "classification": {
    "main_category": "child_protection",
    "sub_category": "mental_health_crisis",
    "intervention_type": "immediate_psychiatric_evaluation",
    "priority": "high",
    "confidence": 0.94,
    "chunk_predictions": [
      {"position": "beginning", "category": "child_protection", "confidence": 0.92},
      {"position": "middle", "category": "mental_health", "confidence": 0.96},
      {"position": "end", "category": "crisis_intervention", "confidence": 0.91}
    ]
  },
  "summary": {
    "executive_summary": "12-year-old girl experiencing acute mental health crisis requiring immediate psychiatric evaluation and family support services.",
    "key_points": [
      "Child age: 12 years old",
      "Location: Kibera, Nairobi",
      "Condition: Mental health crisis",
      "Duration: Symptoms present for two weeks"
    ]
  },
  "insights": {
    "risk_assessment": {
      "risk_level": "high",
      "confidence": 0.91,
      "factors": ["age_vulnerability", "mental_health_indicators", "crisis_keywords"]
    },
    "recommended_disposition": "immediate_psychiatric_evaluation",
    "suggested_categories": [
      {"category": "child_protection", "probability": 0.94},
      {"category": "mental_health", "probability": 0.89},
      {"category": "family_support", "probability": 0.72}
    ],
    "priority_score": 0.92
  },
  "pipeline_metrics": {
    "transcription_time_ms": 8420,
    "translation_time_ms": 5230,
    "ner_time_ms": 1850,
    "classification_time_ms": 3420,
    "summarization_time_ms": 4280,
    "total_pipeline_time_ms": 23400,
    "data_handoff_validations": "passed"
  }
}
```

### Data Flow Validation

The integrated pipeline includes built-in validation to ensure reliable handoffs:

| Handoff Point | Validation | Status |
|---------------|------------|--------|
| Audio → Transcription | Format validation, duration check | Validated |
| Transcription → Translation | Text completeness, encoding check | Validated |
| Translation → NER | Character length, language verification | Validated |
| Translation → Classification | Chunk boundaries, context overlap | Validated |
| All Modules → Output | Schema validation, completeness check | Validated |

## Helpline Case Management Integration

The AI pipeline has been integrated directly into the helpline case management workflow, enabling AI-assisted triage as part of operational case processing.

### Integration Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      HELPLINE CASE MANAGEMENT SYSTEM                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐        ┌─────────────────┐        ┌─────────────────┐    │
│   │  Asterisk   │  TCP   │   AI Pipeline   │  HTTP  │  Case Manager   │    │
│   │    PBX      │───────▶│   (Port 8301)   │───────▶│    System       │    │
│   │             │        │                 │        │                 │    │
│   └─────────────┘        └─────────────────┘        └─────────────────┘    │
│         │                        │                          │              │
│         │                        │                          │              │
│   ┌─────▼─────┐          ┌───────▼───────┐          ┌───────▼───────┐     │
│   │   Live    │          │  Progressive  │          │   Agent UI    │     │
│   │   Calls   │          │  Transcription│          │   Dashboard   │     │
│   │           │          │  & Analysis   │          │   & Alerts    │     │
│   └───────────┘          └───────────────┘          └───────────────┘     │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Operational Workflow

1. **Call Initiation**: Asterisk PBX streams live audio to AI Pipeline via TCP
2. **Real-time Processing**: Pipeline processes audio in 5-30 second windows
3. **Progressive Updates**: Transcription, translation, and triage predictions sent to agents
4. **Case Triage**: Automated classification, priority assignment, and recommendations
5. **Agent Notification**: Results pushed to case management system for agent review
6. **Post-Call Analysis**: Complete analysis stored for case documentation

### Agent Notification System

The pipeline sends structured notifications to agents during and after calls:

```json
{
  "notification_type": "progressive_update",
  "call_id": "CALL-2024-001234",
  "agent_id": "agent_042",
  "timestamp": "2024-01-15T10:23:45Z",
  "data": {
    "transcript_update": "Child reports feeling unsafe at home...",
    "current_classification": {
      "category": "child_protection",
      "priority": "high"
    },
    "entities_detected": ["child", "home", "unsafe"],
    "recommended_action": "Escalate to supervisor"
  }
}
```

### Configuration for Helpline Integration

```bash
# Notification endpoint configuration
NOTIFICATION_ENDPOINT_URL=https://your-helpline-system/api/msg/
NOTIFICATION_BASIC_AUTH=<base64-encoded-credentials>
ENABLE_AGENT_NOTIFICATIONS=true
NOTIFICATION_MODE=progressive  # or results_only

# Asterisk streaming configuration
ENABLE_STREAMING=true
STREAMING_PORT=8301
STREAMING_HOST=0.0.0.0
STREAMING_TRANSCRIPTION_INTERVAL=5
STREAMING_TRANSLATION_INTERVAL=30
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
python -m spacy download en_core_web_lg

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

## Production Status

This AI Pipeline is **production-ready** with full end-to-end integration:

- **Unified Pipeline**: All AI components (transcription, translation, case triage) operate as a single cohesive service
- **Optimized Data Flow**: Seamless data transfer between pipeline stages with zero information loss
- **Helpline Integration**: Operational within case management workflows
- **End-to-End Tested**: Comprehensive functional testing across all pipeline stages
- **Real-time Capable**: Progressive updates during live calls with reliable module handoffs

---

**Built for Social Impact**

Designed to help child protection and social services organizations make faster, more informed decisions to protect vulnerable populations. The integrated pipeline transforms voice and text inputs into actionable case insights within a single, reliable workflow.

For support and questions, please open an issue or reach out to the development team.
