from django.urls import path
<<<<<<< HEAD
from .views import AudioUploadView, TaskStatusView, AudioResultView, HealthView
=======
from .views import AudioUploadView, TaskStatusView, HealthView
>>>>>>> 94764d3335752e5b86366a5dff43db0766aa9299



urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio-upload'),
<<<<<<< HEAD
    path('task_status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path('result/<int:audio_id>/', AudioResultView.as_view(), name='audio-result'),
=======
    path('task_status/<str:task_id>/', TaskStatusView.as_view()),
>>>>>>> 94764d3335752e5b86366a5dff43db0766aa9299
    path('health/', HealthView.as_view(), name='health'),
]
