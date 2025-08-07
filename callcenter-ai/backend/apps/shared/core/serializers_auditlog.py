from rest_framework import serializers
from apps.shared.accounts.serializers import UserSerializer
from apps.shared.core.models import AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    metadata = serializers.JSONField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user', 'action',
            'ip_address', 'object_type', 'object_id',
            'metadata', 'user_agent'
        ]
        read_only_fields = fields

class AuditLogListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user',
            'action', 'object_type', 'object_id'
        ]
        read_only_fields = fields

class AuditLogFilterSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    action = serializers.ChoiceField(
        choices=AuditLog.ACTION_CHOICES,
        required=False
    )
    object_type = serializers.CharField(required=False)
    object_id = serializers.CharField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, data):
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError(
                    "date_from must be before date_to"
                )
        return data
