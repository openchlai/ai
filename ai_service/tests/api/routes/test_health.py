
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