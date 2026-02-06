"""
Application Configuration Settings

This module defines all configuration settings for the AI Pipeline service.
Settings are loaded from environment variables (via .env file) using Pydantic Settings.

Configuration Categories:
- Application: Core app settings (name, version, port, logging)
- Database: Database connection settings
- Resource Management: GPU/CPU resource limits and monitoring
- Model Configuration: Model loading and caching settings
- Security: Site identification and data retention policies
- Redis: Redis connection and database configuration
- Streaming: Real-time streaming configuration
- Whisper Models: Whisper model variants and paths
- HuggingFace: HuggingFace Hub integration and model IDs
- Processing Modes: Real-time, post-call, and adaptive processing
- SCP Audio Download: Secure file transfer settings
- Agent Notifications: Notification endpoint configuration

Environment Variable Override:
All settings can be overridden using environment variables. Pydantic Settings will automatically
map environment variables to settings (case-insensitive). For example:
  - app_name → APP_NAME
  - redis_url → REDIS_URL
  - enable_model_loading → ENABLE_MODEL_LOADING

Docker vs Local:
The system auto-detects Docker environments and adjusts paths accordingly:
  - Local: Uses relative paths (./models, ./logs, ./temp)
  - Docker: Uses absolute paths (/app/models, /app/logs, /app/temp)
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
import os
import redis


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Use Field() with descriptions and validation for better documentation and safety.
    """

    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================

    DATABASE_URL: str = Field(
        default="sqlite:///./ai_service.db",
        description="Database connection URL (SQLite, PostgreSQL, etc.)"
    )

    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================

    app_name: str = Field(
        default="AI Pipeline",
        description="Application name displayed in logs and health checks"
    )

    app_version: str = Field(
        default="0.1.0",
        description="Application version"
    )

    app_port: int = Field(
        default=8125,
        ge=1024,
        le=65535,
        description="FastAPI server port"
    )

    debug: bool = Field(
        default=True,
        description="Enable debug mode (verbose logging, detailed error messages)"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # ============================================================================
    # RESOURCE MANAGEMENT
    # ============================================================================

    max_concurrent_gpu_requests: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Maximum concurrent GPU tasks to prevent out-of-memory errors"
    )

    max_queue_size: int = Field(
        default=20,
        ge=1,
        description="Maximum number of tasks in processing queue"
    )

    request_timeout: int = Field(
        default=300,
        ge=10,
        description="Request timeout in seconds"
    )

    queue_monitor_interval: int = Field(
        default=30,
        ge=5,
        description="Interval in seconds for monitoring queue health"
    )

    # ============================================================================
    # MODEL CONFIGURATION 
    # ============================================================================

    cleanup_interval: int = Field(
        default=300,
        ge=60,
        description="Cleanup interval in seconds for session management"
    )

    enable_model_loading: bool = Field(
        default=True,
        description="Enable local model loading (set to false in API server mode)"
    )

    ollama_model: str = Field(
        # default="mistral",
        default="ai-service",
        description="Ollama model name for insights generation"
    )

    # ============================================================================
    # SECURITY & DATA RETENTION
    # ============================================================================

    site_id: str = Field(
        default="unknown-site",
        description="Site identifier for multi-tenant deployments"
    )

    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================

    enable_queue_metrics: bool = Field(
        default=True,
        description="Enable queue performance metrics collection"
    )

    alert_queue_size: int = Field(
        default=15,
        ge=1,
        description="Queue size threshold for alerts"
    )

    alert_memory_usage: int = Field(
        default=90,
        ge=50,
        le=100,
        description="Memory usage percentage threshold for alerts"
    )

    # ============================================================================
    # FILE PATHS
    # ============================================================================

    models_path: str = Field(
        default="./models",
        description="Path to model files (auto-adjusted for Docker)"
    )

    logs_path: str = Field(
        default="./logs",
        description="Path to log files (auto-adjusted for Docker)"
    )

    temp_path: str = Field(
        default="./temp",
        description="Path to temporary files (auto-adjusted for Docker)"
    )

    # ============================================================================
    # HUGGINGFACE HUB CONFIGURATION
    # ============================================================================

    hf_token: Optional[str] = Field(
        default=None,
        description="HuggingFace API token for private model access"
    )

    use_hf_models: bool = Field(
        default=True,
        description="Use HuggingFace Hub models instead of local models"
    )

    hf_organization: str = Field(
        default="openchs",
        description="HuggingFace organization name for model repository"
    )

    # HuggingFace Model IDs - must be provided via environment variables
    hf_asr_model: str = Field(
        default="",
        description="HuggingFace model ID for automatic speech recognition (Whisper)"
    )

    hf_classifier_model: str = Field(
        default="",
        description="HuggingFace model ID for call classification"
    )

    hf_ner_model: str = Field(
        default="",
        description="HuggingFace model ID for named entity recognition"
    )

    hf_translator_model: str = Field(
        default="",
        description="HuggingFace model ID for translation"
    )

    hf_summarizer_model: str = Field(
        default="",
        description="HuggingFace model ID for summarization"
    )

    hf_qa_model: str = Field(
        default="",
        description="HuggingFace model ID for question answering"
    )

    # ============================================================================
    # REDIS CONFIGURATION
    # ============================================================================

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for main database"
    )

    redis_task_db: int = Field(
        default=1,
        ge=0,
        le=15,
        description="Redis database number for Celery task results"
    )

    redis_streaming_db: int = Field(
        default=2,
        ge=0,
        le=15,
        description="Redis database number for streaming session data"
    )

    redis_streaming_channel_prefix: str = Field(
        default="ai_streaming",
        description="Prefix for Redis pub/sub channels used in streaming"
    )

    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format"""
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError("Redis URL must start with redis:// or rediss://")
        return v

    # ============================================================================
    # STREAMING CONFIGURATION
    # ============================================================================

    enable_streaming: bool = Field(
        default=False,
        description="Enable real-time streaming processing"
    )

    max_streaming_slots: int = Field(
        default=2,
        ge=1,
        description="Maximum concurrent streaming sessions"
    )

    max_batch_slots: int = Field(
        default=1,
        ge=1,
        description="Maximum concurrent batch processing jobs"
    )

    streaming_port: int = Field(
        default=8300,
        ge=1024,
        le=65535,
        description="TCP port for streaming server"
    )

    streaming_host: str = Field(
        default="0.0.0.0",
        description="Host address for streaming server"
    )

    streaming_transcription_interval: int = Field(
        default=5,
        ge=1,
        description="Interval in seconds for streaming transcription updates"
    )

    streaming_translation_interval: int = Field(
        default=30,
        ge=5,
        description="Interval in seconds for streaming translation updates"
    )

    streaming_entity_update_interval: int = Field(
        default=30,
        ge=5,
        description="Interval in seconds for streaming entity extraction updates"
    )

    streaming_classification_update_interval: int = Field(
        default=30,
        ge=5,
        description="Interval in seconds for streaming classification updates"
    )


    # ============================================================================
    # PROCESSING MODE CONFIGURATION
    # ============================================================================

    default_processing_mode: str = Field(
        default="dual",
        description="Default processing mode: streaming, post_call, dual, or adaptive"
    )

    enable_streaming_processing: bool = Field(
        default=True,
        description="Enable streaming processing capability"
    )

    enable_postcall_processing: bool = Field(
        default=True,
        description="Enable post-call processing capability"
    )

    enable_scp_audio_download: bool = Field(
        default=True,
        description="Enable SCP-based audio file download"
    )

    # ============================================================================
    # REAL-TIME PROCESSING CONFIGURATION
    # ============================================================================

    realtime_min_window_chars: int = Field(
        default=150,
        ge=50,
        description="Minimum characters in text window for real-time analysis"
    )

    realtime_target_window_chars: int = Field(
        default=300,
        ge=100,
        description="Target characters in text window for real-time analysis"
    )

    realtime_overlap_chars: int = Field(
        default=50,
        ge=0,
        description="Character overlap between consecutive windows"
    )

    realtime_processing_interval_seconds: int = Field(
        default=30,
        ge=5,
        description="Interval in seconds for real-time processing cycles"
    )

    realtime_enable_progressive_translation: bool = Field(
        default=True,
        description="Enable progressive translation during real-time processing"
    )

    realtime_enable_progressive_entities: bool = Field(
        default=True,
        description="Enable progressive entity extraction during real-time processing"
    )

    realtime_enable_progressive_classification: bool = Field(
        default=True,
        description="Enable progressive classification during real-time processing"
    )

    realtime_enable_agent_notifications: bool = Field(
        default=True,
        description="Enable agent notifications during real-time processing"
    )

    # ============================================================================
    # POST-CALL PROCESSING CONFIGURATION
    # ============================================================================

    postcall_audio_download_method: str = Field(
        default="scp",
        description="Audio download method: scp, http, local, or disabled"
    )

    postcall_enable_full_pipeline: bool = Field(
        default=True,
        description="Enable full processing pipeline for post-call analysis"
    )

    postcall_enable_enhanced_transcription: bool = Field(
        default=True,
        description="Enable enhanced transcription with better model for post-call"
    )

    postcall_enable_audio_quality_improvement: bool = Field(
        default=True,
        description="Enable audio quality enhancement before transcription"
    )

    postcall_whisper_model: str = Field(
        default="large-v3",
        description="Whisper model to use for post-call transcription"
    )

    postcall_enable_diarization: bool = Field(
        default=False,
        description="Enable speaker diarization (who spoke when)"
    )

    postcall_enable_noise_reduction: bool = Field(
        default=True,
        description="Enable noise reduction preprocessing"
    )

    postcall_download_timeout_seconds: int = Field(
        default=60,
        ge=10,
        description="Timeout in seconds for audio file download"
    )

    postcall_convert_to_wav: bool = Field(
        default=True,
        description="Convert audio to WAV format before processing"
    )

    postcall_enable_insights: bool = Field(
        default=True,
        description="Enable insights generation for post-call analysis"
    )

    postcall_enable_qa_scoring: bool = Field(
        default=True,
        description="Enable QA scoring for post-call analysis"
    )

    postcall_enable_summary: bool = Field(
        default=True,
        description="Enable summary generation for post-call analysis"
    )

    postcall_processing_timeout: int = Field(
        default=300,
        ge=60,
        description="Timeout in seconds for post-call processing"
    )

    postcall_notify_completion: bool = Field(
        default=True,
        description="Send notification when post-call processing completes"
    )

    postcall_send_unified_insights: bool = Field(
        default=True,
        description="Send unified insights notification after post-call processing"
    )

    # ============================================================================
    # ADAPTIVE PROCESSING RULES
    # ============================================================================

    adaptive_short_call_threshold: int = Field(
        default=30,
        ge=10,
        description="Short call threshold in seconds for adaptive mode"
    )

    adaptive_long_call_threshold: int = Field(
        default=600,
        ge=60,
        description="Long call threshold in seconds for adaptive mode"
    )

    adaptive_high_priority_keywords: str = Field(
        default="emergency,urgent,critical,suicide,violence,abuse",
        description="Comma-separated list of high-priority keywords for adaptive mode"
    )

    # ============================================================================
    # SCP AUDIO DOWNLOAD CONFIGURATION
    # ============================================================================

    scp_user: str = Field(
        default="helpline",
        description="SSH/SCP username for audio file downloads"
    )

    scp_server: str = Field(
        default="192.168.10.3",
        description="SSH/SCP server hostname or IP address"
    )

    scp_password: str = Field(
        default="h3lpl1n3",
        description="SSH/SCP password (consider using key-based auth in production)"
    )

    scp_remote_path_template: str = Field(
        default="/home/dat/helpline/calls/{call_id}.gsm",
        description="Remote file path template with {call_id} placeholder"
    )

    scp_timeout_seconds: int = Field(
        default=30,
        ge=5,
        description="SCP connection timeout in seconds"
    )

    # ============================================================================
    # AGENT NOTIFICATION CONFIGURATION
    # ============================================================================

    enable_agent_notifications: bool = Field(
        default=True,
        description="Enable agent notification system"
    )

    notification_mode: str = Field(
        default="results_only",
        description="Notification mode: results_only, progressive, or disabled"
    )

    notification_endpoint_url: str = Field(
        default="https://192.168.10.3/hh5aug2025/api/msg/",
        description="HTTP endpoint URL for sending notifications"
    )

    notification_auth_endpoint_url: str = Field(
        default="https://192.168.10.3/hh5aug2025/api/",
        description="HTTP endpoint URL for authentication"
    )

    notification_basic_auth: str = Field(
        default="dGVzdDpwQHNzdzByZA==",
        description="Base64-encoded basic auth credentials (username:password)"
    )

    notification_request_timeout: int = Field(
        default=10,
        ge=1,
        description="HTTP request timeout in seconds for notifications"
    )

    notification_max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts for failed notifications"
    )

    notification_retry_delay: int = Field(
        default=2,
        ge=1,
        description="Delay in seconds between notification retry attempts"
    )

    notification_version: str = Field(
        default="2.0",
        description="Notification API version"
    )

    use_base64_encoding: bool = Field(
        default=False,
        description="Use base64 encoding for notification payloads"
    )

    enable_ui_metadata: bool = Field(
        default=True,
        description="Include UI-specific metadata in notifications"
    )

    notification_batch_size: int = Field(
        default=1,
        ge=1,
        description="Batch size for notification sending (future feature)"
    )

    notification_auth_token: str = Field(
        default="default_token",
        description="Authentication token for notification endpoints"
    )

    # ============================================================================
    # ASTERISK SERVER CONFIGURATION
    # ============================================================================

    asterisk_server_ip: str = Field(
        default="192.168.10.119",
        description="Asterisk PBX server IP address"
    )

    # ============================================================================
    # AGENT PAYLOAD LOGGING (DEVELOPMENT)
    # ============================================================================

    enable_agent_payload_logging: bool = Field(
        default=False,
        description="Enable logging of all notification payloads for UI development"
    )

    agent_payload_log_file: str = Field(
        default="./logs/agent_payloads.jsonl",
        description="Path to agent payload log file (JSONL format)"
    )

    # ============================================================================
    # DOCKER DETECTION
    # ============================================================================

    docker_container: bool = Field(
        default=False,
        description="Indicates if running in Docker container (auto-detected)"
    )

    # ============================================================================
    # MOCK/DEBUG AUDIO SETTINGS
    # ============================================================================

    mock_enabled: bool = Field(
        default=False,
        description="Enable mock mode for local testing without Asterisk server"
    )

    mock_audio_folder: str = Field(
        default="./test_audio",
        description="Path to folder containing test audio files for mock mode"
    )

    mock_use_folder_files: bool = Field(
        default=True,
        description="When call_id file not found, use any available file from folder"
    )

    mock_skip_scp_download: bool = Field(
        default=True,
        description="Skip SCP download and use local files when mock_enabled is True"
    )

    mock_notifications: bool = Field(
        default=False,
        description="Write notifications to markdown files instead of sending to server"
    )

    mock_notifications_folder: str = Field(
        default="./mock_notifications",
        description="Folder for mock notification markdown files"
    )

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def get_model_path(self, model_name: str) -> str:
        """
        Get absolute path for a model.

        Args:
            model_name: Name of the model subdirectory

        Returns:
            Absolute path to the model directory
        """
        return os.path.join(self.models_path, model_name)

    def _get_hf_model_id(self, model_name: str) -> str:
        """
        Get HuggingFace model ID for a given model name.

        Args:
            model_name: Model name (e.g., 'classifier', 'ner', 'translator')

        Returns:
            HuggingFace model ID
        """
        model_id_map = {
            "classifier": self.hf_classifier_model,
            "ner": self.hf_ner_model,
            "translator": self.hf_translator_model,
            "summarizer": self.hf_summarizer_model,
            "qa": self.hf_qa_model
        }

        model_id = model_id_map.get(model_name, "")

        if not model_id and self.hf_organization:
            model_id = f"{self.hf_organization}/{model_name.replace('_', '-')}"

        return model_id

    def get_hf_model_kwargs(self) -> Dict[str, Any]:
        """
        Get common kwargs for HuggingFace model loading with authentication.

        Returns:
            Dictionary with 'token' key if hf_token is configured
        """
        kwargs = {}
        if self.hf_token:
            kwargs["token"] = self.hf_token
        return kwargs

    def get_translator_model_id(self) -> str:
        """
        Return the HuggingFace translator model ID from configuration.
        Falls back to a sensible ID built from hf_organization if not set.

        Returns:
            HuggingFace translator model ID
        """
        if self.hf_translator_model:
            return self.hf_translator_model
        return self._get_hf_model_id("translator")

    def get_processing_mode_config(self) -> Dict[str, Any]:
        """
        Get complete processing mode configuration as dictionary.

        Returns:
            Dictionary containing all processing mode settings organized by category
        """
        return {
            "default_mode": self.default_processing_mode,
            "realtime_processing": {
                "enabled": self.enable_streaming_processing,
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
                "enable_insights_generation": self.postcall_enable_insights,
                "enable_qa_scoring": self.postcall_enable_qa_scoring,
                "enable_summarization": self.postcall_enable_summary,
                "notify_completion": self.postcall_notify_completion,
                "send_unified_insights": self.postcall_send_unified_insights,
                "scp_audio_download": self.enable_scp_audio_download
            },
            "adaptive_rules": {
                "short_call_threshold_seconds": self.adaptive_short_call_threshold,
                "long_call_threshold_seconds": self.adaptive_long_call_threshold,
                "high_priority_keywords": self.adaptive_high_priority_keywords.split(",")
            }
        }

    def initialize_paths(self):
        """
        Initialize paths - called explicitly, not at import time.
        Detects Docker environment and adjusts paths accordingly.
        Creates necessary directories if they don't exist.

        Returns:
            Absolute path to models directory
        """
        self.docker_container = os.getenv("DOCKER_CONTAINER") is not None or os.path.exists("/.dockerenv")

        if self.docker_container:
            if self.models_path == "./models":
                self.models_path = "/app/models"
            if self.logs_path == "./logs":
                self.logs_path = "/app/logs"
            if self.temp_path == "./temp":
                self.temp_path = "/app/temp"
            print("Docker environment detected - using /app paths")
        else:
            print("Local development environment detected - using relative paths")

        self.models_path = os.path.abspath(self.models_path)
        self.logs_path = os.path.abspath(self.logs_path)
        self.temp_path = os.path.abspath(self.temp_path)

        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)

        print(f"Models path: {self.models_path}")
        print(f"Models exists: {os.path.exists(self.models_path)}")
        print(f"Environment: {'Docker' if self.docker_container else 'Local'}")

        return self.models_path

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"  # Allow extra fields to prevent validation errors
    )


# ============================================================================
# MODULE-LEVEL INSTANCES
# ============================================================================

# Global settings instance - imported throughout the application
settings = Settings()

# Global Redis client instances - initialized explicitly when needed
redis_client = None
redis_task_client = None


# ============================================================================
# REDIS INITIALIZATION HELPERS
# ============================================================================

def get_redis_url():
    """
    Get Redis URL with Docker detection.

    Returns:
        Redis URL appropriate for the current environment
    """
    if os.getenv("DOCKER_CONTAINER") or os.path.exists("/.dockerenv"):
        return os.getenv("REDIS_URL", "redis://redis:6379/0")
    else:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")


def initialize_redis():
    """
    Initialize Redis connections - called explicitly when needed.
    Creates connections to both main Redis and task result Redis databases.

    Returns:
        True if connection successful, False otherwise
    """
    global redis_client, redis_task_client

    try:
        redis_url = get_redis_url()
        redis_client = redis.from_url(redis_url)
        redis_task_client = redis.from_url(f"{redis_url.rsplit('/', 1)[0]}/{settings.redis_task_db}")

        redis_client.ping()
        print(f"Redis connected: {redis_url}")
        return True

    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None
        redis_task_client = None
        return False
