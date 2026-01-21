"""
Comprehensive tests for health_tasks to achieve 100% coverage.
"""
import pytest
import socket
from unittest.mock import MagicMock, patch

from app.tasks.health_tasks import health_check_models


class TestHealthCheckModels:
    """Tests for health_check_models task"""

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_all_models_ready(self, mock_hostname, mock_loader):
        """Test health check when all models are ready"""
        mock_hostname.return_value = "test-worker-1"
        mock_loader.get_ready_models.return_value = [
            "qa", "classifier_model", "ner", "summarizer", "translator", "whisper"
        ]

        result = health_check_models()

        assert result['status'] == 'healthy'
        assert result['worker_host'] == "test-worker-1"
        assert result['models_loaded']['qa'] is True
        assert result['models_loaded']['classifier'] is True
        assert result['models_loaded']['ner'] is True
        assert result['models_loaded']['summarizer'] is True
        assert result['models_loaded']['translator'] is True
        assert result['models_loaded']['whisper'] is True
        assert result['total_ready_models'] == 6
        assert result['ready_models'] == [
            "qa", "classifier_model", "ner", "summarizer", "translator", "whisper"
        ]

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_some_models_missing(self, mock_hostname, mock_loader):
        """Test health check when some models are not ready"""
        mock_hostname.return_value = "test-worker-2"
        mock_loader.get_ready_models.return_value = ["qa", "whisper"]

        result = health_check_models()

        assert result['status'] == 'healthy'
        assert result['worker_host'] == "test-worker-2"
        assert result['models_loaded']['qa'] is True
        assert result['models_loaded']['classifier'] is False
        assert result['models_loaded']['ner'] is False
        assert result['models_loaded']['summarizer'] is False
        assert result['models_loaded']['translator'] is False
        assert result['models_loaded']['whisper'] is True
        assert result['total_ready_models'] == 2

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_no_models_ready(self, mock_hostname, mock_loader):
        """Test health check when no models are ready"""
        mock_hostname.return_value = "test-worker-3"
        mock_loader.get_ready_models.return_value = []

        result = health_check_models()

        assert result['status'] == 'healthy'
        assert result['worker_host'] == "test-worker-3"
        assert all(v is False for v in result['models_loaded'].values())
        assert result['total_ready_models'] == 0
        assert result['ready_models'] == []

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_exception_handling(self, mock_hostname, mock_loader):
        """Test health check when model loader raises exception"""
        mock_hostname.return_value = "test-worker-4"
        mock_loader.get_ready_models.side_effect = Exception("Model loader error")

        result = health_check_models()

        assert result['status'] == 'error'
        assert result['worker_host'] == "test-worker-4"
        assert 'error' in result
        assert result['error'] == "Model loader error"
        assert all(v is False for v in result['models_loaded'].values())
        assert result['total_ready_models'] == 0
        assert result['ready_models'] == []

    @patch('socket.gethostname')
    def test_health_check_import_error(self, mock_hostname):
        """Test health check when import fails"""
        mock_hostname.return_value = "test-worker-5"

        # Simulate import error by raising during model loader access
        # Patch the model_loader to raise an exception when accessed
        with patch('app.model_scripts.model_loader.model_loader') as mock_loader:
            mock_loader.get_ready_models.side_effect = RuntimeError("Import failed")
            result = health_check_models()

            assert result['status'] == 'error'
            assert result['worker_host'] == "test-worker-5"
            assert 'error' in result
            assert all(v is False for v in result['models_loaded'].values())

    @patch('app.model_scripts.model_loader.model_loader')
    def test_health_check_returns_dict(self, mock_loader):
        """Test that health check always returns a dictionary"""
        mock_loader.get_ready_models.return_value = ["qa"]

        result = health_check_models()

        assert isinstance(result, dict)
        assert 'status' in result
        assert 'worker_host' in result
        assert 'models_loaded' in result
        assert 'ready_models' in result
        assert 'total_ready_models' in result

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_hostname_included(self, mock_hostname, mock_loader):
        """Test that worker hostname is properly included in response"""
        expected_hostname = "production-worker-42"
        mock_hostname.return_value = expected_hostname
        mock_loader.get_ready_models.return_value = []

        result = health_check_models()

        assert result['worker_host'] == expected_hostname

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_classifier_alias(self, mock_hostname, mock_loader):
        """Test that classifier_model is properly aliased to classifier"""
        mock_hostname.return_value = "test-worker"
        mock_loader.get_ready_models.return_value = ["classifier_model"]

        result = health_check_models()

        # The response should check for 'classifier_model' in ready models
        # and map it to 'classifier' key in models_loaded
        assert result['models_loaded']['classifier'] is True
        assert 'classifier_model' in result['ready_models']

    @patch('app.model_scripts.model_loader.model_loader')
    @patch('socket.gethostname')
    def test_health_check_complete_response_structure(self, mock_hostname, mock_loader):
        """Test complete response structure matches specification"""
        mock_hostname.return_value = "test-worker"
        mock_loader.get_ready_models.return_value = ["qa", "whisper"]

        result = health_check_models()

        # Verify all required keys exist
        required_keys = ['worker_host', 'status', 'models_loaded', 'ready_models', 'total_ready_models']
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

        # Verify models_loaded contains all expected model keys
        expected_models = ['qa', 'classifier', 'ner', 'summarizer', 'translator', 'whisper']
        for model in expected_models:
            assert model in result['models_loaded'], f"Missing model: {model}"

        # Verify types
        assert isinstance(result['worker_host'], str)
        assert isinstance(result['status'], str)
        assert isinstance(result['models_loaded'], dict)
        assert isinstance(result['ready_models'], list)
        assert isinstance(result['total_ready_models'], int)
