from django.contrib import admin
from .models import (
    Conversation, WebhookMessage, Person, Complaint, CaseNote,
    ComplaintStatus, Notification, Voicenote, Contact, WhatsAppMedia,
    WhatsAppMessage, WhatsAppResponse, Organization, WhatsAppCredential
)

# Core Gateway Models
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'sender_id', 'platform', 'is_active', 'last_activity')
    list_filter = ('platform', 'is_active')
    search_fields = ('conversation_id', 'sender_id')

@admin.register(WebhookMessage)
class WebhookMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender_id', 'platform', 'message_type', 'timestamp')
    list_filter = ('platform', 'message_type')
    search_fields = ('message_id', 'sender_id', 'content')

# Webform (Complaint) Models
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender')
    search_fields = ('name',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'reporter_nickname', 'case_category', 'created_at')
    list_filter = ('case_category', 'created_at')
    search_fields = ('complaint_id', 'reporter_nickname', 'complaint_text')
    date_hierarchy = 'created_at'

@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'created_at', 'created_by')
    list_filter = ('created_at',)
    search_fields = ('note_text', 'created_by')

@admin.register(ComplaintStatus)
class ComplaintStatusAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'status', 'updated_at', 'updated_by')
    list_filter = ('status', 'updated_at')
    search_fields = ('updated_by',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'complaint', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message',)

@admin.register(Voicenote)
class VoicenoteAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'created_at')
    list_filter = ('created_at',)

# WhatsApp Models
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('wa_id', 'name', 'display_phone_number')
    search_fields = ('wa_id', 'name')

@admin.register(WhatsAppMedia)
class WhatsAppMediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'media_url', 'media_mime_type')
    list_filter = ('media_type',)

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'message_type', 'status', 'timestamp')
    list_filter = ('message_type', 'status', 'timestamp')
    search_fields = ('content', 'caption')
    date_hierarchy = 'timestamp'

@admin.register(WhatsAppResponse)
class WhatsAppResponseAdmin(admin.ModelAdmin):
    list_display = ('message', 'timestamp')
    search_fields = ('content',)
    date_hierarchy = 'timestamp'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')

@admin.register(WhatsAppCredential)
class WhatsAppCredentialAdmin(admin.ModelAdmin):
    list_display = ('organization', 'business_id', 'phone_number_id', 'token_expiry')
    list_filter = ('token_expiry',)
    search_fields = ('organization__name', 'business_id', 'phone_number_id')
    
    # Exclude sensitive fields from display
    exclude = ('client_secret', 'access_token')