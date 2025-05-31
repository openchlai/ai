from rest_framework import serializers
from .models import AudioFile

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'audio', 'transcript', 'translated_text', 'annotated_text', 'summary', 'insights', 'created_at']
        read_only_fields = ['transcript', 'translated_text', 'annotated_text', 'summary', 'insights', 'created_at']