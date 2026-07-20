# 🧠 AI-Powered Voice Processing & Case Prediction

[![AI Service CI/CD](https://github.com/openchlai/ai/actions/workflows/ai-service-ci.yml/badge.svg)](https://github.com/openchlai/ai/actions/workflows/ai-service-ci.yml)

**OpenCHS AI Service** is an advanced **AI-driven solution** for voice processing and case prediction.  
It enables **automated transcription, translation, and case classification**, enhancing efficiency in omnichannel call management and case management systems.

[![DPG Badge](https://img.shields.io/badge/Verified-DPG-3333AB?logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iMzEiIGhlaWdodD0iMzMiIHZpZXdCb3g9IjAgMCAzMSAzMyIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTE0LjIwMDggMjEuMzY3OEwxMC4xNzM2IDE4LjAxMjRMMTEuNTIxOSAxNi40MDAzTDEzLjk5MjggMTguNDU5TDE5LjYyNjkgMTIuMjExMUwyMS4xOTA5IDEzLjYxNkwxNC4yMDA4IDIxLjM2NzhaTTI0LjYyNDEgOS4zNTEyN0wyNC44MDcxIDMuMDcyOTdMMTguODgxIDUuMTg2NjJMMTUuMzMxNCAtMi4zMzA4MmUtMDVMMTEuNzgyMSA1LjE4NjYyTDUuODU2MDEgMy4wNzI5N0w2LjAzOTA2IDkuMzUxMjdMMCAxMS4xMTc3TDMuODQ1MjEgMTYuMDg5NUwwIDIxLjA2MTJMNi4wMzkwNiAyMi44Mjc3TDUuODU2MDEgMjkuMTA2TDExLjc4MjEgMjYuOTkyM0wxNS4zMzE0IDMyLjE3OUwxOC44ODEgMjYuOTkyM0wyNC44MDcxIDI5LjEwNkwyNC42MjQxIDIyLjgyNzdMMzAuNjYzMSAyMS4wNjEyTDI2LjgxNzYgMTYuMDg5NUwzMC42NjMxIDExLjExNzdMMjQuNjI0MSA5LjM1MTI3WiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+Cg==)](https://digitalpublicgoods.net/r/openchs)

---

## 🌍 Overview

**OpenCHS** is an open-source, multilingual helpline & case management platform that supports governments and NGOs to deliver 24/7 protection, counseling, and referral services, with AI-powered insights for child protection and social services.

This service is part of the **OpenCHS (Open Child Helpline System)** ecosystem — an open-source Digital Public Good developed and maintained by **BITZ IT Consulting Ltd** in collaboration with UNICEF and government partners across Eastern and Southern Africa.

---

## ✨ Features
- 🎙 **Voice Recognition:** Converts speech to text using AI-powered speech-to-text models (Whisper, wav2vec2, or similar).
- 🌐 **Translation:** Translates transcribed text into English or other supported languages to assist multilingual service delivery.
- 🧠 **NLP-Based Case Prediction:** Classifies and prioritizes cases using Natural Language Processing (NLP) for faster triage.
- ⚙️ **Workflow Automation:** Uses **Celery** and task orchestration for scalable background processing.
- 🗄 **Data Storage & Visualization:** Saves processed data in **MinIO/S3** and provides structured outputs for analytics and dashboards.

---



## 🗂 Repository Structure

### **1. Core Components**

#### 📁 `data_pipeline/`
Handles the complete data processing workflow:
- `ingestion/` — Fetches and prepares raw audio data.  
- `transcription/` — Converts speech to text.  
- `translation/` — Translates non-English text.  
- `nlp/` — Applies NLP models for classification.  
- `orchestration/` — Coordinates pipeline tasks using Celery.  
- `storage/` — Manages MinIO/S3 storage.

#### 📁 `models/`
Houses AI models used in the processing pipeline:
- `voice_recognition/` — Speech-to-text models.  
- `translation/` — AI translation models.  
- `case_prediction/` — NLP classification models.

#### 📁 `backend/`
Backend APIs and orchestration:
- `api/` — RESTful endpoints for model access.  
- `authentication/` — Handles user access and tokens.  
- `logging/` — Tracks events and errors.

#### 📁 `frontend/`
Front-end dashboards for visualization and case management.

#### 📁 `infrastructure/`
Deployment and CI/CD configurations:
- `docker/` — Container setup files.  
- `k8s/` — Kubernetes manifests.  
- `ci_cd/` — CI/CD pipeline configurations.

---

## 📘 Documentation

| Document | Description |
|-----------|--------------|
| [PROJECT_CHARTER.md](PROJECT_CHARTER.md) | Project objectives and scope. |
| [DATA_PIPELINE.md](DATA_PIPELINE.md) | Data processing and workflow overview. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture of the system. |
| [SECURITY.md](SECURITY.md) | Security best practices and data protection measures. |
| [GOVERNANCE.md](GOVERNANCE.md) | Project governance and roles. |
| [TESTING_STRATEGY.md](TESTING_STRATEGY.md) | Approach for testing AI models and APIs. |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Deployment setup and environment configuration. |
| [ROADMAP.md](ROADMAP.md) | Upcoming features and development milestones. |

---

## ⚡ Getting Started

### **Prerequisites**
Ensure you have the following installed:
- Python **3.11+**
- Node.js **18+**
- Docker & Docker Compose
- Redis & Celery (for asynchronous orchestration)
- MinIO or compatible S3 object storage

### **Installation**
```bash
# Clone the repository
git clone https://github.com/openchlai/ai.git
cd ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
