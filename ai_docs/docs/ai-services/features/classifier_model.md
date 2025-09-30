# Classifier Model Documentation

## 1. Model Overview

The classifier model is a multi-task DistilBERT model that is fine-tuned for classifying case narratives into a set of predefined categories. It is designed to help social services and child protection agencies to quickly triage and prioritize cases based on their severity and nature.

## 2. Model Details

*   **Model Architecture:** The model is based on the DistilBERT architecture, which is a smaller and faster version of the BERT model. It is a multi-task model, which means that it can predict multiple labels for a single input.
*   **Training Data:** The model was trained on a dataset of case narratives from a child protection agency.
*   **Fine-Tuning:** The model was fine-tuned for the specific task of classifying case narratives.

## 3. API Endpoints

### 3.1. Classify Narrative

*   **Method:** `POST`
*   **Path:** `/classifier/classify`
*   **Description:** Classifies a case narrative into a set of predefined categories.
*   **Request Body:** A JSON object with a `narrative` field.
*   **Response:** A JSON object with the classification results.

## 4. Request Format

The request body for the `/classifier/classify` endpoint should be a JSON object with the following field:

```json
{
  "narrative": "The case narrative to be classified."
}
```

## 5. Response Format

The response from the `/classifier/classify` endpoint is a JSON object with the following fields:

```json
{
  "main_category": "The main category of the case.",
  "sub_category": "The sub-category of the case.",
  "intervention": "The recommended intervention for the case.",
  "priority": "The priority of the case.",
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
  -d '{"narrative": "A 12-year-old girl is being abused by her stepfather."}' \
  http://localhost:8123/classifier/classify
```

## 7. Error Handling

If the classifier model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.
