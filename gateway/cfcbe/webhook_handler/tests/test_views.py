import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from webhook_handler.models import Organization, Notification, Complaint

class WebhookViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    @patch('webhook_handler.views.AdapterFactory.get_adapter')
    def test_unified_webhook_get(self, mock_get_adapter):
        # Mock the adapter and its handle_verification method
        mock_adapter = MagicMock()
        mock_adapter.handle_verification.return_value = HttpResponse("Verified")
        mock_get_adapter.return_value = mock_adapter
        
        # Call the view - using the correct URL pattern name with a dash
        url = reverse('unified-webhook', kwargs={'platform': 'whatsapp'})
        response = self.client.get(url)
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        
    @patch('webhook_handler.views.AdapterFactory.get_adapter')
    def test_unified_webhook_post_incoming_whatsapp(self, mock_get_adapter):
        # Mock the adapter and its methods
        mock_adapter = MagicMock()
        mock_adapter.validate_request.return_value = True
        
        # Include all required fields based on StandardMessage, including source_timestamp
        mock_adapter.parse_messages.return_value = [
            {
                'message_id': '123',
                'source': 'whatsapp',
                'source_uid': 'user123',
                'source_address': 'user123@whatsapp',
                'source_timestamp': '2025-04-30T15:00:00Z',  # Added this field
                'platform': 'whatsapp',
                'timestamp': '2025-04-30T15:00:00Z',
                'direction': 'incoming',
                'content_type': 'text',
                'content': 'Hello',
                'sender': {'id': 'sender123', 'name': 'Test Sender'},
                'recipient': {'id': 'recipient123', 'name': 'Test Recipient'},
                'metadata': {}
            }
        ]
        
        mock_adapter.format_webhook_response.return_value = HttpResponse("OK")
        mock_get_adapter.return_value = mock_adapter
        
        # Mock the router's route_to_endpoint method
        with patch('webhook_handler.views.router.route_to_endpoint') as mock_route:
            mock_route.return_value = {'status': 'success', 'message_id': '123'}
            
            # Call the view
            url = reverse('unified-webhook', kwargs={'platform': 'whatsapp'})
            response = self.client.post(url, data=json.dumps({}), content_type='application/json')
            
            # Assert response status
            self.assertEqual(response.status_code, 200)
    
    @patch('webhook_handler.views.AdapterFactory.get_adapter')
    def test_unified_webhook_post_outgoing_whatsapp(self, mock_get_adapter):
        # Mock the adapter and its methods
        mock_adapter = MagicMock()
        mock_adapter.send_message.return_value = {'status': 'success', 'message_id': '123'}
        mock_get_adapter.return_value = mock_adapter
        
        # Call the view
        url = reverse('unified-webhook', kwargs={'platform': 'whatsapp'})
        payload = {
            'direction': 'outgoing',
            'data': {
                'recipient': '123456789',
                'message_type': 'text',
                'content': 'Hello'
            }
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
    
    @patch('webhook_handler.views.AdapterFactory.get_adapter')
    def test_unified_webhook_post_token_whatsapp(self, mock_get_adapter):
        # Mock the adapter and its methods
        mock_adapter = MagicMock()
        mock_adapter.generate_token.return_value = {
            'status': 'success',
            'token': '123456',
            'expiry': '2025-04-30T12:00:00Z',
            'organization_id': '789'
        }
        mock_get_adapter.return_value = mock_adapter
        
        # Call the view
        url = reverse('unified-webhook', kwargs={'platform': 'whatsapp'})
        payload = {
            'direction': 'token',
            'data': {
                'short_lived_token': 'abcdef',
                'org_id': '789'
            }
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
    
    @patch('webhook_handler.views.AdapterFactory.get_adapter')
    @patch('platform_adapters.webform.serializers.ComplaintSerializer')
    @patch('webhook_handler.views.Notification.objects.create')
    @patch('webhook_handler.views.router.route_to_endpoint')
    @patch('webhook_handler.token_manager.TokenManager.verify_token')
    def test_unified_webhook_post_webform_submission(self, mock_verify_token, mock_route, mock_notification_create, mock_serializer_class, mock_get_adapter):
        # Set up organization
        org = Organization.objects.create(name="Test Org", email="test@example.com")
        
        # Mock token verification to return valid payload
        mock_verify_token.return_value = {
            'org_id': str(org.id),
            'org_name': org.name
        }
        
        # Mock the serializer
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_complaint = MagicMock(spec=Complaint)
        mock_complaint.complaint_id = '123'
        mock_serializer.save.return_value = mock_complaint
        mock_serializer_class.return_value = mock_serializer
        
        # Mock the notification
        mock_notification = MagicMock(spec=Notification)
        mock_notification.notification_id = '456'
        mock_notification_create.return_value = mock_notification
        
        # Mock the adapter
        mock_adapter = MagicMock()
        
        # Use a MagicMock with the required attributes
        mock_std_message = MagicMock()
        mock_std_message.platform = 'webform'
        mock_adapter.create_from_complaint.return_value = mock_std_message
        mock_get_adapter.return_value = mock_adapter
        
        # Mock router response
        mock_route.return_value = {'status': 'success', 'message_id': '123'}
        
        # Call the view
        url = reverse('unified-webhook', kwargs={'platform': 'webform'})
        payload = {
            'reporter_nickname': 'Anonymous',
            'case_category': 'HARASSMENT',
            'complaint_text': 'Test complaint'
        }
        
        # Add auth token to headers
        headers = {'HTTP_AUTHORIZATION': 'Bearer valid_token_for_testing'}
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json',
            **headers
        )
        
        # For debugging if needed
        print(f"Response status: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Response content: {response.content}")
        
        # Should return 200 OK with the mocked token verification
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
    
    def test_unified_webhook_invalid_platform(self):
        # Call the view with an invalid platform
        url = reverse('unified-webhook', kwargs={'platform': 'invalid_platform'})
        response = self.client.get(url)
        
        # Assert response
        self.assertEqual(response.status_code, 404)
    
    def test_webform_submission_no_token(self):
        # Call the webform submission without a token
        url = reverse('unified-webhook', kwargs={'platform': 'webform'})
        payload = {
            'reporter_nickname': 'Anonymous',
            'case_category': 'HARASSMENT',
            'complaint_text': 'Test complaint'
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        
        # We expect a 401 Unauthorized since we're not providing authentication
        self.assertEqual(response.status_code, 401)
    
    @patch('webhook_handler.token_manager.TokenManager.verify_token')
    def test_webform_submission_invalid_token(self, mock_verify_token):
        # Set up the verify_token mock to return None (invalid token)
        mock_verify_token.return_value = None
        
        # Call the webform submission with an invalid token
        url = reverse('unified-webhook', kwargs={'platform': 'webform'})
        payload = {
            'reporter_nickname': 'Anonymous',
            'case_category': 'HARASSMENT',
            'complaint_text': 'Test complaint'
        }
        
        # Add an invalid Authorization header
        headers = {'HTTP_AUTHORIZATION': 'Bearer invalid_token'}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json', **headers)
        
        # We expect a 401 status code for an invalid token
        self.assertEqual(response.status_code, 401)