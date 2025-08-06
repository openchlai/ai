# apps/shared/api/urls.py
"""
Main API URL configuration.
Provides centralized routing for all API versions and platform endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API management router (for API keys, logs, etc.)
api_management_router = DefaultRouter()
api_management_router.register(r'keys', views.APIKeyViewSet, basename='apikey')
api_management_router.register(r'logs', views.APIRequestLogViewSet, basename='apirequestlog')

app_name = 'api'

urlpatterns = [
    # Health check endpoint (no authentication required)
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    
    # API versioning - current version
    path('v1/', include('apps.shared.api.v1.urls')),
    
    # Future versions can be added here
    # path('v2/', include('apps.shared.api.v2.urls')),
    
    # Platform administration endpoints (platform-level API keys only)
    path('/platform/', include('apps.shared.api.platform.urls')),
    
    # API management endpoints (tenant-scoped)
    path('management/', include(api_management_router.urls)),
    
    # API documentation endpoints
    path('docs/', views.APIDocumentationView.as_view(), name='api-docs'),
    path('schema/', views.APISchemaView.as_view(), name='api-schema'),
    
    # Tenant management endpoints
    path('tenants/', include('apps.shared.tenants.urls')),   
  
]



# ============================================================================
# Example: How tenant apps should structure their API URLs

"""
# apps/tenant/cases/urls.py - Example implementation

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

# Create router for this app
router = DefaultRouter()
router.register(r'', views.CaseViewSet, basename='case')  # Base cases endpoint
router.register(r'categories', views.CaseCategoryViewSet, basename='case-category')

app_name = 'cases'

# Standard router URLs
urlpatterns = router.urls

# Add custom endpoints
urlpatterns += [
    # Case-specific actions
    path('<uuid:pk>/assign/', views.AssignCaseView.as_view(), name='assign-case'),
    path('<uuid:pk>/transfer/', views.TransferCaseView.as_view(), name='transfer-case'),
    path('<uuid:pk>/history/', views.CaseHistoryView.as_view(), name='case-history'),
    path('<uuid:pk>/comments/', views.CaseCommentsView.as_view(), name='case-comments'),
    path('<uuid:pk>/documents/', views.CaseDocumentsView.as_view(), name='case-documents'),
    
    # Bulk operations
    path('bulk-update/', views.BulkUpdateCasesView.as_view(), name='bulk-update-cases'),
    path('bulk-assign/', views.BulkAssignCasesView.as_view(), name='bulk-assign-cases'),
    path('bulk-delete/', views.BulkDeleteCasesView.as_view(), name='bulk-delete-cases'),
    
    # Search and filtering
    path('search/', views.CaseSearchView.as_view(), name='case-search'),
    path('advanced-search/', views.AdvancedCaseSearchView.as_view(), name='advanced-case-search'),
    
    # Reporting and analytics
    path('stats/', views.CaseStatsView.as_view(), name='case-stats'),
    path('export/', views.ExportCasesView.as_view(), name='export-cases'),
    
    # Workflow integration
    path('<uuid:pk>/workflow/', views.CaseWorkflowView.as_view(), name='case-workflow'),
    path('<uuid:pk>/workflow/transition/', views.CaseWorkflowTransitionView.as_view(), name='case-workflow-transition'),
]

# Final URL structure results in:
# /api/v1/cases/                           - List/create cases
# /api/v1/cases/{id}/                      - Get/update/delete specific case
# /api/v1/cases/{id}/assign/               - Assign case to user
# /api/v1/cases/{id}/history/              - Case history
# /api/v1/cases/categories/                - Case categories
# /api/v1/cases/bulk-update/               - Bulk operations
# /api/v1/cases/search/                    - Search cases
"""

# ============================================================================
# Configuration for main Django project urls.py

"""
# In your main project urls.py, include the API URLs:

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('apps.shared.api.urls')),
    
    # Add other app URLs as needed
    # path('', include('apps.frontend.urls')),  # Frontend app if using Django templates
]

# This results in the following URL structure:
# /api/health/                             - Health check
# /api/v1/auth/                           - Authentication endpoints
# /api/v1/cases/                          - Cases API
# /api/v1/communications/                 - Communications API
# /api/v1/calls/                          - Calls API
# /api/v1/contacts/                       - Contacts API
# /api/platform/tenants/                  - Platform tenant management
# /api/platform/users/                    - Platform user management
# /api/management/keys/                   - API key management
# /api/docs/                              - API documentation
"""