# audio_data_preparation/serializers.py

from rest_framework import serializers
from .models import AudioProcessingTask

class AudioProcessingTaskSerializer(serializers.ModelSerializer):
    """Serializer for the AudioProcessingTask model"""
    class Meta:
        model = AudioProcessingTask
        fields = ['task_id', 'task_type', 'input_path', 'output_path', 
                  'status', 'created_at', 'completed_at', 'metadata']
        read_only_fields = ['task_id', 'status', 'created_at', 'completed_at', 
                           'output_path', 'metadata']

class AudioPreprocessingRequestSerializer(serializers.Serializer):
    """Serializer for audio preprocessing request"""
    audio_path = serializers.CharField(max_length=255)
    
    # Optional preprocessing parameters
    noise_reduction = serializers.FloatField(required=False, default=0.3)
    normalize = serializers.BooleanField(required=False, default=True)
    
    def validate_audio_path(self, value):
        """Validate that the audio file exists"""
        import os
        if not os.path.isfile(value):
            raise serializers.ValidationError("Audio file does not exist")
        return value

class SpeakerDiarizationRequestSerializer(serializers.Serializer):
    """Serializer for speaker diarization request"""
    audio_path = serializers.CharField(max_length=255)
    
    # Optional diarization parameters
    min_speakers = serializers.IntegerField(required=False, default=2)
    max_speakers = serializers.IntegerField(required=False, default=2)
    
    def validate_audio_path(self, value):
        """Validate that the audio file exists"""
        import os
        if not os.path.isfile(value):
            raise serializers.ValidationError("Audio file does not exist")
        return value
    
    def validate(self, data):
        """Validate that min_speakers <= max_speakers"""
        if data['min_speakers'] > data['max_speakers']:
            raise serializers.ValidationError(
                "min_speakers must be less than or equal to max_speakers")
        return data

class AudioChunkingRequestSerializer(serializers.Serializer):
    """Serializer for audio chunking request"""
    audio_path = serializers.CharField(max_length=255)
    diarization_result = serializers.CharField(required=True)
    
    # Optional chunking parameters
    max_length = serializers.FloatField(required=False, default=10.0)
    overlap = serializers.FloatField(required=False, default=2.0)
    min_chunk = serializers.FloatField(required=False, default=1.0)
    
    def validate_audio_path(self, value):
        """Validate that the audio file exists"""
        import os
        if not os.path.isfile(value):
            raise serializers.ValidationError("Audio file does not exist")
        return value
        
    def validate_diarization_result(self, value):
        """Validate that the diarization result file exists"""
        if value:
            import os
            if not os.path.isfile(value):
                raise serializers.ValidationError("Diarization result file does not exist")
        return value

class TaskStatusSerializer(serializers.Serializer):
    """Serializer for task status request"""
    task_id = serializers.CharField(max_length=100)