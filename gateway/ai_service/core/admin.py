from django.contrib import admin
from .models import AudioFile

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'audio', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('transcript', 'summary')