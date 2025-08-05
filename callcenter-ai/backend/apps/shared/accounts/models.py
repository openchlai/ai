"""
Accounts App Models

This app handles user management, authentication, tenant membership,
and role-based access control for the Murima platform.

Since this is a SHARED_APP, these models are available across all tenants
but are not tenant-specific themselves.
"""

import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import OTPTokenManager, UserManager, TenantMembershipManager, TenantRoleManager, UserSessionManager, UserInvitationManager

from apps.shared.core.models import BaseModel, TimestampedModel, UUIDModel


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Uses email as the primary authentication field instead of username.
    Includes additional fields for user management and audit trails.
    """
    
    # Override email to be required and unique
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
    )
    phone = models.CharField(
        _('phone number'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text=_('Optional. Phone number for SMS notifications.')
    )
    
    # Additional profile fields
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        blank=True,
        help_text=_('Full display name for the user.')
    )
    
    # Platform administration
    is_platform_admin = models.BooleanField(
        _('platform administrator'),
        default=False,
        help_text=_('Designates whether the user can manage the entire platform.')
    )
    
    # Account status and verification
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email address.')
    )
    
    # Account management
    last_password_change = models.DateTimeField(
        _('last password change'),
        auto_now_add=True,
        null=True,
        help_text=_('Date and time of last password change.')
    )
    
    failed_login_attempts = models.PositiveIntegerField(
        _('failed login attempts'),
        default=0,
        help_text=_('Number of consecutive failed login attempts.')
    )
    
    account_locked_until = models.DateTimeField(
        _('account locked until'),
        null=True,
        blank=True,
        help_text=_('Account is locked until this date/time.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    objects = UserManager()  # Custom manager for user operations

    # Use email as username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Required for createsuperuser
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name if available, otherwise email."""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    def is_account_locked(self):
        """Check if account is currently locked."""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock the account for specified duration."""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock the account and reset failed attempts."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])


class TenantMembership(BaseModel):
    """
    Links users to tenants with specific roles.
    
    A user can be a member of multiple tenants with different roles.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_memberships',
        help_text=_('The user who is a member of the tenant.')
    )
    
    tenant = models.ForeignKey(
        'tenants.Tenant',  # Forward reference since tenants app might not be loaded yet
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text=_('The tenant that the user is a member of.')
    )
    
    role = models.ForeignKey(
        'TenantRole',
        on_delete=models.PROTECT,
        related_name='memberships',
        help_text=_('The role assigned to the user in this tenant.')
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this membership is currently active.')
    )
    
    joined_at = models.DateTimeField(
        _('joined at'),
        auto_now_add=True,
        help_text=_('Date and time when the user joined the tenant.')
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenant_memberships_sent',
        help_text=_('The user who invited this member to the tenant.')
    )
    
    deactivated_at = models.DateTimeField(
        _('deactivated at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the membership was deactivated.')
    )
    
    deactivated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deactivated_memberships',
        help_text=_('The user who deactivated this membership.')
    )

    objects = TenantMembershipManager()  # Custom manager for tenant membership operations
    
    class Meta:
        verbose_name = _('Tenant Membership')
        verbose_name_plural = _('Tenant Memberships')
        unique_together = ['user', 'tenant']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['user', 'tenant']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.tenant.name} ({self.role.name})"
    
    def deactivate(self, deactivated_by=None):
        """Deactivate this membership."""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.deactivated_by = deactivated_by
        self.save(update_fields=['is_active', 'deactivated_at', 'deactivated_by'])
    
    def reactivate(self):
        """Reactivate this membership."""
        self.is_active = True
        self.deactivated_at = None
        self.deactivated_by = None
        self.save(update_fields=['is_active', 'deactivated_at', 'deactivated_by'])


