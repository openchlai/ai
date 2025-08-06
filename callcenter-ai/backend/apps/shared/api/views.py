# apps/shared/api/views.py
"""
API management views for API keys, request logs, and system monitoring.
These views are used for managing the API infrastructure itself.
"""

import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import APIKey, APIRequestLog, APIKeyUsageStats
from .authentication import (
    APIKeyAuthentication, 
    TenantAPIKeyAuthentication, 
    PlatformAPIKeyAuthentication,
    APIRequestLoggingMixin,
    APIKeyPermissionMixin
)
# from .serializers import (  # These will be created next
#     APIKeySerializer, 
#     APIRequestLogSerializer, 
#     CreateAPIKeySerializer,
#     APIKeyUsageStatsSerializer
# )


class HealthCheckView(APIView):
    """
    System health check endpoint.
    No authentication required - used for load balancer health checks.
    """
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        """Return system health status."""
        try:
            # Basic database connectivity check
            api_key_count = APIKey.objects.count()
            
            # Check if we can write to database
            now = timezone.now()
            
            health_data = {
                'status': 'healthy',
                'timestamp': now.isoformat(),
                'version': getattr(settings, 'API_VERSION', '1.0.0'),
                'checks': {
                    'database': 'ok',
                    'api_keys_count': api_key_count,
                }
            }
            
            return JsonResponse(health_data)
            
        except Exception as e:
            return JsonResponse({
                'status': 'unhealthy',
                'timestamp': timezone.now().isoformat(),
                'error': str(e),
                'checks': {
                    'database': 'error'
                }
            }, status=500)


