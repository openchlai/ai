from rest_framework import serializers
from .models import (
    DocumentType, Document, DocumentVersion,
    DocumentAccessLog, DocumentShareLink,
    DocumentPreview, DocumentTemplate
)

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('file_size', 'file_hash', 'version')


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = '__all__'


class DocumentAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAccessLog
        fields = '__all__'


class DocumentShareLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentShareLink
        fields = '__all__'
        read_only_fields = ('token',)


class DocumentPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentPreview
        fields = '__all__'


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
