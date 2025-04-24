from rest_framework import serializers
from .models import Complaint, CaseNote, ComplaintStatus, Person, Voicenotes

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'age', 'gender', 'additional_info']
        extra_kwargs = {
            'age': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True, 'allow_blank': True},
            'additional_info': {'required': False, 'allow_blank': True},
        }

# Serializer for the Complaint model
from rest_framework import serializers
from .models import Complaint, Person
from rest_framework import serializers
from .models import Complaint, Person

class ComplaintSerializer(serializers.ModelSerializer):
    victim = PersonSerializer(required=False)  
    perpetrator = PersonSerializer(required=False)  
    complaint_image = serializers.ImageField(required=False, allow_null=True)
    complaint_audio = serializers.FileField(required=False, allow_null=True)  # Ensure FileField is handled
    complaint_video = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Complaint
        fields = [
            'complaint_id', 'session_id', 'timestamp', 'reporter_nickname', 'case_category',
            'complaint_text', 'complaint_image', 'complaint_audio', 'complaint_video',
            'message_id_ref', 'victim', 'perpetrator', 'created_at'
        ]
        read_only_fields = ['complaint_id', 'created_at', 'timestamp']

    def create(self, validated_data):
        victim_data = validated_data.pop('victim', None)
        perpetrator_data = validated_data.pop('perpetrator', None)

        victim = Person.objects.create(**victim_data) if victim_data else None
        perpetrator = Person.objects.create(**perpetrator_data) if perpetrator_data else None

        validated_data['victim'] = victim
        validated_data['perpetrator'] = perpetrator

        return Complaint.objects.create(**validated_data)


# Serializer for the CaseNote model
class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['complaint', 'note_text', 'note_audio', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'complaint']

    def create(self, validated_data):
        # Ensure complaint field is required
        complaint = validated_data.get('complaint')
        if not complaint:
            raise serializers.ValidationError('Complaint field is required.')

        # Create and return the CaseNote instance
        case_note = CaseNote.objects.create(**validated_data)
        return case_note

# Serializer for the ComplaintStatus model
class ComplaintStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintStatus
        fields = ['complaint', 'status', 'updated_at', 'updated_by']
        read_only_fields = ['complaint', 'updated_at']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.save()
        return instance

# Serializer for Voicenotes model
class VoicenotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voicenotes
        fields = ['id', 'voicenote', 'created_at']
