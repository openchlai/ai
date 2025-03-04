import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class BackendClient:
    """
    Client for communicating with the main backend API
    """
    def __init__(self):
        self.base_url = settings.MAIN_BACKEND_URL
        self.token = None
    
    def _get_auth_token(self):
        """
        Get JWT token for API authentication
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/staff-token/",
                data={
                    'whatsapp_number': settings.MAIN_BACKEND_NUMBER,
                    'password': settings.MAIN_BACKEND_PASSWORD
                }
            )
            response.raise_for_status()
            return response.json().get('access')
        except Exception as e:
            logger.error(f"Failed to get auth token: {str(e)}")
            raise
    
    def _get_auth_headers(self):
        """
        Get headers with authentication token
        """
        if self.token is None:
            self.token = self._get_auth_token()
            
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, endpoint, data=None):
        """
        Make authenticated request to backend API
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_auth_headers()
        
        try:
            response = method(url, json=data, headers=headers)
            
            # If unauthorized, refresh token and retry
            if response.status_code == 401:
                self.token = self._get_auth_token()
                headers = self._get_auth_headers()
                response = method(url, json=data, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
    
    def send_progress_update(self, session_id, progress_data):
        """
        Send training progress update
        """
        endpoint = f"train/sessions/{session_id}/progress/"
        return self._make_request(requests.post, endpoint, progress_data)
    
    def send_evaluation_metrics(self, session_id, metrics_data):
        """
        Send evaluation metrics
        """
        endpoint = f"train/sessions/{session_id}/evaluation/"
        return self._make_request(requests.post, endpoint, metrics_data)
    
    def update_session_status(self, session_id, status, error_details=None):
        """
        Update training session status
        """
        endpoint = f"train/sessions/{session_id}/"
        data = {'status': status}
        
        if error_details:
            data['error_details'] = error_details
            
        return self._make_request(requests.patch, endpoint, data)