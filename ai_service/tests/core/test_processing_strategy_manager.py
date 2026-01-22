
import pytest
from unittest.mock import patch, MagicMock
from app.core.processing_strategy_manager import ProcessingStrategyManager
from app.core.processing_modes import CallProcessingMode, AudioDownloadMethod

class TestProcessingStrategyManager:


    @pytest.fixture
    def mock_settings(self):
        """Mock settings for strategy manager"""
        # Patch the source where settings is imported from
        with patch('app.config.settings.settings') as mock:
            # Default mock values - we need to set them as attributes of the mock object
            mock.default_processing_mode = "hybrid"
            mock.enable_realtime_processing = True
            mock.realtime_min_window_chars = 150
            mock.realtime_target_window_chars = 300
            mock.realtime_overlap_chars = 50
            mock.realtime_processing_interval_seconds = 30
            mock.realtime_enable_progressive_translation = True
            mock.realtime_enable_progressive_entities = True
            mock.realtime_enable_progressive_classification = True
            mock.realtime_enable_agent_notifications = True
            
            mock.enable_postcall_processing = True
            mock.postcall_enable_full_pipeline = True
            mock.postcall_enable_enhanced_transcription = True
            mock.postcall_whisper_model = "large-v3"
            mock.postcall_download_timeout_seconds = 60
            mock.postcall_convert_to_wav = True
            mock.postcall_audio_download_method = "scp"
            
            mock.adaptive_short_call_threshold_seconds = 30
            mock.adaptive_long_call_threshold_seconds = 600
            mock.adaptive_high_priority_keywords = "emergency,fire"
            
            mock.scp_user = "user"
            mock.scp_server = "server"
            mock.scp_password = "pass"
            mock.scp_remote_path_template = "/path/{call_id}"
            
            # The manager's __init__ calls self._load_config_from_settings() which reads these
            yield mock

    def test_initialization(self, mock_settings):
        """Test manager initialization reading settings"""
        manager = ProcessingStrategyManager()
        
        assert manager.config.default_mode == CallProcessingMode.HYBRID
        assert manager.config.realtime_config.enabled is True
        assert manager.config.postcall_config.enabled is True
        assert manager.config.postcall_config.audio_download_method == AudioDownloadMethod.SCP

    def test_determine_processing_mode_override(self, mock_settings):
        """Test honoring mode overrides"""
        manager = ProcessingStrategyManager()
        
        context = {"call_id": "123", "mode_override": "realtime_only"}
        mode = manager.determine_processing_mode(context)
        assert mode == CallProcessingMode.REALTIME_ONLY
        assert manager.mode_usage_stats["realtime_only"] > 0

    def test_determine_processing_mode_default(self, mock_settings):
        """Test using default mode"""
        manager = ProcessingStrategyManager()
        # Set default to something specific
        manager.config.default_mode = CallProcessingMode.POSTCALL_ONLY
        
        context = {"call_id": "123"}
        mode = manager.determine_processing_mode(context)
        assert mode == CallProcessingMode.POSTCALL_ONLY

    def test_determine_processing_mode_adaptive(self, mock_settings):
        """Test using adaptive flow when default is adaptive"""
        manager = ProcessingStrategyManager()
        manager.config.default_mode = CallProcessingMode.ADAPTIVE
        
        # Short call -> realtime
        context = {"call_id": "123", "duration_seconds": 10}
        mode = manager.determine_processing_mode(context)
        assert mode == CallProcessingMode.REALTIME_ONLY

    def test_get_audio_download_config(self, mock_settings):
        """Test verifying download config generation"""
        manager = ProcessingStrategyManager()
        
        method, config = manager.get_audio_download_config("call123")
        assert method == "scp"
        assert config["user"] == "user"
        assert config["remote_path_template"] == "/path/{call_id}"

    def test_create_call_processing_plan(self, mock_settings):
        """Test creating a full plan"""
        manager = ProcessingStrategyManager()
        
        context = {"call_id": "call_1"}
        plan = manager.create_call_processing_plan(context)
        
        assert plan["call_id"] == "call_1"
        assert plan["processing_mode"] == "hybrid"
        assert plan["realtime_processing"]["enabled"] is True
        assert plan["postcall_processing"]["enabled"] is True
        assert plan["postcall_processing"]["audio_download"]["method"] == "scp"

    def test_sanitize_sensitive_data(self, mock_settings):
        """Test sanitization of sensitive fields"""
        manager = ProcessingStrategyManager()
        
        data = {
            "public": "info",
            "password": "secret_password",
            "nested": {
                "api_key": "secret_key"
            }
        }
        
        sanitized = manager._sanitize_sensitive_data(data)
        
        assert sanitized["public"] == "info"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["nested"]["api_key"] == "***REDACTED***"

    def test_update_mode_configuration(self, mock_settings):
        """Test runtime configuration updates"""
        manager = ProcessingStrategyManager()
        
        updates = {
            "default_mode": "realtime_only",
            "realtime_config": {"min_window_chars": 999}
        }
        
        success = manager.update_mode_configuration(updates)
        assert success is True
        assert manager.config.default_mode == CallProcessingMode.REALTIME_ONLY
        assert manager.config.realtime_config.min_window_chars == 999
