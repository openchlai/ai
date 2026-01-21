# Agent Feedback API Documentation

**API Version:** 0.1.0
**Last Updated:** 2026-01-20
**Status:** Production

> **Note:** Response structures may vary slightly based on API version and configuration.
> This documentation reflects API version 0.1.0 running in production mode.

## Overview

The Agent Feedback API allows agents to provide ratings and feedback on AI model predictions. This feedback is stored in a database for model performance monitoring and future fine-tuning.

**Base Path:** `/api/v1/agent-feedback`

---

## Quick Start

```bash
# Update feedback for a prediction
curl -X POST "http://localhost:8125/api/v1/agent-feedback/update" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_123456",
    "task": "classification",
    "feedback": 4,
    "reason": "Accurate main category, minor issue with sub-category"
  }'

# Get feedback for a specific call
curl -X GET "http://localhost:8125/api/v1/agent-feedback/call/call_123456"

# Get feedback statistics
curl -X GET "http://localhost:8125/api/v1/agent-feedback/statistics?days=30"

# Health check
curl -X GET "http://localhost:8125/api/v1/agent-feedback/health"
```

---

## Core Features

- **Rating System**: 1-5 star ratings for model predictions
- **Task-Specific Feedback**: Separate feedback for each AI task
- **Reason Tracking**: Optional text explanations for ratings
- **Statistics**: Performance metrics by task and time period
- **Database Storage**: MySQL/PostgreSQL backed for persistence

---

## API Endpoints

### POST /api/v1/agent-feedback/update
Update feedback for a specific call and task.

**Request Body:**
```json
{
  "call_id": "call_123456",
  "task": "classification",
  "feedback": 4,
  "reason": "Accurate main category, minor issue with sub-category"
}
```

**Parameters:**
- `call_id` (string, required): Unique call identifier
- `task` (string, required): One of: `transcription`, `classification`, `ner`, `summarization`, `translation`, `qa`
- `feedback` (integer, required): Rating from 1 (poor) to 5 (excellent)
- `reason` (string, optional): Explanation for the rating

**Response (200 OK):**
```json
{
  "id": 1543,
  "call_id": "call_123456",
  "task": "classification",
  "prediction": {
    "main_category": "VANE",
    "sub_category": "Physical Abuse",
    "priority": "high"
  },
  "feedback": 4,
  "reason": "Accurate main category, minor issue with sub-category",
  "created_at": "2026-01-20T10:30:00",
  "updated_at": "2026-01-20T10:35:00",
  "processing_mode": "streaming",
  "model_version": "cls-gbv-distilbert-v1"
}
```

**Error Responses:**
- `400`: Invalid task or feedback value
- `404`: Feedback entry not found for the specified call_id and task
- `500`: Database error

---

### GET /api/v1/agent-feedback/call/{call_id}
Retrieve feedback entries for a specific call.

**Path Parameters:**
- `call_id` (string, required): Unique call identifier

**Query Parameters:**
- `task` (string, optional): Filter by specific task

**Response (200 OK):**
```json
[
  {
    "id": 1543,
    "call_id": "call_123456",
    "task": "classification",
    "prediction": {
      "main_category": "VANE",
      "sub_category": "Physical Abuse"
    },
    "feedback": 4,
    "reason": "Good overall accuracy",
    "created_at": "2026-01-20T10:30:00",
    "updated_at": "2026-01-20T10:35:00"
  },
  {
    "id": 1544,
    "call_id": "call_123456",
    "task": "ner",
    "prediction": {
      "entities": [
        {"text": "Central Park", "label": "LANDMARK"}
      ]
    },
    "feedback": 5,
    "reason": "All entities correctly identified",
    "created_at": "2026-01-20T10:30:05",
    "updated_at": "2026-01-20T10:36:00"
  }
]
```

**Error Responses:**
- `404`: No feedback found for call_id
- `500`: Database error

---

### GET /api/v1/agent-feedback/statistics
Get feedback statistics for monitoring model performance.

**Query Parameters:**
- `task` (string, optional): Filter by specific task
- `days` (integer, optional, default: 30): Number of days to look back

**Response (200 OK):**
```json
{
  "period_days": 30,
  "tasks": {
    "classification": {
      "total_predictions": 358,
      "rated_predictions": 1,
      "rating_coverage": 0.28,
      "average_rating": 4.0,
      "min_rating": 4,
      "max_rating": 4
    },
    "ner": {
      "total_predictions": 358,
      "rated_predictions": 0,
      "rating_coverage": 0.0,
      "average_rating": null,
      "min_rating": null,
      "max_rating": null
    },
    "summarization": {
      "total_predictions": 358,
      "rated_predictions": 0,
      "rating_coverage": 0.0,
      "average_rating": null,
      "min_rating": null,
      "max_rating": null
    },
    "transcription": {
      "total_predictions": 358,
      "rated_predictions": 4,
      "rating_coverage": 1.12,
      "average_rating": 3.25,
      "min_rating": 3,
      "max_rating": 4
    },
    "translation": {
      "total_predictions": 358,
      "rated_predictions": 2,
      "rating_coverage": 0.56,
      "average_rating": 2.5,
      "min_rating": 2,
      "max_rating": 3
    },
    "qa": {
      "total_predictions": 358,
      "rated_predictions": 0,
      "rating_coverage": 0.0,
      "average_rating": null,
      "min_rating": null,
      "max_rating": null
    }
  }
}
```

**Response Fields:**
- `period_days` (integer): Number of days included in statistics
- `tasks` (object): Statistics per task type

