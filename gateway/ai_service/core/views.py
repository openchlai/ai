# core/views.py
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
        try:
            result = AsyncResult(task_id)
            response = {
                "task_id": task_id,
                "status": result.status,
                "timestamp": result.date_done.isoformat() if result.date_done else None,
            }

            if result.status == 'SUCCESS':
                response["result"] = result.result
                response["completed"] = True
                response["progress"] = 100
            elif result.status == 'FAILURE':
                response["error"] = str(result.result)
                response["completed"] = False
                response["progress"] = 0
            elif result.status == 'PENDING':
                response["message"] = "Task is queued and waiting to start"
                response["completed"] = False
                response["progress"] = 0
            elif result.status == 'RETRY':
                response["message"] = "Task is retrying after an error"
                response["completed"] = False
                response["progress"] = 25
            elif result.status == 'PROGRESS':
                # Get task meta information for progress tracking
                if hasattr(result, 'info') and result.info:
                    response["meta"] = result.info
                    response["progress"] = result.info.get('progress', 50)
                    response["stage"] = result.info.get('stage', 'processing')
                    response["message"] = f"Processing: {response['stage']}"
                else:
                    response["progress"] = 50
                    response["message"] = "Task is in progress"
                response["completed"] = False

            return Response(response, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error checking task status for {task_id}: {e}")
            return Response({
                "task_id": task_id,
                "status": "ERROR",
                "error": "Failed to retrieve task status",
                "completed": False,
                "progress": 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AudioResultView(APIView):
    def get(self, request, audio_id):
        try:
            audio_file = AudioFile.objects.get(id=audio_id)
            serializer = AudioFileSerializer(audio_file)
            
            # Check if processing is complete
            is_processed = bool(
                audio_file.transcript and 
                audio_file.insights and 
                audio_file.summary
            )
            
            response_data = serializer.data
            response_data.update({
                "is_processed": is_processed,
                "has_transcript": bool(audio_file.transcript),
                "has_insights": bool(audio_file.insights),
                "has_summary": bool(audio_file.summary),
                "has_translation": bool(audio_file.translated_text),
                "has_annotations": bool(audio_file.annotated_text),
            })
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except AudioFile.DoesNotExist:
            return Response({
                "error": "Audio file not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving audio result for {audio_id}: {e}")
            return Response({
                "error": "Failed to retrieve audio file"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthView(APIView):
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "ai_service"
        }, status=status.HTTP_200_OK)
