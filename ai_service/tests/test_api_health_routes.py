# tests/test_api_health_routes.py
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_app():
    """Create a test FastAPI app with health routes"""
    from app.api.health_routes import router
    
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(mock_app):
    """Create test client"""
    return TestClient(mock_app)

@pytest.fixture
def mock_settings():
    """Mock settings for health checks"""
    with patch('app.api.health_routes.settings') as mock:
        mock.app_version = "1.0.0"
        mock.site_id = "test-site-001"
        mock.alert_memory_usage = 85.0
        mock.alert_queue_size = 90
        yield mock

@pytest.fixture
def mock_resource_manager():
    """Mock resource manager"""
    with patch('app.api.health_routes.resource_manager') as mock:
        mock.get_gpu_info.return_value = {
            "cuda_available": True,
            "device_count": 2,
            "devices": [
                {"name": "Tesla V100", "memory_total": 16384, "memory_free": 14000},
                {"name": "Tesla V100", "memory_total": 16384, "memory_free": 15000}
            ]
        }
        mock.get_system_info.return_value = {
            "cpu_percent": 25.5,
            "memory_percent": 45.2,
            "memory_available": 8192,
            "disk_usage": 65.0,
            "uptime": 86400
        }
        yield mock

@pytest.fixture
def mock_model_loader():
    """Mock model loader"""
    with patch('app.api.health_routes.model_loader') as mock:
        mock.get_model_status.return_value = {
            "whisper_model": {"loaded": True, "status": "ready"},
            "classifier_model": {"loaded": True, "status": "ready"},
            "ner_model": {"loaded": False, "status": "implementable"}
        }
        mock.get_system_capabilities.return_value = {
            "torch_available": True,
            "transformers_available": True,
            "cuda_available": True,
            "spacy_available": True
        }
        mock.get_ready_models.return_value = ["whisper_model", "classifier_model"]
        mock.get_implementable_models.return_value = ["ner_model"]
        mock.get_blocked_models.return_value = []
        mock.get_missing_dependencies_summary.return_value = {}
        yield mock

class TestBasicHealthEndpoint:
    """Test the basic health endpoint"""

    def test_basic_health_success(self, client, mock_settings):
        """Test successful basic health check"""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["site_id"] == "test-site-001"
        assert "timestamp" in data
        
        # Verify timestamp format
        datetime.fromisoformat(data["timestamp"])

    def test_basic_health_response_structure(self, client, mock_settings):
        """Test that basic health response has correct structure"""
        response = client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["status", "timestamp", "version", "site_id"]
        for field in required_fields:
            assert field in data

    def test_basic_health_multiple_calls(self, client, mock_settings):
        """Test multiple calls to basic health endpoint"""
        # Make multiple calls
        responses = [client.get("/health/") for _ in range(3)]
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
        
        # Timestamps should be different (or close)
        timestamps = [r.json()["timestamp"] for r in responses]
        assert len(set(timestamps)) >= 1  # At least one unique timestamp


