from django.urls import path, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

from core.views import (
    AuditLogListView,
    AuditLogDetailView,
    HealthCheckView,
    SuccessMessageView,
    ExampleModelViewSet  # Replace with your actual viewset
)

# Create a router for ViewSets
router = routers.DefaultRouter()
router.register(r'example-models', ExampleModelViewSet, basename='examplemodel')  # Replace with your actual model

# Schema View for OpenAPI documentation
schema_view = get_schema_view(
    title="Core API",
    description="API for core platform functionality",
    version="1.0.0",
    public=True,
)

urlpatterns = [
    # API Documentation
    path('schema/', schema_view, name='openapi-schema'),
    path('docs/', include_docs_urls(
        title='Core API Documentation',
        description='Comprehensive documentation for Core API endpoints'
    )),
    
    # Health Check
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # Standardized Responses
    path('success/', SuccessMessageView.as_view(), name='success-message'),
    
    # Audit Logs
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),
    path('audit-logs/<uuid:pk>/', AuditLogDetailView.as_view(), name='audit-log-detail'),
    
    # Router URLs (for ViewSets)
    path('', include(router.urls)),
    
    # Auth URLs (if not using django-rest-framework's built-in)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Conditional debug routes
try:
    from django.conf import settings
    if settings.DEBUG:
        from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
        urlpatterns += [
            path('schema/spec/', SpectacularAPIView.as_view(), name='schema'),
            path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),
                 name='swagger-ui'),
        ]
except ImportError:
    pass