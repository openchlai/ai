"""
Accounts App URL Configuration

Updated URL patterns for simplified authentication with password OR OTP login,
removing 2FA complexity while maintaining flexible authentication options.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AuthViewSet, UserProfileViewSet, UserSessionViewSet,
    TenantMembershipViewSet, TenantRoleViewSet, UserInvitationViewSet,
    PlatformRoleViewSet, PublicInvitationView, HealthCheckView
)
from rest_framework_simplejwt.views import TokenRefreshView

# Create router for ViewSets
router = DefaultRouter()

# Authentication and user management
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'sessions', UserSessionViewSet, basename='sessions')

# Tenant management (these will be properly filtered by tenant when tenants app is ready)
router.register(r'memberships', TenantMembershipViewSet, basename='memberships')
router.register(r'roles', TenantRoleViewSet, basename='roles')
router.register(r'invitations', UserInvitationViewSet, basename='invitations')

# Platform administration
router.register(r'platform-roles', PlatformRoleViewSet, basename='platform-roles')

app_name = 'accounts'

# Main URL patterns

urlpatterns = [
    # Health check endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # Public invitation endpoints (no authentication required)
    path('invitation/<uuid:token>/', PublicInvitationView.as_view(), name='invitation-detail'),
    path('invitation/<uuid:token>/accept/', PublicInvitationView.as_view(), name='invitation-accept'),
    
    # API endpoints
    path('api/v1/', include(router.urls)),
    
    # JWT endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

# Primary Authentication Endpoints
auth_patterns = [
    # User Registration
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    
    # Login (Password OR OTP)
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('verify-login-otp/', AuthViewSet.as_view({'post': 'verify_login_otp'}), name='verify-login-otp'),
    
    # Logout
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    
    # OTP Management
    path('request-otp/', AuthViewSet.as_view({'post': 'request_otp'}), name='request-otp'),
    path('verify-otp/', AuthViewSet.as_view({'post': 'verify_otp'}), name='verify-otp'),
    
    # Password Reset
    path('reset-password/', AuthViewSet.as_view({'post': 'reset_password_request'}), name='reset-password'),
    path('reset-password-confirm/', AuthViewSet.as_view({'post': 'reset_password_confirm'}), name='reset-password-confirm'),
    
    # JWT Token Management
    path('refresh/', AuthViewSet.as_view({'post': 'refresh_token'}), name='jwt-refresh'),
]

# User Profile Management Endpoints
profile_patterns = [
    path('me/', UserProfileViewSet.as_view({'get': 'me'}), name='profile-me'),
    path('update/', UserProfileViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='profile-update'),
    path('change-password/', UserProfileViewSet.as_view({'post': 'change_password'}), name='change-password'),
]

# Session Management Endpoints
session_patterns = [
    path('', UserSessionViewSet.as_view({'get': 'list'}), name='sessions-list'),
    path('<uuid:pk>/', UserSessionViewSet.as_view({'get': 'retrieve'}), name='session-detail'),
    path('<uuid:pk>/end/', UserSessionViewSet.as_view({'post': 'end_session'}), name='session-end'),
    path('end-others/', UserSessionViewSet.as_view({'post': 'end_all_other_sessions'}), name='sessions-end-others'),
]

# Add URL patterns
urlpatterns += [
    path('auth/', include(auth_patterns)),
    path('profile/', include(profile_patterns)),
    path('sessions/', include(session_patterns)),
]

# API v1 endpoints (structured for API documentation)
v1_patterns = [
    # Authentication
    path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='v1-register'),
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='v1-login'),
    path('auth/verify-login-otp/', AuthViewSet.as_view({'post': 'verify_login_otp'}), name='v1-verify-login-otp'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='v1-logout'),
    path('auth/otp/request/', AuthViewSet.as_view({'post': 'request_otp'}), name='v1-request-otp'),
    path('auth/otp/verify/', AuthViewSet.as_view({'post': 'verify_otp'}), name='v1-verify-otp'),
    path('auth/password/reset/', AuthViewSet.as_view({'post': 'reset_password_request'}), name='v1-reset-password'),
    path('auth/password/confirm/', AuthViewSet.as_view({'post': 'reset_password_confirm'}), name='v1-reset-password-confirm'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='v1-token-refresh'),
    
    # User profile
    path('users/me/', UserProfileViewSet.as_view({'get': 'me'}), name='v1-user-me'),
    path('users/me/update/', UserProfileViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='v1-user-update'),
    path('users/me/password/', UserProfileViewSet.as_view({'post': 'change_password'}), name='v1-user-change-password'),
    
    # Session management
    path('users/me/sessions/', UserSessionViewSet.as_view({'get': 'list'}), name='v1-user-sessions'),
    path('users/me/sessions/<uuid:pk>/', UserSessionViewSet.as_view({'get': 'retrieve'}), name='v1-user-session-detail'),
    path('users/me/sessions/<uuid:pk>/end/', UserSessionViewSet.as_view({'post': 'end_session'}), name='v1-user-session-end'),
    path('users/me/sessions/end-others/', UserSessionViewSet.as_view({'post': 'end_all_other_sessions'}), name='v1-user-sessions-end-others'),
    
    # Tenant membership
    path('memberships/', TenantMembershipViewSet.as_view({'get': 'list', 'post': 'create'}), name='v1-memberships'),
    path('memberships/<uuid:pk>/', TenantMembershipViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='v1-membership-detail'),
    
    # Tenant roles
    path('roles/', TenantRoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='v1-roles'),
    path('roles/<uuid:pk>/', TenantRoleViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='v1-role-detail'),
    
    # User invitations
    path('invitations/', UserInvitationViewSet.as_view({'get': 'list', 'post': 'create'}), name='v1-invitations'),
    path('invitations/<uuid:pk>/', UserInvitationViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='v1-invitation-detail'),
    path('invitations/<uuid:pk>/resend/', UserInvitationViewSet.as_view({'post': 'resend'}), name='v1-invitation-resend'),
    path('invitations/<uuid:pk>/cancel/', UserInvitationViewSet.as_view({'post': 'cancel'}), name='v1-invitation-cancel'),
    
    # Platform administration
    path('platform/roles/', PlatformRoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='v1-platform-roles'),
    path('platform/roles/<uuid:pk>/', PlatformRoleViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='v1-platform-role-detail'),
]

urlpatterns += [
    path('api/v1/', include(v1_patterns)),
]

# RESTful alternative paths (for developers who prefer this structure)
rest_patterns = [
    # Simple authentication endpoints
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='rest-register'),
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='rest-login'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='rest-logout'),
    path('verify-login-otp/', AuthViewSet.as_view({'post': 'verify_login_otp'}), name='rest-verify-login-otp'),
    path('request-otp/', AuthViewSet.as_view({'post': 'request_otp'}), name='rest-request-otp'),
    path('verify-otp/', AuthViewSet.as_view({'post': 'verify_otp'}), name='rest-verify-otp'),
    path('forgot-password/', AuthViewSet.as_view({'post': 'reset_password_request'}), name='rest-forgot-password'),
    path('reset-password/', AuthViewSet.as_view({'post': 'reset_password_confirm'}), name='rest-reset-password'),
    
    # User profile endpoints
    path('me/', UserProfileViewSet.as_view({'get': 'me'}), name='rest-me'),
    path('me/update/', UserProfileViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='rest-me-update'),
    path('me/change-password/', UserProfileViewSet.as_view({'post': 'change_password'}), name='rest-change-password'),
    path('me/sessions/', UserSessionViewSet.as_view({'get': 'list'}), name='rest-my-sessions'),
    path('me/sessions/end-others/', UserSessionViewSet.as_view({'post': 'end_all_other_sessions'}), name='rest-end-other-sessions'),
]

urlpatterns += [
    path('', include(rest_patterns)),
]

# Admin interface endpoints
admin_patterns = [
    path('admin/users/', include([
        path('', UserProfileViewSet.as_view({'get': 'list'}), name='admin-users-list'),
        path('<uuid:pk>/', UserProfileViewSet.as_view({'get': 'retrieve'}), name='admin-user-detail'),
    ])),
    path('admin/memberships/', include([
        path('', TenantMembershipViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-memberships-list'),
        path('<uuid:pk>/', TenantMembershipViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-membership-detail'),
    ])),
    path('admin/roles/', include([
        path('', TenantRoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-roles-list'),
        path('<uuid:pk>/', TenantRoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-role-detail'),
    ])),
    path('admin/invitations/', include([
        path('', UserInvitationViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-invitations-list'),
        path('<uuid:pk>/', UserInvitationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-invitation-detail'),
        path('<uuid:pk>/resend/', UserInvitationViewSet.as_view({'post': 'resend'}), name='admin-invitation-resend'),
    ])),
    path('admin/platform-roles/', include([
        path('', PlatformRoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-platform-roles-list'),
        path('<uuid:pk>/', PlatformRoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-platform-role-detail'),
    ])),
]

urlpatterns += [
    path('admin-api/', include(admin_patterns)),
]

# Webhook endpoints for external integrations
webhook_patterns = [
    # OTP delivery status webhooks
    path('sms/delivery/', AuthViewSet.as_view({'post': 'sms_delivery_webhook'}), name='webhook-sms-delivery'),
    path('whatsapp/delivery/', AuthViewSet.as_view({'post': 'whatsapp_delivery_webhook'}), name='webhook-whatsapp-delivery'),
    path('email/delivery/', AuthViewSet.as_view({'post': 'email_delivery_webhook'}), name='webhook-email-delivery'),
]

urlpatterns += [
    path('webhooks/', include(webhook_patterns)),
]

"""
=== SIMPLIFIED AUTHENTICATION URL EXAMPLES ===

