# API Rate Limiting & Throttling

## Overview

OpenCHS implements rate limiting to ensure system stability, fair resource allocation, and protection against abuse. This document explains rate limits for both the Helpline service and AI service.

---

## Helpline Service Rate Limits

### Authentication Endpoints

| Endpoint | Limit | Window | Reason |
|----------|-------|--------|--------|
| `/sendOTP` | 5 requests | 1 minute | Prevent OTP spam |
| `/verifyOTP` | 10 attempts | 5 minutes | Prevent brute force |
| `/changeAuth` | 3 requests | 1 hour | Prevent password cycling |

### Case Management Endpoints

| Endpoint | Limit | Window |
|----------|-------|--------|
| `GET /cases` | 100 requests | 1 hour |
| `POST /cases` | 50 requests | 1 hour |
| `PUT /cases/{id}` | 100 requests | 1 hour |
| `DELETE /cases/{id}` | 10 requests | 1 hour |

### File Upload Endpoints

| Endpoint | Limit | Window | Max Size |
|----------|-------|--------|----------|
| `POST /cases/{id}/attachments` | 10 uploads | 1 minute | 100 MB |

### Search Endpoints

| Endpoint | Limit | Window |
|----------|-------|--------|
| `GET /search/cases` | 60 requests | 1 minute |

---

## AI Service Rate Limits

### Audio Processing Endpoints

| Endpoint | Limit | Window | Reason |
|----------|-------|--------|--------|
| `POST /audio/process` | 50 requests | 1 hour | GPU resource management |
| `POST /audio/analyze` | 100 requests | 1 hour | Lighter processing |
| `POST /audio/process-stream` | 20 concurrent | - | Connection limits |

### Model Endpoints

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /whisper/transcribe` | 100 requests | 1 hour |
| `POST /translate/` | 200 requests | 1 hour |
| `POST /ner/extract` | 300 requests | 1 hour |
| `POST /classifier/classify` | 300 requests | 1 hour |

### Resource Limits

| Resource | Limit | Reason |
|----------|-------|--------|
| Concurrent GPU requests | 1 | GPU memory management |
| Queue size | 20 tasks | Prevent queue overflow |
| Max audio file size | 100 MB | Processing constraints |
| Max audio duration | 60 minutes | Processing time limits |

---

## Rate Limit Headers

All API responses include rate limit information in headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1632847200
X-RateLimit-Window: 3600
```

**Header Descriptions:**
- `X-RateLimit-Limit` - Maximum requests allowed in window
- `X-RateLimit-Remaining` - Requests remaining in current window
- `X-RateLimit-Reset` - Unix timestamp when limit resets
- `X-RateLimit-Window` - Window duration in seconds

---

## Rate Limit Exceeded Response

When rate limit is exceeded:

**HTTP Status:** `429 Too Many Requests`

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 100,
      "window_seconds": 3600,
      "retry_after": 1800
    }
  }
}
```

**Headers:**
```http
Retry-After: 1800
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1632847200
```

---

## Implementation Examples

### Handling Rate Limits in Python

```python
import requests
import time
from datetime import datetime

class RateLimitedClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def make_request(self, method, endpoint, **kwargs):
        """Make request with automatic rate limit handling"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            response = self.session.request(
                method,
                f"{self.base_url}{endpoint}",
                **kwargs
            )
            
            # Check rate limit headers
            remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get('Retry-After', 60))
                
                print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                
                retry_count += 1
                continue
            
            # Warn if approaching limit
            if remaining < 10:
                reset_dt = datetime.fromtimestamp(reset_time)
                print(f"Warning: Only {remaining} requests remaining until {reset_dt}")
            
            return response
        
        raise Exception("Max retries exceeded for rate-limited request")

# Usage
client = RateLimitedClient('https://your-domain.com/helpline/api')
response = client.make_request('GET', '/cases')
```

### Handling Rate Limits in JavaScript

```javascript
class RateLimitedAPIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.requestQueue = [];
    this.processing = false;
  }

  async makeRequest(method, endpoint, data = null) {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({ method, endpoint, data, resolve, reject });
      this.processQueue();
    });
  }

  async processQueue() {
    if (this.processing || this.requestQueue.length === 0) return;
    
    this.processing = true;
    const { method, endpoint, data, resolve, reject } = this.requestQueue.shift();

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : undefined
      });

      const remaining = parseInt(response.headers.get('X-RateLimit-Remaining') || '0');
      
      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
        
        console.log(`Rate limit exceeded. Retrying in ${retryAfter} seconds`);
        
        // Re-queue the request
        this.requestQueue.unshift({ method, endpoint, data, resolve, reject });
        
        // Wait before processing next
        await new Promise(r => setTimeout(r, retryAfter * 1000));
      } else {
        const result = await response.json();
        resolve(result);
        
        // Warn if approaching limit
        if (remaining < 10) {
          console.warn(`Only ${remaining} requests remaining`);
        }
      }
    } catch (error) {
      reject(error);
    } finally {
      this.processing = false;
      this.processQueue(); // Process next item
    }
  }
}

// Usage
const client = new RateLimitedAPIClient('https://your-domain.com/helpline/api');
const cases = await client.makeRequest('GET', '/cases');
```

---

## Rate Limit Strategies

### 1. Exponential Backoff

```python
import time

def exponential_backoff_request(func, max_retries=5):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed. Waiting {wait_time}s...")
            time.sleep(wait_time)
```

### 2. Token Bucket Algorithm

```python
import time
from threading import Lock

class TokenBucket:
    """Token bucket for client-side rate limiting"""
    
    def __init__(self, rate, capacity):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = Lock()
    
    def consume(self, tokens=1):
        """Consume tokens, wait if insufficient"""
        with self.lock:
            # Refill tokens
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            # Check if enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                # Wait for tokens
                wait_time = (tokens - self.tokens) / self.rate
                time.sleep(wait_time)
                self.tokens = 0
                self.last_update = time.time()
                return True

# Usage
bucket = TokenBucket(rate=10, capacity=100)  # 10 requests/second

def make_api_call():
    bucket.consume(1)
    response = requests.get('https://api.example.com/data')
    return response
```

### 3. Request Queuing

```python
from queue import Queue
from threading import Thread
import time

class RateLimitedQueue:
    """Process requests at controlled rate"""
    
    def __init__(self, rate_limit, window=60):
        self.rate_limit = rate_limit
        self.window = window
        self.queue = Queue()
        self.request_times = []
        
        # Start worker thread
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()
    
    def add_request(self, func, *args, **kwargs):
        """Add request to queue"""
        self.queue.put((func, args, kwargs))
    
    def _process_queue(self):
        """Process queue with rate limiting"""
        while True:
            # Clean old request times
            now = time.time()
            self.request_times = [
                t for t in self.request_times 
                if now - t < self.window
            ]
            
            # Check if can make request
            if len(self.request_times) < self.rate_limit:
                func, args, kwargs = self.queue.get()
                
                try:
                    func(*args, **kwargs)
                    self.request_times.append(time.time())
                except Exception as e:
                    print(f"Request failed: {e}")
            else:
                # Wait before checking again
                time.sleep(1)
```

---

## Best Practices

### 1. Respect Rate Limits
```python
# Bad: Ignore rate limits
for i in range(1000):
    make_api_call()  # Will get rate limited

# Good: Check limits and batch requests
rate_limit = get_rate_limit_info()
batch_size = rate_limit['remaining']

for batch in chunks(items, batch_size):
    process_batch(batch)
    if rate_limit['remaining'] == 0:
        wait_until(rate_limit['reset_time'])
```

### 2. Cache Responses
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_case(case_id):
    """Cache case data to reduce API calls"""
    response = requests.get(f'/cases/{case_id}')
    return response.json()
```

### 3. Batch Operations
```python
# Bad: Individual requests
for text in texts:
    translate(text)  # 100 API calls

# Good: Batch request
translate_batch(texts)  # 1 API call
```

### 4. Monitor Usage
```python
import logging

def track_api_usage(func):
    """Decorator to track API usage"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = func(*args, **kwargs)
            duration = time.time() - start_time
            
            remaining = response.headers.get('X-RateLimit-Remaining')
            
            logging.info(
                f"API call: {func.__name__}, "
                f"duration: {duration:.2f}s, "
                f"remaining: {remaining}"
            )
            
            return response
        except Exception as e:
            logging.error(f"API call failed: {e}")
            raise
    
    return wrapper
```

---

## Requesting Rate Limit Increases

For production deployments requiring higher limits:

1. **Document usage patterns:**
   - Average requests per minute/hour/day
   - Peak usage times
   - Use case justification

2. **Submit request:**
   ```json
   {
     "organization": "Your Organization",
     "use_case": "Child protection helpline with 1000+ daily cases",
     "current_limit": "100 requests/hour",
     "requested_limit": "500 requests/hour",
     "justification": "Handling increased call volume during crisis"
   }
   ```

3. **Contact:** support@bitz-itc.com

---

## Monitoring Rate Limits

### Check Current Usage

```bash
# Get rate limit info
curl -I https://your-domain.com/helpline/api/cases \
  -H "Cookie: HELPLINE_SESSION_ID=your-session"

# Response headers
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1632847200
```

### Track Limits Programmatically

```python
def get_rate_limit_status(response):
    """Extract rate limit info from response"""
    return {
        'limit': int(response.headers.get('X-RateLimit-Limit', 0)),
        'remaining': int(response.headers.get('X-RateLimit-Remaining', 0)),
        'reset': int(response.headers.get('X-RateLimit-Reset', 0)),
        'percentage_used': (
            1 - int(response.headers.get('X-RateLimit-Remaining', 0)) / 
            int(response.headers.get('X-RateLimit-Limit', 1))
        ) * 100
    }
```

---

## Troubleshooting

### Issue: Constant 429 Errors

**Causes:**
- Too many requests in short period
- Multiple clients sharing same IP
- Retry logic too aggressive

**Solutions:**
- Implement exponential backoff
- Use request queuing
- Distribute requests over time
- Cache responses

### Issue: Inconsistent Rate Limits

**Causes:**
- Different limits for different endpoints
- Limits per user vs per IP
- Development vs production limits

**Solutions:**
- Check endpoint-specific limits
- Verify authentication method
- Review environment configuration

For more information, see the [Helpline API Endpoints](helpline-api-endpoints.md) and [AI Service API Endpoints](ai-service-api-endpoints.md).