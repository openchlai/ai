"""
ASGI config for ai_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

<<<<<<< HEAD
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import models.
django_asgi_app = get_asgi_application()

# Import after Django is set up
from core import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')

application = get_asgi_application()
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
