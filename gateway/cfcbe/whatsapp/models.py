from django.db import models

# Stores WhatsApp contacts to avoid redundancy
class Contact(models.Model):
    wa_id = models.CharField(max_length=15, unique=True)  # WhatsApp ID
    name = models.CharField(max_length=255, blank=True, null=True)  # Optional name
    display_phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else self.wa_id


# Stores media files linked to WhatsApp messages
class WhatsAppMedia(models.Model):
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


# Handles different types of WhatsApp messages
class WhatsAppMessage(models.Model):
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

    # sender = models.CharField(max_length=12,null=True,blank=False)
    # recipient = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="received_messages", blank=True, null=True)
    sender = models.CharField(max_length=255,null=True,blank=True)# ✅ Allows outgoing messages (where sender is NULL)
    recipient = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="received_messages",
        blank=True, null=True  # ✅ Allows incoming messages (where recipient is NULL)
    ) # ✅ Allow null
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


# Represents responses to WhatsApp messages
class WhatsAppResponse(models.Model):
    message = models.ForeignKey(WhatsAppMessage, on_delete=models.CASCADE, related_name="responses")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Response at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_message(self):
        return self.message


# Represents a conversation containing messages and responses
class WhatsAppConversation(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="conversations")
    messages = models.ManyToManyField(WhatsAppMessage, related_name='conversations')
    responses = models.ManyToManyField(WhatsAppResponse, related_name='conversations')

    def __str__(self):
        return f"Conversation with {self.contact} - {self.messages.count()} messages"

# Encryption utility
# def encrypt(data):
#     cipher = Fernet(settings.ENCRYPTION_KEY)
#     return cipher.encrypt(data.encode()).decode()

# def decrypt(data):
#     cipher = Fernet(settings.ENCRYPTION_KEY)
#     return cipher.decrypt(data.encode()).decode()

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WhatsAppCredential(models.Model):
    organization = models.OneToOneField('Organization', on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    client_secret = models.TextField()  # Encrypted
    business_id = models.CharField(max_length=255)
    phone_number_id = models.CharField(max_length=255)
    access_token = models.TextField()  # Encrypted
    token_expiry = models.DateTimeField(null=True)

    # def save(self, *args, **kwargs):
    #     self.client_secret = encrypt(self.client_secret)
    #     self.access_token = encrypt(self.access_token)
    #     super().save(*args, **kwargs)

    # def get_client_secret(self):
    #     return decrypt(self.client_secret)

    # def get_access_token(self):
    #     return decrypt(self.access_token)