class APIKeyViewSet(APIRequestLoggingMixin, APIKeyPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing API keys within a tenant.
    
    Allows tenant users to create, view, and manage their organization's API keys.
    Requires tenant-scoped authentication.
    """
    # serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TenantAPIKeyAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'last_used_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return API keys for the current tenant only."""
        # Get tenant from the authenticated API key
        tenant = self.get_api_tenant()
        if not tenant:
            return APIKey.objects.none()
        
        # Only return active (non-deleted) keys for this tenant
        return APIKey.objects.filter(tenant=tenant)
    
    def perform_create(self, serializer):
        """Create API key with proper tenant and user context."""
        self.check_api_permission('admin.api_keys')
        
        tenant = self.get_api_tenant()
        api_key = serializer.save(
            tenant=tenant,
            created_by=self.request.user,
            updated_by=self.request.user
        )
        
        # Store the raw key in the response (only time it's available)
        self.raw_key = getattr(serializer, 'raw_key', None)
    
    def create(self, request, *args, **kwargs):
        """Override create to return the raw API key."""
        response = super().create(request, *args, **kwargs)
        
        # Add the raw key to the response if available
        if hasattr(self, 'raw_key') and self.raw_key:
            response.data['raw_key'] = self.raw_key
            response.data['warning'] = 'Save this key - you will not be able to see it again!'
        
        return response
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate an API key (creates new key value)."""
        self.check_api_permission('admin.api_keys')
        
        api_key = self.get_object()
        
        # Create new key value
        new_api_key, raw_key = APIKey.objects.create_api_key(
            name=api_key.name,
            tenant=api_key.tenant,
            user=request.user,
            permissions=api_key.permissions,
            rate_limit=api_key.rate_limit
        )
        
        # Soft delete the old key
        api_key.soft_delete(user=request.user)
        
        # Return the new key data
        # serializer = self.get_serializer(new_api_key)
        return Response({
            # **serializer.data,
            'id': str(new_api_key.id),
            'name': new_api_key.name,
            'raw_key': raw_key,
            'warning': 'Save this key - you will not be able to see it again!'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an API key."""
        self.check_api_permission('admin.api_keys')
        
        api_key = self.get_object()
        api_key.is_active = False
        api_key.updated_by = request.user
        api_key.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        
        return Response({'status': 'deactivated'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an API key."""
        self.check_api_permission('admin.api_keys')
        
        api_key = self.get_object()
        api_key.is_active = True
        api_key.updated_by = request.user
        api_key.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Get usage statistics for this API key."""
        api_key = self.get_object()
        
        # Get recent usage stats
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        stats = APIKeyUsageStats.objects.filter(
            api_key=api_key,
            date__gte=thirty_days_ago
        ).order_by('-date')
        
        # Calculate summary statistics
        recent_logs = APIRequestLog.objects.filter(
            api_key=api_key,
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        summary = {
            'total_requests_30d': recent_logs.count(),
            'successful_requests_30d': recent_logs.filter(status_code__lt=400).count(),
            'error_requests_30d': recent_logs.filter(status_code__gte=400).count(),
            'current_rate_limit': api_key.rate_limit,
            'current_usage': api_key.current_usage,
            'usage_percentage': api_key.get_usage_percentage(),
            'last_used': api_key.last_used_at,
        }
        
        return Response({
            'summary': summary,
            # 'daily_stats': APIKeyUsageStatsSerializer(stats, many=True).data
        })


class APIRequestLogViewSet(APIRequestLoggingMixin, APIKeyPermissionMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing API request logs within a tenant.
    
    Provides read-only access to API request history for monitoring and debugging.
    """
    # serializer_class = APIRequestLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TenantAPIKeyAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['method', 'status_code', 'api_key']
    search_fields = ['endpoint', 'ip_address', 'user_agent']
    ordering_fields = ['timestamp', 'response_time', 'status_code']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Return API logs for the current tenant only."""
        tenant = self.get_api_tenant()
        if not tenant:
            return APIRequestLog.objects.none()
        
        # Return logs for this tenant, with some reasonable time limit
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return APIRequestLog.objects.filter(
            tenant=tenant,
            timestamp__gte=thirty_days_ago
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get aggregated statistics for API usage."""
        self.check_api_permission('admin.analytics')
        
        queryset = self.get_queryset()
        
        # Time-based filters
        time_filter = request.GET.get('period', '7d')
        if time_filter == '1d':
            since = timezone.now() - timedelta(days=1)
        elif time_filter == '7d':
            since = timezone.now() - timedelta(days=7)
        elif time_filter == '30d':
            since = timezone.now() - timedelta(days=30)
        else:
            since = timezone.now() - timedelta(days=7)
        
        filtered_logs = queryset.filter(timestamp__gte=since)
        
        # Calculate statistics
        stats = {
            'total_requests': filtered_logs.count(),
            'successful_requests': filtered_logs.filter(status_code__lt=400).count(),
            'client_errors': filtered_logs.filter(status_code__range=[400, 499]).count(),
            'server_errors': filtered_logs.filter(status_code__range=[500, 599]).count(),
            'avg_response_time': filtered_logs.aggregate(
                avg_time=Avg('response_time')
            )['avg_time'],
            'top_endpoints': list(
                filtered_logs.values('endpoint')
                .annotate(count=Count('endpoint'))
                .order_by('-count')[:10]
            ),
            'requests_by_method': list(
                filtered_logs.values('method')
                .annotate(count=Count('method'))
                .order_by('-count')
            ),
            'error_breakdown': list(
                filtered_logs.filter(status_code__gte=400)
                .values('status_code')
                .annotate(count=Count('status_code'))
                .order_by('-count')
            )
        }
        
        return Response(stats)


class APIDocumentationView(APIView):
    """
    API documentation endpoint.
    Returns OpenAPI/Swagger schema information.
    """
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        """Return API documentation."""
        # This would integrate with DRF's schema generation
        # For now, return basic documentation structure
        
        documentation = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Murima API',
                'version': getattr(settings, 'API_VERSION', '1.0.0'),
                'description': 'Comprehensive case management and communication platform API'
            },
            'servers': [
                {
                    'url': request.build_absolute_uri('/api/v1/'),
                    'description': 'Current API version'
                }
            ],
            'paths': {
                '/auth/': {'description': 'Authentication endpoints'},
                '/cases/': {'description': 'Case management'},
                '/communications/': {'description': 'Omnichannel communications'},
                '/calls/': {'description': 'Call center operations'},
                '/contacts/': {'description': 'Contact and CRM management'},
                '/workflows/': {'description': 'Workflow automation'},
                '/reference-data/': {'description': 'Lookup data and references'},
                '/documents/': {'description': 'Document management'},
                '/tasks/': {'description': 'Task management'},
                '/notifications/': {'description': 'Notification system'},
                '/ai-services/': {'description': 'AI integration services'},
            },
            'components': {
                'securitySchemes': {
                    'ApiKeyAuth': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'Authorization',
                        'description': 'API key authentication. Format: "ApiKey your-key-here"'
                    },
                    'ApiKeyHeader': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-API-Key',
                        'description': 'Alternative API key header'
                    }
                }
            }
        }
        
        return Response(documentation)


class APISchemaView(APIView):
    """
    API schema endpoint for programmatic access.
    Returns machine-readable API schema.
    """
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        """Return API schema in OpenAPI format."""
        # This would integrate with DRF's automatic schema generation
        # For now, return a basic schema
        
        schema = {
            'swagger': '2.0',
            'info': {
                'title': 'Murima API',
                'version': getattr(settings, 'API_VERSION', '1.0.0')
            },
            'host': request.get_host(),
            'schemes': ['https' if request.is_secure() else 'http'],
            'basePath': '/api/v1',
            'produces': ['application/json'],
            'consumes': ['application/json'],
            'securityDefinitions': {
                'ApiKey': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header'
                }
            }
        }
        
        return Response(schema)


# Platform-level views (for platform admin API keys)
class PlatformHealthView(APIView):
    """
    Platform-wide health monitoring.
    Requires platform-level API key.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [PlatformAPIKeyAuthentication]
    
    def get(self, request):
        """Return platform health metrics."""
        try:
            # System-wide metrics
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'database': {
                    'status': 'ok',
                    'total_api_keys': APIKey.objects.count(),
                    'active_api_keys': APIKey.objects.filter(is_active=True).count(),
                },
                'api_usage': {
                    'requests_last_hour': APIRequestLog.objects.filter(
                        timestamp__gte=timezone.now() - timedelta(hours=1)
                    ).count(),
                    'requests_last_24h': APIRequestLog.objects.filter(
                        timestamp__gte=timezone.now() - timedelta(hours=24)
                    ).count(),
                },
                'performance': {
                    'avg_response_time_1h': APIRequestLog.objects.filter(
                        timestamp__gte=timezone.now() - timedelta(hours=1)
                    ).aggregate(avg_time=Avg('response_time'))['avg_time']
                }
            }
            
            return Response(metrics)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=500)


class TenantAPIUsageView(ListAPIView):
    """
    Cross-tenant API usage analytics.
    Requires platform-level API key.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [PlatformAPIKeyAuthentication]
    
    def get(self, request):
        """Return usage statistics across all tenants."""
        # Get time period from query params
        period = request.GET.get('period', '7d')
        if period == '1d':
            since = timezone.now() - timedelta(days=1)
        elif period == '30d':
            since = timezone.now() - timedelta(days=30)
        else:
            since = timezone.now() - timedelta(days=7)
        
        # Aggregate usage by tenant
        usage_by_tenant = (
            APIRequestLog.objects
            .filter(timestamp__gte=since)
            .values('tenant__name', 'tenant__id')
            .annotate(
                total_requests=Count('id'),
                successful_requests=Count('id', filter=Q(status_code__lt=400)),
                error_requests=Count('id', filter=Q(status_code__gte=400)),
                avg_response_time=Avg('response_time')
            )
            .order_by('-total_requests')
        )
        
        return Response({
            'period': period,
            'usage_by_tenant': list(usage_by_tenant),
            'summary': {
                'total_tenants': usage_by_tenant.count(),
                'total_requests': sum(t['total_requests'] for t in usage_by_tenant),
                'total_errors': sum(t['error_requests'] for t in usage_by_tenant),
            }
        })
        
        
        
# Temporarry placeholder for Tenant building


