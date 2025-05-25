from rest_framework import serializers
from .models import AudioFile

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'audio', 'uploaded_at', 'transcript', 'translated_text', 'annotated_text', 'summary']
        read_only_fields = ['transcript', 'translated_text', 'annotated_text', 'summary']
