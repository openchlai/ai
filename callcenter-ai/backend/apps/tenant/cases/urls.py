from django.urls import path
from .views import (
    CaseTypeListAPIView, CaseStatusListAPIView,
    CaseListCreateAPIView, CaseRetrieveUpdateDestroyAPIView,
    CaseDocumentListCreateAPIView, CaseDocumentRetrieveUpdateDestroyAPIView,
    CaseNoteListCreateAPIView, CaseNoteRetrieveUpdateDestroyAPIView,
    ProtectionDetailRetrieveUpdateAPIView, SafetyPlanRetrieveUpdateAPIView,
    CaseStatusUpdateAPIView, CaseBulkUpdateAPIView
)

urlpatterns = [
    # Case Types and Statuses
    path('case-types/', CaseTypeListAPIView.as_view(), name='case-type-list'),
    path('case-statuses/', CaseStatusListAPIView.as_view(), name='case-status-list'),
    
    # Cases
    path('cases/', CaseListCreateAPIView.as_view(), name='case-list'),
    path('cases/<int:pk>/', CaseRetrieveUpdateDestroyAPIView.as_view(), name='case-detail'),
    
    # Case Documents
    path('cases/<int:case_id>/documents/', CaseDocumentListCreateAPIView.as_view(), name='case-document-list'),
    path('cases/<int:case_id>/documents/<int:pk>/', CaseDocumentRetrieveUpdateDestroyAPIView.as_view(), name='case-document-detail'),
    
    # Case Notes
    path('cases/<int:case_id>/notes/', CaseNoteListCreateAPIView.as_view(), name='case-note-list'),
    path('cases/<int:case_id>/notes/<int:pk>/', CaseNoteRetrieveUpdateDestroyAPIView.as_view(), name='case-note-detail'),
    
    # Protection Case Features
    path('cases/<int:case_id>/protection-details/', ProtectionDetailRetrieveUpdateAPIView.as_view(), name='protection-details'),
    path('cases/<int:case_id>/safety-plan/', SafetyPlanRetrieveUpdateAPIView.as_view(), name='safety-plan'),
    
    # Workflow Actions
    path('cases/<int:case_id>/change-status/', CaseStatusUpdateAPIView.as_view(), name='change-status'),
    path('cases/bulk-update/', CaseBulkUpdateAPIView.as_view(), name='bulk-update'),
]