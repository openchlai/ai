# middleware.py - Update your existing TokenAuthMiddleware in webhook_handler/middleware.py

from django.http import JsonResponse
import logging

from .token_manager import TokenManager
from .models import Organization

logger = logging.getLogger(__name__)

class TokenAuthMiddleware:
    """
    Middleware to authenticate requests using JWT tokens.
    
    This middleware:
    1. Intercepts incoming requests
    2. Extracts and validates bearer tokens
    3. Attaches organization information to authenticated requests
    4. Rejects unauthorized requests
    5. Bypasses authentication for specific paths or methods
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Bypass paths for the authentication API endpoints
        auth_bypass_paths = [
            '/api/webhook/webform/auth/request-verification/',
            '/api/webhook/webform/auth/verify-otp/',
            '/api/webhook/webform/auth/token/'
        ]
        
        # Skip authentication for auth endpoints
        if any(request.path.endswith(path) for path in auth_bypass_paths):
            return self.get_response(request)
        
        # Skip authentication for non-webform endpoints
        if '/api/webhook/webform/' not in request.path:
            return self.get_response(request)
        
        # Skip authentication for GET requests (like categories)
        if request.method == 'GET':
            return self.get_response(request)
        
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # Check if header exists and has correct format
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required. Please provide a valid bearer token.'
            }, status=401)
            
        # Extract token
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = TokenManager.verify_token(token)
        if not payload:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid or expired token.'
            }, status=401)
            
        try:
            # Get organization from database to ensure it's still active
            org_id = payload.get('org_id')
            organization = Organization.objects.get(id=org_id)
            
            if not organization.is_active:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Organization access has been revoked.'
                }, status=403)
                
            # Add organization info to request
            request.organization_id = str(organization.id)
            request.organization_name = organization.name
            request.organization_email = organization.email
            
        except Organization.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Organization not found.'
            }, status=401)
        except Exception as e:
            logger.exception(f"Error verifying organization: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication error.'
            }, status=500)
        
        # Continue with request
        return self.get_response(request)