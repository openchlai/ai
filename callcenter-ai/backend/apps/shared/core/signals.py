"""
Django signals for automatic audit logging and system monitoring.

This module provides automatic audit trail creation and system event handling
without requiring manual intervention in views or serializers.
"""

import threading
import traceback
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import AuditLog, ErrorLog, BaseModel

User = get_user_model()

# Thread-local storage for request context
_thread_locals = threading.local()


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_thread_locals, 'request', None)


def set_current_request(request):
    """Set the current request in thread-local storage."""
    _thread_locals.request = request


def get_current_user():
    """Get the current user from the request context."""
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None


def get_current_tenant():
    """Get the current tenant from the request context."""
    request = get_current_request()
    if request and hasattr(request, 'tenant'):
        return request.tenant
    return None


def get_client_ip():
    """Get client IP from the current request."""
    request = get_current_request()
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent():
    """Get user agent from the current request."""
    request = get_current_request()
    if request:
        return request.META.get('HTTP_USER_AGENT', '')
    return ''


def should_audit_model(model_class):
    """
    Determine if a model should be audited.
    
    Rules:
    - Audit models that inherit from BaseModel
    - Skip internal Django models unless explicitly configured
    - Skip the AuditLog model itself to avoid recursion
    """
    # Don't audit the audit log itself
    if model_class._meta.label == 'core.AuditLog':
        return False
    
    # Don't audit Django's internal models by default
    django_internal_apps = [
        'auth', 'admin', 'contenttypes', 'sessions', 'messages',
        'staticfiles', 'django_tenants'
    ]
    
    if model_class._meta.app_label in django_internal_apps:
        return False
    
    # Audit models that inherit from BaseModel
    return issubclass(model_class, BaseModel)


def calculate_field_changes(old_instance, new_instance):
    """
    Calculate what fields changed between old and new instance.
    
    Returns a dictionary with field names as keys and
    {'old': old_value, 'new': new_value} as values.
    """
    changes = {}
    
    if not old_instance:
        # This is a new instance - all fields are "new"
        for field in new_instance._meta.fields:
            field_name = field.name
            # Skip auto-generated fields
            if field_name in ['id', 'created_at', 'updated_at']:
                continue
            
            value = getattr(new_instance, field_name, None)
            if value is not None:
                changes[field_name] = {'old': None, 'new': str(value)}
        
        return changes
    
    # Compare old and new values
    for field in new_instance._meta.fields:
        field_name = field.name
        
        # Skip certain fields that change automatically
        if field_name in ['updated_at', 'updated_by']:
            continue
        
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)
        
        # Convert to strings for comparison
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None
        
        if old_str != new_str:
            changes[field_name] = {
                'old': old_str,
                'new': new_str
            }
    
    return changes


@receiver(pre_save)
def store_original_instance(sender, instance, **kwargs):
    """
    Store the original instance before saving for change tracking.
    This runs before the save operation.
    """
    if not should_audit_model(sender):
        return
    
    # Store original instance for comparison
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_instance = original
        except ObjectDoesNotExist:
            instance._original_instance = None
    else:
        instance._original_instance = None


@receiver(post_save)
def create_audit_log_on_save(sender, instance, created, **kwargs):
    """
    Create audit log entry when a model is saved.
    """
    if not should_audit_model(sender):
        return
    
    # Get request context
    user = get_current_user()
    tenant = get_current_tenant()
    
    # Skip if no tenant context (might be a system operation)
    if not tenant:
        return
    
    # Determine action
    action = 'CREATE' if created else 'UPDATE'
    
    # Calculate changes
    changes = {}
    if not created and hasattr(instance, '_original_instance'):
        changes = calculate_field_changes(instance._original_instance, instance)
    elif created:
        changes = calculate_field_changes(None, instance)
    
    # Create audit log entry
    try:
        AuditLog.objects.create(
            user=user,
            tenant=tenant,
            action=action,
            object_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.pk),
            object_repr=str(instance),
            changes=changes,
            description=f"{action.lower().title()} {sender._meta.verbose_name}",
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            metadata={
                'model': sender._meta.label,
                'pk': str(instance.pk),
                'timestamp': timezone.now().isoformat(),
            }
        )
    except Exception as e:
        # Log the error but don't break the main operation
        try:
            ErrorLog.objects.create(
                level='ERROR',
                message=f"Failed to create audit log: {str(e)}",
                exception_type=type(e).__name__,
                stack_trace=traceback.format_exc(),
                user=user,
                tenant=tenant,
                context={
                    'model': sender._meta.label,
                    'instance_pk': str(instance.pk),
                    'action': action,
                }
            )
        except Exception:
            # If we can't even log the error, just pass
            pass


@receiver(post_delete)
def create_audit_log_on_delete(sender, instance, **kwargs):
    """
    Create audit log entry when a model is deleted.
    Note: This is for hard deletes. Soft deletes are handled by post_save.
    """
    if not should_audit_model(sender):
        return
    
    # Get request context
    user = get_current_user()
    tenant = get_current_tenant()
    
    # Skip if no tenant context
    if not tenant:
        return
    
    # Create audit log entry
    try:
        AuditLog.objects.create(
            user=user,
            tenant=tenant,
            action='DELETE',
            object_type=ContentType.objects.get_for_model(sender),
            object_id=str(instance.pk),
            object_repr=str(instance),
            changes={},
            description=f"Delete {sender._meta.verbose_name}",
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            metadata={
                'model': sender._meta.label,
                'pk': str(instance.pk),
                'timestamp': timezone.now().isoformat(),
                'hard_delete': True,
            }
        )
    except Exception as e:
        # Log the error but don't break the main operation
        try:
            ErrorLog.objects.create(
                level='ERROR',
                message=f"Failed to create audit log for delete: {str(e)}",
                exception_type=type(e).__name__,
                stack_trace=traceback.format_exc(),
                user=user,
                tenant=tenant,
                context={
                    'model': sender._meta.label,
                    'instance_pk': str(instance.pk),
                    'action': 'DELETE',
                }
            )
        except Exception:
            pass


