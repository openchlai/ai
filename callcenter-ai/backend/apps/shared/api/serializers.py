# apps/shared/api/serializers.py
"""
Serializers for API management functionality.
Handles API keys, request logs, and usage statistics with proper security considerations.
"""

import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# Import base serializers from core app
from apps.shared.core.serializers import BaseModelSerializer, TimestampedModelSerializer

from .models import APIKey, APIRequestLog, APIKeyUsageStats

User = get_user_model()


class APIKeySerializer(BaseModelSerializer):
    """
    Serializer for APIKey model.
    Handles display and updates, but never exposes the actual key value.
    """
    
    # Read-only computed fields
    key_prefix = serializers.CharField(read_only=True)
    is_expired = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()
    time_until_reset = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    # Writable fields with validation
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    allowed_origins = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        allow_empty=True,
        help_text="List of allowed origin domains/IPs. Empty list means no restrictions."
    )
    permissions = serializers.JSONField(
        required=False,
        help_text="JSON object defining API permissions. Use dot notation like 'cases.create'."
    )
    
    class Meta(BaseModelSerializer.Meta):
        model = APIKey
        fields = BaseModelSerializer.Meta.fields + [
            'name', 'description', 'key_prefix', 'permissions', 'rate_limit',
            'current_usage', 'usage_reset_at', 'is_active', 'expires_at',
            'last_used_at', 'last_used_ip', 'allowed_origins', 'tenant_name',
            # Computed fields
            'is_expired', 'usage_percentage', 'time_until_reset', 'created_by_name'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'key_prefix', 'current_usage', 'usage_reset_at', 'last_used_at',
            'last_used_ip', 'tenant_name', 'created_by_name'
        ]
    
    def get_is_expired(self, obj):
        """Check if the API key has expired."""
        return obj.is_expired()
    
    def get_usage_percentage(self, obj):
        """Get current usage as percentage of rate limit."""
        return obj.get_usage_percentage()
    
    def get_time_until_reset(self, obj):
        """Get seconds until usage counter resets."""
        if obj.usage_reset_at > timezone.now():
            delta = obj.usage_reset_at - timezone.now()
            return int(delta.total_seconds())
        return 0
    
    def validate_permissions(self, value):
        """Validate permissions structure."""
        if not isinstance(value, dict):
            raise ValidationError("Permissions must be a JSON object")
        
        # Validate permission keys format (dot notation)
        def validate_permission_keys(perms, path=""):
            for key, val in perms.items():
                current_path = f"{path}.{key}" if path else key
                
                # Keys should be lowercase and contain only letters, numbers, underscores
                if not key.replace('_', '').replace('-', '').isalnum():
                    raise ValidationError(
                        f"Invalid permission key '{current_path}': use only letters, numbers, hyphens, and underscores"
                    )
                
                # Values should be either True/False or nested dict
                if isinstance(val, dict):
                    validate_permission_keys(val, current_path)
                elif not isinstance(val, bool):
                    raise ValidationError(
                        f"Permission '{current_path}' must be True, False, or a nested object"
                    )
        
        validate_permission_keys(value)
        return value
    
    def validate_allowed_origins(self, value):
        """Validate allowed origins list."""
        if not isinstance(value, list):
            raise ValidationError("Allowed origins must be a list")
        
        for origin in value:
            if not isinstance(origin, str) or not origin.strip():
                raise ValidationError("Each origin must be a non-empty string")
        
        return [origin.strip() for origin in value]
    
    def validate_rate_limit(self, value):
        """Validate rate limit value."""
        if value < 0:
            raise ValidationError("Rate limit cannot be negative")
        if value > 100000:  # Reasonable upper limit
            raise ValidationError("Rate limit cannot exceed 100,000 requests per hour")
        return value
    
    def validate_expires_at(self, value):
        """Validate expiration date."""
        if value and value <= timezone.now():
            raise ValidationError("Expiration date must be in the future")
        return value


class CreateAPIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for creating new API keys.
    Returns the raw key value on creation (only time it's available).
    """
    
    # Optional fields for creation
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    allowed_origins = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        allow_empty=True,
        default=list
    )
    permissions = serializers.JSONField(required=False, default=dict)
    rate_limit = serializers.IntegerField(default=1000, min_value=1, max_value=100000)
    
    # This will be set after creation and included in response
    raw_key = serializers.CharField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'name', 'description', 'permissions', 'rate_limit', 
            'expires_at', 'allowed_origins', 'raw_key'
        ]
    
    def validate_name(self, value):
        """Validate API key name."""
        if not value.strip():
            raise ValidationError("API key name cannot be empty")
        
        # Check for uniqueness within tenant (will be set in view)
        tenant = self.context.get('tenant')
        if tenant:
            existing = APIKey.objects.filter(
                tenant=tenant,
                name__iexact=value.strip(),
                is_deleted=False
            ).exists()
            if existing:
                raise ValidationError("An API key with this name already exists")
        
        return value.strip()
    
    def validate_permissions(self, value):
        """Validate permissions structure (same as APIKeySerializer)."""
        if not isinstance(value, dict):
            raise ValidationError("Permissions must be a JSON object")
        
        # Use same validation logic as APIKeySerializer
        serializer = APIKeySerializer()
        return serializer.validate_permissions(value)
    
    def create(self, validated_data):
        """Create API key with auto-generated key value."""
        # Extract data that doesn't go directly to model
        name = validated_data.pop('name')
        tenant = validated_data.pop('tenant', None)
        user = validated_data.pop('user', None)
        
        # Create the API key using manager method
        api_key, raw_key = APIKey.objects.create_api_key(
            name=name,
            tenant=tenant,
            user=user,
            **validated_data
        )
        
        # Store raw key for response
        self.raw_key = raw_key
        
        return api_key


class APIRequestLogSerializer(TimestampedModelSerializer):
    """
    Serializer for APIRequestLog model.
    Read-only serializer for viewing API request history.
    """
    
    # Related field display names
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    # Computed fields
    response_time_ms = serializers.SerializerMethodField()
    is_successful = serializers.SerializerMethodField()
    is_error = serializers.SerializerMethodField()
    
    class Meta(TimestampedModelSerializer.Meta):
        model = APIRequestLog
        fields = TimestampedModelSerializer.Meta.fields + [
            # Basic request info
            'endpoint', 'method', 'query_params', 'request_size',
            # Client info
            'ip_address', 'user_agent',
            # Response info
            'status_code', 'response_time', 'response_size', 'response_data',
            # Error info
            'error_message', 'exception_type',
            # Relationships
            'api_key_name', 'tenant_name', 'user_name',
            # Computed fields
            'response_time_ms', 'is_successful', 'is_error',
            # Timestamp
            'timestamp'
        ]
        read_only_fields = '__all__'  # This is a read-only serializer
    
    def get_response_time_ms(self, obj):
        """Get response time in milliseconds."""
        return obj.get_response_time_ms()
    
    def get_is_successful(self, obj):
        """Check if request was successful."""
        return obj.is_successful()
    
    def get_is_error(self, obj):
        """Check if request had an error."""
        return obj.is_client_error() or obj.is_server_error()


class APIKeyUsageStatsSerializer(TimestampedModelSerializer):
    """
    Serializer for APIKeyUsageStats model.
    Used for analytics and reporting.
    """
    
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    success_rate = serializers.SerializerMethodField()
    error_rate = serializers.SerializerMethodField()
    avg_response_time_ms = serializers.SerializerMethodField()
    max_response_time_ms = serializers.SerializerMethodField()
    
    class Meta(TimestampedModelSerializer.Meta):
        model = APIKeyUsageStats
        fields = TimestampedModelSerializer.Meta.fields + [
            'api_key_name', 'date', 'hour',
            'total_requests', 'successful_requests', 'failed_requests',
            'total_bytes_transferred', 'avg_response_time', 'max_response_time',
            # Computed fields
            'success_rate', 'error_rate', 'avg_response_time_ms', 'max_response_time_ms'
        ]
        read_only_fields = '__all__'
    
    def get_success_rate(self, obj):
        """Calculate success rate as percentage."""
        if obj.total_requests == 0:
            return 0
        return (obj.successful_requests / obj.total_requests) * 100
    
    def get_error_rate(self, obj):
        """Calculate error rate as percentage."""
        if obj.total_requests == 0:
            return 0
        return (obj.failed_requests / obj.total_requests) * 100
    
    def get_avg_response_time_ms(self, obj):
        """Get average response time in milliseconds."""
        if obj.avg_response_time:
            return obj.avg_response_time.total_seconds() * 1000
        return None
    
    def get_max_response_time_ms(self, obj):
        """Get max response time in milliseconds."""
        if obj.max_response_time:
            return obj.max_response_time.total_seconds() * 1000
        return None


# Action serializers for specific operations

class SoftDeleteActionSerializer(serializers.Serializer):
    """
    Serializer for soft delete actions.
    Used when deactivating/deleting API keys with a reason.
    """
    reason = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Reason for deactivating this API key"
    )
    
    def validate_reason(self, value):
        """Validate deletion reason."""
        if not value.strip():
            raise ValidationError("Reason cannot be empty")
        return value.strip()


class RegenerateAPIKeySerializer(serializers.Serializer):
    """
    Serializer for API key regeneration.
    Returns new key data including raw key value.
    """
    confirm = serializers.BooleanField(
        required=True,
        help_text="Confirm that you want to regenerate this API key"
    )
    reason = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Optional reason for regenerating the key"
    )
    
    # Response fields
    raw_key = serializers.CharField(read_only=True)
    warning = serializers.CharField(read_only=True)
    
    def validate_confirm(self, value):
        """Ensure confirmation is True."""
        if not value:
            raise ValidationError("You must confirm key regeneration")
        return value


class BulkAPIKeyActionSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on API keys.
    """
    api_key_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50,  # Reasonable limit for bulk operations
        help_text="List of API key IDs to perform action on"
    )
    action = serializers.ChoiceField(
        choices=['activate', 'deactivate', 'delete'],
        help_text="Action to perform on selected API keys"
    )
    reason = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Optional reason for the bulk action"
    )


