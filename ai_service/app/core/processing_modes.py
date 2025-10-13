"""
Processing mode configuration and strategy management for flexible call processing
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class CallProcessingMode(Enum):
    """Defines different processing strategies for call handling"""
    REALTIME_ONLY = "realtime_only"       # Live transcription and progressive analysis only
    POSTCALL_ONLY = "postcall_only"       # No streaming, full processing after call ends
    HYBRID = "hybrid"                     # Both real-time + enhanced post-call processing
    ADAPTIVE = "adaptive"                 # Dynamic mode selection based on call characteristics

class AudioDownloadMethod(Enum):
    """Methods for downloading post-call audio"""
    SCP = "scp"                          # SCP with credentials
    HTTP = "http"                        # HTTP API download
    LOCAL = "local"                      # Local filesystem access
    DISABLED = "disabled"                # No audio download

@dataclass
class RealtimeProcessingConfig:
    """Configuration for real-time processing during calls"""
    enabled: bool = True
    min_window_chars: int = 150
    target_window_chars: int = 300
    overlap_chars: int = 50
    processing_interval_seconds: int = 30
    enable_progressive_translation: bool = True
    enable_progressive_entities: bool = True
    enable_progressive_classification: bool = True
    enable_agent_notifications: bool = True
    max_concurrent_streams: int = 2

@dataclass
class PostcallProcessingConfig:
    """Configuration for post-call processing"""
    enabled: bool = True
    audio_download_method: AudioDownloadMethod = AudioDownloadMethod.SCP
    enable_full_pipeline: bool = True
    enable_enhanced_transcription: bool = True
    enable_audio_quality_improvement: bool = True
    
    # Model configuration for post-call (higher quality)
    whisper_model: str = "large-v3"
    enable_diarization: bool = False
    enable_noise_reduction: bool = True
    
    # Audio download settings
    download_timeout_seconds: int = 60
    convert_to_wav: bool = True
    
    # Processing pipeline settings
    enable_insights_generation: bool = True
    enable_qa_scoring: bool = True
    enable_summarization: bool = True
    
    # Notification settings
    notify_completion: bool = True
    send_unified_insights: bool = True

@dataclass
class AdaptiveProcessingRules:
    """Rules for adaptive processing mode selection"""
    short_call_threshold_seconds: int = 30       # Use realtime only for very short calls
    long_call_threshold_seconds: int = 600       # Use hybrid for long calls
    high_priority_keywords: list = None          # Keywords that trigger enhanced processing
    language_specific_rules: Dict[str, str] = None  # Per-language processing preferences
    
    def __post_init__(self):
        if self.high_priority_keywords is None:
            self.high_priority_keywords = [
                "emergency", "urgent", "critical", "suicide", "violence", 
                "accident", "medical", "police", "fire", "ambulance"
            ]
        
        if self.language_specific_rules is None:
            self.language_specific_rules = {
                "sw": "hybrid",      # Swahili benefits from post-call audio quality
                "en": "realtime_only",  # English can rely on real-time processing
                "auto": "adaptive"   # Auto-detect language and adapt
            }

class ProcessingModeConfig:
    """Central configuration manager for call processing modes"""
    
    def __init__(self, 
                 default_mode: CallProcessingMode = CallProcessingMode.HYBRID,
                 realtime_config: Optional[RealtimeProcessingConfig] = None,
                 postcall_config: Optional[PostcallProcessingConfig] = None,
                 adaptive_rules: Optional[AdaptiveProcessingRules] = None):
        
        self.default_mode = default_mode
        self.realtime_config = realtime_config or RealtimeProcessingConfig()
        self.postcall_config = postcall_config or PostcallProcessingConfig()
        self.adaptive_rules = adaptive_rules or AdaptiveProcessingRules()
        
        logger.info(f"🔧 Processing mode config initialized: default={default_mode.value}")
    
    def should_enable_realtime(self, mode: CallProcessingMode) -> bool:
        """Determine if real-time processing should be enabled for this mode"""
        return mode in [CallProcessingMode.REALTIME_ONLY, CallProcessingMode.HYBRID, CallProcessingMode.ADAPTIVE]
    
    def should_enable_postcall(self, mode: CallProcessingMode) -> bool:
        """Determine if post-call processing should be enabled for this mode"""
        return mode in [CallProcessingMode.POSTCALL_ONLY, CallProcessingMode.HYBRID, CallProcessingMode.ADAPTIVE]
    
    def determine_adaptive_mode(self, call_context: Dict[str, Any]) -> CallProcessingMode:
        """Determine processing mode based on call characteristics"""
        
        # Extract call characteristics
        duration = call_context.get('duration_seconds', 0)
        language = call_context.get('language', 'auto').lower()
        transcript = call_context.get('transcript', '').lower()
        priority_score = 0
        
        # Check for high-priority keywords
        for keyword in self.adaptive_rules.high_priority_keywords:
            if keyword.lower() in transcript:
                priority_score += 1
        
        # Apply adaptive rules
        
        # Very short calls - real-time only
        if duration < self.adaptive_rules.short_call_threshold_seconds:
            logger.info(f"🤖 Adaptive mode: REALTIME_ONLY (short call: {duration}s)")
            return CallProcessingMode.REALTIME_ONLY
        
        # High priority calls - always use hybrid for best quality
        if priority_score >= 2:
            logger.info(f"🤖 Adaptive mode: HYBRID (high priority: {priority_score} keywords)")
            return CallProcessingMode.HYBRID
        
        # Language-specific rules
        if language in self.adaptive_rules.language_specific_rules:
            suggested_mode = self.adaptive_rules.language_specific_rules[language]
            if suggested_mode == "hybrid":
                logger.info(f"🤖 Adaptive mode: HYBRID (language: {language})")
                return CallProcessingMode.HYBRID
            elif suggested_mode == "realtime_only":
                logger.info(f"🤖 Adaptive mode: REALTIME_ONLY (language: {language})")
                return CallProcessingMode.REALTIME_ONLY
        
        # Default for adaptive mode
        logger.info(f"🤖 Adaptive mode: HYBRID (default)")
        return CallProcessingMode.HYBRID
    
    def get_processing_config(self, mode: CallProcessingMode) -> Dict[str, Any]:
        """Get complete processing configuration for a given mode"""
        return {
            "mode": mode.value,
            "realtime_enabled": self.should_enable_realtime(mode),
            "postcall_enabled": self.should_enable_postcall(mode),
            "realtime_config": self.realtime_config.__dict__ if self.should_enable_realtime(mode) else {},
            "postcall_config": self.postcall_config.__dict__ if self.should_enable_postcall(mode) else {},
            "adaptive_rules": self.adaptive_rules.__dict__ if mode == CallProcessingMode.ADAPTIVE else {}
        }

# Global configuration instance
processing_mode_config = ProcessingModeConfig()