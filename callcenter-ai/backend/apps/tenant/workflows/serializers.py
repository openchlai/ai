from rest_framework import serializers
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


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']
        read_only_fields = ['app_label', 'model']


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            'id', 'workflow', 'name', 'description', 'order', 'is_final',
            'required_approvals', 'assignment_policy', 'assignment_config',
            'actions', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TransitionSerializer(serializers.ModelSerializer):
    source_stage_name = serializers.CharField(source='source_stage.name', read_only=True)
    target_stage_name = serializers.CharField(source='target_stage.name', read_only=True)

    class Meta:
        model = Transition
        fields = [
            'id', 'source_stage', 'target_stage', 'source_stage_name', 'target_stage_name',
            'name', 'condition', 'actions', 'require_comment', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer()
    stages = StageSerializer(many=True, read_only=True)
    start_stage = StageSerializer(read_only=True)

    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'content_type', 'is_active',
            'start_stage', 'metadata', 'stages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'stages']


class WorkflowTemplateCreateSerializer(serializers.ModelSerializer):
    content_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        source='content_type',
        write_only=True
    )

    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'content_type_id', 'is_active',
            'start_stage', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StageInstanceSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    assignees = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        default=serializers.CreateOnlyDefault([])
    )

    class Meta:
        model = StageInstance
        fields = [
            'id', 'workflow_instance', 'stage', 'stage_name', 'entered_at',
            'exited_at', 'status', 'assignees', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'entered_at', 'exited_at', 'stage_name'
        ]


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    current_stage_name = serializers.CharField(source='current_stage.name', read_only=True)
    content_type = ContentTypeSerializer(read_only=True)
    stage_instances = StageInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'workflow_name', 'content_type', 'object_id',
            'current_stage', 'current_stage_name', 'is_complete', 'metadata',
            'stage_instances', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'workflow_name', 'current_stage_name',
            'stage_instances'
        ]


class TransitionLogSerializer(serializers.ModelSerializer):
    from_stage_name = serializers.CharField(source='from_stage.name', read_only=True)
    to_stage_name = serializers.CharField(source='to_stage.name', read_only=True)
    transition_name = serializers.CharField(source='transition.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = TransitionLog
        fields = [
            'id', 'workflow_instance', 'transition', 'transition_name',
            'from_stage', 'from_stage_name', 'to_stage', 'to_stage_name',
            'performed_by', 'performed_by_name', 'comment', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'transition_name', 'from_stage_name',
            'to_stage_name', 'performed_by_name'
        ]


class SLASerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)

    class Meta:
        model = SLA
        fields = [
            'id', 'stage', 'stage_name', 'name', 'duration_hours',
            'business_hours_only', 'escalation_path', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'stage_name']


class EscalationSerializer(serializers.ModelSerializer):
    sla_name = serializers.CharField(source='sla.name', read_only=True)

    class Meta:
        model = Escalation
        fields = [
            'id', 'stage_instance', 'sla', 'sla_name', 'escalated_at',
            'resolved_at', 'actions_taken', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sla_name', 'escalated_at']


class WorkflowDetailSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)
    transitions = TransitionSerializer(many=True, read_only=True)
    slas = SLASerializer(many=True, read_only=True)
    content_type = ContentTypeSerializer(read_only=True)

    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'content_type', 'is_active',
            'start_stage', 'metadata', 'stages', 'transitions', 'slas',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StageDetailSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    transitions_out = TransitionSerializer(many=True, read_only=True)
    transitions_in = TransitionSerializer(many=True, read_only=True)
    slas = SLASerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = [
            'id', 'workflow', 'workflow_name', 'name', 'description', 'order',
            'is_final', 'required_approvals', 'assignment_policy',
            'assignment_config', 'actions', 'metadata', 'transitions_out',
            'transitions_in', 'slas', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'workflow_name', 'transitions_out',
            'transitions_in', 'slas'
        ]