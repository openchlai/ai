# Getting Started with the AI Service

This document provides a comprehensive guide to setting up, configuring, running, and using the AI service.

## 1. Introduction

The AI service is a powerful, containerized pipeline for processing audio recordings and transforming them into structured, actionable insights. It is designed for organizations that need to analyze audio data, such as call centers, social services, and healthcare providers.

### Key Features

*   **End-to-End Audio Processing:** The service provides a complete pipeline from audio input to structured data output, including transcription, translation, and various NLP analyses.
*   **Real-time and Batch Processing:** It supports both real-time streaming of audio for live analysis and batch processing of large audio files.
*   **Modular and Extensible:** The service is built with a modular architecture, making it easy to add new models and processing steps.
*   **Scalable and Production-Ready:** It is designed for scalability and can be deployed in a production environment using Docker and Celery.
*   **Comprehensive API:** The service exposes a rich API for interacting with the different models and processing pipelines.

## 2. Architecture

The AI service is composed of several key components:

*   **FastAPI:** A modern, high-performance web framework for building the API.
*   **Celery:** A distributed task queue for handling long-running audio processing tasks asynchronously.
*   **Redis:** A fast, in-memory data store used as the message broker for Celery and for caching.
*   **Docker:** A containerization platform for packaging and deploying the application and its dependencies.
*   **AI Models:** A collection of pre-trained and fine-tuned models for various AI tasks, including:
    *   **Whisper:** For speech-to-text transcription.
    *   **Translation:** For translating text between languages.
    *   **NER (Named Entity Recognition):** For extracting entities like names, locations, and organizations.
    *   **Classifier:** For categorizing text into predefined classes.
    *   **Summarizer:** For generating concise summaries of long texts.
    *   **QA (Quality Assurance):** For evaluating call center transcripts against quality metrics.

## 3. Installation and Setup

### Prerequisites

*   **Hardware:**
    *   GPU with 16GB+ VRAM (recommended for optimal performance)
    *   32GB+ RAM
    *   24+ CPU cores
*   **Software:**
    *   Docker 20.10+
    *   Docker Compose 2.0+
    *   NVIDIA Container Runtime (for GPU support)

### Installation Steps

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd ai-pipeline-containerized
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_lg
    ```

## 4. Configuration

The service is configured using environment variables. A `.env.example` file is provided with all the available options.

1.  **Create a `.env` file:**

    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file and set the following variables:**

    *   `MODELS_PATH`: Absolute path to the directory where your AI models are stored.
    *   `LOGS_PATH`: Absolute path to the directory where you want to store logs.
    *   `TEMP_PATH`: Absolute path to a directory for temporary files.
    *   `ASTERISK_SERVER_IP`: The IP address of your Asterisk server.
    *   `REDIS_URL`: The URL for your Redis instance (e.g., `redis://localhost:6379/0`).

## 5. Running the Service

The service can be run using Docker Compose, which orchestrates the different components of the application.

### Production Mode

To run the service in production mode, use the following command:

```bash
docker-compose up -d --build
```

This will start the FastAPI application, the Celery workers, and the Redis container in detached mode.

### Development Mode

For local development with hot reloading, you can create a `docker-compose.dev.yml` file and use it in conjunction with the main `docker-compose.yml` file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Verifying the Installation

Once the service is running, you can verify its status by accessing the following endpoints:

*   **API Health:** `curl http://localhost:8123/health/detailed`
*   **Worker Status:** `curl http://localhost:8123/audio/workers/status`
*   **API Documentation:** Open your browser and navigate to `http://localhost:8123/docs`

## 6. API Reference

The AI service provides a comprehensive API for interacting with its various features. The full API documentation is available at `http://localhost:8123/docs` when the service is running.

### Main Endpoints

*   `/audio/process`: The main endpoint for processing an audio file through the entire pipeline.
*   `/audio/analyze`: A faster endpoint for quick analysis of an audio file.
*   `/audio/process-stream`: An endpoint for real-time streaming of audio processing updates.
*   `/audio/task/{task_id}`: An endpoint for checking the status of a processing task.

### Model-Specific Endpoints

Each AI model has its own set of endpoints for direct interaction:

*   `/whisper/transcribe`: For transcribing audio to text.
*   `/translate/`: For translating text.
*   `/ner/extract`: For extracting named entities.
*   `/classifier/classify`: For classifying text.
*   `/summarizer/summarize`: For summarizing text.
*   `/qa/evaluate`: For evaluating a call center transcript.

## 7. Testing

The service includes a suite of tests to ensure its correctness and reliability.

### Running the Tests

To run the entire test suite, use `pytest`:

```bash
pytest tests/ -v
```

### Test Coverage

To generate a test coverage report, use the `pytest-cov` plugin:

```bash
pytest --cov=app tests/
```

## 8. Development

### Adding a New Model

To add a new model to the service, you need to:

1.  Create a new model script in the `app/model_scripts/` directory.
2.  Implement the model loading and processing logic in the script.
3.  Add the new model to the `model_loader` in `app/model_scripts/model_loader.py`.
4.  Create a new API route in the `app/api/` directory to expose the model's functionality.

### Coding Standards

Please follow the existing coding style and conventions when contributing to the project. Use a linter and a code formatter to ensure consistency.

## 9. Troubleshooting

*   **Model Loading Issues:** If you encounter issues with model loading, make sure that the `MODELS_PATH` environment variable is set correctly and that the models are available in that directory.
*   **Celery Worker Issues:** If the Celery workers are not starting, check the Redis connection and ensure that the `REDIS_URL` is configured correctly.
*   **Docker Issues:** If you have problems with the Docker containers, check the container logs for any error messages.