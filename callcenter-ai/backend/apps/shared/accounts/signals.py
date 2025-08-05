"""
Accounts App Signals

Handles automated audit logging and system events for user management,
authentication, and tenant membership activities.

Integrates with the core app's audit logging system to maintain
comprehensive audit trails for compliance and security.
"""

import json
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

# Import models
from .models import (
    User, TenantMembership, TenantRole, PlatformRole,
    OTPToken, UserSession, UserInvitation
)

# Core app imports (will be available when core app is implemented)
try:
    from apps.shared.core.models import AuditLog
    from apps.shared.core.utils import get_client_ip  # When utils.py is implemented
except ImportError:
    # Fallback for development phase
    AuditLog = None
    
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def create_audit_log(action, instance, user=None, changes=None, description=None, 
                    ip_address=None, user_agent=None, metadata=None):
    """
    Create an audit log entry.
    
    Args:
        action: String action type (CREATE, UPDATE, DELETE, etc.)
        instance: Model instance being audited
        user: User performing the action
        changes: Dict of field changes for UPDATE actions
        description: Human-readable description
        ip_address: Client IP address
        user_agent: Client user agent string
        metadata: Additional metadata dict
    """
    if not AuditLog:
        return  # Skip during development phase
    
    try:
        # Get tenant from various sources
        tenant = None
        if hasattr(instance, 'tenant'):
            tenant = instance.tenant
        elif hasattr(instance, 'user') and hasattr(instance.user, 'tenant_memberships'):
            # Try to get user's first active tenant
            membership = instance.user.tenant_memberships.filter(is_active=True).first()
            if membership:
                tenant = membership.tenant
        elif isinstance(instance, User) and hasattr(instance, 'tenant_memberships'):
            # For User instances, try to get their first active tenant
            membership = instance.tenant_memberships.filter(is_active=True).first()
            if membership:
                tenant = membership.tenant
        
        AuditLog.objects.create(
            user=user,
            tenant=tenant,
            action=action,
            object_type=ContentType.objects.get_for_model(instance),
            object_id=str(instance.pk),
            object_repr=str(instance),
            description=description or f"{action.title()} {instance._meta.verbose_name}",
            changes=changes or {},
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        # Log error but don't break the application
        print(f"Error creating audit log: {e}")


def get_field_changes(instance, original_instance=None):
    """
    Get changes between original and current instance.
    
    Returns dict of changed fields with old and new values.
    """
    if not original_instance:
        return {}
    
    changes = {}
    
    # Get all fields for the model
    for field in instance._meta.fields:
        field_name = field.name
        
        # Skip fields we don't want to track
        if field_name in ['updated_at', 'last_login']:
            continue
        
        old_value = getattr(original_instance, field_name, None)
        new_value = getattr(instance, field_name, None)
        
        # Skip password fields for security
        if 'password' in field_name.lower():
            if old_value != new_value:
                changes[field_name] = {
                    'old': '[REDACTED]',
                    'new': '[REDACTED]'
                }
            continue
        
        # Convert values to comparable format
        if old_value != new_value:
            # Handle special field types
            if hasattr(field, 'choices') and field.choices:
                # For choice fields, show both value and display name
                old_display = None
                new_display = None
                
                for choice_value, choice_display in field.choices:
                    if choice_value == old_value:
                        old_display = choice_display
                    if choice_value == new_value:
                        new_display = choice_display
                
                changes[field_name] = {
                    'old': old_value,
                    'new': new_value,
                    'old_display': old_display,
                    'new_display': new_display
                }
            else:
                changes[field_name] = {
                    'old': str(old_value) if old_value is not None else None,
                    'new': str(new_value) if new_value is not None else None
                }
    
    return changes


# Store original instances for comparison during updates
_original_instances = {}


# User Model Signals
@receiver(pre_save, sender=User)
def store_original_user(sender, instance, **kwargs):
    """Store original user instance for change tracking."""
    if instance.pk:
        try:
            _original_instances[f"user_{instance.pk}"] = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user creation and updates."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=getattr(instance, '_created_by', None),
            description=f"User account created: {instance.email}",
            metadata={
                'email': instance.email,
                'is_verified': instance.is_verified,
                'is_platform_admin': instance.is_platform_admin
            }
        )
    else:
        # Get original instance for comparison
        original_key = f"user_{instance.pk}"
        original_instance = _original_instances.get(original_key)
        
        if original_instance:
            changes = get_field_changes(instance, original_instance)
            
            if changes:
                # Determine if this is a significant change
                significant_changes = [
                    'email', 'is_active', 'is_verified', 'is_platform_admin',
                    'two_factor_enabled', 'preferred_2fa_method'
                ]
                
                has_significant_change = any(
                    field in changes for field in significant_changes
                )
                
                description = f"User account updated: {instance.email}"
                if 'is_verified' in changes and instance.is_verified:
                    description = f"User email verified: {instance.email}"
                elif 'two_factor_enabled' in changes:
                    if instance.two_factor_enabled:
                        description = f"2FA enabled for user: {instance.email}"
                    else:
                        description = f"2FA disabled for user: {instance.email}"
                
                create_audit_log(
                    action='UPDATE',
                    instance=instance,
                    user=getattr(instance, '_updated_by', None),
                    changes=changes,
                    description=description,
                    metadata={
                        'significant_change': has_significant_change,
                        'changed_fields': list(changes.keys())
                    }
                )
            
            # Clean up stored instance
            del _original_instances[original_key]


