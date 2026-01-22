"""
Tests for the agent feedback API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.main import app
from app.db.models import AgentFeedback
from app.db.session import get_db

# This is the mock database session that will be used for all tests
mock_db = MagicMock()

def get_db_override():
    """Dependency override for get_db."""
    return mock_db

app.dependency_overrides[get_db] = get_db_override

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test."""
    mock_db.reset_mock()
    # Resetting specific method mocks if they are configured with side_effects or return_values
    mock_db.execute.reset_mock(return_value=True, side_effect=None)
    mock_db.query.reset_mock(return_value=None, side_effect=None)
    mock_db.refresh.reset_mock()

@pytest.fixture
def mock_feedback_repo():
    """Fixture to mock the FeedbackRepository."""
    with patch('app.api.agent_feedback_routes.FeedbackRepository') as mock_repo:
        yield mock_repo

def test_health_check_success():
    """Test the health check endpoint for the feedback system with a successful database connection."""
    mock_db.execute.return_value = None

    # Mock for the first db.query(...).scalar() call for total feedback
    mock_total_query = MagicMock()
    mock_total_query.scalar.return_value = 10

    # Mock for the second db.query(...).filter(...).scalar() call for rated feedback
    mock_rated_scalar = MagicMock()
    mock_rated_scalar.scalar.return_value = 5
    mock_rated_query = MagicMock()
    mock_rated_query.filter.return_value = mock_rated_scalar

    # Set the side_effect for the two calls to db.query
    mock_db.query.side_effect = [mock_total_query, mock_rated_query]

    response = client.get("/api/v1/agent-feedback/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["total_feedback_entries"] == 10
    assert data["rated_entries"] == 5
    assert data["rating_coverage"] == 50.0

def test_health_check_db_error():
    """Test the health check endpoint when the database connection fails."""
    mock_db.execute.side_effect = Exception("DB connection error")

    response = client.get("/api/v1/agent-feedback/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Service unhealthy"

def test_update_feedback_success(mock_feedback_repo):
    """Test successful feedback update."""
    feedback_entry = AgentFeedback(
        id=1,
        call_id="test_call_id",
        task="classification",
        prediction={"label": "sales"},
        feedback=5,
        reason="Accurate",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        processing_mode="streaming",
        model_version="v1.2"
    )
    mock_feedback_repo.update_feedback.return_value = feedback_entry
    # Mock the refresh to do nothing
    mock_db.refresh = MagicMock()

    request_data = {
        "call_id": "test_call_id",
        "task": "classification",
        "feedback": 5,
        "reason": "Accurate"
    }
    response = client.post("/api/v1/agent-feedback/update", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["call_id"] == "test_call_id"
    assert data["feedback"] == 5
    assert data["reason"] == "Accurate"
    mock_db.refresh.assert_called_once_with(feedback_entry)

def test_update_feedback_not_found(mock_feedback_repo):
    """Test feedback update when the entry is not found."""
    mock_feedback_repo.update_feedback.return_value = None

    request_data = {
        "call_id": "non_existent_call",
        "task": "ner",
        "feedback": 1,
        "reason": "Not found"
    }
    response = client.post("/api/v1/agent-feedback/update", json=request_data)

    assert response.status_code == 404
    assert "Feedback entry not found" in response.json()["detail"]

def test_update_feedback_invalid_task():
    """Test feedback update with an invalid task type."""
    request_data = {
        "call_id": "test_call_id",
        "task": "invalid_task",
        "feedback": 3
    }
    response = client.post("/api/v1/agent-feedback/update", json=request_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_get_call_feedback_success(mock_feedback_repo):
    """Test retrieving feedback for a specific call."""
    now = datetime.now()
    feedback_list = [
        AgentFeedback(id=1, call_id="call123", task="summarization", prediction={"summary": "..."}, created_at=now),
        AgentFeedback(id=2, call_id="call123", task="ner", prediction={"entities": []}, created_at=now)
    ]
    mock_feedback_repo.get_feedback.return_value = feedback_list

    response = client.get("/api/v1/agent-feedback/call/call123")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["task"] == "summarization"

def test_get_call_feedback_not_found(mock_feedback_repo):
    """Test retrieving feedback for a call with no entries."""
    mock_feedback_repo.get_feedback.return_value = []

    response = client.get("/api/v1/agent-feedback/call/non_existent_call")
    assert response.status_code == 404
    assert "No feedback found" in response.json()["detail"]

def test_get_feedback_statistics_success(mock_feedback_repo):
    """Test retrieving feedback statistics."""
    stats_data = {
        "period_days": 30,
        "tasks": {
            "classification": {"average_rating": 4.5, "count": 100},
            "ner": {"average_rating": 3.8, "count": 80}
        }
    }
    mock_feedback_repo.get_feedback_statistics.return_value = stats_data

    response = client.get("/api/v1/agent-feedback/statistics?days=30")
    assert response.status_code == 200
    data = response.json()
    assert data["period_days"] == 30
    assert "classification" in data["tasks"]

def test_get_feedback_statistics_error(mock_feedback_repo):
    """Test retrieving feedback statistics when an error occurs."""
    mock_feedback_repo.get_feedback_statistics.return_value = {"error": "Database query failed"}

    response = client.get("/api/v1/agent-feedback/statistics")
    assert response.status_code == 500
    assert "Database query failed" in response.json()["detail"]

def test_update_feedback_value_error(mock_feedback_repo):
    """Test feedback update when a ValueError occurs."""
    mock_feedback_repo.update_feedback.side_effect = ValueError("A value error occurred")
    request_data = {
        "call_id": "test_call_id",
        "task": "classification",
        "feedback": 5,
        "reason": "Accurate"
    }
    response = client.post("/api/v1/agent-feedback/update", json=request_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"

def test_update_feedback_exception(mock_feedback_repo):
    """Test feedback update when a generic exception occurs."""
    mock_feedback_repo.update_feedback.side_effect = Exception("A generic error occurred")
    request_data = {
        "call_id": "test_call_id",
        "task": "classification",
        "feedback": 5,
        "reason": "Accurate"
    }
    response = client.post("/api/v1/agent-feedback/update", json=request_data)
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to update feedback"

def test_get_call_feedback_exception(mock_feedback_repo):
    """Test retrieving feedback for a call when an exception occurs."""
    mock_feedback_repo.get_feedback.side_effect = Exception("A generic error occurred")
    response = client.get("/api/v1/agent-feedback/call/call123")
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to retrieve feedback"

def test_get_feedback_statistics_exception(mock_feedback_repo):
    """Test retrieving feedback statistics when an exception occurs."""
    mock_feedback_repo.get_feedback_statistics.side_effect = Exception("A generic error occurred")
    response = client.get("/api/v1/agent-feedback/statistics")
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to get statistics"
