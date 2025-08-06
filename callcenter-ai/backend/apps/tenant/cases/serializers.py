from apps.shared.accounts.models import User
from rest_framework import serializers
from .models import (
    CasePriority, CaseStatus, CaseType, Case, CaseDocument, CaseNote, 
    CaseHistory, ProtectionDetail, SafetyPlan
)

class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ProtectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtectionDetail
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class SafetyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyPlan
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CaseDocumentSerializer(serializers.ModelSerializer): 
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = CaseDocument
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'file_size', 'file_type')

    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB")
        return value

class CaseNoteSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    
    class Meta:
        model = CaseNote
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CaseHistorySerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    from_status = serializers.StringRelatedField()
    to_status = serializers.StringRelatedField()
    
    class Meta:
        model = CaseHistory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CaseSerializer(serializers.ModelSerializer):
    case_type = CaseTypeSerializer(read_only=True)
    case_type_id = serializers.PrimaryKeyRelatedField(
        queryset=CaseType.objects.all(),
        write_only=True,
        source='case_type'
    )
    # assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='assigned_to',
        allow_null=True
    )
    protection_details = ProtectionDetailSerializer(read_only=True)
    safety_plan = SafetyPlanSerializer(read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)
    notes = CaseNoteSerializer(many=True, read_only=True)
    history = CaseHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = (
            'created_at', 'updated_at', 'case_number', 
            'resolved_at', 'resolved_by', 'survivor_code'
        )
    
    def validate(self, data):
        if data.get('case_type') and data['case_type'].category in ['vac', 'gbv']:
            if not data.get('incident_date'):
                raise serializers.ValidationError(
                    "Incident date is required for protection cases"
                )
        return data
    
    def create(self, validated_data):
        case = super().create(validated_data)
        if case.case_type.category in ['vac', 'gbv']:
            ProtectionDetail.objects.create(case=case)
        return case

class CaseStatusUpdateSerializer(serializers.Serializer):
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=CaseStatus.objects.all()
    )
    comment = serializers.CharField(required=False)
    
    def validate(self, data):
        case = self.context['case']
        new_status = data['status_id']
        
        if not case.status.allowed_next_statuses.filter(id=new_status.id).exists():
            raise serializers.ValidationError(
                f"Cannot change status from {case.status} to {new_status}"
            )
        
        if new_status.requires_supervisor_review:
            if not self.context['request'].user.has_perm('cases.approve_status_change'):
                raise serializers.ValidationError(
                    "This status change requires supervisor approval"
                )
        return data

class CaseBulkUpdateSerializer(serializers.Serializer):
    case_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    priority = serializers.ChoiceField(
        choices=CasePriority.choices,
        required=False
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    
class CaseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseStatus
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        