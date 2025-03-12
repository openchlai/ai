# Authentication functions
import logging
import time
from django.conf import settings
import requests

# Setup logging
logger = logging.getLogger(__name__)

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


def convert_to_relative_path(full_path):
    """
    Convert a full path to a relative path by removing mount point prefixes.
    
    Args:
        full_path (str): The full path including mount points
        
    Returns:
        str: The relative path without mount points
    """
    # List of possible mount point prefixes
    mount_prefixes = ['/mnt/shared/', '/ai/shared/', 'shared/']
    
    # Remove mount prefix if present
    rel_path = full_path
    for prefix in mount_prefixes:
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix):]
            break
    
    return rel_path