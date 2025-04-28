from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Complaint, CaseNote, ComplaintStatus, Voicenotes
from .serializers import ComplaintSerializer, CaseNoteSerializer, ComplaintStatusSerializer, VoicenotesSerializer
from rest_framework.views import APIView, Response
from rest_framework import generics


# View for creating and retrieving complaints
class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def create(self, request, *args, **kwargs):
        # Create a new complaint along with related victim and perpetrator if provided
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            complaint = serializer.save()
            return Response({
                'case_id': complaint.complaint_id,
                'status': 'Complaint submitted successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # Get list of all complaints (could be filtered based on query params, if needed)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# View for adding case notes
class CaseNoteViewSet(viewsets.ModelViewSet):
    queryset = CaseNote.objects.all()
    serializer_class = CaseNoteSerializer

    def create(self, request, *args, **kwargs):
        # Add a new case note to an existing complaint
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            case_note = serializer.save()
            return Response({
                'message': 'Case note added successfully',
                'case_note_id': case_note.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # List all case notes (can be filtered by complaint_id if needed)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# View for updating complaint status
class ComplaintStatusUpdateView(APIView):
    def put(self, request, *args, **kwargs):
        # Update the status of an existing complaint
        complaint_id = kwargs.get('complaint_id')
        complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
        if not complaint:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate and update status
        serializer = ComplaintStatusSerializer(data=request.data)
        if serializer.is_valid():
            status_data = serializer.save(complaint=complaint)
            return Response({
                'status': status_data.status,
                'message': 'Complaint status updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for retrieving the status of a complaint
@api_view(['GET'])
def get_complaint_status(request, complaint_id):
    # Retrieve the status of a complaint
    complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
    if not complaint:
        return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

    # Fetch the most recent status update
    status = ComplaintStatus.objects.filter(complaint=complaint).order_by('-updated_at').first()
    if not status:
        return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'case_id': complaint.complaint_id,
        'status': status.status,
        'updated_at': status.updated_at,
        'updated_by': status.updated_by
    })

# View for submitting feedback (optional step for the reporter)
@api_view(['POST'])
def submit_feedback(request):
    # Submit feedback related to a case (e.g., satisfaction or additional comments)
    feedback_data = request.data
    # Handle feedback submission logic here
    # For simplicity, assuming feedback is just a text field
    feedback = feedback_data.get('feedback')
    if feedback:
        return Response({'message': 'Feedback submitted successfully'}, status=status.HTTP_200_OK)
    return Response({'error': 'Feedback cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

# Generic view for Voicenotes Model (List, Create, Retrieve, Update, Destroy)
class VoicenotesListCreateView(generics.ListCreateAPIView):
    queryset = Voicenotes.objects.all()
    serializer_class = VoicenotesSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed

class VoicenotesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voicenotes.objects.all()
    serializer_class = VoicenotesSerializer
    #permission_classes = [IsAuthenticated]  # Adjust permissions as needed