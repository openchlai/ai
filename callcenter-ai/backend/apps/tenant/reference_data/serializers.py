from rest_framework import serializers
from .models import ReferenceDataType, ReferenceData, ReferenceDataHistory


class ReferenceDataTypeSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    updated_by = serializers.ReadOnlyField(source='updated_by.username')
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = ReferenceDataType
        fields = '__all__'
        # read_only_fields = ['id', 'created_at', 'updated_at']


class ReferenceDataSerializer(serializers.ModelSerializer):
    data_type_name = serializers.ReadOnlyField(source='data_type.name')
    tenant_name = serializers.ReadOnlyField(source='tenant.name')  # Optional if Tenant has `name`

    class Meta:
        model = ReferenceData
        fields = '__all__'
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']


class ReferenceDataHistorySerializer(serializers.ModelSerializer):
    reference_data_display = serializers.ReadOnlyField(source='reference_data.display_value')
    data_type = serializers.ReadOnlyField(source='reference_data.data_type.name')

    class Meta:
        model = ReferenceDataHistory
        fields = [
            'id',
            'reference_data',
            'reference_data_display',
            'data_type',
            'version',
            'change_reason',
            'changed_fields',
            'previous_state',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
