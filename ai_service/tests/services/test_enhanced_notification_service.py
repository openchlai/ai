import pytest
import httpx
import json
import base64
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.enhanced_notification_service import EnhancedNotificationService, NotificationType
from app.core.enhanced_processing_manager import EnhancedProcessingMode
from app.config.settings import Settings

@pytest.fixture
def mock_settings():
    """Fixture to mock settings for testing."""
    mock = MagicMock()  # Remove spec to allow any attribute
    mock.notification_version = "2.0"
    mock.site_id = "test_site"
    mock.enable_ui_metadata = True
    mock.enable_agent_payload_logging = True  # Required for notification service
    mock.agent_payload_log_file = "/tmp/agent_payloads.log"  # Log file path
    mock.mock_enabled = False  # Disable mock mode for tests
    mock.mock_notifications = False  # Disable mock notifications mode
    mock.notification_endpoint_url = "http://test-notification-url.com"
    mock.notification_auth_endpoint_url = "http://test-auth-url.com"
    mock.notification_basic_auth = "test_basic_auth"
    mock.use_base64_encoding = False
    mock.notification_request_timeout = 10
    mock.notification_max_retries = 3  # Max retries for notification sending
    mock.notification_retry_delay = 1.0  # Retry delay in seconds
    mock.mock_notifications_folder = "/tmp/mock_notifications"  # Mock notifications folder
    return mock

@pytest.fixture
def notification_service(mock_settings):
    """Fixture to create an EnhancedNotificationService instance with mocked settings."""
    with patch('app.services.enhanced_notification_service.settings', new=mock_settings):
        service = EnhancedNotificationService()
        service.client = AsyncMock(spec=httpx.AsyncClient) # Mock the httpx client
        yield service

@pytest.mark.asyncio
async def test_create_base_payload(notification_service):
    """Test the creation of a base payload."""
    call_id = "test_call_123"
    notification_type = NotificationType.STREAMING_TRANSCRIPTION_SEGMENT
    processing_mode = EnhancedProcessingMode.STREAMING
    payload_data = {"segment": "hello", "cumulative_transcript": "hello world"}
    ui_metadata = {"display_priority": "high"}

    payload = notification_service._create_base_payload(
        call_id, notification_type, processing_mode, payload_data, ui_metadata=ui_metadata
    )

    assert payload["version"] == "2.0"
    assert "message_id" in payload
    assert "timestamp" in payload
    assert payload["processing_mode"] == processing_mode.value
    assert payload["call_metadata"]["call_id"] == call_id
    assert payload["call_metadata"]["site_id"] == notification_service.site_id
    assert payload["notification_type"] == notification_type.value
    assert payload["payload"] == payload_data
    assert payload["status"] == "success"
    assert payload["error"] is None
    assert payload["ui_metadata"] == ui_metadata

@pytest.mark.asyncio
async def test_send_notification_success(notification_service):
    """Test successful sending of a notification."""
    notification_service.client.post.return_value = AsyncMock(spec=httpx.Response)
    notification_service.client.post.return_value.raise_for_status.return_value = None
    notification_service.client.post.return_value.status_code = 200

    data = notification_service._create_base_payload(
        "test_call_success", NotificationType.STREAMING_CALL_START, EnhancedProcessingMode.DUAL, {"message": "Call started"}
    )
    result = await notification_service._send_notification(data)

    assert result is True
    notification_service.client.post.assert_called_once()
    args, kwargs = notification_service.client.post.call_args
    assert kwargs["json"] == data
    assert kwargs["headers"]["Content-Type"] == "application/json"

@pytest.mark.asyncio
async def test_send_notification_http_error(notification_service):
    """Test sending notification with an HTTP error (triggers retry logic)."""
    notification_service.client.post.return_value = AsyncMock(spec=httpx.Response)
    notification_service.client.post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=httpx.Request("POST", "url"), response=httpx.Response(400)
    )
    notification_service.client.post.return_value.status_code = 400
    notification_service.client.post.return_value.text = "Error message"

    data = notification_service._create_base_payload(
        "test_call_http_error", NotificationType.STREAMING_CALL_START, EnhancedProcessingMode.DUAL, {"message": "Call started"}
    )
    result = await notification_service._send_notification(data)

    assert result is False
    # With retry logic, it should be called notification_max_retries times (3)
    assert notification_service.client.post.call_count == 3

