"""
Accounts App Serializers

Provides API serializers for simplified authentication with password OR OTP login,
user management, tenant membership, and related functionality.
"""

import re
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.shared.core.serializers import BaseModelSerializer, TimestampedModelSerializer

from .models import (
    User, TenantMembership, TenantRole, PlatformRole,
    OTPToken, UserSession, UserInvitation
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with optional password.
    Users can register with password OR use OTP-only authentication.
    """
    
    password = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Password for login (optional - you can use OTP-only authentication).')
    )
    password_confirm = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Confirm your password (required if password is provided).')
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'full_name',
            'first_name', 'last_name', 'phone'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email is unique and properly formatted."""
        if User.objects.filter(email=value).exists():
            raise ValidationError(_('A user with this email already exists.'))
        return value
    
    def validate_phone(self, value):
        """Validate phone number format if provided."""
        if value:
            # Remove all non-digit characters for validation
            digits_only = re.sub(r'\D', '', value)
            if len(digits_only) < 9 or len(digits_only) > 15:
                raise ValidationError(
                    _('Phone number must be between 9 and 15 digits.')
                )
        return value
    
    def validate_password(self, value):
        """Validate password meets Django's password requirements."""
        if value:  # Only validate if password is provided
            try:
                validate_password(value)
            except DjangoValidationError as e:
                raise ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        """Cross-field validation for optional password."""
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # If either password field is provided, both must be provided and match
        if password or password_confirm:
            if not password:
                raise ValidationError({
                    'password': _('Password is required when password_confirm is provided.')
                })
            if not password_confirm:
                raise ValidationError({
                    'password_confirm': _('Password confirmation is required when password is provided.')
                })
            if password != password_confirm:
                raise ValidationError({
                    'password_confirm': _('Password confirmation does not match.')
                })
        
        return data
    
    def create(self, validated_data):
        """Create a new user with optional password."""
        # Remove password fields from validated_data
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        # Set username same as email for Django compatibility
        validated_data['username'] = validated_data['email']
        
        if password:
            # Create user with password
            user = User.objects.create_user(
                password=password,
                **validated_data
            )
        else:
            # Create user without password (OTP-only authentication)
            user = User.objects.create_user(**validated_data)
            user.set_unusable_password()  # Django method for passwordless users
            user.save()
        
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile management.
    """
    
    tenant_memberships = serializers.SerializerMethodField()
    platform_roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'first_name', 'last_name',
            'phone', 'is_verified', 'last_login', 'date_joined', 
            'tenant_memberships', 'platform_roles'
        ]
        read_only_fields = [
            'id', 'email', 'is_verified', 'last_login', 'date_joined'
        ]
    
    def get_tenant_memberships(self, obj):
        """Return active tenant memberships."""
        memberships = obj.tenant_memberships.filter(is_active=True).select_related(
            'tenant', 'role'
        )
        return [
            {
                'tenant_id': membership.tenant.id,
                'tenant_name': membership.tenant.name,
                'role_name': membership.role.name,
                'role_display_name': membership.role.display_name,
                'joined_at': membership.joined_at
            }
            for membership in memberships
        ]
    
    def get_platform_roles(self, obj):
        """Return active platform roles."""
        roles = obj.platform_roles.filter(is_active=True)
        return [
            {
                'role': role.role,
                'role_display': role.get_role_display(),
                'expires_at': role.expires_at
            }
            for role in roles
            if not role.is_expired()
        ]
    
    def validate_phone(self, value):
        """Validate phone number format if provided."""
        if value:
            digits_only = re.sub(r'\D', '', value)
            if len(digits_only) < 9 or len(digits_only) > 15:
                raise ValidationError(
                    _('Phone number must be between 9 and 15 digits.')
                )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change with current password verification.
    """
    
    current_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Your current password.')
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Your new password.')
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Confirm your new password.')
    )
    
    def validate_current_password(self, value):
        """Validate current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError(_('Current password is incorrect.'))
        return value
    
    def validate_new_password(self, value):
        """Validate new password meets requirements."""
        try:
            validate_password(value, user=self.context['request'].user)
        except DjangoValidationError as e:
            raise ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        if data['new_password'] != data['new_password_confirm']:
            raise ValidationError({
                'new_password_confirm': _('Password confirmation does not match.')
            })
        
        if data['current_password'] == data['new_password']:
            raise ValidationError({
                'new_password': _('New password must be different from current password.')
            })
        
        return data
    
    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.last_password_change = timezone.now()
        user.save(update_fields=['password', 'last_password_change'])
        return user


# Authentication Serializers
class LoginSerializer(serializers.Serializer):
    """
    Serializer for email/password authentication OR OTP login initiation.
    """
    
    email = serializers.EmailField(
        help_text=_('Your email address.')
    )
    password = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'},
        help_text=_('Your password (required for password login).')
    )
    login_method = serializers.ChoiceField(
        choices=[('password', 'Password'), ('otp', 'OTP')],
        default='password',
        help_text=_('Choose login method: password or OTP.')
    )
    delivery_method = serializers.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp')],
        default='email',
        required=False,
        help_text=_('OTP delivery method (only for OTP login).')
    )
    remember_me = serializers.BooleanField(
        default=False,
        help_text=_('Keep me logged in for 30 days.')
    )
    
    def validate_email(self, value):
        """Basic email format validation - don't check existence here."""
        # Just validate email format, don't check if user exists
        # User existence will be checked in the main validate() method
        return value.lower().strip()
    
    def validate(self, data):
        """Authenticate user with email and password OR initiate OTP login."""
        email = data.get('email')
        password = data.get('password')
        login_method = data.get('login_method', 'password')
        
        if not email:
            raise ValidationError(_('Email is required.'))
        
        # Check if user exists - this is the main user existence check
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For security, don't reveal whether email exists or not
            # Use a generic error message for both password and OTP methods
            raise ValidationError(_('Invalid login credentials. Please check your email address.'))
        
        # Check if account is locked
        if user.is_account_locked():
            raise ValidationError(_('Account is temporarily locked. Please try again later.'))
        
        # Check if account is active
        if not user.is_active:
            raise ValidationError(_('Account is disabled. Please contact support.'))
        
        if login_method == 'password':
            # Password-based authentication
            if not password:
                raise ValidationError(_('Password is required for password login.'))
            
            # Authenticate user
            authenticated_user = authenticate(
                request=self.context.get('request'), 
                username=email, 
                password=password
            )
            
            if not authenticated_user:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.lock_account(duration_minutes=30)
                    user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
                    raise ValidationError(_('Too many failed attempts. Account locked for 30 minutes.'))
                else:
                    user.save(update_fields=['failed_login_attempts'])
                
                raise ValidationError(_('Invalid email or password.'))
            
            # Reset failed login attempts on successful authentication
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.save(update_fields=['failed_login_attempts'])
            
            data['user'] = authenticated_user
            data['requires_otp'] = False
            
        elif login_method == 'otp':
            # OTP-based authentication - validate delivery method
            delivery_method = data.get('delivery_method', 'email')
            
            # Validate delivery method and user's contact info
            if delivery_method == 'email':
                # Email is always available since we found the user by email
                pass
            elif delivery_method in ['sms', 'whatsapp']:
                if not user.phone:
                    raise ValidationError(_('Phone number not available for SMS/WhatsApp delivery. Please use email or contact support.'))
            else:
                raise ValidationError(_('Invalid delivery method. Please choose email, SMS, or WhatsApp.'))
            
            # OTP-based authentication - just validate user exists and is active
            # The actual OTP will be generated and sent in the view
            data['user'] = user
            data['requires_otp'] = True
        
        else:
            raise ValidationError(_('Invalid login method. Use "password" or "otp".'))
        
        return data

class OTPRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting OTP tokens for various purposes.
    """
    
    email = serializers.EmailField(
        help_text=_('Email address of the user.')
    )
    purpose = serializers.ChoiceField(
        choices=[('login', 'Login'), ('password_reset', 'Password Reset')],
        help_text=_('Purpose of the OTP request.')
    )
    delivery_method = serializers.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp')],
        default='email',
        help_text=_('How to deliver the OTP token.')
    )
    
    def validate_email(self, value):
        """Validate email exists in system."""
        try:
            user = User.objects.get(email=value, is_active=True)
            self.user = user
        except User.DoesNotExist:
            # Don't reveal whether email exists or not for security
            pass
        return value
    
    def validate(self, data):
        """Validate OTP request parameters."""
        delivery_method = data['delivery_method']
        
        # If we have a user, validate delivery method
        if hasattr(self, 'user'):
            user = self.user
            
            if delivery_method in ['sms', 'whatsapp'] and not user.phone:
                raise ValidationError({
                    'delivery_method': _('User has no phone number for SMS/WhatsApp delivery.')
                })
        
        return data


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP token verification.
    """
    
    user_id = serializers.UUIDField(
        help_text=_('User ID for OTP verification.')
    )
    token = serializers.CharField(
        min_length=6,
        max_length=6,
        help_text=_('6-digit OTP token.')
    )
    token_type = serializers.ChoiceField(
        choices=[
            ('login', 'Login'),
            ('email_verification', 'Email Verification'),
            ('password_reset', 'Password Reset'),
            ('account_unlock', 'Account Unlock')
        ],
        help_text=_('Type of OTP token being verified.')
    )
    
    def validate_token(self, value):
        """Validate token is numeric and correct length."""
        if not value.isdigit():
            raise ValidationError(_('OTP token must be numeric.'))
        return value
    
    def validate_user_id(self, value):
        """Validate user exists."""
        try:
            user = User.objects.get(id=value)
            self.user = user
        except User.DoesNotExist:
            raise ValidationError(_('Invalid user ID.'))
        return value
    
    def validate(self, data):
        """Verify OTP token."""
        if not hasattr(self, 'user'):
            raise ValidationError(_('Invalid user ID.'))
        
        user = self.user
        token = data['token']
        token_type = data['token_type']
        
        # Verify the OTP
        is_valid, otp_token = OTPToken.objects.verify_otp(user, token, token_type)
        
        if not is_valid:
            if otp_token and otp_token.attempts >= 3:
                raise ValidationError(_('Too many failed attempts. Please request a new OTP.'))
            raise ValidationError(_('Invalid or expired OTP token.'))
        
        data['otp_token'] = otp_token
        data['user'] = user
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    
    email = serializers.EmailField(
        help_text=_('Email address associated with your account.')
    )
    delivery_method = serializers.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp')],
        default='email',
        help_text=_('How to deliver the reset OTP.')
    )
    
    def validate_email(self, value):
        """Validate email exists in system."""
        try:
            user = User.objects.get(email=value, is_active=True)
            self.user = user
        except User.DoesNotExist:
            # Don't reveal whether email exists or not for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation with OTP.
    """
    
    email = serializers.EmailField()
    otp_token = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate new password meets requirements."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        """Validate password reset request."""
        email = data['email']
        token = data['otp_token']
        
        # Check if user exists
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise ValidationError(_('Invalid email address.'))
        
        # Verify OTP token
        is_valid, otp_token = OTPToken.objects.verify_otp(
            user, token, 'password_reset'
        )
        
        if not is_valid:
            raise ValidationError(_('Invalid or expired OTP token.'))
        
        # Validate password confirmation
        if data['new_password'] != data['new_password_confirm']:
            raise ValidationError({
                'new_password_confirm': _('Password confirmation does not match.')
            })
        
        data['user'] = user
        data['otp_token'] = otp_token
        return data


# Tenant Management Serializers
class TenantMembershipSerializer(BaseModelSerializer):
    """
    Serializer for tenant membership management.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_display_name = serializers.CharField(source='role.display_name', read_only=True)
    invited_by_email = serializers.CharField(source='invited_by.email', read_only=True)
    
    class Meta(BaseModelSerializer.Meta):
        model = TenantMembership
        fields = BaseModelSerializer.Meta.fields + [
            'user', 'user_email', 'user_full_name', 'tenant', 'tenant_name',
            'role', 'role_name', 'role_display_name', 'is_active',
            'joined_at', 'invited_by', 'invited_by_email'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'joined_at', 'invited_by'
        ]


