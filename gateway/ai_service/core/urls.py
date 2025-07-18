from django.urls import path
from .views import AudioUploadView, TaskStatusView, HealthView



urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio-upload'),
    path('task_status/<str:task_id>/', TaskStatusView.as_view()),
    path('health/', HealthView.as_view(), name='health'),
]
