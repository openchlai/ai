# Service Status Check Guide

This guide provides instructions for confirming that Docker, Redis, and Celery services are running properly for the AI Service application.

## Prerequisites

- Docker and Docker Compose installed
- Terminal/Command line access
- Project directory: `/Users/mac/ai/gateway/ai_service`

## 1. Docker Services Status

### Check Docker Compose Services
```bash
# Navigate to project directory
cd /Users/mac/ai/gateway/ai_service

# Check all services status
docker compose ps
```

**Expected Output:**
```
NAME                  IMAGE               COMMAND                  SERVICE   CREATED          STATUS                    PORTS
ai_service-celery-1   ai_service-celery   "celery -A ai_servic…"   celery    X minutes ago    Up X minutes              8000/tcp
ai_service-redis-1    redis:7.2-alpine    "docker-entrypoint.s…"   redis     X minutes ago    Up X minutes              0.0.0.0:6379->6379/tcp
ai_service-web-1      ai_service-web      "gunicorn --bind 0.0…"   web       X minutes ago    Up X minutes (healthy)    0.0.0.0:8000->8000/tcp
```

### Check Individual Container Status
```bash
# Check specific container
docker ps --filter "name=ai_service"

# Check container logs
docker compose logs web --tail=20
docker compose logs celery --tail=20
docker compose logs redis --tail=20
```

### Start Services (if not running)
```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d web
docker compose up -d celery
docker compose up -d redis
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop specific service
docker compose stop web
docker compose stop celery
docker compose stop redis
```

## 2. Redis Status Check

### Method 1: Through Docker
```bash
# Check Redis container logs
docker compose logs redis --tail=10

# Connect to Redis CLI through Docker
docker compose exec redis redis-cli ping
```

**Expected Output:** `PONG`

### Method 2: Direct Redis Connection
```bash
# If Redis CLI is installed locally
redis-cli -h localhost -p 6379 ping

# Check Redis info
redis-cli -h localhost -p 6379 info server
```

### Method 3: Test Redis Connectivity
```bash
# Test Redis connection and basic operations
docker compose exec redis redis-cli << EOF
ping
set test_key "test_value"
get test_key
del test_key
EOF
```

### Redis Health Check
```bash
# Check Redis memory usage and stats
docker compose exec redis redis-cli info memory
docker compose exec redis redis-cli info stats
```

## 3. Celery Status Check

### Method 1: Check Celery Worker Status
```bash
# View Celery worker logs
docker compose logs celery --tail=20

# Check if Celery is processing tasks
docker compose exec celery celery -A ai_service inspect active
```

### Method 2: Celery Worker Health Check
```bash
# Check registered tasks
docker compose exec celery celery -A ai_service inspect registered

# Check worker statistics
docker compose exec celery celery -A ai_service inspect stats

# Check worker status
docker compose exec celery celery -A ai_service status
```

### Method 3: Monitor Celery in Real-time
```bash
# Monitor Celery events (press Ctrl+C to exit)
docker compose exec celery celery -A ai_service events

# Monitor Celery with flower (if installed)
docker compose exec celery celery -A ai_service flower
```

## 4. Application Health Checks

### Web Service Health Check
```bash
# Check if web service is responding
curl -I http://localhost:8000

# Check specific endpoint (if health check endpoint exists)
curl http://localhost:8000/health/

# Check Django admin (if configured)
curl http://localhost:8000/admin/
```

### Full Stack Test
```bash
# Test all services together
echo "Testing Docker services..."
docker compose ps

echo "Testing Redis connectivity..."
docker compose exec redis redis-cli ping

echo "Testing Celery worker..."
docker compose exec celery celery -A ai_service inspect active

echo "Testing Web service..."
curl -I http://localhost:8000
```

## 5. Troubleshooting

### Common Issues and Solutions

#### Docker Services Not Starting
```bash
# Check Docker daemon status
docker version
docker info

# Rebuild containers if needed
docker compose build --no-cache
docker compose up -d
```

#### Redis Connection Issues
```bash
# Check if Redis port is accessible
telnet localhost 6379

# Check Redis container specifically
docker compose exec redis redis-cli ping
```

#### Celery Worker Issues
```bash
# Restart Celery worker
docker compose restart celery

# Check Celery configuration
docker compose exec celery python -c "from ai_service import settings; print(settings.CELERY_BROKER_URL)"
```

#### Web Service Issues
```bash
# Check web service logs for errors
docker compose logs web --tail=50

# Restart web service
docker compose restart web

# Check if port 8000 is available
lsof -i :8000
```

## 6. Quick Status Script

Create a simple script to check all services:

```bash
#!/bin/bash
# save as check_services.sh

echo "=== Docker Compose Services ==="
docker compose ps

echo -e "\n=== Redis Status ==="
docker compose exec redis redis-cli ping 2>/dev/null || echo "Redis not accessible"

echo -e "\n=== Celery Status ==="
docker compose exec celery celery -A ai_service inspect active 2>/dev/null || echo "Celery not accessible"

echo -e "\n=== Web Service Status ==="
curl -I http://localhost:8000 2>/dev/null | head -1 || echo "Web service not accessible"

echo -e "\n=== Service Health Summary ==="
echo "✓ Check complete"
```

Make it executable and run:
```bash
chmod +x check_services.sh
./check_services.sh
```

## 7. Monitoring Commands

### Real-time Monitoring
```bash
# Monitor all container logs in real-time
docker compose logs -f

# Monitor specific service logs
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f redis
```

### Resource Usage
```bash
# Check container resource usage
docker stats

# Check specific containers
docker stats ai_service-web-1 ai_service-celery-1 ai_service-redis-1
```

---

## Service URLs and Ports

- **Web Application**: http://localhost:8000
- **Redis**: localhost:6379
- **Celery**: Background service (no direct URL)

## Success Indicators

✅ **All services healthy when:**
- `docker compose ps` shows all services as "Up"
- `redis-cli ping` returns `PONG`
- `celery inspect active` returns worker information
- `curl -I http://localhost:8000` returns HTTP 200 status

---

*Last updated: July 17, 2025*