**Per-Task Fields:**
- `total_predictions` (integer): Total number of predictions made for this task
- `rated_predictions` (integer): Number of predictions that have received ratings
- `rating_coverage` (float): Percentage of predictions rated
- `average_rating` (float/null): Average rating score (null if no ratings exist)
- `min_rating` (integer/null): Lowest rating received (null if no ratings exist)
- `max_rating` (integer/null): Highest rating received (null if no ratings exist)

---

### GET /api/v1/agent-feedback/health
Health check endpoint for feedback system.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_feedback_entries": 4320,
  "rated_entries": 3280,
  "rating_coverage": 75.93,
  "timestamp": "2026-01-20T10:30:00"
}
```

**Error Responses:**
- `503`: Service unhealthy (database connection failed)

---

## Rating Guidelines

### Rating Scale

| Rating | Meaning | When to Use |
|--------|---------|-------------|
| ⭐ (1) | Very Poor | Completely wrong, unusable |
| ⭐⭐ (2) | Poor | Major errors, needs significant correction |
| ⭐⭐⭐ (3) | Acceptable | Some errors, but usable with minor edits |
| ⭐⭐⭐⭐ (4) | Good | Mostly accurate, minor improvements possible |
| ⭐⭐⭐⭐⭐ (5) | Excellent | Perfect or near-perfect accuracy |

### Task-Specific Guidelines

#### Classification Feedback
- Rate based on main_category and sub_category accuracy
- Consider priority assignment appropriateness
- Note if intervention recommendation is suitable

#### NER Feedback
- Evaluate entity detection completeness
- Check entity label correctness
- Consider false positives and false negatives

#### Summarization Feedback
- Assess comprehensiveness and accuracy
- Evaluate conciseness and readability
- Check for factual errors or hallucinations

#### Translation Feedback
- Verify meaning preservation
- Check grammatical correctness
- Evaluate naturalness and fluency

#### Transcription Feedback
- Check word accuracy
- Verify punctuation and formatting
- Note any systematic errors

#### QA Feedback
- Evaluate score appropriateness
- Check alignment with actual agent behavior
- Note any missing or incorrect criteria

---

## Database Schema

### AgentFeedback Table

```sql
CREATE TABLE agent_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    call_id VARCHAR(255) NOT NULL,
    task VARCHAR(50) NOT NULL,
    prediction JSON,
    feedback INT NULL,
    reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    processing_mode VARCHAR(50),
    model_version VARCHAR(100),
    UNIQUE KEY unique_call_task (call_id, task),
    INDEX idx_call_id (call_id),
    INDEX idx_task (task),
    INDEX idx_feedback (feedback),
    INDEX idx_created_at (created_at)
);
```

---

## Integration Examples

### Python Example

```python
import requests

class FeedbackClient:
    def __init__(self, base_url="http://localhost:8125"):
        self.base_url = base_url

    def submit_feedback(self, call_id, task, rating, reason=None):
        """Submit agent feedback"""
        payload = {
            "call_id": call_id,
            "task": task,
            "feedback": rating,
            "reason": reason
        }

        response = requests.post(
            f"{self.base_url}/api/v1/agent-feedback/update",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_call_feedback(self, call_id):
        """Get all feedback for a call"""
        response = requests.get(
            f"{self.base_url}/api/v1/agent-feedback/call/{call_id}"
        )
        response.raise_for_status()
        return response.json()

    def get_statistics(self, task=None, days=30):
        """Get feedback statistics"""
        params = {"days": days}
        if task:
            params["task"] = task

        response = requests.get(
            f"{self.base_url}/api/v1/agent-feedback/statistics",
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage
client = FeedbackClient()

# Submit feedback
feedback = client.submit_feedback(
    call_id="call_123456",
    task="classification",
    rating=4,
    reason="Accurate main category, minor sub-category issue"
)
print(f"Feedback ID: {feedback['id']}")

# Get statistics
stats = client.get_statistics(task="classification", days=7)
print(f"Average rating: {stats['tasks']['classification']['average_rating']}")
```

### JavaScript Example

```javascript
async function submitFeedback(callId, task, rating, reason = null) {
    const response = await fetch('http://localhost:8125/api/v1/agent-feedback/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            call_id: callId,
            task: task,
            feedback: rating,
            reason: reason
        })
    });

    return await response.json();
}

// Usage
const feedback = await submitFeedback(
    'call_123456',
    'classification',
    4,
    'Good accuracy overall'
);

console.log(`Feedback submitted: ID ${feedback.id}`);
```

---

## Best Practices

### 1. Timely Feedback
Submit feedback immediately after reviewing predictions while the context is fresh.

### 2. Consistent Rating
Use the rating guidelines consistently across all agents for meaningful statistics.

### 3. Provide Reasons
Always include a reason for ratings below 4 to help identify improvement areas.

### 4. Monitor Statistics
Regularly review statistics to track model performance trends:

```bash
# Weekly check
curl -X GET "http://localhost:8125/api/v1/agent-feedback/statistics?days=7"

# Monthly overview
curl -X GET "http://localhost:8125/api/v1/agent-feedback/statistics?days=30"
```

### 5. Database Maintenance
- Regularly backup the feedback database
- Set up retention policies for old feedback
- Monitor database size and performance

---

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://user:password@host:3306/feedback?charset=utf8mb4
```

---

## Related Documentation

- [Call Sessions API](call_sessions.md)
- [Notifications API](notifications.md)
- [Deployment Guide](../deployment/ai-service-deployment.md)

---
