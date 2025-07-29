from django.apps import AppConfig
from celery.signals import worker_process_init
import threading

class StreamingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'streaming'

    def ready(self):
        from streaming import aii_server

        @worker_process_init.connect
        def start_tcp_server(**kwargs):
            print("[CELERY WORKER] Starting Asterisk TCP stream listener...")
            threading.Thread(
                target=aii_server.start_socket_server, daemon=True
            ).start()

# In streaming/apps.py
def ready(self):
    """Start socket server in background"""
    from streaming import aii_server
    aii_server.start_socket_server()  # Now using the public interface