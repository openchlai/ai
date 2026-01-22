# Troubleshooting Guide

## Common Issues and Solutions

### Service Startup Issues

#### Issue: "Connection refused" when accessing API

**Symptoms:**
```
Error: Connection refused
curl: (7) Failed to connect to localhost port 8125
```

**Solutions:**
1. Check if service is running:
```bash
docker-compose ps
# or
ps aux | grep "uvicorn"
```

2. Check port availability:
```bash
netstat -tuln | grep 8125
lsof -i :8125
```

3. Start the service:
```bash
docker-compose up -d api-server
# or
python -m app.main
```

#### Issue: "Redis connection failed"

**Symptoms:**
```
Error: ConnectionError: Error 111 connecting to localhost:6379
```

**Solutions:**
1. Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

2. Check Redis configuration:
```bash
redis-cli CONFIG GET maxmemory
redis-cli INFO memory
```

3. Restart Redis:
```bash
sudo systemctl restart redis-server
# or
docker-compose restart redis
```

### Audio Processing Issues

#### Issue: "Unsupported audio format"

**Symptoms:**
```json
{
  "status": "error",
  "error": "Unsupported audio format"
}
```

**Solutions:**
1. Check supported formats:
```
Supported: WAV, MP3, FLAC, M4A, OGG
```

2. Convert audio to WAV:
```bash
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 16000 output.wav
```

3. Check sample rate:
```bash
# Should be between 8000 and 48000 Hz
ffmpeg -i audio.wav
```

#### Issue: "Audio file too large"

**Symptoms:**
```json
{
  "status": "error",
  "error": "File exceeds maximum size"
}
```

**Solutions:**
1. Check file size:
```bash
ls -lh audio.wav
```

2. Compress audio:
```bash
ffmpeg -i input.wav -b:a 128k output.wav
```

3. Adjust max size in configuration:
```bash
MAX_AUDIO_SIZE_MB=1000  # Increase limit
```

#### Issue: "Audio processing timeout"

**Symptoms:**
```
Task timeout after 300 seconds
```

**Solutions:**
1. Increase request timeout:
```bash
REQUEST_TIMEOUT=600  # 10 minutes
```

2. Check processing queue:
```bash
curl http://localhost:8125/audio/queue/status
```

3. Scale up workers:
```bash
docker-compose up -d --scale celery-worker=4
```

### Model Loading Issues

#### Issue: "CUDA out of memory"

**Symptoms:**
```
CUDA out of memory. Tried to allocate X.XX GiB
```

**Solutions:**
1. Check GPU memory:
```bash
nvidia-smi
```

2. Reduce batch size:
```bash
BATCH_SIZE=1  # Process one at a time
```

3. Enable model quantization:
```bash
QUANTIZE_MODELS=true
QUANTIZATION_TYPE="int8"
```

4. Use smaller model variant:
```bash
# For real-time
REALTIME_WHISPER_MODEL=base

# For batch
POSTCALL_WHISPER_MODEL=small
```

#### Issue: "Model not found"

**Symptoms:**
```
FileNotFoundError: Model not found at path
```

**Solutions:**
1. Verify model path exists:
```bash
ls -la models/
```

2. Download models:
```bash
python scripts/download_models.py
```

3. Check model configuration:
```bash
curl http://localhost:8125/health/models
```

#### Issue: "Insufficient memory for model loading"

**Symptoms:**
```
MemoryError: Unable to load model
```

**Solutions:**
1. Check system memory:
```bash
free -h
```

2. Clear cache:
```bash
redis-cli FLUSHALL
docker system prune -a
```

3. Reduce number of cached models:
```bash
MODEL_CACHE_SIZE=2  # Only keep 2 models in memory
```

### Database Issues

#### Issue: "Database connection failed"

**Symptoms:**
```
Error: (psycopg2.OperationalError) could not connect to server
```

**Solutions:**
1. Check database server:
```bash
docker-compose logs postgres
# or
sudo systemctl status postgresql
```

2. Verify connection string:
```bash
# Check .env file
cat .env | grep DATABASE_URL
```

3. Test connection:
```bash
psql -h localhost -U user -d ai_service -c "SELECT 1"
```

#### Issue: "Disk space full"

**Symptoms:**
```
Error: No space left on device
```

**Solutions:**
1. Check disk usage:
```bash
df -h
du -sh /path/to/data
```

2. Clean up old logs:
```bash
find logs/ -mtime +30 -delete
```

3. Clean up temporary files:
```bash
rm -rf temp/*
docker system prune -a
```

### API Response Issues

#### Issue: "502 Bad Gateway"

