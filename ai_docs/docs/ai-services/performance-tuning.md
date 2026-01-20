# Performance Tuning

## Overview

This guide covers optimization strategies for maximizing throughput and minimizing latency of the AI Service.

## Hardware Optimization

### GPU Selection

| GPU Model | VRAM | Throughput | Latency | Cost |
|-----------|------|-----------|---------|------|
| NVIDIA A100 | 80GB | Excellent | <5ms | High |
| NVIDIA A10 | 24GB | Good | 5-10ms | Medium |
| NVIDIA V100 | 32GB | Good | 5-10ms | Medium |
| NVIDIA T4 | 16GB | Fair | 10-20ms | Low |

### CPU vs GPU Trade-offs

```bash
# GPU Processing (Fast, Resource-Intensive)
WHISPER_DEVICE=cuda           # Use GPU
BATCH_SIZE=4                  # Larger batches
MAX_CONCURRENT_GPU_REQUESTS=2 # Control concurrency

# CPU Processing (Slower, Lower Resource)
WHISPER_DEVICE=cpu            # Use CPU
BATCH_SIZE=1                  # Smaller batches
ENABLE_OPTIMIZATION=true      # Enable CPU optimizations
```

### Memory Optimization

```bash
# Reduce GPU memory usage
GPU_MEMORY_FRACTION=0.8       # Use 80% of GPU VRAM
CACHE_MODELS_IN_GPU=false     # Don't cache all models
UNLOAD_MODELS_AFTER_USE=true  # Free memory after use

# Enable 8-bit quantization (less memory)
QUANTIZE_MODELS=true
QUANTIZATION_TYPE="int8"
```

## Model Optimization

### Model Quantization

```bash
# Use lighter model variants for real-time processing
# Large-V3 for batch (accurate)
POSTCALL_WHISPER_MODEL=large-v3
POSTCALL_WHISPER_COMPUTE_TYPE=float16

# Base for real-time (faster)
REALTIME_WHISPER_MODEL=base
REALTIME_WHISPER_COMPUTE_TYPE=int8
```

### Model Caching

```bash
# Cache models in memory
CACHE_MODELS_IN_MEMORY=true
MODEL_CACHE_SIZE=5  # Keep 5 models cached

# Cache results
CACHE_RESULTS=true
RESULT_CACHE_TTL=3600  # 1 hour
```

## Processing Optimization

### Batch Processing

```bash
# Increase batch size for throughput
BATCH_SIZE=4      # Process 4 audio files at once (uses more GPU memory)

# Reduce batch size for latency
BATCH_SIZE=1      # Process one at a time (lower latency)

# Adaptive batching
ADAPTIVE_BATCHING=true
MIN_BATCH_SIZE=1
MAX_BATCH_SIZE=8
```

### Pipeline Optimization

```bash
# Parallel processing (faster)
PARALLEL_PROCESSING=true
MAX_PARALLEL_TASKS=4

# Sequential processing (more stable)
PARALLEL_PROCESSING=false

# Skip unnecessary models
INCLUDE_TRANSLATION=false     # Only if needed
INCLUDE_INSIGHTS=false        # Only if needed
```

### Queue Management

```bash
# Processing queue settings
MAX_QUEUE_SIZE=50             # Maximum queued tasks
QUEUE_PRIORITY_ENABLED=true   # Process high-priority first

# Worker pool
CELERY_WORKER_POOL_SIZE=4    # 4 concurrent workers
CELERY_MAX_RETRIES=3          # Retry failed tasks
```

## Network Optimization

### Streaming Configuration

```bash
# Real-time streaming settings
STREAMING_BUFFER_SIZE=320     # Audio buffer size (bytes)
STREAMING_CHUNK_SIZE=32000    # Process chunks of audio
STREAMING_INTERVAL=0.1        # Update interval (seconds)

# TCP Asterisk optimization
TCP_BUFFER_SIZE=65536         # Network buffer size
TCP_SOCKET_TIMEOUT=30         # Socket timeout
```

### API Response Optimization

```bash
# Response compression
ENABLE_GZIP=true
MIN_GZIP_SIZE=1000  # Compress responses > 1KB

# Pagination for large results
RESULTS_PAGE_SIZE=100
MAX_RESULTS_PER_REQUEST=1000
```

## Database Optimization

### Query Optimization

```bash
# Enable query caching
ENABLE_QUERY_CACHE=true
QUERY_CACHE_SIZE=1000

# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
```

### Indexing

```python
# Add database indexes for frequently queried fields
CREATE INDEX idx_call_id ON calls(call_id);
CREATE INDEX idx_created_at ON calls(created_at);
CREATE INDEX idx_status ON tasks(status);
```

