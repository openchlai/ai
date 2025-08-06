from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericRelation
from apps.shared.accounts.models import User
from apps.shared.core.models import BaseModel, AuditLog
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
import uuid

class CaseType(BaseModel):
    """
    Enhanced case type model with VAC/GBV classifications.
    """
    CATEGORY_CHOICES = [
        ('vac', 'Violence Against Children'),
        ('gbv', 'Gender-Based Violence'),
        ('general', 'General Protection'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=50, unique=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # VAC/GBV specific configurations
    requires_immediate_response = models.BooleanField(
        default=False,
        help_text="Whether cases of this type require immediate action"
    )
    mandatory_reporting = models.BooleanField(
        default=False,
        help_text="Whether this case type requires legal reporting"
    )
    default_safety_plan = models.TextField(
        blank=True,
        help_text="Default safety plan template for this case type"
    )
    
    class Meta:
        verbose_name = "Case Type"
        verbose_name_plural = "Case Types"
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['requires_immediate_response']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class CasePriority(models.IntegerChoices):
    """
    Enhanced priority levels with VAC/GBV considerations.
    """
    EMERGENCY = 1, 'Emergency (24h response)'
    URGENT = 2, 'Urgent (48h response)'
    HIGH = 3, 'High (72h response)'
    MEDIUM = 4, 'Medium (5 day response)'
    LOW = 5, 'Low (7 day response)'

class CaseStatus(BaseModel):
    """
    Configurable statuses that cases can have during their lifecycle.
    """
    status_name = models.CharField(  # Changed from 'name' to 'status_name'
        max_length=50,
        help_text="Name of the status (e.g., 'Open', 'In Progress')"
    )
    code = models.SlugField(
        max_length=30,
        unique=True,
        help_text="Short code for the status"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this status"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this status is available for use"
    )
    is_closed = models.BooleanField(
        default=False,
        help_text="Whether this status represents a closed case"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default status for new cases"
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        help_text="Color code to represent this status"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order in which statuses should be displayed"
    )
    allowed_next_statuses = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        help_text="Statuses that can follow this one in workflow"
    )

    class Meta:
        verbose_name = "Case Status"
        verbose_name_plural = "Case Statuses"
        ordering = ['order', 'status_name']  # Updated to use 'status_name'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_closed']),
        ]

    def __str__(self):
        return self.status_name  # Updated to use 'status_name'

    def clean(self):
        if self.is_default and CaseStatus.objects.filter(is_default=True).exclude(pk=self.pk).exists():
            raise ValidationError("There can only be one default status")

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure no other status is marked as default
            CaseStatus.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
class ProtectionDetail(models.Model):
    """
    Dedicated model for protection-specific case details.
    """
    RISK_LEVELS = [
        (1, 'Low Risk'),
        (2, 'Medium Risk'),
        (3, 'High Risk'),
        (4, 'Extreme Risk')
    ]
    
    case = models.OneToOneField(
        'Case',
        on_delete=models.CASCADE,
        related_name='protection_details'
    )
    risk_level = models.PositiveSmallIntegerField(
        choices=RISK_LEVELS,
        default=2
    )
    immediate_needs = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Urgent needs: medical, shelter, legal etc."
    )
    safety_measures = JSONField(
        default=list,
        help_text="Implemented safety actions"
    )
    vulnerability_factors = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="e.g. disability, migration_status"
    )
    
    class Meta:
        verbose_name = "Protection Detail"
        verbose_name_plural = "Protection Details"

