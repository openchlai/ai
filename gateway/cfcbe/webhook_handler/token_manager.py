import jwt
import uuid
import datetime
from django.conf import settings
from webhook_handler.models import Organization

class TokenManager:
    """Manages JWT token generation and verification for the gateway API"""
    
    @staticmethod
    def generate_token(organization_name, organization_email=None):
        """
        Generate a JWT token for an organization.
        Creates the organization if it doesn't exist.
        
        Args:
            organization_name: Name of the organization
            organization_email: Email of the organization (optional)
            
        Returns:
            Dict with token and expiry
        """
        # Get or create organization
        try:
            org, created = Organization.objects.get_or_create(
                name=organization_name,
                defaults={
                    'email': organization_email or f"{organization_name.lower().replace(' ', '')}@example.com"
                }
            )
            
            # Create token payload
            payload = {
                'org_id': str(org.id),
                'org_name': org.name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365),  # 1 year expiry
                'iat': datetime.datetime.utcnow(),
                'jti': str(uuid.uuid4())
            }
            
            # Generate token
            token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            return {
                'token': token,
                'organization_id': str(org.id),
                'expires': payload['exp'].isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate token: {str(e)}")
    
    @staticmethod
    def verify_token(token):
        """
        Verify a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dict with token payload if valid, None otherwise
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Check if organization exists
            org_id = payload.get('org_id')
            if not org_id or not Organization.objects.filter(id=org_id).exists():
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None