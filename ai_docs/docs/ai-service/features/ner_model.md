# NER Model Documentation

## 1. Model Overview

The NER (Named Entity Recognition) model is based on the spaCy library and is used to extract named entities from text. It can identify entities such as persons, organizations, locations, dates, and more.

## 2. Model Details

*   **Model:** The model is a pre-trained spaCy model, `en_core_web_md`.
*   **spaCy Version:** The version of spaCy used is specified in the `requirements.txt` file.

## 3. API Endpoints

### 3.1. Extract Entities

*   **Method:** `POST`
*   **Path:** `/ner/extract`
*   **Description:** Extracts named entities from a given text.
*   **Request Body:** A JSON object with a `text` field.
*   **Response:** A JSON object with the extracted entities.

## 4. Request Format

The request body for the `/ner/extract` endpoint should be a JSON object with the following field:

```json
{
  "text": "The text from which to extract entities."
}
```

## 5. Response Format

The response from the `/ner/extract` endpoint is a JSON object with the following fields:

```json
{
  "entities": [
    {
      "text": "The text of the entity.",
      "label": "The label of the entity (e.g., PERSON, ORG).",
      "start": "The starting character offset of the entity.",
      "end": "The ending character offset of the entity."
    }
  ],
  "processing_time": "The time taken to process the request.",
  "model_info": {
    "model_path": "The path to the model.",
    "loaded": "Whether the model is loaded.",
    "load_time": "The time when the model was loaded.",
    "error": "Any error that occurred during model loading."
  },
  "timestamp": "The timestamp of the request."
}
```

## 6. Example Usage

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple Inc. was founded by Steve Jobs in Cupertino."}' \
  http://localhost:8123/ner/extract
```

## 7. Error Handling

If the NER model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.
