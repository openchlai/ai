# audio_data_preparation/models.py

from django.db import models
import json
import os

class AudioProcessingTask(models.Model):
    """
    Tracks audio processing tasks and their status
    """
    TASK_TYPES = (
        ('preprocessing', 'Audio Preprocessing'),
        ('diarization', 'Speaker Diarization'),
        ('chunking', 'Audio Chunking'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    task_id = models.CharField(max_length=100, unique=True)
    project_id = models.UUIDField()
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    input_path = models.CharField(max_length=255)
    output_path = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Store additional metadata as JSON
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.task_type} - {self.task_id} ({self.status})"
    
    def update_status(self, status, output_path=None, metadata=None, error_message=None):
        """Update task status and related fields"""
        self.status = status
        
        if output_path:
            self.output_path = output_path
            
        if metadata:
            self.metadata = metadata
            
        if error_message:
            self.error_message = error_message
            
        if status == 'completed' or status == 'failed':
            from django.utils import timezone
            self.completed_at = timezone.now()
            
        self.save()
    
    def get_output_details(self):
        """Get details about the output of the task"""
        if self.status != 'completed':
            return {"status": self.status}
        
        # Return different details based on task type
        if self.task_type == 'preprocessing':
            return {
                "status": self.status,
                "output_path": self.output_path,
                "audio_details": self.metadata.get('audio_details', {})
            }
            
        elif self.task_type == 'diarization':
            return {
                "status": self.status,
                "output_path": self.output_path,
                "speaker_count": self.metadata.get('speaker_count', 0),
                "speaker_paths": self.metadata.get('speaker_paths', {})
            }
            
        elif self.task_type == 'chunking':
            return {
                "status": self.status,
                "output_dir": self.output_path,
                "chunk_count": self.metadata.get('chunk_count', 0),
                "chunks": self.metadata.get('chunks', [])
            }
            
        return {"status": self.status, "output_path": self.output_path}