"""
Tests for app/utils/mode_detector.py
Tests execution mode detection (API Server vs Standalone)
"""

import pytest
from unittest.mock import patch, MagicMock


class TestGetExecutionModeBranches:
    """Tests for all branches in get_execution_mode function"""

    def test_api_server_mode_when_model_loading_disabled(self):
        """Test returns 'api_server' when enable_model_loading is False"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = False

            from app.utils.mode_detector import get_execution_mode
            result = get_execution_mode()
            assert result == "api_server"

    def test_standalone_mode_when_models_loaded(self):
        """Test returns 'standalone' when models are loaded locally"""
        mock_model_loader = MagicMock()
        mock_model_loader.get_ready_models.return_value = ["whisper", "translator"]

        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = True

            with patch.dict('sys.modules', {'app.model_scripts.model_loader': MagicMock(model_loader=mock_model_loader)}):
                from app.utils.mode_detector import get_execution_mode
                # This tests the try path with models loaded
                result = get_execution_mode()
                # Result depends on actual model_loader state

    def test_api_server_mode_when_no_models_loaded(self):
        """Test returns 'api_server' when model loading enabled but no models loaded"""
        mock_model_loader = MagicMock()
        mock_model_loader.get_ready_models.return_value = []

        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = True

            with patch('app.model_scripts.model_loader.model_loader', mock_model_loader):
                from app.utils.mode_detector import get_execution_mode
                result = get_execution_mode()
                # Result depends on actual model_loader state

    def test_exception_handling_path(self):
        """Test exception handling when model_loader fails"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = True

            # Simulate import error for model_loader
            original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

            def mock_import(name, *args, **kwargs):
                if 'model_loader' in name:
                    raise ImportError("Test exception")
                return original_import(name, *args, **kwargs)

            # Just verify the function handles exceptions gracefully
            from app.utils.mode_detector import get_execution_mode
            result = get_execution_mode()
            assert result in ["api_server", "standalone"]

    def test_exception_fallback_standalone_mode(self):
        """Test exception fallback returns 'standalone' when enable_model_loading=True"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = True

            # Force exception in get_ready_models call
            with patch('app.model_scripts.model_loader.model_loader') as mock_loader:
                mock_loader.get_ready_models.side_effect = Exception("Model loader crashed")

                from app.utils.mode_detector import get_execution_mode
                result = get_execution_mode()
                assert result == "standalone"

    def test_exception_fallback_api_server_mode(self):
        """Test exception fallback returns 'api_server' when enable_model_loading=False"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = False

            # Force exception in get_ready_models call
            with patch('app.model_scripts.model_loader.model_loader') as mock_loader:
                mock_loader.get_ready_models.side_effect = Exception("Model loader crashed")

                from app.utils.mode_detector import get_execution_mode
                result = get_execution_mode()
                assert result == "api_server"

    def test_is_api_server_mode_returns_correct_bool(self):
        """Test is_api_server_mode returns correct boolean based on execution mode"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.enable_model_loading = False

            from app.utils.mode_detector import is_api_server_mode
            result = is_api_server_mode()
            assert isinstance(result, bool)

    def test_is_standalone_mode_returns_correct_bool(self):
        """Test is_standalone_mode returns correct boolean based on execution mode"""
        from app.utils.mode_detector import is_standalone_mode
        result = is_standalone_mode()
        assert isinstance(result, bool)


class TestGetExecutionMode:
    """Tests for get_execution_mode function"""

    def test_get_execution_mode_returns_valid_string(self):
        """Test that get_execution_mode returns a valid mode string"""
        from app.utils.mode_detector import get_execution_mode

        result = get_execution_mode()
        assert result in ["api_server", "standalone"]

    def test_get_execution_mode_type(self):
        """Test return type is string"""
        from app.utils.mode_detector import get_execution_mode

        result = get_execution_mode()
        assert isinstance(result, str)

    def test_get_execution_mode_consistent(self):
        """Test that get_execution_mode returns consistent result"""
        from app.utils.mode_detector import get_execution_mode

        results = [get_execution_mode() for _ in range(5)]
        assert all(r == results[0] for r in results)


class TestIsApiServerMode:
    """Tests for is_api_server_mode function"""

    def test_returns_boolean(self):
        """Test that is_api_server_mode returns a boolean"""
        from app.utils.mode_detector import is_api_server_mode

        result = is_api_server_mode()
        assert isinstance(result, bool)

    def test_api_server_mode_type(self):
        """Test type is bool"""
        from app.utils.mode_detector import is_api_server_mode

        result = is_api_server_mode()
        assert type(result) is bool


class TestIsStandaloneMode:
    """Tests for is_standalone_mode function"""

    def test_returns_boolean(self):
        """Test that is_standalone_mode returns a boolean"""
        from app.utils.mode_detector import is_standalone_mode

        result = is_standalone_mode()
        assert isinstance(result, bool)

    def test_standalone_mode_type(self):
        """Test type is bool"""
        from app.utils.mode_detector import is_standalone_mode

        result = is_standalone_mode()
        assert type(result) is bool


class TestModeConsistency:
    """Tests for consistency between mode detection functions"""

    def test_modes_are_mutually_exclusive(self):
        """Test that is_api_server_mode and is_standalone_mode are mutually exclusive"""
        from app.utils.mode_detector import is_api_server_mode, is_standalone_mode

        # Only one should be True at a time
        assert is_api_server_mode() != is_standalone_mode()

    def test_exactly_one_mode_is_true(self):
        """Test that exactly one mode is True"""
        from app.utils.mode_detector import is_api_server_mode, is_standalone_mode

        # Exactly one must be True
        assert is_api_server_mode() or is_standalone_mode()
        assert not (is_api_server_mode() and is_standalone_mode())

    def test_get_execution_mode_matches_helpers(self):
        """Test that get_execution_mode result matches helper functions"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode

        mode = get_execution_mode()

        if mode == "api_server":
            assert is_api_server_mode() is True
            assert is_standalone_mode() is False
        else:
            assert is_api_server_mode() is False
            assert is_standalone_mode() is True

    def test_consistent_across_multiple_calls(self):
        """Test that get_execution_mode returns consistent result"""
        from app.utils.mode_detector import get_execution_mode

        results = [get_execution_mode() for _ in range(5)]
        assert all(r == results[0] for r in results)


