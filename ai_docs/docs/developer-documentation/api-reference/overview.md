# API Overview

Welcome to the **openCHS API documentation**.  
These APIs enable integration with the **Helpline Case Management Service** and the **AI Service** for advanced call processing and insights.

---

## Base URLs

| Service               | Base URL                           |
|-----------------------|-----------------------------------|
| Helpline Service      | `https://api.example.com/helpline`|
| AI Service            | `https://api.example.com/ai`      |

---

## Authentication

All API requests require either an **API key** or **OAuth 2.0 token**.  

 

---

## Response Format

- **Content-Type:** `application/json`
- **Success Responses:** HTTP `2xx` status codes with JSON payload
- **Error Responses:** HTTP `4xx` or `5xx` with error details

---

## Quick Links

- [Helpline API Reference](./helpline-service)  
- [AI API Reference](./ai-service)
