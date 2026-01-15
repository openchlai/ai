"""
Comprehensive tests for enhanced_notification_service to achieve 99%+ coverage.
"""
import pytest
import json
import base64
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, AsyncMock, mock_open, PropertyMock
import httpx

from app.services.enhanced_notification_service import (
    EnhancedNotificationService,
    UIMetadata,
    ErrorPayload,
    NotificationV2
)
from app.models.notification_types import NotificationType, ProcessingMode, NotificationStatus


class TestUIMetadata:
    """Test UIMetadata model"""

    def test_ui_metadata_creation(self):
        """Test UIMetadata creation with defaults"""
        metadata = UIMetadata()

        assert metadata.priority == 1
        assert metadata.display_panel == "main"
        assert metadata.requires_action is False
        assert metadata.alert_type is None

    def test_ui_metadata_with_values(self):
        """Test UIMetadata creation with custom values"""
        metadata = UIMetadata(
            priority=3,
            display_panel="alerts",
            requires_action=True,
            alert_type="critical"
        )

        assert metadata.priority == 3
        assert metadata.display_panel == "alerts"
        assert metadata.requires_action is True
        assert metadata.alert_type == "critical"


class TestErrorPayload:
    """Test ErrorPayload model"""

    def test_error_payload_creation(self):
        """Test ErrorPayload creation"""
        error = ErrorPayload(
            error_type="NetworkError",
            error_message="Connection refused",
            component="notification_service"
        )

        assert error.error_type == "NetworkError"
        assert error.error_message == "Connection refused"
        assert error.component == "notification_service"


class TestNotificationV2:
    """Test NotificationV2 model"""

    def test_notification_v2_creation(self):
        """Test NotificationV2 creation with defaults"""
        notification = NotificationV2(
            processing_mode=ProcessingMode.DUAL,
            call_metadata={"call_id": "test123"},
            notification_type=NotificationType.STREAMING_CALL_START,
            payload={"message": "Call started"}
        )

        assert notification.version == "2.0"
        assert notification.message_id is not None
        assert notification.timestamp is not None
        assert notification.processing_mode == ProcessingMode.DUAL
        assert notification.status == NotificationStatus.SUCCESS

    def test_notification_v2_with_error(self):
        """Test NotificationV2 with error"""
        error = ErrorPayload(
            error_type="TestError",
            error_message="Test",
            component="test"
        )
        notification = NotificationV2(
            processing_mode=ProcessingMode.DUAL,
            call_metadata={},
            notification_type=NotificationType.SYSTEM_ERROR,
            payload={},
            status=NotificationStatus.ERROR,
            error=error
        )

        assert notification.status == NotificationStatus.ERROR
        assert notification.error is not None


class TestEnhancedNotificationServiceInit:
    """Test EnhancedNotificationService initialization"""

    @patch('app.services.enhanced_notification_service.settings')
    def test_service_initialization(self, mock_settings):
        """Test service initialization"""
        mock_settings.notification_endpoint_url = "http://localhost:8000/notify"
        mock_settings.notification_auth_endpoint_url = "http://localhost:8000/auth"
        mock_settings.notification_basic_auth = "test_auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site123"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        assert service.endpoint_url == "http://localhost:8000/notify"
        assert service.basic_auth == "test_auth"
        assert service.use_base64 is False
        assert service.site_id == "site123"

    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_service_initialization_with_payload_logging(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test service initialization with payload logging enabled"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = True
        mock_settings.agent_payload_log_file = "/tmp/payloads.jsonl"

        service = EnhancedNotificationService()

        assert service.enable_payload_logging is True

    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', side_effect=Exception("Test error"))
    def test_service_initialization_payload_logging_error(self, mock_exists, mock_makedirs, mock_settings):
        """Test service initialization with payload logging error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = True
        mock_settings.agent_payload_log_file = "/tmp/payloads.jsonl"

        service = EnhancedNotificationService()

        # Should disable payload logging on error
        assert service.enable_payload_logging is False


class TestCreateBasePayload:
    """Test _create_base_payload method"""

    @patch('app.services.enhanced_notification_service.settings')
    def test_create_base_payload(self, mock_settings):
        """Test creating base payload"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        payload = service._create_base_payload(
            "call123",
            NotificationType.STREAMING_CALL_START,
            ProcessingMode.DUAL,
            {"test": "data"}
        )

        assert payload["version"] == "2.0"
        assert payload["processing_mode"] == ProcessingMode.DUAL.value
        assert payload["notification_type"] == NotificationType.STREAMING_CALL_START.value
        assert payload["call_metadata"]["call_id"] == "call123"
        assert payload["payload"]["test"] == "data"
        assert payload["message_id"] is not None
        assert payload["timestamp"] is not None


