from rest_framework import serializers
from .models import (
    Task, TaskTag, TaskTagging, TaskComment,
    TaskAttachment, TaskReminder, TaskChangeLog
)

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = '__all__'

class TaskTaggingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTagging
        fields = '__all__'

class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = '__all__'

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = '__all__'

class TaskReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReminder
        fields = '__all__'

class TaskChangeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskChangeLog
        fields = '__all__'
