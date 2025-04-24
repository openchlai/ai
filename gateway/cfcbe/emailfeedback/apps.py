from django.apps import AppConfig


class EmailfeedbackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "emailfeedback"

    def ready(self):
            import emailfeedback.signals