"""
Custom managers and querysets for core models.

Provides common data access patterns and query optimizations for the Murima platform.
"""

from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet with soft delete functionality.
    Provides methods for working with soft-deleted records.
    """
    
    def active(self):
        """Return only non-deleted records."""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """Return only soft-deleted records."""
        return self.filter(is_deleted=True)
    
    def with_deleted(self):
        """Return all records including soft-deleted ones."""
        return self
    
    def soft_delete(self, user=None):
        """Soft delete all records in the queryset."""
        return self.update(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by=user
        )
    
    def restore(self):
        """Restore all soft-deleted records in the queryset."""
        return self.update(
            is_deleted=False,
            deleted_at=None,
            deleted_by=None
        )


class ActiveManager(models.Manager):
    """
    Manager that automatically filters out soft-deleted records.
    Use this as the default manager for models with soft delete functionality.
    """
    
    def get_queryset(self):
        """Return only non-deleted records by default."""
        return SoftDeleteQuerySet(self.model, using=self._db).active()
    
    def with_deleted(self):
        """Get all records including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """Get only soft-deleted records."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class BaseModelManager(ActiveManager):
    """
    Manager for models inheriting from BaseModel.
    Includes user tracking and audit functionality.
    """
    
    def created_by_user(self, user):
        """Get records created by a specific user."""
        return self.filter(created_by=user)
    
    def updated_by_user(self, user):
        """Get records last updated by a specific user."""
        return self.filter(updated_by=user)
    
    def created_between(self, start_date, end_date):
        """Get records created between two dates."""
        return self.filter(created_at__range=[start_date, end_date])
    
    def updated_between(self, start_date, end_date):
        """Get records updated between two dates."""
        return self.filter(updated_at__range=[start_date, end_date])
    
    def recent(self, days=7):
        """Get records created in the last N days."""
        since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=since)


class SystemConfigurationQuerySet(models.QuerySet):
    """
    QuerySet for SystemConfiguration model with common queries.
    """
    
    def active(self):
        """Get only active configurations."""
        return self.filter(is_active=True)
    
    def by_category(self, category):
        """Get configurations by category."""
        return self.filter(category=category)
    
    def sensitive(self):
        """Get only sensitive configurations."""
        return self.filter(is_sensitive=True)
    
    def public(self):
        """Get only non-sensitive configurations."""
        return self.filter(is_sensitive=False)
    
    def by_data_type(self, data_type):
        """Get configurations by data type."""
        return self.filter(data_type=data_type)
    
    def search(self, query):
        """Search configurations by name, key, or description."""
        return self.filter(
            models.Q(name__icontains=query) |
            models.Q(key__icontains=query) |
            models.Q(description__icontains=query)
        )


class SystemConfigurationManager(models.Manager):
    """
    Manager for SystemConfiguration model.
    Provides convenient methods for configuration management.
    """
    
    def get_queryset(self):
        """Use custom queryset."""
        return SystemConfigurationQuerySet(self.model, using=self._db)
    
    def active(self):
        """Get only active configurations."""
        return self.get_queryset().active()
    
    def by_category(self, category):
        """Get configurations by category."""
        return self.get_queryset().by_category(category)
    
    def get_value(self, key, default=None):
        """
        Get configuration value by key.
        Returns the value or default if not found/inactive.
        """
        try:
            config = self.get_queryset().active().get(key=key)
            return config.value
        except self.model.DoesNotExist:
            return default
    
    def set_value(self, key, value, user=None):
        """
        Set configuration value by key.
        Creates new configuration if key doesn't exist.
        """
        config, created = self.get_or_create(
            key=key,
            defaults={
                'name': key.replace('_', ' ').title(),
                'value': value,
                'created_by': user,
                'updated_by': user,
            }
        )
        
        if not created:
            config.value = value
            if user:
                config.updated_by = user
            config.save()
        
        return config
    
    def get_category_configs(self, category):
        """Get all active configurations for a category."""
        return self.get_queryset().active().by_category(category)
    
    def get_public_configs(self):
        """Get all active, non-sensitive configurations."""
        return self.get_queryset().active().public()


class AuditLogQuerySet(models.QuerySet):
    """
    QuerySet for AuditLog model with common audit queries.
    """
    
    def by_user(self, user):
        """Get audit logs for a specific user."""
        return self.filter(user=user)
    
    def by_action(self, action):
        """Get audit logs for a specific action."""
        return self.filter(action=action)
    
    def by_object_type(self, model_class):
        """Get audit logs for a specific model type."""
        content_type = ContentType.objects.get_for_model(model_class)
        return self.filter(object_type=content_type)
    
    def by_object(self, obj):
        """Get audit logs for a specific object instance."""
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return self.filter(object_type=content_type, object_id=str(obj.pk))
    
    def by_tenant(self, tenant):
        """Get audit logs for a specific tenant."""
        return self.filter(tenant=tenant)
    
    def recent(self, hours=24):
        """Get audit logs from the last N hours."""
        since = timezone.now() - timedelta(hours=hours)
        return self.filter(created_at__gte=since)
    
    def by_ip(self, ip_address):
        """Get audit logs from a specific IP address."""
        return self.filter(ip_address=ip_address)
    
    def security_relevant(self):
        """Get security-relevant audit logs."""
        return self.filter(
            action__in=['LOGIN', 'LOGOUT', 'DELETE', 'EXPORT', 'ASSIGN']
        )


class AuditLogManager(models.Manager):
    """
    Manager for AuditLog model.
    Provides methods for audit trail analysis.
    """
    
    def get_queryset(self):
        """Use custom queryset with optimizations."""
        return AuditLogQuerySet(self.model, using=self._db).select_related(
            'user', 'tenant', 'object_type'
        )
    
    def log_action(self, user, tenant, action, obj, description='', 
                   request=None, changes=None, metadata=None):
        """
        Convenience method to create audit log entries.
        """
        content_type = ContentType.objects.get_for_model(obj.__class__)
        
        audit_data = {
            'user': user,
            'tenant': tenant,
            'action': action,
            'object_type': content_type,
            'object_id': str(obj.pk),
            'object_repr': str(obj),
            'description': description,
            'changes': changes or {},
            'metadata': metadata or {},
        }
        
        if request:
            audit_data.update({
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            })
        
        return self.create(**audit_data)
    
    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def user_activity(self, user, days=30):
        """Get user activity summary for the last N days."""
        since = timezone.now() - timedelta(days=days)
        return self.get_queryset().by_user(user).filter(
            created_at__gte=since
        ).values('action').annotate(count=models.Count('action'))
    
    def tenant_activity(self, tenant, days=30):
        """Get tenant activity summary for the last N days."""
        since = timezone.now() - timedelta(days=days)
        return self.get_queryset().by_tenant(tenant).filter(
            created_at__gte=since
        ).values('action', 'user__username').annotate(count=models.Count('id'))


class ErrorLogQuerySet(models.QuerySet):
    """
    QuerySet for ErrorLog model with error analysis methods.
    """
    
    def unresolved(self):
        """Get unresolved errors."""
        return self.filter(is_resolved=False)
    
    def resolved(self):
        """Get resolved errors."""
        return self.filter(is_resolved=True)
    
    def by_level(self, level):
        """Get errors by severity level."""
        return self.filter(level=level)
    
    def critical(self):
        """Get critical errors."""
        return self.filter(level='CRITICAL')
    
    def errors(self):
        """Get error-level and above."""
        return self.filter(level__in=['ERROR', 'CRITICAL'])
    
    def warnings(self):
        """Get warning-level and above."""
        return self.filter(level__in=['WARNING', 'ERROR', 'CRITICAL'])
    
    def by_exception_type(self, exception_type):
        """Get errors by exception type."""
        return self.filter(exception_type=exception_type)
    
    def by_user(self, user):
        """Get errors encountered by a specific user."""
        return self.filter(user=user)
    
    def by_tenant(self, tenant):
        """Get errors for a specific tenant."""
        return self.filter(tenant=tenant)
    
    def recent(self, hours=24):
        """Get errors from the last N hours."""
        since = timezone.now() - timedelta(hours=hours)
        return self.filter(created_at__gte=since)
    
    def frequent_errors(self, days=7, min_count=5):
        """Get frequently occurring errors."""
        since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=since).values(
            'exception_type', 'message'
        ).annotate(
            count=models.Count('id')
        ).filter(count__gte=min_count).order_by('-count')


class ErrorLogManager(models.Manager):
    """
    Manager for ErrorLog model.
    Provides methods for error monitoring and analysis.
    """
    
    def get_queryset(self):
        """Use custom queryset with optimizations."""
        return ErrorLogQuerySet(self.model, using=self._db).select_related(
            'user', 'tenant', 'resolved_by'
        )
    
    def log_error(self, level, message, exception_type='', stack_trace='',
                  user=None, tenant=None, request=None, context=None):
        """
        Convenience method to create error log entries.
        """
        error_data = {
            'level': level,
            'message': message,
            'exception_type': exception_type,
            'stack_trace': stack_trace,
            'user': user,
            'tenant': tenant,
            'context': context or {},
        }
        
        if request:
            error_data.update({
                'request_path': request.path,
                'request_method': request.method,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            })
        
        return self.create(**error_data)
    
    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def error_summary(self, days=7):
        """Get error summary for the last N days."""
        since = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(created_at__gte=since).values(
            'level'
        ).annotate(count=models.Count('id')).order_by('level')
    
    def resolution_stats(self, days=30):
        """Get error resolution statistics."""
        since = timezone.now() - timedelta(days=days)
        total = self.get_queryset().filter(created_at__gte=since).count()
        resolved = self.get_queryset().filter(
            created_at__gte=since, is_resolved=True
        ).count()
        
        return {
            'total': total,
            'resolved': resolved,
            'unresolved': total - resolved,
            'resolution_rate': (resolved / total * 100) if total > 0 else 0
        }


# Utility functions for managers

def get_tenant_from_request(request):
    """
    Extract tenant from request object.
    Helper function for tenant-aware managers.
    """
    if hasattr(request, 'tenant'):
        return request.tenant
    return None


def optimize_queryset_for_list(queryset, select_related_fields=None, prefetch_related_fields=None):
    """
    Apply common optimizations to querysets for list views.
    """
    if select_related_fields:
        queryset = queryset.select_related(*select_related_fields)
    
    if prefetch_related_fields:
        queryset = queryset.prefetch_related(*prefetch_related_fields)
    
    return queryset


class TenantAwareManager(models.Manager):
    """
    Base manager for tenant-aware models.
    Automatically filters by tenant when available.
    """
    
    def __init__(self, tenant_field='tenant'):
        super().__init__()
        self.tenant_field = tenant_field
    
    def for_tenant(self, tenant):
        """Get records for a specific tenant."""
        filter_kwargs = {self.tenant_field: tenant}
        return self.filter(**filter_kwargs)
    
    def get_queryset(self):
        """Base queryset - override in subclasses for tenant filtering."""
        return super().get_queryset()