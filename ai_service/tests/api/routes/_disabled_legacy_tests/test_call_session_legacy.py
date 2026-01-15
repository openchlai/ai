import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock 
from app.main import app 

class MockCallSession:
    def __init__(self, call_id="test_id"):
        self.call_id = call_id
        self.cumulative_transcript = "This is a test transcript."
        self.total_audio_duration = 120.5
        self.segment_count = 5
        self.status = "in_progress"
        self.start_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        self.last_activity = datetime(2023, 1, 1, 10, 2, 0, tzinfo=timezone.utc)
        self.transcript_segments = [
            {"id": 1, "text": "Hello."},
            {"id": 2, "text": "How are you?"}
        ]

    def to_dict(self):
        return {
            "call_id": self.call_id,
            "cumulative_transcript": self.cumulative_transcript,
            "total_audio_duration": self.total_audio_duration,
            "segment_count": self.segment_count,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

class MockProgressiveAnalysis:
    def __init__(self, call_id="test_id"):
        self.call_id = call_id
        self.cumulative_translation = "This is a translated transcript."
        self.windows = [
            MagicMock(translation="translated segment 1"),
            MagicMock(translation="translated segment 2")
        ]
        self.latest_entities = [{"entity": "person", "text": "John"}]
        self.latest_classification = {"topic": "support", "score": 0.9}
        self.processing_stats = {"total_tokens": 100}
        self.entity_evolution = [
            {"segment": 1, "entities": [{"entity": "person", "text": "Alice"}]},
            {"segment": 2, "entities": [{"entity": "location", "text": "Paris"}]}
        ]
        self.classification_evolution = [
            {"segment": 1, "classification": {"topic": "greeting"}},
            {"segment": 2, "classification": {"topic": "problem_statement"}}
        ]

    def to_dict(self):
        return {
            "call_id": self.call_id,
            "cumulative_translation": self.cumulative_translation,
            "latest_entities": self.latest_entities,
            "latest_classification": self.latest_classification
        }

@pytest.fixture
def mock_call_session_manager():
    """Fixture to mock the call_session_manager singleton"""
    with patch("app.api.call_session_routes.call_session_manager") as mock_manager:
        mock_manager.get_all_active_sessions = AsyncMock(return_value=[MockCallSession(), MockCallSession("test_id_2")])
        mock_manager.get_session_stats = AsyncMock(return_value={"active_sessions": 1, "completed_sessions": 10})
        mock_manager.get_session = AsyncMock()
        mock_manager.end_session = AsyncMock()
        mock_manager._trigger_ai_pipeline = AsyncMock()
        yield mock_manager

@pytest.fixture
def mock_progressive_processor():
    """Fixture to mock the progressive_processor singleton"""
    with patch("app.api.call_session_routes.progressive_processor") as mock_processor:
        mock_processor.get_call_analysis = AsyncMock()
        yield mock_processor

@pytest.fixture
def mock_agent_notification_service():
    """Fixture to mock the enhanced_notification_service singleton"""
    with patch("app.api.call_session_routes.enhanced_notification_service") as mock_service:
        mock_service.get_health_status = AsyncMock()
        mock_service._ensure_valid_token = AsyncMock()
        mock_service.send_call_start = AsyncMock()
        mock_service.send_notification = AsyncMock(return_value=True)
        yield mock_service


        
def test_get_active_calls_success(mock_call_session_manager):
    """Test getting a list of active calls successfully."""
    mock_call_session_manager.get_all_active_sessions.return_value = [MockCallSession(), MockCallSession("test_id_2")]
    client = TestClient(app)
    response = client.get("/api/v1/calls/active")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["call_id"] == "test_id"

def test_get_active_calls_internal_error(mock_call_session_manager):
    """Test handling of internal server error when getting active calls."""
    mock_call_session_manager.get_all_active_sessions.side_effect = Exception("Test error")
    client = TestClient(app)
    response = client.get("/api/v1/calls/active")
    
    assert response.status_code == 500
    assert "Failed to retrieve active calls" in response.json()["detail"]

def test_get_call_stats_success(mock_call_session_manager):
    """Test getting call statistics successfully."""
    mock_call_session_manager.get_session_stats.return_value = {"active_sessions": 1, "completed_sessions": 10}
    client = TestClient(app)
    response = client.get("/api/v1/calls/stats")
    
    assert response.status_code == 200
    assert response.json()["active_sessions"] == 1

def test_get_call_session_success(mock_call_session_manager):
    """Test getting a specific call session successfully."""
    mock_session = MockCallSession("123")
    mock_call_session_manager.get_session.return_value = mock_session
    client = TestClient(app)
    response = client.get("/api/v1/calls/123")
    
    assert response.status_code == 200
    assert response.json()["call_id"] == "123"

def test_get_call_session_not_found(mock_call_session_manager):
    """Test getting a call session that does not exist."""
    mock_call_session_manager.get_session.return_value = None
    client = TestClient(app)
    response = client.get("/api/v1/calls/non_existent_id")
    
    assert response.status_code == 404
    assert "Call session non_existent_id not found" in response.json()["detail"]

def test_get_call_transcript_success(mock_call_session_manager):
    """Test getting a call transcript without segments."""
    mock_session = MockCallSession("123")
    mock_call_session_manager.get_session.return_value = mock_session
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/transcript")
    
    assert response.status_code == 200
    assert "cumulative_transcript" in response.json()
    assert "segments" not in response.json()

def test_get_call_transcript_with_segments(mock_call_session_manager):
    """Test getting a call transcript with segments included."""
    mock_session = MockCallSession("123")
    mock_call_session_manager.get_session.return_value = mock_session
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/transcript?include_segments=true")
    
    assert response.status_code == 200
    assert "segments" in response.json()
    assert len(response.json()["segments"]) == 2

def test_manually_end_call_success(mock_call_session_manager):
    """Test ending a call session successfully."""
    mock_session = MockCallSession("123")
    mock_call_session_manager.end_session.return_value = mock_session
    client = TestClient(app)
    response = client.post("/api/v1/calls/123/end?reason=manual")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Call session 123 ended successfully"
    assert "final_transcript" in response.json()

def test_get_call_segments_success(mock_call_session_manager):
    """Test getting paginated call segments."""
    mock_session = MockCallSession("123")
    mock_session.transcript_segments = [{"id": i, "text": f"segment {i}"} for i in range(10)]
    mock_call_session_manager.get_session.return_value = mock_session
    
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/segments?limit=5&offset=2")
        
    assert response.status_code == 200
    data = response.json()
    assert len(data["segments"]) == 5
    assert data["segments"][0]["text"] == "segment 2"
    assert data["has_more"] is True

def test_export_call_for_ai_pipeline_json_format(mock_call_session_manager):
    """Test exporting call data in JSON format."""
    mock_session = MockCallSession("123")
    mock_session.cumulative_transcript = "A" * 60 # Ensure transcript is long enough
    mock_call_session_manager.get_session.return_value = mock_session
    
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/export?format=json")
        
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "json"
    assert data["content"]["ready_for_ai_pipeline"] is True

def test_export_call_for_ai_pipeline_text_format(mock_call_session_manager):
    """Test exporting call data in text format."""
    mock_session = MockCallSession("123")
    mock_call_session_manager.get_session.return_value = mock_session
    
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/export?format=text")
        
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "text"
    assert data["content"] == "This is a test transcript."

def test_trigger_ai_pipeline_processing_success(mock_call_session_manager):
    """Test triggering the AI pipeline successfully."""
    mock_session = MockCallSession("123")
    mock_session.cumulative_transcript = "A" * 60 # Ensure transcript is long enough
    mock_call_session_manager.get_session.return_value = mock_session
    mock_call_session_manager._trigger_ai_pipeline = MagicMock() 
    
    client = TestClient(app)
    response = client.post("/api/v1/calls/123/trigger-ai-pipeline")
        
    assert response.status_code == 200
    assert "AI pipeline processing triggered" in response.json()["message"]
    mock_call_session_manager._trigger_ai_pipeline.assert_called_once()

def test_trigger_ai_pipeline_processing_transcript_too_short(mock_call_session_manager):
    """Test triggering AI pipeline with a short transcript."""
    mock_session = MockCallSession("123")
    mock_session.cumulative_transcript = "short" 
    mock_call_session_manager.get_session.return_value = mock_session
    
    client = TestClient(app)
    response = client.post("/api/v1/calls/123/trigger-ai-pipeline")
        
    assert response.status_code == 400
    assert "Call transcript too short" in response.json()["detail"]

def test_get_progressive_analysis_success(mock_progressive_processor):
    """Test getting progressive analysis successfully."""
    mock_analysis = MockProgressiveAnalysis("123")
    mock_progressive_processor.get_call_analysis.return_value = mock_analysis
    
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/progressive-analysis")
        
    assert response.status_code == 200
    assert response.json()["call_id"] == "123"

def test_get_call_translation_success(mock_progressive_processor):
    """Test getting cumulative translation."""
    mock_analysis = MockProgressiveAnalysis("123")
    mock_progressive_processor.get_call_analysis.return_value = mock_analysis
    
    client = TestClient(app)
    response = client.get("/api/v1/calls/123/translation")
        
    assert response.status_code == 200
    assert response.json()["cumulative_translation"] == "This is a translated transcript."


def test_get_agent_service_health_success(mock_agent_notification_service):
    """Test getting agent service health when available."""
    mock_agent_notification_service.get_health_status.return_value = {"status": "ok"}
    client = TestClient(app)
    response = client.get("/api/v1/calls/agent-service/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_agent_service_health_unavailable():
    """Test getting agent service health when not available."""
    # Mock the service to raise an exception
    with patch("app.api.call_session_routes.enhanced_notification_service") as mock_service:
        mock_service.get_health_status.side_effect = Exception("Service unavailable")
        client = TestClient(app)
        response = client.get("/api/v1/calls/agent-service/health")

        # Should return error status
        assert response.status_code in [500, 503]

def test_test_agent_auth_success(mock_agent_notification_service):
    """Test successful agent authentication."""
    mock_agent_notification_service._ensure_valid_token = MagicMock(return_value=True)
    mock_agent_notification_service.bearer_token = "some_long_token_string"
    mock_agent_notification_service.token_expires_at = datetime.now()
    
    client = TestClient(app)
    response = client.post("/api/v1/calls/agent-service/test-auth")
    
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("app.api.call_session_routes.AGENT_SERVICE_AVAILABLE", new=True)
def test_test_agent_notification_success(mock_agent_notification_service):
    """Test sending a test notification successfully."""
    mock_agent_notification_service.send_call_start = MagicMock(return_value=True)
    
    client = TestClient(app)
    response = client.post("/api/v1/calls/agent-service/test-notification")
    
    assert response.status_code == 200
    assert response.json()["success"] is True