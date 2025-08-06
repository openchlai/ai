"""
Core serializers for the Murima platform.

This module provides base serializers and system model serializers that ensure
consistency across all tenant applications.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, SystemConfiguration, ErrorLog

User = get_user_model()


# Base Serializers - To be inherited by other apps
class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for models that inherit from BaseModel.
    
    Automatically handles:
    - User tracking fields (created_by, updated_by)
    - Soft delete status
    - Read-only timestamp fields
    - Consistent field ordering
    """
    
    # Read-only fields that should never be set via API
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)
    
    # Soft delete fields (usually hidden from API responses)
    is_deleted = serializers.BooleanField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
    deleted_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        abstract = True
        # Common field ordering for all models
        fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
        # Read-only fields that can be extended by child serializers
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
    
    def create(self, validated_data):
        """Automatically set created_by and updated_by from request user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Automatically set updated_by from request user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        Customize the output representation.
        - Hide soft-deleted fields by default
        - Format user fields consistently
        """
        representation = super().to_representation(instance)
        
        # Hide soft delete fields unless specifically requested
        request = self.context.get('request')
        show_deleted_fields = request and request.query_params.get('show_deleted_fields', False)
        
        if not show_deleted_fields:
            representation.pop('is_deleted', None)
            representation.pop('deleted_at', None)
            representation.pop('deleted_by', None)
        
        return representation

class TimestampedModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for models that only inherit from TimestampedModel.
    Used for lookup/reference data that doesn't need full audit trails.
    """
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True
        fields = ['created_at', 'updated_at']
        # Read-only fields that can be extended by child serializers
        read_only_fields = ['created_at', 'updated_at']


class ReadOnlyBaseSerializer(BaseModelSerializer):
    """
    Base serializer for read-only endpoints.
    All fields are read-only except for soft delete actions.
    """
    
    def create(self, validated_data):
        raise serializers.ValidationError("Create operations not allowed on this endpoint")
    
    def update(self, instance, validated_data):
        raise serializers.ValidationError("Update operations not allowed on this endpoint")


# System Model Serializers

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested representations."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields


class ContentTypeSerializer(serializers.ModelSerializer):
    """Serializer for ContentType model."""
    
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']


class AuditLogSerializer(ReadOnlyBaseSerializer):
    """
    Serializer for AuditLog model.
    Read-only - audit logs should never be modified via API.
    """
    
    user = UserBasicSerializer(read_only=True)
    object_type = ContentTypeSerializer(read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = BaseModelSerializer.Meta.fields + [
            'user', 'tenant_name', 'action', 'object_type', 'object_id', 
            'object_repr', 'changes', 'description', 'metadata', 
            'ip_address', 'user_agent'
        ]
        read_only_fields = fields


class AuditLogListSerializer(AuditLogSerializer):
    """
    Simplified serializer for audit log lists.
    Excludes heavy fields like stack traces and detailed metadata.
    """
    
    class Meta(AuditLogSerializer.Meta):
        fields = [
            'id', 'created_at', 'user', 'action', 'object_type', 
            'object_repr', 'description', 'ip_address'
        ]


class SystemConfigurationSerializer(BaseModelSerializer):
    """
    Serializer for SystemConfiguration model.
    Handles validation and type conversion for configuration values.
    """
    
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = SystemConfiguration
        fields = BaseModelSerializer.Meta.fields + [
            'key', 'name', 'value', 'data_type', 'validation_rules',
            'description', 'category', 'is_sensitive', 'is_active'
        ]
        read_only_fields = ['key']  # Key should not be changed after creation
    
    def validate(self, data):
        """
        Validate the configuration value based on data_type.
        """
        data_type = data.get('data_type')
        value = data.get('value')
        
        if data_type and value is not None:
            if data_type == 'integer' and not isinstance(value, int):
                raise serializers.ValidationError({
                    'value': 'Value must be an integer for integer data type'
                })
            elif data_type == 'float' and not isinstance(value, (int, float)):
                raise serializers.ValidationError({
                    'value': 'Value must be a number for float data type'
                })
            elif data_type == 'boolean' and not isinstance(value, bool):
                raise serializers.ValidationError({
                    'value': 'Value must be a boolean for boolean data type'
                })
            elif data_type == 'string' and not isinstance(value, str):
                raise serializers.ValidationError({
                    'value': 'Value must be a string for string data type'
                })
            elif data_type == 'list' and not isinstance(value, list):
                raise serializers.ValidationError({
                    'value': 'Value must be a list for list data type'
                })
        
        return data
    
    def to_representation(self, instance):
        """
        Hide sensitive values in API responses.
        """
        representation = super().to_representation(instance)
        
        # Hide sensitive configuration values
        if instance.is_sensitive:
            representation['value'] = '***HIDDEN***'
        
        return representation


class SystemConfigurationPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for SystemConfiguration - only shows non-sensitive configs.
    """
    
    class Meta:
        model = SystemConfiguration
        fields = ['key', 'name', 'value', 'data_type', 'description', 'category']
    
    def to_representation(self, instance):
        """Only show non-sensitive configurations."""
        if instance.is_sensitive:
            return None  # Skip sensitive configurations
        return super().to_representation(instance)


