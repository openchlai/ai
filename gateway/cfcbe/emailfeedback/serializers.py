from rest_framework import serializers
from .models import Email

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ['id', 'sender', 'recipient', 'subject', 'body', 'received_date', 'is_read']