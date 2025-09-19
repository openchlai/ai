---
layout: doc
title: api
---

# API Integration

Our API allows for seamless integration between our AI service and human operators. This enables a smooth handoff process when a caller needs to speak with a human.

## API Endpoints

- **`/handoff`:** This endpoint is used to transfer a call from the AI to a human operator. It accepts a `call_id` and an `operator_id` as parameters.
- **`/summary`:** This endpoint is used to retrieve a summary of a call. It accepts a `call_id` as a parameter and returns a JSON object containing the call transcript, sentiment analysis, and other relevant information.

## Authentication

All API requests must be authenticated with an API key. You can obtain an API key by contacting our support team.

## Rate Limiting

To ensure the stability of our service, we have implemented rate limiting on our API. You can make up to 100 requests per minute.