@pytest.mark.asyncio
async def test_send_notification_general_exception(notification_service):
    """Test sending notification with a request error (which is caught and retried)."""
    notification_service.client.post.side_effect = httpx.RequestError("Network error")

    data = notification_service._create_base_payload(
        "test_call_general_error", NotificationType.STREAMING_CALL_START, EnhancedProcessingMode.DUAL, {"message": "Call started"}
    )
    result = await notification_service._send_notification(data)

    assert result is False
    # Should be called notification_max_retries times (3)
    assert notification_service.client.post.call_count == 3

@pytest.mark.asyncio
async def test_send_notification_base64_encoding(notification_service, mock_settings):
    """Test sending notification with Base64 encoding enabled."""
    mock_settings.use_base64_encoding = True
    notification_service.use_base64 = True # Update the service instance
    notification_service.client.post.return_value = AsyncMock(spec=httpx.Response)
    notification_service.client.post.return_value.raise_for_status.return_value = None
    notification_service.client.post.return_value.status_code = 200

    data = notification_service._create_base_payload(
        "test_call_base64", NotificationType.STREAMING_CALL_START, EnhancedProcessingMode.DUAL, {"message": "Call started"}
    )
    result = await notification_service._send_notification(data)

    assert result is True
    notification_service.client.post.assert_called_once()
    args, kwargs = notification_service.client.post.call_args

    sent_content = kwargs["json"]
    # Base64 encoding now uses 'message' key instead of 'data'
    assert "message" in sent_content
    decoded_data = json.loads(base64.b64decode(sent_content["message"]).decode('utf-8'))
    assert decoded_data == data

@pytest.mark.asyncio
async def test_send_streaming_transcription(notification_service):
    """Test send_streaming_transcription method."""
    with patch.object(notification_service, '_send_notification', new=AsyncMock()) as mock_send:
        await notification_service.send_streaming_transcription(
            "call_id_st", "segment text", "cumulative text"
        )
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        payload = args[0]
        assert payload["notification_type"] == NotificationType.STREAMING_TRANSCRIPTION.value
        assert payload["payload"]["segment_text"] == "segment text"
        assert payload["payload"]["cumulative_transcript"] == "cumulative text"
        assert payload["ui_metadata"]["display_panel"] == "transcript"

@pytest.mark.asyncio
async def test_send_postcall_complete(notification_service):
    """Test send_postcall_complete method."""
    with patch.object(notification_service, '_send_notification', new=AsyncMock()) as mock_send:
        with patch.object(notification_service, 'create_feedback_entries', new=AsyncMock()) as mock_feedback:
            unified_insights = {"case_type": "abuse"}
            pipeline_results = {"whisper": "done"}
            await notification_service.send_postcall_complete(
                "call_id_pc", unified_insights, pipeline_results
            )
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            payload = args[0]
            assert payload["notification_type"] == NotificationType.POSTCALL_COMPLETE.value
            assert payload["payload"]["unified_insights"] == unified_insights
            assert payload["payload"]["pipeline_results"] == pipeline_results

@pytest.mark.asyncio
async def test_send_progress_update(notification_service):
    """Test send_progress_update method."""
    with patch.object(notification_service, '_send_notification', new=AsyncMock()) as mock_send:
        await notification_service.send_progress_update(
            "call_id_progress", "download", 50.0
        )
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        payload = args[0]
        assert payload["notification_type"] == NotificationType.SYSTEM_PROCESSING_PROGRESS.value
        assert payload["payload"]["stage"] == "download"
        assert payload["payload"]["progress_percent"] == 50.0
        assert payload["status"] == "in_progress"

@pytest.mark.asyncio
async def test_send_error_notification(notification_service):
    """Test send_error_notification method."""
    with patch.object(notification_service, '_send_notification', new=AsyncMock()) as mock_send:
        await notification_service.send_error_notification(
            "call_id_error", "NetworkError", "Failed to connect", component="transcription", ui_metadata={"toast": "true"}
        )
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        payload = args[0]
        assert payload["notification_type"] == NotificationType.SYSTEM_PROCESSING_ERROR.value
        assert payload["status"] == "error"
        assert payload["error"]["error_type"] == "NetworkError"
        assert payload["error"]["error_message"] == "Failed to connect"
        assert payload["error"]["component"] == "transcription"
