"""
Core models for the Murima platform.

This module contains abstract base models and system-wide models that provide
common functionality across all tenant applications.
"""

import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

# from apps.shared.core.middleware import get_current_user
from crum import get_current_user


# Get the User model - this will work with custom user models
# User = get_user_model()


class TimestampedModel(models.Model):
    """
    Abstract base model that provides automatic timestamp tracking.
    
    Automatically sets created_at when the object is first saved,
    and updates updated_at every time the object is saved.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was first created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as the primary key.
    
    Provides a UUID4 primary key which is more secure than
    auto-incrementing integers and allows for better data portability.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )
    
    class Meta:
        abstract = True


from django.db import models
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


class UserTrackingModel(models.Model):
    """
    Abstract base model that tracks who created and last updated a record.
    Integrates with get_current_user for automatic assignment.
    """

    created_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        related_name="created_%(class)s",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        related_name="updated_%(class)s",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def get_valid_user(self, user=None):
        user = user or get_current_user()

        if isinstance(user, SimpleLazyObject):
            user = user._wrapped if hasattr(user, "_wrapped") else None

        if not user or isinstance(user, AnonymousUser):
            return None

        return user

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        user = self.get_valid_user(user)

        if not self.pk and not self.created_by:
            self.created_by = user
        self.updated_by = user

        super().save(*args, **kwargs)


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    
    Instead of actually deleting records from the database, this model
    marks them as deleted by setting is_deleted=True and recording
    when and by whom the deletion occurred.
    """
    is_deleted = models.BooleanField(
        default=False,
        help_text="Whether this record has been soft deleted"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the record was soft deleted"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_records_%(app_label)s_%(class)s',
        help_text="User who soft deleted this record"
    )
    
    def soft_delete(self, user=None):
        """
        Soft delete this object by setting is_deleted=True and recording metadata.
        
        Args:
            user: The user performing the deletion (optional)
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    def restore(self):
        """
        Restore a soft-deleted object by clearing the deletion metadata.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    class Meta:
        abstract = True

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()



class BaseModel(UUIDModel, TimestampedModel, UserTrackingModel, SoftDeleteModel):
    """
    Complete base model that combines all common functionality.
    
    This model provides:
    - UUID primary key
    - Automatic timestamp tracking (created_at, updated_at)
    - User tracking (created_by, updated_by)
    - Soft delete functionality (is_deleted, deleted_at, deleted_by)
    
    Most models in the system should inherit from this base model.
    """
    
    class Meta:
        abstract = True


# System and Audit Models

class AuditLog(TimestampedModel):
    """
    Comprehensive audit logging for all system actions.
    
    This model tracks all significant actions performed in the system,
    providing a complete audit trail for compliance and debugging purposes.
    """
    # Who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who performed the action (null for system actions)"
    )
    
    # Which tenant this action belongs to
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Tenant where this action occurred"
    )
    
    # What action was performed
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('ASSIGN', 'Assign'),
        ('TRANSFER', 'Transfer'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('ARCHIVE', 'Archive'),
        ('RESTORE', 'Restore'),
    ]
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    
    # What object was affected
    object_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
         null=True,
        blank=True,
        help_text="Type of object that was affected"
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID of the object that was affected"
    )
    object_repr = models.CharField(
        max_length=255,
        help_text="String representation of the affected object"
    )
    
    # Details of what changed
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON object containing the changes made"
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address where the action originated"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string from the request"
    )
    
    # Additional context
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the action"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action"
    )
    
    class Meta:
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.object_type.name} by {self.user} at {self.created_at}"


class SystemConfiguration(BaseModel):
    """
    System-wide configuration settings.
    
    This model stores configuration values that can be modified at runtime
    without requiring code changes or deployments.
    """
    # Configuration key (unique identifier)
    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique key identifying this configuration setting"
    )
    
    # Human-readable name
    name = models.CharField(
        max_length=200,
        help_text="Human-readable name for this setting"
    )
    
    # Configuration value (stored as JSON for flexibility)
    value = models.JSONField(
        help_text="The configuration value (can be any JSON-serializable type)"
    )
    
    # Data type hint for validation and UI rendering
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON Object'),
            ('list', 'List'),
        ],
        default='string',
        help_text="Type of data stored in the value field"
    )
    
    # Validation rules
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Validation rules for this configuration value"
    )
    
    # Metadata
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this setting controls"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Category to group related settings"
    )
    is_sensitive = models.BooleanField(
        default=False,
        help_text="Whether this setting contains sensitive information"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this setting is currently active"
    )
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.key})"
    
    def clean(self):
        """
        Validate the configuration value based on data_type and validation_rules.
        """
        super().clean()
        
        # Type validation
        if self.data_type == 'integer' and not isinstance(self.value, int):
            raise ValidationError({'value': 'Value must be an integer'})
        elif self.data_type == 'float' and not isinstance(self.value, (int, float)):
            raise ValidationError({'value': 'Value must be a number'})
        elif self.data_type == 'boolean' and not isinstance(self.value, bool):
            raise ValidationError({'value': 'Value must be a boolean'})
        elif self.data_type == 'string' and not isinstance(self.value, str):
            raise ValidationError({'value': 'Value must be a string'})
        elif self.data_type == 'list' and not isinstance(self.value, list):
            raise ValidationError({'value': 'Value must be a list'})
        
        # Custom validation rules
        if self.validation_rules:
            # Add custom validation logic here based on validation_rules
            pass


class ErrorLog(TimestampedModel):
    """
    System error logging for debugging and monitoring.
    
    This model captures application errors and exceptions to help with
    debugging and system monitoring.
    """
    # Error classification
    level = models.CharField(
        max_length=20,
        choices=[
            ('DEBUG', 'Debug'),
            ('INFO', 'Info'),
            ('WARNING', 'Warning'),
            ('ERROR', 'Error'),
            ('CRITICAL', 'Critical'),
        ],
        default='ERROR',
        help_text="Severity level of the error"
    )
    
    # Error details
    message = models.TextField(
        help_text="Error message or description"
    )
    exception_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of exception that occurred"
    )
    stack_trace = models.TextField(
        blank=True,
        help_text="Full stack trace of the error"
    )
    
    # Context information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who encountered the error"
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Tenant where the error occurred"
    )
    
    # Request information
    request_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL path where the error occurred"
    )
    request_method = models.CharField(
        max_length=10,
        blank=True,
        help_text="HTTP method of the request"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string from the request"
    )
    
    # Additional context
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context data about the error"
    )
    
    # Resolution tracking
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether this error has been resolved"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this error was marked as resolved"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='errors_resolved',
        help_text="User who marked this error as resolved"
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notes about how the error was resolved"
    )
    
    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_resolved', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.level}: {self.message[:100]}..."
    
    def mark_resolved(self, user=None, notes=''):
        """
        Mark this error as resolved.
        
        Args:
            user: The user who resolved the error
            notes: Optional notes about the resolution
        """
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes'])