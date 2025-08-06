# tests/test_api_call_session_routes.py
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_app():
    """Create a test FastAPI app with call session routes"""
    from app.api.call_session_routes import router
    
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(mock_app):
    """Create test client"""
    return TestClient(mock_app)

@pytest.fixture
def mock_call_session():
    """Create a mock call session"""
    session = MagicMock()
    session.call_id = "test_call_001"
    session.status = "active"
    session.cumulative_transcript = "Hello, how can I help you today? I need assistance with my account."
    session.total_audio_duration = 45.5
    session.segment_count = 3
    session.start_time = datetime(2023, 1, 1, 10, 0, 0)
    session.last_activity = datetime(2023, 1, 1, 10, 0, 45)
    session.transcript_segments = [
        {"text": "Hello, how can I help you today?", "start": 0.0, "end": 3.5, "confidence": 0.95},
        {"text": "I need assistance", "start": 4.0, "end": 6.2, "confidence": 0.88},
        {"text": "with my account.", "start": 6.5, "end": 8.1, "confidence": 0.92}
    ]
    session.to_dict.return_value = {
        "call_id": session.call_id,
        "status": session.status,
        "cumulative_transcript": session.cumulative_transcript,
        "total_duration": session.total_audio_duration,
        "segment_count": session.segment_count,
        "start_time": session.start_time.isoformat(),
        "last_activity": session.last_activity.isoformat()
    }
    return session

@pytest.fixture
def mock_call_session_manager():
    """Mock call session manager"""
    with patch('app.api.call_session_routes.call_session_manager') as mock:
        yield mock

@pytest.fixture
def mock_progressive_processor():
    """Mock progressive processor"""
    with patch('app.api.call_session_routes.progressive_processor') as mock:
        yield mock

@pytest.fixture
def mock_agent_service():
    """Mock agent notification service"""
    with patch('app.api.call_session_routes.agent_notification_service') as mock:
        yield mock

