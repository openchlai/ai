"""
Tenants App Django Admin

Provides comprehensive admin interfaces for platform administrators
to manage tenants, domains, invitations, and settings.
"""

from datetime import timedelta
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Tenant, Domain, TenantInvitation, TenantSettings

User = get_user_model()


class DomainInline(admin.TabularInline):
    """Inline admin for domains within tenant admin."""
    model = Domain
    extra = 0
    fields = ['domain', 'is_primary', 'is_custom', 'is_verified', 'verified_at']
    readonly_fields = ['is_verified', 'verified_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant')


class TenantSettingsInline(admin.TabularInline):
    """Inline admin for tenant settings."""
    model = TenantSettings
    extra = 0
    fields = ['category', 'key', 'name', 'value', 'setting_type', 'is_sensitive', 'is_system']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant')


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Comprehensive admin interface for tenant management.
    """
    
    # Display configuration
    list_display = [
        'name', 'subdomain', 'owner_link', 'sector', 'subscription_plan',
        'subscription_status', 'is_active', 'user_count', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'sector', 'subscription_plan', 'require_2fa',
        'created_at', 'subscription_expires_at'
    ]
    
    search_fields = [
        'name', 'subdomain', 'primary_contact_email', 'owner__email',
        'owner__first_name', 'owner__last_name'
    ]
    
    readonly_fields = [
        'schema_name', 'created_at', 'updated_at', 'subscription_status_display',
        'trial_status_display', 'usage_stats_display', 'domains_display'
    ]
    
    # Form layout
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'subdomain', 'description', 'sector', 'owner'
            )
        }),
        ('Contact Information', {
            'fields': (
                'primary_contact_email', 'primary_contact_phone'
            )
        }),
        ('Address', {
            'fields': (
                'address', 'city', 'state_province', 'postal_code', 'country'
            ),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': (
                'registration_number', 'tax_id'
            ),
            'classes': ('collapse',)
        }),
        ('Subscription & Billing', {
            'fields': (
                'subscription_plan', 'subscription_started_at', 
                'subscription_expires_at', 'trial_ends_at',
                'subscription_status_display', 'trial_status_display'
            )
        }),
        ('Limits & Quotas', {
            'fields': (
                'max_users', 'max_storage_mb', 'max_monthly_calls', 'max_monthly_sms'
            ),
            'classes': ('collapse',)
        }),
        ('Security & Compliance', {
            'fields': (
                'data_retention_days', 'require_2fa', 'ip_whitelist'
            ),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': (
                'branding_settings', 'feature_flags', 'integration_settings'
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'schema_name', 'is_active', 'created_at', 'updated_at',
                'usage_stats_display', 'domains_display'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    # Inlines
    inlines = [DomainInline, TenantSettingsInline]
    
    # Ordering
    ordering = ['-created_at']
    
    # Pagination
    list_per_page = 25
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('owner').annotate(
            user_count=Count('memberships', distinct=True, filter=Q(memberships__is_active=True))
        )
    
    def owner_link(self, obj):
        """Display owner as a link to user admin."""
        if obj.owner:
            url = reverse('admin:accounts_user_change', args=[obj.owner.pk])
            return format_html('<a href="{}">{}</a>', url, obj.owner.get_full_name() or obj.owner.email)
        return "-"
    owner_link.short_description = "Owner"
    owner_link.admin_order_field = 'owner__first_name'
    
    def subscription_status(self, obj):
        """Display subscription status with color coding."""
        if obj.is_trial:
            days_remaining = obj.trial_days_remaining
            if days_remaining > 7:
                color = 'green'
            elif days_remaining > 3:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {};">Trial ({} days left)</span>',
                color, days_remaining
            )
        elif obj.is_subscription_expired:
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    subscription_status.short_description = "Status"
    
    def subscription_status_display(self, obj):
        """Detailed subscription status for readonly display."""
        status = []
        
        if obj.is_trial:
            status.append(f"Trial - {obj.trial_days_remaining} days remaining")
        
        if obj.subscription_expires_at:
            if obj.is_subscription_expired:
                status.append("⚠️ Subscription EXPIRED")
            else:
                days_until_expiry = (obj.subscription_expires_at - timezone.now()).days
                status.append(f"Expires in {days_until_expiry} days")
        
        if obj.subscription_plan:
            status.append(f"Plan: {obj.get_subscription_plan_display()}")
        
        return "\n".join(status) if status else "No subscription info"
    subscription_status_display.short_description = "Subscription Status"
    
    def trial_status_display(self, obj):
        """Trial status display."""
        if not obj.is_trial:
            return "Not on trial"
        
        if obj.trial_ends_at:
            remaining = obj.trial_ends_at - timezone.now()
            if remaining.total_seconds() > 0:
                return f"Trial ends in {remaining.days} days ({obj.trial_ends_at.strftime('%Y-%m-%d')})"
            else:
                return "⚠️ Trial has expired"
        
        return "Trial (no end date set)"
    trial_status_display.short_description = "Trial Status"
    
    def usage_stats_display(self, obj):
        """Display current usage statistics."""
        stats = obj.get_usage_stats()
        return format_html(
            "Users: {}/{}<br>"
            "Storage: {} MB / {} MB<br>"
            "Monthly Calls: {}<br>"
            "Monthly SMS: {}",
            stats.get('current_users', 0), obj.max_users,
            stats.get('storage_used_mb', 0), obj.max_storage_mb,
            stats.get('monthly_calls', 0),
            stats.get('monthly_sms', 0)
        )
    usage_stats_display.short_description = "Usage Statistics"
    
    def domains_display(self, obj):
        """Display associated domains."""
        domains = obj.domains.all()
        if not domains:
            return "No domains"
        
        domain_list = []
        for domain in domains:
            status = "✓" if domain.is_verified else "⚠️"
            primary = " (Primary)" if domain.is_primary else ""
            domain_list.append(f"{status} {domain.domain}{primary}")
        
        return format_html("<br>".join(domain_list))
    domains_display.short_description = "Domains"
    
    def user_count(self, obj):
        """Display user count annotation."""
        return getattr(obj, 'user_count', 0)
    user_count.short_description = "Users"
    user_count.admin_order_field = 'user_count'
    
    # Custom actions
    actions = ['activate_tenants', 'deactivate_tenants', 'extend_trial', 'export_tenant_data']
    
    def activate_tenants(self, request, queryset):
        """Bulk activate tenants."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {updated} tenant(s).",
            messages.SUCCESS
        )
    activate_tenants.short_description = "Activate selected tenants"
    
    def deactivate_tenants(self, request, queryset):
        """Bulk deactivate tenants."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {updated} tenant(s).",
            messages.WARNING
        )
    deactivate_tenants.short_description = "Deactivate selected tenants"
    
    def extend_trial(self, request, queryset):
        """Extend trial period for selected tenants."""
        trial_tenants = queryset.filter(subscription_plan='trial')
        extended_count = 0
        
        for tenant in trial_tenants:
            if tenant.trial_ends_at:
                tenant.trial_ends_at += timedelta(days=7)
                tenant.save()
                extended_count += 1
        
        self.message_user(
            request,
            f"Extended trial by 7 days for {extended_count} tenant(s).",
            messages.SUCCESS
        )
    extend_trial.short_description = "Extend trial by 7 days"
    
    def export_tenant_data(self, request, queryset):
        """Export tenant data to CSV."""
        # This would implement CSV export functionality
        # For now, just show a message
        self.message_user(
            request,
            f"Export functionality for {queryset.count()} tenant(s) would be implemented here.",
            messages.INFO
        )
    export_tenant_data.short_description = "Export tenant data"


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin interface for domain management.
    """
    
    list_display = [
        'domain', 'tenant_link', 'is_primary', 'is_custom', 
        'verification_status', 'created_at'
    ]
    
    list_filter = [
        'is_primary', 'is_custom', 'created_at'
    ]
    
    search_fields = [
        'domain', 'tenant__name', 'tenant__subdomain'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'verification_status_display']
    
    fieldsets = (
        ('Domain Information', {
            'fields': ('domain', 'tenant', 'is_primary', 'is_custom')
        }),
        ('SSL Configuration', {
            'fields': ('ssl_certificate', 'ssl_private_key'),
            'classes': ('collapse',),
            'description': 'SSL configuration for custom domains'
        }),
        ('Verification', {
            'fields': ('verified_at', 'verification_status_display'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant')
    
    def tenant_link(self, obj):
        """Display tenant as a link."""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.pk])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return "-"
    tenant_link.short_description = "Tenant"
    tenant_link.admin_order_field = 'tenant__name'
    
    def verification_status(self, obj):
        """Display verification status with icon."""
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        else:
            return format_html('<span style="color: red;">⚠️ Not Verified</span>')
    verification_status.short_description = "Status"
    
    def verification_status_display(self, obj):
        """Detailed verification status."""
        if obj.is_verified:
            return f"✓ Verified on {obj.verified_at.strftime('%Y-%m-%d %H:%M')}"
        else:
            return "⚠️ Not verified - domain ownership needs to be confirmed"
    verification_status_display.short_description = "Verification Status"
    
    actions = ['verify_domains', 'mark_as_primary']
    
    def verify_domains(self, request, queryset):
        """Mark selected domains as verified."""
        unverified = queryset.filter(verified_at__isnull=True)
        for domain in unverified:
            domain.mark_as_verified()
        
        self.message_user(
            request,
            f"Verified {unverified.count()} domain(s).",
            messages.SUCCESS
        )
    verify_domains.short_description = "Mark as verified"
    
    def mark_as_primary(self, request, queryset):
        """Mark domain as primary (only works for single selection)."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one domain to mark as primary.",
                messages.ERROR
            )
            return
        
        domain = queryset.first()
        
        # Remove primary status from other domains for this tenant
        Domain.objects.filter(tenant=domain.tenant, is_primary=True).update(is_primary=False)
        
        # Set this domain as primary
        domain.is_primary = True
        domain.save()
        
        self.message_user(
            request,
            f"Set {domain.domain} as primary domain for {domain.tenant.name}.",
            messages.SUCCESS
        )
    mark_as_primary.short_description = "Set as primary domain"


@admin.register(TenantInvitation)
class TenantInvitationAdmin(admin.ModelAdmin):
    """
    Admin interface for tenant invitation management.
    """
    
    list_display = [
        'email', 'tenant_link', 'role_name', 'status', 'invited_by_link',
        'expiry_status', 'sent_at'
    ]
    
    list_filter = [
        'status', 'role_name', 'sent_at', 'expires_at'
    ]
    
    search_fields = [
        'email', 'tenant__name', 'invited_by__email', 'invited_by__first_name', 'invited_by__last_name'
    ]
    
    readonly_fields = [
        'token', 'sent_at', 'created_at', 'updated_at', 'acceptance_url_display',
        'status_details_display'
    ]
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('tenant', 'email', 'role_name', 'invited_by', 'message')
        }),
        ('Status & Timing', {
            'fields': ('status', 'expires_at', 'status_details_display')
        }),
        ('Acceptance', {
            'fields': ('accepted_at', 'accepted_by'),
            'classes': ('collapse',)
        }),
        ('Revocation', {
            'fields': ('revoked_at', 'revoked_by'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('token', 'acceptance_url_display', 'sent_at', 'reminder_sent_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tenant', 'invited_by', 'accepted_by', 'revoked_by'
        )
    
    def tenant_link(self, obj):
        """Display tenant as a link."""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.pk])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return "-"
    tenant_link.short_description = "Tenant"
    tenant_link.admin_order_field = 'tenant__name'
    
    def invited_by_link(self, obj):
        """Display inviter as a link."""
        if obj.invited_by:
            url = reverse('admin:accounts_user_change', args=[obj.invited_by.pk])
            return format_html('<a href="{}">{}</a>', url, obj.invited_by.get_full_name() or obj.invited_by.email)
        return "-"
    invited_by_link.short_description = "Invited By"
    invited_by_link.admin_order_field = 'invited_by__first_name'
    
    def expiry_status(self, obj):
        """Display expiry status with color coding."""
        if obj.status != 'pending':
            return "-"
        
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        
        days_remaining = obj.days_until_expiry
        if days_remaining <= 1:
            color = 'red'
        elif days_remaining <= 3:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {};">{} days left</span>',
            color, days_remaining
        )
    expiry_status.short_description = "Expiry"
    
    def acceptance_url_display(self, obj):
        """Display the acceptance URL."""
        return obj.get_acceptance_url()
    acceptance_url_display.short_description = "Acceptance URL"
    
    def status_details_display(self, obj):
        """Display detailed status information."""
        details = []
        
        if obj.status == 'pending':
            if obj.is_expired:
                details.append("⚠️ EXPIRED")
            else:
                details.append(f"✓ Active - expires in {obj.days_until_expiry} days")
        
        elif obj.status == 'accepted':
            details.append(f"✓ Accepted on {obj.accepted_at.strftime('%Y-%m-%d %H:%M')}")
            if obj.accepted_by:
                details.append(f"Accepted by: {obj.accepted_by.get_full_name() or obj.accepted_by.email}")
        
        elif obj.status == 'revoked':
            details.append(f"🚫 Revoked on {obj.revoked_at.strftime('%Y-%m-%d %H:%M')}")
            if obj.revoked_by:
                details.append(f"Revoked by: {obj.revoked_by.get_full_name() or obj.revoked_by.email}")
        
        if obj.reminder_sent_at:
            details.append(f"Last reminder: {obj.reminder_sent_at.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(details) if details else "No additional details"
    status_details_display.short_description = "Status Details"
    
    actions = ['send_reminders', 'revoke_invitations', 'extend_expiry']
    
    def send_reminders(self, request, queryset):
        """Send reminder emails for pending invitations."""
        pending_invitations = queryset.filter(status='pending', expires_at__gt=timezone.now())
        
        reminder_count = 0
        for invitation in pending_invitations:
            if invitation.send_reminder():
                reminder_count += 1
        
        self.message_user(
            request,
            f"Sent reminders for {reminder_count} invitation(s).",
            messages.SUCCESS
        )
    send_reminders.short_description = "Send reminder emails"
    
    def revoke_invitations(self, request, queryset):
        """Revoke selected invitations."""
        pending_invitations = queryset.filter(status='pending')
        
        revoked_count = 0
        for invitation in pending_invitations:
            try:
                invitation.revoke(user=request.user, reason="Revoked by admin")
                revoked_count += 1
            except ValidationError:
                pass
        
        self.message_user(
            request,
            f"Revoked {revoked_count} invitation(s).",
            messages.WARNING
        )
    revoke_invitations.short_description = "Revoke invitations"
    
    def extend_expiry(self, request, queryset):
        """Extend expiry for pending invitations."""
        pending_invitations = queryset.filter(status='pending')
        
        extended_count = 0
        for invitation in pending_invitations:
            invitation.expires_at += timedelta(days=7)
            invitation.save()
            extended_count += 1
        
        self.message_user(
            request,
            f"Extended expiry by 7 days for {extended_count} invitation(s).",
            messages.SUCCESS
        )
    extend_expiry.short_description = "Extend expiry by 7 days"


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for tenant settings management.
    """
    
    list_display = [
        'tenant_link', 'category', 'key', 'name', 'setting_type',
        'is_sensitive', 'is_system', 'created_at'
    ]
    
    list_filter = [
        'setting_type', 'is_sensitive', 'is_system', 'category', 'created_at'
    ]
    
    search_fields = [
        'tenant__name', 'category', 'key', 'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'typed_value_display']
    
    fieldsets = (
        ('Setting Information', {
            'fields': ('tenant', 'category', 'key', 'name', 'description')
        }),
        ('Value & Type', {
            'fields': ('value', 'setting_type', 'typed_value_display')
        }),
        ('Flags', {
            'fields': ('is_sensitive', 'is_system')
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'created_by', 'updated_by')
    
    def tenant_link(self, obj):
        """Display tenant as a link."""
        if obj.tenant:
            url = reverse('admin:tenants_tenant_change', args=[obj.tenant.pk])
            return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
        return "-"
    tenant_link.short_description = "Tenant"
    tenant_link.admin_order_field = 'tenant__name'
    
    def typed_value_display(self, obj):
        """Display the typed value (hide sensitive values)."""
        if obj.is_sensitive:
            return "***HIDDEN*** (Sensitive data)"
        
        typed_value = obj.get_typed_value()
        
        if obj.setting_type == 'json':
            import json
            return json.dumps(typed_value, indent=2)
        
        return str(typed_value)
    typed_value_display.short_description = "Typed Value"
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on whether this is sensitive data."""
        form = super().get_form(request, obj, **kwargs)
        
        # For sensitive settings, show a warning
        if obj and obj.is_sensitive:
            form.base_fields['value'].help_text = (
                "⚠️ This is sensitive data. Be careful when editing."
            )
        
        return form
    
    actions = ['mark_as_sensitive', 'mark_as_non_sensitive', 'export_settings']
    
    def mark_as_sensitive(self, request, queryset):
        """Mark settings as sensitive."""
        updated = queryset.update(is_sensitive=True)
        self.message_user(
            request,
            f"Marked {updated} setting(s) as sensitive.",
            messages.SUCCESS
        )
    mark_as_sensitive.short_description = "Mark as sensitive"
    
    def mark_as_non_sensitive(self, request, queryset):
        """Mark settings as non-sensitive."""
        updated = queryset.update(is_sensitive=False)
        self.message_user(
            request,
            f"Marked {updated} setting(s) as non-sensitive.",
            messages.SUCCESS
        )
    mark_as_non_sensitive.short_description = "Mark as non-sensitive"
    
    def export_settings(self, request, queryset):
        """Export settings (would implement CSV export)."""
        self.message_user(
            request,
            f"Export functionality for {queryset.count()} setting(s) would be implemented here.",
            messages.INFO
        )
    export_settings.short_description = "Export settings"


# Register any additional admin customizations
admin.site.site_header = "Murima Platform Administration"
admin.site.site_title = "Murima Admin"
admin.site.index_title = "Platform Management"