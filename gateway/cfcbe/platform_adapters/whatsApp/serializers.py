from rest_framework import serializers
from webhook_handler.models import (
    Contact, 
    WhatsAppMedia, 
    WhatsAppMessage, 
    WhatsAppResponse, 
    WhatsAppConversation,
    Conversation,
    WebhookMessage
)
from shared.models.standard_message import StandardMessage

# Contact Serializer
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'wa_id', 'name', 'display_phone_number', 'conversation']
        read_only_fields = ['conversation']


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
    sender_id = serializers.CharField(write_only=True, required=False)  # Allows sending only the sender ID
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), source='recipient', write_only=True, required=False
    )  # Allows sending only the recipient ID
    media_id = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppMedia.objects.all(), source='media', write_only=True, allow_null=True, required=False
    )  # Allows linking media via ID
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all(), required=False)
    webhook_message = serializers.PrimaryKeyRelatedField(queryset=WebhookMessage.objects.all(), required=False)

    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'sender', 'recipient', 'sender_id', 'recipient_id', 'message_type', 
            'content', 'caption', 'media', 'media_id', 'timestamp', 'status', 
            'is_forwarded_to_main_system', 'conversation', 'webhook_message'
        ]

    def create(self, validated_data):
        sender_id = validated_data.pop('sender_id', None)
        
        # If we have a sender_id but no sender object, handle it
        if sender_id and 'sender' not in validated_data:
            # In our architecture, sender is a string field, not a foreign key
            validated_data['sender'] = sender_id
            
        return super().create(validated_data)


# WhatsApp Response Serializer
class WhatsAppResponseSerializer(serializers.ModelSerializer):
    message = WhatsAppMessageSerializer(read_only=True)  # Nested message details
    message_id = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppMessage.objects.all(), source='message', write_only=True
    )  # Allows sending only the message ID
    webhook_message = serializers.PrimaryKeyRelatedField(queryset=WebhookMessage.objects.all(), required=False)

    class Meta:
        model = WhatsAppResponse
        fields = ['id', 'message', 'message_id', 'content', 'timestamp', 'webhook_message']


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
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all(), required=False)

    class Meta:
        model = WhatsAppConversation
        fields = [
            'id', 'contact', 'contact_id', 'messages', 'message_ids', 
            'responses', 'response_ids', 'conversation'
        ]


# Standard Message Serializer (for internal gateway usage)
class StandardMessageSerializer(serializers.Serializer):
    message_id = serializers.CharField()
    sender_id = serializers.CharField()
    platform = serializers.CharField()
    content = serializers.CharField()
    timestamp = serializers.FloatField()
    recipient_id = serializers.CharField(required=False, allow_blank=True, default="")
    message_type = serializers.CharField(default="text")
    media_url = serializers.URLField(required=False, allow_null=True)
    metadata = serializers.DictField(default=dict)
    
    def create(self, validated_data):
        return StandardMessage(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance