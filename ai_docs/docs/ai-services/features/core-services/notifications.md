# Notification System API Documentation

**API Version:** 0.1.0
**Last Updated:** 2026-01-20
**Status:** Production

> **Note:** Response structures may vary slightly based on API version and configuration.
> This documentation reflects API version 0.1.0 running in production mode.

## Overview

The Notification System API provides intelligent filtering and management of real-time agent notifications during call processing. Configure notification modes, track statistics, and test notification delivery.

**Base Path:** `/api/v1/notifications`

---

## Quick Start

```bash
# Get notification system status
curl -X GET "http://localhost:8125/api/v1/notifications/status"

# Get available notification modes
curl -X GET "http://localhost:8125/api/v1/notifications/modes"

# Update notification mode
curl -X POST "http://localhost:8125/api/v1/notifications/configure" \
  -H "Content-Type: application/json" \
  -d '{"mode": "results_only"}'

# Get statistics
curl -X GET "http://localhost:8125/api/v1/notifications/statistics"
```

---

## Notification Modes

### Available Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `all` | Send all notifications (progress, intermediate, results) | Development/testing |
| `results_only` | Only send notifications with actual results (default) | Production |
| `critical_only` | Only send call start/end and final results | High-volume scenarios |
| `disabled` | No notifications sent | Maintenance mode |

---

## API Endpoints

### GET /api/v1/notifications/status
Get current notification system status and configuration.

**Response (200 OK):**
```json
{
  "timestamp": "2026-01-20T14:33:12.052253",
  "notification_system": {
    "enabled": true,
    "mode": "results_only",
    "service_available": true,
    "statistics": {
      "total_considered": 0,
      "total_sent": 0,
      "total_filtered": 0,
      "by_type": {}
    },
    "available_modes": [
      "all",
      "results_only",
      "critical_only",
      "disabled"
    ],
    "configuration": {
      "endpoint_url": "https://agent-service-url/notifications",
      "timeout": 10,
      "max_retries": 3
    }
  }
}
```

**Response Fields:**
- `timestamp` (string): Current server timestamp
- `notification_system` (object): Notification system details
  - `enabled` (boolean): Whether notifications are enabled
  - `mode` (string): Current notification mode
  - `service_available` (boolean): Whether notification service is reachable
  - `statistics` (object): Notification statistics
    - `total_considered` (integer): Total notifications considered
    - `total_sent` (integer): Total notifications sent
    - `total_filtered` (integer): Notifications filtered out
    - `by_type` (object): Statistics by notification type
  - `available_modes` (array): List of available notification modes
  - `configuration` (object): Current configuration settings
    - `endpoint_url` (string): Agent service notification endpoint
    - `timeout` (integer): Request timeout in seconds
    - `max_retries` (integer): Maximum retry attempts

---

### GET /api/v1/notifications/modes
Get available notification modes and their descriptions.

**Response (200 OK):**
```json
{
  "available_modes": [
    {
      "name": "all",
      "description": "Send all notifications (progress, intermediate, results)"
    },
    {
      "name": "results_only",
      "description": "Only send notifications with actual results (default)"
    },
    {
      "name": "critical_only",
      "description": "Only send call start/end and final results"
    },
    {
      "name": "disabled",
      "description": "No notifications sent"
    }
  ],
  "current_mode": "results_only",
  "mode_explanations": {
    "all": "🔔 All updates: Every transcript segment, progress update, and result",
    "results_only": "📊 Results only: Translation, entities, QA scores, summaries, insights",
    "critical_only": "🚨 Critical only: Call start/end and final processing results",
    "disabled": "🔇 Disabled: No notifications sent to agent system"
  }
}
```

---

### POST /api/v1/notifications/configure
Update notification mode at runtime.

**Request Body:**
```json
{
  "mode": "results_only"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification mode updated from 'all' to 'results_only'",
  "previous_mode": "all",
  "new_mode": "results_only",
  "timestamp": "2026-01-20T10:30:00"
}
```

**Error Responses:**
- `400`: Invalid mode specified

---

### GET /api/v1/notifications/statistics
Get notification statistics and filtering metrics.

**Response (200 OK):**
```json
{
  "current_mode": "results_only",
  "summary": {
    "total_considered": 1543,
    "total_sent": 432,
    "total_filtered": 1111,
    "filter_rate_percent": 72.0,
    "send_rate_percent": 28.0
  },
  "by_notification_type": {
    "streaming_transcription_segment": {"sent": 0, "filtered": 543},
    "streaming_translation": {"sent": 234, "filtered": 0},
    "streaming_entities": {"sent": 198, "filtered": 0}
  },
  "timestamp": "2026-01-20T10:30:00"
}
```

---

