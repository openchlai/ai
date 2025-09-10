from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os
from pathlib import Path
import redis

class Settings(BaseSettings):
    # Application
    app_name: str = "AI Pipeline"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Resource Management
    max_concurrent_gpu_requests: int = 1
    max_queue_size: int = 20
    request_timeout: int = 300
    queue_monitor_interval: int = 30
    
    # Model Configuration
    model_cache_size: int = 8192
    cleanup_interval: int = 3600
    enable_model_loading: bool = True
    
    # Security
    site_id: str = "unknown-site"
    data_retention_hours: int = 24
    
    # Performance
    enable_queue_metrics: bool = True
    alert_queue_size: int = 15
    alert_memory_usage: int = 90
    
    # Paths - Use environment variables with sensible defaults
    models_path: str = "./models"
    logs_path: str = "./logs"
    temp_path: str = "./temp"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_task_db: int = 1
    redis_streaming_db: int = 2
    redis_streaming_channel_prefix: str = "ai_streaming"
    
    enable_streaming: bool = False
    max_streaming_slots: int = 2
    max_batch_slots: int = 1  
    streaming_port: int = 8300
    streaming_host: str = "0.0.0.0"
    
    # Whisper Model Configuration
    whisper_streaming_model: str = "base"
    whisper_batch_model: str = "large-v3"
    
    # Agent Notification Configuration
    asterisk_server_ip: str = "192.168.10.119"
    
    # Docker detection
    docker_container: bool = False
    
    # Processing Mode Configuration
    default_processing_mode: str = "hybrid"  # realtime_only, postcall_only, hybrid, adaptive
    enable_realtime_processing: bool = True
    enable_postcall_processing: bool = True
    enable_scp_audio_download: bool = True
    
    # Real-time Processing Configuration
    realtime_min_window_chars: int = 150
    realtime_target_window_chars: int = 300
    realtime_overlap_chars: int = 50
    realtime_processing_interval_seconds: int = 30
    realtime_enable_progressive_translation: bool = True
    realtime_enable_progressive_entities: bool = True
    realtime_enable_progressive_classification: bool = True
    realtime_enable_agent_notifications: bool = True
    
    # Post-call Processing Configuration
    postcall_audio_download_method: str = "scp"  # scp, http, local, disabled
    postcall_enable_full_pipeline: bool = True
    postcall_enable_enhanced_transcription: bool = True
    postcall_enable_audio_quality_improvement: bool = True
    postcall_whisper_model: str = "large-v3"
    postcall_enable_diarization: bool = False
    postcall_enable_noise_reduction: bool = True
    postcall_download_timeout_seconds: int = 60
    postcall_convert_to_wav: bool = True
    postcall_enable_insights_generation: bool = True
    postcall_enable_qa_scoring: bool = True
    postcall_enable_summarization: bool = True
    postcall_notify_completion: bool = True
    postcall_send_unified_insights: bool = True
    
    # Adaptive Processing Rules
    adaptive_short_call_threshold_seconds: int = 30
    adaptive_long_call_threshold_seconds: int = 600
    adaptive_high_priority_keywords: str = "emergency,urgent,critical,suicide,violence,accident,medical,police,fire,ambulance"
    
    # SCP Audio Download Configuration
    scp_user: str = "helpline"
    scp_server: str = "192.168.10.3"
    scp_password: str = "h3lpl1n3"
    scp_remote_path_template: str = "/home/dat/helpline/calls/{call_id}.gsm"
    scp_timeout_seconds: int = 30
    
    # Whisper Model Configuration
    whisper_model_variant: str = "large_v3"  # large_v3, large_turbo
    translation_strategy: str = "whisper_builtin"  # whisper_builtin, custom_model
    whisper_large_v3_path: str = "./models/whisper_large_v3"
    whisper_large_turbo_path: str = "./models/whisper_large_turbo"
    whisper_active_symlink: str = "./models/whisper"  # Symlink for backward compatibility
    
    # Agent Notification Configuration
    enable_agent_notifications: bool = True
    notification_mode: str = "results_only"  # all, results_only, critical_only, disabled
    notification_endpoint_url: str = "https://192.168.10.3/hh5aug2025/api/msg/"
    notification_auth_endpoint_url: str = "https://192.168.10.3/hh5aug2025/api/"
    notification_basic_auth: str = "dGVzdDpwQHNzdzByZA=="  # Base64 encoded
    notification_request_timeout: int = 10
    notification_max_retries: int = 3
    
    def get_model_path(self, model_name: str) -> str:
        """Get absolute path for a model"""
        return os.path.join(self.models_path, model_name)
    
    def get_active_whisper_path(self) -> str:
        """Get path to the currently active whisper model"""
        if self.whisper_model_variant == "large_v3":
            return os.path.abspath(self.whisper_large_v3_path)
        elif self.whisper_model_variant == "large_turbo":
            return os.path.abspath(self.whisper_large_turbo_path)
        else:
            # Fallback to symlink path
            return os.path.abspath(self.whisper_active_symlink)
    
    def get_processing_mode_config(self) -> Dict[str, Any]:
        """Get complete processing mode configuration as dictionary"""
        return {
            "default_mode": self.default_processing_mode,
            "realtime_processing": {
                "enabled": self.enable_realtime_processing,
                "min_window_chars": self.realtime_min_window_chars,
                "target_window_chars": self.realtime_target_window_chars,
                "overlap_chars": self.realtime_overlap_chars,
                "processing_interval_seconds": self.realtime_processing_interval_seconds,
                "enable_progressive_translation": self.realtime_enable_progressive_translation,
                "enable_progressive_entities": self.realtime_enable_progressive_entities,
                "enable_progressive_classification": self.realtime_enable_progressive_classification,
                "enable_agent_notifications": self.realtime_enable_agent_notifications
            },
            "postcall_processing": {
                "enabled": self.enable_postcall_processing,
                "audio_download_method": self.postcall_audio_download_method,
                "enable_full_pipeline": self.postcall_enable_full_pipeline,
                "enable_enhanced_transcription": self.postcall_enable_enhanced_transcription,
                "enable_audio_quality_improvement": self.postcall_enable_audio_quality_improvement,
                "whisper_model": self.postcall_whisper_model,
                "enable_diarization": self.postcall_enable_diarization,
                "enable_noise_reduction": self.postcall_enable_noise_reduction,
                "download_timeout_seconds": self.postcall_download_timeout_seconds,
                "convert_to_wav": self.postcall_convert_to_wav,
                "enable_insights_generation": self.postcall_enable_insights_generation,
                "enable_qa_scoring": self.postcall_enable_qa_scoring,
                "enable_summarization": self.postcall_enable_summarization,
                "notify_completion": self.postcall_notify_completion,
                "send_unified_insights": self.postcall_send_unified_insights,
                "scp_audio_download": self.enable_scp_audio_download
            },
            "adaptive_rules": {
                "short_call_threshold_seconds": self.adaptive_short_call_threshold_seconds,
                "long_call_threshold_seconds": self.adaptive_long_call_threshold_seconds,
                "high_priority_keywords": self.adaptive_high_priority_keywords.split(",")
            }
        }
    
    def initialize_paths(self):
        """Initialize paths - called explicitly, not at import time"""
        # Auto-detect Docker environment
        self.docker_container = os.getenv("DOCKER_CONTAINER") is not None or os.path.exists("/.dockerenv")
        
        # Auto-detect paths based on environment
        if self.docker_container:
            # Docker environment: use /app paths
            if self.models_path == "./models":
                self.models_path = "/app/models"
            if self.logs_path == "./logs":
                self.logs_path = "/app/logs"
            if self.temp_path == "./temp":
                self.temp_path = "/app/temp"
            print("🐳 Docker environment detected - using /app paths")
        else:
            # Local development: use relative paths
            print("💻 Local development environment detected - using relative paths")
        
        # Convert to absolute paths
        self.models_path = os.path.abspath(self.models_path)
        self.logs_path = os.path.abspath(self.logs_path)
        self.temp_path = os.path.abspath(self.temp_path)
        
        # Create directories if they don't exist
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        
        # Debug output
        print(f"📁 Models path: {self.models_path}")
        print(f"📁 Models exists: {os.path.exists(self.models_path)}")
        print(f"🔧 Environment: {'Docker' if self.docker_container else 'Local'}")
        
        return self.models_path
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Initialize settings (but don't call path initialization at import time)
settings = Settings()

# Redis clients with error handling - but don't connect at import time
redis_client = None
redis_task_client = None

def get_redis_url():
    """Get Redis URL with Docker detection"""
    if os.getenv("DOCKER_CONTAINER") or os.path.exists("/.dockerenv"):
        return os.getenv("REDIS_URL", "redis://redis:6379/0")
    else:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

def initialize_redis():
    """Initialize Redis connections - called explicitly when needed"""
    global redis_client, redis_task_client
    
    try:
        redis_url = get_redis_url()
        redis_client = redis.from_url(redis_url)
        redis_task_client = redis.from_url(f"{redis_url.rsplit('/', 1)[0]}/{settings.redis_task_db}")
        
        # Test connection
        redis_client.ping()
        print(f"✅ Redis connected: {redis_url}")
        return True
        
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        redis_client = None
        redis_task_client = None
        return False