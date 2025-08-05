from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    DocumentType, Document, DocumentVersion,
    DocumentAccessLog, DocumentShareLink,
    DocumentPreview, DocumentTemplate
)
from .serializers import (
    DocumentTypeSerializer, DocumentSerializer,
    DocumentVersionSerializer, DocumentAccessLogSerializer,
    DocumentShareLinkSerializer, DocumentPreviewSerializer,
    DocumentTemplateSerializer
)

class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        document = self.get_object()
        versions = document.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)


class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentAccessLog.objects.all()
    serializer_class = DocumentAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentShareLinkViewSet(viewsets.ModelViewSet):
    queryset = DocumentShareLink.objects.all()
    serializer_class = DocumentShareLinkSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentPreviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentPreview.objects.all()
    serializer_class = DocumentPreviewSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
