"""
Comprehensive tests for audio_tasks.py worker initialization and core functions
Focus: Achieving 95% coverage by testing worker init, task processing, and error handling
"""
import pytest
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call
from datetime import datetime


class TestWorkerInitialization:
    """Tests for worker initialization (@worker_init.connect)"""

    @patch('app.tasks.audio_tasks.initialize_redis')
    @patch('app.tasks.audio_tasks.ModelLoader')
    @patch('app.tasks.audio_tasks.settings')
    @patch('app.tasks.audio_tasks.logger')
    def test_init_worker_success(self, mock_logger, mock_settings, mock_model_loader_class, mock_init_redis):
        """Test successful worker initialization"""
        from app.tasks.audio_tasks import init_worker

        # Setup mocks
        mock_init_redis.return_value = True
        mock_settings.initialize_paths.return_value = "/app/models"
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_ready_models.return_value = ["whisper", "translator"]
        mock_loader_instance.get_implementable_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = []
        mock_loader_instance.get_failed_models.return_value = []
        mock_model_loader_class.return_value = mock_loader_instance

        # Mock async load_all_models
        async def mock_load_all():
            return True
        mock_loader_instance.load_all_models = AsyncMock(return_value=True)

        # Mock os.path.exists to return True for models path
        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['whisper', 'translator']):
                with patch('os.getcwd', return_value='/app'):
                    with patch('asyncio.get_event_loop') as mock_get_loop:
                        mock_loop = MagicMock()
                        mock_loop.is_closed.return_value = False
                        mock_loop.run_until_complete = MagicMock()
                        mock_get_loop.return_value = mock_loop

                        # Call init_worker
                        init_worker()

                        # Verify calls
                        mock_init_redis.assert_called_once()
                        mock_settings.initialize_paths.assert_called_once()
                        mock_model_loader_class.assert_called_once()
                        mock_logger.info.assert_called()

    @patch('app.tasks.audio_tasks.initialize_redis')
    @patch('app.tasks.audio_tasks.ModelLoader')
    @patch('app.tasks.audio_tasks.settings')
    @patch('app.tasks.audio_tasks.logger')
    def test_init_worker_redis_failure(self, mock_logger, mock_settings, mock_model_loader_class, mock_init_redis):
        """Test worker initialization when Redis fails"""
        from app.tasks.audio_tasks import init_worker

        # Setup mocks - Redis fails
        mock_init_redis.return_value = False
        mock_settings.initialize_paths.return_value = "/app/models"
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_ready_models.return_value = []
        mock_loader_instance.get_implementable_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = []
        mock_loader_instance.get_failed_models.return_value = []
        mock_model_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_all_models = AsyncMock()

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=[]):
                with patch('os.getcwd', return_value='/app'):
                    with patch('asyncio.get_event_loop') as mock_get_loop:
                        mock_loop = MagicMock()
                        mock_loop.is_closed.return_value = False
                        mock_loop.run_until_complete = MagicMock()
                        mock_get_loop.return_value = mock_loop

                        init_worker()

                        # Verify warning was logged
                        warning_calls = [call for call in mock_logger.warning.call_args_list
                                       if "Redis initialization failed" in str(call)]
                        assert len(warning_calls) > 0

    @patch('app.tasks.audio_tasks.initialize_redis')
    @patch('app.tasks.audio_tasks.ModelLoader')
    @patch('app.tasks.audio_tasks.settings')
    @patch('app.tasks.audio_tasks.logger')
    def test_init_worker_models_path_not_found(self, mock_logger, mock_settings,
                                                 mock_model_loader_class, mock_init_redis):
        """Test worker initialization when models path doesn't exist"""
        from app.tasks.audio_tasks import init_worker

        mock_init_redis.return_value = True
        mock_settings.initialize_paths.return_value = "/app/models"
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_ready_models.return_value = []
        mock_loader_instance.get_implementable_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = []
        mock_loader_instance.get_failed_models.return_value = []
        mock_model_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_all_models = AsyncMock()

        # Mock os.path.exists to return False for models path
        def exists_side_effect(path):
            if path == "/app/models":
                return False
            elif path in ["./models", "../models", "models", "/app/models"]:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect):
            with patch('os.listdir', return_value=['model1']):
                with patch('os.path.abspath', side_effect=lambda x: x):
                    with patch('os.getcwd', return_value='/app'):
                        with patch('asyncio.get_event_loop') as mock_get_loop:
                            mock_loop = MagicMock()
                            mock_loop.is_closed.return_value = False
                            mock_loop.run_until_complete = MagicMock()
                            mock_get_loop.return_value = mock_loop

                            init_worker()

                            # Verify warning about models directory not found
                            error_calls = [call for call in mock_logger.error.call_args_list
                                          if "NOT FOUND" in str(call)]
                            assert len(error_calls) > 0

    @patch('app.tasks.audio_tasks.initialize_redis')
    @patch('app.tasks.audio_tasks.ModelLoader')
    @patch('app.tasks.audio_tasks.settings')
    @patch('app.tasks.audio_tasks.logger')
    def test_init_worker_event_loop_closed(self, mock_logger, mock_settings,
                                            mock_model_loader_class, mock_init_redis):
        """Test worker initialization when event loop is closed"""
        from app.tasks.audio_tasks import init_worker

        mock_init_redis.return_value = True
        mock_settings.initialize_paths.return_value = "/app/models"
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_ready_models.return_value = ["whisper"]
        mock_loader_instance.get_implementable_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = []
        mock_loader_instance.get_failed_models.return_value = []
        mock_model_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_all_models = AsyncMock()

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['whisper']):
                with patch('os.getcwd', return_value='/app'):
                    with patch('asyncio.get_event_loop') as mock_get_loop:
                        # Event loop is closed, should create new one
                        mock_closed_loop = MagicMock()
                        mock_closed_loop.is_closed.return_value = True
                        mock_new_loop = MagicMock()
                        mock_new_loop.run_until_complete = MagicMock()

                        mock_get_loop.return_value = mock_closed_loop

                        with patch('asyncio.new_event_loop', return_value=mock_new_loop):
                            with patch('asyncio.set_event_loop') as mock_set_loop:
                                init_worker()

                                # Verify new loop was created and set
                                mock_set_loop.assert_called()

    @patch('app.tasks.audio_tasks.initialize_redis')
    @patch('app.tasks.audio_tasks.ModelLoader')
    @patch('app.tasks.audio_tasks.settings')
    @patch('app.tasks.audio_tasks.logger')
    def test_init_worker_runtime_error(self, mock_logger, mock_settings,
                                        mock_model_loader_class, mock_init_redis):
        """Test worker initialization when get_event_loop raises RuntimeError"""
        from app.tasks.audio_tasks import init_worker

        mock_init_redis.return_value = True
        mock_settings.initialize_paths.return_value = "/app/models"
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_ready_models.return_value = []
        mock_loader_instance.get_implementable_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = []
        mock_loader_instance.get_failed_models.return_value = []
        mock_model_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_all_models = AsyncMock()

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=[]):
                with patch('os.getcwd', return_value='/app'):
                    with patch('asyncio.get_event_loop', side_effect=RuntimeError("No event loop")):
                        mock_new_loop = MagicMock()
                        mock_new_loop.run_until_complete = MagicMock()

                        with patch('asyncio.new_event_loop', return_value=mock_new_loop):
                            with patch('asyncio.set_event_loop'):
                                init_worker()

                                # Should create new loop on RuntimeError
                                assert mock_new_loop.run_until_complete.called

    @patch('app.tasks.audio_tasks.initialize_redis')
    @patch('app.tasks.audio_tasks.ModelLoader')
    @patch('app.tasks.audio_tasks.settings')
    @patch('app.tasks.audio_tasks.logger')
    def test_init_worker_with_failed_models(self, mock_logger, mock_settings,
                                             mock_model_loader_class, mock_init_redis):
        """Test worker initialization when some models fail to load"""
        from app.tasks.audio_tasks import init_worker

        mock_init_redis.return_value = True
        mock_settings.initialize_paths.return_value = "/app/models"
        mock_loader_instance = MagicMock()
        mock_loader_instance.get_ready_models.return_value = ["whisper"]
        mock_loader_instance.get_implementable_models.return_value = []
        mock_loader_instance.get_blocked_models.return_value = ["classifier"]
        mock_loader_instance.get_failed_models.return_value = ["ner"]
        mock_model_loader_class.return_value = mock_loader_instance
        mock_loader_instance.load_all_models = AsyncMock()

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['whisper']):
                with patch('os.getcwd', return_value='/app'):
                    with patch('asyncio.get_event_loop') as mock_get_loop:
                        mock_loop = MagicMock()
                        mock_loop.is_closed.return_value = False
                        mock_loop.run_until_complete = MagicMock()
                        mock_get_loop.return_value = mock_loop

                        init_worker()

                        # Verify logging of failed/blocked models
                        assert mock_logger.info.called
                        # Check that blocked and failed models were logged
                        log_messages = [str(call) for call in mock_logger.info.call_args_list]
                        assert any("Blocked models" in msg or "blocked_models" in msg.lower()
                                  for msg in log_messages)