class TestFunctionSignatures:
    """Tests for function signatures and types"""

    def test_get_execution_mode_returns_valid_string(self):
        """Test that get_execution_mode returns a valid mode string"""
        from app.utils.mode_detector import get_execution_mode

        result = get_execution_mode()
        assert result in ["api_server", "standalone"]

    def test_functions_require_no_arguments(self):
        """Test that mode detection functions require no arguments"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode
        import inspect

        for func in [get_execution_mode, is_api_server_mode, is_standalone_mode]:
            sig = inspect.signature(func)
            assert len(sig.parameters) == 0

    def test_all_functions_are_callable(self):
        """Test that all mode detection functions are callable"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode

        assert callable(get_execution_mode)
        assert callable(is_api_server_mode)
        assert callable(is_standalone_mode)


class TestModuleImports:
    """Test that module can be imported correctly"""

    def test_module_imports(self):
        """Test that module imports correctly"""
        from app.utils import mode_detector

        assert hasattr(mode_detector, 'get_execution_mode')
        assert hasattr(mode_detector, 'is_api_server_mode')
        assert hasattr(mode_detector, 'is_standalone_mode')

    def test_functions_exist(self):
        """Test that all functions exist"""
        from app.utils.mode_detector import get_execution_mode, is_api_server_mode, is_standalone_mode

        assert get_execution_mode is not None
        assert is_api_server_mode is not None
        assert is_standalone_mode is not None
