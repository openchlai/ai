"""
Accounts App Managers

Custom managers and querysets for user management, authentication,
and tenant membership functionality.

Follows the core app patterns and extends BaseModelManager where appropriate.
"""

from datetime import timedelta
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone
from django.db.models import Q, Count, Exists, OuterRef

from apps.shared.core.managers import BaseModelManager


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    
    Extends Django's BaseUserManager to handle email as the primary
    authentication field instead of username.
    """
    
    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_platform_admin', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_platform_admin', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)
    
    def verified(self):
        """Return only verified users."""
        return self.filter(is_verified=True)
    
    def unverified(self):
        """Return only unverified users."""
        return self.filter(is_verified=False)
    
    def active(self):
        """Return only active users (not locked, not disabled)."""
        now = timezone.now()
        return self.filter(
            is_active=True
        ).filter(
            Q(account_locked_until__isnull=True) | 
            Q(account_locked_until__lt=now)
        )
    
    def locked(self):
        """Return only locked users."""
        now = timezone.now()
        return self.filter(
            account_locked_until__isnull=False,
            account_locked_until__gt=now
        )
    
    def platform_admins(self):
        """Return only platform administrators."""
        return self.filter(is_platform_admin=True, is_active=True)
    
    def with_2fa_enabled(self):
        """Return users with two-factor authentication enabled."""
        return self.filter(two_factor_enabled=True)
    
    def recent_signups(self, days=30):
        """Return users who signed up in the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(date_joined__gte=cutoff_date)
    
    def search(self, query):
        """Search users by email, name, or username."""
        return self.filter(
            Q(email__icontains=query) |
            Q(full_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        )


class TenantMembershipQuerySet(models.QuerySet):
    """Custom queryset for TenantMembership model."""
    
    def active(self):
        """Return only active memberships."""
        return self.filter(is_active=True)
    
    def inactive(self):
        """Return only inactive memberships."""
        return self.filter(is_active=False)
    
    def for_tenant(self, tenant):
        """Return memberships for a specific tenant."""
        return self.filter(tenant=tenant)
    
    def for_user(self, user):
        """Return memberships for a specific user."""
        return self.filter(user=user)
    
    def with_role(self, role_name):
        """Return memberships with a specific role name."""
        return self.filter(role__name=role_name)
    
    def admins(self):
        """Return admin memberships."""
        return self.filter(role__name__in=['admin', 'owner'])
    
    def supervisors(self):
        """Return supervisor memberships."""
        return self.filter(role__name='supervisor')
    
    def agents(self):
        """Return agent memberships."""
        return self.filter(role__name='agent')
    
    def recent_joins(self, days=30):
        """Return memberships created in the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(joined_at__gte=cutoff_date)
    
    def with_user_details(self):
        """Return memberships with user details prefetched."""
        return self.select_related('user', 'role', 'invited_by')
    
    def by_join_date(self):
        """Order by join date (newest first)."""
        return self.order_by('-joined_at')


class TenantMembershipManager(BaseModelManager):
    """Custom manager for TenantMembership model."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return TenantMembershipQuerySet(self.model, using=self._db)
    
    def active(self):
        """Return only active memberships."""
        return self.get_queryset().active()
    
    def for_tenant(self, tenant):
        """Return memberships for a specific tenant."""
        return self.get_queryset().for_tenant(tenant)
    
    def for_user(self, user):
        """Return memberships for a specific user."""
        return self.get_queryset().for_user(user)
    
    def create_membership(self, user, tenant, role, invited_by=None, created_by=None):
        """Create a new tenant membership with proper audit trail."""
        membership = self.create(
            user=user,
            tenant=tenant,
            role=role,
            invited_by=invited_by,
            created_by=created_by or invited_by,
            updated_by=created_by or invited_by
        )
        return membership
    
    def get_user_tenants(self, user):
        """Get all tenants where user has active membership."""
        return self.active().filter(user=user).values_list('tenant', flat=True)
    
    def get_tenant_users(self, tenant, role_name=None):
        """Get all users in a tenant, optionally filtered by role."""
        queryset = self.active().filter(tenant=tenant)
        if role_name:
            queryset = queryset.filter(role__name=role_name)
        return queryset.values_list('user', flat=True)


class TenantRoleQuerySet(models.QuerySet):
    """Custom queryset for TenantRole model."""
    
    def active(self):
        """Return only active roles."""
        return self.filter(is_active=True)
    
    def for_tenant(self, tenant):
        """Return roles for a specific tenant."""
        return self.filter(tenant=tenant)
    
    def system_roles(self):
        """Return only system-defined roles."""
        return self.filter(is_system_role=True)
    
    def custom_roles(self):
        """Return only custom (non-system) roles."""
        return self.filter(is_system_role=False)
    
    def with_permission(self, permission_key):
        """Return roles that have a specific permission."""
        return self.filter(permissions__has_key=permission_key)
    
    def ordered(self):
        """Return roles ordered by sort_order and name."""
        return self.order_by('sort_order', 'name')


class TenantRoleManager(BaseModelManager):
    """Custom manager for TenantRole model."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return TenantRoleQuerySet(self.model, using=self._db)
    
    def active(self):
        """Return only active roles."""
        return self.get_queryset().active()
    
    def for_tenant(self, tenant):
        """Return roles for a specific tenant."""
        return self.get_queryset().for_tenant(tenant)
    
    def create_default_roles(self, tenant, created_by):
        """Create default system roles for a new tenant."""
        default_roles = [
            {
                'name': 'owner',
                'display_name': 'Owner',
                'description': 'Full access to all tenant features and settings',
                'permissions': {
                    'admin.full_access': True,
                    'users.manage': True,
                    'settings.manage': True,
                    'billing.manage': True,
                },
                'is_system_role': True,
                'sort_order': 1
            },
            {
                'name': 'admin',
                'display_name': 'Administrator',
                'description': 'Administrative access to most tenant features',
                'permissions': {
                    'users.manage': True,
                    'cases.manage': True,
                    'reports.view': True,
                },
                'is_system_role': True,
                'sort_order': 2
            },
            {
                'name': 'supervisor',
                'display_name': 'Supervisor',
                'description': 'Supervisory access with team management capabilities',
                'permissions': {
                    'cases.manage': True,
                    'users.view': True,
                    'reports.view': True,
                },
                'is_system_role': True,
                'sort_order': 3
            },
            {
                'name': 'agent',
                'display_name': 'Agent',
                'description': 'Standard agent access for case handling',
                'permissions': {
                    'cases.create': True,
                    'cases.update_own': True,
                    'cases.view': True,
                },
                'is_system_role': True,
                'sort_order': 4
            },
            {
                'name': 'viewer',
                'display_name': 'Viewer',
                'description': 'Read-only access to cases and reports',
                'permissions': {
                    'cases.view': True,
                    'reports.view': True,
                },
                'is_system_role': True,
                'sort_order': 5
            }
        ]
        
        created_roles = []
        for role_data in default_roles:
            role = self.create(
                tenant=tenant,
                name=role_data['name'],
                display_name=role_data['display_name'],
                description=role_data['description'],
                permissions=role_data['permissions'],
                is_system_role=role_data['is_system_role'],
                sort_order=role_data['sort_order'],
                created_by=created_by,
                updated_by=created_by
            )
            created_roles.append(role)
        
        return created_roles


class OTPTokenQuerySet(models.QuerySet):
    """Custom queryset for OTPToken model."""
    
    def valid(self):
        """Return only valid (unused and not expired) tokens."""
        now = timezone.now()
        return self.filter(is_used=False, expires_at__gt=now)
    
    def expired(self):
        """Return only expired tokens."""
        now = timezone.now()
        return self.filter(expires_at__lte=now)
    
    def used(self):
        """Return only used tokens."""
        return self.filter(is_used=True)
    
    def for_user(self, user):
        """Return tokens for a specific user."""
        return self.filter(user=user)
    
    def by_type(self, token_type):
        """Return tokens of a specific type."""
        return self.filter(token_type=token_type)
    
    def by_delivery_method(self, method):
        """Return tokens by delivery method."""
        return self.filter(delivery_method=method)
    
    def recent(self, hours=24):
        """Return tokens created in the last N hours."""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return self.filter(created_at__gte=cutoff_time)
    
    def for_login(self):
        """Return login tokens."""
        return self.filter(token_type='login')
    
    def for_password_reset(self):
        """Return password reset tokens."""
        return self.filter(token_type='password_reset')
    
    def for_verification(self):
        """Return email verification tokens."""
        return self.filter(token_type='email_verification')


class OTPTokenManager(models.Manager):
    """Custom manager for OTPToken model with simplified authentication flow."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return OTPTokenQuerySet(self.model, using=self._db)
    
    def valid(self):
        """Return only valid tokens."""
        return self.get_queryset().valid()
    
    def for_user(self, user):
        """Return tokens for a specific user."""
        return self.get_queryset().for_user(user)
    
    def create_otp(self, user, token_type, delivery_method, recipient, 
                   expires_in_minutes=None, ip_address=None, user_agent=None):
        """
        Create a new OTP token with smart expiration based on purpose.
        
        Args:
            user: User instance
            token_type: 'login', 'password_reset', 'email_verification', 'account_unlock'
            delivery_method: 'email', 'sms', 'whatsapp'
            recipient: email address or phone number
            expires_in_minutes: optional override for expiration time
            ip_address: client IP address
            user_agent: client user agent string
        """
        import random
        import string
        
        # Generate 6-digit numeric token
        token = ''.join(random.choices(string.digits, k=6))
        
        # Set smart expiration times based on token type
        if expires_in_minutes is None:
            expiration_map = {
                'login': 10,                    # Login OTP expires in 10 minutes
                'password_reset': 15,           # Password reset OTP expires in 15 minutes
                'email_verification': 30,       # Email verification expires in 30 minutes
                'account_unlock': 10            # Account unlock expires in 10 minutes
            }
            expires_in_minutes = expiration_map.get(token_type, 10)
        
        expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)
        
        # Invalidate any existing valid tokens of the same type for this user
        # This prevents OTP spam and ensures only one valid token per purpose
        self.valid().filter(
            user=user,
            token_type=token_type
        ).update(
            is_used=True, 
            used_at=timezone.now()
        )
        
        # Create new token
        otp_token = self.create(
            user=user,
            token=token,
            token_type=token_type,
            delivery_method=delivery_method,
            recipient=recipient,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # TODO: Send OTP via chosen delivery method
        # This would integrate with email/SMS/WhatsApp services
        self._send_otp(otp_token)
        
        return otp_token
    
    def verify_otp(self, user, token, token_type):
        """
        Verify an OTP token for the given user and purpose.
        
        Returns:
            tuple: (is_valid: bool, otp_token: OTPToken|None)
        """
        try:
            # Find valid token matching criteria
            otp_token = self.valid().get(
                user=user,
                token=token,
                token_type=token_type
            )
            
            # Mark as used
            otp_token.mark_as_used()
            return True, otp_token
            
        except self.model.DoesNotExist:
            # Check if token exists but is invalid (expired or used)
            try:
                otp_token = self.get(
                    user=user,
                    token=token,
                    token_type=token_type
                )
                # Increment attempts for rate limiting
                otp_token.attempts += 1
                otp_token.save(update_fields=['attempts'])
                return False, otp_token
                
            except self.model.DoesNotExist:
                # Token doesn't exist at all
                return False, None
    
    def verify_login_otp(self, user, token):
        """Convenience method for login OTP verification."""
        return self.verify_otp(user, token, 'login')
    
    def verify_password_reset_otp(self, user, token):
        """Convenience method for password reset OTP verification."""
        return self.verify_otp(user, token, 'password_reset')
    
    def verify_email_verification_otp(self, user, token):
        """Convenience method for email verification OTP."""
        return self.verify_otp(user, token, 'email_verification')
    
    def create_login_otp(self, user, delivery_method='email', recipient=None):
        """Create OTP for login authentication."""
        if not recipient:
            recipient = user.email if delivery_method == 'email' else user.phone
        
        return self.create_otp(
            user=user,
            token_type='login',
            delivery_method=delivery_method,
            recipient=recipient,
            expires_in_minutes=10
        )
    
    def create_password_reset_otp(self, user, delivery_method='email', recipient=None):
        """Create OTP for password reset."""
        if not recipient:
            recipient = user.email if delivery_method == 'email' else user.phone
        
        return self.create_otp(
            user=user,
            token_type='password_reset',
            delivery_method=delivery_method,
            recipient=recipient,
            expires_in_minutes=15
        )
    
    def create_email_verification_otp(self, user):
        """Create OTP for email verification."""
        return self.create_otp(
            user=user,
            token_type='email_verification',
            delivery_method='email',
            recipient=user.email,
            expires_in_minutes=30
        )
    
    def get_user_recent_attempts(self, user, token_type, hours=1):
        """Get count of recent OTP requests for rate limiting."""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return self.filter(
            user=user,
            token_type=token_type,
            created_at__gte=cutoff_time
        ).count()
    
    def can_request_otp(self, user, token_type, max_attempts_per_hour=5):
        """Check if user can request another OTP (rate limiting)."""
        recent_attempts = self.get_user_recent_attempts(user, token_type)
        return recent_attempts < max_attempts_per_hour
    
    def cleanup_expired(self, older_than_days=7):
        """
        Clean up expired tokens older than specified days.
        Default is 7 days to maintain some audit trail.
        """
        cutoff_date = timezone.now() - timedelta(days=older_than_days)
        deleted_count, _ = self.filter(
            expires_at__lt=cutoff_date
        ).delete()
        return deleted_count
    
    def cleanup_used_tokens(self, older_than_hours=24):
        """Clean up used tokens older than specified hours."""
        cutoff_time = timezone.now() - timedelta(hours=older_than_hours)
        deleted_count, _ = self.filter(
            is_used=True,
            used_at__lt=cutoff_time
        ).delete()
        return deleted_count
    
    def get_delivery_stats(self, user=None, days=30):
        """Get delivery method statistics for analytics."""
        queryset = self.filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        )
        if user:
            queryset = queryset.filter(user=user)
        
        from django.db.models import Count
        return queryset.values('delivery_method').annotate(
            count=Count('id')
        ).order_by('-count')
    
    def _send_otp(self, otp_token):
        """
        Send OTP via the specified delivery method.
        This is a placeholder for actual delivery service integration.
        """
        # TODO: Implement actual OTP delivery
        # This would integrate with:
        # - Email service (SMTP, SendGrid, etc.)
        # - SMS service (Twilio, Africa's Talking, etc.) 
        # - WhatsApp Business API
        
        delivery_methods = {
            'email': self._send_email_otp,
            'sms': self._send_sms_otp,
            'whatsapp': self._send_whatsapp_otp
        }
        
        send_method = delivery_methods.get(otp_token.delivery_method)
        if send_method:
            try:
                send_method(otp_token)
            except Exception as e:
                # Log the error but don't fail the OTP creation
                # In production, you'd want proper logging here
                print(f"Failed to send OTP via {otp_token.delivery_method}: {e}")
    
    def _send_email_otp(self, otp_token):
        """Send OTP via email."""
        from django.core.mail import send_mail
        from django.conf import settings
        
        user = otp_token.user
        
        # Determine email subject based on token type
        subject_map = {
            'login': 'Your Login OTP Code',
            'password_reset': 'Password Reset OTP Code',
            'email_verification': 'Email Verification Code',
            'account_unlock': 'Account Unlock Code'
        }
        
        subject = subject_map.get(otp_token.token_type, 'Your OTP Code')
        
        # Create personalized message based on token type
        user_name = user.get_full_name() or user.first_name or user.email.split('@')[0]
        
        if otp_token.token_type == 'login':
            message = (
                f"Hello {user_name},\n\n"
                f"Your login verification code is: {otp_token.token}\n\n"
                f"This code will expire in 10 minutes.\n"
                f"If you didn't request this code, please ignore this email.\n\n"
                f"Best regards,\n"
                f"Murima Support Team"
            )
        elif otp_token.token_type == 'password_reset':
            message = (
                f"Hello {user_name},\n\n"
                f"You requested to reset your password. Your verification code is: {otp_token.token}\n\n"
                f"This code will expire in 15 minutes.\n"
                f"If you didn't request a password reset, please ignore this email.\n\n"
                f"Best regards,\n"
                f"Murima Support Team"
            )
        elif otp_token.token_type == 'email_verification':
            message = (
                f"Hello {user_name},\n\n"
                f"Welcome to Murima! Please verify your email address with this code: {otp_token.token}\n\n"
                f"This code will expire in 30 minutes.\n"
                f"If you didn't create an account, please ignore this email.\n\n"
                f"Best regards,\n"
                f"Murima Support Team"
            )
        elif otp_token.token_type == 'account_unlock':
            message = (
                f"Hello {user_name},\n\n"
                f"Your account unlock verification code is: {otp_token.token}\n\n"
                f"This code will expire in 10 minutes.\n"
                f"If you didn't request account unlock, please contact support.\n\n"
                f"Best regards,\n"
                f"Murima Support Team"
            )
        else:
            message = (
                f"Hello {user_name},\n\n"
                f"Your OTP code is: {otp_token.token}\n\n"
                f"This code will expire soon.\n\n"
                f"Best regards,\n"
                f"Murima Support Team"
            )
        
        try:
            # Get sender email from settings, fallback to default
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@bitz-itc.com')
            
            send_mail(
                subject,
                message,
                from_email,
                [otp_token.recipient],
                fail_silently=False,
            )
            print(f"✅ OTP email sent to {otp_token.recipient}")
            
        except Exception as e:
            print(f"❌ EMAIL ERROR: Failed to send OTP to {otp_token.recipient} - {e}")
            # In production, you might want to log this error properly
            # and potentially retry or use an alternative delivery method
            raise
    
    def _send_sms_otp(self, otp_token):
        """Send OTP via SMS."""
        # Placeholder for SMS delivery (Twilio, Africa's Talking, etc.)
        user = otp_token.user
        user_name = user.get_full_name() or user.first_name or "User"
        
        message = f"Hello {user_name}, your Murima verification code is: {otp_token.token}. It expires in {self._get_expiry_minutes(otp_token)} minutes."
        
        print(f"📱 SMS OTP: Sending '{message}' to {otp_token.recipient}")
        # TODO: Integrate with SMS service provider
        # Example: send_sms(to=otp_token.recipient, message=message)
    
    def _send_whatsapp_otp(self, otp_token):
        """Send OTP via WhatsApp."""
        # Placeholder for WhatsApp Business API
        user = otp_token.user
        user_name = user.get_full_name() or user.first_name or "User"
        
        message = f"Hello {user_name}, your Murima verification code is: {otp_token.token}. It expires in {self._get_expiry_minutes(otp_token)} minutes."
        
        print(f"💬 WhatsApp OTP: Sending '{message}' to {otp_token.recipient}")
        # TODO: Integrate with WhatsApp Business API
        # Example: send_whatsapp_message(to=otp_token.recipient, message=message)
    
    def _get_expiry_minutes(self, otp_token):
        """Calculate remaining minutes until OTP expires."""
        remaining = otp_token.expires_at - timezone.now()
        return max(1, int(remaining.total_seconds() / 60))

