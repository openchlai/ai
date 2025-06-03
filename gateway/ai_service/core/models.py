from django.db import models
from django.db.models import JSONField

class AudioFile(models.Model):
    audio = models.FileField(upload_to='audio_files/')
    transcript = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    annotated_text = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    insights = JSONField(blank=True, null=True)  # Stores the insights JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AudioFile {self.id} - {self.created_at}"