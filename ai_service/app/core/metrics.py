"""
Prometheus Metrics for AI Service
Tracks API performance, model processing times, and system health
"""
import logging
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time

logger = logging.getLogger(__name__)

# ============================================
# API METRICS
# ============================================

# Request counters
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# Request duration histogram
api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf'))
)

# Active requests gauge
api_active_requests = Gauge(
    'api_active_requests',
    'Number of active API requests',
    ['endpoint']
)

# Upload file size
api_upload_size_bytes = Histogram(
    'api_upload_size_bytes',
    'Size of uploaded files in bytes',
    ['endpoint'],
    buckets=(1024, 10240, 102400, 1048576, 10485760, 104857600, float('inf'))
)

# ============================================
# MODEL PROCESSING METRICS
# ============================================

# Model processing duration
model_processing_seconds = Histogram(
    'model_processing_seconds',
    'Model processing time in seconds',
    ['model', 'operation'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf'))
)

# Model success/failure counter
model_operations_total = Counter(
    'model_operations_total',
    'Total model operations',
    ['model', 'operation', 'status']
)

# Model loading status
model_loaded = Gauge(
    'model_loaded',
    'Whether a model is currently loaded (1=loaded, 0=not loaded)',
    ['model']
)

# ============================================
# CELERY METRICS
# ============================================

# Queue length
celery_queue_length = Gauge(
    'celery_queue_length',
    'Number of tasks in Celery queue',
    ['queue']
)

# Task duration
celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task', 'state'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, float('inf'))
)

# Task counter
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task', 'state']
)

# Active tasks
celery_active_tasks = Gauge(
    'celery_active_tasks',
    'Number of active Celery tasks',
    ['queue']
)

# Workers online
celery_workers_online = Gauge(
    'celery_workers_online',
    'Number of online Celery workers'
)

# ============================================
# STREAMING METRICS
# ============================================

# Active streaming sessions
streaming_active_sessions = Gauge(
    'streaming_active_sessions',
    'Number of active streaming sessions',
    ['type']
)

# Streaming latency
streaming_latency_seconds = Histogram(
    'streaming_latency_seconds',
    'Streaming processing latency in seconds',
    ['session_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf'))
)

# Audio buffer status
streaming_buffer_size_bytes = Gauge(
    'streaming_buffer_size_bytes',
    'Current audio buffer size in bytes',
    ['session_id']
)

# ============================================
# SYSTEM INFO
# ============================================

# Application info
app_info = Info(
    'app_info',
    'Application information'
)

# ============================================
# HELPER DECORATORS
# ============================================

def track_model_time(model_name: str, operation: str = "process"):
    """
    Decorator to track model processing time
    
    Usage:
        @track_model_time("whisper", "transcribe")
        def transcribe_audio(audio):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                model_processing_seconds.labels(model=model_name, operation=operation).observe(duration)
                model_operations_total.labels(model=model_name, operation=operation, status="success").inc()
                return result
            except Exception as e:
                duration = time.time() - start_time
                model_processing_seconds.labels(model=model_name, operation=operation).observe(duration)
                model_operations_total.labels(model=model_name, operation=operation, status="failure").inc()
                raise
        return wrapper
    return decorator


def track_api_time(endpoint: str):
    """
    Decorator to track API endpoint time
    
    Usage:
        @track_api_time("/audio/process")
        async def process_audio():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            api_active_requests.labels(endpoint=endpoint).inc()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                api_request_duration_seconds.labels(method="POST", endpoint=endpoint).observe(duration)
                return result
            finally:
                api_active_requests.labels(endpoint=endpoint).dec()
        return wrapper
    return decorator


# ============================================
# METRIC UPDATE FUNCTIONS
# ============================================

def update_queue_metrics(queue_name: str, length: int):
    """Update Celery queue length metric"""
    celery_queue_length.labels(queue=queue_name).set(length)


def update_worker_count(count: int):
    """Update number of online workers"""
    celery_workers_online.set(count)


def update_model_status(model_name: str, loaded: bool):
    """Update model loading status"""
    model_loaded.labels(model=model_name).set(1 if loaded else 0)


def record_upload_size(endpoint: str, size_bytes: int):
    """Record uploaded file size"""
    api_upload_size_bytes.labels(endpoint=endpoint).observe(size_bytes)


def update_streaming_sessions(session_type: str, count: int):
    """Update active streaming session count"""
    streaming_active_sessions.labels(type=session_type).set(count)


def record_streaming_latency(session_type: str, latency_seconds: float):
    """Record streaming latency"""
    streaming_latency_seconds.labels(session_type=session_type).observe(latency_seconds)


# ============================================
# INITIALIZATION
# ============================================

def initialize_metrics(app_name: str, version: str, site_id: str):
    """Initialize application info metric"""
    app_info.info({
        'app_name': app_name,
        'version': version,
        'site_id': site_id
    })
    logger.info(f"Prometheus metrics initialized for {app_name} v{version}")
