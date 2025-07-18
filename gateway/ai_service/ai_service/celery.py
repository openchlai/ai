# ai_service/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')

app = Celery('ai_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
