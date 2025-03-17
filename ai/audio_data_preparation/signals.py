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
CHUCKED_AUDIO_ENDPOINT = f"{S3_SERVER_BASE_URL}/transcriptions/audio-chunks/"

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

@receiver(post_save, sender=AudioProcessingTask)
def handle_chunking_task_completion(sender, instance, **kwargs):
    """
    Signal handler to process completed chunking tasks.
    When a chunking task is completed successfully and has no errors,
    this will create AudioChunk objects for each chunk on the S3 server.
    """
    # Check if this is a completed chunking task with no errors
    if (instance.status == 'completed' and 
        instance.error_message is None and 
        instance.task_type == 'chunking' and
        instance.metadata):
        
        logger.info(f"Processing completed chunking task: {instance.task_id}")
        
        # Extract the metadata which contains chunk paths
        metadata = instance.metadata
        
        # Ensure we have the expected metadata structure
        if not ('chunks' in metadata and 
                'speaker' in metadata and 
                metadata.get('status') == 'success'):
            logger.error(f"Invalid metadata format for chunking task {instance.task_id}")
            return
        
        # Get speaker information from metadata
        speaker = metadata.get('speaker', '')
        
        # Process each audio chunk
        for chunk in metadata['chunks']:
            logger.info(f"Processing chunk {chunk.get('chunk_id')} with path {chunk.get('path')}")
            
            # Extract path and duration
            chunk_path = chunk.get('path')
            duration = float(chunk.get('duration', 0))
            
            # Skip if missing essential data
            if not chunk_path:
                logger.warning(f"Missing path for chunk in task {instance.task_id}")
                continue
            
            # Get additional metadata from the audio file if needed
            try:
                chunk_metadata = get_audio_metadata(chunk_path)
                # If duration wasn't in the JSON, try to get it from the file
                if duration == 0 and 'duration' in chunk_metadata:
                    duration = chunk_metadata['duration']
            except Exception as e:
                logger.warning(f"Error getting metadata for chunk {chunk_path}: {str(e)}")
                # Continue with available information
            
            # Convert to relative path for storage
            rel_chunk_path = convert_to_relative_path(chunk_path)
            
            # Prepare the request data
            request_data = {
                'chunk_file': rel_chunk_path,
                'duration': duration,
                # Default values for optional fields
                # 'gender': 'not_sure',
                # 'locale': 'EN',
                # Additional metadata that might be useful
                # 'speaker_id': speaker,
                # 'start_time': float(chunk.get('start', 0)),
                # 'end_time': float(chunk.get('end', 0)),
                # 'chunk_id': chunk.get('chunk_id', '')
            }
            
            logger.info(f"Sending request to create AudioChunk with data: {request_data}")

            # Send the request to create an AudioChunk
            success, response = send_api_request(
                CHUCKED_AUDIO_ENDPOINT, 
                request_data,
                instance.project_id
            )
            
            if success:
                logger.info(f"Successfully created AudioChunk for {chunk.get('chunk_id')} in task {instance.task_id}")
            else:
                logger.error(f"Failed to create AudioChunk for {chunk.get('chunk_id')} in task {instance.task_id}")


# Initialize by logging in when the module is loaded
login()