class TenantRole(BaseModel):
    """
    Defines roles within a tenant with specific permissions.
    
    Each tenant can define custom roles with different permission sets.
    """
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='roles',
        help_text=_('The tenant this role belongs to.')
    )
    
    name = models.CharField(
        _('name'),
        max_length=50,
        help_text=_('Internal name for the role (e.g., "admin", "supervisor", "agent").')
    )
    
    display_name = models.CharField(
        _('display name'),
        max_length=100,
        help_text=_('Human-readable name for the role.')
    )
    
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description of what this role can do.')
    )
    
    permissions = models.JSONField(
        _('permissions'),
        default=dict,
        help_text=_('JSON object containing permission definitions.')
    )

    asterisk = models.BooleanField(
        _('asterisk'),
        default=False,
        help_text=_('Determines if this role will be given an extension.')
    )
    
    is_system_role = models.BooleanField(
        _('system role'),
        default=False,
        help_text=_('Whether this is a system-defined role that cannot be deleted.')
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this role is currently active.')
    )
    
    sort_order = models.PositiveIntegerField(
        _('sort order'),
        default=0,
        help_text=_('Order for displaying roles in lists.')
    )

    objects = TenantRoleManager()  # Custom manager for tenant role operations
    
    class Meta:
        verbose_name = _('Tenant Role')
        verbose_name_plural = _('Tenant Roles')
        unique_together = ['tenant', 'name']
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['name', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.display_name}"
    
    def has_permission(self, permission_key):
        """Check if this role has a specific permission."""
        return self.permissions.get(permission_key, False)


class PlatformRole(BaseModel):
    """
    Platform-level administrative roles.
    
    These roles grant permissions across the entire platform,
    not just within specific tenants.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='platform_roles',
        help_text=_('The user who has this platform role.')
    )
    
    role = models.CharField(
        _('role'),
        max_length=50,
        choices=[
            ('super_admin', _('Super Administrator')),
            ('admin', _('Administrator')),
            ('support', _('Support Staff')),
            ('billing', _('Billing Manager')),
            ('security', _('Security Officer')),
        ],
        help_text=_('The platform role assigned to the user.')
    )
    
    permissions = models.JSONField(
        _('permissions'),
        default=dict,
        help_text=_('Additional permission overrides for this role.')
    )
    
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_platform_roles',
        help_text=_('The user who granted this platform role.')
    )
    
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('Date and time when this role expires (optional).')
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this platform role is currently active.')
    )
    
    class Meta:
        verbose_name = _('Platform Role')
        verbose_name_plural = _('Platform Roles')
        unique_together = ['user', 'role']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"
    
    def is_expired(self):
        """Check if this role has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class OTPToken(TimestampedModel):
    """
    One-Time Password tokens for authentication and verification.
    
    Used for email verification, phone verification, and password reset.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_tokens',
        help_text=_('The user this OTP token belongs to.')
    )
    
    token = models.CharField(
        _('token'),
        max_length=10,
        help_text=_('The OTP token (usually 6 digits).')
    )
    
    token_type = models.CharField(
        _('token type'),
        max_length=20,
        choices=[
            ('login', _('Login Authentication')),
            ('email_verification', _('Email Verification')),
            ('password_reset', _('Password Reset')),
            ('account_unlock', _('Account Unlock')),
        ],
        help_text=_('The purpose of this OTP token.')
    )
    
    delivery_method = models.CharField(
        _('delivery method'),
        max_length=20,
        choices=[
            ('email', _('Email')),
            ('sms', _('SMS')),
            ('whatsapp', _('WhatsApp')),
        ],
        help_text=_('How the OTP was delivered to the user.')
    )
    
    recipient = models.CharField(
        _('recipient'),
        max_length=255,
        help_text=_('Email address or phone number where OTP was sent.')
    )
    
    expires_at = models.DateTimeField(
        _('expires at'),
        help_text=_('Date and time when this OTP expires.')
    )
    
    is_used = models.BooleanField(
        _('used'),
        default=False,
        help_text=_('Whether this OTP has been used.')
    )
    
    used_at = models.DateTimeField(
        _('used at'),
        null=True,
        blank=True,
        help_text=_('Date and time when this OTP was used.')
    )
    
    attempts = models.PositiveIntegerField(
        _('attempts'),
        default=0,
        help_text=_('Number of verification attempts for this OTP.')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True,
        help_text=_('IP address from which the OTP was requested.')
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        help_text=_('User agent string from the request.')
    )

    objects = OTPTokenManager()
    
    class Meta:
        verbose_name = _('OTP Token')
        verbose_name_plural = _('OTP Tokens')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'token_type', 'is_used']),
            models.Index(fields=['token', 'expires_at']),
            models.Index(fields=['expires_at', 'is_used']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_token_type_display()} - {self.token}"
    
    def is_expired(self):
        """Check if this OTP has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if this OTP is valid for use."""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark this OTP as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])


class UserSession(TimestampedModel):
    """
    User session tracking for security and analytics.
    
    Tracks active user sessions across different devices and locations.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text=_('The user this session belongs to.')
    )
    
    session_key = models.CharField(max_length=255, unique=True)  # Store JWT ID (jti)
    token_type = models.CharField(
        max_length=20, 
        choices=[('session', 'Session'), ('jwt', 'JWT')], 
        default='jwt'
    )
    
    device_type = models.CharField(
        _('device type'),
        max_length=20,
        choices=[
            ('desktop', _('Desktop')),
            ('mobile', _('Mobile')),
            ('tablet', _('Tablet')),
            ('unknown', _('Unknown')),
        ],
        default='unknown',
        help_text=_('Type of device used for this session.')
    )
    
    browser = models.CharField(
        _('browser'),
        max_length=100,
        blank=True,
        help_text=_('Browser name and version.')
    )
    
    operating_system = models.CharField(
        _('operating system'),
        max_length=100,
        blank=True,
        help_text=_('Operating system name and version.')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        help_text=_('IP address used for this session.')
    )
    
    location = models.CharField(
        _('location'),
        max_length=255,
        blank=True,
        help_text=_('Geographical location based on IP address.')
    )
    
    last_activity = models.DateTimeField(
        _('last activity'),
        auto_now=True,
        help_text=_('Date and time of last activity in this session.')
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether this session is currently active.')
    )
    
    ended_at = models.DateTimeField(
        _('ended at'),
        null=True,
        blank=True,
        help_text=_('Date and time when this session ended.')
    )

    objects = UserSessionManager()  # Custom manager for user session operations
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.ip_address}"
    
    def end_session(self):
        """End this session."""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save(update_fields=['is_active', 'ended_at'])


