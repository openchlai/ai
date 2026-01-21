

import pytest
import os
from unittest.mock import patch, MagicMock
from app.config.settings import Settings, get_redis_url, initialize_redis

class TestSettings:
    

    def test_default_values(self):
        """Test that default values are set correctly"""
        # Pass _env_file=None to ignore local .env file and test code defaults
        settings = Settings(_env_file=None)
        assert settings.app_name == "AI Pipeline"
        assert settings.app_port == 8125
        # Field is defined as DATABASE_URL
        assert settings.DATABASE_URL == "sqlite:///./ai_service.db"
        assert settings.log_level == "INFO"
        assert settings.debug is True
        
    def test_redis_url_validation(self):
        """Test valid and invalid Redis URLs"""
        # Valid URLs
        s1 = Settings(redis_url="redis://localhost:6379/0")
        assert s1.redis_url == "redis://localhost:6379/0"
        
        s2 = Settings(redis_url="rediss://localhost:6379/0")
        assert s2.redis_url == "rediss://localhost:6379/0"
        
        # Invalid URL
        with pytest.raises(ValueError, match="Redis URL must start with"):
            Settings(redis_url="http://localhost:6379/0")

    def test_get_hf_model_id(self):
        """Test internal method for resolving HF model IDs"""
        settings = Settings()
        # Test specific mapping when model ID is set
        settings.hf_classifier_model = "my-classifier"
        assert settings._get_hf_model_id("classifier") == "my-classifier"
        
        # Test fallback to organization/model-name
        settings.hf_translator_model = ""
        settings.hf_organization = "my-org"
        # The code does: model_id = f"{self.hf_organization}/{model_name.replace('_', '-')}"
        assert settings._get_hf_model_id("translator") == "my-org/translator"
        
        # Test fallback with underscores replaced
        assert settings._get_hf_model_id("some_model") == "my-org/some_model".replace("_", "-")

    def test_get_translator_model_id(self):
        """Test helper for translator model ID"""
        settings = Settings()
        settings.hf_translator_model = "specific-translator"
        assert settings.get_translator_model_id() == "specific-translator"
        
        settings.hf_translator_model = ""
        settings.hf_organization = "test-org"
        assert settings.get_translator_model_id() == "test-org/translator"

    def test_get_hf_model_kwargs(self):
        """Test HF kwargs generation"""
        settings = Settings()
        settings.hf_token = "secret-token"
        assert settings.get_hf_model_kwargs() == {"token": "secret-token"}
        
        settings.hf_token = None
        assert settings.get_hf_model_kwargs() == {}

    def test_get_processing_mode_config(self):
        """Test exporting processing mode configuration"""
        settings = Settings()
        config = settings.get_processing_mode_config()
        
        assert "default_mode" in config
        assert "realtime_processing" in config
        assert "postcall_processing" in config
        assert "adaptive_rules" in config
        
        assert config["default_mode"] == settings.default_processing_mode
        assert config["realtime_processing"]["enabled"] == settings.enable_streaming_processing
        assert config["postcall_processing"]["audio_download_method"] == settings.postcall_audio_download_method
        assert config["adaptive_rules"]["short_call_threshold_seconds"] == settings.adaptive_short_call_threshold

    def test_initialize_paths_local(self):
        """Test path initialization for local environment"""
        settings = Settings()
        original_models_path = "./models"
        settings.models_path = original_models_path
        
        # Mock os.environ to ensure no DOCKER_CONTAINER var and os.path.exists to not find .dockerenv
        # Also mock os.makedirs to avoid creating directories
        with patch.dict(os.environ, {}, clear=True), \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs") as mock_makedirs:
            
            settings.initialize_paths()
            
            # Should stay relative/local but be abspath'd
            expected = os.path.abspath(original_models_path)
            assert settings.models_path == expected
            assert not settings.docker_container
            assert mock_makedirs.called

    def test_initialize_paths_docker(self):
        """Test path initialization for Docker environment"""
        settings = Settings()
        settings.models_path = "./models"
        settings.logs_path = "./logs"
        settings.temp_path = "./temp"
        
        # Simulate docker env via valid DOCKER_CONTAINER env var
        # Mock os.makedirs to prevent PermissionError on /app
        with patch.dict(os.environ, {"DOCKER_CONTAINER": "true"}), \
             patch("os.makedirs") as mock_makedirs:
            
            settings.initialize_paths()
            
            assert settings.models_path == "/app/models"
            assert settings.logs_path == "/app/logs"
            assert settings.temp_path == "/app/temp"
            assert settings.docker_container
            assert mock_makedirs.called

    def test_env_var_overrides(self):
        """Test that environment variables override defaults"""
        # Note: Pydantic BaseSettings reads env vars at instantiation.
        # We need to patch os.environ BEFORE creating the instance.
        with patch.dict(os.environ, {"APP_PORT": "9000", "DEBUG": "false", "REQUEST_TIMEOUT": "60"}):
            settings = Settings()
            assert settings.app_port == 9000
            assert settings.debug is False
            assert settings.request_timeout == 60

class TestModuleFunctions:
    
    def test_get_redis_url(self):
        """Test get_redis_url in local and docker scenarios"""
        
        # Local
        with patch.dict(os.environ, {}, clear=True), \
             patch("os.path.exists", return_value=False):
            assert get_redis_url() == "redis://localhost:6379/0"
            
        # Docker
        with patch.dict(os.environ, {"DOCKER_CONTAINER": "true"}):
            assert get_redis_url() == "redis://redis:6379/0"
            
        # Manual override
        with patch.dict(os.environ, {"REDIS_URL": "redis://custom:6379/0"}):
            assert get_redis_url() == "redis://custom:6379/0"

    def test_initialize_redis_success(self):
        """Test successful Redis initialization"""
        with patch("app.config.settings.redis.from_url") as mock_from_url:
            mock_client = MagicMock()
            mock_from_url.return_value = mock_client
            
            assert initialize_redis() is True
            assert mock_client.ping.called
            
    def test_initialize_redis_failure(self):
        """Test Redis initialization failure"""
        with patch("app.config.settings.redis.from_url") as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")
            
            assert initialize_redis() is False

