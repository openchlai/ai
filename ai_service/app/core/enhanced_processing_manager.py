"""
Enhanced Processing Manager

This module defines the different processing modes for the AI service and provides
a manager to determine the appropriate mode for a given call based on a set of rules.
"""
import logging
from enum import Enum
from typing import Dict, Any, List

from app.config.settings import settings

logger = logging.getLogger(__name__)

class EnhancedProcessingMode(str, Enum):
    """
    Defines the enhanced processing modes available.
    - STREAMING: Real-time transcription and analysis only.
    - POST_CALL: Full analysis after the call has ended.
    - DUAL: Both real-time streaming and full post-call analysis.
    - ADAPTIVE: Mode is determined dynamically based on call context.
    """
    STREAMING = "streaming"
    POST_CALL = "post_call"
    DUAL = "dual"
    ADAPTIVE = "adaptive"


class EnhancedProcessingManager:
    """
    Manages the determination of processing modes for calls.
    """
    def __init__(self):
        self.mode_stats = {mode.value: 0 for mode in EnhancedProcessingMode}
        self.adaptive_keywords = [kw.strip().lower() for kw in settings.adaptive_high_priority_keywords.split(',')]
        logger.info("✅ EnhancedProcessingManager initialized")

    def determine_mode(self, call_context: Dict[str, Any]) -> EnhancedProcessingMode:
        """
        Determines the processing mode for a call based on context and rules.

        The logic is as follows:
        1. Check for an explicit `mode_override` in the call context.
        2. If the configured mode is ADAPTIVE, apply adaptive rules.
        3. Fall back to the `default_processing_mode` from settings.

        Args:
            call_context: A dictionary containing information about the call,
                          e.g., `duration_seconds`, `priority`, `transcript`.

        Returns:
            The determined EnhancedProcessingMode.
        """
        # 1. Check for explicit override
        mode_override = call_context.get("mode_override")
        if mode_override:
            try:
                mode = EnhancedProcessingMode(mode_override)
                logger.info(f"🎯 [mode] Using explicit override: {mode.value} for call {call_context.get('call_id')}")
                self.mode_stats[mode.value] += 1
                return mode
            except ValueError:
                logger.warning(f"⚠️ [mode] Invalid mode override '{mode_override}', using default")

        # 2. Apply adaptive rules if in ADAPTIVE mode
        default_mode_str = settings.default_processing_mode
        try:
            default_mode = EnhancedProcessingMode(default_mode_str)
        except ValueError:
            logger.warning(f"⚠️ [mode] Invalid default mode '{default_mode_str}', using DUAL")
            default_mode = EnhancedProcessingMode.DUAL
        
        if default_mode == EnhancedProcessingMode.ADAPTIVE:
            mode = self._apply_adaptive_rules(call_context)
            logger.info(f"🎯 [mode] Adaptively determined: {mode.value} for call {call_context.get('call_id')}")
            self.mode_stats[mode.value] += 1
            return mode

        # 3. Fall back to default configured mode
        logger.info(f"🎯 [mode] Using default mode: {default_mode.value} for call {call_context.get('call_id')}")
        self.mode_stats[default_mode.value] += 1
        return default_mode

    def _apply_adaptive_rules(self, call_context: Dict[str, Any]) -> EnhancedProcessingMode:
        """
        Applies a set of rules to determine the best processing mode.
        """
        # Get call characteristics
        duration_seconds = call_context.get("duration_seconds", -1)
        priority = call_context.get("priority", "normal")
        complexity = call_context.get("complexity", "normal")
        transcript = call_context.get("transcript", "").lower()
        language = call_context.get("language", "sw")

        # Rule 1: High priority or complexity triggers DUAL mode
        if priority == "high" or complexity == "high":
            logger.info(f"🎯 [adaptive] High priority/complexity → DUAL mode")
            return EnhancedProcessingMode.DUAL

        # Rule 2: Check for high priority keywords in transcript
        if any(kw in transcript for kw in self.adaptive_keywords):
            logger.info(f"🎯 [adaptive] High priority keyword detected → DUAL mode")
            return EnhancedProcessingMode.DUAL

        # Rule 3: Very long calls use POST_CALL to save resources
        if duration_seconds > settings.adaptive_long_call_threshold:
            logger.info(f"🎯 [adaptive] Long call ({duration_seconds}s) → POST_CALL mode")
            return EnhancedProcessingMode.POST_CALL

        # Rule 4: Very short calls only need STREAMING
        if 0 <= duration_seconds < settings.adaptive_short_call_threshold:
            logger.info(f"🎯 [adaptive] Short call ({duration_seconds}s) → STREAMING mode")
            return EnhancedProcessingMode.STREAMING
            
        # Rule 5: Language-specific logic (example)
        if language == "es":  # Spanish calls get DUAL mode
            logger.info(f"🎯 [adaptive] Spanish language → DUAL mode")
            return EnhancedProcessingMode.DUAL

        # Default adaptive outcome
        logger.info(f"🎯 [adaptive] No specific rules matched → DUAL mode (default)")
        return EnhancedProcessingMode.DUAL

    def should_enable_streaming(self, mode: EnhancedProcessingMode) -> bool:
        """
        Checks if the streaming pipeline should be activated for a given mode.
        """
        if not settings.enable_streaming_processing:
            return False
        return mode in [EnhancedProcessingMode.STREAMING, EnhancedProcessingMode.DUAL]

    def should_enable_postcall(self, mode: EnhancedProcessingMode) -> bool:
        """
        Checks if the post-call pipeline should be triggered for a given mode.
        """
        if not settings.enable_postcall_processing:
            return False
        return mode in [EnhancedProcessingMode.POST_CALL, EnhancedProcessingMode.DUAL]

    def get_processing_config(self, mode: EnhancedProcessingMode) -> Dict[str, Any]:
        """
        Returns a configuration dictionary based on the processing mode.
        """
        return {
            "mode": mode.value,
            "streaming_enabled": self.should_enable_streaming(mode),
            "postcall_enabled": self.should_enable_postcall(mode),
            "streaming_config": {
                "transcription_interval": settings.streaming_transcription_interval,
                "translation_interval": settings.streaming_translation_interval,
                "entity_update_interval": settings.streaming_entity_update_interval,
                "classification_update_interval": settings.streaming_classification_update_interval,
            } if self.should_enable_streaming(mode) else None,
            "postcall_config": {
                "enable_insights": settings.postcall_enable_insights,
                "enable_qa_scoring": settings.postcall_enable_qa_scoring,
                "enable_summary": settings.postcall_enable_summary,
                "processing_timeout": settings.postcall_processing_timeout,
            } if self.should_enable_postcall(mode) else None,
        }

    def get_mode_statistics(self) -> Dict[str, int]:
        """
        Returns statistics on how many times each mode has been used.
        """
        return self.mode_stats

# Singleton instance
enhanced_processing_manager = EnhancedProcessingManager()