class TestGetWorkerModels:
    """Tests for get_worker_models function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_get_worker_models_when_initialized(self, mock_loader):
        """Test get_worker_models when loader is initialized"""
        from app.tasks.audio_tasks import get_worker_models

        mock_loader.models = {"whisper": MagicMock(), "translator": MagicMock()}

        result = get_worker_models()

        assert result is not None
        assert result == mock_loader

    @patch('app.tasks.audio_tasks.worker_model_loader', None)
    def test_get_worker_models_when_not_initialized(self):
        """Test get_worker_models when loader is None"""
        from app.tasks.audio_tasks import get_worker_models

        result = get_worker_models()

        assert result is None


class TestGetWorkerStatus:
    """Tests for get_worker_status function"""

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_get_worker_status_ready(self, mock_loader):
        """Test get_worker_status when models are ready"""
        from app.tasks.audio_tasks import get_worker_status

        mock_loader.get_ready_models.return_value = ["whisper", "translator", "ner"]
        mock_loader.get_failed_models.return_value = []

        result = get_worker_status()

        assert result is not None
        assert result["status"] == "ready"
        assert len(result["ready_models"]) == 3
        assert "whisper" in result["ready_models"]

    @patch('app.tasks.audio_tasks.worker_model_loader')
    def test_get_worker_status_with_failures(self, mock_loader):
        """Test get_worker_status when some models failed"""
        from app.tasks.audio_tasks import get_worker_status

        mock_loader.get_ready_models.return_value = ["whisper"]
        mock_loader.get_failed_models.return_value = ["classifier", "ner"]

        result = get_worker_status()

        assert result is not None
        assert result["status"] == "ready"
        assert len(result["ready_models"]) == 1
        assert len(result["failed_models"]) == 2

    @patch('app.tasks.audio_tasks.worker_model_loader', None)
    def test_get_worker_status_not_initialized(self):
        """Test get_worker_status when loader is not initialized"""
        from app.tasks.audio_tasks import get_worker_status

        result = get_worker_status()

        assert result is not None
        assert result["status"] == "not_initialized"
        assert "error" in result
        assert result["ready_models"] == []
