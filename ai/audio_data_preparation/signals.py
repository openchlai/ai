import os
import time
import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import AudioProcessingTask

# Setup logging
logger = logging.getLogger(__name__)

# S3 Server API settings
S3_SERVER_BASE_URL = getattr(settings, 'S3_SERVER_BASE_URL')
PROCESSED_AUDIO_ENDPOINT = f"{S3_SERVER_BASE_URL}/transcriptions/processed-audio-files/"

# Authentication settings
AUTH_ENDPOINT = getattr(settings, 'AUTH_ENDPOINT')
AUTH_CREDENTIALS = {
    'whatsapp_number': getattr(settings, 'AUTH_WHATSAPP', ''),
    'password': getattr(settings, 'AUTH_PASSWORD', '')
}
TOKEN_LIFETIME = getattr(settings, 'TOKEN_LIFETIME', 1800)  # 1 hour default

# Global variables for authentication
auth_token = None
token_expiry = 0

# Authentication functions
def login():
    """Authenticate and get JWT token."""
    global auth_token, token_expiry
    
    try:
        logger.info("Authenticating with S3 API...")
        response = requests.post(AUTH_ENDPOINT, json=AUTH_CREDENTIALS)
        
        if response.status_code in [200, 201]:
            token_data = response.json()
            auth_token = token_data.get('access')
            
            # Set token expiry time (current time + token lifetime)
            token_expiry = time.time() + TOKEN_LIFETIME
            
            logger.info("Authentication successful")
            return True
        else:
            logger.error(f"Authentication failed. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False

def get_auth_header():
    """Get authorization header with valid token."""
    global auth_token, token_expiry
    
    # If token doesn't exist or is about to expire (within 5 minutes), refresh it
    if auth_token is None or time.time() > (token_expiry - 300):
        if not login():
            logger.error("Failed to obtain valid authentication token")
            return {}
    
    return {"Authorization": f"Bearer {auth_token}"}

# Helper function for sending API requests
def send_api_request(endpoint, data, project_id, retry=True):
    """Send POST requests to API endpoints with authentication."""
    try:
        # Get authentication header
        auth_header = get_auth_header()
        headers = {
            "Content-Type": "application/json",
            "X-Project-ID": str(project_id),
            **auth_header
        }
        
        response = requests.post(endpoint, json=data, headers=headers)
        
        # Handle successful response
        if response.status_code in [200, 201]:
            logger.info(f"Successfully sent data to {endpoint}")
            return True, response.json()
            
        # Handle authentication errors
        elif response.status_code in [401, 403] and retry:
            logger.warning("Token expired or invalid. Attempting to refresh token...")
            if login():
                # Retry the request with new token
                return send_api_request(endpoint, data, project_id, retry=False)
            else:
                logger.error("Failed to refresh authentication token")
                return False, None
                
        # Handle other errors
        else:
            logger.error(f"Failed to send data to {endpoint}. Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error sending request to {endpoint}: {str(e)}")
        return False, None

def get_audio_metadata(file_path):
    """Extract metadata from audio file."""
    try:
        # This is just a placeholder - you would use a library like pydub or librosa
        # to extract actual metadata from the audio file
        import os
        from pydub import AudioSegment
        import wave
        
        file_size = os.path.getsize(file_path)
        
        # Try to get audio duration
        try:
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception:
            # Fallback to wave for wave files
            try:
                with wave.open(file_path, 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
            except Exception:
                duration = None
                
        return {
            'file_size': file_size,
            'duration': duration
        }
    except Exception as e:
        logger.error(f"Error extracting audio metadata: {str(e)}")
        return {
            'file_size': None,
            'duration': None
        }

@receiver(post_save, sender=AudioProcessingTask)
def handle_task_completion(sender, instance, **kwargs):
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
        rel_path = instance.output_path
        
        # If the path starts with a mount point like /mnt/shared/, remove it
        # to get a relative path
        mount_prefixes = ['/mnt/shared/', '/ai/shared/', 'shared/']
        for prefix in mount_prefixes:
            if rel_path.startswith(prefix):
                rel_path = rel_path[len(prefix):]
                break
        
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

# Initialize by logging in when the module is loaded
login()