@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Log user deletion."""
    create_audit_log(
        action='DELETE',
        instance=instance,
        user=getattr(instance, '_deleted_by', None),
        description=f"User account deleted: {instance.email}",
        metadata={
            'email': instance.email,
            'was_verified': instance.is_verified,
            'was_platform_admin': instance.is_platform_admin
        }
    )


# Authentication Signals
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    create_audit_log(
        action='LOGIN',
        instance=user,
        user=user,
        description=f"User logged in: {user.email}",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata={
            'session_key': request.session.session_key,
            'login_method': 'password'  # Could be extended for other methods
        }
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if user:  # user might be None for anonymous sessions
        create_audit_log(
            action='LOGOUT',
            instance=user,
            user=user,
            description=f"User logged out: {user.email}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'session_key': getattr(request.session, 'session_key', None)
            }
        )


@receiver(user_login_failed)
def log_login_failure(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    email = credentials.get('username', 'unknown')
    
    # Try to get the user for audit purposes
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        pass
    
    create_audit_log(
        action='LOGIN_FAILED',
        instance=user,
        user=None,  # No authenticated user for failed login
        description=f"Failed login attempt for: {email}",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata={
            'email': email,
            'reason': 'invalid_credentials'
        }
    )


# Tenant Membership Signals
@receiver(post_save, sender=TenantMembership)
def log_membership_changes(sender, instance, created, **kwargs):
    """Log tenant membership creation and updates."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=instance.created_by,
            description=f"User {instance.user.email} added to tenant {instance.tenant.name} as {instance.role.display_name}",
            metadata={
                'user_email': instance.user.email,
                'tenant_name': instance.tenant.name,
                'role_name': instance.role.name,
                'invited_by': instance.invited_by.email if instance.invited_by else None
            }
        )
    else:
        # Check if status changed
        if hasattr(instance, '_original_is_active'):
            if instance._original_is_active != instance.is_active:
                action = 'ACTIVATE' if instance.is_active else 'DEACTIVATE'
                description = f"Membership {'activated' if instance.is_active else 'deactivated'} for {instance.user.email} in {instance.tenant.name}"
                
                create_audit_log(
                    action=action,
                    instance=instance,
                    user=instance.updated_by,
                    description=description,
                    metadata={
                        'user_email': instance.user.email,
                        'tenant_name': instance.tenant.name,
                        'role_name': instance.role.name,
                        'status_change': {
                            'from': instance._original_is_active,
                            'to': instance.is_active
                        }
                    }
                )


