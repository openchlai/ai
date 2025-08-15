# Translator Model Documentation

## 1. Model Overview

The translator model is a sequence-to-sequence model that is designed to translate text from one language to another. It is based on the T5 (Text-to-Text Transfer Transformer) architecture and has been fine-tuned for translation.

## 2. Model Details

*   **Model Architecture:** The model is based on the T5 architecture.
*   **Training Data:** The model was pre-trained on a large corpus of text and then fine-tuned on a translation dataset.

## 3. API Endpoints

### 3.1. Translate Text

*   **Method:** `POST`
*   **Path:** `/translate/`
*   **Description:** Translates a given text.
*   **Request Body:** A JSON object with a `text` field.
*   **Response:** A JSON object with the translated text.

## 4. Request Format

The request body for the `/translate/` endpoint should be a JSON object with the following field:

```json
{
  "text": "The text to be translated."
}
```

## 5. Response Format

The response from the `/translate/` endpoint is a JSON object with the following fields:

```json
{
  "translated": "The translated text.",
  "processing_time": "The time taken to process the request.",
  "model_info": {
    "model_path": "The path to the model.",
    "loaded": "Whether the model is loaded.",
    "load_time": "The time when the model was loaded.",
    "device": "The device on which the model is running.",
    "error": "Any error that occurred during model loading."
  },
  "timestamp": "The timestamp of the request."
}
```

## 6. Example Usage

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}' \
  http://localhost:8123/translate/
```

## 7. Error Handling

If the translator model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.
