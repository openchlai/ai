# Summarizer Model Documentation

## 1. Model Overview

The summarizer model is a sequence-to-sequence model that is designed to generate concise summaries of long texts. It can be used to quickly understand the main points of a helpline's call transcript  without having to read the entire text.

## 2. Model Details

*   **Model Architecture:** The model is based on the T5 (Text-to-Text Transfer Transformer) architecture.
*   **Training Data:** The model was pre-trained on a large corpus of text and then fine-tuned on English translated helpline call transcripts summarization dataset.

## 3. API Endpoints

### 3.1. Summarize Text

*   **Method:** `POST`
*   **Path:** `/summarizer/summarize`
*   **Description:** Generates a summary of a given English call transcript.
*   **Request Body:** A JSON object with a `text` field.
*   **Response:** A JSON object with the summary.

## 4. Request Format

The request body for the `/summarizer/summarize` endpoint should be a JSON object with the following field:

```json
{
  "text": "The text to be summarized."
}
```

## 5. Response Format

The response from the `/summarizer/summarize` endpoint is a JSON object with the following fields:

```json
{
  "summary": "The generated summary.",
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
  -d '{"text": "Hello, is this 116? Yes, thank you for your call. Who am I speaking with? My name is Ahmed, and I'm calling from Mombasa. I have a problem that requires immediate attention. A friend of mine has a daughter, only 5 years old, who is being forced into child labor at a local factory. This sounds dire, Ahmed. Thank you for bringing this to our notice. Has anyone else noticed this? Sadly, no one seems to care. She looks exhausted and malnourished. I'm worried sick. I understand your concern. The best thing you can do is report it to the Mombasa Child Welfare Society and also to the police. We can follow up on this case too. Please don't hesitate to call again."}'\
  http://localhost:8123/summarizer/summarize
```

## 7. Error Handling

If the summarizer model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.