# Authentication-related audit logging

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    tenant = getattr(request, 'tenant', None)
    
    try:
        AuditLog.objects.create(
            user=user,
            tenant=tenant,
            action='LOGIN',
            object_type=ContentType.objects.get_for_model(User),
            object_id=str(user.pk),
            object_repr=str(user),
            changes={},
            description=f"User {user.username} logged in",
            ip_address=get_client_ip() or request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'login_method': 'standard',
                'timestamp': timezone.now().isoformat(),
            }
        )
    except Exception as e:
        # Don't break login process, but try to log the error
        try:
            ErrorLog.objects.create(
                level='WARNING',
                message=f"Failed to audit user login: {str(e)}",
                exception_type=type(e).__name__,
                user=user,
                tenant=tenant,
                request_path=request.path,
                request_method=request.method,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        except Exception:
            pass


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if not user:  # Anonymous logout
        return
    
    tenant = getattr(request, 'tenant', None)
    
    try:
        AuditLog.objects.create(
            user=user,
            tenant=tenant,
            action='LOGOUT',
            object_type=ContentType.objects.get_for_model(User),
            object_id=str(user.pk),
            object_repr=str(user),
            changes={},
            description=f"User {user.username} logged out",
            ip_address=get_client_ip() or request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'timestamp': timezone.now().isoformat(),
            }
        )
    except Exception:
        # Don't break logout process
        pass


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts for security monitoring."""
    tenant = getattr(request, 'tenant', None)
    username = credentials.get('username', 'unknown')
    
    try:
        AuditLog.objects.create(
            user=None,  # No user for failed login
            tenant=tenant,
            action='LOGIN',
            object_type=ContentType.objects.get_for_model(User),
            object_id='',
            object_repr=f"Failed login for {username}",
            changes={},
            description=f"Failed login attempt for username: {username}",
            ip_address=get_client_ip() or request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'login_method': 'failed',
                'username_attempted': username,
                'timestamp': timezone.now().isoformat(),
                'security_event': True,
            }
        )
    except Exception:
        # Don't break the login process
        pass


# Custom signal for soft delete auditing
def log_soft_delete(instance, user=None, reason=''):
    """
    Manually log soft delete operations.
    Call this when using the soft_delete() method.
    """
    try:
        tenant = get_current_tenant()
        
        AuditLog.objects.create(
            user=user or get_current_user(),
            tenant=tenant,
            action='DELETE',
            object_type=ContentType.objects.get_for_model(instance.__class__),
            object_id=str(instance.pk),
            object_repr=str(instance),
            changes={'is_deleted': {'old': False, 'new': True}},
            description=f"Soft delete {instance._meta.verbose_name}: {reason}",
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            metadata={
                'model': instance._meta.label,
                'pk': str(instance.pk),
                'soft_delete': True,
                'reason': reason,
                'timestamp': timezone.now().isoformat(),
            }
        )
    except Exception as e:
        # Log the error
        try:
            ErrorLog.objects.create(
                level='ERROR',
                message=f"Failed to audit soft delete: {str(e)}",
                exception_type=type(e).__name__,
                stack_trace=traceback.format_exc(),
                user=user or get_current_user(),
                tenant=get_current_tenant(),
                context={
                    'model': instance._meta.label,
                    'instance_pk': str(instance.pk),
                    'action': 'SOFT_DELETE',
                }
            )
        except Exception:
            pass


# Exception handling signal
def log_exception(exception, request=None, user=None, tenant=None, context=None):
    """
    Manually log exceptions that occur in the application.
    Can be called from exception handlers or middleware.
    """
    try:
        level = 'CRITICAL' if isinstance(exception, (SystemExit, KeyboardInterrupt)) else 'ERROR'
        
        ErrorLog.objects.create(
            level=level,
            message=str(exception),
            exception_type=type(exception).__name__,
            stack_trace=traceback.format_exc(),
            user=user or get_current_user(),
            tenant=tenant or get_current_tenant(),
            request_path=request.path if request else '',
            request_method=request.method if request else '',
            ip_address=get_client_ip() if request else None,
            user_agent=get_user_agent() if request else '',
            context=context or {}
        )
    except Exception:
        # If we can't log the exception, there's not much we can do
        pass


# Utility function to disable auditing temporarily
class DisableAuditing:
    """
    Context manager to temporarily disable audit logging.
    Useful for bulk operations or system maintenance.
    
    Usage:
        with DisableAuditing():
            # Bulk operations that shouldn't be audited
            Model.objects.bulk_create(instances)
    """
    
    def __init__(self):
        self.original_handlers = {}
    
    def __enter__(self):
        # Disconnect signal handlers
        self.original_handlers['post_save'] = post_save.receivers
        self.original_handlers['post_delete'] = post_delete.receivers
        self.original_handlers['pre_save'] = pre_save.receivers
        
        # Clear receivers temporarily
        post_save.receivers = []
        post_delete.receivers = []
        pre_save.receivers = []
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore signal handlers
        post_save.receivers = self.original_handlers['post_save']
        post_delete.receivers = self.original_handlers['post_delete']
        pre_save.receivers = self.original_handlers['pre_save']