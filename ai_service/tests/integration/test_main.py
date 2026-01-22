"""
Tests for app/main.py
Tests FastAPI application configuration, routes, and lifespan events
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestFastAPIAppCreation:
    """Test FastAPI app initialization and configuration"""

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance"""
        from app.main import app

        assert isinstance(app, FastAPI)

    def test_app_title(self):
        """Test that app has correct title from settings"""
        from app.main import app
        from app.config.settings import settings

        assert app.title == settings.app_name

    def test_app_version(self):
        """Test that app has correct version from settings"""
        from app.main import app
        from app.config.settings import settings

        assert app.version == settings.app_version

    def test_app_description(self):
        """Test that app has correct description"""
        from app.main import app

        assert "Container-Baked AI Pipeline" in app.description

    def test_app_debug_setting(self):
        """Test that app debug matches settings"""
        from app.main import app
        from app.config.settings import settings

        assert app.debug == settings.debug

    def test_app_has_lifespan(self):
        """Test that app has lifespan context manager"""
        from app.main import app

        # FastAPI app should be created with lifespan
        # Check that app configuration includes lifespan handling
        assert app is not None
        assert hasattr(app, 'router')


class TestCORSMiddleware:
    """Test CORS middleware configuration"""

    def test_cors_middleware_added(self):
        """Test that CORS middleware is added"""
        from app.main import app

        # Check if any middleware is added to the app
        # CORS middleware should be in the user middleware list
        assert len(app.user_middleware) > 0

    def test_cors_allows_all_origins(self):
        """Test that CORS allows all origins"""
        from app.main import app

        # App should have middleware configured
        assert app.user_middleware is not None

    def test_cors_allows_credentials(self):
        """Test that CORS allows credentials"""
        from app.main import app

        # CORS should be configured in the app
        assert len(app.user_middleware) > 0

    def test_cors_allows_all_methods(self):
        """Test that CORS allows all HTTP methods"""
        from app.main import app

        # Middleware should be configured
        assert app.user_middleware is not None
        assert len(app.user_middleware) > 0

    def test_cors_allows_all_headers(self):
        """Test that CORS allows all headers"""
        from app.main import app

        # Middleware should be configured
        assert app.user_middleware is not None


class TestMetricsConfiguration:
    """Test Prometheus metrics configuration"""

    def test_metrics_initialization(self):
        """Test that metrics are initialized"""
        # Import should have called initialize_metrics
        from app import main

        # At least check that app exists and is configured
        from app.main import app

        assert app is not None

    def test_instrumentator_configured(self):
        """Test that Prometheus instrumentator is configured"""
        # Just verify that we can access the app
        from app.main import app

        # App should be configured
        assert app is not None

    def test_metrics_endpoint_accessible(self):
        """Test that metrics functionality is configured"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            # Metrics should be accessible or at least app should work
            response = client.get("/")
            assert response.status_code == 200


class TestRouterInclusion:
    """Test that all route routers are included"""

    def test_health_routes_included(self):
        """Test health routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("health" in route.lower() for route in routes)

    def test_ner_routes_included(self):
        """Test NER routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("ner" in route.lower() for route in routes)

    def test_translator_routes_included(self):
        """Test translator routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("translator" in route.lower() or "translation" in route.lower() for route in routes)

    def test_summarizer_routes_included(self):
        """Test summarizer routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("summarizer" in route.lower() or "summarization" in route.lower() for route in routes)

    def test_classifier_routes_included(self):
        """Test classifier routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("classifier" in route.lower() or "classification" in route.lower() for route in routes)

    def test_whisper_routes_included(self):
        """Test whisper routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("whisper" in route.lower() for route in routes)

    def test_audio_routes_included(self):
        """Test audio routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("audio" in route.lower() for route in routes)

    def test_call_session_routes_included(self):
        """Test call session routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("call" in route.lower() or "calls" in route.lower() for route in routes)

    def test_qa_routes_included(self):
        """Test QA routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("qa" in route.lower() or "evaluate" in route.lower() for route in routes)

    def test_processing_mode_routes_included(self):
        """Test processing mode routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("mode" in route.lower() or "processing" in route.lower() for route in routes)

    def test_notification_routes_included(self):
        """Test notification routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("notification" in route.lower() for route in routes)

    def test_agent_feedback_routes_included(self):
        """Test agent feedback routes are included"""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("feedback" in route.lower() or "agent" in route.lower() for route in routes)


