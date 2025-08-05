"""
Tenants App Serializers

Provides REST API serialization for tenant management.
Includes different serializers for different use cases and permission levels.
"""

import re
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.shared.core.serializers import BaseModelSerializer, TimestampedModelSerializer
from .models import Tenant, Domain, TenantInvitation, TenantSettings

User = get_user_model()


class TenantListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing tenants.
    Used in admin interfaces and tenant selection.
    """
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    primary_domain_url = serializers.CharField(source='get_absolute_url', read_only=True)
    is_trial = serializers.BooleanField(read_only=True)
    trial_days_remaining = serializers.IntegerField(read_only=True)
    is_subscription_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'schema_name', 'name', 'subdomain', 'sector', 'subscription_plan',
            'is_active', 'created_at', 'owner_name', 'primary_domain_url',
            'is_trial', 'trial_days_remaining', 'is_subscription_expired'
        ]
        read_only_fields = ['schema_name', 'created_at']


class TenantDetailSerializer(serializers.ModelSerializer):
    """
    Detailed tenant serializer for full CRUD operations.
    Used by platform administrators and tenant owners.
    """
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    primary_domain_url = serializers.CharField(source='get_absolute_url', read_only=True)
    is_trial = serializers.BooleanField(read_only=True)
    trial_days_remaining = serializers.IntegerField(read_only=True)
    is_subscription_expired = serializers.BooleanField(read_only=True)
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            # Core information
            'schema_name', 'name', 'subdomain', 'description', 'sector',
            
            # Contact information
            'primary_contact_email', 'primary_contact_phone',
            
            # Address
            'address', 'city', 'state_province', 'postal_code', 'country',
            
            # Business information
            'registration_number', 'tax_id',
            
            # System information
            'owner', 'owner_name', 'owner_email', 'subscription_plan',
            'is_active', 'primary_domain_url',
            
            # Subscription details
            'subscription_started_at', 'subscription_expires_at', 'trial_ends_at',
            'is_trial', 'trial_days_remaining', 'is_subscription_expired',
            
            # Configuration
            'branding_settings', 'feature_flags', 'integration_settings',
            
            # Limits and quotas
            'max_users', 'max_storage_mb', 'max_monthly_calls', 'max_monthly_sms',
            
            # Security and compliance
            'data_retention_days', 'require_2fa', 'ip_whitelist',
            
            # Metadata
            'notes', 'created_at', 'updated_at', 'usage_stats'
        ]
        read_only_fields = [
            'schema_name', 'created_at', 'updated_at', 'owner_name', 
            'owner_email', 'primary_domain_url', 'is_trial', 
            'trial_days_remaining', 'is_subscription_expired', 'usage_stats'
        ]
    
    def get_usage_stats(self, obj):
        """Get current usage statistics."""
        return obj.get_usage_stats()
    
    def validate_subdomain(self, value):
        """Validate subdomain format and uniqueness."""
        if not value:
            raise serializers.ValidationError("Subdomain is required")
        
        # Convert to lowercase
        value = value.lower()
        
        # Check format
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', value):
            raise serializers.ValidationError(
                "Subdomain must contain only lowercase letters, numbers, and hyphens. "
                "Cannot start or end with hyphen."
            )
        
        # Check length
        if len(value) < 3:
            raise serializers.ValidationError("Subdomain must be at least 3 characters long")
        
        if len(value) > 63:
            raise serializers.ValidationError("Subdomain cannot exceed 63 characters")
        
        # Check for reserved subdomains
        reserved_subdomains = [
            'www', 'api', 'app', 'admin', 'support', 'help', 'docs', 'blog',
            'mail', 'email', 'ftp', 'ssh', 'test', 'staging', 'dev', 'demo',
            'status', 'cdn', 'assets', 'static', 'media', 'uploads'
        ]
        
        if value in reserved_subdomains:
            raise serializers.ValidationError(f"'{value}' is a reserved subdomain")
        
        return value
    
    def validate_primary_contact_email(self, value):
        """Validate primary contact email."""
        if value:
            try:
                validate_email(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Enter a valid email address")
        return value
    
    def validate_max_users(self, value):
        """Validate max users limit."""
        if value < 1:
            raise serializers.ValidationError("Maximum users must be at least 1")
        if value > 10000:
            raise serializers.ValidationError("Maximum users cannot exceed 10,000")
        return value
    
    def validate_max_storage_mb(self, value):
        """Validate storage limit."""
        if value < 100:
            raise serializers.ValidationError("Storage limit must be at least 100 MB")
        return value
    
    def validate_data_retention_days(self, value):
        """Validate data retention period."""
        if value < 30:
            raise serializers.ValidationError("Data retention must be at least 30 days")
        if value > 3650:  # ~10 years
            raise serializers.ValidationError("Data retention cannot exceed 10 years")
        return value
    
    def validate_ip_whitelist(self, value):
        """Validate IP whitelist format."""
        if not isinstance(value, list):
            raise serializers.ValidationError("IP whitelist must be a list")
        
        import ipaddress
        for ip_entry in value:
            try:
                # Try to parse as IP address or network
                ipaddress.ip_network(ip_entry, strict=False)
            except ValueError:
                raise serializers.ValidationError(f"Invalid IP address or network: {ip_entry}")
        
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        # Validate subscription dates
        subscription_started = data.get('subscription_started_at')
        subscription_expires = data.get('subscription_expires_at')
        
        if subscription_started and subscription_expires:
            if subscription_started >= subscription_expires:
                raise serializers.ValidationError(
                    "Subscription start date must be before expiration date"
                )
        
        # Validate trial dates for trial subscriptions
        subscription_plan = data.get('subscription_plan')
        trial_ends_at = data.get('trial_ends_at')
        
        if subscription_plan == 'trial' and not trial_ends_at:
            # Auto-set trial end date
            data['trial_ends_at'] = timezone.now() + timedelta(days=30)
        
        return data


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new tenants.
    Includes only the essential fields needed for tenant creation.
    """
    
    owner_email = serializers.EmailField(write_only=True, help_text="Email of the tenant owner")
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'subdomain', 'description', 'sector',
            'primary_contact_email', 'primary_contact_phone',
            'owner_email', 'subscription_plan'
        ]
    
    def validate_owner_email(self, value):
        """Validate that owner email corresponds to an existing user."""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No user found with this email address. User must be created first."
            )
        return value
    
    def validate_subdomain(self, value):
        """Use the same subdomain validation as TenantDetailSerializer."""
        serializer = TenantDetailSerializer()
        return serializer.validate_subdomain(value)
    
    def create(self, validated_data):
        """Create tenant and set up initial configuration."""
        owner_email = validated_data.pop('owner_email')
        owner = User.objects.get(email=owner_email)
        
        # Set the owner
        validated_data['owner'] = owner
        
        # Create the tenant
        tenant = super().create(validated_data)
        
        # Create default domain
        Domain.objects.create(
            domain=f"{tenant.subdomain}.murima.com",
            tenant=tenant,
            is_primary=True
        )
        
        return tenant


class TenantPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for tenant information.
    Only includes non-sensitive information that can be shown to users.
    """
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'description', 'sector', 'branding_settings'
        ]


class DomainSerializer(serializers.ModelSerializer):
    """
    Serializer for domain management.
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Domain
        fields = [
            'domain', 'tenant', 'tenant_name', 'is_primary', 'is_custom',
            'is_verified', 'verified_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'tenant_name', 'is_verified', 'verified_at', 
            'created_at', 'updated_at'
        ]
    
    def validate_domain(self, value):
        """Validate domain format."""
        if not value:
            raise serializers.ValidationError("Domain is required")
        
        # Basic domain format validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, value):
            raise serializers.ValidationError("Enter a valid domain name")
        
        return value.lower()
    
    def validate(self, data):
        """Cross-field validation."""
        # Only one primary domain per tenant
        if data.get('is_primary', False):
            tenant = data.get('tenant')
            if tenant and self.instance:
                # Updating existing domain
                existing_primary = Domain.objects.filter(
                    tenant=tenant, is_primary=True
                ).exclude(pk=self.instance.pk).exists()
            elif tenant:
                # Creating new domain
                existing_primary = Domain.objects.filter(
                    tenant=tenant, is_primary=True
                ).exists()
            else:
                existing_primary = False
            
            if existing_primary:
                raise serializers.ValidationError(
                    "Only one primary domain is allowed per tenant"
                )
        
        return data


class TenantInvitationSerializer(BaseModelSerializer):
    """
    Serializer for tenant invitations.
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    accepted_by_name = serializers.CharField(source='accepted_by.get_full_name', read_only=True)
    revoked_by_name = serializers.CharField(source='revoked_by.get_full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    acceptance_url = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = TenantInvitation
        fields = BaseModelSerializer.Meta.fields + [
            'tenant', 'tenant_name', 'email', 'role_name', 'invited_by', 'invited_by_name',
            'message', 'token', 'status', 'expires_at', 'accepted_at', 'accepted_by',
            'accepted_by_name', 'sent_at', 'reminder_sent_at', 'revoked_at', 
            'revoked_by', 'revoked_by_name', 'is_expired', 'is_pending', 
            'days_until_expiry', 'acceptance_url'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'token', 'status', 'accepted_at', 'accepted_by', 'sent_at',
            'reminder_sent_at', 'revoked_at', 'revoked_by', 'tenant_name',
            'invited_by_name', 'accepted_by_name', 'revoked_by_name',
            'is_expired', 'is_pending', 'days_until_expiry', 'acceptance_url'
        ]
    
    def get_acceptance_url(self, obj):
        """Get the acceptance URL for the invitation."""
        request = self.context.get('request')
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
            return obj.get_acceptance_url(base_url)
        return obj.get_acceptance_url()
    
    def validate_email(self, value):
        """Validate invitation email."""
        if not value:
            raise serializers.ValidationError("Email is required")
        
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        return value.lower()
    
    def validate_role_name(self, value):
        """Validate role name exists for the tenant."""
        # Note: This validation will be enhanced once accounts app is created
        # to check if the role actually exists for the tenant
        
        valid_roles = ['owner', 'admin', 'supervisor', 'agent', 'viewer']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        return value
    
    def validate_expires_at(self, value):
        """Validate expiration date."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        data = super().validate(data)
        
        # Check for existing pending invitation
        tenant = data.get('tenant')
        email = data.get('email')
        
        if tenant and email and not self.instance:
            existing = TenantInvitation.objects.filter(
                tenant=tenant,
                email=email,
                status='pending'
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    "A pending invitation already exists for this email address"
                )
        
        # Set default expiration if not provided
        if not data.get('expires_at'):
            data['expires_at'] = timezone.now() + timedelta(days=7)
        
        return data


class TenantInvitationAcceptSerializer(serializers.Serializer):
    """
    Serializer for accepting tenant invitations.
    """
    
    token = serializers.UUIDField(required=True)
    
    def validate_token(self, value):
        """Validate invitation token."""
        try:
            invitation = TenantInvitation.objects.get(token=value)
        except TenantInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token")
        
        if not invitation.is_pending:
            raise serializers.ValidationError("Invitation is no longer valid")
        
        if invitation.is_expired:
            raise serializers.ValidationError("Invitation has expired")
        
        return value


class TenantSettingsSerializer(BaseModelSerializer):
    """
    Serializer for tenant settings management.
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    typed_value = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = TenantSettings
        fields = BaseModelSerializer.Meta.fields + [
            'tenant', 'tenant_name', 'category', 'key', 'name', 'description',
            'value', 'setting_type', 'is_sensitive', 'is_system', 'typed_value'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'tenant_name', 'typed_value'
        ]
    
    def get_typed_value(self, obj):
        """Get the typed value, but hide sensitive values."""
        if obj.is_sensitive:
            return "***HIDDEN***"
        return obj.get_typed_value()
    
    def validate_key(self, value):
        """Validate setting key format."""
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError(
                "Key must contain only lowercase letters, numbers, and underscores"
            )
        return value
    
    def validate_category(self, value):
        """Validate category format."""
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError(
                "Category must contain only lowercase letters, numbers, and underscores"
            )
        return value
    
    def validate_value(self, value):
        """Validate value based on setting type."""
        setting_type = self.initial_data.get('setting_type', 'string')
        
        if setting_type == 'integer':
            try:
                int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Value must be a valid integer")
        
        elif setting_type == 'boolean':
            valid_boolean_values = ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']
            if str(value).lower() not in valid_boolean_values:
                raise serializers.ValidationError("Value must be a valid boolean")
        
        elif setting_type == 'json':
            try:
                import json
                json.loads(value)
            except (json.JSONDecodeError, TypeError):
                raise serializers.ValidationError("Value must be valid JSON")
        
        elif setting_type == 'email':
            try:
                validate_email(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Value must be a valid email address")
        
        elif setting_type == 'url':
            from django.core.validators import URLValidator
            validator = URLValidator()
            try:
                validator(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Value must be a valid URL")
        
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        data = super().validate(data)
        
        # Check for unique key per tenant/category
        tenant = data.get('tenant')
        category = data.get('category')
        key = data.get('key')
        
        if tenant and category and key and not self.instance:
            existing = TenantSettings.objects.filter(
                tenant=tenant,
                category=category,
                key=key
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    f"Setting '{key}' already exists in category '{category}'"
                )
        
        return data


class BulkTenantActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions on tenants.
    """
    
    ACTION_CHOICES = [
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
        ('extend_trial', 'Extend Trial'),
        ('change_plan', 'Change Subscription Plan'),
    ]
    
    tenant_ids = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        help_text="List of tenant schema names to perform action on"
    )
    
    action = serializers.ChoiceField(
        choices=ACTION_CHOICES,
        help_text="Action to perform on selected tenants"
    )
    
    # Optional parameters for specific actions
    subscription_plan = serializers.CharField(
        required=False,
        help_text="New subscription plan (required for 'change_plan' action)"
    )
    
    trial_extension_days = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        help_text="Number of days to extend trial (required for 'extend_trial' action)"
    )
    
    reason = serializers.CharField(
        required=False,
        max_length=200,
        help_text="Reason for performing this action"
    )
    
    def validate(self, data):
        """Validate action-specific requirements."""
        action = data.get('action')
        
        if action == 'change_plan' and not data.get('subscription_plan'):
            raise serializers.ValidationError(
                "subscription_plan is required for 'change_plan' action"
            )
        
        if action == 'extend_trial' and not data.get('trial_extension_days'):
            raise serializers.ValidationError(
                "trial_extension_days is required for 'extend_trial' action"
            )
        
        # Validate that all tenant IDs exist
        tenant_ids = data.get('tenant_ids', [])
        existing_tenants = Tenant.objects.filter(schema_name__in=tenant_ids)
        existing_ids = set(existing_tenants.values_list('schema_name', flat=True))
        provided_ids = set(tenant_ids)
        
        missing_ids = provided_ids - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"The following tenant IDs do not exist: {', '.join(missing_ids)}"
            )
        
        return data