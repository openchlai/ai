---
layout: doc
title: Docker Compose Deployment
---

# Docker Compose Deployment

Deploy the AI Service using Docker Compose for production environments.

## Overview

Docker Compose provides a complete stack including:

- **API Server** - FastAPI application (port 8125)
- **Celery Worker** - Background task processing with GPU support
- **Redis** - Message broker and result backend
- **Flower** - Celery monitoring dashboard (port 5555)
- **NGINX** - Reverse proxy and load balancer (ports 80/443)

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Container Runtime (for GPU support)
- 50GB+ disk space
- 16GB+ RAM (32GB recommended)
- NVIDIA GPU with 16GB+ VRAM (recommended)

### Verify Prerequisites

```bash
# Docker version
docker --version

# Docker Compose version
docker compose version

# NVIDIA runtime (for GPU)
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

## Complete Stack Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api-server:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      redis:
        condition: service_healthy
    ports:
      - "8125:8125"
    environment:
      - APP_NAME=AI_Pipeline
      - APP_PORT=8125
      - ENABLE_MODEL_LOADING=false
      - REDIS_URL=redis://redis:6379/0
      - STREAMING_PORT=8301
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8125/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      redis:
        condition: service_healthy
    command: celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery
    environment:
      - ENABLE_MODEL_LOADING=true
      - REDIS_URL=redis://redis:6379/0
      - CUDA_VISIBLE_DEVICES=0
      - WHISPER_DEVICE=cuda
      - WHISPER_COMPUTE_TYPE=float16
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  flower:
    image: mher/flower:2.0
    restart: unless-stopped
    depends_on:
      - redis
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
      - FLOWER_BASIC_AUTH=admin:password
    command: celery --broker=redis://redis:6379/0 flower --port=5555

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    depends_on:
      - api-server
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro

volumes:
  redis_data:
```

---

## Environment Configuration

Create a `.env` file in the project root:

```bash
# ============ APPLICATION ============
APP_NAME=AI_Pipeline
APP_VERSION=0.1.0
APP_PORT=8125
DEBUG=false
LOG_LEVEL=INFO
SITE_ID=production-001

# ============ DATABASE ============
DATABASE_URL=sqlite:///./ai_service.db

# ============ REDIS ============
REDIS_URL=redis://redis:6379/0
REDIS_TASK_DB=1
REDIS_CACHE_DB=2

# ============ RESOURCES ============
MAX_CONCURRENT_GPU_REQUESTS=1
MAX_QUEUE_SIZE=20
REQUEST_TIMEOUT=300
ENABLE_MODEL_LOADING=true

# ============ MODELS ============
WHISPER_COMPUTE_TYPE=float16
WHISPER_DEVICE=cuda
BATCH_SIZE=1
USE_HF_MODELS=true
HF_ASR_MODEL=openai/whisper-large-v3
HF_CLASSIFIER_MODEL=openchs/multitask-classifier
HF_NER_MODEL=openchs/ner-model
HF_TRANSLATOR_MODEL=openchs/translation-model
HF_SUMMARIZER_MODEL=openchs/summarization-model
HF_QA_MODEL=openchs/qa-model

# ============ PROCESSING MODES ============
DEFAULT_PROCESSING_MODE=adaptive
ENABLE_STREAMING_PROCESSING=true
ENABLE_POSTCALL_PROCESSING=true

# ============ STREAMING ============
ENABLE_ASTERISK_TCP=true
STREAMING_HOST=0.0.0.0
STREAMING_PORT=8301

# ============ NOTIFICATIONS ============
NOTIFICATION_ENABLED=true
NOTIFICATION_WEBHOOK_URL=http://localhost:8000/api/notifications
```

---

## NGINX Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api-server:8125;
    }

    server {
        listen 80;
        server_name _;

        # Redirect HTTP to HTTPS (uncomment for production)
        # return 301 https://$server_name$request_uri;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Timeout settings
            proxy_connect_timeout 60s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }

        # Large file uploads
        client_max_body_size 500M;
    }

    # HTTPS server (uncomment for production)
    # server {
    #     listen 443 ssl http2;
    #     server_name _;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #
    #     location / {
    #         proxy_pass http://api;
    #         # ... same as above
    #     }
    # }
}
```

---

## Deployment Commands

### Start Services

```bash
# Start all services in background
docker compose up -d

# Start with build (if Dockerfile changed)
docker compose up -d --build

# Start specific services only
docker compose up -d api-server celery-worker redis
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f celery-worker

# Last 100 lines
docker compose logs --tail=100 api-server
```

### Scale Workers

```bash
# Scale to 3 Celery workers
docker compose up -d --scale celery-worker=3

# Check running containers
docker compose ps
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v

# Stop specific service
docker compose stop celery-worker
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart api-server
```

---

## Health Checks

### Verify Services

```bash
# Check all services are running
docker compose ps

# Check API health
curl http://localhost:8125/health

# Check detailed health
curl http://localhost:8125/health/detailed | jq

# Check model status
curl http://localhost:8125/health/models | jq

# Check Redis
docker compose exec redis redis-cli ping
```

### Access Dashboards

- **Swagger UI**: http://localhost:8125/docs
- **Flower (Celery)**: http://localhost:5555
- **API Health**: http://localhost:8125/health/detailed

---

## Production Considerations

### Security

1. **Change default passwords** in `.env` and `docker-compose.yml`
2. **Enable HTTPS** by uncommenting SSL config in nginx.conf
3. **Restrict port exposure** - only expose 80/443 in production
4. **Use secrets management** for sensitive values

### Performance

1. **Allocate sufficient GPU memory** - at least 16GB VRAM
2. **Configure Redis memory limits** to prevent OOM
3. **Set appropriate worker count** based on load

### Monitoring

1. **Enable Prometheus metrics** at `/metrics`
2. **Set up Grafana dashboards** for visualization
3. **Configure alerting** for critical metrics

### Backup

1. **Redis data**: Back up `redis_data` volume
2. **Logs**: Archive logs regularly
3. **Models**: Models are downloaded from HuggingFace; ensure network access

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs api-server

# Check resource limits
docker stats

# Verify GPU access
docker compose exec celery-worker nvidia-smi
```

### Models not loading

```bash
# Check worker logs
docker compose logs celery-worker | grep -i model

# Verify HuggingFace access
docker compose exec celery-worker python -c "from transformers import AutoModel; print('OK')"
```

### Redis connection issues

```bash
# Test Redis connectivity
docker compose exec api-server redis-cli -h redis ping

# Check Redis logs
docker compose logs redis
```

---

## Next Steps

- [Kubernetes Deployment](./kubernetes.md) - Scale with Kubernetes
- [Manual Installation](./manual.md) - Install without Docker
- [Environment Variables](../configuration/environment-variables.md) - Full configuration reference
