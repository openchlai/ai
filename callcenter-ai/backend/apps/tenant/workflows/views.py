from rest_framework import generics, permissions
from django.contrib.contenttypes.models import ContentType
from .models import (
    WorkflowTemplate,
    Stage,
    Transition,
    WorkflowInstance,
    StageInstance,
    TransitionLog,
    SLA,
    Escalation
)
from .serializers import (
    WorkflowTemplateSerializer,
    WorkflowTemplateCreateSerializer,
    WorkflowDetailSerializer,
    StageSerializer,
    StageDetailSerializer,
    TransitionSerializer,
    WorkflowInstanceSerializer,
    StageInstanceSerializer,
    TransitionLogSerializer,
    SLASerializer,
    EscalationSerializer,
    ContentTypeSerializer
)


class ContentTypeListView(generics.ListAPIView):
    """
    List all content types that can have workflows attached
    """
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class WorkflowTemplateListCreateView(generics.ListCreateAPIView):
    """
    List all workflow templates or create a new one
    """
    queryset = WorkflowTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowTemplateCreateSerializer
        return WorkflowTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WorkflowTemplateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a workflow template
    """
    queryset = WorkflowTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WorkflowDetailSerializer
        return WorkflowTemplateSerializer


class StageListCreateView(generics.ListCreateAPIView):
    """
    List all stages or create a new one for a specific workflow
    """
    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return Stage.objects.filter(workflow_id=workflow_id)

    def perform_create(self, serializer):
        workflow_id = self.kwargs.get('workflow_id')
        serializer.save(workflow_id=workflow_id, created_by=self.request.user)


class StageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a stage
    """
    serializer_class = StageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return Stage.objects.filter(workflow_id=workflow_id)


class TransitionListCreateView(generics.ListCreateAPIView):
    """
    List all transitions or create a new one between stages
    """
    serializer_class = TransitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return Transition.objects.filter(
            source_stage__workflow_id=workflow_id
        ).select_related('source_stage', 'target_stage')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TransitionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a transition
    """
    serializer_class = TransitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_id = self.kwargs.get('workflow_id')
        return Transition.objects.filter(
            source_stage__workflow_id=workflow_id
        ).select_related('source_stage', 'target_stage')


class WorkflowInstanceListCreateView(generics.ListCreateAPIView):
    """
    List all workflow instances or create a new one
    """
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by content type if provided
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        queryset = WorkflowInstance.objects.select_related(
            'workflow', 'current_stage', 'content_type'
        ).prefetch_related('stage_instances')
        
        if content_type and object_id:
            queryset = queryset.filter(
                content_type_id=content_type,
                object_id=object_id
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WorkflowInstanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a workflow instance
    """
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WorkflowInstance.objects.select_related(
        'workflow', 'current_stage', 'content_type'
    ).prefetch_related('stage_instances')


class StageInstanceListCreateView(generics.ListCreateAPIView):
    """
    List all stage instances or create a new one for a workflow instance
    """
    serializer_class = StageInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_instance_id = self.kwargs.get('workflow_instance_id')
        return StageInstance.objects.filter(
            workflow_instance_id=workflow_instance_id
        ).select_related('stage')

    def perform_create(self, serializer):
        workflow_instance_id = self.kwargs.get('workflow_instance_id')
        serializer.save(
            workflow_instance_id=workflow_instance_id,
            created_by=self.request.user
        )


class StageInstanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a stage instance
    """
    serializer_class = StageInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_instance_id = self.kwargs.get('workflow_instance_id')
        return StageInstance.objects.filter(
            workflow_instance_id=workflow_instance_id
        ).select_related('stage')


class TransitionLogListView(generics.ListAPIView):
    """
    List all transition logs for a workflow instance
    """
    serializer_class = TransitionLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workflow_instance_id = self.kwargs.get('workflow_instance_id')
        return TransitionLog.objects.filter(
            workflow_instance_id=workflow_instance_id
        ).select_related(
            'transition', 'from_stage', 'to_stage', 'performed_by'
        ).order_by('-created_at')


class SLAListCreateView(generics.ListCreateAPIView):
    """
    List all SLAs or create a new one for a stage
    """
    serializer_class = SLASerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        stage_id = self.kwargs.get('stage_id')
        return SLA.objects.filter(stage_id=stage_id)

    def perform_create(self, serializer):
        stage_id = self.kwargs.get('stage_id')
        serializer.save(stage_id=stage_id, created_by=self.request.user)


class SLARetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an SLA
    """
    serializer_class = SLASerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        stage_id = self.kwargs.get('stage_id')
        return SLA.objects.filter(stage_id=stage_id)


class EscalationListCreateView(generics.ListCreateAPIView):
    """
    List all escalations or create a new one for a stage instance
    """
    serializer_class = EscalationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        stage_instance_id = self.kwargs.get('stage_instance_id')
        return Escalation.objects.filter(
            stage_instance_id=stage_instance_id
        ).select_related('sla').order_by('-escalated_at')

    def perform_create(self, serializer):
        stage_instance_id = self.kwargs.get('stage_instance_id')
        serializer.save(
            stage_instance_id=stage_instance_id,
            created_by=self.request.user
        )


class EscalationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an escalation
    """
    serializer_class = EscalationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        stage_instance_id = self.kwargs.get('stage_instance_id')
        return Escalation.objects.filter(stage_instance_id=stage_instance_id)