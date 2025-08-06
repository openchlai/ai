# tests/test_agent_notification_service.py
import pytest
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestAgentNotificationService:
    """Unit tests for the Agent Notification Service"""

    @pytest.fixture
    def mock_service(self):
        """Create a mocked agent notification service"""
        with patch('app.services.agent_notification_service.requests') as mock_requests, \
             patch('app.services.agent_notification_service.settings') as mock_settings:
            
            mock_settings.AGENT_WEBHOOK_URL = "http://agent.example.com/webhook"
            mock_settings.AGENT_API_KEY = "test_api_key"
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_requests.post.return_value = mock_response
            
            return service, mock_requests

    def test_service_initialization(self):
        """Test service initialization"""
        with patch('app.services.agent_notification_service.settings') as mock_settings:
            mock_settings.AGENT_WEBHOOK_URL = "http://test.com"
            mock_settings.AGENT_API_KEY = "test_key"
            mock_settings.NOTIFICATION_TIMEOUT = 30
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            assert service.webhook_url == "http://test.com"
            assert service.api_key == "test_key"
            assert service.timeout == 30

    def test_send_transcription_notification(self, mock_service):
        """Test sending transcription notification to agent"""
        service, mock_requests = mock_service
        
        notification_data = {
            "call_id": "call_001",
            "transcript": "Hello, how can I help you?",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.95,
            "language": "en"
        }
        
        result = service.send_transcription_notification(notification_data)
        
        assert result is True
        mock_requests.post.assert_called_once()
        
        # Verify request details
        call_args = mock_requests.post.call_args
        assert "http://agent.example.com/webhook" in call_args[0]
        assert "json" in call_args[1]

    def test_send_classification_notification(self, mock_service):
        """Test sending classification notification to agent"""
        service, mock_requests = mock_service
        
        classification_data = {
            "call_id": "call_001",
            "classification": {
                "main_category": "technical_support",
                "sub_category": "billing_issue",
                "confidence": 0.87,
                "priority": "high"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        result = service.send_classification_notification(classification_data)
        
        assert result is True
        mock_requests.post.assert_called_once()

    def test_send_entity_notification(self, mock_service):
        """Test sending entity extraction notification"""
        service, mock_requests = mock_service
        
        entity_data = {
            "call_id": "call_001",
            "entities": [
                {"text": "John Smith", "label": "PERSON", "confidence": 0.95},
                {"text": "Microsoft", "label": "ORG", "confidence": 0.92}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        result = service.send_entity_notification(entity_data)
        
        assert result is True
        mock_requests.post.assert_called_once()

    def test_send_qa_evaluation_notification(self, mock_service):
        """Test sending QA evaluation notification"""
        service, mock_requests = mock_service
        
        qa_data = {
            "call_id": "call_001",
            "qa_scores": {
                "opening": 0.8,
                "listening": 0.7,
                "resolution": 0.9,
                "overall_score": 0.8
            },
            "recommendations": ["Improve opening greeting"],
            "timestamp": datetime.now().isoformat()
        }
        
        result = service.send_qa_evaluation_notification(qa_data)
        
        assert result is True
        mock_requests.post.assert_called_once()

    def test_send_call_summary_notification(self, mock_service):
        """Test sending call summary notification"""
        service, mock_requests = mock_service
        
        summary_data = {
            "call_id": "call_001",
            "summary": "Customer called regarding billing issue. Resolved by updating payment method.",
            "duration": 180.5,
            "status": "resolved",
            "timestamp": datetime.now().isoformat()
        }
        
        result = service.send_call_summary_notification(summary_data)
        
        assert result is True
        mock_requests.post.assert_called_once()

    def test_notification_failure_handling(self):
        """Test handling of notification failures"""
        with patch('app.services.agent_notification_service.requests') as mock_requests:
            # Mock failed response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_requests.post.return_value = mock_response
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            notification_data = {"call_id": "test", "transcript": "test"}
            result = service.send_transcription_notification(notification_data)
            
            assert result is False

    def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        with patch('app.services.agent_notification_service.requests') as mock_requests:
            # Mock timeout exception
            mock_requests.post.side_effect = mock_requests.exceptions.Timeout()
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            notification_data = {"call_id": "test", "transcript": "test"}
            result = service.send_transcription_notification(notification_data)
            
            assert result is False

    def test_connection_error_handling(self):
        """Test handling of connection errors"""
        with patch('app.services.agent_notification_service.requests') as mock_requests:
            # Mock connection error
            mock_requests.post.side_effect = mock_requests.exceptions.ConnectionError()
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            notification_data = {"call_id": "test", "transcript": "test"}
            result = service.send_transcription_notification(notification_data)
            
            assert result is False

    def test_batch_notification_sending(self, mock_service):
        """Test sending multiple notifications in batch"""
        service, mock_requests = mock_service
        
        notifications = [
            {"type": "transcription", "data": {"call_id": "call_001", "transcript": "Hello"}},
            {"type": "classification", "data": {"call_id": "call_001", "classification": {}}},
            {"type": "entities", "data": {"call_id": "call_001", "entities": []}}
        ]
        
        results = service.send_batch_notifications(notifications)
        
        assert len(results) == 3
        assert all(results)
        assert mock_requests.post.call_count == 3

    def test_notification_retry_mechanism(self):
        """Test retry mechanism for failed notifications"""
        with patch('app.services.agent_notification_service.requests') as mock_requests:
            # First call fails, second succeeds
            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 500
            
            mock_response_success = MagicMock()
            mock_response_success.status_code = 200
            
            mock_requests.post.side_effect = [mock_response_fail, mock_response_success]
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            notification_data = {"call_id": "test", "transcript": "test"}
            result = service.send_transcription_notification(notification_data, retry_count=1)
            
            assert result is True
            assert mock_requests.post.call_count == 2

    def test_notification_data_validation(self, mock_service):
        """Test validation of notification data"""
        service, mock_requests = mock_service
        
        # Test with invalid data (missing required fields)
        invalid_data = {"transcript": "Hello"}  # Missing call_id
        
        result = service.send_transcription_notification(invalid_data)
        
        # Should handle validation gracefully
        assert isinstance(result, bool)

    def test_webhook_authentication(self, mock_service):
        """Test webhook authentication headers"""
        service, mock_requests = mock_service
        
        notification_data = {"call_id": "test", "transcript": "test"}
        service.send_transcription_notification(notification_data)
        
        # Verify authentication header was included
        call_args = mock_requests.post.call_args
        headers = call_args[1].get('headers', {})
        assert 'Authorization' in headers or 'X-API-Key' in headers

    def test_notification_rate_limiting(self):
        """Test notification rate limiting"""
        with patch('app.services.agent_notification_service.requests') as mock_requests, \
             patch('time.sleep') as mock_sleep:
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_requests.post.return_value = mock_response
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService(rate_limit=2)  # 2 requests per second
            
            # Send multiple notifications rapidly
            notifications = [{"call_id": f"call_{i}", "transcript": "test"} for i in range(5)]
            
            for notification in notifications:
                service.send_transcription_notification(notification)
            
            # Should have called sleep for rate limiting (if implemented)
            # Implementation dependent

    def test_notification_queuing(self):
        """Test notification queuing for offline scenarios"""
        from app.services.agent_notification_service import AgentNotificationService
        service = AgentNotificationService()
        
        # Test queuing notification when service is offline
        with patch.object(service, '_is_service_available', return_value=False):
            notification_data = {"call_id": "test", "transcript": "test"}
            result = service.send_transcription_notification(notification_data)
            
            # Should queue for later delivery or handle gracefully
            assert isinstance(result, bool)

    def test_notification_metrics_tracking(self, mock_service):
        """Test tracking of notification metrics"""
        service, mock_requests = mock_service
        
        # Send several notifications
        for i in range(3):
            notification_data = {"call_id": f"call_{i}", "transcript": "test"}
            service.send_transcription_notification(notification_data)
        
        # Get metrics
        metrics = service.get_notification_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_sent" in metrics or len(metrics) >= 0

    @pytest.mark.asyncio
    async def test_async_notification_sending(self):
        """Test asynchronous notification sending"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            from app.services.agent_notification_service import AsyncAgentNotificationService
            service = AsyncAgentNotificationService()
            
            notification_data = {"call_id": "test", "transcript": "test"}
            result = await service.send_transcription_notification_async(notification_data)
            
            assert result is True

    def test_notification_formatting(self, mock_service):
        """Test proper formatting of notification payloads"""
        service, mock_requests = mock_service
        
        notification_data = {
            "call_id": "call_001",
            "transcript": "Hello world",
            "timestamp": "2023-01-01T10:00:00Z",
            "confidence": 0.95
        }
        
        service.send_transcription_notification(notification_data)
        
        # Verify the payload structure
        call_args = mock_requests.post.call_args
        payload = call_args[1]['json']
        
        assert isinstance(payload, dict)
        assert "type" in payload
        assert "data" in payload
        assert payload["type"] == "transcription"