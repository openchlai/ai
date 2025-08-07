"""
Accounts App Django Admin Configuration

Provides comprehensive admin interfaces for user management,
tenant membership, roles, authentication, and security features.

Follows Django admin best practices with proper filtering,
searching, and bulk actions.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm, CharField, PasswordInput

from .models import (
    User, TenantMembership, TenantRole, PlatformRole,
    OTPToken, UserSession, UserInvitation
)


# Custom Forms
class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for admin."""
    
    class Meta:
        model = User
        fields = ('email', 'username', 'full_name')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for admin."""
    
    class Meta:
        model = User
        fields = '__all__'


# Admin Classes
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced user admin with custom fields and functionality."""
    
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # List display
    list_display = [
        'email', 'full_name', 'is_verified_display', 'is_active', 
        'is_platform_admin', 'tenant_count', 'last_login', 'date_joined'
    ]
    
    list_filter = [
        'is_active', 'is_verified', 'is_platform_admin', 'is_staff', 
        'is_superuser', 'date_joined', 'last_login'
    ]
    
    search_fields = ['email', 'full_name', 'first_name', 'last_name', 'phone']
    
    ordering = ['-date_joined']
    
    readonly_fields = [
        'date_joined', 'last_login', 'last_password_change', 
        'failed_login_attempts', 'account_locked_until',
        'tenant_memberships_display'
    ]
    
    # Fieldsets for detailed view
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('full_name', 'first_name', 'last_name', 'phone')
        }),
        ('Verification Status', {
            'fields': ('is_verified',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_platform_admin',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': (
                'last_password_change', 'failed_login_attempts', 
                'account_locked_until'
            ),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Tenant Memberships', {
            'fields': ('tenant_memberships_display',),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for add user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
        ('Additional Info', {
            'classes': ('wide', 'collapse'),
            'fields': ('phone', 'is_platform_admin'),
        }),
    )
    
    # Custom methods for list display
    def is_verified_display(self, obj):
        """Display verification status with color coding."""
        if obj.is_verified:
            return format_html(
                '<span style="color: green;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Unverified</span>'
        )
    is_verified_display.short_description = 'Verified'
    
    def tenant_count(self, obj):
        """Display count of tenant memberships."""
        count = obj.tenant_memberships.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:accounts_tenantmembership_changelist')
            return format_html(
                '<a href="{}?user__id__exact={}">{} tenant(s)</a>',
                url, obj.id, count
            )
        return '0 tenants'
    tenant_count.short_description = 'Tenants'
    
    def tenant_memberships_display(self, obj):
        """Display tenant memberships in readonly format."""
        memberships = obj.tenant_memberships.filter(is_active=True).select_related(
            'tenant', 'role'
        )
        
        if not memberships:
            return 'No active tenant memberships'
        
        html_parts = []
        for membership in memberships:
            url = reverse(
                'admin:accounts_tenantmembership_change', 
                args=[membership.id]
            )
            html_parts.append(
                f'<a href="{url}">{membership.tenant.name} ({membership.role.display_name})</a>'
            )
        
        return format_html('<br>'.join(html_parts))
    tenant_memberships_display.short_description = 'Active Memberships'
    
    # Actions
    actions = ['verify_users', 'unverify_users', 'unlock_accounts', 'send_verification_otp']
    
    def verify_users(self, request, queryset):
        """Bulk action to verify users."""
        count = queryset.filter(is_verified=False).update(is_verified=True)
        self.message_user(
            request, 
            f'{count} user(s) were successfully verified.'
        )
    verify_users.short_description = 'Verify selected users'
    
    def unverify_users(self, request, queryset):
        """Bulk action to unverify users."""
        count = queryset.filter(is_verified=True).update(is_verified=False)
        self.message_user(
            request, 
            f'{count} user(s) were successfully unverified.'
        )
    unverify_users.short_description = 'Unverify selected users'
    
    def unlock_accounts(self, request, queryset):
        """Bulk action to unlock accounts."""
        count = 0
        for user in queryset:
            if user.is_account_locked():
                user.unlock_account()
                count += 1
        
        self.message_user(
            request, 
            f'{count} account(s) were successfully unlocked.'
        )
    unlock_accounts.short_description = 'Unlock selected accounts'
    
    def send_verification_otp(self, request, queryset):
        """Bulk action to send verification OTP to unverified users."""
        from .models import OTPToken
        
        count = 0
        for user in queryset.filter(is_verified=False):
            try:
                OTPToken.objects.create_email_verification_otp(user)
                count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f'Failed to send OTP to {user.email}: {str(e)}',
                    level='ERROR'
                )
        
        self.message_user(
            request, 
            f'Verification OTP sent to {count} user(s).'
        )
    send_verification_otp.short_description = 'Send verification OTP to selected users'
@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    """Admin for tenant membership management."""
    
    list_display = [
        'user_email', 'tenant_name', 'role_display', 'is_active',
        'joined_at', 'invited_by_email'
    ]
    
    list_filter = [
        'is_active', 'role__name', 'joined_at', 'tenant'
    ]
    
    search_fields = [
        'user__email', 'user__full_name', 'tenant__name', 
        'role__display_name', 'invited_by__email'
    ]
    
    readonly_fields = [
        'joined_at', 'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    
    raw_id_fields = ['user', 'invited_by', 'created_by', 'updated_by']
    
    autocomplete_fields = ['tenant', 'role']
    
    ordering = ['-joined_at']
    
    # Custom display methods
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def tenant_name(self, obj):
        return obj.tenant.name
    tenant_name.short_description = 'Tenant'
    tenant_name.admin_order_field = 'tenant__name'
    
    def role_display(self, obj):
        return obj.role.display_name
    role_display.short_description = 'Role'
    role_display.admin_order_field = 'role__display_name'
    
    def invited_by_email(self, obj):
        return obj.invited_by.email if obj.invited_by else '-'
    invited_by_email.short_description = 'Invited By'
    invited_by_email.admin_order_field = 'invited_by__email'
    
    # Actions
    actions = ['activate_memberships', 'deactivate_memberships']
    
    def activate_memberships(self, request, queryset):
        """Bulk activate memberships."""
        count = queryset.filter(is_active=False).count()
        for membership in queryset.filter(is_active=False):
            membership.reactivate()
        
        self.message_user(
            request,
            f'{count} membership(s) were successfully activated.'
        )
    activate_memberships.short_description = 'Activate selected memberships'
    
    def deactivate_memberships(self, request, queryset):
        """Bulk deactivate memberships."""
        count = queryset.filter(is_active=True).count()
        for membership in queryset.filter(is_active=True):
            membership.deactivate(deactivated_by=request.user)
        
        self.message_user(
            request,
            f'{count} membership(s) were successfully deactivated.'
        )
    deactivate_memberships.short_description = 'Deactivate selected memberships'


@admin.register(TenantRole)
class TenantRoleAdmin(admin.ModelAdmin):
    """Admin for tenant role management."""
    
    list_display = [
        'display_name', 'tenant_name', 'name', 'is_system_role',
        'is_active', 'member_count', 'sort_order'
    ]
    
    list_filter = [
        'is_system_role', 'is_active', 'tenant'
    ]
    
    search_fields = [
        'name', 'display_name', 'description', 'tenant__name'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    
    raw_id_fields = ['created_by', 'updated_by']
    
    autocomplete_fields = ['tenant']
    
    ordering = ['tenant', 'sort_order', 'name']
    
    # Custom display methods
    def tenant_name(self, obj):
        return obj.tenant.name
    tenant_name.short_description = 'Tenant'
    tenant_name.admin_order_field = 'tenant__name'
    
    def member_count(self, obj):
        """Display count of users with this role."""
        count = obj.memberships.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:accounts_tenantmembership_changelist')
            return format_html(
                '<a href="{}?role__id__exact={}">{} member(s)</a>',
                url, obj.id, count
            )
        return '0 members'
    member_count.short_description = 'Members'
    
    # Fieldsets
    fieldsets = (
        (None, {
            'fields': ('tenant', 'name', 'display_name', 'description')
        }),
        ('Configuration', {
            'fields': ('permissions', 'is_system_role', 'is_active', 'sort_order')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlatformRole)
class PlatformRoleAdmin(admin.ModelAdmin):
    """Admin for platform role management."""
    
    list_display = [
        'user_email', 'role', 'is_active', 'expires_at',
        'granted_by_email', 'created_at'
    ]
    
    list_filter = [
        'role', 'is_active', 'expires_at', 'created_at'
    ]
    
    search_fields = [
        'user__email', 'user__full_name', 'granted_by__email'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by'
    ]
    
    raw_id_fields = ['user', 'granted_by', 'created_by', 'updated_by']
    
    ordering = ['-created_at']
    
    # Custom display methods
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def granted_by_email(self, obj):
        return obj.granted_by.email if obj.granted_by else '-'
    granted_by_email.short_description = 'Granted By'
    granted_by_email.admin_order_field = 'granted_by__email'


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    """Admin for OTP token management."""
    
    list_display = [
        'user_email', 'token_type', 'delivery_method', 'token_masked',
        'is_used', 'expires_at', 'attempts', 'created_at'
    ]
    
    list_filter = [
        'token_type', 'delivery_method', 'is_used', 'expires_at', 'created_at'
    ]
    
    search_fields = [
        'user__email', 'recipient', 'token'
    ]
    
    readonly_fields = [
        'token', 'created_at', 'used_at', 'ip_address', 'user_agent'
    ]
    
    raw_id_fields = ['user']
    
    ordering = ['-created_at']
    
    date_hierarchy = 'created_at'
    
    # Custom display methods
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def token_masked(self, obj):
        """Display masked token for security."""
        if len(obj.token) >= 4:
            return f"****{obj.token[-2:]}"
        return "****"
    token_masked.short_description = 'Token'
    
    # Actions
    actions = ['mark_as_used', 'cleanup_expired']
    
    def mark_as_used(self, request, queryset):
        """Mark tokens as used."""
        count = 0
        for token in queryset.filter(is_used=False):
            token.mark_as_used()
            count += 1
        
        self.message_user(
            request,
            f'{count} token(s) marked as used.'
        )
    mark_as_used.short_description = 'Mark selected tokens as used'
    
    def cleanup_expired(self, request, queryset):
        """Delete expired tokens."""
        expired_tokens = queryset.filter(expires_at__lt=timezone.now())
        count = expired_tokens.count()
        expired_tokens.delete()
        
        self.message_user(
            request,
            f'{count} expired token(s) deleted.'
        )
    cleanup_expired.short_description = 'Delete expired tokens'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for user session management."""
    
    list_display = [
        'user_email', 'device_type', 'browser', 'ip_address',
        'is_active', 'last_activity', 'created_at'
    ]
    
    list_filter = [
        'device_type', 'browser', 'is_active', 'last_activity', 'created_at'
    ]
    
    search_fields = [
        'user__email', 'ip_address', 'location', 'session_key'
    ]
    
    readonly_fields = [
        'session_key', 'created_at', 'ended_at', 'operating_system',
        'location', 'last_activity'
    ]
    
    raw_id_fields = ['user']
    
    ordering = ['-last_activity']
    
    date_hierarchy = 'created_at'
    
    # Custom display methods
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    # Actions
    actions = ['end_sessions', 'cleanup_inactive']
    
    def end_sessions(self, request, queryset):
        """End active sessions."""
        count = 0
        for session in queryset.filter(is_active=True):
            session.end_session()
            count += 1
        
        self.message_user(
            request,
            f'{count} session(s) ended.'
        )
    end_sessions.short_description = 'End selected sessions'
    
    def cleanup_inactive(self, request, queryset):
        """Mark old sessions as inactive."""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        
        count = queryset.filter(
            is_active=True,
            last_activity__lt=cutoff_date
        ).count()
        
        queryset.filter(
            is_active=True,
            last_activity__lt=cutoff_date
        ).update(
            is_active=False,
            ended_at=timezone.now()
        )
        
        self.message_user(
            request,
            f'{count} inactive session(s) cleaned up.'
        )
    cleanup_inactive.short_description = 'Cleanup inactive sessions'


@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    """Admin for user invitation management."""
    
    list_display = [
        'email', 'tenant_name', 'role_display', 'invited_by_email',
        'is_accepted', 'expires_at', 'created_at'
    ]
    
    list_filter = [
        'is_accepted', 'expires_at', 'role__name', 'tenant', 'created_at'
    ]
    
    search_fields = [
        'email', 'tenant__name', 'role__display_name', 'invited_by__email'
    ]
    
    readonly_fields = [
        'token', 'accepted_at', 'accepted_by', 'created_at',
        'updated_at', 'created_by', 'updated_by'
    ]
    
    raw_id_fields = [
        'invited_by', 'accepted_by', 'created_by', 'updated_by'
    ]
    
    autocomplete_fields = ['tenant', 'role']
    
    ordering = ['-created_at']
    
    date_hierarchy = 'created_at'
    
    # Custom display methods
    def tenant_name(self, obj):
        return obj.tenant.name
    tenant_name.short_description = 'Tenant'
    tenant_name.admin_order_field = 'tenant__name'
    
    def role_display(self, obj):
        return obj.role.display_name
    role_display.short_description = 'Role'
    role_display.admin_order_field = 'role__display_name'
    
    def invited_by_email(self, obj):
        return obj.invited_by.email
    invited_by_email.short_description = 'Invited By'
    invited_by_email.admin_order_field = 'invited_by__email'
    
    # Actions
    actions = ['resend_invitations', 'cancel_invitations']
    
    def resend_invitations(self, request, queryset):
        """Resend invitation emails."""
        count = 0
        for invitation in queryset.filter(is_accepted=False):
            if invitation.is_valid():
                # Here you would integrate with your email service
                # send_invitation_email(invitation)
                count += 1
        
        self.message_user(
            request,
            f'{count} invitation(s) resent.'
        )
    resend_invitations.short_description = 'Resend selected invitations'
    
    def cancel_invitations(self, request, queryset):
        """Cancel pending invitations."""
        count = 0
        for invitation in queryset.filter(is_accepted=False):
            invitation.soft_delete(user=request.user)
            count += 1
        
        self.message_user(
            request,
            f'{count} invitation(s) cancelled.'
        )
    cancel_invitations.short_description = 'Cancel selected invitations'


# Register additional customizations
admin.site.site_header = 'Murima Platform Administration'
admin.site.site_title = 'Murima Admin'
admin.site.index_title = 'Platform Management'