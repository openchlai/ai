from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet, CaseNoteViewSet, ComplaintStatusUpdateView, get_complaint_status, submit_feedback, VoicenotesListCreateView, VoicenotesRetrieveUpdateDestroyView

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet)
router.register(r'case-notes', CaseNoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('complaints/<str:complaint_id>/status/', ComplaintStatusUpdateView.as_view(), name='update-complaint-status'),
    path('complaints/<str:complaint_id>/status/', get_complaint_status, name='get-complaint-status'),
    path('submit-feedback/', submit_feedback, name='submit-feedback'),
        # Voicenotes API
    path('voicenotes/', VoicenotesListCreateView.as_view(), name='voicenote-list-create'),
    path('voicenotes/<int:pk>/', VoicenotesRetrieveUpdateDestroyView.as_view(), name='voicenote-detail'),
]
