from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Import inside ready() to avoid AppRegistryNotReady errors
        if not hasattr(self, 'already_run'):
            self.already_run = True
            
            # Only start in production or when running the actual server
            # (not during management commands like migrate, collectstatic, etc.)
            import sys
            if 'runserver' in sys.argv:
                try:
                    from core.websocket import start_websocket_client
                    from threading import Thread
                    
                    logger.info("Starting WebSocket client thread...")
                    thread = Thread(target=start_websocket_client)
                    thread.daemon = True  # Daemonize thread
                    thread.start()
                except Exception as e:
                    logger.error(f"Failed to start WebSocket client: {str(e)}")