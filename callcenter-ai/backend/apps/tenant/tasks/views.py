# views.py
from rest_framework import generics
from .models import Task, TaskTag, TaskTagging, TaskComment, TaskAttachment, TaskReminder, TaskChangeLog
from .serializers import (
    TaskSerializer, TaskTagSerializer, TaskTaggingSerializer,
    TaskCommentSerializer, TaskAttachmentSerializer, TaskReminderSerializer,
    TaskChangeLogSerializer
)


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskTagListCreateView(generics.ListCreateAPIView):
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer


class TaskTaggingListCreateView(generics.ListCreateAPIView):
    queryset = TaskTagging.objects.all()
    serializer_class = TaskTaggingSerializer


class TaskCommentListCreateView(generics.ListCreateAPIView):
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer


class TaskAttachmentListCreateView(generics.ListCreateAPIView):
    queryset = TaskAttachment.objects.all()
    serializer_class = TaskAttachmentSerializer


class TaskReminderListCreateView(generics.ListCreateAPIView):
    queryset = TaskReminder.objects.all()
    serializer_class = TaskReminderSerializer


class TaskChangeLogListView(generics.ListAPIView):
    queryset = TaskChangeLog.objects.all()
    serializer_class = TaskChangeLogSerializer

