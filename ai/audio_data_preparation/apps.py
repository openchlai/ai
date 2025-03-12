from django.apps import AppConfig


class AudioDataPreparationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audio_data_preparation'

    def ready(self):
        import audio_data_preparation.signals
