from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from django.http import HttpRequest, HttpResponse

class BaseAdapter(ABC):
    """
    Abstract base class for all platform adapters.
    
    Each communication platform (WhatsApp, Messenger, Email, WebForm, etc.)
    must implement this interface to be integrated with the gateway.
    """
    
    @abstractmethod
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle platform verification challenges.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HttpResponse if verification was handled, None otherwise
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: HttpRequest) -> bool:
        """
        Validate the authenticity of the incoming request.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            True if request is valid, False otherwise.
            
        Raises:
            ValidationError: If request fails validation
        """
        pass
    
    @abstractmethod
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Extract messages from platform-specific format.
        
        Args:
            request: The incoming request data (HttpRequest or model instance)
            
        Returns:
            List of parsed messages in standardized format
        """
        pass
    
    @abstractmethod
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a recipient on this platform.
        
        Args:
            recipient_id: ID of the recipient on this platform
            message_content: Content to send in standardized format
            
        Returns:
            Response data from the platform
        """
        pass
    
    @abstractmethod
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to the platform's webhook.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            HttpResponse in the format expected by the platform
        """
        pass
    
    def get_platform_name(self) -> str:
        """
        Get the name of this platform.
        
        Returns:
            String identifier for this platform
        """
        # Default implementation extracts from class name
        # Override if needed
        class_name = self.__class__.__name__
        if class_name.endswith('Adapter'):
            return class_name[:-7].lower()
        return class_name.lower()