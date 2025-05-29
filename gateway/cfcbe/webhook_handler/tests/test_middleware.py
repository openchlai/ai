import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from webhook_handler.middleware import TokenAuthMiddleware
from webhook_handler.models import Organization

class TokenAuthMiddlewareTestCase(TestCase):
    """Tests for the TokenAuthMiddleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TokenAuthMiddleware(get_response=lambda request: JsonResponse({'status': 'ok'}))
        self.org = Organization.objects.create(
            name="Test Organization",
            email="test@example.com"
        )
    
    def test_non_webform_path_bypassed(self):
        """Test that non-webform paths are bypassed"""
        # Create request for a non-webform path
        request = self.factory.post('/api/webhook/whatsapp/')
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert request was processed without authentication
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'ok')
    
    def test_auth_endpoint_bypassed(self):
        """Test that authentication endpoints are bypassed"""
        # Create request for auth endpoint
        request = self.factory.post('/api/webhook/webform/auth/request-verification/')
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert request was processed without authentication
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'ok')
    
    def test_get_request_bypassed(self):
        """Test that GET requests are bypassed"""
        # Create GET request for webform endpoint
        request = self.factory.get('/api/webhook/webform/categories/')
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert request was processed without authentication
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'ok')
    
    def test_missing_auth_header(self):
        """Test request with missing Authorization header"""
        # Create request without Authorization header
        request = self.factory.post('/api/webhook/webform/')
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert authentication failure
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content)['status'], 'error')
    
    def test_invalid_auth_header_format(self):
        """Test request with invalid Authorization header format"""
        # Create request with invalid Authorization header
        request = self.factory.post('/api/webhook/webform/')
        request.META['HTTP_AUTHORIZATION'] = 'InvalidFormat Token123'
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert authentication failure
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content)['status'], 'error')
    
    @patch('webhook_handler.token_manager.TokenManager.verify_token')
    def test_invalid_token(self, mock_verify_token):
        """Test request with invalid token"""
        # Mock token verification to fail
        mock_verify_token.return_value = None
        
        # Create request with invalid token
        request = self.factory.post('/api/webhook/webform/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token'
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert authentication failure
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content)['status'], 'error')
    
    @patch('webhook_handler.token_manager.TokenManager.verify_token')
    def test_organization_not_found(self, mock_verify_token):
        """Test request with token for non-existent organization"""
        # Generate a random UUID that doesn't match any existing organization
        non_existent_uuid = str(uuid.uuid4())
        
        # Mock token verification to return payload with non-existent but valid UUID
        mock_verify_token.return_value = {
            'org_id': non_existent_uuid,
            'org_name': 'Non-existent Org'
        }
        
        # Create request with token
        request = self.factory.post('/api/webhook/webform/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert authentication failure
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content)['status'], 'error')
    
    @patch('webhook_handler.token_manager.TokenManager.verify_token')
    def test_inactive_organization(self, mock_verify_token):
        """Test request with token for inactive organization"""
        # Set organization as inactive
        self.org.is_active = False
        self.org.save()
        
        # Mock token verification to return valid payload
        mock_verify_token.return_value = {
            'org_id': str(self.org.id),
            'org_name': self.org.name
        }
        
        # Create request with token
        request = self.factory.post('/api/webhook/webform/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert authentication failure
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['status'], 'error')
    
    @patch('webhook_handler.token_manager.TokenManager.verify_token')
    def test_valid_authentication(self, mock_verify_token):
        """Test request with valid token"""
        # Mock token verification to return valid payload
        mock_verify_token.return_value = {
            'org_id': str(self.org.id),
            'org_name': self.org.name
        }
        
        # Create request with token
        request = self.factory.post('/api/webhook/webform/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer valid_token'
        
        # Process request through middleware
        response = self.middleware(request)
        
        # Assert authentication success
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'ok')
        
        # Assert organization info was added to request
        self.assertEqual(request.organization_id, str(self.org.id))
        self.assertEqual(request.organization_name, self.org.name)
        self.assertEqual(request.organization_email, self.org.email)