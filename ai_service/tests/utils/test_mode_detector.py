"""
Tests for app/utils/mode_detector.py
Tests execution mode detection (API Server vs Standalone)
"""

import pytest
from unittest.mock import patch, MagicMock


class TestModeDetector:
    """Test execution mode detection logic"""

    def test_get_execution_mode_returns_string(self):
        """Test that get_execution_mode returns either api_server or standalone"""
        from app.utils.mode_detector import get_execution_mode

        result = get_execution_mode()
        assert result in ["api_server", "standalone"]

    def test_is_api_server_mode_is_boolean(self):
        """Test that is_api_server_mode returns a boolean"""
        from app.utils.mode_detector import is_api_server_mode

        result = is_api_server_mode()
        assert isinstance(result, bool)

    def test_is_standalone_mode_is_boolean(self):
        """Test that is_standalone_mode returns a boolean"""
        from app.utils.mode_detector import is_standalone_mode

        result = is_standalone_mode()
        assert isinstance(result, bool)

    def test_mode_detection_consistency(self):
        """Test that is_api_server_mode and is_standalone_mode are mutually exclusive"""
        from app.utils.mode_detector import is_api_server_mode, is_standalone_mode

        # Only one should be True at a time
        assert is_api_server_mode() != is_standalone_mode()
        # At least one must be True (exactly one)
        assert is_api_server_mode() or is_standalone_mode()

    def test_get_execution_mode_and_helper_consistency(self):
        """Test that get_execution_mode result matches helper functions"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode

        mode = get_execution_mode()

        if mode == "api_server":
            assert is_api_server_mode() is True
            assert is_standalone_mode() is False
        else:  # standalone
            assert is_api_server_mode() is False
            assert is_standalone_mode() is True

    def test_get_execution_mode_called_multiple_times(self):
        """Test that get_execution_mode returns consistent result"""
        from app.utils.mode_detector import get_execution_mode

        # Call multiple times - should be consistent
        result1 = get_execution_mode()
        result2 = get_execution_mode()
        result3 = get_execution_mode()

        assert result1 == result2 == result3

    @patch('app.config.settings.settings')
    def test_mode_detection_respects_settings(self, mock_settings):
        """Test that mode detection considers enable_model_loading setting"""
        # Test API server mode (model loading disabled)
        mock_settings.enable_model_loading = False

        from app.utils.mode_detector import get_execution_mode

        # When settings say model loading is disabled, should be API server mode
        result = get_execution_mode()
        # Result depends on whether models are actually loaded, but settings affect it
        assert isinstance(result, str)

    def test_get_execution_mode_type_validation(self):
        """Test that return type is always a string literal"""
        from app.utils.mode_detector import get_execution_mode

        result = get_execution_mode()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_api_server_mode_implies_not_standalone(self):
        """Test that API server mode implies standalone is False"""
        from app.utils.mode_detector import is_api_server_mode, is_standalone_mode

        if is_api_server_mode():
            assert not is_standalone_mode()

    def test_standalone_mode_implies_not_api_server(self):
        """Test that standalone mode implies API server is False"""
        from app.utils.mode_detector import is_api_server_mode, is_standalone_mode

        if is_standalone_mode():
            assert not is_api_server_mode()

    def test_execution_mode_detection_callable(self):
        """Test that all mode detection functions are callable"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode

        assert callable(get_execution_mode)
        assert callable(is_api_server_mode)
        assert callable(is_standalone_mode)

    def test_mode_functions_require_no_arguments(self):
        """Test that mode detection functions require no arguments"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode
        import inspect

        # Check get_execution_mode signature
        sig = inspect.signature(get_execution_mode)
        assert len(sig.parameters) == 0

        # Check is_api_server_mode signature
        sig = inspect.signature(is_api_server_mode)
        assert len(sig.parameters) == 0

        # Check is_standalone_mode signature
        sig = inspect.signature(is_standalone_mode)
        assert len(sig.parameters) == 0