@receiver(post_delete, sender=TenantMembership)
def log_membership_deletion(sender, instance, **kwargs):
    """Log tenant membership deletion."""
    create_audit_log(
        action='DELETE',
        instance=instance,
        user=getattr(instance, '_deleted_by', None),
        description=f"Membership removed for {instance.user.email} in {instance.tenant.name}",
        metadata={
            'user_email': instance.user.email,
            'tenant_name': instance.tenant.name,
            'role_name': instance.role.name
        }
    )


# Tenant Role Signals
@receiver(post_save, sender=TenantRole)
def log_role_changes(sender, instance, created, **kwargs):
    """Log tenant role creation and updates."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=instance.created_by,
            description=f"Role created: {instance.display_name} in {instance.tenant.name}",
            metadata={
                'role_name': instance.name,
                'tenant_name': instance.tenant.name,
                'is_system_role': instance.is_system_role,
                'permissions': instance.permissions
            }
        )


@receiver(post_delete, sender=TenantRole)
def log_role_deletion(sender, instance, **kwargs):
    """Log tenant role deletion."""
    create_audit_log(
        action='DELETE',
        instance=instance,
        user=getattr(instance, '_deleted_by', None),
        description=f"Role deleted: {instance.display_name} in {instance.tenant.name}",
        metadata={
            'role_name': instance.name,
            'tenant_name': instance.tenant.name,
            'was_system_role': instance.is_system_role
        }
    )


# Platform Role Signals
@receiver(post_save, sender=PlatformRole)
def log_platform_role_changes(sender, instance, created, **kwargs):
    """Log platform role creation and updates."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=instance.granted_by,
            description=f"Platform role granted: {instance.get_role_display()} to {instance.user.email}",
            metadata={
                'user_email': instance.user.email,
                'role': instance.role,
                'granted_by': instance.granted_by.email if instance.granted_by else None,
                'expires_at': instance.expires_at.isoformat() if instance.expires_at else None
            }
        )


@receiver(post_delete, sender=PlatformRole)
def log_platform_role_deletion(sender, instance, **kwargs):
    """Log platform role deletion."""
    create_audit_log(
        action='DELETE',
        instance=instance,
        user=getattr(instance, '_deleted_by', None),
        description=f"Platform role revoked: {instance.get_role_display()} from {instance.user.email}",
        metadata={
            'user_email': instance.user.email,
            'role': instance.role
        }
    )


# OTP Token Signals
@receiver(post_save, sender=OTPToken)
def log_otp_creation(sender, instance, created, **kwargs):
    """Log OTP token creation and usage."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=instance.user,
            description=f"OTP token generated for {instance.user.email} via {instance.delivery_method}",
            ip_address=instance.ip_address,
            user_agent=instance.user_agent,
            metadata={
                'token_type': instance.token_type,
                'delivery_method': instance.delivery_method,
                'recipient': instance.recipient,
                'expires_at': instance.expires_at.isoformat()
            }
        )
    else:
        # Check if token was used
        if instance.is_used and hasattr(instance, '_was_unused'):
            create_audit_log(
                action='USE',
                instance=instance,
                user=instance.user,
                description=f"OTP token used for {instance.user.email} ({instance.get_token_type_display()})",
                metadata={
                    'token_type': instance.token_type,
                    'delivery_method': instance.delivery_method,
                    'attempts': instance.attempts,
                    'used_at': instance.used_at.isoformat() if instance.used_at else None
                }
            )


# User Session Signals
@receiver(post_save, sender=UserSession)
def log_session_changes(sender, instance, created, **kwargs):
    """Log user session creation and status changes."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=instance.user,
            description=f"New session created for {instance.user.email} from {instance.ip_address}",
            ip_address=instance.ip_address,
            metadata={
                'device_type': instance.device_type,
                'browser': instance.browser,
                'operating_system': instance.operating_system,
                'location': instance.location
            }
        )
    else:
        # Check if session was ended
        if not instance.is_active and hasattr(instance, '_was_active'):
            create_audit_log(
                action='END',
                instance=instance,
                user=instance.user,
                description=f"Session ended for {instance.user.email}",
                metadata={
                    'session_duration': str(instance.ended_at - instance.created_at) if instance.ended_at else None,
                    'device_type': instance.device_type,
                    'ip_address': instance.ip_address
                }
            )


