# audio_data_preparation/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AudioProcessingTask
from .serializers import (
    AudioProcessingTaskSerializer,
    AudioPreprocessingRequestSerializer,
    SpeakerDiarizationRequestSerializer,
    AudioChunkingRequestSerializer,
    TaskStatusSerializer,
)
from .tasks import create_task, run_task_async


class AudioPreprocessingView(APIView):
    """
    API endpoint for audio preprocessing.
    """

    def post(self, request, format=None):
        serializer = AudioPreprocessingRequestSerializer(data=request.data)
        if serializer.is_valid():
            audio_path = serializer.validated_data["audio_path"]
            project_id = request.data.get("project_id")

            # Create task
            task = create_task(
                "preprocessing",
                project_id,
                audio_path,
                noise_reduction=serializer.validated_data.get("noise_reduction", 0.3),
                normalize=serializer.validated_data.get("normalize", True),
            )

            # Start processing in background
            run_task_async(task.task_id)

            # Return task info
            task_serializer = AudioProcessingTaskSerializer(task)
            return Response(
                {
                    "task_id": task.task_id,
                    "status": "processing",
                    "message": "Audio preprocessing started",
                    "task": task_serializer.data,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpeakerDiarizationView(APIView):
    """
    API endpoint for speaker diarization.
    """

    def post(self, request, format=None):
        serializer = SpeakerDiarizationRequestSerializer(data=request.data)
        if serializer.is_valid():
            audio_path = serializer.validated_data["audio_path"]
            project_id = request.data.get("project_id")

            # Create task
            task = create_task(
                "diarization",
                project_id,
                audio_path,
                min_speakers=serializer.validated_data.get("min_speakers", 2),
                max_speakers=serializer.validated_data.get("max_speakers", 2),
            )

            # Start processing in background
            run_task_async(task.task_id)

            # Return task info
            task_serializer = AudioProcessingTaskSerializer(task)
            return Response(
                {
                    "task_id": task.task_id,
                    "status": "processing",
                    "message": "Speaker diarization started",
                    "task": task_serializer.data,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioChunkingView(APIView):
    """
    API endpoint for audio chunking.
    """

    def post(self, request, format=None):
        serializer = AudioChunkingRequestSerializer(data=request.data)
        if serializer.is_valid():
            audio_path = serializer.validated_data["audio_path"]
            project_id = request.data.get("project_id")

            # Create task
            task = create_task(
                "chunking",
                project_id,
                audio_path,
                diarization_result=serializer.validated_data.get("diarization_result"),
                max_length=serializer.validated_data.get("max_length", 10.0),
                overlap=serializer.validated_data.get("overlap", 2.0),
                min_chunk=serializer.validated_data.get("min_chunk", 1.0),
            )

            # Start processing in background
            run_task_async(task.task_id)

            # Return task info
            task_serializer = AudioProcessingTaskSerializer(task)
            return Response(
                {
                    "task_id": task.task_id,
                    "status": "processing",
                    "message": "Audio chunking started",
                    "task": task_serializer.data,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskStatusView(APIView):
    """
    API endpoint for checking task status.
    """

    def get(self, request, task_id=None, format=None):
        if task_id:
            # Get status for specific task
            try:
                task = AudioProcessingTask.objects.get(task_id=task_id)
                result = task.get_output_details()
                return Response(result)
            except AudioProcessingTask.DoesNotExist:
                return Response(
                    {"error": f"Task with ID {task_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            # Check if task_id was provided in query params
            serializer = TaskStatusSerializer(data=request.query_params)
            if serializer.is_valid():
                task_id = serializer.validated_data["task_id"]
                try:
                    task = AudioProcessingTask.objects.get(task_id=task_id)
                    result = task.get_output_details()
                    return Response(result)
                except AudioProcessingTask.DoesNotExist:
                    return Response(
                        {"error": f"Task with ID {task_id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # If no task_id provided, return list of recent tasks
            tasks = AudioProcessingTask.objects.all().order_by("-created_at")[:10]
            task_serializer = AudioProcessingTaskSerializer(tasks, many=True)
            return Response({"tasks": task_serializer.data})


class TaskListView(APIView):
    """
    API endpoint for listing tasks.
    """

    def get(self, request, format=None):
        # Get optional filters from query params
        task_type = request.query_params.get("type")
        status_filter = request.query_params.get("status")

        # Apply filters
        tasks = AudioProcessingTask.objects.all()
        if task_type:
            tasks = tasks.filter(task_type=task_type)
        if status_filter:
            tasks = tasks.filter(status=status_filter)

        # Sort by creation time
        tasks = tasks.order_by("-created_at")

        # Paginate (simple implementation)
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))

        tasks = tasks[offset : offset + limit]

        # Serialize and return
        task_serializer = AudioProcessingTaskSerializer(tasks, many=True)
        return Response({"count": tasks.count(), "tasks": task_serializer.data})
