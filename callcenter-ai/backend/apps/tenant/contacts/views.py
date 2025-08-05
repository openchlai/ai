from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import (
    Contact, ContactType, ContactTag, ContactGroup,
    ContactContactType, ContactTagAssignment, ContactInteraction
)
from .serializers import (
    ContactSerializer, ContactListSerializer,
    ContactTypeSerializer, ContactTagSerializer,
    ContactGroupSerializer, ContactInteractionSerializer,
    ContactContactTypeSerializer, ContactTagAssignmentSerializer
)
from apps.shared.core.permissions import IsTenantUser, IsTenantAdmin
from apps.shared.core.pagination import StandardResultsSetPagination

User = get_user_model()

class ContactTypeListCreateView(generics.ListCreateAPIView):
    queryset = ContactType.objects.all()
    serializer_class = ContactTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

class ContactTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactType.objects.all()
    serializer_class = ContactTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

class ContactTagListCreateView(generics.ListCreateAPIView):
    queryset = ContactTag.objects.all()
    serializer_class = ContactTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

class ContactTagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactTag.objects.all()
    serializer_class = ContactTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

class ContactGroupListCreateView(generics.ListCreateAPIView):
    queryset = ContactGroup.objects.all()
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)

class ContactGroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactGroup.objects.all()
    serializer_class = ContactGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant)

class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'is_active': ['exact'],
        'types__id': ['exact'],
        'tags__id': ['exact'],
        'groups__id': ['exact'],
        'created_at': ['gte', 'lte', 'exact'],
    }
    search_fields = [
        'first_name', 'last_name', 'email', 'phone', 'mobile',
        'organization', 'job_title', 'notes'
    ]
    ordering_fields = ['last_name', 'first_name', 'organization', 'created_at']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ContactListSerializer
        return ContactSerializer

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant).select_related(
            'created_by', 'last_modified_by'
        ).prefetch_related(
            'types', 'tags', 'groups'
        )

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)

class ContactRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.tenant).select_related(
            'created_by', 'last_modified_by'
        ).prefetch_related(
            'types', 'tags', 'groups'
        )

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)

class ContactInteractionListCreateView(generics.ListCreateAPIView):
    queryset = ContactInteraction.objects.all()
    serializer_class = ContactInteractionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'contact__id': ['exact'],
        'interaction_type': ['exact'],
        'date': ['gte', 'lte', 'exact'],
    }
    search_fields = ['subject', 'notes']
    ordering_fields = ['date', 'created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(
            contact__tenant=self.request.tenant
        ).select_related(
            'contact', 'related_case', 'related_task', 'created_by'
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ContactInteractionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactInteraction.objects.all()
    serializer_class = ContactInteractionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    lookup_field = 'pk'

    def get_queryset(self):
        return self.queryset.filter(
            contact__tenant=self.request.tenant
        ).select_related(
            'contact', 'related_case', 'related_task', 'created_by'
        )

class ContactContactTypeListCreateView(generics.ListCreateAPIView):
    queryset = ContactContactType.objects.all()
    serializer_class = ContactContactTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'contact__id': ['exact'],
        'contact_type__id': ['exact'],
    }
    ordering_fields = ['assigned_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(
            contact__tenant=self.request.tenant,
            contact_type__tenant=self.request.tenant
        ).select_related('contact', 'contact_type', 'assigned_by')

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

class ContactTagAssignmentListCreateView(generics.ListCreateAPIView):
    queryset = ContactTagAssignment.objects.all()
    serializer_class = ContactTagAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'contact__id': ['exact'],
        'tag__id': ['exact'],
    }
    ordering_fields = ['assigned_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(
            contact__tenant=self.request.tenant,
            tag__tenant=self.request.tenant
        ).select_related('contact', 'tag', 'assigned_by')

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)