import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.api.health_routes import router 
from app.config.settings import settings
from app.main import app

client = TestClient(app)


# Define mock settings for predictable behavior
def mock_settings():
    settings.app_version = "v1.0.0"
    settings.site_id = "test-site"
    settings.alert_memory_usage = 80.0
    settings.alert_queue_size = 5
    settings.enable_streaming = True
    settings.max_streaming_slots = 2
    settings.max_batch_slots = 1
    settings.streaming_port = 8300

mock_settings()

@pytest.fixture(autouse=True)
def mock_health_dependencies():
    with patch('app.api.health_routes.resource_manager') as mock_rm, \
         patch('app.api.health_routes.request_queue') as mock_rq, \
         patch('app.api.health_routes.model_loader') as mock_ml, \
         patch('app.api.health_routes.celery_app') as mock_ca, \
         patch('app.api.health_routes.celery_monitor') as mock_cm, \
         patch('app.api.health_routes.unified_resource_manager') as mock_urm:
        
        # Default mock values for a "healthy" state
        mock_rm.get_gpu_info.return_value = {"gpu_count": 1, "utilization_percent": 10}
        mock_rm.get_system_info.return_value = {"memory_percent": 50.0}
        
        mock_rq.get_queue_status.return_value = {
            "queue_size": 2, "max_queue_size": 10, "total_requests": 100,
            "completed_requests": 90, "failed_requests": 10
        }
        
        mock_ml.get_model_status.return_value = {
            "translator": {"status": "ready", "dependencies_met": True},
            "whisper": {"status": "ready", "dependencies_met": True},
        }
        mock_ml.get_system_capabilities.return_value = {"cuda": True, "torch": True}
        mock_ml.get_ready_models.return_value = ["translator", "whisper"]
        mock_ml.get_implementable_models.return_value = []
        mock_ml.get_blocked_models.return_value = []
        mock_ml.get_missing_dependencies_summary.return_value = {}

        # Default mock values for Celery monitor
        mock_cm.get_connection_status.return_value = {
            "is_monitoring": True, "thread_alive": True, "active_tasks_count": 0, "workers_seen": 1
        }
        # Default mock values for Celery app
        mock_inspect = MagicMock()
        mock_ca.control.inspect.return_value = mock_inspect
        mock_inspect.stats.return_value = {"worker1": {}}
        mock_inspect.ping.return_value = {"worker1": {"ok": "pong"}}
        
        # Default mock values for unified_resource_manager
        mock_urm.get_resource_status.return_value = {"cpu_utilization": 25.0}
        mock_urm.get_gpu_info.return_value = {"gpu_count": 1}
        mock_urm.get_system_info.return_value = {"memory_percent": 40.0}
        
        yield {
            "rm": mock_rm, "rq": mock_rq, "ml": mock_ml,
            "ca": mock_ca, "cm": mock_cm, "urm": mock_urm
        }


def test_basic_health():
    """Test the basic health check endpoint returns a healthy status."""
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()
    assert response.json()["version"] == "v1.0.0"


def test_detailed_health_healthy_status(mock_health_dependencies):
    """Test detailed health check for a fully healthy system."""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["issues"] == []
    assert response.json()["models"]["ready"] == 2
    assert response.json()["queue"]["queue_size"] == 2

def test_detailed_health_degraded_high_memory(mock_health_dependencies):
    """Test detailed health check with high memory usage causing a degraded status."""
    mock_health_dependencies["rm"].get_system_info.return_value = {"memory_percent": 85.0}
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert "High memory usage" in response.json()["issues"][0]

def test_detailed_health_degraded_queue_full(mock_health_dependencies):
    """Test detailed health check with a nearly full queue causing a degraded status."""
    mock_health_dependencies["rq"].get_queue_status.return_value = {
        "queue_size": 6, "max_queue_size": 10, "total_requests": 100
    }
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert "Queue nearly full" in response.json()["issues"][0]

def test_detailed_health_unhealthy_no_models_ready(mock_health_dependencies):
    """Test detailed health check with no ready models, causing an unhealthy status."""
    mock_health_dependencies["ml"].get_ready_models.return_value = []
    mock_health_dependencies["ml"].get_implementable_models.return_value = []
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "unhealthy"
    assert "No models are ready or implementable" in response.json()["issues"][0]

