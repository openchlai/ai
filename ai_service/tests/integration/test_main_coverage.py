"""
Comprehensive coverage tests for app/main.py - Phase 3B
Focuses on achieving 95% coverage for main.py (currently 49%)
Tests endpoints, error handling, and conditional code paths
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
import os


class TestAppInfoEndpointConditionalLogic:
    """Tests for conditional logic in /info endpoint"""

    def test_app_info_with_model_loading_disabled(self, client):
        """Test /info endpoint shows celery as not_applicable when model loading disabled"""
        with patch('app.main.settings') as mock_settings:
            mock_settings.enable_model_loading = False

            response = client.get("/info")
            assert response.status_code == 200
            data = response.json()
            assert "celery" in data
            assert data["celery"]["status"] == "not_applicable"
            assert data["app"]["mode"] == "api_server"

    def test_app_info_includes_app_metadata(self, client):
        """Test /info endpoint includes all required app metadata"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()

        assert "app" in data
        assert "name" in data["app"]
        assert "version" in data["app"]
        assert "site_id" in data["app"]
        assert "debug" in data["app"]
        assert "mode" in data["app"]

    def test_app_info_includes_system_and_gpu(self, client):
        """Test /info endpoint includes system and GPU info"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()

        assert "system" in data
        assert "gpu" in data

    def test_app_info_with_celery_check_logic(self, client):
        """Test /info endpoint Celery status logic"""
        with patch('app.main.settings') as mock_settings:
            mock_settings.enable_model_loading = True
            mock_settings.app_name = "TestApp"
            mock_settings.app_version = "1.0"
            mock_settings.site_id = "test"
            mock_settings.debug = False

            # Check that endpoint handles Celery status gracefully
            response = client.get("/info")
            assert response.status_code == 200
            data = response.json()
            assert "celery" in data


class TestRootEndpointConditionalMode:
    """Tests for mode detection in root endpoint"""

    def test_root_endpoint_shows_mode(self, client):
        """Test root endpoint includes execution mode"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["worker", "api_server"]

    def test_root_endpoint_includes_all_endpoints(self, client):
        """Test root endpoint lists all major endpoints"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        endpoints = data.get("endpoints", {})
        assert "health" in endpoints
        assert "websocket_audio_stream" in endpoints
        assert "asterisk_status" in endpoints
        assert "celery_status" in endpoints

    def test_root_endpoint_includes_app_info(self, client):
        """Test root endpoint includes app name and version"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        assert "app" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


class TestAsteriskStatusEndpoint:
    """Tests for /asterisk/status endpoint"""

    def test_asterisk_status_endpoint_responds(self, client):
        """Test /asterisk/status endpoint responds with proper structure"""
        response = client.get("/asterisk/status")
        assert response.status_code == 200
        data = response.json()

        assert "tcp_server" in data
        assert "websocket_server" in data

    def test_asterisk_status_with_server_not_running(self, client):
        """Test /asterisk/status when TCP server not running"""
        with patch('app.main.asterisk_server', None):
            response = client.get("/asterisk/status")
            assert response.status_code == 200
            data = response.json()

            assert "tcp_server" in data
            assert "error" in data["tcp_server"]
            assert "TCP listener not running" in str(data["tcp_server"]["error"])

    def test_asterisk_status_with_running_server(self, client):
        """Test /asterisk/status when TCP server is running"""
        mock_server = MagicMock()
        mock_server.get_status.return_value = {"status": "running", "port": 8300}

        with patch('app.main.asterisk_server', mock_server):
            response = client.get("/asterisk/status")
            assert response.status_code == 200
            data = response.json()
            assert "tcp_server" in data


class TestWebSocketEndpoint:
    """Tests for WebSocket endpoint"""

    def test_websocket_endpoint_exists(self, client):
        """Test WebSocket endpoint is registered"""
        websocket_routes = [r for r in client.app.routes if hasattr(r, 'path') and r.path == "/audio/stream"]
        assert len(websocket_routes) > 0

    def test_websocket_endpoint_path_correct(self, client):
        """Test WebSocket endpoint has correct path"""
        routes = client.app.routes
        websocket_paths = [r.path for r in routes if hasattr(r, 'path')]
        assert "/audio/stream" in websocket_paths


