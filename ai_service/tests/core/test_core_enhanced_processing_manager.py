
import pytest
from enum import Enum
from unittest.mock import patch, MagicMock
from app.core.enhanced_processing_manager import EnhancedProcessingManager, EnhancedProcessingMode

class TestEnhancedProcessingManager:

    @pytest.fixture
    def mock_settings(self):
        with patch('app.core.enhanced_processing_manager.settings') as mock:
            # Setting default values for tests
            mock.default_processing_mode = "dual"
            mock.adaptive_high_priority_keywords = "emergency,fire"
            mock.adaptive_long_call_threshold = 600
            mock.adaptive_short_call_threshold = 30
            mock.enable_streaming_processing = True
            mock.enable_postcall_processing = True
            
            # Configs
            mock.streaming_transcription_interval = 2
            mock.streaming_translation_interval = 5
            mock.streaming_entity_update_interval = 10
            mock.streaming_classification_update_interval = 30
            
            mock.postcall_enable_insights = True
            mock.postcall_enable_qa_scoring = True
            mock.postcall_enable_summary = True
            mock.postcall_processing_timeout = 300
            
            yield mock

    def test_initialization(self, mock_settings):
        manager = EnhancedProcessingManager()
        assert "streaming" in manager.mode_stats
        assert "emergency" in manager.adaptive_keywords

    def test_determine_mode_override(self, mock_settings):
        manager = EnhancedProcessingManager()
        context = {"call_id": "1", "mode_override": "streaming"}
        
        mode = manager.determine_mode(context)
        assert mode == EnhancedProcessingMode.STREAMING
        assert manager.mode_stats["streaming"] == 1

    def test_determine_mode_fallback_default(self, mock_settings):
        manager = EnhancedProcessingManager()
        mock_settings.default_processing_mode = "post_call"
        
        context = {"call_id": "1"}
        mode = manager.determine_mode(context)
        assert mode == EnhancedProcessingMode.POST_CALL

    def test_determine_mode_adaptive(self, mock_settings):
        manager = EnhancedProcessingManager()
        mock_settings.default_processing_mode = "adaptive"
        
        # Test short call -> Streaming
        context_short = {"call_id": "2", "duration_seconds": 10}
        assert manager.determine_mode(context_short) == EnhancedProcessingMode.STREAMING
        
        # Test long call -> Post Call
        context_long = {"call_id": "3", "duration_seconds": 700}
        assert manager.determine_mode(context_long) == EnhancedProcessingMode.POST_CALL
        
        # Test high priority -> Dual
        context_prio = {"call_id": "4", "duration_seconds": 100, "priority": "high"}
        assert manager.determine_mode(context_prio) == EnhancedProcessingMode.DUAL
        
        # Test high priority keyword -> Dual
        context_kw = {"call_id": "5", "duration_seconds": 100, "transcript": "this is an emergency"}
        assert manager.determine_mode(context_kw) == EnhancedProcessingMode.DUAL
        
        # Test specific language -> Dual
        context_es = {"call_id": "6", "duration_seconds": 100, "language": "es"}
        assert manager.determine_mode(context_es) == EnhancedProcessingMode.DUAL
        
        # Test Default adaptive -> Dual
        context_def = {"call_id": "7", "duration_seconds": 100}
        assert manager.determine_mode(context_def) == EnhancedProcessingMode.DUAL

    def test_determine_mode_invalid_override(self, mock_settings):
        manager = EnhancedProcessingManager()
        context = {"call_id": "1", "mode_override": "invalid_mode"}
        
        # Should fallback to default (dual)
        mode = manager.determine_mode(context)
        assert mode == EnhancedProcessingMode.DUAL

    def test_determine_mode_invalid_default(self, mock_settings):
        mock_settings.default_processing_mode = "invalid"
        manager = EnhancedProcessingManager()
        
        # Should fallback to DUAL hardcoded default
        context = {"call_id": "1"}
        mode = manager.determine_mode(context)
        assert mode == EnhancedProcessingMode.DUAL

    def test_should_enable_streaming(self, mock_settings):
        manager = EnhancedProcessingManager()
        
        assert manager.should_enable_streaming(EnhancedProcessingMode.STREAMING) is True
        assert manager.should_enable_streaming(EnhancedProcessingMode.DUAL) is True
        assert manager.should_enable_streaming(EnhancedProcessingMode.POST_CALL) is False
        
        mock_settings.enable_streaming_processing = False
        assert manager.should_enable_streaming(EnhancedProcessingMode.STREAMING) is False

    def test_should_enable_postcall(self, mock_settings):
        manager = EnhancedProcessingManager()
        
        assert manager.should_enable_postcall(EnhancedProcessingMode.POST_CALL) is True
        assert manager.should_enable_postcall(EnhancedProcessingMode.DUAL) is True
        assert manager.should_enable_postcall(EnhancedProcessingMode.STREAMING) is False
        
        mock_settings.enable_postcall_processing = False
        assert manager.should_enable_postcall(EnhancedProcessingMode.POST_CALL) is False

    def test_get_processing_config(self, mock_settings):
        manager = EnhancedProcessingManager()
        
        # Test DUAL config
        config = manager.get_processing_config(EnhancedProcessingMode.DUAL)
        assert config["streaming_enabled"] is True
        assert config["postcall_enabled"] is True
        assert config["streaming_config"] is not None
        assert config["postcall_config"] is not None
        
        # Test STREAMING config
        config = manager.get_processing_config(EnhancedProcessingMode.STREAMING)
        assert config["streaming_enabled"] is True
        assert config["postcall_enabled"] is False
        assert config["postcall_config"] is None

    def test_get_mode_statistics(self, mock_settings):
        manager = EnhancedProcessingManager()
        manager.mode_stats["streaming"] = 5
        assert manager.get_mode_statistics()["streaming"] == 5