## Redis Optimization

### Caching Strategy

```bash
# Cache results
REDIS_CACHE_ENABLED=true
REDIS_CACHE_DB=2

# Set TTL for cache entries
CACHE_TTL_SECONDS=3600  # 1 hour

# Eviction policy
REDIS_MAXMEMORY_POLICY=allkeys-lru  # Evict least recently used
REDIS_MAXMEMORY=4gb
```

### Connection Pooling

```bash
# Redis connection pool
REDIS_POOL_SIZE=10
REDIS_MAX_CONNECTIONS=50
```

## Monitoring Performance

### Key Metrics to Monitor

```bash
# Response time
curl -w '@curl-format.txt' -o /dev/null -s http://localhost:8125/health

# Throughput (requests per second)
# Monitor via Prometheus: rate(requests_total[1m])

# GPU utilization
nvidia-smi dmon -c 1

# Memory usage
free -h
```

### Prometheus Metrics

```bash
# Access Prometheus metrics
curl http://localhost:8125/metrics

# Key metrics:
# - request_duration_seconds (latency)
# - requests_total (throughput)
# - gpu_memory_usage_bytes
# - task_queue_length
```

### Flower Monitoring

```bash
# Access Flower at http://localhost:5555
# Monitor:
# - Active tasks
# - Task execution time
# - Worker status
# - Failed tasks
```

## Performance Tuning Examples

### Scenario 1: Low Latency Real-Time Processing

```bash
# Configuration for minimal latency
DEFAULT_PROCESSING_MODE=realtime_only
REALTIME_WHISPER_MODEL=base
REALTIME_WHISPER_COMPUTE_TYPE=int8
BATCH_SIZE=1
MAX_CONCURRENT_GPU_REQUESTS=1
STREAMING_INTERVAL=0.1

# Disable unnecessary processing
INCLUDE_TRANSLATION=false
INCLUDE_INSIGHTS=false
```

### Scenario 2: High Throughput Batch Processing

```bash
# Configuration for maximum throughput
DEFAULT_PROCESSING_MODE=postcall_only
POSTCALL_WHISPER_MODEL=large-v3
BATCH_SIZE=8
MAX_CONCURRENT_GPU_REQUESTS=2
PARALLEL_PROCESSING=true
MAX_PARALLEL_TASKS=4

# Enable all features
INCLUDE_TRANSLATION=true
INCLUDE_INSIGHTS=true
```

### Scenario 3: Balanced Production Setup

```bash
# Configuration for balance between latency and throughput
DEFAULT_PROCESSING_MODE=hybrid
REALTIME_WHISPER_MODEL=base
POSTCALL_WHISPER_MODEL=large-v3
BATCH_SIZE=2
MAX_CONCURRENT_GPU_REQUESTS=2
CACHE_RESULTS=true
RESULT_CACHE_TTL=3600
```

## Load Testing

### Test with ApacheBench

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8125/health

# Results show:
# - Requests per second
# - Time per request
# - Failed requests
```

### Test with Locust

```python
from locust import HttpUser, task

class AudioProcessing(HttpUser):
    @task
    def process_audio(self):
        with open("test.wav", "rb") as f:
            self.client.post(
                "/audio/process",
                files={"audio": f},
                data={"language": "sw"}
            )
```

```bash
# Run load test
locust -f locustfile.py --host=http://localhost:8125
```

## Bottleneck Analysis

### Identify Bottlenecks

```bash
# CPU bottleneck
# - Top processes using CPU
top -b -n 1 | head -20

# GPU bottleneck
nvidia-smi

# Memory bottleneck
free -h
vm

# I/O bottleneck
iostat -x 1 5

# Network bottleneck
nethogs
```

### Profiling

```bash
# Profile CPU usage
python -m cProfile -s cumtime app/main.py

# Profile memory usage
python -m memory_profiler app/main.py

# Profile with py-spy
py-spy record -o profile.svg -- python app/main.py
```

## Optimization Checklist

- [ ] GPU properly configured and detected
- [ ] Model quantization enabled where appropriate
- [ ] Batch size optimized for workload
- [ ] Caching enabled for frequently accessed data
- [ ] Database indices created for common queries
- [ ] Connection pooling configured
- [ ] Monitoring enabled (Prometheus, Flower)
- [ ] Load testing performed
- [ ] Bottlenecks identified and resolved
- [ ] Response times acceptable (<2s for real-time)
- [ ] Throughput meets requirements (>50 calls/hour)
