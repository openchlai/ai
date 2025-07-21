from django.urls import path
from .views import AudioUploadView, TaskStatusView, AudioResultView, HealthView



urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio-upload'),
    path('task_status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path('result/<int:audio_id>/', AudioResultView.as_view(), name='audio-result'),
    path('health/', HealthView.as_view(), name='health'),
]
