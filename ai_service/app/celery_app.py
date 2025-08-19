# app/celery_app.py - MLOps Production Configuration
from celery import Celery
import os

def get_redis_url():
    if os.getenv("DOCKER_CONTAINER") or os.path.exists("/.dockerenv"):
        return os.getenv("REDIS_URL", "redis://redis:6379/0")
    else:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

broker_url = get_redis_url()
result_backend = get_redis_url().replace("/0", "/1")

celery_app = Celery(
    "audio_pipeline",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks.audio_tasks", "app.tasks.inference_tasks"]
)

# PRODUCTION-GRADE CONFIGURATION
celery_app.conf.update(
    # Serialization - KEY FIX
    task_serializer="json",
    result_serializer="json", 
    accept_content=["json"],
    
    worker_pool='solo',
    worker_concurrency=1,  # Only 1 task at a time for GPU
    
    # Task execution settings
    task_soft_time_limit=300,
    task_time_limit=600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Critical for GPU tasks
    
    # Result backend settings - CRITICAL FIXES
    result_expires=7200,  # 2 hours instead of 1
    result_backend_max_retries=3,  # Reduce retries
    result_compression='gzip',  # Compress large results
    
    # Task routing
    task_routes={
        # Heavy audio processing tasks
        'app.tasks.audio_tasks.process_audio_task': {'queue': 'audio_processing'},
        'app.tasks.audio_tasks.process_audio_quick_task': {'queue': 'audio_quick'},
        'app.tasks.audio_tasks.process_streaming_audio_task': {'queue': 'audio_streaming'},
        'app.tasks.audio_tasks.process_post_call_audio_task': {'queue': 'audio_processing'},
        
        # Lightweight inference tasks (higher priority)
        'app.tasks.inference_tasks.whisper_transcribe_inference': {'queue': 'inference'},
        'app.tasks.inference_tasks.whisper_get_info': {'queue': 'inference'},
        'app.tasks.inference_tasks.whisper_get_languages': {'queue': 'inference'},
        'app.tasks.inference_tasks.ner_extract_inference': {'queue': 'inference'},
        'app.tasks.inference_tasks.translator_inference': {'queue': 'inference'},
        'app.tasks.inference_tasks.summarizer_inference': {'queue': 'inference'},
        'app.tasks.inference_tasks.classifier_inference': {'queue': 'inference'},
        'app.tasks.inference_tasks.qa_inference': {'queue': 'inference'},
    },
    
    # Error handling - CRITICAL
    task_reject_on_worker_lost=True,
    task_ignore_result=False,  # We need results
    
    # Redis connection settings - IMPORTANT
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_pool_limit=10,
    
    # Worker settings
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # AVOID PROBLEMATIC SETTINGS
    # Do NOT use these - they cause serialization issues:
    # task_always_eager=False,
    # task_store_eager_result=False,
)