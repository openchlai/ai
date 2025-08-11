import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.api.queue_routes import router 
from app.main import app

client = TestClient(app)

def mock_queue():
    mock = MagicMock()
    # Mock status for a single request
    mock.get_request_status.side_effect = lambda req_id: {
        "req-123": {"status": "queued", "created_at": "...", "position": 0},
        "req-456": {"status": "processing", "created_at": "..."},
        "req-789": {"status": "completed", "created_at": "...", "completed_at": "..."},
        "req-000": {"status": "failed", "created_at": "...", "error": "test error"}
    }.get(req_id)
    # Mock queue-level status
    mock.get_queue_status.return_value = {
        "queue_size": 2,
        "max_queue_size": 10,
        "pending_requests": 1,
        "processing_requests": 1,
        "completed_requests": 10,
        "failed_requests": 2,
        "total_requests": 12
    }
    return mock

# Patch the request_queue for all tests in this file
@pytest.fixture(autouse=True)
def mock_request_queue_fixture():
    with patch('app.api.queue_routes.request_queue', new=mock_queue()) as mock_queue_instance:
        yield mock_queue_instance


def test_get_queue_status_success():
    """Test retrieving overall queue status."""
    response = client.get("/queue/status")
    assert response.status_code == 200
    assert response.json()["queue_size"] == 2
    assert response.json()["total_requests"] == 12

def test_get_request_status_success():
    """Test retrieving status for a specific, valid request."""
    response = client.get("/queue/status/req-123")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert "position" in response.json()

def test_get_request_status_not_found():
    """Test retrieving status for a non-existent request."""
    response = client.get("/queue/status/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"


def test_get_queue_metrics_success():
    """Test retrieving calculated queue metrics."""
    response = client.get("/queue/metrics")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total_requests"] == 12
    assert response_json["success_rate_percent"] == 83.33
    assert response_json["failure_rate_percent"] == 16.67
    assert response_json["queue_utilization_percent"] == 20.0

def test_get_queue_metrics_no_requests():
    """Test metrics calculation when no requests have been made."""
    # Temporarily override the mock for this test
    with patch('app.api.queue_routes.request_queue') as mock:
        mock.get_queue_status.return_value = {
            "queue_size": 0,
            "max_queue_size": 10,
            "pending_requests": 0,
            "processing_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "total_requests": 0
        }
        response = client.get("/queue/metrics")
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["total_requests"] == 0
        assert response_json["success_rate_percent"] == 0
        assert response_json["failure_rate_percent"] == 0
        assert response_json["queue_utilization_percent"] == 0


def test_cancel_request_success(mock_request_queue_fixture): 
    """Test canceling a queued request."""
    response = client.delete("/queue/request/req-123")
    assert response.status_code == 200
    assert response.json()["message"] == "Request cancelled successfully"
    # Verify that the complete_request method was called
    mock_request_queue_fixture.complete_request.assert_called_with("req-123", error="Cancelled by user")

def test_cancel_request_not_found():
    """Test canceling a non-existent request."""
    response = client.delete("/queue/request/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"

def test_cancel_request_already_processing():
    """Test canceling a request that is currently being processed."""
    response = client.delete("/queue/request/req-456")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot cancel request that is already processing"

def test_cancel_request_already_completed():
    """Test canceling a request that has already been completed."""
    response = client.delete("/queue/request/req-789")
    assert response.status_code == 400
    assert response.json()["detail"] == "Request already completed"

def test_cancel_request_already_failed():
    """Test canceling a request that has already failed."""
    response = client.delete("/queue/request/req-000")
    assert response.status_code == 400
    assert response.json()["detail"] == "Request already completed"