class TenantRoleSerializer(BaseModelSerializer):
    """
    Serializer for tenant role management.
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = TenantRole
        fields = BaseModelSerializer.Meta.fields + [
            'tenant', 'tenant_name', 'name', 'display_name', 'description',
            'permissions', 'asterisk', 'is_system_role', 'is_active', 'sort_order',
            'member_count'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'is_system_role'
        ]
    
    def get_member_count(self, obj):
        """Return count of active members with this role."""
        return obj.memberships.filter(is_active=True).count()
    
    def validate_name(self, value):
        """Validate role name is unique within tenant."""
        tenant = self.instance.tenant if self.instance else self.initial_data.get('tenant')
        if tenant:
            queryset = TenantRole.objects.filter(tenant=tenant, name=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError(_('Role with this name already exists in tenant.'))
        return value


class UserInvitationSerializer(BaseModelSerializer):
    """
    Serializer for user invitation management.
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    role_display_name = serializers.CharField(source='role.display_name', read_only=True)
    invited_by_email = serializers.CharField(source='invited_by.email', read_only=True)
    is_valid = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = UserInvitation
        fields = BaseModelSerializer.Meta.fields + [
            'tenant', 'tenant_name', 'email', 'role', 'role_display_name',
            'invited_by', 'invited_by_email', 'message', 'expires_at',
            'is_accepted', 'accepted_at', 'is_valid'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'token', 'invited_by', 'expires_at', 'is_accepted', 'accepted_at'
        ]
    
    def get_is_valid(self, obj):
        """Return whether invitation is still valid."""
        return obj.is_valid()
    
    def validate_email(self, value):
        """Validate email format and check for existing membership."""
        tenant = self.initial_data.get('tenant')
        if tenant:
            # Check if user is already a member of this tenant
            try:
                user = User.objects.get(email=value)
                if TenantMembership.objects.filter(
                    user=user, tenant=tenant, is_active=True
                ).exists():
                    raise ValidationError(
                        _('User is already a member of this tenant.')
                    )
            except User.DoesNotExist:
                # User doesn't exist yet, which is fine for invitations
                pass
            
            # Check for existing valid invitation
            if UserInvitation.objects.filter(
                tenant=tenant, email=value
            ).valid().exists():
                raise ValidationError(
                    _('A valid invitation already exists for this email.')
                )
        
        return value


