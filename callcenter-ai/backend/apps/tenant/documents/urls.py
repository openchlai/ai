from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentTypeViewSet, DocumentViewSet, DocumentVersionViewSet,
    DocumentAccessLogViewSet, DocumentShareLinkViewSet,
    DocumentPreviewViewSet, DocumentTemplateViewSet
)

router = DefaultRouter()
router.register(r'types', DocumentTypeViewSet, basename='document-type')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'versions', DocumentVersionViewSet, basename='document-version')
router.register(r'access-logs', DocumentAccessLogViewSet, basename='access-log')
router.register(r'share-links', DocumentShareLinkViewSet, basename='share-link')
router.register(r'previews', DocumentPreviewViewSet, basename='preview')
router.register(r'templates', DocumentTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
