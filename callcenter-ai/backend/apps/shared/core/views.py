from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from core.models import BaseModel, AuditLog
from core.serializers import (
    BaseModelSerializer,
    AuditLogSerializer,
    AuditLogFilterSerializer,
    SuccessSerializer,
    ErrorSerializer
)
from core.utils import log_action
from django.http import HttpRequest

User = get_user_model()

class BaseCreateAPIView(generics.CreateAPIView):
    """
    Base create view with audit logging
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        log_action('CREATE', self.request, obj=instance)
        return instance

class BaseRetrieveAPIView(generics.RetrieveAPIView):
    """
    Base retrieve view with audit logging
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action('READ', request, obj=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BaseUpdateAPIView(generics.UpdateAPIView):
    """
    Base update view with audit logging
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user)
        log_action('UPDATE', self.request, obj=instance)
        return instance

class BaseDestroyAPIView(generics.DestroyAPIView):
    """
    Base delete view with soft delete and audit logging
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        instance.delete(user=self.request.user)
        log_action('DELETE', self.request, obj=instance)
        return instance

class BaseListAPIView(generics.ListAPIView):
    """
    Base list view with pagination and filtering
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Set your preferred pagination class
    
    def filter_queryset(self, queryset):
        """
        Add any base filtering logic here
        """
        return super().filter_queryset(queryset)

class BaseModelViewSet(
    BaseCreateAPIView,
    BaseRetrieveAPIView,
    BaseUpdateAPIView,
    BaseDestroyAPIView,
    BaseListAPIView
):
    """
    Complete CRUD viewset for models inheriting from BaseModel
    """
    def get_queryset(self):
        if getattr(self.queryset, 'filter_by_tenant', None):
            return self.queryset.filter_by_tenant(self.request)
        return super().get_queryset().filter(is_deleted=False)


class AuditLogListView(generics.ListAPIView):
    """
    View for listing and filtering audit logs
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = AuditLog.objects.all().order_by('-timestamp')
    
    def get_serializer_class(self):
        if self.request.query_params.get('minimal'):
            return AuditLogListSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter_serializer = AuditLogFilterSerializer(data=self.request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        if filters.get('user'):
            queryset = queryset.filter(user=filters['user'])
        if filters.get('action'):
            queryset = queryset.filter(action=filters['action'])
        if filters.get('object_type'):
            queryset = queryset.filter(object_type=filters['object_type'])
        if filters.get('object_id'):
            queryset = queryset.filter(object_id=filters['object_id'])
        if filters.get('date_from'):
            queryset = queryset.filter(timestamp__gte=filters['date_from'])
        if filters.get('date_to'):
            queryset = queryset.filter(timestamp__lte=filters['date_to'])
        
        return queryset

class AuditLogDetailView(generics.RetrieveAPIView):
    """
    View for retrieving single audit log entry
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = AuditLog.objects.all()
    lookup_field = 'id'
    

class HealthCheckView(generics.GenericAPIView):
    """
    Basic health check endpoint
    """
    serializer_class = EmptySerializer
    
    def get(self, request):
        return Response({
            "status": "ok",
            "timestamp": timezone.now().isoformat()
        })

class SuccessMessageView(generics.GenericAPIView):
    """
    Standardized success response
    """
    serializer_class = SuccessSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)