class TestExtractNotificationSummary:
    """Test _extract_notification_summary method"""

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_transcription_summary(self, mock_settings):
        """Test extracting transcription summary"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_transcription",
            {"transcript": "This is a transcript"}
        )

        assert summary["length"] == 20
        assert summary["text"] == "This is a transcript"

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_translation_summary(self, mock_settings):
        """Test extracting translation summary"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_translation",
            {"translation": "Translated text"}
        )

        assert summary["length"] == 15
        assert summary["text"] == "Translated text"

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_classification_summary(self, mock_settings):
        """Test extracting classification summary"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_classification",
            {
                "main_category": "violence",
                "sub_category": "physical",
                "sub_category_2": "severe",
                "intervention": "police",
                "priority": "high",
                "confidence": 0.95
            }
        )

        assert summary["main_category"] == "violence"
        assert summary["sub_category"] == "physical"
        assert summary["sub_category_2"] == "severe"
        assert summary["confidence"] == 95.0

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_entities_summary(self, mock_settings):
        """Test extracting entities summary"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_entities",
            {
                "entities": {
                    "persons": ["John", "Jane"],
                    "locations": ["Home"]
                }
            }
        )

        assert summary["counts"]["persons"] == 2
        assert summary["counts"]["locations"] == 1

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_qa_scoring_summary(self, mock_settings):
        """Test extracting QA scoring summary"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_qa_scoring",
            {
                "qa_results": {
                    "total_metrics_evaluated": 10,
                    "pass_rate_percentage": 85.0,
                    "overall_quality": "Good"
                }
            }
        )

        assert summary["total_metrics"] == 10
        assert summary["pass_rate"] == 85.0

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_summary_notification(self, mock_settings):
        """Test extracting summary notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_summary",
            {"summary": "Case summary text"}
        )

        assert summary["summary"] == "Case summary text"

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_complete_notification(self, mock_settings):
        """Test extracting complete notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "postcall_complete",
            {
                "status": "completed",
                "processing_time_seconds": 45.5
            }
        )

        assert summary["status"] == "completed"
        assert summary["processing_time"] == 45.5

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_unknown_type_summary(self, mock_settings):
        """Test extracting summary for unknown type"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        summary = service._extract_notification_summary(
            "unknown_type",
            {"key": "value"}
        )

        assert "data" in summary

    @patch('app.services.enhanced_notification_service.settings')
    def test_extract_summary_error(self, mock_settings):
        """Test extract summary with error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        # Pass invalid data to trigger error path
        with patch('app.services.enhanced_notification_service.logger'):
            summary = service._extract_notification_summary(
                "postcall_entities",
                {"entities": "invalid"}  # Should be dict with lists
            )
            assert "error" in summary


class TestWriteMockNotification:
    """Test _write_mock_notification method"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_transcription(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock transcription notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_transcription",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {"transcript": "Test transcript"}
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_translation(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock translation notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_translation",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {"translation": "Translated text"}
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_classification(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock classification notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_classification",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {
                "main_category": "abuse",
                "sub_category": "physical",
                "sub_category_2": "severe",
                "intervention": "police",
                "priority": "high",
                "confidence": 0.95
            }
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_entities(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock entities notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_entities",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {
                "entities": {
                    "persons": ["John", "Jane"],
                    "locations": ["Home"]
                }
            }
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_qa_scoring(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock QA scoring notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_qa_scoring",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {
                "qa_results": {
                    "total_metrics_evaluated": 10,
                    "pass_rate_percentage": 85.0,
                    "overall_quality": "Good"
                }
            }
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_summary(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock summary notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_summary",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {"summary": "Case summary"}
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_complete(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock complete notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "postcall_complete",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {"status": "completed", "processing_time_seconds": 45.5}
        }

        await service._write_mock_notification(payload)
        assert mock_file.called

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('builtins.open', side_effect=Exception("Test error"))
    async def test_write_mock_notification_error(self, mock_file, mock_settings):
        """Test writing mock notification with error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        with patch('os.makedirs'):
            with patch('os.path.exists', return_value=False):
                payload = {
                    "call_metadata": {"call_id": "call123"},
                    "notification_type": "postcall_transcription",
                    "timestamp": datetime.now().isoformat(),
                    "processing_mode": "post_call",
                    "payload": {"transcript": "Test"}
                }

                # Should not raise, just log error
                await service._write_mock_notification(payload)


class TestFetchAuthToken:
    """Test _fetch_auth_token method"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_success(self, mock_settings):
        """Test successful token fetch"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        # Mock the client with proper async json method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"access_token": "token123", "expires_in": 3600})

        service.client.get = AsyncMock(return_value=mock_response)

        token = await service._fetch_auth_token()

        assert token == "token123"

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_from_ss_structure(self, mock_settings):
        """Test token fetch from 'ss' structure"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"ss": [["token_from_ss"]]})

        service.client.get = AsyncMock(return_value=mock_response)

        token = await service._fetch_auth_token()

        assert token == "token_from_ss"

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_failure_non_200(self, mock_settings):
        """Test token fetch failure with non-200 status"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        service.client.get = AsyncMock(return_value=mock_response)

        token = await service._fetch_auth_token()

        assert token is None

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_failure_exception(self, mock_settings):
        """Test token fetch with exception"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        service.client.get = AsyncMock(side_effect=Exception("Test error"))

        token = await service._fetch_auth_token()

        assert token is None


class TestEnsureValidToken:
    """Test _ensure_valid_token method"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_ensure_valid_token_no_token(self, mock_settings):
        """Test ensuring valid token when none exists"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        service.bearer_token = None

        # Mock fetch token
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"access_token": "new_token"})

        service.client.get = AsyncMock(return_value=mock_response)

        result = await service._ensure_valid_token()

        assert result is True
        assert service.bearer_token == "new_token"

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_ensure_valid_token_still_valid(self, mock_settings):
        """Test ensuring valid token when token is still valid"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        service.bearer_token = "valid_token"
        service.token_expires_at = datetime.now() + timedelta(hours=1)

        result = await service._ensure_valid_token()

        assert result is True
        assert service.bearer_token == "valid_token"

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_ensure_valid_token_refresh_needed(self, mock_settings):
        """Test ensuring valid token when refresh is needed"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        service.bearer_token = "old_token"
        service.token_expires_at = datetime.now() - timedelta(minutes=1)

        # Mock fetch token
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"access_token": "refreshed_token"})

        service.client.get = AsyncMock(return_value=mock_response)

        result = await service._ensure_valid_token()

        assert result is True
        assert service.bearer_token == "refreshed_token"

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_ensure_valid_token_refresh_failed(self, mock_settings):
        """Test ensuring valid token when refresh fails"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        service.bearer_token = "old_token"
        service.token_expires_at = datetime.now() - timedelta(minutes=1)

        # Mock failed fetch
        mock_response = AsyncMock()
        mock_response.status_code = 401

        service.client.get = AsyncMock(return_value=mock_response)

        result = await service._ensure_valid_token()

        assert result is False


class TestSendNotification:
    """Test _send_notification method"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_success(self, mock_settings):
        """Test successful notification sending"""
        mock_settings.notification_endpoint_url = "http://localhost/notify"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        payload = {
            "version": "2.0",
            "message_id": "msg123",
            "timestamp": datetime.now().isoformat(),
            "notification_type": "streaming_call_start",
            "call_metadata": {"call_id": "test123"},
            "payload": {},
            "processing_mode": "streaming"
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"success": True})

        service.client.post = AsyncMock(return_value=mock_response)

        result = await service._send_notification(payload)

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_with_base64(self, mock_settings):
        """Test notification with base64 encoding"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = True
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        payload = {
            "version": "2.0",
            "message_id": "msg123",
            "timestamp": datetime.now().isoformat(),
            "notification_type": "test",
            "call_metadata": {"call_id": "test123"},
            "payload": {"data": "test"}
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200

        service.client.post = AsyncMock(return_value=mock_response)

        result = await service._send_notification(payload)

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_mock_mode(self, mock_settings):
        """Test notification in mock mode"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = True
        mock_settings.mock_notifications_folder = "/tmp/mock"

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        payload = {
            "version": "2.0",
            "message_id": "msg123",
            "timestamp": datetime.now().isoformat(),
            "notification_type": "test",
            "call_metadata": {"call_id": "test123"},
            "payload": {"data": "test"}
        }

        with patch.object(service, '_write_mock_notification', new_callable=AsyncMock):
            result = await service._send_notification(payload)

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_retry_on_error(self, mock_settings):
        """Test notification retry on error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 0.1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        payload = {
            "version": "2.0",
            "message_id": "msg123",
            "timestamp": datetime.now().isoformat(),
            "notification_type": "test",
            "call_metadata": {"call_id": "test123"},
            "payload": {}
        }

        # First fails, then succeeds
        mock_error_response = AsyncMock()
        mock_error_response.status_code = 500
        mock_error_response.raise_for_status = AsyncMock(side_effect=httpx.HTTPStatusError(
            "500", request=None, response=mock_error_response
        ))
        mock_error_response.text = "Server error"

        mock_success_response = AsyncMock()
        mock_success_response.status_code = 200
        mock_success_response.raise_for_status = AsyncMock(return_value=None)

        service.client.post = AsyncMock(side_effect=[
            mock_error_response,
            mock_success_response
        ])

        result = await service._send_notification(payload)

        # Should retry and eventually succeed
        assert result is True


class TestSendNotificationMethod:
    """Test send_notification method"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_method_success(self, mock_settings):
        """Test send_notification method success"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_notification(
            call_id="call123",
            notification_type=NotificationType.STREAMING_CALL_START,
            processing_mode=ProcessingMode.STREAMING,
            payload_data={"test": "data"}
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_method_error(self, mock_settings):
        """Test send_notification method with error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        with patch.object(service, '_send_notification', side_effect=Exception("Test error")):
            result = await service.send_notification(
                call_id="call123",
                notification_type=NotificationType.STREAMING_CALL_START,
                processing_mode=ProcessingMode.STREAMING,
                payload_data={}
            )

        assert result is False


