from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Case, CaseDocument, CaseNote, 
    ProtectionDetail, SafetyPlan,
    CaseType, CaseStatus
)
from .serializers import (
    CaseSerializer, CaseDocumentSerializer,
    CaseNoteSerializer, CaseStatusUpdateSerializer,
    ProtectionDetailSerializer, SafetyPlanSerializer,
    CaseBulkUpdateSerializer, CaseTypeSerializer,
    CaseStatusSerializer
)
from .filters import CaseFilter
from .permissions import (
    CaseAccessPermission, ProtectionCasePermission,
    DocumentAccessPermission
)

# ========== CASE TYPE & STATUS VIEWS ==========
class CaseTypeListAPIView(generics.ListAPIView):
    queryset = CaseType.objects.all()
    serializer_class = CaseTypeSerializer
    permission_classes = [IsAuthenticated]

class CaseStatusListAPIView(generics.ListAPIView):
    queryset = CaseStatus.objects.all()
    serializer_class = CaseStatusSerializer
    permission_classes = [IsAuthenticated]

# ========== CASE VIEWS ==========
class CaseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Case.objects.select_related('case_type', 'status', 'assigned_to')
    serializer_class = CaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CaseFilter
    permission_classes = [IsAuthenticated, CaseAccessPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('protection_only'):
            queryset = queryset.filter(
                case_type__category__in=['vac', 'gbv']
            )
        return queryset

class CaseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Case.objects.select_related(
        'case_type', 'status', 'assigned_to'
    ).prefetch_related(
        'documents', 'notes', 'history'
    )
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated, CaseAccessPermission]
    lookup_field = 'pk'

# ========== CASE DOCUMENT VIEWS ==========
class CaseDocumentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CaseDocumentSerializer
    permission_classes = [IsAuthenticated, DocumentAccessPermission]

    def get_queryset(self):
        return CaseDocument.objects.filter(
            case_id=self.kwargs.get('case_id')
        ).select_related('uploaded_by')

    def perform_create(self, serializer):
        serializer.save(
            uploaded_by=self.request.user,
            case_id=self.kwargs.get('case_id'),
            file_type=serializer.validated_data['file'].name.split('.')[-1],
            file_size=serializer.validated_data['file'].size
        )

class CaseDocumentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaseDocumentSerializer
    permission_classes = [IsAuthenticated, DocumentAccessPermission]
    lookup_field = 'pk'

    def get_queryset(self):
        return CaseDocument.objects.filter(
            case_id=self.kwargs.get('case_id')
        )

# ========== CASE NOTE VIEWS ==========
class CaseNoteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CaseNoteSerializer
    permission_classes = [IsAuthenticated, CaseAccessPermission]

    def get_queryset(self):
        queryset = CaseNote.objects.filter(
            case_id=self.kwargs.get('case_id')
        ).select_related('created_by')
        
        if not self.request.user.has_perm('cases.view_internal_notes'):
            queryset = queryset.filter(is_internal=False)
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            case_id=self.kwargs.get('case_id')
        )

class CaseNoteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaseNoteSerializer
    permission_classes = [IsAuthenticated, CaseAccessPermission]
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = CaseNote.objects.filter(
            case_id=self.kwargs.get('case_id')
        )
        if not self.request.user.has_perm('cases.view_internal_notes'):
            queryset = queryset.filter(is_internal=False)
        return queryset

# ========== PROTECTION CASE VIEWS ==========
class ProtectionDetailRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProtectionDetailSerializer
    permission_classes = [IsAuthenticated, ProtectionCasePermission]

    def get_object(self):
        case = generics.get_object_or_404(
            Case.objects.filter(pk=self.kwargs['case_id'])
        )
        if not hasattr(case, 'protection_details'):
            raise generics.NotFound("Not a protection case")
        return case.protection_details

class SafetyPlanRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = SafetyPlanSerializer
    permission_classes = [IsAuthenticated, ProtectionCasePermission]

    def get_object(self):
        case = generics.get_object_or_404(
            Case.objects.filter(pk=self.kwargs['case_id'])
        )
        if not hasattr(case, 'protection_details'):
            raise generics.NotFound("Not a protection case")
        if not hasattr(case, 'safety_plan'):
            return SafetyPlan.objects.create(case=case)
        return case.safety_plan

# ========== CASE WORKFLOW VIEWS ==========
class CaseStatusUpdateAPIView(generics.GenericAPIView):
    serializer_class = CaseStatusUpdateSerializer
    permission_classes = [IsAuthenticated, CaseAccessPermission]

    def post(self, request, *args, **kwargs):
        case = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'case': case, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status_id']
        case.update_status(
            new_status=new_status,
            changed_by=request.user,
            comment=serializer.validated_data.get('comment')
        )
        
        return Response(
            CaseSerializer(case).data,
            status=status.HTTP_200_OK
        )

    def get_object(self):
        return generics.get_object_or_404(
            Case.objects.all(),
            pk=self.kwargs['case_id']
        )

class CaseBulkUpdateAPIView(generics.GenericAPIView):
    serializer_class = CaseBulkUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cases = Case.objects.filter(
            id__in=serializer.validated_data['case_ids']
        )
        updates = {}
        
        if 'priority' in serializer.validated_data:
            updates['priority'] = serializer.validated_data['priority']
        if 'assigned_to_id' in serializer.validated_data:
            updates['assigned_to'] = serializer.validated_data['assigned_to_id']
        
        cases.update(**updates)
        return Response(
            {"updated_count": cases.count()},
            status=status.HTTP_200_OK
        )