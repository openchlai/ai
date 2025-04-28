from rest_framework import serializers
from .models import Contact, WhatsAppMedia, WhatsAppMessage, WhatsAppResponse, WhatsAppConversation

# Contact Serializer
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'wa_id', 'name', 'display_phone_number']


# WhatsApp Media Serializer
class WhatsAppMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMedia
        fields = ['id', 'media_type', 'media_url', 'media_file', 'media_mime_type']



# WhatsApp Message Serializer
class WhatsAppMessageSerializer(serializers.ModelSerializer):
    sender = ContactSerializer(read_only=True)  # Nested serialization for sender
    recipient = ContactSerializer(read_only=True)  # Nested serialization for recipient
    media = WhatsAppMediaSerializer(read_only=True)  # Nested media object
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), source='sender', write_only=True
    )  # Allows sending only the sender ID
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), source='recipient', write_only=True
    )  # Allows sending only the recipient ID
    media_id = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppMedia.objects.all(), source='media', write_only=True, allow_null=True
    )  # Allows linking media via ID

    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'sender', 'recipient', 'sender_id', 'recipient_id', 'message_type', 
            'content', 'caption', 'media', 'media_id', 'timestamp', 'status', 'is_forwarded_to_main_system'
        ]


# WhatsApp Response Serializer
class WhatsAppResponseSerializer(serializers.ModelSerializer):
    message = WhatsAppMessageSerializer(read_only=True)  # Nested message details
    message_id = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppMessage.objects.all(), source='message', write_only=True
    )  # Allows sending only the message ID

    class Meta:
        model = WhatsAppResponse
        fields = ['id', 'message', 'message_id', 'content', 'timestamp']


# WhatsApp Conversation Serializer
class WhatsAppConversationSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)  # Nested contact
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), source='contact', write_only=True
    )  # Allows sending only the contact ID
    messages = WhatsAppMessageSerializer(many=True, read_only=True)  # Nested messages
    message_ids = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppMessage.objects.all(), source='messages', many=True, write_only=True
    )  # Allows adding messages via ID
    responses = WhatsAppResponseSerializer(many=True, read_only=True)  # Nested responses
    response_ids = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppResponse.objects.all(), source='responses', many=True, write_only=True
    )  # Allows adding responses via ID

    class Meta:
        model = WhatsAppConversation
        fields = ['id', 'contact', 'contact_id', 'messages', 'message_ids', 'responses', 'response_ids']
