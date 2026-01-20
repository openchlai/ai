---
layout: doc
title: Quick Start
---

# Quick Start

Get the AI Service up and running in 5 minutes.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Docker** 20.10+ installed
- [ ] **NVIDIA drivers** installed (for GPU support)
- [ ] **NVIDIA Container Runtime** configured (for GPU support)
- [ ] **50GB+** free disk space
- [ ] **Stable internet** connection (for downloading models)

### Verify Prerequisites

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10.x or higher

# Check Docker Compose
docker compose version
# Expected: Docker Compose version v2.x.x

# Check NVIDIA drivers (if using GPU)
nvidia-smi
# Expected: Shows GPU info and driver version

# Check disk space
df -h
# Ensure at least 50GB free
```

---

## Option 1: Docker Compose (Recommended)

The fastest way to get started.

### Step 1: Clone Repository

```bash
git clone https://github.com/openchlai/ai-service.git
cd ai_service
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env
```

**Minimum required settings in `.env`:**

```bash
APP_PORT=8125
REDIS_URL=redis://redis:6379/0
ENABLE_MODEL_LOADING=true
```

### Step 3: Start Services

```bash
# Start all services in background
docker compose up -d

# Wait for services to initialize (2-3 minutes)
# Models need to download on first run
sleep 180
```

### Step 4: Verify Installation

```bash
# Check API health
curl http://localhost:8125/health

# Expected response:
# {"status":"healthy","version":"0.1.0","timestamp":"..."}

# Check detailed status
curl http://localhost:8125/health/detailed | jq

# Check model status
curl http://localhost:8125/health/models | jq
```

### Step 5: Access Documentation

Open your browser to view the interactive API documentation:

```bash
# Swagger UI
open http://localhost:8125/docs

# ReDoc (alternative)
open http://localhost:8125/redoc

# Flower monitoring (Celery tasks)
open http://localhost:5555
```

---

## Option 2: Local Development (Python)

For development and debugging.

### Step 1: Create Virtual Environment

```bash
# Ensure Python 3.11+
python3.11 --version

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg
```

### Step 3: Start Redis

In a separate terminal:

```bash
# Using Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Or install locally
# Ubuntu: sudo apt-get install redis-server
# macOS: brew install redis
redis-server
```

### Step 4: Start Celery Worker

In a separate terminal:

```bash
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery
```

### Step 5: Start API Server

In the main terminal:

```bash
source venv/bin/activate
python -m app.main
```

### Step 6: Verify

```bash
curl http://localhost:8125/health
```

---

## Option 3: Quick Test with Mock Audio

Test the service with sample audio files.

### Prerequisites

Ensure Docker Compose is running (Option 1).

### Run Test

```bash
# Copy test audio files
cp /path/to/audio/*.wav ai_service/test_audio/

# Run quick test
cd ai_service
./scripts/quick_test_mock.sh realtime 1

# Monitor in real-time
tail -f logs/ai-pipeline.log
```

---

## Your First Audio Processing

Once the service is running, try processing an audio file:

### Using cURL

```bash
# Process audio file
curl -X POST \
  -F "audio=@sample.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  http://localhost:8125/audio/process
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Audio processing started",
  "estimated_time": "15-45 seconds",
  "status_endpoint": "/audio/task/550e8400-e29b-41d4-a716-446655440000"
}
```

### Check Task Status

```bash
# Replace TASK_ID with the ID from the response above
curl http://localhost:8125/audio/task/550e8400-e29b-41d4-a716-446655440000 | jq
```

**Response (when complete):**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "results": {
    "transcript": "Msichana mdogo ana miaka 12...",
    "translation": "A small girl is 12 years old...",
    "entities": {
      "PERSON": [...],
      "AGE": [...]
    },
    "classification": {
      "main_category": "child_protection",
      "priority": "high"
    },
    "summary": "..."
  }
}
```

### Stream Real-time Updates

```bash
# Get streaming updates as processing happens
curl -N http://localhost:8125/audio/process-stream \
  -F "audio=@sample.wav" \
  -F "language=sw"
```

---

## Troubleshooting Quick Start

### Issue: "Connection refused" on port 8125

**Cause:** API server not running or still starting.

**Solution:**

```bash
# Check if container is running
docker compose ps

# Check logs
docker compose logs api-server

# Wait for startup to complete
sleep 60 && curl http://localhost:8125/health
```

### Issue: "Model not ready" (503 error)

**Cause:** Models still loading or failed to load.

**Solution:**

```bash
# Check model loading status
curl http://localhost:8125/health/models | jq

# Check worker logs
docker compose logs celery-worker

# Ensure worker has GPU access
docker compose exec celery-worker nvidia-smi
```

### Issue: "Redis connection error"

**Cause:** Redis not running or wrong URL.

**Solution:**

```bash
# Check Redis is running
docker compose ps redis

# Test Redis connection
docker compose exec redis redis-cli ping
# Expected: PONG

# Check REDIS_URL in .env
grep REDIS_URL .env
```

### Issue: Out of disk space

**Cause:** Models and Docker images use significant space.

**Solution:**

```bash
# Check disk space
df -h

# Clean Docker (removes unused images)
docker system prune -a

# Remove old logs
rm -rf logs/*.log
```

---

## Next Steps

Now that the service is running:

1. **Explore the API**: [API Reference](./api-reference/audio-processing.md)
2. **Configure settings**: [Environment Variables](./configuration/environment-variables.md)
3. **Set up production**: [Docker Compose Deployment](./installation/docker-compose.md)
4. **Learn about models**: [AI Features](./features/whisper.md)

---

## Getting Help

- **Documentation**: Browse this documentation site
- **Issues**: [GitHub Issues](https://github.com/openchlai/ai-service/issues)
- **Community**: [GitHub Discussions](https://github.com/openchlai/ai-service/discussions)
