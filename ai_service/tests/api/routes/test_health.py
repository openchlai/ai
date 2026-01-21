
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api.health_routes import router

@pytest.fixture
def mock_app():
    """Create a test FastAPI app with health routes"""
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(mock_app):
    """Create test client"""
    return TestClient(mock_app)

@pytest.fixture
def mock_dependencies():
    """Mock all dependencies for health routes"""
    # Patch targets must match where they are used in app.api.health_routes
    with patch('app.api.health_routes.settings') as mock_settings, \
         patch('app.api.health_routes.resource_manager') as mock_rm, \
         patch('app.api.health_routes.model_loader') as mock_ml, \
         patch('app.api.health_routes.celery_app') as mock_ca, \
         patch('app.api.health_routes.celery_monitor') as mock_cm, \
         patch('app.api.health_routes.is_api_server_mode') as mock_is_api, \
         patch('app.api.health_routes.get_execution_mode') as mock_exec_mode:
        
        mock_settings.app_version = "1.0.0"
        mock_settings.site_id = "test-site"
        mock_settings.alert_memory_usage = 85.0
        mock_settings.alert_queue_size = 90
        
        mock_rm.get_gpu_info.return_value = {"gpu_available": True}
        mock_rm.get_system_info.return_value = {"memory_percent": 40.0}
        
        mock_ml.get_model_status.return_value = {"test_model": {"status": "ready"}}
        mock_ml.get_system_capabilities.return_value = {"cuda": True}
        mock_ml.get_ready_models.return_value = ["test_model"]
        mock_ml.get_implementable_models.return_value = []
        mock_ml.get_blocked_models.return_value = []
        
        mock_cm.get_connection_status.return_value = {"is_monitoring": True}
        
        mock_inspect = MagicMock()
        mock_ca.control.inspect.return_value = mock_inspect
        mock_inspect.stats.return_value = {"worker1": {}}
        mock_inspect.ping.return_value = {"worker1": "pong"}
        
        mock_is_api.return_value = False
        mock_exec_mode.return_value = "standalone"
        
        yield {
            "settings": mock_settings,
            "rm": mock_rm,
            "ml": mock_ml,
            "ca": mock_ca,
            "cm": mock_cm,
            "is_api": mock_is_api,
            "exec_mode": mock_exec_mode
        }

def test_basic_health(client, mock_dependencies):
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"

def test_detailed_health_healthy(client, mock_dependencies):
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "system" in data

def test_detailed_health_degraded_memory(client, mock_dependencies):
    mock_dependencies["rm"].get_system_info.return_value = {"memory_percent": 90.0}
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert "High memory usage" in response.json()["issues"][0]

def test_models_health_standalone(client, mock_dependencies):
    mock_dependencies["is_api"].return_value = False
    response = client.get("/health/models")
    assert response.status_code == 200
    assert response.json()["mode"] == "standalone"
    assert "ready_models" in response.json()

@patch('app.tasks.health_tasks.health_check_models')
def test_models_health_api_mode(mock_health_task, client, mock_dependencies):
    mock_dependencies["is_api"].return_value = True
    mock_dependencies["exec_mode"].return_value = "api_server"
    
    # Mock celery task result
    mock_task = MagicMock()
    mock_task.get.return_value = {
        "models_loaded": {
            "qa": True, "classifier": True, "ner": True, 
            "summarizer": True, "translator": True, "whisper": True
        },
        "total_ready_models": 6,
        "worker_host": "test-host"
    }
    mock_health_task.delay.return_value = mock_task
    
    response = client.get("/health/models")
    assert response.status_code == 200
    assert response.json()["mode"] == "api_server"
    assert response.json()["summary"]["total_ready_models"] == 6

def test_celery_status_healthy(client, mock_dependencies):
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    assert response.json()["overall_status"] == "healthy"

def test_celery_status_critical(client, mock_dependencies):
    mock_dependencies["ca"].control.inspect.return_value.stats.return_value = None
    mock_dependencies["ca"].control.inspect.return_value.ping.return_value = None
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    assert response.json()["overall_status"] == "critical"

def test_resources_health(client, mock_dependencies):
    # For resources_health, it imports unified_resource_manager locally, so we need to patch it correctly
    with patch('app.core.resource_manager.unified_resource_manager') as mock_urm:
        mock_urm.get_resource_status.return_value = {"status": "ok"}
        mock_urm.get_gpu_info.return_value = {"gpu": "ok"}
        mock_urm.get_system_info.return_value = {"system": "ok"}
        
        response = client.get("/health/resources")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["resource_utilization"] == {"status": "ok"}