class TestActiveCallsEndpoint:
    """Test the /calls/active endpoint"""

    @pytest.mark.asyncio
    async def test_get_active_calls_success(self, client, mock_call_session_manager, mock_call_session):
        """Test successful retrieval of active calls"""
        # Mock multiple active sessions
        sessions = [mock_call_session, mock_call_session]
        mock_call_session_manager.get_all_active_sessions.return_value = sessions
        
        response = client.get("/api/v1/calls/active")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["call_id"] == "test_call_001"
        assert data[0]["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_active_calls_empty(self, client, mock_call_session_manager):
        """Test retrieval when no active calls exist"""
        mock_call_session_manager.get_all_active_sessions.return_value = []
        
        response = client.get("/api/v1/calls/active")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_active_calls_error(self, client, mock_call_session_manager):
        """Test error handling in active calls endpoint"""
        mock_call_session_manager.get_all_active_sessions.side_effect = Exception("Database error")
        
        response = client.get("/api/v1/calls/active")
        
        assert response.status_code == 500
        assert "Failed to retrieve active calls" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_active_calls_large_number(self, client, mock_call_session_manager, mock_call_session):
        """Test handling of large number of active calls"""
        # Create many mock sessions
        sessions = [mock_call_session for _ in range(100)]
        mock_call_session_manager.get_all_active_sessions.return_value = sessions
        
        response = client.get("/api/v1/calls/active")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 100

class TestCallStatsEndpoint:
    """Test the /calls/stats endpoint"""

    @pytest.mark.asyncio
    async def test_get_call_stats_success(self, client, mock_call_session_manager):
        """Test successful retrieval of call statistics"""
        mock_stats = {
            "active_sessions": 5,
            "total_sessions_today": 25,
            "average_duration": 120.5,
            "total_duration_today": 3012.5,
            "success_rate": 0.96,
            "error_rate": 0.04
        }
        mock_call_session_manager.get_session_stats.return_value = mock_stats
        
        response = client.get("/api/v1/calls/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active_sessions"] == 5
        assert data["total_sessions_today"] == 25
        assert data["average_duration"] == 120.5
        assert data["success_rate"] == 0.96

    @pytest.mark.asyncio
    async def test_get_call_stats_empty(self, client, mock_call_session_manager):
        """Test stats when no calls have been processed"""
        mock_stats = {
            "active_sessions": 0,
            "total_sessions_today": 0,
            "average_duration": 0.0,
            "total_duration_today": 0.0,
            "success_rate": 0.0,
            "error_rate": 0.0
        }
        mock_call_session_manager.get_session_stats.return_value = mock_stats
        
        response = client.get("/api/v1/calls/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active_sessions"] == 0
        assert data["total_sessions_today"] == 0

    @pytest.mark.asyncio
    async def test_get_call_stats_error(self, client, mock_call_session_manager):
        """Test error handling in stats endpoint"""
        mock_call_session_manager.get_session_stats.side_effect = Exception("Stats calculation failed")
        
        response = client.get("/api/v1/calls/stats")
        
        assert response.status_code == 500
        assert "Failed to retrieve call statistics" in response.json()["detail"]

class TestSpecificCallEndpoint:
    """Test the /calls/{call_id} endpoint"""

    @pytest.mark.asyncio
    async def test_get_call_session_success(self, client, mock_call_session_manager, mock_call_session):
        """Test successful retrieval of specific call session"""
        mock_call_session_manager.get_session.return_value = mock_call_session
        
        response = client.get("/api/v1/calls/test_call_001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["call_id"] == "test_call_001"
        assert data["status"] == "active"
        assert "cumulative_transcript" in data

    @pytest.mark.asyncio
    async def test_get_call_session_not_found(self, client, mock_call_session_manager):
        """Test retrieval of non-existent call session"""
        mock_call_session_manager.get_session.return_value = None
        
        response = client.get("/api/v1/calls/nonexistent_call")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_call_session_error(self, client, mock_call_session_manager):
        """Test error handling in specific call endpoint"""
        mock_call_session_manager.get_session.side_effect = Exception("Database error")
        
        response = client.get("/api/v1/calls/test_call_001")
        
        assert response.status_code == 500
        assert "Failed to retrieve call session" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_call_session_invalid_id(self, client, mock_call_session_manager):
        """Test call with invalid ID format"""
        mock_call_session_manager.get_session.return_value = None
        
        response = client.get("/api/v1/calls/invalid-id-format-!!!")
        
        assert response.status_code == 404

class TestCallTranscriptEndpoint:
    """Test the /calls/{call_id}/transcript endpoint"""

    @pytest.mark.asyncio
    async def test_get_call_transcript_success(self, client, mock_call_session_manager, mock_call_session):
        """Test successful retrieval of call transcript"""
        mock_call_session_manager.get_session.return_value = mock_call_session
        
        response = client.get("/api/v1/calls/test_call_001/transcript")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["call_id"] == "test_call_001"
        assert data["cumulative_transcript"] == "Hello, how can I help you today? I need assistance with my account."
        assert data["total_duration"] == 45.5
        assert data["segment_count"] == 3
        assert "segments" not in data  # Default is not to include segments

    @pytest.mark.asyncio
    async def test_get_call_transcript_with_segments(self, client, mock_call_session_manager, mock_call_session):
        """Test transcript retrieval with segments included"""
        mock_call_session_manager.get_session.return_value = mock_call_session
        
        response = client.get("/api/v1/calls/test_call_001/transcript?include_segments=true")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "segments" in data
        assert len(data["segments"]) == 3
        assert data["segments"][0]["text"] == "Hello, how can I help you today?"
        assert data["segments"][0]["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_get_call_transcript_not_found(self, client, mock_call_session_manager):
        """Test transcript retrieval for non-existent call"""
        mock_call_session_manager.get_session.return_value = None
        
        response = client.get("/api/v1/calls/nonexistent/transcript")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_call_transcript_query_parameters(self, client, mock_call_session_manager, mock_call_session):
        """Test various query parameter combinations"""
        mock_call_session_manager.get_session.return_value = mock_call_session
        
        # Test include_segments=false
        response = client.get("/api/v1/calls/test_call_001/transcript?include_segments=false")
        assert response.status_code == 200
        assert "segments" not in response.json()
        
        # Test include_segments=true
        response = client.get("/api/v1/calls/test_call_001/transcript?include_segments=true")
        assert response.status_code == 200
        assert "segments" in response.json()

    @pytest.mark.asyncio
    async def test_get_call_transcript_empty_transcript(self, client, mock_call_session_manager, mock_call_session):
        """Test transcript retrieval for call with no transcript"""
        mock_call_session.cumulative_transcript = ""
        mock_call_session.segment_count = 0
        mock_call_session.transcript_segments = []
        mock_call_session_manager.get_session.return_value = mock_call_session
        
        response = client.get("/api/v1/calls/test_call_001/transcript")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["cumulative_transcript"] == ""
        assert data["segment_count"] == 0

class TestEndCallEndpoint:
    """Test the /calls/{call_id}/end endpoint"""

    @pytest.mark.asyncio
    async def test_manually_end_call_success(self, client, mock_call_session_manager, mock_call_session):
        """Test successful manual call termination"""
        mock_call_session_manager.end_session.return_value = mock_call_session
        
        response = client.post("/api/v1/calls/test_call_001/end")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "Call session test_call_001 ended successfully" in data["message"]
        assert data["final_transcript"] == mock_call_session.cumulative_transcript
        assert data["total_duration"] == 45.5
        assert data["segment_count"] == 3

    @pytest.mark.asyncio
    async def test_manually_end_call_with_reason(self, client, mock_call_session_manager, mock_call_session):
        """Test manual call termination with custom reason"""
        mock_call_session_manager.end_session.return_value = mock_call_session
        
        response = client.post("/api/v1/calls/test_call_001/end?reason=timeout")
        
        assert response.status_code == 200
        # Verify that end_session was called with the custom reason
        mock_call_session_manager.end_session.assert_called_with("test_call_001", reason="timeout")

    @pytest.mark.asyncio
    async def test_manually_end_call_not_found(self, client, mock_call_session_manager):
        """Test ending a non-existent call"""
        mock_call_session_manager.end_session.return_value = None
        
        response = client.post("/api/v1/calls/nonexistent/end")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_manually_end_call_error(self, client, mock_call_session_manager):
        """Test error handling in end call endpoint"""
        mock_call_session_manager.end_session.side_effect = Exception("Failed to end session")
        
        response = client.post("/api/v1/calls/test_call_001/end")
        
        assert response.status_code == 500
        assert "Failed to end call session" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_manually_end_call_default_reason(self, client, mock_call_session_manager, mock_call_session):
        """Test ending call with default reason"""
        mock_call_session_manager.end_session.return_value = mock_call_session
        
        response = client.post("/api/v1/calls/test_call_001/end")
        
        assert response.status_code == 200
        # Verify default reason was used
        mock_call_session_manager.end_session.assert_called_with("test_call_001", reason="manual")

class TestProgressiveProcessingEndpoints:
    """Test progressive processing related endpoints"""

    @pytest.mark.asyncio
    async def test_get_processing_status(self, client, mock_progressive_processor):
        """Test getting progressive processing status"""
        mock_status = {
            "active_processors": 3,
            "queue_size": 5,
            "processing_rate": 2.5,
            "average_latency": 150.0
        }
        mock_progressive_processor.get_status.return_value = mock_status
        
        response = client.get("/api/v1/calls/processing/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active_processors"] == 3
        assert data["queue_size"] == 5
        assert data["processing_rate"] == 2.5

    @pytest.mark.asyncio
    async def test_get_call_processing_status(self, client, mock_progressive_processor):
        """Test getting processing status for specific call"""
        mock_status = {
            "call_id": "test_call_001",
            "processing_stage": "transcription",
            "progress": 0.75,
            "estimated_completion": 45.0,
            "current_segment": 3,
            "total_segments": 4
        }
        mock_progressive_processor.get_call_processing_status.return_value = mock_status
        
        response = client.get("/api/v1/calls/test_call_001/processing")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["call_id"] == "test_call_001"
        assert data["processing_stage"] == "transcription"
        assert data["progress"] == 0.75

class TestAgentIntegrationEndpoints:
    """Test agent integration endpoints"""

    @pytest.mark.asyncio
    async def test_agent_notification_health(self, client, mock_agent_service):
        """Test agent notification service health check"""
        mock_agent_service.get_health_status.return_value = {
            "status": "healthy",
            "notifications_sent": 150,
            "success_rate": 0.98,
            "last_notification": datetime(2023, 1, 1, 10, 0, 0).isoformat()
        }
        
        response = client.get("/api/v1/calls/agent/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["notifications_sent"] == 150

    @pytest.mark.asyncio
    async def test_test_agent_notification(self, client, mock_agent_service):
        """Test sending test notification to agent"""
        mock_agent_service.send_test_notification.return_value = True
        
        response = client.post("/api/v1/calls/agent/test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "test notification sent" in data["message"]

    @pytest.mark.asyncio
    async def test_agent_notification_service_unavailable(self, client):
        """Test endpoints when agent service is unavailable"""
        with patch('app.api.call_session_routes.AGENT_SERVICE_AVAILABLE', False):
            response = client.get("/api/v1/calls/agent/health")
            
            assert response.status_code == 503
            assert "Agent notification service not available" in response.json()["detail"]

class TestCallSessionRouteIntegration:
    """Test integration between different call session endpoints"""

    @pytest.mark.asyncio
    async def test_call_lifecycle_integration(self, client, mock_call_session_manager, mock_call_session):
        """Test complete call session lifecycle"""
        # Mock the session to be found in all calls
        mock_call_session_manager.get_session.return_value = mock_call_session
        mock_call_session_manager.end_session.return_value = mock_call_session
        
        # Get call session
        response = client.get("/api/v1/calls/test_call_001")
        assert response.status_code == 200
        
        # Get transcript
        response = client.get("/api/v1/calls/test_call_001/transcript")
        assert response.status_code == 200
        
        # End the call
        response = client.post("/api/v1/calls/test_call_001/end")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_concurrent_access_same_call(self, client, mock_call_session_manager, mock_call_session):
        """Test concurrent access to same call session"""
        import threading
        
        mock_call_session_manager.get_session.return_value = mock_call_session
        results = []
        
        def access_call():
            response = client.get("/api/v1/calls/test_call_001")
            results.append(response.status_code)
        
        # Start multiple threads accessing same call
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=access_call)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(status == 200 for status in results)

class TestCallSessionRouteConfiguration:
    """Test call session route configuration"""

    def test_router_configuration(self):
        """Test router is properly configured"""
        from app.api.call_session_routes import router
        
        assert router.prefix == "/api/v1/calls"
        assert "call-sessions" in router.tags

    @pytest.mark.asyncio
    async def test_logging_integration(self, client, mock_call_session_manager):
        """Test that endpoints log appropriately"""
        with patch('app.api.call_session_routes.logger') as mock_logger:
            # Trigger an error to test error logging
            mock_call_session_manager.get_all_active_sessions.side_effect = Exception("Test error")
            
            response = client.get("/api/v1/calls/active")
            
            assert response.status_code == 500
            mock_logger.error.assert_called()

    def test_response_model_validation(self, client, mock_call_session_manager, mock_call_session):
        """Test that response models are properly validated"""
        # Mock response that should match the expected model
        mock_call_session_manager.get_all_active_sessions.return_value = [mock_call_session]
        
        response = client.get("/api/v1/calls/active")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list of dictionaries with required fields
        assert isinstance(data, list)
        if len(data) > 0:
            assert "call_id" in data[0]
            assert "status" in data[0]

class TestErrorHandlingAcrossEndpoints:
    """Test error handling consistency across all call session endpoints"""

    @pytest.mark.asyncio
    async def test_database_connection_errors(self, client, mock_call_session_manager):
        """Test handling of database connection errors across endpoints"""
        error = Exception("Database connection lost")
        
        # Set all manager methods to raise the same error
        mock_call_session_manager.get_all_active_sessions.side_effect = error
        mock_call_session_manager.get_session_stats.side_effect = error
        mock_call_session_manager.get_session.side_effect = error
        mock_call_session_manager.end_session.side_effect = error
        
        # Test all endpoints handle the error gracefully
        endpoints = [
            ("/api/v1/calls/active", "GET"),
            ("/api/v1/calls/stats", "GET"),
            ("/api/v1/calls/test_call/transcript", "GET"),
            ("/api/v1/calls/test_call", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint)
            
            assert response.status_code == 500
            assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_malformed_call_ids(self, client, mock_call_session_manager):
        """Test handling of malformed call IDs"""
        mock_call_session_manager.get_session.return_value = None
        
        malformed_ids = ["", "   ", "call/with/slashes", "call with spaces", "call?with=query"]
        
        for call_id in malformed_ids:
            response = client.get(f"/api/v1/calls/{call_id}")
            assert response.status_code in [404, 422]  # Either not found or validation error