🔐 AUTHENTICATION ENDPOINTS:

Registration:
POST /accounts/auth/register/
POST /accounts/register/

Password Login:
POST /accounts/auth/login/
{
  "email": "user@example.com",
  "password": "password123",
  "login_method": "password",
  "remember_me": true
}

OTP Login (Step 1 - Request OTP):
POST /accounts/auth/login/
{
  "email": "user@example.com",
  "login_method": "otp",
  "delivery_method": "email"
}

OTP Login (Step 2 - Verify OTP):
POST /accounts/auth/verify-login-otp/
{
  "user_id": "uuid",
  "token": "123456",
  "remember_me": true
}

Alternative OTP Request:
POST /accounts/auth/request-otp/
{
  "email": "user@example.com",
  "purpose": "login",
  "delivery_method": "sms"
}

Generic OTP Verification:
POST /accounts/auth/verify-otp/
{
  "user_id": "uuid",
  "token": "123456",
  "token_type": "login"
}

Password Reset (Step 1):
POST /accounts/auth/reset-password/
{
  "email": "user@example.com",
  "delivery_method": "whatsapp"
}

Password Reset (Step 2):
POST /accounts/auth/reset-password-confirm/
{
  "email": "user@example.com",
  "otp_token": "123456",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}

Logout:
POST /accounts/auth/logout/
{
  "refresh_token": "...",
  "session_id": "uuid"
}

Token Refresh:
POST /accounts/auth/token/refresh/
POST /accounts/auth/refresh/

👤 USER PROFILE:
GET /accounts/profile/me/
PUT/PATCH /accounts/profile/update/
POST /accounts/profile/change-password/

💻 SESSION MANAGEMENT:
GET /accounts/sessions/
GET /accounts/sessions/{id}/
POST /accounts/sessions/{id}/end/
POST /accounts/sessions/end-others/

🔗 PUBLIC INVITATIONS:
GET /accounts/invitation/{token}/
POST /accounts/invitation/{token}/accept/

🏢 TENANT MANAGEMENT:
GET/POST /accounts/memberships/
GET/PUT/DELETE /accounts/memberships/{id}/
GET/POST /accounts/roles/
GET/POST /accounts/invitations/

⚙️ HEALTH CHECK:
GET /accounts/health/

=== KEY CHANGES FROM 2FA SYSTEM ===

❌ REMOVED:
- /auth/verify-2fa/
- /auth/enable-2fa/
- /auth/confirm-2fa/
- /auth/disable-2fa/

✅ ADDED:
- /auth/verify-login-otp/
- Enhanced /auth/login/ with login_method parameter
- Enhanced /auth/request-otp/ with purpose parameter

✨ SIMPLIFIED FLOW:
1. Login with password → Get tokens immediately
2. Login with OTP → Get OTP → Verify OTP → Get tokens
3. Password reset → Request OTP → Verify OTP + new password
"""