class APIKeyPermissionCheckSerializer(serializers.Serializer):
    """
    Serializer for checking API key permissions.
    Used to validate whether a key has specific permissions.
    """
    permission = serializers.CharField(
        max_length=100,
        help_text="Permission to check in dot notation (e.g., 'cases.create')"
    )
    
    # Response fields
    has_permission = serializers.BooleanField(read_only=True)
    permission_details = serializers.JSONField(read_only=True)


class APIUsageStatsRequestSerializer(serializers.Serializer):
    """
    Serializer for API usage statistics requests.
    Handles filtering and aggregation parameters.
    """
    period = serializers.ChoiceField(
        choices=['1h', '1d', '7d', '30d'],
        default='7d',
        help_text="Time period for statistics"
    )
    api_key_id = serializers.UUIDField(
        required=False,
        help_text="Optional: filter by specific API key"
    )
    group_by = serializers.ChoiceField(
        choices=['hour', 'day'],
        default='day',
        help_text="Group statistics by hour or day"
    )
    include_errors = serializers.BooleanField(
        default=True,
        help_text="Include error statistics in response"
    )


class APIEndpointStatsSerializer(serializers.Serializer):
    """
    Serializer for endpoint-specific usage statistics.
    """
    endpoint = serializers.CharField(read_only=True)
    total_requests = serializers.IntegerField(read_only=True)
    successful_requests = serializers.IntegerField(read_only=True)
    error_requests = serializers.IntegerField(read_only=True)
    avg_response_time = serializers.FloatField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)


# Platform-level serializers (for platform admin operations)

class PlatformAPIKeySerializer(APIKeySerializer):
    """
    Extended API key serializer for platform administration.
    Includes additional fields and capabilities for platform admins.
    """
    
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)
    is_platform_key = serializers.SerializerMethodField()
    total_requests_30d = serializers.SerializerMethodField()
    
    class Meta(APIKeySerializer.Meta):
        fields = APIKeySerializer.Meta.fields + [
            'tenant_id', 'is_platform_key', 'total_requests_30d'
        ]
    
    def get_is_platform_key(self, obj):
        """Check if this is a platform-wide key."""
        return obj.tenant is None
    
    def get_total_requests_30d(self, obj):
        """Get total requests in last 30 days."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return APIRequestLog.objects.filter(
            api_key=obj,
            timestamp__gte=thirty_days_ago
        ).count()


class TenantUsageSummarySerializer(serializers.Serializer):
    """
    Serializer for cross-tenant usage summaries.
    Used in platform administration for monitoring tenant activity.
    """
    tenant_id = serializers.UUIDField(read_only=True)
    tenant_name = serializers.CharField(read_only=True)
    active_api_keys = serializers.IntegerField(read_only=True)
    total_requests = serializers.IntegerField(read_only=True)
    successful_requests = serializers.IntegerField(read_only=True)
    error_requests = serializers.IntegerField(read_only=True)
    avg_response_time = serializers.FloatField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)


# Validation utilities

def validate_permission_structure(permissions):
    """
    Utility function to validate permission structure.
    Can be used across different serializers.
    """
    if not isinstance(permissions, dict):
        raise ValidationError("Permissions must be a JSON object")
    
    def validate_nested(perms, path=""):
        for key, value in perms.items():
            current_path = f"{path}.{key}" if path else key
            
            # Validate key format
            if not key.replace('_', '').replace('-', '').isalnum():
                raise ValidationError(
                    f"Invalid permission key '{current_path}': use only letters, numbers, hyphens, and underscores"
                )
            
            # Validate value
            if isinstance(value, dict):
                validate_nested(value, current_path)
            elif not isinstance(value, bool):
                raise ValidationError(
                    f"Permission '{current_path}' must be True, False, or a nested object"
                )
    
    validate_nested(permissions)
    return permissions


# Response serializers for complex operations

class APIKeyCreationResponseSerializer(serializers.Serializer):
    """
    Serializer for API key creation response.
    Includes the API key data plus the raw key value.
    """
    api_key = APIKeySerializer(read_only=True)
    raw_key = serializers.CharField(read_only=True)
    warning = serializers.CharField(
        read_only=True,
        default="Save this key - you will not be able to see it again!"
    )


class BulkOperationResponseSerializer(serializers.Serializer):
    """
    Serializer for bulk operation responses.
    """
    success_count = serializers.IntegerField(read_only=True)
    error_count = serializers.IntegerField(read_only=True)
    errors = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    processed_ids = serializers.ListField(
        child=serializers.UUIDField(),
        read_only=True
    )