def test_detailed_health_degraded_blocked_models(mock_health_dependencies):
    """Test detailed health check with blocked models, causing a degraded status."""
    mock_health_dependencies["ml"].get_blocked_models.return_value = ["model_a"]
    response = client.get("/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert "Some models blocked by dependencies" in response.json()["issues"][0]

def test_detailed_health_exception_on_run():
    """Test the detailed health check handles an unexpected exception."""
    with patch('app.api.health_routes.resource_manager.get_system_info', side_effect=Exception("Mock resource error")):
        response = client.get("/health/detailed")
        assert response.status_code == 500
        assert response.json()["detail"] == "Health check failed"


def test_models_health_ready_state(mock_health_dependencies):
    """Test model health endpoint when models are ready."""
    response = client.get("/health/models")
    assert response.status_code == 200
    assert response.json()["summary"]["ready"] == 2
    assert response.json()["ready_models"] == ["translator", "whisper"]

def test_models_health_with_blocked_models(mock_health_dependencies):
    """Test model health endpoint when some models are blocked."""
    mock_health_dependencies["ml"].get_ready_models.return_value = ["translator"]
    mock_health_dependencies["ml"].get_blocked_models.return_value = ["blocked_model"]
    mock_health_dependencies["ml"].get_missing_dependencies_summary.return_value = {"blocked_model": ["dep_A", "dep_B"]}
    response = client.get("/health/models")
    assert response.status_code == 200
    assert response.json()["summary"]["ready"] == 1
    assert response.json()["summary"]["blocked"] == 1
    assert response.json()["blocked_models"] == ["blocked_model"]
    assert "missing_dependencies" in response.json()


def test_system_capabilities_check(mock_health_dependencies):
    """Test system capabilities endpoint."""
    response = client.get("/health/capabilities")
    assert response.status_code == 200
    assert response.json()["cuda"] is True


def test_celery_status_healthy(mock_health_dependencies):
    """Test Celery status when workers and monitoring are healthy."""
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    assert response.json()["overall_status"] == "healthy"
    assert response.json()["issues"] == []
    assert response.json()["celery_workers"]["available"] is True
    assert response.json()["event_monitoring"]["is_monitoring"] is True

def test_celery_status_critical_no_workers(mock_health_dependencies):
    """Test Celery status when no workers are available."""
    mock_health_dependencies["ca"].control.inspect.return_value.stats.return_value = None
    mock_health_dependencies["ca"].control.inspect.return_value.ping.return_value = None
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    assert response.json()["overall_status"] == "critical"
    assert "No Celery workers responding" in response.json()["issues"]
    assert response.json()["celery_workers"]["available"] is False

def test_celery_status_degraded_no_monitoring(mock_health_dependencies):
    """Test Celery status when workers are available but monitoring is not connected."""
    mock_health_dependencies["cm"].get_connection_status.return_value = {
        "is_monitoring": False, "thread_alive": False, "active_tasks_count": 0, "workers_seen": 1
    }
    response = client.get("/health/celery/status")
    assert response.status_code == 200
    assert response.json()["overall_status"] == "degraded"
    assert "Event monitoring not connected (worker busy or starting up)" in response.json()["issues"]


def test_resources_health_healthy(mock_health_dependencies):
    """Test resources health endpoint with a healthy status."""
    response = client.get("/health/resources")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "resource_utilization" in response.json()
    assert "gpu_info" in response.json()
    assert response.json()["streaming_enabled"] is True
    


def test_resources_health_exception_on_run():
    """Test the resources health check handles an unexpected exception."""
    
    # Create a mock object that will raise an exception
    mock_urm = MagicMock()
    mock_urm.get_resource_status.side_effect = Exception("Mock resource manager error")
    
    # Patch the unified_resource_manager in its home module
    with patch('app.core.resource_manager.unified_resource_manager', new=mock_urm):
        response = client.get("/health/resources")
        
        # The endpoint should return a 200 OK with an error status in the body
        assert response.status_code == 200
        
        response_json = response.json()
        assert response_json["status"] == "error"
        assert "Mock resource manager error" in response_json["error"]

