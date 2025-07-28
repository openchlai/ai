from django.urls import path
<<<<<<< HEAD
from .views import AudioUploadView, TaskStatusView, AudioResultView, HealthView
=======
from .views import AudioUploadView, TaskStatusView, HealthView
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1



urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio-upload'),
<<<<<<< HEAD
    path('task_status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path('result/<int:audio_id>/', AudioResultView.as_view(), name='audio-result'),
=======
    path('task_status/<str:task_id>/', TaskStatusView.as_view()),
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
    path('health/', HealthView.as_view(), name='health'),
]
