from rest_framework import serializers
from .models import (
    MyUser, Category, Complaint, AudioFile, Translation,
    Feedback, Metric, TriageLog, CaseworkerAction, Notification
)

# User Serializer
class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'language_preference']

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

# Complaint Serializer
class ComplaintSerializer(serializers.ModelSerializer):
    user = MyUserSerializer(read_only=True)  # Include user details in the response
    category = CategorySerializer(read_only=True)  # Include category details
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )  # For creating/updating with category

    class Meta:
        model = Complaint
        fields = [
            'id', 'user', 'text', 'audio_url', 'language', 'severity',
            'status', 'category', 'category_id', 'created_at', 'updated_at'
        ]

# Audio File Serializer
class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'complaint', 'file_path', 'transcription', 'language', 'created_at']

# Translation Serializer
class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['id', 'complaint', 'source_language', 'target_language', 'translated_text', 'created_at']

# Feedback Serializer
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'complaint', 'rating', 'comments', 'created_at']

# Metric Serializer
class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = ['id', 'metric_type', 'value', 'caseworker', 'created_at']

# Triage Log Serializer
class TriageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriageLog
        fields = ['id', 'complaint', 'severity', 'keywords_detected', 'created_at']

# Caseworker Action Serializer
class CaseworkerActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseworkerAction
        fields = ['id', 'caseworker', 'complaint', 'action', 'timestamp']

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'read_status', 'created_at']
