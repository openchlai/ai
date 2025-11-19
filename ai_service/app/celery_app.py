# app/celery_app.py - MLOps Production Configuration
# app/celery_app.py - Updated with Model Tasks
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
    # IMPORTANT: Include audio_tasks, model_tasks, and health_tasks
    include=["app.tasks.audio_tasks", "app.tasks.model_tasks", "app.tasks.health_tasks"]
)

# PRODUCTION-GRADE CONFIGURATION
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json", 
    accept_content=["json"],
    
    # Worker settings
    worker_pool='solo',
    worker_concurrency=1,  # 1 task at a time for GPU
    
    # Task execution settings
    task_soft_time_limit=600,  # 10 minutes soft limit
    task_time_limit=900,  # 15 minutes hard limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Critical for GPU tasks
    
    # Result backend settings
    result_expires=7200,  # 2 hours
    result_backend_max_retries=3,
    result_compression='gzip',
    
    # Task routing - UPDATED with model tasks
    task_routes={
        # Audio processing tasks
        'app.tasks.audio_tasks.process_audio_task': {'queue': 'audio_processing'},
        'app.tasks.audio_tasks.process_audio_quick_task': {'queue': 'audio_quick'},
        'app.tasks.audio_tasks.process_streaming_audio_task': {'queue': 'audio_streaming'},

        # Individual model tasks - NEW
        'app.tasks.model_tasks.ner_extract_task': {'queue': 'model_processing'},
        'app.tasks.model_tasks.classifier_classify_task': {'queue': 'model_processing'},
        'app.tasks.model_tasks.translation_translate_task': {'queue': 'model_processing'},
        'app.tasks.model_tasks.summarization_summarize_task': {'queue': 'model_processing'},
        'app.tasks.model_tasks.qa_evaluate_task': {'queue': 'model_processing'},
        'app.tasks.model_tasks.whisper_transcribe_task': {'queue': 'model_processing'},
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Redis connection settings
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