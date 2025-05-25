from django.db import models

class AudioFile(models.Model):
    audio = models.FileField(upload_to='audio/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    annotated_text = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"AudioFile {self.id} uploaded at {self.uploaded_at}"
