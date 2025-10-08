# Webhook & Event Reference

## Overview

OpenCHS supports webhooks for real-time event notifications. External systems can subscribe to events and receive HTTP POST requests when specific actions occur in the system.

## Webhook Configuration

### Registering a Webhook

```sql
-- Webhook configuration table
CREATE TABLE webhook_subscription (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  url VARCHAR(500) NOT NULL,
  secret VARCHAR(255) NOT NULL,
  events JSON NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Retry configuration
  max_retries INT DEFAULT 3,
  retry_delay_seconds INT DEFAULT 60,
  
  -- Statistics
  total_deliveries INT DEFAULT 0,
  failed_deliveries INT DEFAULT 0,
  last_delivery_at TIMESTAMP NULL,
  last_success_at TIMESTAMP NULL,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_is_active (is_active)
);
```

### Register via API (Future Implementation)

```bash
curl -X POST https://your-domain.com/helpline/api/webhooks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "External CRM Integration",
    "url": "https://your-system.com/webhooks/openchs",
    "secret": "your-webhook-secret",
    "events": [
      "case.created",
      "case.updated",
      "case.resolved"
    ]
  }'
```

---

## Webhook Payload Structure

All webhook requests follow this format:

```json
{
  "event": "case.created",
  "timestamp": "2025-09-26T14:30:00Z",
  "webhook_id": "wh_abc123",
  "delivery_id": "del_xyz789",
  "data": {
    // Event-specific data
  }
}
```

### HTTP Headers

```
POST /your-webhook-endpoint HTTP/1.1
Host: your-system.com
Content-Type: application/json
X-OpenCHS-Event: case.created
X-OpenCHS-Delivery: del_xyz789
X-OpenCHS-Signature: sha256=abc123...
User-Agent: OpenCHS-Webhooks/1.0
```

### Signature Verification

Verify webhook authenticity using HMAC SHA256:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected_signature}",
        signature
    )

# Usage in webhook handler
@app.route('/webhooks/openchs', methods=['POST'])
def handle_openchs_webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('X-OpenCHS-Signature')
    
    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return {'error': 'Invalid signature'}, 401
    
    data = request.get_json()
    process_webhook_event(data)
    
    return {'status': 'received'}, 200
