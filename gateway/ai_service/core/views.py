from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import AudioFile
from .serializers import AudioFileSerializer
from .tasks import process_audio_pipeline
from celery.result import AsyncResult
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class AudioUploadView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        # Validate and save uploaded file
        serializer = AudioFileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_instance = serializer.save()
        logger.info(f"Audio file uploaded: {audio_instance.audio.path}")

        # Dispatch Celery task
        task = process_audio_pipeline.delay(audio_instance.id, audio_instance.audio.path)
        logger.info(f"Task {task.id} started for audio ID {audio_instance.id}")

        return Response({
            "message": "Audio uploaded and processing started.",
            "audio_id": audio_instance.id,
            "task_id": task.id,
            "status_check_url": f"/api/task_status/{task.id}/"
        }, status=status.HTTP_202_ACCEPTED)


class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "status": result.status,
        }

        if result.status == 'SUCCESS':
            response["result"] = result.result
        elif result.status == 'FAILURE':
            response["error"] = str(result.result)

        return Response(response, status=status.HTTP_200_OK)


class HealthView(APIView):
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "ai_service"
        }, status=status.HTTP_200_OK)
