from rest_framework import serializers

class TrainingSessionSerializer(serializers.Serializer):
    """
    Serializer for training session data from main backend
    """
    session_id = serializers.UUIDField(required=True)
    config = serializers.JSONField(required=True)