# User Invitation Signals
@receiver(post_save, sender=UserInvitation)
def log_invitation_changes(sender, instance, created, **kwargs):
    """Log user invitation creation and acceptance."""
    if created:
        create_audit_log(
            action='CREATE',
            instance=instance,
            user=instance.invited_by,
            description=f"Invitation sent to {instance.email} for {instance.tenant.name} as {instance.role.display_name}",
            metadata={
                'email': instance.email,
                'tenant_name': instance.tenant.name,
                'role_name': instance.role.name,
                'invited_by': instance.invited_by.email,
                'expires_at': instance.expires_at.isoformat()
            }
        )
    else:
        # Check if invitation was accepted
        if instance.is_accepted and hasattr(instance, '_was_not_accepted'):
            create_audit_log(
                action='ACCEPT',
                instance=instance,
                user=instance.accepted_by,
                description=f"Invitation accepted by {instance.email} for {instance.tenant.name}",
                metadata={
                    'email': instance.email,
                    'tenant_name': instance.tenant.name,
                    'role_name': instance.role.name,
                    'accepted_by': instance.accepted_by.email if instance.accepted_by else None,
                    'accepted_at': instance.accepted_at.isoformat() if instance.accepted_at else None
                }
            )


# Custom Signal Handlers for Special Events
def log_password_change(user, request=None):
    """Log password change events."""
    create_audit_log(
        action='PASSWORD_CHANGE',
        instance=user,
        user=user,
        description=f"Password changed for {user.email}",
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
        metadata={'security_event': True}
    )


def log_account_lockout(user, request=None, reason='failed_attempts'):
    """Log account lockout events."""
    create_audit_log(
        action='LOCKOUT',
        instance=user,
        user=None,  # System action
        description=f"Account locked for {user.email} due to {reason}",
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
        metadata={
            'security_event': True,
            'reason': reason,
            'failed_attempts': user.failed_login_attempts,
            'locked_until': user.account_locked_until.isoformat() if user.account_locked_until else None
        }
    )


def log_account_unlock(user, unlocked_by=None, request=None):
    """Log account unlock events."""
    create_audit_log(
        action='UNLOCK',
        instance=user,
        user=unlocked_by,
        description=f"Account unlocked for {user.email}",
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
        metadata={
            'security_event': True,
            'unlocked_by': unlocked_by.email if unlocked_by else 'system'
        }
    )


def log_email_verification(user, request=None):
    """Log email verification events."""
    create_audit_log(
        action='EMAIL_VERIFY',
        instance=user,
        user=user,
        description=f"Email verified for {user.email}",
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
        metadata={
            'verification_event': True,
            'verified_at': user.email_verified_at.isoformat() if user.email_verified_at else None
        }
    )


def log_phone_verification(user, request=None):
    """Log phone verification events."""
    create_audit_log(
        action='PHONE_VERIFY',
        instance=user,
        user=user,
        description=f"Phone verified for {user.email}",
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
        metadata={
            'verification_event': True,
            'phone': user.phone,
            'verified_at': user.phone_verified_at.isoformat() if user.phone_verified_at else None
        }
    )


# Helper function to manually trigger audit logs
def trigger_audit_log(action, instance, user=None, description=None, request=None, **metadata):
    """
    Manually trigger an audit log entry.
    
    Useful for custom business logic that needs audit trails.
    """
    create_audit_log(
        action=action,
        instance=instance,
        user=user,
        description=description,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
        metadata=metadata
    )


"""
Usage Examples:

# In views or business logic:
from .signals import log_password_change, log_account_lockout

# Manual audit logging
log_password_change(user, request)
log_account_lockout(user, request, reason='security_policy')

# Custom business events
trigger_audit_log(
    action='BULK_IMPORT',
    instance=user,
    user=request.user,
    description='Users imported from CSV',
    request=request,
    imported_count=50,
    source='csv_upload'
)
"""