class UserSessionQuerySet(models.QuerySet):
    """Custom queryset for UserSession model."""
    
    def active(self):
        """Return only active sessions."""
        return self.filter(is_active=True)
    
    def for_user(self, user):
        """Return sessions for a specific user."""
        return self.filter(user=user)
    
    def by_device_type(self, device_type):
        """Return sessions by device type."""
        return self.filter(device_type=device_type)
    
    def recent_activity(self, hours=24):
        """Return sessions with recent activity."""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return self.filter(last_activity__gte=cutoff_time)
    
    def stale(self, hours=24):
        """Return sessions with no recent activity."""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return self.filter(last_activity__lt=cutoff_time)


class UserSessionManager(models.Manager):
    """Custom manager for UserSession model."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return UserSessionQuerySet(self.model, using=self._db)
    
    def active(self):
        """Return only active sessions."""
        return self.get_queryset().active()
    
    def for_user(self, user):
        """Return sessions for a specific user."""
        return self.get_queryset().for_user(user)
    
    def create_session(self, user, session_key, ip_address, user_agent=None):
        """Create a new user session."""
        # Parse user agent for device info (simplified)
        device_type = 'unknown'
        browser = ''
        operating_system = ''
        
        if user_agent:
            user_agent_lower = user_agent.lower()
            if 'mobile' in user_agent_lower:
                device_type = 'mobile'
            elif 'tablet' in user_agent_lower:
                device_type = 'tablet'
            else:
                device_type = 'desktop'
            
            # Extract browser info (simplified)
            if 'chrome' in user_agent_lower:
                browser = 'Chrome'
            elif 'firefox' in user_agent_lower:
                browser = 'Firefox'
            elif 'safari' in user_agent_lower:
                browser = 'Safari'
            elif 'edge' in user_agent_lower:
                browser = 'Edge'
        
        session = self.create(
            user=user,
            session_key=session_key,
            device_type=device_type,
            browser=browser,
            operating_system=operating_system,
            ip_address=ip_address
        )
        
        return session
    
    def cleanup_inactive(self, inactive_days=30):
        """Clean up inactive sessions older than specified days."""
        cutoff_date = timezone.now() - timedelta(days=inactive_days)
        updated_count = self.filter(
            is_active=True,
            last_activity__lt=cutoff_date
        ).update(
            is_active=False,
            ended_at=timezone.now()
        )
        return updated_count


class UserInvitationQuerySet(models.QuerySet):
    """Custom queryset for UserInvitation model."""
    
    def valid(self):
        """Return only valid (not accepted and not expired) invitations."""
        now = timezone.now()
        return self.filter(is_accepted=False, expires_at__gt=now)
    
    def expired(self):
        """Return only expired invitations."""
        now = timezone.now()
        return self.filter(expires_at__lte=now)
    
    def accepted(self):
        """Return only accepted invitations."""
        return self.filter(is_accepted=True)
    
    def pending(self):
        """Return only pending invitations."""
        return self.valid()
    
    def for_tenant(self, tenant):
        """Return invitations for a specific tenant."""
        return self.filter(tenant=tenant)
    
    def for_email(self, email):
        """Return invitations for a specific email."""
        return self.filter(email=email)


class UserInvitationManager(BaseModelManager):
    """Custom manager for UserInvitation model."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return UserInvitationQuerySet(self.model, using=self._db)
    
    def valid(self):
        """Return only valid invitations."""
        return self.get_queryset().valid()
    
    def for_tenant(self, tenant):
        """Return invitations for a specific tenant."""
        return self.get_queryset().for_tenant(tenant)
    
    def create_invitation(self, tenant, email, role, invited_by, 
                         message='', expires_in_days=7):
        """Create a new user invitation."""
        expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        # Invalidate any existing valid invitations for the same email/tenant
        self.valid().filter(
            tenant=tenant,
            email=email
        ).update(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by=invited_by
        )
        
        invitation = self.create(
            tenant=tenant,
            email=email,
            role=role,
            invited_by=invited_by,
            message=message,
            expires_at=expires_at,
            created_by=invited_by,
            updated_by=invited_by
        )
        
        return invitation
    
    def cleanup_expired(self, older_than_days=30):
        """Clean up expired invitations older than specified days."""
        cutoff_date = timezone.now() - timedelta(days=older_than_days)
        deleted_count, _ = self.filter(
            expires_at__lt=cutoff_date
        ).delete()
        return deleted_count