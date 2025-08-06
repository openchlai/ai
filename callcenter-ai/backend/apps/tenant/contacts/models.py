from django.db import models
from django.core.validators import validate_email, RegexValidator
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
from apps.shared.core.models import BaseModel


# Communication method choices (customize as needed)
COMMUNICATION_METHOD_CHOICES = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ('sms', 'SMS'),
    ('mail', 'Mail'),
    ('in_person', 'In Person'),
]

class ContactType(BaseModel):
    """Model for categorizing contacts (Customer, Partner, Vendor, etc.)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        
        verbose_name = "Contact Type"
        verbose_name_plural = "Contact Types"
        
    def __str__(self):
        return self.name


class ContactTag(BaseModel):
    """Model for tagging contacts with keywords"""
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#808080')  # Hex color

    class Meta:
        
        verbose_name = "Contact Tag"
        verbose_name_plural = "Contact Tags"
        
    def __str__(self):
        return self.name


class ContactGroup(BaseModel):
    """Model for grouping contacts together"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        
        verbose_name = "Contact Group"
        verbose_name_plural = "Contact Groups"
        
    def __str__(self):
        return self.name


class Contact(BaseModel):
    """Main model for storing contact information"""
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=30, blank=True, null=True)  # Mr., Mrs., Dr., etc.
    suffix = models.CharField(max_length=30, blank=True, null=True)  # Jr., Sr., III, etc.
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Organization Details
    organization = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(validators=[validate_email], blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}',
        message="Phone number must be entered in the format: '+999999999'."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional Details
    website = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Communication Preferences
    preferred_communication_method = models.CharField(
        max_length=50,
        choices=COMMUNICATION_METHOD_CHOICES,
        blank=True, 
        null=True
    )
    do_not_call = models.BooleanField(default=False)
    do_not_email = models.BooleanField(default=False)
    
    # Relationships
    types = models.ManyToManyField(ContactType, through='ContactContactType', related_name='contacts_of_type')
    tags = models.ManyToManyField(ContactTag, through='ContactTagAssignment', related_name='tagged_contacts')
    groups = models.ManyToManyField(ContactGroup, related_name='group_contacts')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ContactContactType(BaseModel):
    """Through model for Contact to ContactType relationship"""
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    contact_type = models.ForeignKey(ContactType, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('contact', 'contact_type')
        verbose_name = "Contact Type Assignment"
        verbose_name_plural = "Contact Type Assignments"
        
    def __str__(self):
        return f"{self.contact} - {self.contact_type}"


class ContactTagAssignment(BaseModel):
    """Through model for Contact to ContactTag relationship"""
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    tag = models.ForeignKey(ContactTag, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('contact', 'tag')
        verbose_name = "Contact Tag Assignment"
        verbose_name_plural = "Contact Tag Assignments"
        
    def __str__(self):
        return f"{self.contact} - {self.tag}"


class ContactInteraction(BaseModel):
    """Model for tracking interactions with contacts"""
    INTERACTION_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('message', 'Message'),
    ]
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_CHOICES)
    subject = models.CharField(max_length=255)
    notes = models.TextField()
    date = models.DateTimeField()
    duration = models.DurationField(blank=True, null=True)  # For calls/meetings
    related_case = models.ForeignKey(
        'cases.Case', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='contact_interactions'
    )
    related_task = models.ForeignKey(
        'tasks.Task', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='contact_interactions'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = "Contact Interaction"
        verbose_name_plural = "Contact Interactions"
        
    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.contact} on {self.date}"