class InvitationAcceptSerializer(serializers.Serializer):
    """
    Serializer for accepting user invitations.
    """
    
    token = serializers.UUIDField(
        help_text=_('Invitation token from the invitation email.')
    )
    user_data = UserRegistrationSerializer(
        required=False,
        help_text=_('User registration data if user does not exist.')
    )
    
    def validate_token(self, value):
        """Validate invitation token exists and is valid."""
        try:
            invitation = UserInvitation.objects.get(token=value)
            if not invitation.is_valid():
                raise ValidationError(_('Invitation has expired or been used.'))
            self.invitation = invitation
        except UserInvitation.DoesNotExist:
            raise ValidationError(_('Invalid invitation token.'))
        return value
    
    def validate(self, data):
        """Validate invitation acceptance."""
        invitation = self.invitation
        
        # Check if user already exists
        try:
            user = User.objects.get(email=invitation.email)
            data['user'] = user
            data['user_exists'] = True
        except User.DoesNotExist:
            # User needs to be created
            if not data.get('user_data'):
                raise ValidationError({
                    'user_data': _('User registration data is required for new users.')
                })
            
            # Validate email matches invitation
            if data['user_data']['email'] != invitation.email:
                raise ValidationError({
                    'user_data': {'email': _('Email must match invitation email.')}
                })
            
            data['user_exists'] = False
        
        data['invitation'] = invitation
        return data


# Session Management Serializers
class UserSessionSerializer(TimestampedModelSerializer):
    """
    Serializer for user session information.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_current_session = serializers.SerializerMethodField()
    
    class Meta(TimestampedModelSerializer.Meta):
        model = UserSession
        fields = TimestampedModelSerializer.Meta.fields + [
            'user', 'user_email', 'device_type', 'browser', 'operating_system',
            'ip_address', 'location', 'last_activity', 'is_active',
            'is_current_session'
        ]
        read_only_fields = TimestampedModelSerializer.Meta.read_only_fields + [
            'user', 'session_key', 'device_type', 'browser', 'operating_system',
            'ip_address', 'location', 'last_activity', 'ended_at'
        ]
    
    def get_is_current_session(self, obj):
        """Check if this is the current session."""
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            return obj.session_key == request.session.session_key
        return False


# Platform Administration Serializers
class PlatformRoleSerializer(BaseModelSerializer):
    """
    Serializer for platform role management.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    granted_by_email = serializers.CharField(source='granted_by.email', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta(BaseModelSerializer.Meta):
        model = PlatformRole
        fields = BaseModelSerializer.Meta.fields + [
            'user', 'user_email', 'user_full_name', 'role', 'role_display',
            'permissions', 'granted_by', 'granted_by_email', 'expires_at',
            'is_active', 'is_expired'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'granted_by'
        ]
    
    def get_is_expired(self, obj):
        """Check if role has expired."""
        return obj.is_expired()