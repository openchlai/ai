from rest_framework import serializers
from webhook_handler.models import (
    Complaint, 
    CaseNote, 
    ComplaintStatus, 
    Person, 
    Voicenote,
    Conversation,
    WebhookMessage,
    Notification
)

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'age', 'gender', 'additional_info']
        extra_kwargs = {
            'age': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True, 'allow_blank': True},
            'additional_info': {'required': False, 'allow_blank': True},
        }


class ComplaintSerializer(serializers.ModelSerializer):
    victim = PersonSerializer(required=False)  
    perpetrator = PersonSerializer(required=False)  
    complaint_image = serializers.ImageField(required=False, allow_null=True)
    complaint_audio = serializers.FileField(required=False, allow_null=True)
    complaint_video = serializers.FileField(required=False, allow_null=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all(), required=False)
    
    # New fields from the standardized payload
    src = serializers.CharField(required=False, write_only=True)
    src_uid = serializers.CharField(required=False, write_only=True)
    src_address = serializers.CharField(required=False, write_only=True)
    src_uid2 = serializers.CharField(required=False, write_only=True)
    src_usr = serializers.CharField(required=False, write_only=True)
    src_vector = serializers.CharField(required=False, write_only=True)
    src_callid = serializers.CharField(required=False, write_only=True)
    src_ts = serializers.CharField(required=False, write_only=True)
    reporters_uuid = serializers.JSONField(required=False, write_only=True)
    clients_case = serializers.JSONField(required=False, write_only=True)
    perpetrators_case = serializers.JSONField(required=False, write_only=True)
    attachments_case = serializers.JSONField(required=False, write_only=True)
    services = serializers.JSONField(required=False, write_only=True)
    knowabout116_id = serializers.CharField(required=False, write_only=True)
    case_category_id = serializers.CharField(required=False, write_only=True)
    narrative = serializers.CharField(required=False, write_only=True)
    plan = serializers.CharField(required=False, write_only=True)
    justice_id = serializers.CharField(required=False, write_only=True)
    assessment_id = serializers.CharField(required=False, write_only=True)
    priority = serializers.CharField(required=False, write_only=True)
    status = serializers.CharField(required=False, write_only=True)
    escalated_to_id = serializers.CharField(required=False, write_only=True)
    gbv_related = serializers.CharField(required=False, write_only=True)
    
    # Add metadata field if your model has it
    metadata = serializers.JSONField(required=False)

    class Meta:
        model = Complaint
        fields = [
            'complaint_id', 'session_id', 'timestamp', 'reporter_nickname', 'case_category',
            'complaint_text', 'complaint_image', 'complaint_audio', 'complaint_video',
            'message_id_ref', 'victim', 'perpetrator', 'created_at', 'conversation',
            # Add metadata field if your model has it
            'metadata',
            # New fields from standardized payload
            'src', 'src_uid', 'src_address', 'src_uid2', 'src_usr', 'src_vector', 
            'src_callid', 'src_ts', 'reporters_uuid', 'clients_case', 'perpetrators_case',
            'attachments_case', 'services', 'knowabout116_id', 'case_category_id',
            'narrative', 'plan', 'justice_id', 'assessment_id', 'priority', 'status',
            'escalated_to_id', 'gbv_related'
        ]
        read_only_fields = ['complaint_id', 'created_at', 'timestamp']

    def create(self, validated_data):
        # Extract nested data
        victim_data = validated_data.pop('victim', None)
        perpetrator_data = validated_data.pop('perpetrator', None)
        
        # Handle narrative field - map to complaint_text if needed
        if 'narrative' in validated_data and not validated_data.get('complaint_text'):
            validated_data['complaint_text'] = validated_data.pop('narrative')
        elif 'narrative' in validated_data:
            validated_data.pop('narrative')
        
        # Extract victim information from clients_case if it exists and victim_data is None
        if victim_data is None and 'clients_case' in validated_data and validated_data['clients_case']:
            client = validated_data['clients_case'][0]
            victim_data = {
                'name': client.get('fname', ''),
                'age': int(client.get('age', 0)) if client.get('age') else None,
                'gender': '',  # Map appropriate field if available
                'additional_info': ''  # Add any additional info if needed
            }
        
        # Extract perpetrator information from perpetrators_case if it exists and perpetrator_data is None
        if perpetrator_data is None and 'perpetrators_case' in validated_data and validated_data['perpetrators_case']:
            perp = validated_data['perpetrators_case'][0]
            perpetrator_data = {
                'name': perp.get('fname', ''),
                'age': int(perp.get('age', 0)) if perp.get('age') else None,
                'gender': perp.get('sex', '').replace('^', '') if perp.get('sex') else '',
                'additional_info': perp.get('notes', '')
            }
        
        # Collect all metadata fields
        metadata_fields = [
            'src', 'src_uid', 'src_address', 'src_uid2', 'src_usr', 'src_vector', 
            'src_callid', 'src_ts', 'reporters_uuid', 'clients_case', 'perpetrators_case',
            'attachments_case', 'services', 'knowabout116_id', 'case_category_id',
            'plan', 'justice_id', 'assessment_id', 'priority', 'status',
            'escalated_to_id', 'gbv_related'
        ]
        
        # Create metadata dictionary
        metadata = {}
        for field in metadata_fields:
            if field in validated_data:
                metadata[field] = validated_data.pop(field)
        
        # Set metadata if your model has this field
        if hasattr(Complaint, 'metadata'):
            validated_data['metadata'] = metadata
            
        # Create victim if data provided
        victim = None
        if victim_data:
            victim = Person.objects.create(**victim_data)
            
        # Create perpetrator if data provided
        perpetrator = None
        if perpetrator_data:
            perpetrator = Person.objects.create(**perpetrator_data)

        # Set relationship fields
        validated_data['victim'] = victim
        validated_data['perpetrator'] = perpetrator
        
        # Get reporter nickname from reporters_uuid if available
        if metadata.get('reporters_uuid') and metadata['reporters_uuid'].get('fname') and not validated_data.get('reporter_nickname'):
            validated_data['reporter_nickname'] = metadata['reporters_uuid']['fname']
            
        # If case_category_id exists but case_category doesn't, you might want to map it here
        # This would require having a mapping of IDs to category names
        
        # Create and return the complaint
        return Complaint.objects.create(**validated_data)
    
    def validate_complaint_image(self, value):
        if value and value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Image file is too large (max 5MB)")
        return value

    def validate_complaint_audio(self, value):
        if value and value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("Audio file is too large (max 10MB)")
        return value
    
    def validate_complaint_video(self, value):
        if value and value.size > 20 * 1024 * 1024:  # 20MB limit
            raise serializers.ValidationError("Video file is too large (max 20MB)")
        return value

