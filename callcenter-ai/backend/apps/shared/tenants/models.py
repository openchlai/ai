"""
Tenants App Models

This app manages the multi-tenant architecture using django-tenants.
Each tenant represents an organization using the Murima platform.

Key Models:
- Tenant: Core tenant/organization model (inherits from TenantMixin)
- Domain: Domain routing for tenants (inherits from DomainMixin)  
- TenantInvitation: System for inviting users to join tenants
- TenantSettings: Flexible tenant-specific configuration
"""

import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_tenants.models import TenantMixin, DomainMixin

from apps.shared.core.models import BaseModel, TimestampedModel

User = get_user_model()


class TenantManager(models.Manager):
    """Custom manager for Tenant model with common queries."""
    
    def active(self):
        """Return only active tenants."""
        return self.filter(is_active=True)
    
    def by_sector(self, sector):
        """Filter tenants by sector."""
        return self.filter(sector=sector)
    
    def by_subscription_plan(self, plan):
        """Filter tenants by subscription plan."""
        return self.filter(subscription_plan=plan)
    
    def search(self, query):
        """Search tenants by name or subdomain."""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(subdomain__icontains=query)
        )


class Tenant(TenantMixin):
    """
    Core tenant model representing an organization using Murima.
    
    This model inherits from TenantMixin (django-tenants) which provides:
    - schema_name: PostgreSQL schema for tenant isolation
    - auto_create_schema: Automatic schema creation
    - auto_drop_schema: Automatic schema cleanup
    
    Note: Cannot inherit from BaseModel due to TenantMixin requirements,
    so we manually add the necessary fields for consistency.
    """
    
    # Sector choices based on target markets
    SECTOR_CHOICES = [
        ('general', 'General Purpose'),
        ('helpline', 'Child Helplines & Crisis Support'),
        ('healthcare', 'Healthcare Providers'),
        ('customer_service', 'Customer Service Centers'),
        ('government', 'Government Agencies'),
        ('nonprofit', 'Non-Profit Organizations'),
        ('education', 'Educational Institutions'),
    ]
    
    # Subscription plan choices
    SUBSCRIPTION_PLAN_CHOICES = [
        ('trial', 'Trial (30 days)'),
        ('basic', 'Basic Plan'),
        ('professional', 'Professional Plan'),
        ('enterprise', 'Enterprise Plan'),
        ('custom', 'Custom Plan'),
    ]
    
    # Core tenant information
    name = models.CharField(
        max_length=100,
        help_text="Organization name"
    )
    
    subdomain = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-z0-9]([a-z0-9-]*[a-z0-9])?$',
                message='Subdomain must contain only lowercase letters, numbers, and hyphens. Cannot start or end with hyphen.'
            ),
            MinLengthValidator(3, 'Subdomain must be at least 3 characters long.')
        ],
        help_text="Unique subdomain for tenant access (e.g., 'acme' for acme.murima.com)"
    )
    
    # Organization details
    description = models.TextField(
        blank=True,
        help_text="Brief description of the organization"
    )
    
    sector = models.CharField(
        max_length=50,
        choices=SECTOR_CHOICES,
        default='general',
        help_text="Industry sector for specialized features"
    )
    
    # Contact information
    primary_contact_email = models.EmailField(
        help_text="Primary contact email for the organization"
    )
    
    primary_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Primary contact phone number"
    )
    
    # Address information
    address = models.TextField(
        blank=True,
        help_text="Organization's physical address"
    )
    
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Business information
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Business registration or license number"
    )
    
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tax identification number"
    )
    
    # System information
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='owned_tenants',
        help_text="User who owns/administers this tenant"
    )
    
    subscription_plan = models.CharField(
        max_length=50,
        choices=SUBSCRIPTION_PLAN_CHOICES,
        default='trial',
        help_text="Current subscription plan"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this tenant is currently active"
    )
    
    # Timestamps (manually added since we can't inherit from BaseModel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Subscription and billing
    subscription_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the current subscription started"
    )
    
    subscription_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the current subscription expires"
    )
    
    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the trial period ends"
    )
    
    # Configuration and customization
    branding_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Tenant-specific branding configuration (logo, colors, etc.)"
    )
    
    feature_flags = models.JSONField(
        default=dict,
        blank=True,
        help_text="Enabled/disabled features for this tenant"
    )
    
    integration_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Third-party integration configurations"
    )
    
    # Usage limits and quotas
    max_users = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of users allowed for this tenant"
    )
    
    max_storage_mb = models.PositiveIntegerField(
        default=1024,  # 1GB default
        help_text="Maximum storage in megabytes"
    )
    
    max_monthly_calls = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of calls per month (null = unlimited)"
    )
    
    max_monthly_sms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of SMS messages per month (null = unlimited)"
    )
    
    # Compliance and security
    data_retention_days = models.PositiveIntegerField(
        default=2555,  # ~7 years default
        help_text="Number of days to retain data before auto-deletion"
    )
    
    require_2fa = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is required for all users"
    )
    
    ip_whitelist = models.JSONField(
        default=list,
        blank=True,
        help_text="List of allowed IP addresses/ranges (empty = no restriction)"
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this tenant (visible to platform admins only)"
    )
    
    objects = TenantManager()
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ['name']
        indexes = [
            models.Index(fields=['subdomain']),
            models.Index(fields=['sector', 'is_active']),
            models.Index(fields=['subscription_plan', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['subscription_expires_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.subdomain})"
    
    def clean(self):
        """Validate model data."""
        super().clean()
        
        # Ensure subdomain is lowercase
        if self.subdomain:
            self.subdomain = self.subdomain.lower()
        
        # Validate subscription dates
        if self.subscription_started_at and self.subscription_expires_at:
            if self.subscription_started_at >= self.subscription_expires_at:
                raise ValidationError(
                    "Subscription start date must be before expiration date"
                )
        
        # Validate trial dates
        if self.trial_ends_at and self.trial_ends_at <= timezone.now():
            if self.subscription_plan == 'trial':
                raise ValidationError(
                    "Trial period has ended but subscription plan is still 'trial'"
                )
    
    def save(self, *args, **kwargs):
        """Override save to set defaults and validate."""
        # Set trial end date for new trial tenants
        if self.subscription_plan == 'trial' and not self.trial_ends_at:
            self.trial_ends_at = timezone.now() + timedelta(days=30)
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_trial(self):
        """Check if tenant is on trial."""
        return self.subscription_plan == 'trial'
    
    @property
    def trial_days_remaining(self):
        """Get number of trial days remaining."""
        if not self.trial_ends_at:
            return None
        
        remaining = self.trial_ends_at - timezone.now()
        return max(0, remaining.days)
    
    @property
    def is_subscription_expired(self):
        """Check if subscription has expired."""
        if not self.subscription_expires_at:
            return False
        return self.subscription_expires_at <= timezone.now()
    
    @property
    def primary_domain(self):
        """Get the primary domain for this tenant."""
        return self.domains.filter(is_primary=True).first()
    
    def get_absolute_url(self):
        """Get the primary URL for this tenant."""
        primary_domain = self.primary_domain
        if primary_domain:
            return f"https://{primary_domain.domain}"
        return f"https://{self.subdomain}.murima.com"
    
    def is_feature_enabled(self, feature_name, default=False):
        """Check if a feature is enabled for this tenant."""
        return self.feature_flags.get(feature_name, default)
    
    def enable_feature(self, feature_name):
        """Enable a feature for this tenant."""
        self.feature_flags[feature_name] = True
        self.save(update_fields=['feature_flags'])
    
    def disable_feature(self, feature_name):
        """Disable a feature for this tenant."""
        self.feature_flags[feature_name] = False
        self.save(update_fields=['feature_flags'])
    
    def get_usage_stats(self):
        """Get current usage statistics for this tenant."""
        # Note: This would be implemented with actual usage queries
        # when other apps are built
        return {
            'current_users': 0,  # User.objects.filter(tenant_memberships__tenant=self).count()
            'storage_used_mb': 0,  # Calculate from documents
            'monthly_calls': 0,  # Calculate from calls this month
            'monthly_sms': 0,  # Calculate from SMS this month
        }


class Domain(DomainMixin):
    """
    Domain model for tenant routing.
    
    Inherits from DomainMixin (django-tenants) which provides:
    - domain: The domain name
    - tenant: FK to tenant
    - is_primary: Whether this is the primary domain
    """
    
    # Additional domain metadata
    is_custom = models.BooleanField(
        default=False,
        help_text="Whether this is a custom domain (vs. subdomain.murima.com)"
    )
    
    ssl_certificate = models.TextField(
        blank=True,
        help_text="SSL certificate for custom domains"
    )
    
    ssl_private_key = models.TextField(
        blank=True,
        help_text="SSL private key for custom domains"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the domain was verified"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['is_primary', 'tenant']),
        ]
    
    def __str__(self):
        primary_indicator = " (Primary)" if self.is_primary else ""
        return f"{self.domain}{primary_indicator}"
    
    @property
    def is_verified(self):
        """Check if domain is verified."""
        return self.verified_at is not None
    
    def mark_as_verified(self):
        """Mark domain as verified."""
        self.verified_at = timezone.now()
        self.save(update_fields=['verified_at'])


class TenantInvitation(BaseModel):
    """
    Model for inviting users to join a tenant.
    
    When someone is invited to join a tenant, an invitation record is created
    with a unique token. The invitee can use this token to accept the invitation
    and join the tenant with the specified role.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='tenant_invitations',
        help_text="Tenant the user is being invited to join"
    )
    
    email = models.EmailField(
        help_text="Email address of the person being invited"
    )
    
    # Note: This FK will work once accounts app is created
    role_name = models.CharField(
        max_length=50,
        help_text="Name of the role to assign (e.g., 'admin', 'agent', 'viewer')"
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_invitations_sent',
        help_text="User who sent the invitation"
    )
    
    # Invitation details
    message = models.TextField(
        blank=True,
        help_text="Personal message to include with the invitation"
    )
    
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text="Unique token for accepting the invitation"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the invitation"
    )
    
    expires_at = models.DateTimeField(
        help_text="When the invitation expires"
    )
    
    # Acceptance details
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the invitation was accepted"
    )
    
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenant_invitations_accepted',
        help_text="User who accepted the invitation (may differ from invited email)"
    )
    
    # Tracking
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the invitation was sent"
    )
    
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last reminder was sent"
    )
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the invitation was revoked"
    )
    
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_invitations',
        help_text="User who revoked the invitation"
    )
    
    class Meta:
        verbose_name = "Tenant Invitation"
        verbose_name_plural = "Tenant Invitations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'tenant']),
            models.Index(fields=['token']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['tenant', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'email'],
                condition=models.Q(status='pending'),
                name='unique_pending_invitation_per_email_tenant'
            )
        ]
    
    def __str__(self):
        return f"Invitation for {self.email} to join {self.tenant.name}"
    
    def clean(self):
        """Validate invitation data."""
        super().clean()
        
        # Set expiration date if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        
        # Validate expiration date
        if self.expires_at <= timezone.now():
            raise ValidationError("Expiration date must be in the future")
    
    def save(self, *args, **kwargs):
        """Override save to set defaults."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if invitation has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_pending(self):
        """Check if invitation is still pending."""
        return self.status == 'pending' and not self.is_expired
    
    @property
    def days_until_expiry(self):
        """Get number of days until expiry."""
        if self.is_expired:
            return 0
        
        remaining = self.expires_at - timezone.now()
        return remaining.days
    
    def accept(self, user):
        """Accept the invitation."""
        if not self.is_pending:
            raise ValidationError("Invitation is not in pending status")
        
        if self.is_expired:
            raise ValidationError("Invitation has expired")
        
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.accepted_by = user
        self.save()
        
        # Note: Creating the actual TenantMembership would be done
        # in the accounts app when it's available
        
        return self
    
    def revoke(self, user, reason=""):
        """Revoke the invitation."""
        if self.status not in ['pending', 'expired']:
            raise ValidationError("Can only revoke pending or expired invitations")
        
        self.status = 'revoked'
        self.revoked_at = timezone.now()
        self.revoked_by = user
        
        # Store revocation reason in notes if provided
        if reason:
            self.message = f"[REVOKED: {reason}] {self.message}"
        
        self.save()
        return self
    
    def send_reminder(self):
        """Send a reminder email (implementation would be in notifications)."""
        if not self.is_pending:
            return False
        
        self.reminder_sent_at = timezone.now()
        self.save(update_fields=['reminder_sent_at'])
        
        # Note: Actual email sending would be implemented
        # in notifications app
        return True
    
    def get_acceptance_url(self, base_url="https://app.murima.com"):
        """Get the URL for accepting this invitation."""
        return f"{base_url}/invitations/accept/{self.token}/"


class TenantSettings(BaseModel):
    """
    Flexible settings storage for tenant-specific configurations.
    
    This model provides a flexible way to store tenant-specific settings
    that don't warrant their own dedicated fields in the Tenant model.
    """
    
    SETTING_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON Object'),
        ('text', 'Long Text'),
        ('url', 'URL'),
        ('email', 'Email'),
        ('phone', 'Phone Number'),
    ]
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text="Tenant this setting belongs to"
    )
    
    category = models.CharField(
        max_length=50,
        help_text="Category for grouping settings (e.g., 'email', 'phone', 'branding')"
    )
    
    key = models.CharField(
        max_length=100,
        help_text="Setting identifier within the category"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name for the setting"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what this setting controls"
    )
    
    value = models.TextField(
        help_text="Setting value (stored as text, interpreted based on setting_type)"
    )
    
    setting_type = models.CharField(
        max_length=20,
        choices=SETTING_TYPES,
        default='string',
        help_text="Type of value stored in this setting"
    )
    
    is_sensitive = models.BooleanField(
        default=False,
        help_text="Whether this setting contains sensitive data (API keys, passwords, etc.)"
    )
    
    is_system = models.BooleanField(
        default=False,
        help_text="Whether this is a system setting (not user-configurable)"
    )
    
    class Meta:
        verbose_name = "Tenant Setting"
        verbose_name_plural = "Tenant Settings"
        ordering = ['category', 'key']
        indexes = [
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['tenant', 'key']),
            models.Index(fields=['category', 'key']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'category', 'key'],
                name='unique_tenant_setting'
            )
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.category}.{self.key}"
    
    def get_typed_value(self):
        """Get the value converted to its proper type."""
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'integer':
            try:
                return int(self.value)
            except ValueError:
                return 0
        elif self.setting_type == 'json':
            try:
                import json
                return json.loads(self.value)
            except (json.JSONDecodeError, ValueError):
                return {}
        else:
            return self.value
    
    def set_typed_value(self, value):
        """Set the value with proper type conversion."""
        if self.setting_type == 'boolean':
            self.value = str(bool(value)).lower()
        elif self.setting_type == 'integer':
            self.value = str(int(value))
        elif self.setting_type == 'json':
            import json
            self.value = json.dumps(value)
        else:
            self.value = str(value)