class Case(BaseModel):
    """
    Enhanced Case model with integrated VAC/GBV functionality.
    """
    # ========== CORE CASE FIELDS ==========
    case_type = models.ForeignKey(
        CaseType,
        on_delete=models.PROTECT,
        related_name='cases'
    )
    case_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.ForeignKey(
        CaseStatus,
        on_delete=models.PROTECT,
        related_name='cases'
    )
    priority = models.PositiveSmallIntegerField(
        choices=CasePriority.choices,
        default=CasePriority.MEDIUM
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assigned_cases',
        null=True,
        blank=True
    )
    due_date = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_cases'
    )
    
    # ========== VAC/GBV SPECIFIC FIELDS ==========
    survivor_code = models.CharField(
        max_length=36,
        blank=True,
        help_text="Anonymous identifier for survivors"
    )
    incident_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the reported incident"
    )
    incident_location = JSONField(
        default=dict,
        blank=True,
        help_text="Location details of incident"
    )
    perpetrator_relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text="Relationship to survivor (if known)"
    )
    protection_concerns = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Specific protection risks identified"
    )
    
    # ========== SERVICE COORDINATION ==========
    services_provided = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Services accessed by survivor"
    )
    referral_organizations = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Organizations involved in case"
    )
    
    # ========== CONFIDENTIALITY & CONSENT ==========
    disclosure_consent = models.BooleanField(
        default=False,
        help_text="Whether survivor consented to information sharing"
    )
    consent_details = JSONField(
        default=dict,
        blank=True,
        help_text="Scope and limitations of consent"
    )
    
    class Meta:
        verbose_name = "Case"
        verbose_name_plural = "Cases"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['case_type']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['survivor_code']),
        ]

    def save(self, *args, **kwargs):
        if not self.case_number:
            prefix = 'VAC' if self.case_type.category == 'vac' else 'GBV' if self.case_type.category == 'gbv' else 'CASE'
            timestamp = timezone.now().strftime('%y%m%d')
            last_id = Case.objects.filter(case_number__startswith=f"{prefix}-{timestamp}").count()
            self.case_number = f"{prefix}-{timestamp}-{last_id + 1:04d}"
        
        if not self.survivor_code and self.case_type.category in ['vac', 'gbv']:
            self.survivor_code = f"SURV-{uuid.uuid4().hex[:8].upper()}"
            
        super().save(*args, **kwargs)

    @property
    def is_protection_case(self):
        return self.case_type.category in ['vac', 'gbv']

    def create_protection_details(self):
        """Initialize protection-specific tracking"""
        if self.is_protection_case and not hasattr(self, 'protection_details'):
            return ProtectionDetail.objects.create(case=self)
        return None

# ========== ENHANCED DOCUMENT MODEL FOR PROTECTION CASES ==========
class CaseDocument(BaseModel):
    """
    Enhanced document model with protection case features.
    """
    DOCUMENT_TYPES = [
        ('medical', 'Medical Report'),
        ('police', 'Police Report'),
        ('consent', 'Consent Form'),
        ('other', 'Other')
    ]
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='other'
    )
    file = models.FileField(upload_to='case_documents/%Y/%m/%d/')
    description = models.TextField(blank=True)
    is_confidential = models.BooleanField(
        default=False,
        help_text="Whether document contains sensitive information"
    )
    
    class Meta:
        verbose_name = "Case Document"
        verbose_name_plural = "Case Documents"
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['is_confidential']),
        ]

# ========== SAFETY PLAN MODEL ==========
class SafetyPlan(models.Model):
    """
    Dedicated safety plan model for protection cases.
    """
    case = models.OneToOneField(
        Case,
        on_delete=models.CASCADE,
        related_name='safety_plan'
    )
    emergency_contacts = JSONField(
        default=list,
        help_text="List of safe contacts"
    )
    safety_actions = JSONField(
        default=list,
        help_text="Specific safety measures"
    )
    warning_signs = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Danger indicators"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Safety Plan"
        verbose_name_plural = "Safety Plans"

# ========== CASE HISTORY ENHANCEMENTS ==========
class CaseHistory(BaseModel):
    """
    Enhanced case history with protection-specific tracking.
    """
    # ... [Keep existing CaseHistory fields] ...
    
    protection_notes = models.TextField(
        blank=True,
        help_text="Special notes for protection cases"
    )
    risk_assessment = models.PositiveSmallIntegerField(
        choices=ProtectionDetail.RISK_LEVELS,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Case History"
        # ... [Keep existing Meta] ...
        
class CaseNote(BaseModel):
    """
    Enhanced case note model with protection-specific fields.
    """
    # ... [Keep existing CaseNote fields] ...

    protection_notes = models.TextField(
        blank=True,
        help_text="Special notes for protection cases"
    )
    risk_assessment = models.PositiveSmallIntegerField(
        choices=ProtectionDetail.RISK_LEVELS,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Case Note"
        # ... [Keep existing Meta] ...