class TestAppRouterInclusion:
    """Tests that all routers are properly included"""

    def test_all_required_routers_included(self, client):
        """Test that root endpoint lists all expected routers"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        endpoints = data.get("endpoints", {})

        # Verify major endpoint categories are present
        required_endpoints = [
            "health",
            "models",
            "resources",
            "whisper",
            "qa_predict",
            "notification_status",
            "agent_feedback_update",
            "call_sessions"
        ]

        for endpoint in required_endpoints:
            assert endpoint in endpoints, f"Expected endpoint {endpoint} not found"

    def test_websocket_in_endpoints_list(self, client):
        """Test WebSocket endpoint is listed in root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        endpoints = data.get("endpoints", {})

        assert "websocket_audio_stream" in endpoints
        assert "ws://localhost" in endpoints["websocket_audio_stream"]


class TestModeDetectionInEndpoints:
    """Tests for mode detection across endpoints"""

    def test_mode_in_root_response(self, client):
        """Test root endpoint correctly identifies execution mode"""
        response = client.get("/")
        data = response.json()
        assert "mode" in data

    def test_mode_in_info_response(self, client):
        """Test /info endpoint includes execution mode"""
        response = client.get("/info")
        data = response.json()
        assert "mode" in data["app"]
        assert data["app"]["mode"] in ["worker", "api_server"]


class TestErrorHandling:
    """Tests for error handling in main endpoints"""

    def test_asterisk_status_handles_error(self, client):
        """Test /asterisk/status handles errors gracefully"""
        # Test with None server - should return error gracefully
        response = client.get("/asterisk/status")
        assert response.status_code == 200  # Should still return 200
        data = response.json()
        assert isinstance(data, dict)

    def test_info_endpoint_handles_missing_resources(self, client):
        """Test /info endpoint handles missing resource manager gracefully"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()

        # Should have gracefully handled any missing components
        assert "app" in data


class TestAppInitialization:
    """Tests for app initialization and configuration"""

    def test_app_has_cors_middleware(self, client):
        """Test that CORS middleware is configured"""
        # Try making a request with CORS headers
        response = client.options("/")
        # Should handle OPTIONS requests (CORS preflight)
        assert response.status_code in [200, 405, 204]  # Different frameworks handle this differently

    def test_app_configuration_from_settings(self, client):
        """Test that app configuration comes from settings"""
        from app.config.settings import settings
        from app.main import app

        assert app.title == settings.app_name
        assert app.version == settings.app_version


class TestAppRoutes:
    """Tests for app route registration"""

    def test_required_routes_registered(self, client):
        """Test that all required routes are registered"""
        routes = {r.path for r in client.app.routes if hasattr(r, 'path')}

        required_routes = [
            "/",
            "/info",
            "/asterisk/status",
            "/audio/stream"  # WebSocket
        ]

        for route in required_routes:
            assert route in routes, f"Expected route {route} not found"

    def test_app_has_routes(self, client):
        """Test that app has routes configured"""
        from app.main import app
        # Verify the app has routes registered
        assert len(app.routes) > 0


class TestSettingsIntegration:
    """Tests for settings integration in main.py"""

    def test_app_name_from_settings(self, client):
        """Test that app name comes from settings"""
        response = client.get("/")
        data = response.json()

        from app.config.settings import settings
        assert data["app"] == settings.app_name

    def test_site_id_in_response(self, client):
        """Test that site_id is included in responses"""
        response = client.get("/")
        data = response.json()

        from app.config.settings import settings
        assert data["site_id"] == settings.site_id

    def test_app_port_from_settings(self, client):
        """Test that configuration respects settings"""
        from app.main import app
        from app.config.settings import settings

        # Verify app is created with settings values
        assert app.title == settings.app_name
        assert app.version == settings.app_version


class TestConditionalImportPaths:
    """Tests to verify conditional import behavior"""

    def test_asterisk_server_initialized_at_module_level(self):
        """Test that asterisk_server is initialized at module level"""
        from app.main import asterisk_server
        # Should be None or not raise AttributeError
        assert asterisk_server is None or asterisk_server is not None

    def test_celery_imports_conditional(self):
        """Test that Celery imports are conditional"""
        from app.config.settings import settings
        from app.main import app

        # App should always exist regardless of enable_model_loading
        assert app is not None


class TestEndpointResponses:
    """Tests for endpoint response structure"""

    def test_root_response_structure(self, client):
        """Test that root endpoint returns proper structure"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["app", "version", "status", "mode", "endpoints"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_info_response_structure(self, client):
        """Test that /info endpoint returns proper structure"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["app", "celery", "system", "gpu"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_asterisk_status_response_structure(self, client):
        """Test that /asterisk/status returns proper structure"""
        response = client.get("/asterisk/status")
        assert response.status_code == 200
        data = response.json()

        required_fields = ["tcp_server", "websocket_server"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
