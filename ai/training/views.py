from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TrainingSessionSerializer
from training.tasks import start_whisper_training

class StartTrainingView(APIView):
    """
    API endpoint to trigger training session
    """
    def post(self, request):
        serializer = TrainingSessionSerializer(data=request.data)
        
        if serializer.is_valid():
            session_id = serializer.validated_data.get('session_id')
            config = serializer.validated_data.get('config')
            
            # Start asynchronous training task
            task = start_whisper_training.delay(session_id, config)
            
            return Response({
                'status': 'success',
                'message': 'Training started',
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainingStatusView(APIView):
    """
    API endpoint to check training status
    """
    def get(self, request, task_id):
        # Get task status (implementation depends on Celery setup)
        task = start_whisper_training.AsyncResult(task_id)
        
        response = {
            'task_id': task_id,
            'status': task.status,
        }
        
        if task.successful():
            response['result'] = task.get()
        
        return Response(response)