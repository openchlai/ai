"""
Django admin configuration for core models.

Provides admin interfaces for system configuration, audit logs, and error tracking.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.contenttypes.models import ContentType
import json

from .models import SystemConfiguration, AuditLog, ErrorLog


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base admin class for models inheriting from BaseModel.
    Provides common functionality for user tracking and timestamps.
    """
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by',
                      'is_deleted', 'deleted_at', 'deleted_by')
    
    def get_readonly_fields(self, request, obj=None):
        """Make user tracking fields readonly, but allow setting on creation."""
        readonly = list(super().get_readonly_fields(request, obj))
        
        if obj:  # Editing existing object
            readonly.extend(['created_by'])
        
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Automatically set user tracking fields."""
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(BaseModelAdmin):
    """
    Admin interface for system configuration management.
    """
    
    list_display = [
        'name', 'key', 'category', 'data_type', 'value_preview', 
        'is_sensitive', 'is_active', 'updated_at'
    ]
    list_filter = [
        'category', 'data_type', 'is_sensitive', 'is_active', 
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'key', 'description', 'category']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('key', 'name', 'description', 'category')
        }),
        ('Configuration Value', {
            'fields': ('value', 'data_type', 'validation_rules'),
            'description': 'The actual configuration value and its type'
        }),
        ('Security & Status', {
            'fields': ('is_sensitive', 'is_active'),
            'description': 'Security and activation settings'
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System-generated audit fields'
        }),
    )
    
    def value_preview(self, obj):
        """Show a preview of the configuration value."""
        if obj.is_sensitive:
            return format_html('<span style="color: red;">***SENSITIVE***</span>')
        
        value_str = str(obj.value)
        if len(value_str) > 50:
            return format_html(
                '<span title="{}">{}</span>',
                value_str,
                value_str[:47] + '...'
            )
        return value_str
    
    value_preview.short_description = 'Value'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'created_by', 'updated_by'
        )
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Customize form fields."""
        if db_field.name == 'value':
            kwargs['help_text'] = 'Enter the configuration value. Will be validated based on data type.'
        elif db_field.name == 'validation_rules':
            kwargs['help_text'] = 'JSON object with validation rules (optional)'
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing audit logs.
    Read-only interface for compliance and debugging.
    """
    
    list_display = [
        'created_at', 'user', 'tenant', 'action', 'object_type', 
        'object_repr', 'ip_address'
    ]
    list_filter = [
        'action', 'object_type', 'created_at', 'tenant'
    ]
    search_fields = [
        'user__username', 'user__email', 'object_repr', 
        'description', 'ip_address'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = [
        'user', 'tenant', 'action', 'object_type', 'object_id', 
        'object_repr', 'changes_formatted', 'description', 'metadata_formatted',
        'ip_address', 'user_agent', 'created_at'
    ]
    
    fieldsets = (
        ('Action Information', {
            'fields': ('created_at', 'user', 'tenant', 'action')
        }),
        ('Object Details', {
            'fields': ('object_type', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('changes_formatted', 'description'),
            'description': 'Details of what was changed'
        }),
        ('Request Context', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Additional Metadata', {
            'fields': ('metadata_formatted',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Audit logs should not be manually created."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs should not be modified."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Audit logs should not be deleted."""
        return False
    
    def changes_formatted(self, obj):
        """Format changes JSON for better readability."""
        if not obj.changes:
            return "No changes recorded"
        
        formatted = json.dumps(obj.changes, indent=2, ensure_ascii=False)
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted)
    
    changes_formatted.short_description = 'Changes'
    
    def metadata_formatted(self, obj):
        """Format metadata JSON for better readability."""
        if not obj.metadata:
            return "No metadata"
        
        formatted = json.dumps(obj.metadata, indent=2, ensure_ascii=False)
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted)
    
    metadata_formatted.short_description = 'Metadata'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'user', 'tenant', 'object_type'
        )


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    """
    Admin interface for error log management.
    Allows viewing and resolving system errors.
    """
    
    list_display = [
        'created_at', 'level', 'message_preview', 'exception_type',
        'user', 'tenant', 'is_resolved', 'resolved_by'
    ]
    list_filter = [
        'level', 'is_resolved', 'exception_type', 'created_at', 'tenant'
    ]
    search_fields = [
        'message', 'exception_type', 'request_path',
        'user__username', 'user__email'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = [
        'level', 'message', 'exception_type', 'stack_trace_formatted',
        'user', 'tenant', 'request_path', 'request_method', 
        'ip_address', 'user_agent', 'context_formatted',
        'created_at', 'resolved_at'
    ]
    
    fieldsets = (
        ('Error Information', {
            'fields': ('created_at', 'level', 'message', 'exception_type')
        }),
        ('Context', {
            'fields': ('user', 'tenant', 'request_path', 'request_method', 'ip_address'),
            'description': 'Context where the error occurred'
        }),
        ('Technical Details', {
            'fields': ('stack_trace_formatted', 'context_formatted'),
            'classes': ('collapse',),
            'description': 'Technical debugging information'
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolution_notes', 'resolved_by', 'resolved_at'),
            'description': 'Error resolution tracking'
        }),
    )
    
    actions = ['mark_resolved', 'mark_unresolved']
    
    def message_preview(self, obj):
        """Show a preview of the error message."""
        message = obj.message
        if len(message) > 100:
            return format_html(
                '<span title="{}">{}</span>',
                message,
                message[:97] + '...'
            )
        return message
    
    message_preview.short_description = 'Message'
    
    def stack_trace_formatted(self, obj):
        """Format stack trace for better readability."""
        if not obj.stack_trace:
            return "No stack trace available"
        
        return format_html(
            '<pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px;">{}</pre>',
            obj.stack_trace
        )
    
    stack_trace_formatted.short_description = 'Stack Trace'
    
    def context_formatted(self, obj):
        """Format context JSON for better readability."""
        if not obj.context:
            return "No context data"
        
        formatted = json.dumps(obj.context, indent=2, ensure_ascii=False)
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted)
    
    context_formatted.short_description = 'Context Data'
    
    def mark_resolved(self, request, queryset):
        """Admin action to mark errors as resolved."""
        count = 0
        for error in queryset:
            if not error.is_resolved:
                error.mark_resolved(user=request.user, notes="Resolved via admin action")
                count += 1
        
        self.message_user(request, f"{count} error(s) marked as resolved.")
    
    mark_resolved.short_description = "Mark selected errors as resolved"
    
    def mark_unresolved(self, request, queryset):
        """Admin action to mark errors as unresolved."""
        count = queryset.filter(is_resolved=True).update(
            is_resolved=False,
            resolved_at=None,
            resolved_by=None,
            resolution_notes=""
        )
        
        self.message_user(request, f"{count} error(s) marked as unresolved.")
    
    mark_unresolved.short_description = "Mark selected errors as unresolved"
    
    def save_model(self, request, obj, form, change):
        """Handle resolution when saving."""
        if change and obj.is_resolved and not obj.resolved_by:
            obj.mark_resolved(user=request.user, notes=obj.resolution_notes)
        else:
            super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'user', 'tenant', 'resolved_by'
        )


# Custom admin site configuration
admin.site.site_header = "Murima Platform Administration"
admin.site.site_title = "Murima Admin"
admin.site.index_title = "Platform Management"

# Register admin classes that provide overview information
class PlatformOverviewAdmin(admin.ModelAdmin):
    """
    Provides platform overview information in admin.
    """
    
    def changelist_view(self, request, extra_context=None):
        """Add overview statistics to the changelist."""
        extra_context = extra_context or {}
        
        # Add platform statistics
        extra_context.update({
            'total_configurations': SystemConfiguration.objects.count(),
            'active_configurations': SystemConfiguration.objects.filter(is_active=True).count(),
            'recent_errors': ErrorLog.objects.filter(is_resolved=False).count(),
            'recent_audit_entries': AuditLog.objects.count(),
        })
        
        return super().changelist_view(request, extra_context=extra_context)