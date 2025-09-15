# Whisper Model Documentation

## 1. Model Overview

The Whisper model is a state-of-the-art speech recognition model from OpenAI. It is designed to transcribe audio from a variety of languages and accents with high accuracy.

## 2. Model Details

*   **Model:** The model is the `whisper-large-v3-turbo` model from OpenAI.
*   **Languages:** The model supports over 99 languages.

## 3. API Endpoints

### 3.1. Transcribe Audio

*   **Method:** `POST`
*   **Path:** `/whisper/transcribe`
*   **Description:** Transcribes an audio file to text.
*   **Request Body:** `multipart/form-data` with an `audio` file.
*   **Response:** A JSON object with the transcript.

## 4. Request Format

The request body for the `/whisper/transcribe` endpoint should be a `multipart/form-data` request with the following field:

*   `audio`: The audio file to be transcribed.

## 5. Response Format

The response from the `/whisper/transcribe` endpoint is a JSON object with the following fields:

```json
{
  "transcript": "The transcribed text.",
  "language": "The detected language of the audio.",
  "processing_time": "The time taken to process the request.",
  "model_info": {
    "model_path": "The path to the model.",
    "loaded": "Whether the model is loaded.",
    "load_time": "The time when the model was loaded.",
    "device": "The device on which the model is running.",
    "error": "Any error that occurred during model loading."
  },
  "timestamp": "The timestamp of the request.",
  "audio_info": {
    "filename": "The name of the audio file.",
    "file_size_mb": "The size of the audio file in megabytes.",
    "format": "The format of the audio file.",
    "content_type": "The content type of the audio file."
  }
}
```

## 6. Example Usage

```bash
curl -X POST \
  -F "audio=@/path/to/your/audio.wav" \
  http://localhost:8123/whisper/transcribe
```

## 7. Error Handling

If the Whisper model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.
