# audio_data_preparation/urls.py

from django.urls import path
from .views import (
    AudioPreprocessingView,
    SpeakerDiarizationView,
    AudioChunkingView,
    TaskStatusView,
    TaskListView
)

urlpatterns = [
    path('preprocess/', AudioPreprocessingView.as_view(), name='audio-preprocess'),
    path('diarize/', SpeakerDiarizationView.as_view(), name='speaker-diarize'),
    path('chunk/', AudioChunkingView.as_view(), name='audio-chunk'),
    path('status/<str:task_id>/', TaskStatusView.as_view(), name='task-status-detail'),
    path('status/', TaskStatusView.as_view(), name='task-status'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
]