```

---

## Available Events

### Case Events

#### `case.created`
Triggered when a new case is created.

**Payload:**
```json
{
  "event": "case.created",
  "timestamp": "2025-09-26T14:30:00Z",
  "data": {
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "title": "Child safety concern",
      "description": "Reported concern about child welfare",
      "category": "abuse",
      "subcategory": "physical_abuse",
      "priority": "high",
      "status": "open",
      "reporter_phone": "+254700123456",
      "reporter_email": "reporter@example.com",
      "child_age": 12,
      "child_gender": "female",
      "assigned_user_id": null,
      "created_at": "2025-09-26T14:30:00Z",
      "created_by": 5
    },
    "creator": {
      "id": 5,
      "username": "operator_john",
      "role": "operator"
    }
  }
}
```

#### `case.updated`
Triggered when case details are modified.

**Payload:**
```json
{
  "event": "case.updated",
  "timestamp": "2025-09-26T15:45:00Z",
  "data": {
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "status": "assigned",
      "assigned_user_id": 8
      // ... other fields
    },
    "changes": {
      "status": {
        "old": "open",
        "new": "assigned"
      },
      "assigned_user_id": {
        "old": null,
        "new": 8
      }
    },
    "updated_by": {
      "id": 7,
      "username": "supervisor_jane",
      "role": "supervisor"
    }
  }
}
```

#### `case.assigned`
Triggered when case is assigned to a user.

**Payload:**
```json
{
  "event": "case.assigned",
  "timestamp": "2025-09-26T15:45:00Z",
  "data": {
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "title": "Child safety concern"
    },
    "assigned_to": {
      "id": 8,
      "username": "case_manager_maria",
      "role": "case_manager",
      "organization": "Nairobi Helpline"
    },
    "assigned_by": {
      "id": 7,
      "username": "supervisor_jane"
    }
  }
}
```

#### `case.status_changed`
Triggered when case status changes.

**Payload:**
```json
{
  "event": "case.status_changed",
  "timestamp": "2025-09-27T10:15:00Z",
  "data": {
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234"
    },
    "status": {
      "old": "in_progress",
      "new": "resolved"
    },
    "resolution_notes": "Case successfully resolved. Family provided support services.",
    "changed_by": {
      "id": 8,
      "username": "case_manager_maria"
    }
  }
}
```

#### `case.escalated`
Triggered when case is escalated.

**Payload:**
```json
{
  "event": "case.escalated",
  "timestamp": "2025-09-26T16:00:00Z",
  "data": {
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "priority": "critical"
    },
    "escalation_reason": "Immediate danger to child",
    "escalated_to": {
      "id": 7,
      "username": "supervisor_jane",
      "role": "supervisor"
    },
    "escalated_by": {
      "id": 8,
      "username": "case_manager_maria"
    }
  }
}
```

#### `case.resolved`
Triggered when case is marked as resolved.

**Payload:**
```json
{
  "event": "case.resolved",
  "timestamp": "2025-09-27T10:15:00Z",
  "data": {
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234",
      "title": "Child safety concern",
      "status": "resolved",
      "resolution_time_hours": 19
    },
    "resolution": {
      "outcome": "services_provided",
      "notes": "Family provided counseling and support services",
      "follow_up_required": true,
      "follow_up_date": "2025-10-27"
    },
    "resolved_by": {
      "id": 8,
      "username": "case_manager_maria"
    }
  }
}
```

### Communication Events

#### `communication.received`
Triggered when new communication is logged.

**Payload:**
```json
{
  "event": "communication.received",
  "timestamp": "2025-09-26T14:25:00Z",
  "data": {
    "communication": {
      "id": 456,
      "case_id": 123,
      "contact_type": "call",
      "direction": "inbound",
      "contact_address": "+254700123456",
      "duration": 180,
      "call_status": "answered",
      "disposition": "case_created",
      "created_at": "2025-09-26T14:25:00Z"
    },
    "case": {
      "id": 123,
      "case_number": "CASE-2025-001234"
    }
  }
}
```

#### `audio.processed`
Triggered when audio processing completes.

**Payload:**
```json
{
  "event": "audio.processed",
  "timestamp": "2025-09-26T14:26:30Z",
  "data": {
    "communication_id": 456,
    "case_id": 123,
    "processing_results": {
      "transcript": "Ninahitaji msaada kwa mtoto...",
      "translation": "I need help for a child...",
      "language_detected": "sw",
      "classification": {
        "category": "child_protection",
        "subcategory": "abuse",
        "risk_level": "high",
        "confidence": 0.94
      },
      "entities": {
        "PERSON": ["Maria"],
        "LOC": ["Nairobi", "Kibera"],
        "AGE": ["12 years old"]
      }
    },
    "processing_time_seconds": 23.4
  }
}
```

### AI Events

#### `ai.prediction_complete`
Triggered when AI case prediction completes.

**Payload:**
```json
{
  "event": "ai.prediction_complete",
  "timestamp": "2025-09-26T14:26:00Z",
  "data": {
    "case_id": 123,
    "prediction": {
      "risk_level": "high",
      "confidence": 0.94,
      "classification": "child_protection",
      "recommended_actions": [
        "immediate_intervention",
        "notify_supervisor",
        "contact_child_services"
      ],
      "entities_detected": {
        "PERSON": ["Maria"],
        "LOC": ["Nairobi"],
        "ORG": ["City Hospital"]
      }
    },
    "model_version": "v1.2.3"
  }
}
```

### User Events

#### `user.login`
Triggered when user successfully logs in.

**Payload:**
```json
{
  "event": "user.login",
  "timestamp": "2025-09-26T08:00:00Z",
  "data": {
    "user": {
      "id": 5,
      "username": "operator_john",
      "role": "operator",
      "organization": "Nairobi Helpline"
    },
    "session": {
      "id": "sess_abc123",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  }
}
```

---

## Webhook Best Practices

### Idempotency

Handle duplicate deliveries gracefully:

```python
class WebhookHandler:
    def __init__(self):
        self.processed_deliveries = set()
    
    def handle_webhook(self, data):
        delivery_id = data['delivery_id']
        
        # Check if already processed
        if delivery_id in self.processed_deliveries:
            return {'status': 'already_processed'}, 200
        
        # Process event
        self.process_event(data)
        
        # Mark as processed
        self.processed_deliveries.add(delivery_id)
        
        return {'status': 'processed'}, 200
```

### Async Processing

Process webhooks asynchronously to avoid timeouts:

```python
from celery import Celery

app = Celery('webhooks')

@app.route('/webhooks/openchs', methods=['POST'])
def receive_webhook():
    data = request.get_json()
    
    # Queue for async processing
    process_webhook_async.delay(data)
    
    # Return immediately
    return {'status': 'queued'}, 202

@app.task
def process_webhook_async(data):
    """Process webhook in background"""
    event_type = data['event']
    
    if event_type == 'case.created':
        handle_case_created(data['data'])
    elif event_type == 'case.updated':
        handle_case_updated(data['data'])
    # ... handle other events
```

### Error Handling

```python
@app.route('/webhooks/openchs', methods=['POST'])
def handle_webhook():
    try:
        # Verify signature
        if not verify_signature(request):
            return {'error': 'Invalid signature'}, 401
        
        data = request.get_json()
        
        # Validate payload
        if not validate_webhook_payload(data):
            return {'error': 'Invalid payload'}, 400
        
        # Process event
        result = process_event(data)
        
        return {'status': 'success', 'result': result}, 200
        
    except Exception as e:
        # Log error
        logger.error(f"Webhook processing error: {str(e)}")
        
        # Return 500 to trigger retry
        return {'error': 'Processing failed'}, 500
```

### Retry Logic

OpenCHS will retry failed webhook deliveries:

```
Attempt 1: Immediate
Attempt 2: After 60 seconds
Attempt 3: After 120 seconds
Attempt 4: After 240 seconds
```

**Respond quickly to avoid retries:**
- Return 2xx status within 5 seconds
- Queue long-running tasks
- Use async processing

### Testing Webhooks

```bash
# Simulate webhook locally
curl -X POST http://localhost:5000/webhooks/openchs \
  -H "Content-Type: application/json" \
  -H "X-OpenCHS-Event: case.created" \
  -H "X-OpenCHS-Signature: sha256=..." \
  -d '{
    "event": "case.created",
    "timestamp": "2025-09-26T14:30:00Z",
    "data": {
      "case": {
        "id": 123,
        "case_number": "CASE-2025-001234"
      }
    }
  }'