class UserInvitation(BaseModel):
    """
    Invitations for users to join tenants.
    
    Handles the invitation workflow before users become tenant members.
    """
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text=_('The tenant the user is invited to join.')
    )
    
    email = models.EmailField(
        _('email'),
        help_text=_('Email address of the invited user.')
    )
    
    role = models.ForeignKey(
        TenantRole,
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text=_('The role the user will have when they accept.')
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_invitations_sent',
        help_text=_('The user who sent this invitation.')
    )
    
    token = models.UUIDField(
        _('invitation token'),
        default=uuid.uuid4,
        unique=True,
        help_text=_('Unique token for this invitation.')
    )
    
    message = models.TextField(
        _('invitation message'),
        blank=True,
        help_text=_('Personal message included with the invitation.')
    )
    
    expires_at = models.DateTimeField(
        _('expires at'),
        help_text=_('Date and time when this invitation expires.')
    )
    
    is_accepted = models.BooleanField(
        _('accepted'),
        default=False,
        help_text=_('Whether this invitation has been accepted.')
    )
    
    accepted_at = models.DateTimeField(
        _('accepted at'),
        null=True,
        blank=True,
        help_text=_('Date and time when this invitation was accepted.')
    )
    
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_invitations_accepted',
        help_text=_('The user who accepted this invitation.')
    )

    objects = UserInvitationManager()  # Custom manager for user invitation operations
    
    class Meta:
        verbose_name = _('User Invitation')
        verbose_name_plural = _('User Invitations')
        unique_together = ['tenant', 'email']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email', 'expires_at']),
            models.Index(fields=['tenant', 'is_accepted']),
        ]
    
    def __str__(self):
        return f"Invitation: {self.email} to {self.tenant.name}"
    
    def is_expired(self):
        """Check if this invitation has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if this invitation is valid for acceptance."""
        return not self.is_accepted and not self.is_expired()
    
    def accept(self, user):
        """Accept this invitation and create tenant membership."""
        if not self.is_valid():
            raise ValueError("Invitation is not valid for acceptance")
        
        # Create tenant membership
        membership = TenantMembership.objects.create(
            user=user,
            tenant=self.tenant,
            role=self.role,
            invited_by=self.invited_by,
            created_by=user,
            updated_by=user
        )
        
        # Mark invitation as accepted
        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.accepted_by = user
        self.save(update_fields=['is_accepted', 'accepted_at', 'accepted_by'])
        
        return membership