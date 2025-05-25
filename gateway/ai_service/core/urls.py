from django.urls import path
from .views import AudioUploadView

urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio-upload'),
]
