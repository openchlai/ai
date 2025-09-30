# QA Model Documentation

## 1. Model Overview

The QA (Quality Assurance) model is a multi-head classifier that is designed to evaluate call center transcripts against a set of predefined quality assurance metrics. It can be used to automate the process of QA and to provide feedback to call center agents.

## 2. Model Details

*   **Model Architecture:** The model is based on the DistilBERT architecture and has multiple classification heads, one for each QA metric.
*   **QA Metrics:** The model is trained to evaluate the following QA metrics:
    *   Opening
    *   Listening
    *   Proactiveness
    *   Resolution
    *   Hold
    *   Closing

## 3. API Endpoints

### 3.1. Evaluate Transcript

*   **Method:** `POST`
*   **Path:** `/qa/evaluate`
*   **Description:** Evaluates a call center transcript against a set of QA metrics.
*   **Request Body:** A JSON object with a `transcript` field.
*   **Response:** A JSON object with the evaluation results.

## 4. Request Format

The request body for the `/qa/evaluate` endpoint should be a JSON object with the following field:

```json
{
  "transcript": "The call center transcript to be evaluated."
}
```

## 5. Response Format

The response from the `/qa/evaluate` endpoint is a JSON object with the following fields:

```json
{
  "evaluations": {
    "opening": [
      {
        "submetric": "Use of call opening phrase",
        "prediction": true,
        "score": "✓",
        "probability": 0.95
      }
    ],
    "listening": [
      {
        "submetric": "Caller was not interrupted",
        "prediction": true,
        "score": "✓",
        "probability": 0.92
      }
    ]
  },
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
  -d '{"transcript": "Agent: Thank you for calling. How can I help you?"}' \
  http://localhost:8123/qa/evaluate
```

## 7. Error Handling

If the QA model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.
