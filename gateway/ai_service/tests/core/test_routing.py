
from django.urls import path
from core import consumers

websocket_urlpatterns = [
    path('ws/audio/', consumers.AudioConsumer.as_asgi()),
]
