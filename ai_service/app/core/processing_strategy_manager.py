"""
Processing Strategy Manager for flexible call processing mode management
Coordinates between real-time and post-call processing based on configuration
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .processing_modes import (
    CallProcessingMode, 
    ProcessingModeConfig,
    RealtimeProcessingConfig,
    PostcallProcessingConfig,
    AudioDownloadMethod
)

logger = logging.getLogger(__name__)

class ProcessingStrategyManager:
    """
    Central manager for coordinating call processing strategies
    Handles mode determination, resource allocation, and processing coordination
    """
    
    def __init__(self, config: Optional[ProcessingModeConfig] = None):
        from ..config.settings import settings
        
        self.settings = settings
        self.config = config or ProcessingModeConfig()
        
        # Initialize from settings
        self._load_config_from_settings()
        
        # Runtime statistics
        self.mode_usage_stats = {
            "realtime_only": 0,
            "postcall_only": 0, 
            "hybrid": 0,
            "adaptive": 0
        }
        
        logger.info(f"🎛️ ProcessingStrategyManager initialized with default mode: {self.config.default_mode.value}")
    
    def _load_config_from_settings(self):
        """Load configuration from settings"""
        try:
            # Map string mode to enum
            mode_mapping = {
                "realtime_only": CallProcessingMode.REALTIME_ONLY,
                "postcall_only": CallProcessingMode.POSTCALL_ONLY,
                "hybrid": CallProcessingMode.HYBRID,
                "adaptive": CallProcessingMode.ADAPTIVE
            }
            
            default_mode_str = self.settings.default_processing_mode.lower()
            self.config.default_mode = mode_mapping.get(default_mode_str, CallProcessingMode.HYBRID)
            
            # Update real-time config from settings
            self.config.realtime_config.enabled = self.settings.enable_realtime_processing
            self.config.realtime_config.min_window_chars = self.settings.realtime_min_window_chars
            self.config.realtime_config.target_window_chars = self.settings.realtime_target_window_chars
            self.config.realtime_config.processing_interval_seconds = self.settings.realtime_processing_interval_seconds
            self.config.realtime_config.enable_progressive_translation = self.settings.realtime_enable_progressive_translation
            self.config.realtime_config.enable_progressive_entities = self.settings.realtime_enable_progressive_entities
            self.config.realtime_config.enable_progressive_classification = self.settings.realtime_enable_progressive_classification
            self.config.realtime_config.enable_agent_notifications = self.settings.realtime_enable_agent_notifications
            
            # Update post-call config from settings
            self.config.postcall_config.enabled = self.settings.enable_postcall_processing
            self.config.postcall_config.enable_full_pipeline = self.settings.postcall_enable_full_pipeline
            self.config.postcall_config.enable_enhanced_transcription = self.settings.postcall_enable_enhanced_transcription
            self.config.postcall_config.whisper_model = self.settings.postcall_whisper_model
            self.config.postcall_config.download_timeout_seconds = self.settings.postcall_download_timeout_seconds
            self.config.postcall_config.convert_to_wav = self.settings.postcall_convert_to_wav
            
            # Map download method string to enum
            method_mapping = {
                "scp": AudioDownloadMethod.SCP,
                "http": AudioDownloadMethod.HTTP,
                "local": AudioDownloadMethod.LOCAL,
                "disabled": AudioDownloadMethod.DISABLED
            }
            method_str = self.settings.postcall_audio_download_method.lower()
            self.config.postcall_config.audio_download_method = method_mapping.get(method_str, AudioDownloadMethod.SCP)
            
            # Update adaptive rules from settings
            self.config.adaptive_rules.short_call_threshold_seconds = self.settings.adaptive_short_call_threshold_seconds
            self.config.adaptive_rules.long_call_threshold_seconds = self.settings.adaptive_long_call_threshold_seconds
            
            keywords_str = self.settings.adaptive_high_priority_keywords
            self.config.adaptive_rules.high_priority_keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            
            logger.info(f"🎛️ Loaded configuration from settings: {self.config.default_mode.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load config from settings: {e}")
            logger.warning("⚠️ Using default configuration")
    
    def determine_processing_mode(self, call_context: Dict[str, Any]) -> CallProcessingMode:
        """
        Determine the appropriate processing mode for a call
        
        Args:
            call_context: Dictionary containing call information:
                - call_id: str
                - duration_seconds: float (optional)
                - language: str (optional)
                - transcript: str (optional) 
                - priority_override: str (optional)
                - client_config: Dict (optional)
        
        Returns:
            CallProcessingMode to use for this call
        """
        
        call_id = call_context.get('call_id', 'unknown')
        
        # Check for explicit override
        if 'mode_override' in call_context:
            override_mode_str = call_context['mode_override'].lower()
            mode_mapping = {
                "realtime_only": CallProcessingMode.REALTIME_ONLY,
                "postcall_only": CallProcessingMode.POSTCALL_ONLY,
                "hybrid": CallProcessingMode.HYBRID,
                "adaptive": CallProcessingMode.ADAPTIVE
            }
            if override_mode_str in mode_mapping:
                override_mode = mode_mapping[override_mode_str]
                logger.info(f"🎛️ [mode] Using override mode for {call_id}: {override_mode.value}")
                self.mode_usage_stats[override_mode.value] += 1
                return override_mode
        
        # Use configured default mode
        if self.config.default_mode != CallProcessingMode.ADAPTIVE:
            logger.info(f"🎛️ [mode] Using default mode for {call_id}: {self.config.default_mode.value}")
            self.mode_usage_stats[self.config.default_mode.value] += 1
            return self.config.default_mode
        
        # Adaptive mode determination
        adaptive_mode = self.config.determine_adaptive_mode(call_context)
        logger.info(f"🎛️ [mode] Adaptive mode selected for {call_id}: {adaptive_mode.value}")
        self.mode_usage_stats[adaptive_mode.value] += 1
        return adaptive_mode
    
    def should_enable_realtime_processing(self, mode: CallProcessingMode, call_context: Dict[str, Any] = None) -> bool:
        """Check if real-time processing should be enabled for this call"""
        
        # Global real-time processing disabled
        if not self.config.realtime_config.enabled:
            return False
            
        # Mode-specific logic
        return self.config.should_enable_realtime(mode)
    
    def should_enable_postcall_processing(self, mode: CallProcessingMode, call_context: Dict[str, Any] = None) -> bool:
        """Check if post-call processing should be enabled for this call"""
        
        # Global post-call processing disabled
        if not self.config.postcall_config.enabled:
            return False
            
        # Mode-specific logic
        return self.config.should_enable_postcall(mode)
    
    def get_realtime_config(self, call_context: Dict[str, Any] = None) -> RealtimeProcessingConfig:
        """Get real-time processing configuration for a call"""
        # For now, return global config - could be customized per call in future
        return self.config.realtime_config
    
    def get_postcall_config(self, call_context: Dict[str, Any] = None) -> PostcallProcessingConfig:
        """Get post-call processing configuration for a call"""
        # For now, return global config - could be customized per call in future
        return self.config.postcall_config
    
    def get_audio_download_config(self, call_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Get audio download method and configuration for a call
        
        Returns:
            Tuple of (method_string, config_dict)
        """
        
        method = self.config.postcall_config.audio_download_method
        
        if method == AudioDownloadMethod.SCP:
            scp_config = {
                "timeout_seconds": self.config.postcall_config.download_timeout_seconds,
                "user": self.settings.scp_user,
                "server": self.settings.scp_server,
                "password": self.settings.scp_password,
                "remote_path_template": self.settings.scp_remote_path_template
            }
            return "scp", scp_config
            
        elif method == AudioDownloadMethod.HTTP:
            http_config = {
                "timeout_seconds": self.config.postcall_config.download_timeout_seconds,
                # HTTP-specific config
            }
            return "http", http_config
            
        elif method == AudioDownloadMethod.LOCAL:
            local_config = {
                "timeout_seconds": self.config.postcall_config.download_timeout_seconds,
                # Local filesystem config
            }
            return "local", local_config
            
        else:  # DISABLED
            return "disabled", {}
    
    def create_call_processing_plan(self, call_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive processing plan for a call
        
        Returns:
            Dictionary with complete processing strategy
        """
        
        call_id = call_context.get('call_id', 'unknown')
        
        # Determine processing mode
        processing_mode = self.determine_processing_mode(call_context)
        
        # Get configurations
        realtime_enabled = self.should_enable_realtime_processing(processing_mode, call_context)
        postcall_enabled = self.should_enable_postcall_processing(processing_mode, call_context)
        
        realtime_config = self.get_realtime_config(call_context) if realtime_enabled else None
        postcall_config = self.get_postcall_config(call_context) if postcall_enabled else None
        
        download_method, download_config = self.get_audio_download_config(call_id) if postcall_enabled else ("disabled", {})
        
        processing_plan = {
            "call_id": call_id,
            "processing_mode": processing_mode.value,
            "timestamp": datetime.now().isoformat(),
            
            "realtime_processing": {
                "enabled": realtime_enabled,
                "config": realtime_config.__dict__ if realtime_config else {}
            },
            
            "postcall_processing": {
                "enabled": postcall_enabled,
                "config": postcall_config.__dict__ if postcall_config else {},
                "audio_download": {
                    "method": download_method,
                    "config": download_config
                }
            },
            
            "resource_requirements": {
                "streaming_gpu_needed": realtime_enabled,
                "batch_gpu_needed": postcall_enabled,
                "estimated_realtime_duration": 5.0,  # seconds per window
                "estimated_postcall_duration": 60.0,  # seconds for full processing
            }
        }
        
        logger.info(f"📋 [strategy] Created processing plan for {call_id}: {processing_mode.value}")
        logger.debug(f"📋 [strategy] Plan details: realtime={realtime_enabled}, postcall={postcall_enabled}, download={download_method}")

        return processing_plan

    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive information from data structures for logging/API responses

        Args:
            data: Dictionary that may contain sensitive data

        Returns:
            Sanitized copy of the dictionary
        """
        import copy
        sanitized = copy.deepcopy(data)

        # Sanitize password fields
        if isinstance(sanitized, dict):
            for key, value in sanitized.items():
                if isinstance(value, dict):
                    sanitized[key] = self._sanitize_sensitive_data(value)
                elif key.lower() in ['password', 'passwd', 'pwd', 'secret', 'token', 'api_key']:
                    sanitized[key] = '***REDACTED***'

        return sanitized

    def get_sanitized_processing_plan(self, call_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a processing plan with sensitive data removed for API responses/logging

        Args:
            call_context: Dictionary containing call information

        Returns:
            Sanitized processing plan safe for external exposure
        """
        plan = self.create_call_processing_plan(call_context)
        return self._sanitize_sensitive_data(plan)

    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get current system processing capabilities"""
        return {
            "processing_modes": {
                "available_modes": [mode.value for mode in CallProcessingMode],
                "current_default": self.config.default_mode.value,
                "realtime_enabled": self.config.realtime_config.enabled,
                "postcall_enabled": self.config.postcall_config.enabled
            },
            "audio_download": {
                "available_methods": [method.value for method in AudioDownloadMethod],
                "current_method": self.config.postcall_config.audio_download_method.value,
                "scp_enabled": self.settings.enable_scp_audio_download
            },
            "usage_statistics": self.mode_usage_stats,
            "configuration": {
                "realtime_config": self.config.realtime_config.__dict__,
                "postcall_config": self.config.postcall_config.__dict__,
                "adaptive_rules": self.config.adaptive_rules.__dict__
            }
        }
    
    def update_mode_configuration(self, new_config: Dict[str, Any]) -> bool:
        """
        Update processing mode configuration at runtime
        
        Args:
            new_config: Dictionary with configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update default mode if provided
            if 'default_mode' in new_config:
                mode_str = new_config['default_mode'].lower()
                mode_mapping = {
                    "realtime_only": CallProcessingMode.REALTIME_ONLY,
                    "postcall_only": CallProcessingMode.POSTCALL_ONLY,
                    "hybrid": CallProcessingMode.HYBRID,
                    "adaptive": CallProcessingMode.ADAPTIVE
                }
                if mode_str in mode_mapping:
                    self.config.default_mode = mode_mapping[mode_str]
                    logger.info(f"🎛️ Updated default processing mode to: {mode_str}")
            
            # Update realtime config if provided
            if 'realtime_config' in new_config:
                realtime_updates = new_config['realtime_config']
                for key, value in realtime_updates.items():
                    if hasattr(self.config.realtime_config, key):
                        setattr(self.config.realtime_config, key, value)
                        logger.info(f"🎛️ Updated realtime config {key} = {value}")
            
            # Update postcall config if provided
            if 'postcall_config' in new_config:
                postcall_updates = new_config['postcall_config']
                for key, value in postcall_updates.items():
                    if hasattr(self.config.postcall_config, key):
                        setattr(self.config.postcall_config, key, value)
                        logger.info(f"🎛️ Updated postcall config {key} = {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update mode configuration: {e}")
            return False

# Global strategy manager instance
processing_strategy_manager = ProcessingStrategyManager()