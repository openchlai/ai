from django.urls import path
from .views import StartTrainingView, TrainingStatusView

urlpatterns = [
    path('training/start/', StartTrainingView.as_view(), name='start-training'),
    path('training/status/<str:task_id>/', TrainingStatusView.as_view(), name='training-status'),
]