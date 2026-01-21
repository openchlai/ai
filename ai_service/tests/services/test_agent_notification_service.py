# tests/test_agent_notification_service.py
import pytest
import sys
import os
from unittest.mock import patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.mark.skip(reason="AgentNotificationService has been deprecated and replaced with EnhancedNotificationService")
class TestAgentNotificationService:
    """Unit tests for the Agent Notification Service (DEPRECATED - use EnhancedNotificationService)"""

    def test_service_initialization(self):
        """Test service initialization"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.asterisk_server_ip = "192.168.10.3"
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            assert service.asterisk_server_ip == "192.168.10.3"
            assert service.endpoint_url == "https://192.168.10.3/hh5aug2025/api/msg/"
            assert service.basic_auth == "dGVzdDpwQHNzdzByZA=="
            assert service.bearer_token is None
            assert service.session is None

    def test_update_type_enum(self):
        """Test UpdateType enum values"""
        from app.services.agent_notification_service import UpdateType
        
        assert UpdateType.CALL_START.value == "call_start"
        assert UpdateType.TRANSCRIPT_SEGMENT.value == "transcript_segment"
        assert UpdateType.TRANSLATION_UPDATE.value == "translation_update"
        assert UpdateType.ENTITY_UPDATE.value == "entity_update"
        assert UpdateType.CLASSIFICATION_UPDATE.value == "classification_update"
        assert UpdateType.QA_UPDATE.value == "qa_update"
        assert UpdateType.CALL_END.value == "call_end"
        assert UpdateType.CALL_SUMMARY.value == "call_summary"
        assert UpdateType.CALL_INSIGHTS.value == "call_insights"
        assert UpdateType.GPT_INSIGHTS.value == "gpt_insights"
        assert UpdateType.ERROR.value == "error"

    def test_service_attributes(self):
        """Test service has expected attributes"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.asterisk_server_ip = "192.168.10.3"
            
            from app.services.agent_notification_service import AgentNotificationService
            service = AgentNotificationService()
            
            # Test basic attributes
            assert hasattr(service, 'asterisk_server_ip')
            assert hasattr(service, 'endpoint_url')
            assert hasattr(service, 'auth_endpoint_url')
            assert hasattr(service, 'basic_auth')
            assert hasattr(service, 'bearer_token')
            assert hasattr(service, 'token_expires_at')
            assert hasattr(service, 'token_refresh_threshold')
            assert hasattr(service, 'session')
            assert hasattr(service, 'max_retries')
            
            # Test default values
            assert service.token_refresh_threshold == 300
            assert service.max_retries == 3

    def test_service_can_be_imported(self):
        """Test that service and enum can be imported successfully"""
        from app.services.agent_notification_service import AgentNotificationService, UpdateType
        
        assert AgentNotificationService is not None
        assert UpdateType is not None
        
        # Test enum has all expected values
        expected_update_types = [
            'CALL_START', 'TRANSCRIPT_SEGMENT', 'TRANSLATION_UPDATE', 
            'ENTITY_UPDATE', 'CLASSIFICATION_UPDATE', 'QA_UPDATE',
            'CALL_END', 'CALL_SUMMARY', 'CALL_INSIGHTS', 'GPT_INSIGHTS', 'ERROR'
        ]
        
        for update_type in expected_update_types:
            assert hasattr(UpdateType, update_type)