### POST /api/v1/notifications/statistics/reset
Reset notification statistics.

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification statistics reset",
  "timestamp": "2026-01-20T10:30:00"
}
```

---

### POST /api/v1/notifications/test
Test notification filtering with different scenarios.

**Request Body:**
```json
{
  "call_id": "test_call_123",
  "notification_type": "streaming_translation",
  "include_results": true
}
```

**Response (200 OK):**
```json
{
  "test_scenario": {
    "call_id": "test_call_123",
    "notification_type": "streaming_translation",
    "include_results": true,
    "current_mode": "results_only"
  },
  "filtering_result": {
    "would_send": true,
    "reason": "allowed"
  },
  "mode_behavior": {
    "all": true,
    "results_only": true,
    "critical_only": false,
    "disabled": false
  }
}
```

---

### GET /api/v1/notifications/types
Get all available notification types and their categories.

**Response (200 OK):**
```json
{
  "notification_types": {
    "progress_notifications": [
      "streaming_call_start",
      "streaming_transcription_segment",
      "streaming_translation_progress",
      "streaming_processing_update"
    ],
    "result_notifications": [
      "streaming_translation",
      "streaming_entities",
      "streaming_classification",
      "streaming_qa",
      "streaming_summary",
      "streaming_insights",
      "postcall_gpt_insights"
    ],
    "critical_notifications": [
      "streaming_call_end",
      "system_processing_error",
      "unified_insight"
    ]
  },
  "filtering_behavior": {
    "all": "Sends all types",
    "results_only": "Sends result_notifications + critical_notifications",
    "critical_only": "Sends critical_notifications only",
    "disabled": "Sends no notifications"
  },
  "total_types": 26
}
```

**Note:** The `total_types` count may vary based on system configuration and available notification types. The example above shows the core notification types, but additional types may be registered at runtime.

---

## Notification Type Categories

### Progress Notifications
- `streaming_call_start`: Call session initiated
- `streaming_transcription_segment`: New transcript segment received
- `streaming_translation_progress`: Translation in progress
- `streaming_processing_update`: General processing update

### Result Notifications
- `streaming_translation`: Translation result ready
- `streaming_entities`: NER extraction complete
- `streaming_classification`: Case classification ready
- `streaming_qa`: QA evaluation complete
- `streaming_summary`: Summary generated
- `streaming_insights`: Full insights ready
- `postcall_gpt_insights`: Post-call GPT analysis complete

### Critical Notifications
- `streaming_call_end`: Call session ended
- `system_processing_error`: System error occurred
- `unified_insight`: Combined insights ready

---

## Configuration Guide

### Environment Variables

```bash
# Agent Notification Configuration
ENABLE_AGENT_NOTIFICATIONS=true
NOTIFICATION_MODE=results_only
NOTIFICATION_ENDPOINT_URL=https://your-agent-system.com/api/msg/
NOTIFICATION_AUTH_ENDPOINT_URL=https://your-agent-system.com/api/
NOTIFICATION_BASIC_AUTH=base64_encoded_credentials
NOTIFICATION_REQUEST_TIMEOUT=10
NOTIFICATION_MAX_RETRIES=3
USE_BASE64_ENCODING=true
```

---

## Integration Examples

### Python Example

```python
import requests

class NotificationClient:
    def __init__(self, base_url="http://localhost:8125"):
        self.base_url = base_url

    def set_mode(self, mode):
        """Change notification mode"""
        response = requests.post(
            f"{self.base_url}/api/v1/notifications/configure",
            json={"mode": mode}
        )
        response.raise_for_status()
        return response.json()

    def get_statistics(self):
        """Get notification statistics"""
        response = requests.get(
            f"{self.base_url}/api/v1/notifications/statistics"
        )
        response.raise_for_status()
        return response.json()

# Usage
client = NotificationClient()

# Set to results_only mode for production
client.set_mode("results_only")

# Check statistics
stats = client.get_statistics()
print(f"Filter rate: {stats['summary']['filter_rate_percent']}%")
```

### JavaScript Example

```javascript
async function configureNotifications(mode) {
    const response = await fetch('http://localhost:8125/api/v1/notifications/configure', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode })
    });

    return await response.json();
}

// Set mode
await configureNotifications('results_only');
```

---

## Best Practices

### 1. Production Mode
Use `results_only` mode in production to reduce noise while maintaining critical updates.

### 2. Development/Testing
Use `all` mode during development to see all notification events.

### 3. High-Volume Scenarios
Use `critical_only` mode for high-volume call centers to minimize notification overhead.

### 4. Monitor Statistics
Regularly check statistics to tune filtering based on your needs:

```bash
curl -X GET "http://localhost:8125/api/v1/notifications/statistics"
```

---

## Related Documentation

- [Call Sessions API](call_sessions.md)
- [Agent Feedback API](agent_feedback.md)
- [Deployment Guide](../deployment/ai-service-deployment.md)

---
