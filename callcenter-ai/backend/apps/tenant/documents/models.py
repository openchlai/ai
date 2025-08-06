from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from apps.shared.core.models import (
    BaseModel,
)
from enum import Enum
import uuid
import os

User = get_user_model()

def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    return f"documents/{instance.tenant_id}/{uuid.uuid4()}/{filename}"

class DocumentType(BaseModel):
    """Classification for different document types"""
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, blank=True)
    allowed_extensions = models.JSONField(default=list)
    
    class Meta:
        verbose_name = _("Document Type")
        verbose_name_plural = _("Document Types")

class DocumentPermissionLevel(Enum):
    PRIVATE = 1
    INTERNAL = 2
    RESTRICTED = 3
    PUBLIC = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Document(BaseModel):
    """Core document model with versioning and access control"""
    DOCUMENT_CATEGORIES = [
        ('case', 'Case Document'),
        ('contact', 'Contact Document'),
        ('task', 'Task Document'),
        ('general', 'General Document'),
    ]
    
    # Core Fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'txt', 'csv'
        ])]
    )
    file_size = models.PositiveIntegerField(editable=False)
    file_hash = models.CharField(max_length=64, editable=False)  # SHA-256
    
    # Metadata
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='documents'
    )
    category = models.CharField(
        max_length=20,
        choices=DOCUMENT_CATEGORIES,
        default='general'
    )
    tags = models.JSONField(default=list)  # For flexible tagging
    permission_level = models.PositiveSmallIntegerField(
        choices=DocumentPermissionLevel.choices(),
        default=DocumentPermissionLevel.INTERNAL.value
    )
    is_encrypted = models.BooleanField(default=False)
    
    # Relationships
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        related_name='related_case',
        null=True,
        blank=True
    )
    contact = models.ForeignKey(
        'contacts.Contact',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_versions'
    )
    
    # Indexes for performance
    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['permission_level']),
            models.Index(fields=['created_at']),
            models.Index(fields=['case', 'contact', 'task']),
        ]
        ordering = ['-created_at']
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def save(self, *args, **kwargs):
        """Calculate file size and hash before saving"""
        if self.file:
            self.file_size = self.file.size
            # In production, calculate actual file hash
            self.file_hash = str(uuid.uuid4())  
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Generate secure download URL"""
        from django.urls import reverse
        return reverse('document-download', kwargs={'pk': self.pk})

class DocumentVersion(BaseModel):
    """Track complete version history"""
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version = models.PositiveIntegerField()
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.PositiveIntegerField()
    file_hash = models.CharField(max_length=64)
    change_reason = models.TextField(blank=True)
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('document', 'version')
        ordering = ['document', '-version']
        verbose_name = _("Document Version")
        verbose_name_plural = _("Document Versions")

    def __str__(self):
        return f"{self.document.title} - v{self.version}"

class DocumentAccessLog(BaseModel):
    """Audit trail for document access"""
    ACCESS_TYPES = [
        ('view', 'View'),
        ('download', 'Download'),
        ('preview', 'Preview'),
        ('share', 'Share'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Document Access Log")
        verbose_name_plural = _("Document Access Logs")

class DocumentShareLink(BaseModel):
    """Temporary sharing links for documents"""
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='share_links'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expiration = models.DateTimeField()
    max_downloads = models.PositiveIntegerField(null=True, blank=True)
    password = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_share_links'
    )

    class Meta:
        verbose_name = _("Document Share Link")
        verbose_name_plural = _("Document Share Links")

    def __str__(self):
        return f"Share link for {self.document.title}"

class DocumentPreview(BaseModel):
    """Generated previews for documents"""
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='preview'
    )
    thumbnail = models.ImageField(upload_to='document-previews/')
    preview_file = models.FileField(
        upload_to='document-previews/',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('ready', 'Ready'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = _("Document Preview")
        verbose_name_plural = _("Document Previews")

class DocumentTemplate(BaseModel):
    """Reusable document templates"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='document-templates/')
    variables = models.JSONField(default=list)  # Template variables
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='templates'
    )
    is_system = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Document Template")
        verbose_name_plural = _("Document Templates")

    def __str__(self):
        return self.name