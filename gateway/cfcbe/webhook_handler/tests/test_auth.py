import json
import jwt
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta

from webhook_handler.models import Organization, EmailVerification
from webhook_handler.token_manager import TokenManager

class TokenManagerTestCase(TestCase):
    """Test cases for the TokenManager class"""

    def setUp(self):
        self.org_name = "Test Organization"
        self.org_email = "test@example.com"
        
    def test_generate_token(self):
        """Test token generation for an organization"""
        # Generate token
        token_data = TokenManager.generate_token(self.org_name, self.org_email)
        
        # Verify response structure
        self.assertIn('token', token_data)
        self.assertIn('organization_id', token_data)
        self.assertIn('expires', token_data)
        
        # Verify organization was created
        org = Organization.objects.get(name=self.org_name)
        self.assertEqual(org.email, self.org_email)
        self.assertEqual(str(org.id), token_data['organization_id'])
        
        # Verify token is valid
        payload = jwt.decode(
            token_data['token'],
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        self.assertEqual(payload['org_id'], token_data['organization_id'])
        self.assertEqual(payload['org_name'], self.org_name)
    
    def test_verify_token_valid(self):
        """Test verification of a valid token"""
        # Create organization
        org = Organization.objects.create(name=self.org_name, email=self.org_email)
        
        # Create token payload
        payload = {
            'org_id': str(org.id),
            'org_name': org.name,
            'exp': int((timezone.now() + timedelta(hours=1)).timestamp()),  # 1 hour expiry
            'iat': int(timezone.now().timestamp()),
            'jti': '123456'
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # Verify token
        result = TokenManager.verify_token(token)
        self.assertIsNotNone(result)
        self.assertEqual(result['org_id'], str(org.id))
        self.assertEqual(result['org_name'], org.name)
    
    def test_verify_token_expired(self):
        """Test verification of an expired token"""
        # Create organization
        org = Organization.objects.create(name=self.org_name, email=self.org_email)
        
        # Create token payload with past expiry
        payload = {
            'org_id': str(org.id),
            'org_name': org.name,
            'exp': int((timezone.now() - timedelta(hours=1)).timestamp()),  # 1 hour in the past
            'iat': int((timezone.now() - timedelta(hours=2)).timestamp()),
            'jti': '123456'
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # Verify token should fail
        result = TokenManager.verify_token(token)
        self.assertIsNone(result)
    
    def test_verify_token_invalid_signature(self):
        """Test verification of a token with invalid signature"""
        # Create organization
        org = Organization.objects.create(name=self.org_name, email=self.org_email)
        
        # Create token payload
        payload = {
            'org_id': str(org.id),
            'org_name': org.name,
            'exp': int((timezone.now() + timedelta(hours=1)).timestamp()),
            'iat': int(timezone.now().timestamp()),
            'jti': '123456'
        }
        
        # Generate token with wrong key
        token = jwt.encode(
            payload,
            "wrong_secret_key",
            algorithm='HS256'
        )
        
        # Verify token should fail
        result = TokenManager.verify_token(token)
        self.assertIsNone(result)
    
    def test_verify_token_nonexistent_organization(self):
        """Test verification of a token with non-existent organization ID"""
        # Create token payload with non-existent org ID
        payload = {
            'org_id': 'nonexistent-org-id',
            'org_name': 'Non-existent Org',
            'exp': int((timezone.now() + timedelta(hours=1)).timestamp()),
            'iat': int(timezone.now().timestamp()),
            'jti': '123456'
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # Verify token should fail
        result = TokenManager.verify_token(token)
        self.assertIsNone(result)


class AuthViewsTestCase(TestCase):
    """Test cases for authentication views"""

    def setUp(self):
        self.client = Client()
        self.email = "test@example.com"
        self.organization_name = "Test Organization"
        
    @patch('webhook_handler.auth_views.EmailService.send_otp_email')
    def test_request_email_verification_success(self, mock_send_email):
        """Test successful request for email verification"""
        # Mock email sending
        mock_send_email.return_value = True
        
        # Request verification
        url = reverse('request_email_verification')
        payload = {
            'email': self.email,
            'organization_name': self.organization_name
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['email'], self.email)
        
        # Assert verification was created
        verification = EmailVerification.objects.filter(email=self.email).first()
        self.assertIsNotNone(verification)
        self.assertFalse(verification.is_verified)
        self.assertGreater(verification.expires_at, timezone.now())
    
    def test_request_email_verification_missing_fields(self):
        """Test request for email verification with missing fields"""
        # Request verification without email
        url = reverse('request_email_verification')
        payload = {
            'organization_name': self.organization_name
            # Missing email
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    @patch('webhook_handler.auth_views.EmailService.send_otp_email')
    def test_request_email_verification_email_failure(self, mock_send_email):
        """Test request for email verification when email sending fails"""
        # Mock email sending to fail
        mock_send_email.return_value = False
        
        # Request verification
        url = reverse('request_email_verification')
        payload = {
            'email': self.email,
            'organization_name': self.organization_name
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    def test_verify_otp_success(self):
        """Test successful OTP verification"""
        # Create verification
        verification = EmailVerification.create_verification(self.email)
        otp = verification.otp
        
        # Verify OTP
        url = reverse('verify_otp')
        payload = {
            'email': self.email,
            'otp': otp,
            'organization_name': self.organization_name
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('token', data)
        self.assertIn('organization_id', data)
        
        # Assert verification was updated
        verification.refresh_from_db()
        self.assertTrue(verification.is_verified)
    
    def test_verify_otp_missing_fields(self):
        """Test OTP verification with missing fields"""
        # Verify OTP without OTP
        url = reverse('verify_otp')
        payload = {
            'email': self.email,
            'organization_name': self.organization_name
            # Missing OTP
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    def test_verify_otp_no_pending_verification(self):
        """Test OTP verification when no verification exists"""
        # Verify OTP without existing verification
        url = reverse('verify_otp')
        payload = {
            'email': self.email,
            'otp': '123456',  # Random OTP
            'organization_name': self.organization_name
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code"""
        # Create verification
        verification = EmailVerification.create_verification(self.email)
        
        # Verify with wrong OTP
        url = reverse('verify_otp')
        payload = {
            'email': self.email,
            'otp': '000000',  # Wrong OTP
            'organization_name': self.organization_name
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        
        # Assert verification was not updated
        verification.refresh_from_db()
        self.assertFalse(verification.is_verified)
    
    def test_verify_otp_expired(self):
        """Test OTP verification with expired verification"""
        # Create verification
        verification = EmailVerification.objects.create(
            email=self.email,
            otp='123456',
            expires_at=timezone.now() - timedelta(minutes=1)  # Already expired
        )
        
        # Verify OTP
        url = reverse('verify_otp')
        payload = {
            'email': self.email,
            'otp': '123456',
            'organization_name': self.organization_name
        }
        response = self.client.post(
            url, 
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')