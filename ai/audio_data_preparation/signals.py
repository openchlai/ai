import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .utils import get_audio_metadata, convert_to_relative_path, send_api_request, login

from .models import AudioProcessingTask

# Setup logging
logger = logging.getLogger(__name__)

# S3 Server API settings
S3_SERVER_BASE_URL = getattr(settings, 'S3_SERVER_BASE_URL')
PROCESSED_AUDIO_ENDPOINT = f"{S3_SERVER_BASE_URL}/transcriptions/processed-audio-files/"
DIARIZED_AUDIO_ENDPOINT = f"{S3_SERVER_BASE_URL}/transcriptions/diarized-audio-files/"

@receiver(post_save, sender=AudioProcessingTask)
def handle_preprocessing_task_completion(sender, instance, **kwargs):
    """
    Signal handler to process completed audio processing tasks.
    When a task is completed successfully and has no errors,
    this will create a ProcessedAudioFile on the S3 server.
    """
    # Check if this is a completed preprocessing task with no errors
    if (instance.status == 'completed' and 
        instance.error_message is None and 
        instance.task_type == 'preprocessing' and
        instance.output_path):
        
        logger.info(f"Processing completed task: {instance.task_id}")
        
        # Extract metadata from the processed audio file
        # The output_path contains the path to the processed file
        metadata = get_audio_metadata(instance.output_path)
        
        # Prepare data for the S3 server API
        # We need to convert the full path to a relative path for the FileField
        # Assuming the output_path is something like /mnt/shared/processed/file.wav
        # and we want to store processed/file.wav in the FileField
        rel_path = convert_to_relative_path(instance.output_path)
        
        # Prepare the request data
        request_data = {
            'processed_file': rel_path,
            'file_size': metadata['file_size'],
            'duration': metadata['duration'],
            'is_diarized': False,  # Set to True if this was a diarization task
        }
        
        logger.info(f"Sending request to create ProcessedAudioFile with data: {request_data}")

        # Send the request to create a ProcessedAudioFile
        success, response = send_api_request(
            PROCESSED_AUDIO_ENDPOINT, 
            request_data,
            instance.project_id
        )
        
        if success:
            logger.info(f"Successfully created ProcessedAudioFile for task {instance.task_id}")
        else:
            logger.error(f"Failed to create ProcessedAudioFile for task {instance.task_id}")

@receiver(post_save, sender=AudioProcessingTask)
def handle_diarization_task_completion(sender, instance, **kwargs):
    """
    Signal handler to process completed diarization tasks.
    When a diarization task is completed successfully and has no errors,
    this will create a DiarizedAudioFile for each speaker on the S3 server.
    """
    # Check if this is a completed diarization task with no errors
    if (instance.status == 'completed' and 
        instance.error_message is None and 
        instance.task_type == 'diarization' and
        instance.metadata):
        
        logger.info(f"Processing completed diarization task: {instance.task_id}")
        
        # Extract the metadata which contains speaker paths
        metadata = instance.metadata
        
        # Ensure we have the expected metadata structure
        if not ('speaker_paths' in metadata and 
                'diarization_json' in metadata and 
                metadata.get('status') == 'success'):
            logger.error(f"Invalid metadata format for diarization task {instance.task_id}")
            return
        
        # Get relative path for the diarization result JSON
        diarization_json_path = metadata['diarization_json']
        rel_diarization_json_path = convert_to_relative_path(diarization_json_path)
        
        # Process each speaker audio file
        for speaker_id, speaker_path in metadata['speaker_paths'].items():
            logger.info(f"Processing speaker {speaker_id} with audio at {speaker_path}")
            
            # Extract metadata from the speaker audio file
            speaker_metadata = get_audio_metadata(speaker_path)
            
            # Convert to relative path for storage
            rel_speaker_path = convert_to_relative_path(speaker_path)
            
            # Prepare the request data
            request_data = {
                'diarized_file': rel_speaker_path,
                'diarization_result_json_path': rel_diarization_json_path,
                'file_size': speaker_metadata['file_size'],
                'duration': speaker_metadata['duration'],
                'speaker_id': speaker_id,  # Additional info that might be useful
            }
            
            logger.info(f"Sending request to create DiarizedAudioFile with data: {request_data}")

            # Send the request to create a DiarizedAudioFile
            success, response = send_api_request(
                DIARIZED_AUDIO_ENDPOINT, 
                request_data,
                instance.project_id
            )
            
            if success:
                logger.info(f"Successfully created DiarizedAudioFile for speaker {speaker_id} in task {instance.task_id}")
            else:
                logger.error(f"Failed to create DiarizedAudioFile for speaker {speaker_id} in task {instance.task_id}")




# Initialize by logging in when the module is loaded
login()