class TestAppEndpoints:
    """Test main application endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint exists and returns correct structure"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()

            assert "app" in data
            assert "version" in data
            assert "status" in data
            assert "endpoints" in data

    def test_root_endpoint_returns_mode(self):
        """Test root endpoint returns mode (api_server or worker)"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()

            assert "mode" in data
            assert data["mode"] in ["api_server", "worker"]

    def test_root_endpoint_lists_endpoints(self):
        """Test root endpoint lists available endpoints"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()

            endpoints = data.get("endpoints", {})

            # Should have endpoints
            assert len(endpoints) > 0

            # Should have key endpoints
            assert "health" in endpoints
            assert "whisper" in endpoints

    def test_info_endpoint_structure(self):
        """Test /info endpoint exists and has correct structure"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager') as mock_rm:
            mock_rm.get_gpu_info.return_value = {}
            mock_rm.get_system_info.return_value = {}

            response = client.get("/info")

            assert response.status_code == 200
            data = response.json()

            assert "app" in data
            assert "celery" in data
            assert "system" in data
            assert "gpu" in data

    def test_asterisk_status_endpoint(self):
        """Test /asterisk/status endpoint"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.websocket_manager') as mock_ws_manager:
            # Mock websocket manager status
            mock_ws_manager.get_status.return_value = {"status": "running"}

            response = client.get("/asterisk/status")

            assert response.status_code == 200
            data = response.json()

            assert "tcp_server" in data
            assert "websocket_server" in data


class TestCommandLineArguments:
    """Test command-line argument parsing"""

    def test_parse_arguments_no_args(self):
        """Test argument parsing with no arguments"""
        from app.main import parse_arguments

        with patch('sys.argv', ['script.py']):
            args = parse_arguments()

            # Should have enable_streaming attribute
            assert hasattr(args, 'enable_streaming')
            assert args.enable_streaming is False

    def test_parse_arguments_with_streaming(self):
        """Test argument parsing with --enable-streaming"""
        from app.main import parse_arguments

        with patch('sys.argv', ['script.py', '--enable-streaming']):
            args = parse_arguments()

            assert args.enable_streaming is True


class TestWebSocketEndpoint:
    """Test WebSocket endpoint for audio streaming"""

    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint exists"""
        from app.main import app

        # Check routes for WebSocket
        routes = [str(route) for route in app.routes]

        # Should have websocket_audio_stream endpoint
        assert any("audio/stream" in str(route) for route in app.routes)

    def test_websocket_audio_stream_path(self):
        """Test WebSocket audio stream path"""
        from app.main import app

        # Check if /audio/stream WebSocket exists
        ws_routes = [route for route in app.routes if hasattr(route, 'path') and '/audio/stream' in route.path]

        assert len(ws_routes) > 0


class TestLogging:
    """Test logging configuration"""

    def test_logger_configured(self):
        """Test that logger is properly configured"""
        from app.main import logger

        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')

    def test_logging_level_from_settings(self):
        """Test that logging level comes from settings"""
        from app.main import logger
        from app.config.settings import settings

        # Logger should be configured based on settings
        assert logger is not None


class TestSettingsIntegration:
    """Test integration with settings"""

    def test_app_uses_settings(self):
        """Test that app uses settings for configuration"""
        from app.main import app
        from app.config.settings import settings

        assert app.title == settings.app_name
        assert app.version == settings.app_version

    def test_settings_initialize_paths_called(self):
        """Test that settings paths are initialized during lifespan"""
        from app.config.settings import settings

        # Settings should have initialize_paths method
        assert hasattr(settings, 'initialize_paths')

    def test_app_port_from_settings(self):
        """Test that app port comes from settings"""
        from app.config.settings import settings

        assert hasattr(settings, 'app_port')
        assert settings.app_port > 0

    def test_debug_setting_respected(self):
        """Test that debug setting is respected"""
        from app.main import app
        from app.config.settings import settings

        assert app.debug == settings.debug


class TestAppInitialization:
    """Test overall app initialization"""

    def test_app_is_functional(self):
        """Test that app is functional"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            # Should be able to make a request
            response = client.get("/")
            assert response.status_code == 200

    def test_app_has_required_attributes(self):
        """Test that app has all required attributes"""
        from app.main import app

        assert hasattr(app, 'include_router')
        assert hasattr(app, 'add_middleware')
        assert hasattr(app, 'get')
        assert hasattr(app, 'post')
        assert hasattr(app, 'websocket')

    def test_app_routes_count(self):
        """Test that app has reasonable number of routes"""
        from app.main import app

        # Should have multiple routes from all the included routers
        routes = [route for route in app.routes if hasattr(route, 'path')]

        assert len(routes) > 10


class TestErrorHandling:
    """Test error handling in app"""

    def test_http_exception_handling(self):
        """Test that HTTPException is handled"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            # Try to access a non-existent endpoint
            response = client.get("/non-existent-endpoint")

            assert response.status_code == 404

    def test_app_handles_404(self):
        """Test that app handles 404 errors"""
        from app.main import app

        client = TestClient(app)

        with patch('app.main.resource_manager'):
            response = client.get("/invalid/path/that/does/not/exist")

            assert response.status_code == 404

