from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.shared.core.models import BaseModel, AuditLog
import uuid

User = get_user_model()

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class Priority(models.IntegerChoices):
        LOW = 1, _('Low')
        MEDIUM = 2, _('Medium')
        HIGH = 3, _('High')
        CRITICAL = 4, _('Critical')

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PENDING = 'pending', _('Pending')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        ON_HOLD = 'on_hold', _('On Hold')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    priority = models.PositiveSmallIntegerField(
        _('priority'),
        choices=Priority.choices,
        default=Priority.MEDIUM,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    due_date = models.DateTimeField(_('due date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name='%(class)s_created',
        verbose_name=_('created by')
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('updated by')
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name=_('assigned to')
    )
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('case')
    )
    workflow = models.ForeignKey(
        'workflows.WorkflowInstance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('workflow')
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name=_('parent task')
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        ordering = ['-priority', 'due_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['case']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Update completed_at when status changes to completed
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def is_overdue(self):
        return self.due_date and timezone.now() > self.due_date and self.status != self.Status.COMPLETED

    def get_progress(self):
        if self.status == self.Status.COMPLETED:
            return 100
        subtasks = self.subtasks.all()
        if subtasks.exists():
            completed = subtasks.filter(status=self.Status.COMPLETED).count()
            return int((completed / subtasks.count()) * 100)
        return 0 if self.status == self.Status.PENDING else 50
    

class TaskTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=50, unique=True)
    color = models.CharField(_('color'), max_length=7, default='#808080')
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task tag')
        verbose_name_plural = _('task tags')

    def __str__(self):
        return self.name


class TaskTagging(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('task')
    )
    tag = models.ForeignKey(
        TaskTag,
        on_delete=models.CASCADE,
        verbose_name=_('tag')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task tagging')
        verbose_name_plural = _('task taggings')
        unique_together = ('task', 'tag')


class TaskComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('task')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('author')
    )
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_system_note = models.BooleanField(_('is system note'), default=False)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task comment')
        verbose_name_plural = _('task comments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"


class TaskAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('task')
    )
    file = models.FileField(_('file'), upload_to='task_attachments/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('uploaded by')
    )
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    description = models.CharField(_('description'), max_length=255, blank=True)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task attachment')
        verbose_name_plural = _('task attachments')

    def __str__(self):
        return f"Attachment for {self.task}"


class TaskReminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name=_('task')
    )
    remind_at = models.DateTimeField(_('remind at'))
    notified = models.BooleanField(_('notified'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task reminder')
        verbose_name_plural = _('task reminders')
        ordering = ['remind_at']

    def __str__(self):
        return f"Reminder for {self.task} at {self.remind_at}"


class TaskChangeLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name=_('task')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('changed by')
    )
    changed_at = models.DateTimeField(_('changed at'), auto_now_add=True)
    field = models.CharField(_('field'), max_length=50)
    old_value = models.TextField(_('old value'), blank=True, null=True)
    new_value = models.TextField(_('new value'), blank=True, null=True)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant'
    )

    class Meta:
        verbose_name = _('task change log')
        verbose_name_plural = _('task change logs')
        ordering = ['-changed_at']

    def __str__(self):
        return f"Change to {self.task} - {self.field}"