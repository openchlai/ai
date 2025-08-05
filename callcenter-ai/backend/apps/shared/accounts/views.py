"""
Accounts App Views

Provides API endpoints for user management, authentication,
tenant membership, and OTP-based verification workflows.

Includes comprehensive authentication flow with email/password + OTP
support for email, SMS, and WhatsApp delivery channels.
"""

from datetime import timedelta
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    User, TenantMembership, TenantRole, PlatformRole,
    OTPToken, UserSession, UserInvitation
)
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, ChangePasswordSerializer,
    LoginSerializer, OTPRequestSerializer, OTPVerificationSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    TenantMembershipSerializer, TenantRoleSerializer, UserInvitationSerializer,
    InvitationAcceptSerializer, UserSessionSerializer, PlatformRoleSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        token['is_verified'] = user.is_verified
        token['tenant_count'] = user.tenant_memberships.filter(is_active=True).count()
        
        return token

# apps/shared/accounts/views.py

class AuthViewSet(GenericViewSet):
    """
    Updated AuthViewSet for simplified authentication with password OR OTP login.
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user account."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate email verification OTP
            otp_token = OTPToken.objects.create_otp(
                user=user,
                token_type='email_verification',
                delivery_method='email',
                recipient=user.email,
                expires_in_minutes=30,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'message': 'Registration successful. Please verify your email.',
                'user_id': str(user.id),
                'verification_sent': True,
                'delivery_method': 'email'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Authenticate user with password OR initiate OTP login.
        """
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            requires_otp = serializer.validated_data['requires_otp']
            remember_me = serializer.validated_data.get('remember_me', False)
            
            if requires_otp:
                # OTP login flow - generate and send OTP
                delivery_method = request.data.get('delivery_method', 'email')
                
                # Validate delivery method and recipient
                if delivery_method == 'email':
                    recipient = user.email
                elif delivery_method in ['sms', 'whatsapp']:
                    if not user.phone:
                        return Response({
                            'error': 'Phone number required for SMS/WhatsApp delivery'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    recipient = user.phone
                else:
                    return Response({
                        'error': 'Invalid delivery method. Use email, sms, or whatsapp.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Generate login OTP
                otp_token = OTPToken.objects.create_otp(
                    user=user,
                    token_type='login',
                    delivery_method=delivery_method,
                    recipient=recipient,
                    expires_in_minutes=10,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response({
                    'requires_otp': True,
                    'delivery_method': delivery_method,
                    'message': f'Login OTP sent via {delivery_method}',
                    'user_id': str(user.id),
                    'expires_in': 10  # minutes
                }, status=status.HTTP_200_OK)
            
            else:
                # Password login flow - generate JWT tokens immediately
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Extend refresh token lifetime if remember_me
                if remember_me:
                    refresh.set_exp(lifetime=timedelta(days=30))
                
                # Create session record for tracking
                session_data = self._create_user_session(user, request, str(refresh['jti']))
                
                return Response({
                    'access_token': str(access_token),
                    'refresh_token': str(refresh),
                    'token_type': 'Bearer',
                    'expires_in': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                    'user': UserProfileSerializer(user).data,
                    'session_id': session_data['session_id'],
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_login_otp(self, request):
        """
        Complete OTP login and return JWT tokens.
        """
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        remember_me = request.data.get('remember_me', False)
        
        if not user_id or not token:
            return Response({
                'error': 'Both user_id and token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid user ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        is_valid, otp_token = OTPToken.objects.verify_otp(user, token, 'login')
        
        if not is_valid:
            if otp_token and otp_token.attempts >= 3:
                return Response({
                    'error': 'Too many failed attempts. Please request a new OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'error': 'Invalid or expired OTP token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=30))
        
        # Create session record
        session_data = self._create_user_session(user, request, str(refresh['jti']))
        
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            'user': UserProfileSerializer(user).data,
            'session_id': session_data['session_id'],
            'message': 'OTP verification successful'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def request_otp(self, request):
        """
        Request OTP for login or password reset.
        """
        email = request.data.get('email')
        purpose = request.data.get('purpose', 'login')  # 'login' or 'password_reset'
        delivery_method = request.data.get('delivery_method', 'email')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if purpose not in ['login', 'password_reset']:
            return Response({
                'error': 'Invalid purpose. Use "login" or "password_reset".'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return Response({
                'message': f'If the email exists, an OTP has been sent via {delivery_method}'
            }, status=status.HTTP_200_OK)
        
        # Check if account is locked
        if user.is_account_locked():
            return Response({
                'error': 'Account is temporarily locked. Please try again later.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate delivery method and recipient
        if delivery_method == 'email':
            recipient = user.email
        elif delivery_method in ['sms', 'whatsapp']:
            if not user.phone:
                return Response({
                    'error': 'Phone number not available for SMS/WhatsApp delivery'
                }, status=status.HTTP_400_BAD_REQUEST)
            recipient = user.phone
        else:
            return Response({
                'error': 'Invalid delivery method. Use email, sms, or whatsapp.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP
        otp_token = OTPToken.objects.create_otp(
            user=user,
            token_type=purpose,
            delivery_method=delivery_method,
            recipient=recipient,
            expires_in_minutes=10,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': f'OTP sent via {delivery_method}',
            'delivery_method': delivery_method,
            'user_id': str(user.id),
            'expires_in': 10  # minutes
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """
        Verify OTP for email verification or other purposes.
        """
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        token_type = request.data.get('token_type', 'email_verification')
        
        if not user_id or not token:
            return Response({
                'error': 'Both user_id and token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid user ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        is_valid, otp_token = OTPToken.objects.verify_otp(user, token, token_type)
        
        if not is_valid:
            if otp_token and otp_token.attempts >= 3:
                return Response({
                    'error': 'Too many failed attempts. Please request a new OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'error': 'Invalid or expired OTP token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle different token types
        if token_type == 'email_verification':
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            
            return Response({
                'message': 'Email verified successfully',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'OTP verified successfully',
            'token_type': token_type
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def reset_password_request(self, request):
        """
        Request password reset OTP.
        """
        return self.request_otp(request)  # Reuse the request_otp logic
    
    @action(detail=False, methods=['post'])
    def reset_password_confirm(self, request):
        """
        Reset password using OTP verification.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Set new password
            user.set_password(new_password)
            user.last_password_change = timezone.now()
            user.save(update_fields=['password', 'last_password_change'])
            
            # End all user sessions for security
            UserSession.objects.filter(
                user=user, 
                is_active=True
            ).update(
                is_active=False,
                ended_at=timezone.now()
            )
            
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user and blacklist refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # End user session record
            session_id = request.data.get('session_id')
            if session_id:
                UserSession.objects.filter(
                    session_key=session_id,
                    user=request.user,
                    is_active=True
                ).update(
                    is_active=False,
                    ended_at=timezone.now()
                )
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Logout failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        """Refresh access token using refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({
                    'error': 'Refresh token required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            access_token = token.access_token
            
            return Response({
                'access_token': str(access_token),
                'expires_in': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            })
            
        except Exception as e:
            return Response({
                'error': 'Token refresh failed',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    def _create_user_session(self, user, request, jti):
        """Create session record for JWT tracking."""
        session = UserSession.objects.create_session(
            user=user,
            session_key=jti,  # Use JWT ID as session key
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return {'session_id': str(session.id)}

# User Profile Management
class UserProfileViewSet(GenericViewSet):
    """
    ViewSet for user profile management.
    
    Provides endpoints for viewing and updating user profiles,
    changing passwords, and managing account settings.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Update current user's profile information.
        """
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user's password.
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # End all other sessions for security
            UserSession.objects.filter(
                user=request.user, 
                is_active=True
            ).exclude(
                session_key=request.session.session_key
            ).update(
                is_active=False,
                ended_at=timezone.now()
            )
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def enable_2fa(self, request):
        """
        Enable two-factor authentication for user.
        """
        user = request.user
        
        # Verify user's email or phone based on preferred method
        preferred_method = request.data.get('preferred_2fa_method', 'email')
        
        if preferred_method in ['sms', 'whatsapp'] and not user.phone:
            return Response({
                'error': 'Phone number required for SMS/WhatsApp 2FA'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if preferred_method == 'email' and not user.is_verified:
            return Response({
                'error': 'Email must be verified before enabling 2FA'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate verification OTP
        recipient = user.email if preferred_method == 'email' else user.phone
        otp_token = OTPToken.objects.create_otp(
            user=user,
            token_type='email_verification' if preferred_method == 'email' else 'phone_verification',
            delivery_method=preferred_method,
            recipient=recipient,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': f'Verification code sent via {preferred_method}',
            'step': 'verify_method',
            'delivery_method': preferred_method
        })
    
    @action(detail=False, methods=['post'])
    def confirm_2fa_setup(self, request):
        """
        Confirm 2FA setup with OTP verification.
        """
        serializer = OTPVerificationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            preferred_method = request.data.get('preferred_2fa_method', 'email')
            
            user.two_factor_enabled = True
            user.preferred_2fa_method = preferred_method
            user.save(update_fields=['two_factor_enabled', 'preferred_2fa_method'])
            
            return Response({
                'message': '2FA enabled successfully',
                'user': UserProfileSerializer(user).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def disable_2fa(self, request):
        """
        Disable two-factor authentication.
        """
        user = request.user
        user.two_factor_enabled = False
        user.save(update_fields=['two_factor_enabled'])
        
        return Response({
            'message': '2FA disabled successfully',
            'user': UserProfileSerializer(user).data
        })


# Session Management
class UserSessionViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    """
    ViewSet for managing user sessions.
    
    Allows users to view and manage their active sessions.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSessionSerializer
    
    def get_queryset(self):
        """Return sessions for the current user."""
        return UserSession.objects.filter(
            user=self.request.user
        ).order_by('-last_activity')
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """
        End a specific session.
        """
        session = self.get_object()
        
        if session.user != request.user:
            return Response({
                'error': 'You can only end your own sessions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        session.end_session()
        
        return Response({
            'message': 'Session ended successfully'
        })
    
    @action(detail=False, methods=['post'])
    def end_all_other_sessions(self, request):
        """
        End all sessions except the current one.
        """
        current_session_key = request.session.session_key
        
        ended_count = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(
            session_key=current_session_key
        ).update(
            is_active=False,
            ended_at=timezone.now()
        )
        
        return Response({
            'message': f'Ended {ended_count} other session(s)'
        })


# Tenant Management Views
class TenantMembershipViewSet(ModelViewSet):
    """
    ViewSet for tenant membership management.
    
    Requires proper tenant context and permissions.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TenantMembershipSerializer
    
    def get_queryset(self):
        """Return memberships for current tenant."""
        # TODO: Add tenant filtering when tenants app is implemented
        # tenant = get_current_tenant(self.request)
        # return TenantMembership.objects.filter(tenant=tenant)
        return TenantMembership.objects.none()  # Placeholder


class TenantRoleViewSet(ModelViewSet):
    """
    ViewSet for tenant role management.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TenantRoleSerializer
    
    def get_queryset(self):
        """Return roles for current tenant."""
        # TODO: Add tenant filtering when tenants app is implemented
        return TenantRole.objects.none()  # Placeholder


class UserInvitationViewSet(ModelViewSet):
    """
    ViewSet for user invitation management.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserInvitationSerializer
    
    def get_queryset(self):
        """Return invitations for current tenant."""
        # TODO: Add tenant filtering when tenants app is implemented
        return UserInvitation.objects.none()  # Placeholder
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """
        Resend an invitation email.
        """
        invitation = self.get_object()
        
        if not invitation.is_valid():
            return Response({
                'error': 'Invitation is no longer valid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Send invitation email
        # send_invitation_email(invitation)
        
        return Response({
            'message': 'Invitation resent successfully'
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an invitation.
        """
        invitation = self.get_object()
        invitation.soft_delete(user=request.user)
        
        return Response({
            'message': 'Invitation cancelled successfully'
        })


# Public Invitation Views
class PublicInvitationView(APIView):
    """
    Public view for accepting invitations without authentication.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        """
        Get invitation details by token.
        """
        try:
            invitation = UserInvitation.objects.get(token=token)
            if not invitation.is_valid():
                return Response({
                    'error': 'Invitation has expired or been used'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already exists
            user_exists = User.objects.filter(email=invitation.email).exists()
            
            return Response({
                'invitation': {
                    'tenant_name': invitation.tenant.name,
                    'role_name': invitation.role.display_name,
                    'invited_by': invitation.invited_by.get_full_name(),
                    'email': invitation.email,
                    'message': invitation.message,
                    'expires_at': invitation.expires_at
                },
                'user_exists': user_exists
            })
            
        except UserInvitation.DoesNotExist:
            return Response({
                'error': 'Invalid invitation token'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, token):
        """
        Accept an invitation.
        """
        data = request.data.copy()
        data['token'] = token
        
        serializer = InvitationAcceptSerializer(data=data)
        if serializer.is_valid():
            invitation = serializer.validated_data['invitation']
            user_exists = serializer.validated_data['user_exists']
            
            with transaction.atomic():
                if user_exists:
                    user = serializer.validated_data['user']
                else:
                    # Create new user
                    user_serializer = UserRegistrationSerializer(
                        data=serializer.validated_data['user_data']
                    )
                    if user_serializer.is_valid():
                        user = user_serializer.save()
                    else:
                        return Response(
                            user_serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Accept invitation and create membership
                membership = invitation.accept(user)
                
                return Response({
                    'message': 'Invitation accepted successfully',
                    'user': UserProfileSerializer(user).data,
                    'membership': TenantMembershipSerializer(membership).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Platform Administration Views
class PlatformRoleViewSet(ModelViewSet):
    """
    ViewSet for platform role management.
    
    Restricted to platform administrators.
    """
    
    permission_classes = [IsAuthenticated]  # TODO: Add PlatformAdminPermission
    serializer_class = PlatformRoleSerializer
    queryset = PlatformRole.objects.all()
    
    def perform_create(self, serializer):
        """Set granted_by to current user."""
        serializer.save(
            granted_by=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by to current user."""
        serializer.save(updated_by=self.request.user)


# Health Check View
class HealthCheckView(APIView):
    """
    Simple health check endpoint for the accounts app.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return health status."""
        return Response({
            'status': 'healthy',
            'service': 'accounts',
            'timestamp': timezone.now()
        })