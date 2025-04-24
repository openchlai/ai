import logging
from datetime import datetime, timedelta, timezone
import requests
from django.conf import settings
from webhook_handler.models import Organization, WhatsAppCredential

logger = logging.getLogger(__name__)

class TokenManager:
    """
    Manages WhatsApp API tokens, including retrieval, validation, and refreshing.
    """
    
    @staticmethod
    def ensure_aware_datetime(dt):
        """Convert naive datetime to timezone-aware datetime."""
        if dt and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    
    @staticmethod
    def check_token_validity(access_token):
        """
        Use Facebook's API to check if the access token is valid and fetch expiry info.
        """
        if not access_token:
            return None
            
        url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={access_token}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    return data["data"]
                else:
                    logger.error(f"Error in token response data: {data}")
                    return None
            else:
                logger.error(f"Token validity check failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error checking token validity: {e}")
            return None
    
    @staticmethod
    def is_long_term_token(token_info):
        """
        Check if the token is long-term by comparing the expiry timestamp.
        Typically long-term tokens are valid for ~60 days.
        """
        if not token_info or "expires_at" not in token_info:
            return False
            
        try:
            expiry_time = datetime.utcfromtimestamp(token_info["expires_at"])
            current_time = datetime.utcnow()
            # Check if the expiry time is within ~60 days, indicating a long-term token
            return (expiry_time - current_time) > timedelta(days=50)
        except Exception as e:
            logger.error(f"Error determining token type: {e}")
            return False
    
    @classmethod
    def get_access_token(cls, org_id=None):
        """
        Retrieve the access token for the given organization.
        If expired or short-term, refresh it.
        
        Args:
            org_id: Organization ID (optional)
            
        Returns:
            Access token or None if retrieval fails
        """
        # If org_id not provided, try to get the first organization
        if not org_id:
            try:
                org = Organization.objects.first()
                if org:
                    org_id = org.id
                else:
                    # Create a default organization if none exists
                    org = Organization.objects.create(
                        name="Default Organization",
                        email="default@example.com"
                    )
                    org_id = org.id
            except Exception as e:
                logger.error(f"Error getting default organization: {e}")
                return cls._get_default_token()
        
        try:
            # Get credentials for organization
            creds = WhatsAppCredential.objects.filter(organization_id=org_id).first()
            
            if not creds:
                logger.error(f"No credentials found for org {org_id}.")
                return cls._get_default_token()
            
            # Ensure token_expiry is aware datetime
            token_expiry = cls.ensure_aware_datetime(creds.token_expiry)
            
            # Ensure current time is aware datetime
            current_time = datetime.now(timezone.utc)
            
            # If token is expired, refresh it
            if token_expiry and token_expiry < current_time:
                logger.warning(f"Access token for org {org_id} expired. Refreshing token...")
                return cls.refresh_access_token(org_id)
            
            # If token is not expired, verify its validity
            token_info = cls.check_token_validity(creds.access_token)
            
            if token_info and token_info.get("is_valid"):
                logger.info(f"Using stored access token for org {org_id}.")
                return creds.access_token
            else:
                logger.info(f"Invalid token detected for org {org_id}, refreshing...")
                return cls.refresh_access_token(org_id)
                
        except Exception as e:
            logger.error(f"Error retrieving access token: {e}")
            return cls._get_default_token()
    
    @classmethod
    def refresh_access_token(cls, org_id, new_token=None):
        """
        Refresh the access token for an organization.
        
        Args:
            org_id: Organization ID
            new_token: New token to use (optional)
            
        Returns:
            New access token or None if refresh fails
        """
        try:
            # Get credentials
            creds = WhatsAppCredential.objects.filter(organization_id=org_id).first()
            
            if not creds and not new_token:
                logger.error(f"No credentials found for org {org_id}.")
                return cls._get_default_token()
            
            # If a new token is provided, use it directly
            if new_token:
                # Get or create the organization
                organization = None
                try:
                    organization = Organization.objects.get(id=org_id)
                except Organization.DoesNotExist:
                    # Create a dummy organization
                    organization = Organization.objects.create(
                        id=org_id,
                        name=f"Organization {org_id}",
                        email=f"org{org_id}@example.com"
                    )
                
                # Calculate expiry (60 days from now)
                expiry = datetime.now(timezone.utc) + timedelta(days=60)
                
                # Save or update credentials
                credentials, created = WhatsAppCredential.objects.update_or_create(
                    organization=organization,
                    defaults={
                        'access_token': new_token,
                        'token_expiry': expiry,
                        'client_id': getattr(settings, 'WHATSAPP_CLIENT_ID', ''),
                        'client_secret': getattr(settings, 'WHATSAPP_CLIENT_SECRET', ''),
                        'business_id': getattr(settings, 'WHATSAPP_BUSINESS_ID', ''),
                        'phone_number_id': getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
                    }
                )
                
                return {
                    'status': 'success',
                    'token': new_token,
                    'expiry': expiry.isoformat(),
                    'organization_id': organization.id
                }
            
            # Otherwise, try to refresh the existing token
            # Get configuration from settings
            client_id = getattr(settings, 'WHATSAPP_CLIENT_ID', None)
            client_secret = getattr(settings, 'WHATSAPP_CLIENT_SECRET', None)
            
            if not client_id or not client_secret:
                logger.error("Missing WhatsApp API client configuration in settings.")
                return cls._get_default_token()
            
            # Exchange token URL
            exchange_url = (
                f"https://graph.facebook.com/v18.0/oauth/access_token"
                f"?grant_type=fb_exchange_token"
                f"&client_id={client_id}"
                f"&client_secret={client_secret}"
                f"&fb_exchange_token={creds.access_token}"
            )
            
            # Make request
            response = requests.get(exchange_url)
            
            if response.status_code == 200:
                response_data = response.json()
                new_token = response_data.get("access_token")
                
                if new_token:
                    # Update credentials with new token
                    creds.access_token = new_token
                    creds.token_expiry = datetime.now(timezone.utc) + timedelta(days=60)
                    creds.save()
                    
                    logger.info(f"Successfully refreshed access token for org {org_id}.")
                    return new_token
                else:
                    logger.error("No access token in refresh response.")
                    return cls._get_default_token()
            else:
                error_data = response.json().get("error", {})
                error_message = error_data.get("message", "Unknown error")
                error_code = error_data.get("code", "")
                
                logger.error(f"Failed to refresh token: {error_message} (Code: {error_code})")
                return cls._get_default_token()
                
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return cls._get_default_token()
    
    @staticmethod
    def _get_default_token():
        """
        Get default access token from settings.
        
        Returns:
            Default access token from settings or None
        """
        try:
            default_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
            if default_token:
                logger.info("Using default access token from settings.")
                return default_token
            else:
                logger.error("No default access token found in settings.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving default token: {e}")
            return None