class ErrorLogSerializer(BaseModelSerializer):
    """
    Serializer for ErrorLog model.
    Allows marking errors as resolved.
    """
    
    user = UserBasicSerializer(read_only=True)
    resolved_by = UserBasicSerializer(read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = ErrorLog
        fields = BaseModelSerializer.Meta.fields + [
            'level', 'message', 'exception_type', 'stack_trace',
            'user', 'tenant_name', 'request_path', 'request_method',
            'ip_address', 'user_agent', 'context',
            'is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes'
        ]
        read_only_fields = [
            'level', 'message', 'exception_type', 'stack_trace',
            'user', 'tenant_name', 'request_path', 'request_method',
            'ip_address', 'user_agent', 'context', 'resolved_at', 'resolved_by'
        ]
    
    def update(self, instance, validated_data):
        """
        Handle marking errors as resolved.
        """
        if 'is_resolved' in validated_data and validated_data['is_resolved']:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                instance.mark_resolved(
                    user=request.user,
                    notes=validated_data.get('resolution_notes', '')
                )
                # Remove from validated_data as it's handled by mark_resolved
                validated_data.pop('is_resolved', None)
                validated_data.pop('resolution_notes', None)
        
        return super().update(instance, validated_data)


class ErrorLogListSerializer(ErrorLogSerializer):
    """
    Simplified serializer for error log lists.
    Excludes heavy fields like stack traces.
    """
    
    class Meta(ErrorLogSerializer.Meta):
        fields = [
            'id', 'created_at', 'level', 'message', 'exception_type',
            'user', 'tenant_name', 'is_resolved', 'resolved_by'
        ]


# Utility Serializers and Mixins

class SoftDeleteActionSerializer(serializers.Serializer):
    """
    Serializer for soft delete actions.
    Used in custom actions for soft deleting/restoring records.
    """
    
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Optional reason for the deletion"
    )


class BulkActionSerializer(serializers.Serializer):
    """
    Base serializer for bulk actions.
    """
    
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of record IDs to perform action on"
    )
    
    def validate_ids(self, value):
        """Ensure all IDs are unique."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate IDs are not allowed")
        return value


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for system health check responses.
    """
    
    status = serializers.ChoiceField(choices=['healthy', 'warning', 'critical'])
    timestamp = serializers.DateTimeField()
    components = serializers.DictField()
    message = serializers.CharField(required=False)


# Mixins for common functionality

class TenantFilterMixin:
    """
    Mixin that ensures serializers only work with objects from the current tenant.
    """
    
    def validate(self, data):
        """Add tenant validation to any serializer."""
        data = super().validate(data)
        
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            # Add tenant validation logic here if needed
            pass
        
        return data


class AuditableMixin:
    """
    Mixin that adds audit logging to serializer actions.
    """
    
    def create(self, validated_data):
        """Log creation in audit trail."""
        instance = super().create(validated_data)
        # Add audit logging logic here
        return instance
    
    def update(self, instance, validated_data):
        """Log updates in audit trail."""
        old_values = {}
        for field in validated_data.keys():
            if hasattr(instance, field):
                old_values[field] = getattr(instance, field)
        
        instance = super().update(instance, validated_data)
        
        # Add audit logging logic here with old_values vs new values
        return instance