class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['id', 'complaint', 'note_text', 'note_audio', 'created_at', 'created_by']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        # Ensure complaint field is required
        complaint = validated_data.get('complaint')
        if not complaint:
            raise serializers.ValidationError('Complaint field is required.')

        # Create and return the CaseNote instance
        return CaseNote.objects.create(**validated_data)


class ComplaintStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintStatus
        fields = ['id', 'complaint', 'status', 'updated_at', 'updated_by']
        read_only_fields = ['updated_at']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.save()
        return instance
    
    def create(self, validated_data):
        status = super().create(validated_data)
        # Log status change in system
        complaint = validated_data.get('complaint')
        if complaint:
            # Create notification for status change
            Notification.objects.create(
                complaint=complaint,
                message=f"Status updated to: {validated_data.get('status')}",
                is_read=False
            )
        return status


class VoicenotesSerializer(serializers.ModelSerializer):
    complaint = serializers.PrimaryKeyRelatedField(queryset=Complaint.objects.all(), required=False)
    
    class Meta:
        model = Voicenote
        fields = ['id', 'complaint', 'voicenote', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_voicenote(self, value):
        if value and hasattr(value, 'size') and value.size > 15 * 1024 * 1024:  # 15MB limit
            raise serializers.ValidationError("Voice note file is too large (max 15MB)")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'complaint', 'message', 'is_read', 'created_at']
        read_only_fields = ['notification_id', 'created_at']


# Serializer for simplified complaint listings
class ComplaintListSerializer(serializers.ModelSerializer):
    victim_name = serializers.SerializerMethodField()
    perpetrator_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Complaint
        fields = [
            'complaint_id', 'reporter_nickname', 'case_category',
            'created_at', 'victim_name', 'perpetrator_name', 'status'
        ]
    
    def get_victim_name(self, obj):
        return obj.victim.name if obj.victim else None
    
    def get_perpetrator_name(self, obj):
        return obj.perpetrator.name if obj.perpetrator else None
    
    def get_status(self, obj):
        status = ComplaintStatus.objects.filter(complaint=obj).order_by('-updated_at').first()
        return status.status if status else 'New'