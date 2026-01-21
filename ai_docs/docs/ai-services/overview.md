---
layout: doc
title: AI Service Overview
---

# AI Service Overview

> **Production-ready, multi-modal audio processing system for child protection and social services organizations.**

## What is the AI Service?

The AI Service is a containerized, production-ready AI pipeline designed to transform audio recordings into actionable insights for child protection and social services organizations. It processes audio files through a complete AI pipeline, extracting key information needed for case assessment and management.

OpenCHS integrates **state-of-the-art AI services** to transform how child helplines operate — turning every conversation into **accurate, structured, and actionable case data** while dramatically reducing the administrative burden on caseworkers.

Our design philosophy blends **AI-powered automation** with **human-centered practice**, ensuring that:

- No call is lost
- No survivor is left unsupported
- Every decision is backed by **real-time, data-driven insights**

---

## Core Processing Pipeline

```
Audio File Input
       ↓
[Preprocessing & Format Validation]
       ↓
[Speech-to-Text (Whisper)]
       ↓
[Translation (Swahili ↔ English)]
       ↓
[NLP Analysis]
       ├─ Named Entity Recognition (NER)
       ├─ Case Classification
       ├─ Summarization
       └─ Q&A Analysis
       ↓
[Insights Generation & Risk Assessment]
       ↓
Structured Results Output
```

The OpenCHS AI pipeline operates from the **moment a call is received** to the **moment actionable intelligence reaches decision-makers**.

---

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Crisis Call Analysis** | Analyze emergency hotline calls for child protection cases |
| **Case Recording Processing** | Transform case interviews into structured case documentation |
| **Healthcare Triage** | Mental health crisis detection and triage |
| **Social Services** | Client interview analysis and assessment automation |
| **Emergency Response** | Rapid case classification and priority assessment |

## Target Organizations

- Child Protection Services
- Crisis Hotlines (116 Child Helplines)
- Social Services Departments
- Healthcare Facilities
- NGOs and Community Organizations

---

## Key Capabilities

### Audio Processing
- **Speech-to-Text**: OpenAI Whisper Large-V3 with 99+ language support
- **Translation**: Domain-optimized Swahili ↔ English translation
- **Real-time & Batch**: Support for live calls and post-call analysis

### NLP Analysis
- **Named Entity Recognition**: Extract persons, locations, organizations, dates
- **Case Classification**: Multi-task classification (category, priority, intervention)
- **Summarization**: Abstractive summaries preserving critical information
- **Question-Answering**: Extract specific information from transcripts

### Processing Modes
| Mode | Description |
|------|-------------|
| **Real-time Only** | Live transcription during calls |
| **Post-call Only** | Comprehensive analysis after call ends |
| **Hybrid** | Both real-time and enhanced post-call |
| **Adaptive** | Intelligent automatic mode selection |

---

## Why This Matters

OpenCHS AI services are **not just software** — they are a **force multiplier** for social protection systems. By automating the repetitive and accelerating the critical, we enable:

- **Faster response times** — urgent cases routed in real time
- **Reduced administrative load** — helpline call agents regain hours per shift
- **Higher-quality case data** — structured, standardized, and complete
- **Better survivor outcomes** — more timely and appropriate interventions
- **Data-driven policy change** — grounded in real-world evidence

---

## Training & Capacity Building

Technology alone isn't enough. OpenCHS invests in skills transfer and capacity building, ensuring that countries and organizations can deploy, adapt, and sustain these AI capabilities.

Crucially, AI is designed to complement — not replace — call agents: it augments their judgement by automating routine tasks (transcription, data and entity capture), surfacing critical cues, and enabling faster, more informed decisions so agents can focus on empathetic support and complex casework.

Training emphasizes hands-on use, human-in-the-loop workflows, ethical handling of sensitive data, and continuous coaching and monitoring so teams retain control, build trust in AI outputs, and feed operational insights back into model improvement.

---

## Documentation Structure

| Section | Description |
|---------|-------------|
| [Architecture](./architecture.md) | System design and component layers |
| [Quick Start](./quick-start.md) | Get up and running in 5 minutes |
| [Installation](./installation/docker-compose.md) | Deployment options (Docker, Kubernetes, Manual) |
| [Configuration](./configuration/environment-variables.md) | Environment variables and settings |
| [API Reference](./api-reference/audio-processing.md) | Complete API documentation |
| [Features](./features/whisper.md) | Individual AI model documentation |
| [Development](./development/project-structure.md) | Contributing and extending |
| [Operations](./operations/monitoring.md) | Monitoring, security, troubleshooting |

---

## Quick Links

- **Get Started**: [Quick Start Guide](./quick-start.md)
- **Deploy**: [Docker Compose Setup](./installation/docker-compose.md)
- **Configure**: [Environment Variables](./configuration/environment-variables.md)
- **API Docs**: [Audio Processing API](./api-reference/audio-processing.md)
- **Contribute**: [Development Guide](./development/contributing.md)

---

**From the first word spoken to the final policy decision — OpenCHS AI keeps child protection teams informed, focused, and effective.**
