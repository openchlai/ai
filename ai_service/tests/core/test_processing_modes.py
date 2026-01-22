
import pytest
from app.core.processing_modes import (
    CallProcessingMode,
    AudioDownloadMethod,
    RealtimeProcessingConfig,
    PostcallProcessingConfig,
    AdaptiveProcessingRules,
    ProcessingModeConfig
)

class TestProcessingModes:
    
    def test_enums(self):
        """Test basic enum values"""
        assert CallProcessingMode.REALTIME_ONLY.value == "realtime_only"
        assert CallProcessingMode.POSTCALL_ONLY.value == "postcall_only"
        assert CallProcessingMode.HYBRID.value == "hybrid"
        assert CallProcessingMode.ADAPTIVE.value == "adaptive"
        
        assert AudioDownloadMethod.SCP.value == "scp"
        assert AudioDownloadMethod.HTTP.value == "http"
        assert AudioDownloadMethod.LOCAL.value == "local"
        assert AudioDownloadMethod.DISABLED.value == "disabled"

    def test_dataclasses_defaults(self):
        """Test default values of dataclasses"""
        rt_config = RealtimeProcessingConfig()
        assert rt_config.enabled is True
        assert rt_config.min_window_chars == 150
        
        pc_config = PostcallProcessingConfig()
        assert pc_config.enabled is True
        assert pc_config.audio_download_method == AudioDownloadMethod.SCP
        
        adaptive_rules = AdaptiveProcessingRules()
        assert adaptive_rules.short_call_threshold_seconds == 30
        assert "emergency" in adaptive_rules.high_priority_keywords

    def test_should_enable_realtime(self):
        """Test logic for enabling realtime processing"""
        config = ProcessingModeConfig()
        
        assert config.should_enable_realtime(CallProcessingMode.REALTIME_ONLY) is True
        assert config.should_enable_realtime(CallProcessingMode.HYBRID) is True
        assert config.should_enable_realtime(CallProcessingMode.ADAPTIVE) is True
        assert config.should_enable_realtime(CallProcessingMode.POSTCALL_ONLY) is False

    def test_should_enable_postcall(self):
        """Test logic for enabling postcall processing"""
        config = ProcessingModeConfig()
        
        assert config.should_enable_postcall(CallProcessingMode.POSTCALL_ONLY) is True
        assert config.should_enable_postcall(CallProcessingMode.HYBRID) is True
        assert config.should_enable_postcall(CallProcessingMode.ADAPTIVE) is True
        assert config.should_enable_postcall(CallProcessingMode.REALTIME_ONLY) is False

    def test_determine_adaptive_mode_short_call(self):
        """Test adaptive mode: short call"""
        config = ProcessingModeConfig()
        context = {"duration_seconds": 10} # < 30s threshold
        
        mode = config.determine_adaptive_mode(context)
        assert mode == CallProcessingMode.REALTIME_ONLY

    def test_determine_adaptive_mode_high_priority(self):
        """Test adaptive mode: high priority keywords"""
        config = ProcessingModeConfig()
        # duration > short threshold, but high priority keywords
        context = {
            "duration_seconds": 60,
            "transcript": "hello emergency help police" # contains multiple keywords
        }
        
        mode = config.determine_adaptive_mode(context)
        assert mode == CallProcessingMode.HYBRID

    def test_determine_adaptive_mode_language(self):
        """Test adaptive mode: language specific"""
        config = ProcessingModeConfig()
        
        # English -> realtime_only (default rule)
        context_en = {"duration_seconds": 60, "language": "en"}
        assert config.determine_adaptive_mode(context_en) == CallProcessingMode.REALTIME_ONLY
        
        # Swahili -> hybrid (default rule)
        context_sw = {"duration_seconds": 60, "language": "sw"}
        assert config.determine_adaptive_mode(context_sw) == CallProcessingMode.HYBRID

    def test_get_processing_config(self):
        """Test getting full config dict"""
        config = ProcessingModeConfig()
        
        res = config.get_processing_config(CallProcessingMode.HYBRID)
        assert res["mode"] == "hybrid"
        assert res["realtime_enabled"] is True
        assert res["postcall_enabled"] is True
        assert "realtime_config" in res
        assert "postcall_config" in res