class TestDetailedHealthEndpoint:
    """Test the detailed health endpoint"""

    def test_detailed_health_success_healthy(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health check with healthy system"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert len(data["issues"]) == 0
        
        # Check all required sections
        assert "system" in data
        assert "gpu" in data
        assert "queue" in data
        assert "models" in data
        assert "capabilities" in data

    def test_detailed_health_high_memory_usage(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health with high memory usage"""
        # Mock high memory usage
        mock_resource_manager.get_system_info.return_value = {
            "cpu_percent": 25.5,
            "memory_percent": 90.0,  # Above alert threshold
            "memory_available": 1024,
            "disk_usage": 65.0,
            "uptime": 86400
        }
        
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert len(data["issues"]) == 1
        assert "High memory usage" in data["issues"][0]

    def test_detailed_health_no_ready_models(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health with no ready models"""
        mock_model_loader.get_ready_models.return_value = []
        mock_model_loader.get_implementable_models.return_value = []
        
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "unhealthy"
        assert any("No models are ready" in issue for issue in data["issues"])

    def test_detailed_health_blocked_models(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health with blocked models"""
        mock_model_loader.get_blocked_models.return_value = ["qa_model", "summarizer_model"]
        
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert any("models blocked by dependencies" in issue for issue in data["issues"])

    def test_detailed_health_models_section(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health models section structure"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        models = data["models"]
        assert "total" in models
        assert "ready" in models
        assert "implementable" in models
        assert "blocked" in models
        assert "ready_models" in models
        assert "implementable_models" in models
        assert "blocked_models" in models
        assert "details" in models
        
        # Verify model counts
        assert models["ready"] == 2
        assert models["implementable"] == 1
        assert models["blocked"] == 0

    def test_detailed_health_gpu_section(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health GPU section"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        gpu = data["gpu"]
        assert gpu["cuda_available"] is True
        assert gpu["device_count"] == 2
        assert len(gpu["devices"]) == 2

    def test_detailed_health_system_section(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test detailed health system section"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        system = data["system"]
        assert "cpu_percent" in system
        assert "memory_percent" in system
        assert "memory_available" in system
        assert "disk_usage" in system
        assert "uptime" in system

    def test_detailed_health_exception_handling(self, client, mock_settings):
        """Test detailed health endpoint exception handling"""
        with patch('app.api.health_routes.resource_manager') as mock_rm:
            mock_rm.get_gpu_info.side_effect = Exception("GPU info failed")
            
            response = client.get("/health/detailed")
            
            assert response.status_code == 500
            assert "Health check failed" in response.json()["detail"]


class TestModelsHealthEndpoint:
    """Test the models health endpoint"""

    def test_models_health_success(self, client, mock_model_loader):
        """Test successful models health check"""
        response = client.get("/health/models")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "models" in data
        assert "capabilities" in data
        assert "ready" in data
        assert "implementable" in data
        assert "blocked" in data
        assert "missing_dependencies" in data

    def test_models_health_response_structure(self, client, mock_model_loader):
        """Test models health response structure"""
        response = client.get("/health/models")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check model lists
        assert isinstance(data["ready"], list)
        assert isinstance(data["implementable"], list)
        assert isinstance(data["blocked"], list)
        
        # Check capabilities
        capabilities = data["capabilities"]
        assert "torch_available" in capabilities
        assert "transformers_available" in capabilities
        assert "cuda_available" in capabilities

    def test_models_health_with_missing_dependencies(self, client, mock_model_loader):
        """Test models health with missing dependencies"""
        mock_model_loader.get_missing_dependencies_summary.return_value = {
            "pytorch": {"required": "1.9.0", "installed": "1.8.0"},
            "transformers": {"required": "4.0.0", "installed": None}
        }
        
        response = client.get("/health/models")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["missing_dependencies"]) == 2
        assert "pytorch" in data["missing_dependencies"]
        assert "transformers" in data["missing_dependencies"]

    def test_models_health_no_capabilities(self, client, mock_model_loader):
        """Test models health with no system capabilities"""
        mock_model_loader.get_system_capabilities.return_value = {
            "torch_available": False,
            "transformers_available": False,
            "cuda_available": False,
            "spacy_available": False
        }
        
        response = client.get("/health/models")
        
        assert response.status_code == 200
        data = response.json()
        
        capabilities = data["capabilities"]
        assert not any(capabilities.values())  # All should be False


class TestCeleryHealthEndpoint:
    """Test the Celery health endpoint"""

    @patch('app.api.health_routes.celery_monitor')
    def test_celery_health_success(self, mock_monitor, client):
        """Test successful Celery health check"""
        mock_monitor.get_celery_status.return_value = {
            "broker_connected": True,
            "active_workers": 3,
            "active_tasks": 5,
            "queue_size": 2,
            "worker_stats": {
                "worker1": {"status": "online", "processed": 150},
                "worker2": {"status": "online", "processed": 200}
            }
        }
        
        response = client.get("/health/celery")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["broker_connected"] is True
        assert data["active_workers"] == 3
        assert data["active_tasks"] == 5

    @patch('app.api.health_routes.celery_monitor')
    def test_celery_health_broker_disconnected(self, mock_monitor, client):
        """Test Celery health with broker disconnected"""
        mock_monitor.get_celery_status.return_value = {
            "broker_connected": False,
            "active_workers": 0,
            "active_tasks": 0,
            "queue_size": 0,
            "worker_stats": {}
        }
        
        response = client.get("/health/celery")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["broker_connected"] is False
        assert data["active_workers"] == 0

    @patch('app.api.health_routes.celery_monitor')
    def test_celery_health_exception(self, mock_monitor, client):
        """Test Celery health endpoint exception handling"""
        mock_monitor.get_celery_status.side_effect = Exception("Celery connection failed")
        
        response = client.get("/health/celery")
        
        # Should handle gracefully
        assert response.status_code in [200, 500]


class TestStreamingHealthEndpoint:
    """Test the streaming health endpoint"""

    @patch('app.api.health_routes.unified_resource_manager')
    def test_streaming_health_success(self, mock_urm, client):
        """Test successful streaming health check"""
        mock_urm.get_resource_status.return_value = {
            "streaming": {
                "total_slots": 4,
                "available_slots": 2,
                "utilization_pct": 50.0,
                "total_processed": 100
            },
            "batch": {
                "total_slots": 2,
                "available_slots": 1,
                "utilization_pct": 50.0,
                "total_processed": 25
            }
        }
        
        response = client.get("/health/streaming")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "streaming" in data
        assert "batch" in data
        assert data["streaming"]["utilization_pct"] == 50.0
        assert data["batch"]["available_slots"] == 1

    @patch('app.api.health_routes.unified_resource_manager')
    def test_streaming_health_high_utilization(self, mock_urm, client):
        """Test streaming health with high utilization"""
        mock_urm.get_resource_status.return_value = {
            "streaming": {
                "total_slots": 4,
                "available_slots": 0,
                "utilization_pct": 100.0,
                "total_processed": 500
            },
            "batch": {
                "total_slots": 2,
                "available_slots": 0,
                "utilization_pct": 100.0,
                "total_processed": 100
            }
        }
        
        response = client.get("/health/streaming")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["streaming"]["utilization_pct"] == 100.0
        assert data["batch"]["available_slots"] == 0


class TestHealthRouteIntegration:
    """Test health route integration and cross-endpoint functionality"""

    def test_health_endpoint_consistency(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test consistency across different health endpoints"""
        basic_response = client.get("/health/")
        detailed_response = client.get("/health/detailed")
        models_response = client.get("/health/models")
        
        # All should succeed
        assert basic_response.status_code == 200
        assert detailed_response.status_code == 200
        assert models_response.status_code == 200
        
        # Version should be consistent
        basic_data = basic_response.json()
        detailed_data = detailed_response.json()
        
        assert basic_data["version"] == detailed_data["version"]
        assert basic_data["site_id"] == detailed_data["site_id"]

    def test_health_route_performance(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test health route response times"""
        import time
        
        start_time = time.time()
        response = client.get("/health/detailed")
        end_time = time.time()
        
        assert response.status_code == 200
        # Health check should be fast (under 1 second)
        assert (end_time - start_time) < 1.0

    def test_health_route_concurrent_access(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test concurrent access to health endpoints"""
        import threading
        
        results = []
        
        def check_health():
            response = client.get("/health/detailed")
            results.append(response.status_code)
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=check_health)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5


class TestHealthRouteConfiguration:
    """Test health route configuration"""

    def test_router_configuration(self):
        """Test router is properly configured"""
        from app.api.health_routes import router
        
        assert router.prefix == "/health"
        assert "health" in router.tags

    def test_logging_configuration(self, client, mock_settings, mock_resource_manager, mock_model_loader):
        """Test that health endpoints log appropriately"""
        with patch('app.api.health_routes.logger') as mock_logger:
            # Trigger an error to test error logging
            mock_resource_manager.get_gpu_info.side_effect = Exception("Test error")
            
            response = client.get("/health/detailed")
            
            assert response.status_code == 500
            mock_logger.error.assert_called()

    def test_settings_integration(self, client):
        """Test integration with settings"""
        with patch('app.api.health_routes.settings') as mock_settings:
            mock_settings.app_version = "2.0.0"
            mock_settings.site_id = "prod-site-123"
            
            response = client.get("/health/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["version"] == "2.0.0"
            assert data["site_id"] == "prod-site-123"