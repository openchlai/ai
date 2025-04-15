#!/bin/bash

# Define folders
folders=(
    "data_pipeline"
    "data_pipeline/ingestion"
    "data_pipeline/transcription"
    "data_pipeline/translation"
    "data_pipeline/nlp"
    "data_pipeline/orchestration"
    "data_pipeline/storage"
    "models"
    "models/voice_recognition"
    "models/translation"
    "models/case_prediction"
    "models/fine_tuning"
    "backend"
    "backend/api"
    "backend/authentication"
    "backend/logging"
    "frontend"
    "frontend/ui"
    "frontend/dashboard"
    "infrastructure"
    "infrastructure/docker"
    "infrastructure/k8s"
    "infrastructure/ci_cd"
    "docs"
    "docs/api_docs"
    "docs/research"
    "docs/compliance"
    "tests"
    "tests/backend"
    "tests/models"
    "tests/pipeline"
    "scripts"
)

# Create folders
for folder in "${folders[@]}"; do
    mkdir -p "$folder"
done

# Create README.md files
echo "# AI-Powered Voice Processing & Case Prediction" > README.md
echo "- **Voice Recognition**: Convert speech to text." >> README.md
echo "- **Translation**: Convert non-English text to English." >> README.md
echo "- **NLP-Based Case Prediction**: Predict case outcomes using AI models." >> README.md
echo "- **Workflow Automation**: Orchestrate tasks efficiently." >> README.md
echo "- **Data Storage & Visualization**: Store & display insights." >> README.md

echo "# Data Pipeline" > data_pipeline/README.md
echo "Processes voice data through ingestion, transcription, translation, NLP, and storage." >> data_pipeline/README.md

echo "# AI Models" > models/README.md
echo "Contains AI models for speech recognition, translation, and case prediction." >> models/README.md

echo "# Backend Services" > backend/README.md
echo "Handles API services, authentication, and logging." >> backend/README.md

echo "# Frontend" > frontend/README.md
echo "Web UI for visualization and data presentation." >> frontend/README.md

echo "# Infrastructure" > infrastructure/README.md
echo "Deployment and orchestration setup (Docker, Kubernetes, CI/CD)." >> infrastructure/README.md

echo "# Documentation" > docs/README.md
echo "API docs, research notes, and compliance information." >> docs/README.md

echo "# Tests" > tests/README.md
echo "Unit and integration tests for various components." >> tests/README.md

echo "# Scripts" > scripts/README.md
echo "Utility scripts for data processing and model execution." >> scripts/README.md

# Print success message
echo "Folder structure and README files have been created successfully!"

