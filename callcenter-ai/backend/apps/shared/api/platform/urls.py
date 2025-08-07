# apps/shared/api/platform/urls.py
"""
Platform administration API URLs.
These endpoints require platform-level API keys and are used for cross-tenant operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import platform admin views (these will be created)
# from apps.shared.tenants.views import TenantManagementViewSet
# from apps.shared.accounts.views import PlatformUserManagementViewSet
# from . import views as platform_views

# Platform administration router
platform_router = DefaultRouter()
# platform_router.register(r'tenants', TenantManagementViewSet, basename='platform-tenant')
# platform_router.register(r'users', PlatformUserManagementViewSet, basename='platform-user')
# platform_router.register(r'audit-logs', platform_views.PlatformAuditLogViewSet, basename='platform-audit')
# platform_router.register(r'system-config', platform_views.SystemConfigurationViewSet, basename='platform-config')

app_name = 'platform'

urlpatterns = [
    # Platform management endpoints
    path('', include(platform_router.urls)),
    
    # System health and monitoring
    # path('health/', platform_views.SystemHealthView.as_view(), name='system-health'),
    # path('metrics/', platform_views.PlatformMetricsView.as_view(), name='platform-metrics'),
    # path('usage/', platform_views.TenantUsageStatsView.as_view(), name='tenant-usage'),
    
    # Platform configuration management
    # path('config/', include([
    #     path('', platform_views.SystemConfigurationListView.as_view(), name='config-list'),
    #     path('<str:key>/', platform_views.SystemConfigurationDetailView.as_view(), name='config-detail'),
    #     path('bulk-update/', platform_views.BulkConfigurationUpdateView.as_view(), name='config-bulk-update'),
    # ])),
    
    # Cross-tenant analytics and reporting
    # path('analytics/', include([
    #     path('usage/', platform_views.CrossTenantUsageView.as_view(), name='cross-tenant-usage'),
    #     path('performance/', platform_views.PerformanceMetricsView.as_view(), name='performance-metrics'),
    #     path('security/', platform_views.SecurityReportView.as_view(), name='security-report'),
    # ])),
    
    # API key management for platform admins
    # path('api-keys/', include([
    #     path('', platform_views.PlatformAPIKeyListView.as_view(), name='platform-api-keys'),
    #     path('create/', platform_views.CreatePlatformAPIKeyView.as_view(), name='create-platform-api-key'),
    #     path('<uuid:pk>/', platform_views.PlatformAPIKeyDetailView.as_view(), name='platform-api-key-detail'),
    # ])),
]