class TestStreamingNotifications:
    """Test streaming notification methods"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_streaming_transcription(self, mock_settings):
        """Test sending streaming transcription"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_streaming_transcription(
            "call123",
            "segment text",
            "cumulative text"
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_streaming_translation(self, mock_settings):
        """Test sending streaming translation"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_streaming_translation(
            "call123",
            "window text",
            "cumulative translation"
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_streaming_entities(self, mock_settings):
        """Test sending streaming entities"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_streaming_entities(
            "call123",
            {"persons": ["John"], "locations": ["Home"]}
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_streaming_classification(self, mock_settings):
        """Test sending streaming classification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_streaming_classification(
            "call123",
            {"category": "abuse", "urgency": "high"}
        )

        assert result is True


class TestDisabledNotifications:
    """Test disabled notification methods"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_call_start_disabled(self, mock_settings):
        """Test send_call_start is disabled"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        result = await service.send_call_start(
            "call123",
            ProcessingMode.STREAMING,
            {}
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_call_end_streaming_disabled(self, mock_settings):
        """Test send_call_end_streaming is disabled"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        result = await service.send_call_end_streaming(
            "call123",
            "transcript",
            ProcessingMode.STREAMING
        )

        assert result is True


class TestPostcallNotifications:
    """Test postcall notification methods"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_postcall_transcription(self, mock_settings):
        """Test sending postcall transcription"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_postcall_transcription("call123", "Full transcript")

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('app.services.enhanced_notification_service.SessionLocal')
    async def test_send_postcall_complete(self, mock_session, mock_settings):
        """Test sending postcall complete"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        # Mock the db session
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        result = await service.send_postcall_complete(
            "call123",
            {"insights": "data"},
            {"transcript": "data"}
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_progress_update(self, mock_settings):
        """Test sending progress update"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_progress_update(
            "call123",
            "processing",
            75
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_error_notification(self, mock_settings):
        """Test sending error notification"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 3
        mock_settings.notification_retry_delay = 1
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token"

        service.client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await service.send_error_notification(
            "call123",
            "NetworkError",
            "Connection failed",
            "notification_service"
        )

        assert result is True


class TestPayloadLogging:
    """Test payload logging functionality"""

    @patch('app.services.enhanced_notification_service.settings')
    def test_log_payload_success(self, mock_settings):
        """Test successful payload logging"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = True
        mock_settings.agent_payload_log_file = "/tmp/payloads.jsonl"

        with patch('builtins.open', new_callable=mock_open):
            service = EnhancedNotificationService()
            payload = {"notification_type": "test", "call_metadata": {"call_id": "test123"}}
            request_body = {"data": "test"}

            service._log_payload(payload, request_body)

    @patch('app.services.enhanced_notification_service.settings')
    def test_log_payload_disabled(self, mock_settings):
        """Test payload logging when disabled"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()
        payload = {}
        request_body = {}

        service._log_payload(payload, request_body)
        assert service.enable_payload_logging is False

    @patch('app.services.enhanced_notification_service.settings')
    def test_log_payload_error(self, mock_settings):
        """Test payload logging with error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = True
        mock_settings.agent_payload_log_file = "/tmp/payloads.jsonl"

        service = EnhancedNotificationService()

        with patch('builtins.open', side_effect=Exception("Test error")):
            payload = {"notification_type": "test"}
            request_body = {"data": "test"}
            service._log_payload(payload, request_body)


