"""
Tenants App URLs

Provides URL routing for tenant management with clear separation between:
- Platform admin endpoints (cross-tenant management)
- Tenant self-management endpoints
- Public endpoints (invitations, health checks)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# Create routers for different API sections
platform_router = DefaultRouter()
tenant_router = DefaultRouter()

# Platform Admin Routes (cross-tenant management)
platform_router.register(
    r"tenants", views.PlatformTenantViewSet, basename="platform-tenant"
)
platform_router.register(
    r"domains", views.PlatformDomainViewSet, basename="platform-domain"
)

# Tenant Self-Management Routes (only these will be included in the api app)
# Note: Removed my-tenants from router since it conflicts with function-based view
tenant_router.register(
    r"tenant-management", views.TenantSelfManagementViewSet, basename="tenant-self"
)
tenant_router.register(
    r"invitations", views.TenantInvitationViewSet, basename="tenant-invitation"
)
tenant_router.register(
    r"settings", views.TenantSettingsViewSet, basename="tenant-settings"
)

# App name for namespacing
app_name = "tenants"

urlpatterns = [
    # ==============================================
    # TENANT SELF-MANAGEMENT ENDPOINTS
    # ==============================================
    # These endpoints are for tenant owners/admins to manage their own tenant
    # Will be accessed via: /api/v1/tenant/... (api app provides /api/v1/)
    
    # RESTful tenant self-management (router handles the base URLs)
    path("", include(tenant_router.urls)),
    
    # Additional tenant management actions (non-router URLs)
    path(
        "current/",
        views.TenantSelfManagementViewSet.as_view({"get": "current_tenant"}),
        name="current-tenant",
    ),
    path(
        "<uuid:pk>/branding/",
        views.TenantSelfManagementViewSet.as_view({"post": "update_branding"}),
        name="tenant-update-branding",
    ),
    path(
        "<uuid:pk>/feature/",
        views.TenantSelfManagementViewSet.as_view({"post": "toggle_feature"}),
        name="tenant-toggle-feature",
    ),
    
    # Invitation management actions (extend router URLs)
    path(
        "invitations/<uuid:pk>/reminder/",
        views.TenantInvitationViewSet.as_view({"post": "send_reminder"}),
        name="invitation-send-reminder",
    ),
    path(
        "invitations/<uuid:pk>/revoke/",
        views.TenantInvitationViewSet.as_view({"post": "revoke"}),
        name="invitation-revoke",
    ),
    path(
        "invitations/bulk-reminders/",
        views.TenantInvitationViewSet.as_view({"post": "bulk_send_reminders"}),
        name="invitation-bulk-reminders",
    ),
    
    # Settings management actions (extend router URLs)
    path(
        "settings/by-category/",
        views.TenantSettingsViewSet.as_view({"get": "by_category"}),
        name="settings-by-category",
    ),
    path(
        "settings/bulk-update/",
        views.TenantSettingsViewSet.as_view({"post": "bulk_update"}),
        name="settings-bulk-update",
    ),
    
    # Standalone endpoints
    path("create/", views.create_tenant, name="create-tenant"),
    path("my-tenants/", views.list_my_tenants, name="list-my-tenants"),
    path(
        "check-subdomain/",
        views.check_subdomain_availability,
        name="check-subdomain",
    ),
]

# ==============================================
# PLATFORM ADMIN ENDPOINTS (Separate from tenant app)
# ==============================================
# These should be defined in a separate URLs file for platform admin
# or in the main project urls.py, not in tenant app URLs
# They would be accessed via: /api/platform/... (bypassing the v1 routing)

platform_urlpatterns = [
    # RESTful tenant and domain management  
    path("", include(platform_router.urls)),
    # Additional platform admin endpoints
    path(
        "statistics/",
        views.PlatformTenantViewSet.as_view({"get": "platform_statistics"}),
        name="platform-statistics",
    ),
    path("system-status/", views.system_status, name="system-status"),
    # Bulk operations
    path(
        "tenants/bulk-action/",
        views.PlatformTenantViewSet.as_view({"post": "bulk_action"}),
        name="platform-tenant-bulk-action",
    ),
    path(
        "domains/bulk-verify/",
        views.PlatformDomainViewSet.as_view({"post": "bulk_verify"}),
        name="platform-domain-bulk-verify",
    ),
]

# ==============================================
# PUBLIC ENDPOINTS (Separate from tenant app)
# ==============================================  
# These should be defined in main project urls.py
# They would be accessed via: /api/public/... (bypassing the v1 routing)

public_urlpatterns = [
    # Tenant public information (for branding, etc.)
    path(
        "tenant/<str:subdomain>/",
        views.tenant_public_info,
        name="tenant-public-info",
    ),
    # Invitation handling (public access needed)
    path(
        "invitation/<uuid:token>/",
        views.invitation_details,
        name="invitation-details",
    ),
    path(
        "invitation/accept/",
        views.accept_invitation,
        name="invitation-accept",
    ),
    # Subdomain validation (for signup forms)
    path(
        "validate-subdomain/",
        views.validate_subdomain,
        name="validate-subdomain",
    ),
    # Health check
    path("health/", views.health_check, name="health-check"),
]

# Add format suffix patterns for content negotiation (.json, .xml, etc.)
# urlpatterns = format_suffix_patterns(urlpatterns)

"""
CORRECTED URL STRUCTURE for Tenants App:

Since the API app already provides /api/v1/ and includes tenants URLs with:
path('tenant/', include('apps.shared.tenants.urls'))

Your final URLs will be:

1. Tenant Self-Management (via /api/v1/tenant/):
   # Function-based views
   GET  /api/v1/tenant/my-tenants/                # List own tenants (function view)
   POST /api/v1/tenant/create/                    # Create new tenant (function view)
   POST /api/v1/tenant/check-subdomain/           # Check subdomain availability (function view)
   
   # ViewSet-based endpoints  
   GET  /api/v1/tenant/tenant-management/         # List tenants (viewset)
   GET  /api/v1/tenant/tenant-management/{id}/    # Get tenant details (viewset)
   PUT  /api/v1/tenant/tenant-management/{id}/    # Update tenant (viewset)
   
   GET  /api/v1/tenant/current/                   # Get current tenant info
   POST /api/v1/tenant/{id}/branding/             # Update branding
   POST /api/v1/tenant/{id}/feature/              # Toggle features
   
   GET  /api/v1/tenant/invitations/               # List invitations (from router)
   POST /api/v1/tenant/invitations/               # Create invitation (from router)
   POST /api/v1/tenant/invitations/{id}/reminder/ # Send reminder
   POST /api/v1/tenant/invitations/{id}/revoke/   # Revoke invitation
   
   GET  /api/v1/tenant/settings/                  # List settings (from router)
   POST /api/v1/tenant/settings/                  # Create setting (from router)
   GET  /api/v1/tenant/settings/by-category/      # Group by category

2. Platform Admin URLs should be defined in main project urls.py:
   GET  /api/platform/tenants/                    # List all tenants
   POST /api/platform/tenants/                    # Create new tenant
   GET  /api/platform/statistics/                # Platform stats

3. Public URLs should be defined in main project urls.py:
   GET  /api/public/tenant/{subdomain}/           # Public tenant info
   GET  /api/public/invitation/{token}/           # Invitation details
   POST /api/public/invitation/accept/            # Accept invitation

Key Changes:
1. Removed all /api/v1/ and /api/platform/ prefixes from tenant app URLs
2. Only kept tenant-specific URLs that will be accessed via /api/v1/tenant/
3. Moved platform admin and public URLs to separate patterns for main project
4. Router now provides clean CRUD operations under the tenant prefix

Usage in your project:
- Include only the main urlpatterns in the tenant app URLs
- Add platform_urlpatterns to main project urls.py under 'api/platform/'
- Add public_urlpatterns to main project urls.py under 'api/public/'
"""