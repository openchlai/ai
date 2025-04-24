from django.db import models
from django.utils import timezone
import uuid
import random
import string

#######################################
# Core Gateway Models
#######################################

class Conversation(models.Model):
    """Model for tracking conversations across platforms."""
    
    conversation_id = models.CharField(max_length=255, unique=True)
    sender_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.platform} conversation with {self.sender_id}"

class WebhookMessage(models.Model):
    """Model for storing incoming webhook messages."""
    
    message_id = models.CharField(max_length=255, unique=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    media_url = models.URLField(blank=True, null=True)
    message_type = models.CharField(max_length=50, default='text')
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Message from {self.sender_id} on {self.platform}"

#######################################
# Authentication Models
#######################################

class Organization(models.Model):
    """
    Represents an organization using the Gateway API.
    
    Enhanced with authentication capabilities for both WhatsApp and Webform.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EmailVerification(models.Model):
    """
    Tracks email verification attempts with OTP.
    """
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP."""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_verification(cls, email):
        """Create a new verification entry with OTP."""
        # Expire any existing verification for this email
        cls.objects.filter(email=email).update(is_verified=False)
        
        # Create new verification
        otp = cls.generate_otp()
        expiration = timezone.now() + timezone.timedelta(minutes=10)  # OTP valid for 10 minutes
        
        verification = cls.objects.create(
            email=email,
            otp=otp,
            expires_at=expiration
        )
        
        return verification
    
    def is_valid(self):
        """Check if the OTP is still valid."""
        return not self.is_verified and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Verification for {self.email}"

#######################################
# Webform (Complaint) Models
#######################################

class Person(models.Model):
    """Model for storing information about Victims or Perpetrators."""
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Complaint(models.Model):
    """Model to represent a Complaint."""
    complaint_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    session_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True) 
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    timestamp = models.DateTimeField(auto_now_add=True)
    reporter_nickname = models.CharField(max_length=100, null=True, blank=True)
    case_category = models.CharField(max_length=255, default="Not Specified", null=True, blank=True)
    complaint_text = models.TextField(blank=True, null=True)
    complaint_image = models.ImageField(upload_to="complaints/images/", blank=True, null=True)
    complaint_audio = models.FileField(upload_to="complaints/audio/", blank=True, null=True)
    complaint_video = models.FileField(upload_to="complaints/videos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    message_id_ref = models.CharField(max_length=255, null=True, blank=True)
    
    victim = models.ForeignKey(Person, related_name='victims', on_delete=models.CASCADE, null=True, blank=True)
    perpetrator = models.ForeignKey(Person, related_name='perpetrators', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Complaint {self.complaint_id} by {self.reporter_nickname}"

class CaseNote(models.Model):
    """Model for Case Notes (to document updates or notes related to the case)."""
    complaint = models.ForeignKey(Complaint, related_name='case_notes', on_delete=models.CASCADE)
    note_text = models.TextField()
    note_audio = models.BinaryField(blank=True, null=True)  # Optional audio note
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)  # This could be an agent's name or system

    def __str__(self):
        return f"CaseNote for {self.complaint.complaint_id} on {self.created_at}"

class ComplaintStatus(models.Model):
    """Model for storing the status of a complaint."""
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255)  # This could be an agent's name or system

    def __str__(self):
        return f"Status for Complaint {self.complaint.complaint_id}: {self.status}"

class Notification(models.Model):
    """Model for notifications about complaints."""
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for Complaint {self.complaint.complaint_id}"

class Voicenote(models.Model):
    """Model for voice notes."""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='voicenotes', null=True, blank=True)
    voicenote = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        complaint_id = self.complaint.complaint_id if self.complaint else "No complaint"
        return f"Voicenote for Complaint {complaint_id}"

#######################################
# WhatsApp Models
#######################################

class Contact(models.Model):
    """Stores WhatsApp contacts to avoid redundancy."""
    wa_id = models.CharField(max_length=15, unique=True)  # WhatsApp ID
    name = models.CharField(max_length=255, blank=True, null=True)  # Optional name
    display_phone_number = models.CharField(max_length=15, blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')

    def __str__(self):
        return self.name if self.name else self.wa_id

class WhatsAppMedia(models.Model):
    """Stores media files linked to WhatsApp messages."""
    MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
    ]

    media_type = models.CharField(max_length=50, choices=MEDIA_TYPES, help_text="Type of the media file")
    media_url = models.URLField(blank=True, null=True, help_text="URL of the media file, if applicable")
    media_file = models.FileField(upload_to='whatsapp_media/', blank=True, null=True, help_text="Uploaded media file")
    media_mime_type = models.CharField(max_length=100, blank=True, null=True, help_text="MIME type of the media file")

    def __str__(self):
        return f"Media ({self.media_type}) - {self.media_url or self.media_file}"

class WhatsAppMessage(models.Model):
    """Handles different types of WhatsApp messages."""
    MESSAGE_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
        ("sticker", "Sticker"),
        ("location", "Location"),
        ("contact", "Contact"),
    ]

    MESSAGE_STATUS = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("delivered", "Delivered"),
        ("read", "Read"),
    ]

    sender = models.CharField(max_length=255, null=True, blank=True)
    recipient = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="received_messages", blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_messages')
    webhook_message = models.OneToOneField(WebhookMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_message')
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES, default="text", help_text="Type of the message")
    content = models.TextField(blank=True, null=True, help_text="Text content of the message, if applicable")
    caption = models.TextField(blank=True, null=True, help_text="Caption for media messages, if applicable")
    media = models.ForeignKey(WhatsAppMedia, on_delete=models.SET_NULL, blank=True, null=True, help_text="Linked media file")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp of when the message was sent/received")
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS, default="pending", help_text="Current status of the message")
    is_forwarded_to_main_system = models.BooleanField(default=False, help_text="Flag to track if the message was forwarded to the main system")

    class Meta:
        ordering = ['-timestamp']

    def mark_as_sent(self):
        """Update the message status to 'sent'."""
        self.status = "sent"
        self.save()

    def mark_as_failed(self):
        """Update the message status to 'failed'."""
        self.status = "failed"
        self.save()

    def mark_as_delivered(self):
        """Update the message status to 'delivered'."""
        self.status = "delivered"
        self.save()

    def mark_as_read(self):
        """Update the message status to 'read'."""
        self.status = "read"
        self.save()

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} ({self.message_type}, {self.status})"

class WhatsAppResponse(models.Model):
    """Represents responses to WhatsApp messages."""
    message = models.ForeignKey(WhatsAppMessage, on_delete=models.CASCADE, related_name="responses")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    webhook_message = models.OneToOneField(WebhookMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_response')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Response at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_message(self):
        return self.message

class WhatsAppCredential(models.Model):
    """Stores WhatsApp API credentials for an organization."""
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    client_secret = models.TextField()  # Could be encrypted
    business_id = models.CharField(max_length=255)
    phone_number_id = models.CharField(max_length=255)
    access_token = models.TextField()  # Could be encrypted
    token_expiry = models.DateTimeField(null=True)

    def __str__(self):
        return f"WhatsApp Credentials for {self.organization.name}"