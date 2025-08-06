from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Contact, ContactType, ContactTag, ContactGroup,
    ContactContactType, ContactTagAssignment, ContactInteraction
)

User = get_user_model()

class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactType
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'tenant')

class ContactTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactTag
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'tenant')

class ContactGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactGroup
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'tenant')

class ContactContactTypeSerializer(serializers.ModelSerializer):
    contact_type = ContactTypeSerializer(read_only=True)
    contact_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContactType.objects.all(),
        source='contact_type',
        write_only=True
    )

    class Meta:
        model = ContactContactType
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'assigned_at', 'assigned_by')

class ContactTagAssignmentSerializer(serializers.ModelSerializer):
    tag = ContactTagSerializer(read_only=True)
    tag_id = serializers.PrimaryKeyRelatedField(
        queryset=ContactTag.objects.all(),
        source='tag',
        write_only=True
    )

    class Meta:
        model = ContactTagAssignment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'assigned_at', 'assigned_by')

class ContactInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInteraction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ContactSerializer(serializers.ModelSerializer):
    types = ContactContactTypeSerializer(source='contactcontacttype_set', many=True, read_only=True)
    tags = ContactTagAssignmentSerializer(source='contacttagassignment_set', many=True, read_only=True)
    groups = ContactGroupSerializer(many=True, read_only=True)
    type_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContactType.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContactTag.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContactGroup.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    full_name = serializers.CharField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    last_modified_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'tenant')

    def validate_email(self, value):
        """Ensure email is unique within the tenant"""
        if value:
            tenant = self.context['request'].tenant
            if Contact.objects.filter(tenant=tenant, email=value).exists():
                if self.instance is None or self.instance.email != value:
                    raise serializers.ValidationError("A contact with this email already exists.")
        return value

    def create(self, validated_data):
        """Handle creation with many-to-many relationships"""
        type_ids = validated_data.pop('type_ids', [])
        tag_ids = validated_data.pop('tag_ids', [])
        group_ids = validated_data.pop('group_ids', [])

        contact = Contact.objects.create(**validated_data)
        
        # Set the current user as the assigned_by for types and tags
        user = self.context['request'].user
        
        # Add types
        for type_id in type_ids:
            ContactContactType.objects.create(
                contact=contact,
                contact_type=type_id,
                assigned_by=user
            )
        
        # Add tags
        for tag_id in tag_ids:
            ContactTagAssignment.objects.create(
                contact=contact,
                tag=tag_id,
                assigned_by=user
            )
        
        # Add groups
        contact.groups.set(group_ids)
        
        return contact

    def update(self, instance, validated_data):
        """Handle update with many-to-many relationships"""
        type_ids = validated_data.pop('type_ids', None)
        tag_ids = validated_data.pop('tag_ids', None)
        group_ids = validated_data.pop('group_ids', None)
        
        user = self.context['request'].user
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.last_modified_by = user
        instance.save()
        
        # Update types if provided
        if type_ids is not None:
            current_types = set(instance.types.values_list('id', flat=True))
            new_types = set(t.id for t in type_ids)
            
            # Remove types not in the new set
            for type_id in current_types - new_types:
                ContactContactType.objects.filter(
                    contact=instance,
                    contact_type_id=type_id
                ).delete()
            
            # Add new types
            for type_id in new_types - current_types:
                ContactContactType.objects.create(
                    contact=instance,
                    contact_type_id=type_id,
                    assigned_by=user
                )
        
        # Update tags if provided
        if tag_ids is not None:
            current_tags = set(instance.tags.values_list('id', flat=True))
            new_tags = set(t.id for t in tag_ids)
            
            # Remove tags not in the new set
            for tag_id in current_tags - new_tags:
                ContactTagAssignment.objects.filter(
                    contact=instance,
                    tag_id=tag_id
                ).delete()
            
            # Add new tags
            for tag_id in new_tags - current_tags:
                ContactTagAssignment.objects.create(
                    contact=instance,
                    tag_id=tag_id,
                    assigned_by=user
                )
        
        # Update groups if provided
        if group_ids is not None:
            instance.groups.set(group_ids)
        
        return instance

class ContactListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing contacts"""
    full_name = serializers.CharField(read_only=True)
    primary_type = serializers.SerializerMethodField()
    primary_tag = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id', 'full_name', 'email', 'phone', 'organization', 'job_title',
            'primary_type', 'primary_tag', 'is_active', 'created_at'
        )
        read_only_fields = fields

    def get_primary_type(self, obj):
        first_type = obj.types.first()
        return first_type.name if first_type else None

    def get_primary_tag(self, obj):
        first_tag = obj.tags.first()
        return first_tag.name if first_tag else None