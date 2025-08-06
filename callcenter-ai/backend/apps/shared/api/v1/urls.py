# apps/shared/api/v1/urls.py
"""
API v1 URL configuration.
Includes URLs from all tenant apps with consistent routing patterns.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import routers from tenant apps (these will be created in each app)
# from apps.tenant.cases.urls import router as cases_router
# from apps.tenant.communications.urls import router as communications_router
# from apps.tenant.calls.urls import router as calls_router
# from apps.tenant.contacts.urls import router as contacts_router
# from apps.tenant.workflows.urls import router as workflows_router
# from apps.tenant.reference_data.urls import router as reference_data_router
# from apps.tenant.documents.urls import router as documents_router
# from apps.tenant.tasks.urls import router as tasks_router
# from apps.tenant.notifications.urls import router as notifications_router
# from apps.tenant.ai_services.urls import router as ai_services_router

# Import authentication URLs from accounts app
# from apps.shared.accounts.urls import urlpatterns as auth_urls

app_name = 'v1'

urlpatterns = [
    # Authentication endpoints (shared app)
    path('auth/', include('apps.shared.accounts.urls')),
    
    # Tenant app endpoints
    # Note: These imports will be uncommented as each app is implemented
    path('tenant/', include('apps.shared.tenants.urls')),
    
    # Cases management
    path('cases/', include('apps.tenant.cases.urls')),
    
    # Communications (omnichannel)
    # path('communications/', include('apps.tenant.communications.urls')),
    
    # Call center operations
    # path('calls/', include('apps.tenant.calls.urls')),
    
    # CRM and contact management
    path('contacts/', include('apps.tenant.contacts.urls')),
    
    # Workflow management
    path('workflows/', include('apps.tenant.workflows.urls')),
    
    # Reference data and lookups
    path('reference-data/', include('apps.tenant.reference_data.urls')),
    
    # Document management
    path('documents/', include('apps.tenant.documents.urls')),
    
    # Task management
    path('tasks/', include('apps.tenant.tasks.urls')),
    
    # Notifications
    # path('notifications/', include('apps.tenant.notifications.urls')),
    
    # AI services integration
    # path('ai-services/', include('apps.tenant.ai_services.urls')),
]

# Example of how tenant apps should structure their URLs:
"""
# apps/tenant/cases/urls.py
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cases', views.CaseViewSet, basename='case')
router.register(r'categories', views.CaseCategoryViewSet, basename='case-category')

app_name = 'cases'
urlpatterns = router.urls

# Additional custom endpoints can be added:
urlpatterns += [
    path('cases/<uuid:pk>/assign/', views.AssignCaseView.as_view(), name='assign-case'),
    path('cases/<uuid:pk>/history/', views.CaseHistoryView.as_view(), name='case-history'),
    path('cases/bulk-update/', views.BulkUpdateCasesView.as_view(), name='bulk-update-cases'),
]
"""