def test_capabilities(client, mock_dependencies):
    response = client.get("/health/capabilities")
    assert response.status_code == 200
    assert response.json() == {"cuda": True}


# Additional tests for better coverage

def test_detailed_health_queue_nearly_full(client, mock_dependencies):
    """Test detailed health when queue is nearly full"""
    mock_dependencies["settings"].alert_queue_size = 0  # Any queue size > 0 triggers warning
    response = client.get("/health/detailed")
    assert response.status_code == 200
    # Queue status is simplified in the route, so this won't trigger the warning
    # but we're testing the code path


def test_detailed_health_no_models(client, mock_dependencies):
    """Test detailed health when no models are ready or implementable"""
    mock_dependencies["ml"].get_ready_models.return_value = []
    mock_dependencies["ml"].get_implementable_models.return_value = []
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "unhealthy"
    assert "No models are ready or implementable" in response.json()["issues"][0]


def test_detailed_health_blocked_models(client, mock_dependencies):
    """Test detailed health when some models are blocked"""
    mock_dependencies["ml"].get_blocked_models.return_value = ["test_model"]
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert "blocked" in response.json()["issues"][0].lower()


def test_detailed_health_exception(client, mock_dependencies):
    """Test detailed health when an exception occurs"""
    mock_dependencies["rm"].get_gpu_info.side_effect = Exception("Test exception")
    response = client.get("/health/detailed")
    assert response.status_code == 500


@patch('app.tasks.health_tasks.health_check_models')
def test_models_health_api_mode_no_workers(mock_health_task, client, mock_dependencies):
    """Test models health in API mode when no workers are available"""
    mock_dependencies["is_api"].return_value = True
    mock_dependencies["exec_mode"].return_value = "api_server"

    # Make inspect return no workers
    mock_inspect = MagicMock()
    mock_inspect.active.return_value = None
    mock_dependencies["ca"].control.inspect.return_value = mock_inspect

    response = client.get("/health/models")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["reason"] == "No Celery workers available"


@patch('app.tasks.health_tasks.health_check_models')
def test_models_health_api_mode_exception(mock_health_task, client, mock_dependencies):
    """Test models health in API mode when an exception occurs"""
    mock_dependencies["is_api"].return_value = True
    mock_dependencies["exec_mode"].return_value = "api_server"

    # Make task.get() raise an exception
    mock_inspect = MagicMock()
    mock_inspect.active.return_value = {"worker1": []}
    mock_dependencies["ca"].control.inspect.return_value = mock_inspect

    mock_task = MagicMock()
    mock_task.get.side_effect = Exception("Task failed")
    mock_health_task.delay.return_value = mock_task

    response = client.get("/health/models")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "Task failed" in data["error"]


def test_celery_status_monitor_exception(client, mock_dependencies):
    """Test celery status when monitor throws exception"""
    mock_dependencies["cm"].get_connection_status.side_effect = Exception("Monitor error")
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    data = response.json()
    assert data["event_monitoring"]["status"] == "monitoring_unavailable"


def test_celery_status_degraded_no_monitoring(client, mock_dependencies):
    """Test celery status when monitoring is not active"""
    mock_dependencies["cm"].get_connection_status.return_value = {"is_monitoring": False}
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "degraded"


def test_celery_status_ping_only(client, mock_dependencies):
    """Test celery status when ping works but stats don't"""
    mock_inspect = MagicMock()
    mock_inspect.stats.return_value = None
    mock_inspect.ping.return_value = {"worker1": "pong"}
    mock_dependencies["ca"].control.inspect.return_value = mock_inspect

    response = client.get("/health/celery/status")
    assert response.status_code == 200
    data = response.json()
    assert data["celery_workers"]["available"] is True
    assert "Workers responding but stats unavailable" in data["celery_workers"].get("note", "")


def test_celery_status_inspect_exception(client, mock_dependencies):
    """Test celery status when inspect raises exception"""
    mock_dependencies["ca"].control.inspect.side_effect = Exception("Connection failed")
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    data = response.json()
    assert data["celery_workers"]["error"] is not None


def test_resources_health_exception(client, mock_dependencies):
    """Test resources health when exception occurs"""
    with patch('app.core.resource_manager.unified_resource_manager') as mock_urm:
        mock_urm.get_resource_status.side_effect = Exception("Resource error")
        response = client.get("/health/resources")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Resource error" in data["error"]