from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.shared.core.models import BaseModel, AuditLog

class WorkflowTemplate(BaseModel):
    """
    Template for a workflow that can be instantiated for specific objects.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of this workflow template"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this workflow's purpose"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to=models.Q(app_label='cases') | models.Q(app_label='tasks'),
        help_text="Type of object this workflow applies to"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is available for use"
    )
    start_stage = models.ForeignKey(
        'Stage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text="Initial stage for new workflow instances"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration for this workflow"
    )

    class Meta:
        ordering = ['name']
        unique_together = [('name',)]
        indexes = [
            models.Index(fields=['content_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.content_type.model})"

    def clean(self):
        if self.start_stage and self.start_stage.workflow != self:
            raise ValidationError("Start stage must belong to this workflow")

class Stage(BaseModel):
    """
    A stage in a workflow with specific actions and requirements.
    """
    workflow = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.CASCADE,
        related_name='stages',
        help_text="Workflow this stage belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of this stage"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what happens in this stage"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of this stage in the workflow"
    )
    is_final = models.BooleanField(
        default=False,
        help_text="Whether this is a final/terminal stage"
    )
    required_approvals = models.PositiveIntegerField(
        default=0,
        help_text="Number of required approvals to progress"
    )
    assignment_policy = models.CharField(
        max_length=20,
        choices=[
            ('MANUAL', 'Manual Assignment'),
            ('ROLE_BASED', 'Role Based'),
            ('SELF', 'Case Creator'),
            ('PREVIOUS', 'Previous Assignee'),
            ('TEAM', 'Team Based'),
        ],
        default='MANUAL',
        help_text="How assignees are determined for this stage"
    )
    assignment_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration for assignment policy"
    )
    actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Automated actions to execute when entering this stage"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration for this stage"
    )

    class Meta:
        ordering = ['workflow', 'order']
        unique_together = [('workflow', 'name'), ('workflow', 'order')]
        indexes = [
            models.Index(fields=['is_final']),
            models.Index(fields=['assignment_policy']),
        ]

    def __str__(self):
        return f"{self.workflow.name} - {self.name}"

    def clean(self):
        if self.is_final and self.transitions_out.exists():
            raise ValidationError("Final stages cannot have outgoing transitions")

class Transition(BaseModel):
    """
    A possible transition between stages in a workflow.
    """
    source_stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='transitions_out',
        help_text="Stage this transition comes from"
    )
    target_stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='transitions_in',
        help_text="Stage this transition goes to"
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name for this transition"
    )
    condition = models.JSONField(
        default=dict,
        blank=True,
        help_text="Condition expression for this transition"
    )
    actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Actions to execute when this transition occurs"
    )
    require_comment = models.BooleanField(
        default=False,
        help_text="Whether a comment is required to perform this transition"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration for this transition"
    )

    class Meta:
        ordering = ['source_stage__order', 'target_stage__order']
        unique_together = [('source_stage', 'target_stage')]

    def __str__(self):
        return f"{self.source_stage} → {self.target_stage}"

    def clean(self):
        if self.source_stage.workflow != self.target_stage.workflow:
            raise ValidationError("Transitions must be within the same workflow")

class WorkflowInstance(BaseModel):
    """
    An instance of a workflow attached to a specific object.
    """
    workflow = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.PROTECT,
        related_name='instances',
        help_text="Template this instance is based on"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        help_text="Type of the object this workflow is for"
    )
    object_id = models.UUIDField(
        help_text="ID of the object this workflow is for"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    current_stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name='+',
        help_text="Current stage of this workflow instance"
    )
    is_complete = models.BooleanField(
        default=False,
        help_text="Whether this workflow has reached a final stage"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional state information for this instance"
    )

    class Meta:
        unique_together = [('content_type', 'object_id')]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_complete']),
            models.Index(fields=['current_stage']),
        ]

    def __str__(self):
        return f"{self.workflow.name} for {self.content_object}"

    def clean(self):
        if self.current_stage.workflow != self.workflow:
            raise ValidationError("Current stage must belong to the workflow template")

class StageInstance(BaseModel):
    """
    Tracks an object's progression through a specific stage.
    """
    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='stage_instances',
        help_text="Workflow instance this belongs to"
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name='+',
        help_text="Stage definition"
    )
    entered_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this stage was entered"
    )
    exited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this stage was exited"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('ESCALATED', 'Escalated'),
        ],
        default='PENDING',
        help_text="Current status of this stage instance"
    )
    assignees = models.ManyToManyField(
        'accounts.User',
        related_name='assigned_stages',
        help_text="Users assigned to this stage instance"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional state information for this stage"
    )

    class Meta:
        ordering = ['-entered_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['entered_at']),
        ]

    def __str__(self):
        return f"{self.stage} for {self.workflow_instance}"

class TransitionLog(BaseModel):
    """
    Log of all transitions between stages.
    """
    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='transition_logs',
        help_text="Workflow instance this transition belongs to"
    )
    transition = models.ForeignKey(
        Transition,
        on_delete=models.PROTECT,
        related_name='+',
        help_text="Transition definition"
    )
    from_stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name='+',
        help_text="Stage transitioned from"
    )
    to_stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name='+',
        help_text="Stage transitioned to"
    )
    performed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='+',
        help_text="User who performed the transition"
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional comment about the transition"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context about this transition"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workflow_instance']),
            models.Index(fields=['transition']),
        ]

    def __str__(self):
        return f"{self.from_stage} → {self.to_stage} by {self.performed_by}"

class SLA(BaseModel):
    """
    Service Level Agreement definition for workflow stages.
    """
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='workflow_slas',
        help_text="Stage this SLA applies to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of this SLA"
    )
    duration_hours = models.PositiveIntegerField(
        help_text="Expected duration in hours"
    )
    business_hours_only = models.BooleanField(
        default=False,
        help_text="Whether SLA only counts during business hours"
    )
    escalation_path = models.JSONField(
        default=list,
        blank=True,
        help_text="Steps to take when SLA is breached"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration for this SLA"
    )

    class Meta:
        unique_together = [('stage', 'name')]
        indexes = [
            models.Index(fields=['business_hours_only']),
        ]
        base_manager_name = 'objects'

    def __str__(self):
        return f"{self.stage} - {self.name}"

class Escalation(BaseModel):
    """
    Record of an SLA breach and escalation.
    """
    stage_instance = models.ForeignKey(
        StageInstance,
        on_delete=models.CASCADE,
        related_name='escalations',
        help_text="Stage instance that was escalated"
    )
    sla = models.ForeignKey(
        SLA,
        on_delete=models.PROTECT,
        related_name='+',
        help_text="SLA that was breached"
    )
    escalated_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the escalation occurred"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the escalation was resolved"
    )
    actions_taken = models.JSONField(
        default=list,
        blank=True,
        help_text="Actions taken during escalation"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context about this escalation"
    )

    class Meta:
        ordering = ['-escalated_at']
        indexes = [
            models.Index(fields=['stage_instance']),
            models.Index(fields=['resolved_at']),
        ]

    def __str__(self):
        return f"Escalation for {self.stage_instance}"