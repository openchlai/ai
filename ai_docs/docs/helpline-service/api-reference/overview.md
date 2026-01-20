# API Reference Overview

The Helpline Service provides a comprehensive REST API for case management, user management, communications, and reporting.

## Base URL

```
http://localhost:8888/api/v1
```

## Authentication

All API requests require authentication headers:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8888/api/v1/cases
```

## Response Format

All responses are JSON:

```json
{
  "status": "success|error",
  "data": {},
  "message": "Description",
  "timestamp": "2024-01-20T15:35:00Z"
}
```

## Main Endpoints

### Cases
- `GET /cases` - List all cases
- `POST /cases` - Create new case
- `GET /cases/{id}` - Get case details
- `PUT /cases/{id}` - Update case
- `DELETE /cases/{id}` - Delete case

### Clients
- `GET /clients` - List clients
- `POST /clients` - Create client
- `GET /clients/{id}` - Get client details
- `PUT /clients/{id}` - Update client

### Users
- `GET /users` - List users
- `POST /users` - Create user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Communications
- `GET /communications` - List messages
- `POST /communications` - Send message
- `GET /communications/{id}` - Get message details

### Dashboard
- `GET /dashboard/stats` - Dashboard statistics
- `GET /dashboard/cases-by-type` - Cases breakdown
- `GET /dashboard/agent-performance` - Agent metrics

## Common Parameters

### Pagination

```bash
GET /cases?page=1&limit=20&sort=created_at&order=desc
```

### Filtering

```bash
GET /cases?status=open&type=abuse&created_after=2024-01-01
```

### Sorting

```bash
GET /cases?sort=created_at&order=desc
```

## Error Handling

Errors return appropriate HTTP status codes:

```json
{
  "status": "error",
  "message": "Case not found",
  "code": 404
}
```

**Common Errors:**
- `400` Bad Request - Invalid parameters
- `401` Unauthorized - Missing or invalid token
- `403` Forbidden - Insufficient permissions
- `404` Not Found - Resource doesn't exist
- `500` Server Error - Internal error

## Rate Limiting

- Rate limit: 1000 requests per hour
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## API Documentation

Detailed endpoint documentation:

- [Cases API](#cases-api)
- [Clients API](#clients-api)
- [Users API](#users-api)
- [Communications API](#communications-api)
- [Dashboard API](#dashboard-api)

## Getting Started

1. **Authenticate**: Get API token from login
2. **Make Request**: Include token in Authorization header
3. **Parse Response**: Handle JSON response
4. **Handle Errors**: Implement error handling

## Code Examples

### JavaScript/Node.js

```javascript
const API_URL = 'http://localhost:8888/api/v1';
const TOKEN = 'your-api-token';

async function getCases() {
  const response = await fetch(`${API_URL}/cases`, {
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    }
  });

  const data = await response.json();
  return data.data; // API wraps data in 'data' field
}
```

### Python

```python
import requests

API_URL = 'http://localhost:8888/api/v1'
TOKEN = 'your-api-token'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(f'{API_URL}/cases', headers=headers)
data = response.json()
cases = data['data']
```

### cURL

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8888/api/v1/cases
```

## Webhooks

Webhooks notify your system of important events:

```bash
POST /webhooks/subscribe
{
  "event": "case.created",
  "url": "https://your-app.com/webhook"
}
```

**Events:**
- `case.created`
- `case.updated`
- `case.closed`
- `user.created`
- `message.received`

## Rate Limits & Quotas

| Endpoint | Limit |
|----------|-------|
| Cases | 1000/hr |
| Users | 500/hr |
| Communications | 2000/hr |
| Dashboard | 500/hr |

## Versioning

API follows semantic versioning:
- `v1` - Current stable version
- `v2` - Future version (planned)

Upgrade path provided for backward compatibility.

## Support

- [Issues & Bugs](https://github.com/openchlai/ai/issues)
- [API Questions](#)
- [Community Chat](#)

---

For detailed endpoint documentation, see individual API sections or visit the interactive API documentation at:

```
http://localhost:8888/api/docs
```
