
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.api.processing_mode_routes import router
from app.core.processing_modes import CallProcessingMode

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_strategy_manager():
    with patch('app.api.processing_mode_routes.processing_strategy_manager') as mock:
        mock.get_system_capabilities.return_value = {"cuda": True, "adaptive_supported": True}
        mock.config.default_mode = CallProcessingMode.ADAPTIVE
        mock.mode_usage_stats = {
            "realtime_only": 10,
            "postcall_only": 5,
            "hybrid": 15,
            "adaptive": 20
        }
        yield mock

def test_get_processing_status(client, mock_strategy_manager):
    response = client.get("/api/v1/processing/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "system_capabilities" in data
    assert data["system_capabilities"]["cuda"] is True

def test_get_processing_status_error(client, mock_strategy_manager):
    mock_strategy_manager.get_system_capabilities.side_effect = Exception("System error")
    response = client.get("/api/v1/processing/status")
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to get processing status"

def test_get_available_modes(client, mock_strategy_manager):
    response = client.get("/api/v1/processing/modes")
    assert response.status_code == 200
    data = response.json()
    assert "available_modes" in data
    assert len(data["available_modes"]) == len(CallProcessingMode)
    assert data["current_default"] == "adaptive"

def test_update_processing_configuration_success(client, mock_strategy_manager):
    mock_strategy_manager.update_mode_configuration.return_value = True
    payload = {
        "default_mode": "hybrid",
        "realtime_config": {"chunk_size": 10},
        "postcall_config": {"priority": "high"}
    }
    response = client.post("/api/v1/processing/configure", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_strategy_manager.update_mode_configuration.assert_called_once()

def test_update_processing_configuration_failure(client, mock_strategy_manager):
    mock_strategy_manager.update_mode_configuration.return_value = False
    payload = {"default_mode": "invalid"}
    response = client.post("/api/v1/processing/configure", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to update configuration"

def test_create_call_processing_plan(client, mock_strategy_manager):
    mock_plan = {"processing_mode": "hybrid", "streaming": True}
    mock_strategy_manager.get_sanitized_processing_plan.return_value = mock_plan
    
    payload = {
        "call_id": "test_call_1",
        "mode_override": "hybrid",
        "call_context": {"user": "tester"}
    }
    response = client.post("/api/v1/processing/plan", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["processing_plan"] == mock_plan

def test_get_processing_statistics(client, mock_strategy_manager):
    response = client.get("/api/v1/processing/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_calls_processed"] == 50
    assert data["mode_usage_percentages"]["adaptive"] == 40.0

def test_test_processing_mode_success(client, mock_strategy_manager):
    mock_plan = {"processing_mode": "hybrid"}
    mock_strategy_manager.get_sanitized_processing_plan.return_value = mock_plan
    
    response = client.post("/api/v1/processing/test-mode/hybrid", params={"call_id": "custom_test_id"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["actual_mode"] == "hybrid"
    assert data["test_call_id"] == "custom_test_id"

def test_test_processing_mode_invalid(client, mock_strategy_manager):
    response = client.post("/api/v1/processing/test-mode/invalid_mode")
    assert response.status_code == 400
    assert "Invalid mode" in response.json()["detail"]


# Additional exception tests for missing coverage

def test_get_available_modes_exception(client):
    """Test exception handling in get_available_modes"""
    with patch('app.api.processing_mode_routes.processing_strategy_manager') as mock_mgr:
        # Make accessing config.default_mode.value raise an exception
        type(mock_mgr.config).default_mode = property(fget=lambda s: (_ for _ in ()).throw(Exception("Config error")))

        response = client.get("/api/v1/processing/modes")
        assert response.status_code == 500
        assert "Failed to get available modes" in response.json()["detail"]


def test_update_processing_configuration_exception(client, mock_strategy_manager):
    """Test exception handling in update_processing_configuration"""
    mock_strategy_manager.update_mode_configuration.side_effect = Exception("Update failed")

    payload = {"default_mode": "hybrid"}
    response = client.post("/api/v1/processing/configure", json=payload)
    assert response.status_code == 500
    assert "Failed to update" in response.json()["detail"]


def test_create_call_processing_plan_exception(client, mock_strategy_manager):
    """Test exception handling in create_call_processing_plan"""
    mock_strategy_manager.get_sanitized_processing_plan.side_effect = Exception("Plan creation failed")

    payload = {"call_id": "test_call"}
    response = client.post("/api/v1/processing/plan", json=payload)
    assert response.status_code == 500
    assert "Failed to create processing plan" in response.json()["detail"]


def test_get_processing_statistics_exception(client, mock_strategy_manager):
    """Test exception handling in get_processing_statistics"""
    mock_strategy_manager.mode_usage_stats = None  # Cause an error

    response = client.get("/api/v1/processing/statistics")
    assert response.status_code == 500
    assert "Failed to get statistics" in response.json()["detail"]


def test_test_processing_mode_exception(client, mock_strategy_manager):
    """Test exception handling in test_processing_mode"""
    mock_strategy_manager.get_sanitized_processing_plan.side_effect = Exception("Test mode failed")

    response = client.post("/api/v1/processing/test-mode/hybrid")
    assert response.status_code == 500
    assert "Failed to test" in response.json()["detail"]
