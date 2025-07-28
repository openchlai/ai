from pydantic_settings import BaseSettings
from typing import Optional
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
    
    # Docker detection
    docker_container: bool = False
    
    def get_model_path(self, model_name: str) -> str:
        """Get absolute path for a model"""
        return os.path.join(self.models_path, model_name)
    
    def initialize_paths(self):
        """Initialize paths - called explicitly, not at import time"""
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
        
        return self.models_path
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Initialize settings (but don't call path initialization at import time)
settings = Settings()

# Redis clients with error handling - but don't connect at import time
redis_client = None
redis_task_client = None

def initialize_redis():
    """Initialize Redis connections - called explicitly when needed"""
    global redis_client, redis_task_client
    
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_task_client = redis.from_url(f"{settings.redis_url.rsplit('/', 1)[0]}/{settings.redis_task_db}")
        
        # Test connection
        redis_client.ping()
        print(f"✅ Redis connected: {settings.redis_url}")
        return True
        
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        redis_client = None
        redis_task_client = None
        return False