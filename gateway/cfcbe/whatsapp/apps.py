from django.apps import AppConfig


class WhatsappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whatsapp"

    def ready(self):
            import whatsapp.signals
            # from whatsapp.utils import setup
            # setup(1)  # Ensures the token is refreshed on app startup