```

---

## Event Filtering

Subscribe to specific events only:

```json
{
  "events": [
    "case.created",
    "case.resolved",
    "case.escalated"
  ]
}
```

Or use wildcards:

```json
{
  "events": [
    "case.*",           // All case events
    "communication.*",  // All communication events
    "ai.prediction_complete"
  ]
}
```

---

## Monitoring

### Webhook Delivery Logs

```sql
CREATE TABLE webhook_delivery_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  webhook_subscription_id INT NOT NULL,
  delivery_id VARCHAR(100) UNIQUE NOT NULL,
  event VARCHAR(100) NOT NULL,
  payload JSON NOT NULL,
  
  -- Delivery details
  url VARCHAR(500) NOT NULL,
  http_status INT,
  response_body TEXT,
  response_time_ms INT,
  
  -- Retry information
  attempt_number INT DEFAULT 1,
  max_attempts INT DEFAULT 3,
  next_retry_at TIMESTAMP NULL,
  
  -- Status
  status ENUM('pending', 'delivered', 'failed', 'exhausted') DEFAULT 'pending',
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  delivered_at TIMESTAMP NULL,
  
  FOREIGN KEY (webhook_subscription_id) REFERENCES webhook_subscription(id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);
```

### Query Delivery Status

```sql
-- Recent deliveries
SELECT 
    ws.name,
    wdl.event,
    wdl.status,
    wdl.http_status,
    wdl.attempt_number,
    wdl.created_at
FROM 
    webhook_delivery_log wdl
    INNER JOIN webhook_subscription ws ON wdl.webhook_subscription_id = ws.id
WHERE 
    wdl.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY 
    wdl.created_at DESC
LIMIT 100;

-- Failed deliveries requiring attention
SELECT 
    ws.name,
    ws.url,
    COUNT(*) as failed_count,
    MAX(wdl.created_at) as last_failure
FROM 
    webhook_delivery_log wdl
    INNER JOIN webhook_subscription ws ON wdl.webhook_subscription_id = ws.id
WHERE 
    wdl.status = 'failed'
    AND wdl.created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY 
    ws.id, ws.name, ws.url
HAVING 
    failed_count >= 5;
```

---

## Troubleshooting

### Webhook Not Received

1. Check webhook is active and URL is correct
2. Verify firewall allows OpenCHS IP addresses
3. Check webhook delivery logs for errors
4. Test endpoint manually with curl

### Invalid Signature

1. Verify webhook secret matches registration
2. Check signature calculation implementation
3. Ensure payload is not modified before verification

### Slow Processing

1. Implement async processing
2. Return 202 Accepted immediately
3. Process webhooks in background queue

For additional support, see the [Integration Guide](integrating-with-external-systems.md).