import jwt
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
import datetime

from webhook_handler.token_manager import TokenManager
from webhook_handler.models import Organization

class TokenManagerTestCase(TestCase):
    """Tests for the TokenManager class"""
    
    def setUp(self):
        """Set up test data"""
        self.organization_name = "Test Organization"
        self.organization_email = "test@example.com"
    
    def test_generate_token_new_organization(self):
        """Test generating a token for a new organization"""
        # Generate token for a new organization
        token_data = TokenManager.generate_token(self.organization_name, self.organization_email)
        
        # Verify the token data structure
        self.assertIn('token', token_data)
        self.assertIn('organization_id', token_data)
        self.assertIn('expires', token_data)
        
        # Verify the organization was created
        org = Organization.objects.get(name=self.organization_name)
        self.assertEqual(org.email, self.organization_email)
        
        # Verify the token can be decoded with the correct secret
        decoded = jwt.decode(token_data['token'], settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(decoded['org_id'], str(org.id))
        self.assertEqual(decoded['org_name'], self.organization_name)
    
    def test_generate_token_existing_organization(self):
        """Test generating a token for an existing organization"""
        # Create an organization first
        org = Organization.objects.create(
            name=self.organization_name,
            email=self.organization_email
        )
        
        # Generate token for the existing organization
        token_data = TokenManager.generate_token(self.organization_name)
        
        # Verify token references the existing organization
        self.assertEqual(token_data['organization_id'], str(org.id))
        
        # Verify no new organization was created
        self.assertEqual(Organization.objects.count(), 1)
    
    def test_verify_token_valid(self):
        """Test verifying a valid token"""
        # Create an organization
        org = Organization.objects.create(
            name=self.organization_name,
            email=self.organization_email
        )
        
        # Create a valid token payload
        payload = {
            'org_id': str(org.id),
            'org_name': org.name,
            'exp': int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()),
            'iat': int(datetime.datetime.now().timestamp()),
            'jti': 'test-uuid'
        }
        
        # Encode the token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Verify the token
        result = TokenManager.verify_token(token)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['org_id'], str(org.id))
        self.assertEqual(result['org_name'], org.name)
    
    def test_verify_token_expired(self):
        """Test verifying an expired token"""
        # Create an organization
        org = Organization.objects.create(
            name=self.organization_name,
            email=self.organization_email
        )
        
        # Create an expired token payload
        payload = {
            'org_id': str(org.id),
            'org_name': org.name,
            'exp': int((datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp()),
            'iat': int((datetime.datetime.now() - datetime.timedelta(hours=2)).timestamp()),
            'jti': 'test-uuid'
        }
        
        # Encode the token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Verify the token
        result = TokenManager.verify_token(token)
        
        # Verify the result is None for expired token
        self.assertIsNone(result)
    
    def test_verify_token_invalid_signature(self):
        """Test verifying a token with invalid signature"""
        # Create an organization
        org = Organization.objects.create(
            name=self.organization_name,
            email=self.organization_email
        )
        
        # Create a valid token payload
        payload = {
            'org_id': str(org.id),
            'org_name': org.name,
            'exp': int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()),
            'iat': int(datetime.datetime.now().timestamp()),
            'jti': 'test-uuid'
        }
        
        # Encode the token with wrong secret
        token = jwt.encode(payload, "wrong_secret_key", algorithm='HS256')
        
        # Verify the token
        result = TokenManager.verify_token(token)
        
        # Verify the result is None for token with invalid signature
        self.assertIsNone(result)
    
    def test_verify_token_missing_org(self):
        """Test verifying a token for a non-existent organization"""
        # Create a valid token payload with non-existent org_id
        import uuid
        non_existent_uuid = str(uuid.uuid4())
        
        payload = {
            'org_id': non_existent_uuid,
            'org_name': "Non-existent Org",
            'exp': int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()),
            'iat': int(datetime.datetime.now().timestamp()),
            'jti': 'test-uuid'
        }
        
        # Encode the token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Verify the token
        result = TokenManager.verify_token(token)
        
        # Verify the result is None for token with non-existent org
        self.assertIsNone(result)
    
    @patch('webhook_handler.token_manager.Organization.objects.get_or_create')
    def test_generate_token_exception(self, mock_get_or_create):
        """Test handling of exceptions during token generation"""
        # Mock the get_or_create method to raise an exception
        mock_get_or_create.side_effect = Exception("Test exception")
        
        # Attempt to generate a token
        with self.assertRaises(Exception) as context:
            TokenManager.generate_token(self.organization_name, self.organization_email)
        
        # Verify the exception message
        self.assertTrue("Failed to generate token" in str(context.exception))