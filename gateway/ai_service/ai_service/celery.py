# ai_service/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')

app = Celery('ai_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ---- Add queue routing (NEW) ----
app.conf.task_routes = {
    'core.tasks.process_audio_streaming': {'queue': 'streaming'},
    # You can also explicitly set default queue tasks:
    'core.tasks.process_audio_pipeline': {'queue': 'default'},
}

# Optional: declare the queues explicitly
app.conf.task_queues = {
    'default': {},
    'streaming': {},
}