class TestCreateFeedbackEntries:
    """Test create_feedback_entries method"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('app.services.enhanced_notification_service.SessionLocal')
    @patch('app.services.enhanced_notification_service.FeedbackRepository')
    async def test_create_feedback_entries_success(self, mock_feedback_repo, mock_session, mock_settings):
        """Test creating feedback entries"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_feedback_repo.create_initial_feedback.return_value = MagicMock()

        pipeline_results = {
            "transcript": "Test transcript",
            "classification": {"category": "abuse"},
            "entities": {"persons": ["John"]},
            "summary": "Test summary",
            "translation": "Translated",
            "qa_scores": {"score": 0.95}
        }

        await service.create_feedback_entries("call123", pipeline_results, "post_call")

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('app.services.enhanced_notification_service.SessionLocal')
    async def test_create_feedback_entries_error(self, mock_session, mock_settings):
        """Test creating feedback entries with error"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_session.side_effect = Exception("Database error")

        pipeline_results = {"transcript": "Test"}

        # Should not raise, just log error
        await service.create_feedback_entries("call123", pipeline_results)


class TestUnknownNotificationTypes:
    """Test handling of unknown notification types"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    async def test_write_mock_unknown_type(self, mock_file, mock_exists, mock_makedirs, mock_settings):
        """Test writing mock notification with unknown type"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.mock_notifications_folder = "/tmp/mock_notifications"

        service = EnhancedNotificationService()

        payload = {
            "call_metadata": {"call_id": "call123"},
            "notification_type": "unknown_type_123",
            "timestamp": datetime.now().isoformat(),
            "processing_mode": "post_call",
            "payload": {"custom_data": "value"}
        }

        await service._write_mock_notification(payload)
        assert mock_file.called


class TestErrorPaths:
    """Test error handling paths"""

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_no_token_in_response(self, mock_settings):
        """Test token fetch when no token in response"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"data": "no_token_here"})

        service.client.get = AsyncMock(return_value=mock_response)

        token = await service._fetch_auth_token()

        assert token is None

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_error_with_readable_response(self, mock_settings):
        """Test token fetch error with readable response body"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        service.client.get = AsyncMock(return_value=mock_response)

        token = await service._fetch_auth_token()

        assert token is None

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_fetch_auth_token_error_response_unreadable(self, mock_settings):
        """Test token fetch error with unreadable response body"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = PropertyMock(side_effect=Exception("Cannot read"))

        service.client.get = AsyncMock(return_value=mock_response)

        token = await service._fetch_auth_token()

        assert token is None

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    async def test_send_notification_request_error(self, mock_settings):
        """Test send notification with RequestError"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False
        mock_settings.notification_max_retries = 1
        mock_settings.notification_retry_delay = 0.001
        mock_settings.mock_enabled = False

        service = EnhancedNotificationService()
        service.bearer_token = "token123"

        payload = {
            "version": "2.0",
            "message_id": "msg123",
            "timestamp": datetime.now().isoformat(),
            "notification_type": "test",
            "call_metadata": {"call_id": "test123"},
            "payload": {}
        }

        service.client.post = AsyncMock(side_effect=httpx.RequestError("Connection error"))

        result = await service._send_notification(payload)

        assert result is False

    @pytest.mark.asyncio
    @patch('app.services.enhanced_notification_service.settings')
    @patch('app.services.enhanced_notification_service.SessionLocal')
    @patch('app.services.enhanced_notification_service.FeedbackRepository')
    async def test_create_feedback_entries_none_result(self, mock_feedback_repo, mock_session, mock_settings):
        """Test creating feedback when repository returns None"""
        mock_settings.notification_endpoint_url = "http://localhost"
        mock_settings.notification_auth_endpoint_url = "http://localhost/auth"
        mock_settings.notification_basic_auth = "auth"
        mock_settings.use_base64_encoding = False
        mock_settings.site_id = "site"
        mock_settings.notification_request_timeout = 30
        mock_settings.enable_agent_payload_logging = False

        service = EnhancedNotificationService()

        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_feedback_repo.create_initial_feedback.return_value = None

        pipeline_results = {
            "transcript": "Test transcript",
            "classification": {"category": "abuse"}
        }

        await service.create_feedback_entries("call123", pipeline_results)
        # Should complete without error
