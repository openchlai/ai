# AI Service API Reference

This document provides a comprehensive reference for the AI service's API.

## 1. Audio Processing

These endpoints are for processing audio files through the AI pipeline.

### 1.1. Process Audio (Complete Pipeline)

*   **Method:** `POST`
*   **Path:** `/audio/process`
*   **Description:** Submits an audio file for processing through the complete AI pipeline, including transcription, translation, and insights.
*   **Parameters:**
    *   `audio`: The audio file to process (required).
    *   `language`: The language of the audio (e.g., `en`, `sw`). If not provided, the language will be auto-detected.
    *   `include_translation`: Whether to include translation in the results (default: `true`).
    *   `include_insights`: Whether to include insights in the results (default: `true`).
*   **Request Body:** `multipart/form-data`
*   **Response:** A JSON object with the task ID and a link to the status endpoint.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -F "audio=@/path/to/your/audio.wav" \
      -F "language=sw" \
      -F "include_translation=true" \
      http://localhost:8123/audio/process
    ```

### 1.2. Quick Audio Analysis

*   **Method:** `POST`
*   **Path:** `/audio/analyze`
*   **Description:** Submits an audio file for a quick analysis, which includes transcription and basic NLP.
*   **Parameters:**
    *   `audio`: The audio file to process (required).
    *   `language`: The language of the audio (e.g., `en`, `sw`). If not provided, the language will be auto-detected.
*   **Request Body:** `multipart/form-data`
*   **Response:** A JSON object with the task ID and a link to the status endpoint.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -F "audio=@/path/to/your/audio.wav" \
      -F "language=en" \
      http://localhost:8123/audio/analyze
    ```

### 1.3. Process Audio with Real-time Updates (SSE)

*   **Method:** `POST`
*   **Path:** `/audio/process-stream`
*   **Description:** Processes an audio file and streams real-time updates using Server-Sent Events (SSE).
*   **Parameters:**
    *   `audio`: The audio file to process (required).
    *   `language`: The language of the audio (e.g., `en`, `sw`).
    *   `include_translation`: Whether to include translation (default: `true`).
    *   `include_insights`: Whether to include insights (default: `true`).
*   **Request Body:** `multipart/form-data`
*   **Response:** A stream of Server-Sent Events.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -F "audio=@/path/to/your/audio.wav" \
      http://localhost:8123/audio/process-stream
    ```

### 1.4. Get Task Status

*   **Method:** `GET`
*   **Path:** `/audio/task/{task_id}`
*   **Description:** Retrieves the status of an audio processing task.
*   **Parameters:**
    *   `task_id`: The ID of the task (required).
*   **Response:** A JSON object with the task status and results (if completed).
*   **Example Usage:**

    ```bash
    curl http://localhost:8123/audio/task/your-task-id
    ```

## 2. Call Session Management

These endpoints are for managing real-time call sessions.

### 2.1. Get Active Calls

*   **Method:** `GET`
*   **Path:** `/api/v1/calls/active`
*   **Description:** Retrieves a list of all active call sessions.
*   **Response:** A JSON array of call session objects.
*   **Example Usage:**

    ```bash
    curl http://localhost:8123/api/v1/calls/active
    ```

### 2.2. Get Call Session

*   **Method:** `GET`
*   **Path:** `/api/v1/calls/{call_id}`
*   **Description:** Retrieves a specific call session by its ID.
*   **Parameters:**
    *   `call_id`: The ID of the call session (required).
*   **Response:** A JSON object with the call session details.
*   **Example Usage:**

    ```bash
    curl http://localhost:8123/api/v1/calls/your-call-id
    ```

## 3. Model-Specific Endpoints

These endpoints provide direct access to the individual AI models.

### 3.1. Whisper (Transcription)

*   **Method:** `POST`
*   **Path:** `/whisper/transcribe`
*   **Description:** Transcribes an audio file to text.
*   **Request Body:** `multipart/form-data` with an `audio` file.
*   **Response:** A JSON object with the transcript.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -F "audio=@/path/to/your/audio.wav" \
      http://localhost:8123/whisper/transcribe
    ```

### 3.2. Translator

*   **Method:** `POST`
*   **Path:** `/translate/`
*   **Description:** Translates text from one language to another.
*   **Request Body:** A JSON object with a `text` field.
*   **Response:** A JSON object with the translated text.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"text": "Hello, world!"}' \
      http://localhost:8123/translate/
    ```

### 3.3. NER (Named Entity Recognition)

*   **Method:** `POST`
*   **Path:** `/ner/extract`
*   **Description:** Extracts named entities from a text.
*   **Request Body:** A JSON object with a `text` field.
*   **Response:** A JSON object with the extracted entities.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"text": "Apple is a company based in Cupertino."}' \
      http://localhost:8123/ner/extract
    ```

### 3.4. Classifier

*   **Method:** `POST`
*   **Path:** `/classifier/classify`
*   **Description:** Classifies a text into predefined categories.
*   **Request Body:** A JSON object with a `narrative` field.
*   **Response:** A JSON object with the classification results.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"narrative": "This is a text about a new product launch."}' \
      http://localhost:8123/classifier/classify
    ```

### 3.5. Summarizer

*   **Method:** `POST`
*   **Path:** `/summarizer/summarize`
*   **Description:** Generates a summary of a text.
*   **Request Body:** A JSON object with a `text` field.
*   **Response:** A JSON object with the summary.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"text": "This is a long text that needs to be summarized."}' \
      http://localhost:8123/summarizer/summarize
    ```

### 3.6. QA (Quality Assurance)

*   **Method:** `POST`
*   **Path:** `/qa/evaluate`
*   **Description:** Evaluates a call center transcript against QA metrics.
*   **Request Body:** A JSON object with a `transcript` field.
*   **Response:** A JSON object with the evaluation results.
*   **Example Usage:**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"transcript": "Agent: Hello, how can I help you?"}' \
      http://localhost:8123/qa/evaluate
    ```

## 4. Health and Status

These endpoints provide information about the health and status of the service.

### 4.1. Detailed Health Check

*   **Method:** `GET`
*   **Path:** `/health/detailed`
*   **Description:** Provides a detailed health check of the service and its components.
*   **Response:** A JSON object with the health status of each component.
*   **Example Usage:**

    ```bash
    curl http://localhost:8123/health/detailed
    ```

### 4.2. Worker Status

*   **Method:** `GET`
*   **Path:** `/audio/workers/status`
*   **Description:** Retrieves the status of the Celery workers.
*   **Response:** A JSON object with the worker status.
*   **Example Usage:**

    ```bash
    curl http://localhost:8123/audio/workers/status
    ```
