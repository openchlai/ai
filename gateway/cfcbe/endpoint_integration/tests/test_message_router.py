import pytest
from unittest.mock import MagicMock, patch
from endpoint_integration.message_router import MessageRouter
from shared.models.standard_message import StandardMessage

@pytest.fixture
def standard_message():
    return StandardMessage(
        platform="webform",
        source_uid="abc123",
        source_timestamp=1717072085.123,
        metadata={
            "victim": {"name": "John Doe", "age": 25},
            "perpetrator": {"name": "Perp Name"}
        },
        source="form-site",
        source_address="https://form.example.com",
        message_id="msg-001",
        content="This is a test message"
    )

@pytest.fixture
def message_router():
    with patch('endpoint_integration.message_router.ConversationService') as MockConversationService:
        mock_convo_service = MockConversationService.return_value
        mock_convo_service.get_or_create_conversation.return_value = MagicMock()
        
        router = MessageRouter()
        router.endpoint_config = {
            "cases_endpoint": {
                "url": "http://example.com/api/cases"
            }
        }
        return router

def test_route_to_valid_endpoint(message_router, standard_message):
    with patch('endpoint_integration.message_router.MessageRouter._send_to_endpoint') as mock_send:
        mock_send.return_value = {"status": "success"}
        result = message_router.route_to_endpoint(standard_message)
        assert result["status"] == "success"

def test_route_to_unknown_endpoint(message_router, standard_message):
    # Use a platform that routes to a non-configured endpoint
    standard_message.platform = "whatsapp"  # will route to messaging_endpoint (not in config)
    result = message_router.route_to_endpoint(standard_message)
    assert result["status"] == "error"
    assert "Endpoint not configured" in result["error"]

def test_determine_endpoint_webform(message_router, standard_message):
    standard_message.platform = "webform"
    endpoint = message_router._determine_endpoint(standard_message)
    assert endpoint == "cases_endpoint"

def test_determine_endpoint_others(message_router, standard_message):
    standard_message.platform = "whatsapp"
    endpoint = message_router._determine_endpoint(standard_message)
    assert endpoint == "messaging_endpoint"
