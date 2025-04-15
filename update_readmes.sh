#!/bin/bash

# Function to append content if it doesn't already exist
append_if_missing() {
    local file="$1"
    local content="$2"
    if ! grep -qF "$content" "$file"; then
        echo -e "\n$content" >> "$file"
    fi
}

# Main README
append_if_missing "README.md" "## Repository Structure
- **data_pipeline/** - Handles data processing.
- **models/** - AI models for transcription, translation, and prediction.
- **backend/** - API services and data management.
- **frontend/** - User interface for visualization.
- **infrastructure/** - Deployment setup (Docker, Kubernetes, CI/CD).
- **docs/** - Documentation and research.
- **tests/** - Unit and integration testing.
- **scripts/** - Helper scripts for automation."

# Data Pipeline README
append_if_missing "data_pipeline/README.md" "## Components
- **ingestion/** - Fetches and preprocesses voice data.
- **transcription/** - Converts voice to text.
- **translation/** - Translates text into English.
- **nlp/** - Predicts case categories using AI.
- **orchestration/** - Uses Celery to manage workflows.
- **storage/** - Manages data in MinIO/S3.

### Usage
Run the pipeline:
\`\`\`bash
python run_pipeline.py --step transcription
\`\`\`"

# AI Models README
append_if_missing "models/README.md" "## Model Categories
- **voice_recognition/** - Speech-to-text models.
- **translation/** - AI-based language translation.
- **case_prediction/** - NLP-based case classification.

### Model Inference
To run a model:
\`\`\`bash
python model_runner.py --model case_prediction
\`\`\`"

# Backend README
append_if_missing "backend/README.md" "## Backend Services
- **api/** - REST API for processing requests.
- **authentication/** - User authentication and authorization.
- **logging/** - Logs events using ELK/Prometheus.

### Running the Backend
\`\`\`bash
uvicorn main:app --reload
\`\`\`"

# Frontend README
append_if_missing "frontend/README.md" "## Frontend Components
- **ui/** - Vue.js/React components for the UI.
- **dashboard/** - Displays case insights.

### Running the Frontend
\`\`\`bash
npm install && npm run serve
\`\`\`"

# Infrastructure README
append_if_missing "infrastructure/README.md" "## Infrastructure Setup
- **docker/** - Docker configurations.
- **k8s/** - Kubernetes deployment files.
- **ci_cd/** - GitHub Actions/Jenkins setup.

### Deploy with Docker
\`\`\`bash
docker-compose up -d
\`\`\`"

# Documentation README
append_if_missing "docs/README.md" "## Documentation Sections
- **api_docs/** - API documentation.
- **research/** - AI model research.
- **compliance/** - Security & privacy policies."

# Tests README
append_if_missing "tests/README.md" "## Testing Frameworks
- **backend/** - API tests (Pytest).
- **models/** - AI model validation.
- **pipeline/** - Data pipeline tests.

### Run All Tests
\`\`\`bash
pytest tests/
\`\`\`"

# Scripts README
append_if_missing "scripts/README.md" "## Utility Scripts
- **data_cleanup.py** - Cleans raw data.
- **model_runner.py** - Runs AI models.

### Running a Script
\`\`\`bash
python scripts/data_cleanup.py
\`\`\`"

echo "All README.md files have been updated with more comprehensive details!"