**Symptoms:**
```
502 Bad Gateway - The server is temporarily unable to service the request
```

**Solutions:**
1. Check API server:
```bash
docker-compose logs api-server
```

2. Check NGINX configuration:
```bash
nginx -t
```

3. Restart services:
```bash
docker-compose restart nginx api-server
```

#### Issue: "504 Gateway Timeout"

**Symptoms:**
```
504 Gateway Timeout - The server did not respond within the timeout period
```

**Solutions:**
1. Increase timeout in NGINX:
```nginx
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;
```

2. Increase processing timeout:
```bash
REQUEST_TIMEOUT=600
```

3. Restart NGINX:
```bash
docker-compose restart nginx
```

### Authentication Issues

#### Issue: "Invalid or expired token"

**Symptoms:**
```json
{
  "status": "error",
  "error": "Invalid or expired token"
}
```

**Solutions:**
1. Generate new token:
```bash
curl -X POST http://localhost:8125/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

2. Check token expiry:
```bash
# Decoded JWT to verify expiration
```

3. Increase token expiry:
```bash
TOKEN_EXPIRY_MINUTES=120  # 2 hours
```

### Logging and Diagnostics

#### Enable Debug Logging

```bash
# Set environment variables
export LOG_LEVEL=DEBUG
export DEBUG=true

# Or update .env
LOG_LEVEL=DEBUG
DEBUG=true

# Restart services
docker-compose restart api-server celery-worker
```

#### View Logs

```bash
# API logs
docker-compose logs -f api-server

# Worker logs
docker-compose logs -f celery-worker

# All logs
docker-compose logs -f

# Filter by service and follow
docker-compose logs -f --tail=100 api-server
```

#### Get System Information

```bash
# Python and packages
python --version
pip list | grep -E "fastapi|celery|torch"

# Docker info
docker version
docker-compose version

# System resources
uname -a
cat /proc/cpuinfo | grep processor | wc -l
free -h
nvidia-smi
```

### Health Checks

#### Check Overall Health

```bash
curl http://localhost:8125/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

#### Check Component Health

```bash
curl http://localhost:8125/health/detailed | jq
```

#### Check Model Status

```bash
curl http://localhost:8125/health/models | jq
```

#### Check Queue Status

```bash
curl http://localhost:8125/audio/queue/status | jq
```

#### Check Worker Status

```bash
curl http://localhost:8125/audio/workers/status | jq
```

### Performance Issues

#### Issue: Slow audio processing

**Symptoms:**
- Processing takes longer than expected
- High CPU/GPU usage

**Solutions:**
1. Check worker status:
```bash
curl http://localhost:8125/audio/workers/status | jq
```

2. Check queue length:
```bash
curl http://localhost:8125/audio/queue/status | jq '.queue.queued'
```

3. Scale up workers:
```bash
docker-compose up -d --scale celery-worker=4
```

4. Profile performance:
```bash
python -m cProfile -s cumtime app/main.py
```

### Data Issues

#### Issue: Missing or corrupted results

**Symptoms:**
- Task completed but no results
- Partial results returned

**Solutions:**
1. Check task status:
```bash
curl http://localhost:8125/audio/task/{task_id}
```

2. Check database integrity:
```bash
# For SQLite
sqlite3 ai_service.db ".check"

# For PostgreSQL
psql -d ai_service -c "PRAGMA integrity_check"
```

3. Re-process task:
```bash
curl -X DELETE http://localhost:8125/audio/task/{task_id}
# Then resubmit the audio
```

## Getting Help

### Collect Diagnostic Information

```bash
#!/bin/bash
# save_diagnostics.sh

echo "=== System Info ===" > diagnostics.txt
uname -a >> diagnostics.txt

echo -e "\n=== Python Version ===" >> diagnostics.txt
python --version >> diagnostics.txt

echo -e "\n=== Installed Packages ===" >> diagnostics.txt
pip list >> diagnostics.txt

echo -e "\n=== Service Status ===" >> diagnostics.txt
docker-compose ps >> diagnostics.txt

echo -e "\n=== API Health ===" >> diagnostics.txt
curl -s http://localhost:8125/health/detailed >> diagnostics.txt

echo -e "\n=== Recent Logs ===" >> diagnostics.txt
docker-compose logs --tail=50 >> diagnostics.txt

echo "Diagnostics saved to diagnostics.txt"
```

### Support Resources

- GitHub Issues: https://github.com/openchlai/ai-service/issues
- Documentation: https://docs.openchs.org
- Email: support@openchs.org
- Slack: #ai-service (OpenCHS Slack workspace)
