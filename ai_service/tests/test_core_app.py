import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestSettings:
    """Test settings configuration"""

    def test_settings_initialization(self):
        """Test settings can be imported and initialized"""
        from app.config.settings import settings
        
        assert settings is not None
        assert hasattr(settings, 'get_model_path')

    def test_get_model_path_default(self):
        """Test getting model path with default implementation"""
        from app.config.settings import settings
        
        # Test that method exists and returns something
        result = settings.get_model_path("test_model")
        assert isinstance(result, str)

    def test_settings_attributes(self):
        """Test that settings has expected attributes"""
        from app.config.settings import settings
        
        # Test common settings attributes exist
        expected_attrs = ['app_version', 'site_id']
        for attr in expected_attrs:
            assert hasattr(settings, attr), f"Settings missing attribute: {attr}"

class TestCeleryApp:
    """Test Celery application configuration"""

    def test_celery_app_import(self):
        """Test that celery app can be imported"""
        with patch('celery.Celery') as mock_celery:
            mock_celery.return_value = MagicMock()
            from app.celery_app import celery_app
            assert celery_app is not None

    def test_celery_app_configuration(self):
        """Test celery app has basic configuration"""
        with patch('celery.Celery') as mock_celery:
            mock_instance = MagicMock()
            mock_celery.return_value = mock_instance
            
            from app.celery_app import celery_app
            
            # Verify Celery was instantiated
            mock_celery.assert_called_once()

class TestModelLoader:
    """Test model loader functionality"""

    def test_model_loader_import(self):
        """Test that model loader can be imported"""
        from app.model_scripts.model_loader import ModelLoader
        
        loader = ModelLoader()
        assert loader is not None

    def test_model_loader_initialization(self):
        """Test model loader initialization"""
        from app.model_scripts.model_loader import ModelLoader
        
        loader = ModelLoader()
        assert hasattr(loader, 'models')
        assert isinstance(loader.models, dict)

    def test_available_libraries(self):
        """Test that library availability is tracked"""
        from app.model_scripts.model_loader import AVAILABLE_LIBRARIES
        
        assert isinstance(AVAILABLE_LIBRARIES, dict)
        # Should have some common libraries
        expected_libs = ['torch', 'transformers', 'spacy']
        for lib in expected_libs:
            if lib in AVAILABLE_LIBRARIES:
                assert isinstance(AVAILABLE_LIBRARIES[lib], str)  # Version string

class TestResourceManager:
    """Test resource manager functionality"""

    def test_unified_resource_manager_import(self):
        """Test that unified resource manager can be imported"""
        from app.core.resource_manager import UnifiedResourceManager
        
        rm = UnifiedResourceManager()
        assert rm is not None

    def test_resource_manager_initialization(self):
        """Test resource manager initialization"""
        from app.core.resource_manager import UnifiedResourceManager
        
        rm = UnifiedResourceManager(max_streaming_slots=2, max_batch_slots=1)
        assert rm.max_streaming_slots == 2
        assert rm.max_batch_slots == 1

    def test_resource_manager_status(self):
        """Test resource manager status method"""
        from app.core.resource_manager import UnifiedResourceManager
        
        rm = UnifiedResourceManager()
        status = rm.get_resource_status()
        
        assert isinstance(status, dict)
        assert 'streaming' in status
        assert 'batch' in status

class TestTextChunker:
    """Test text chunker functionality"""

    def test_text_chunker_import(self):
        """Test that text chunker can be imported"""
        from app.core.text_chunker import IntelligentTextChunker
        
        chunker = IntelligentTextChunker()
        assert chunker is not None

    def test_text_chunker_initialization(self):
        """Test text chunker initialization"""
        from app.core.text_chunker import IntelligentTextChunker
        
        chunker = IntelligentTextChunker()
        assert hasattr(chunker, 'chunk_configs')
        assert len(chunker.chunk_configs) > 0

    def test_chunk_config_classes(self):
        """Test chunk configuration classes"""
        from app.core.text_chunker import ChunkConfig, TextChunk
        
        config = ChunkConfig(max_tokens=512, overlap_tokens=50, min_chunk_tokens=10)
        assert config.max_tokens == 512
        
        chunk = TextChunk(
            text="Test text",
            start_pos=0,
            end_pos=9,
            chunk_id=0,
            token_count=2,
            sentence_count=1
        )
        assert chunk.text == "Test text"

class TestStreamingComponents:
    """Test streaming components"""

    def test_audio_buffer_import(self):
        """Test that audio buffer can be imported"""
        from app.streaming.audio_buffer import AsteriskAudioBuffer
        
        buffer = AsteriskAudioBuffer()
        assert buffer is not None

    def test_tcp_server_import(self):
        """Test that TCP server can be imported"""
        from app.streaming.tcp_server import AsteriskTCPServer
        
        server = AsteriskTCPServer()
        assert server is not None

    def test_tcp_server_status(self):
        """Test TCP server status method"""
        from app.streaming.tcp_server import AsteriskTCPServer
        
        server = AsteriskTCPServer()
        status = server.get_status()
        
        assert isinstance(status, dict)
        assert 'server_running' in status
        assert 'active_connections' in status

class TestAudioTasks:
    """Test audio processing tasks"""

    @patch('app.tasks.audio_tasks.model_loader')
    def test_audio_tasks_import(self, mock_loader):
        """Test that audio tasks can be imported"""
        from app.tasks.audio_tasks import process_streaming_audio_task
        
        assert process_streaming_audio_task is not None

    def test_task_helper_functions(self):
        """Test task helper functions"""
        with patch('app.tasks.audio_tasks.tempfile'), \
             patch('soundfile.write'):
            from app.tasks.audio_tasks import _save_audio_bytes_to_temp_file
            
            # Test that function exists and can be called
            result = _save_audio_bytes_to_temp_file(b"fake_audio", 16000)
            assert isinstance(result, str)

@pytest.mark.skip(reason="AgentNotificationService has been deprecated and replaced with EnhancedNotificationService")
class TestAgentNotificationService:
    """Test agent notification service (DEPRECATED)"""

    def test_agent_service_import(self):
        """Test that agent service can be imported"""
        with patch('requests.post'):
            from app.services.agent_notification_service import AgentNotificationService
            
            service = AgentNotificationService()
            assert service is not None

    def test_agent_service_initialization(self):
        """Test agent service initialization"""
        with patch('requests.post'), \
             patch('app.services.agent_notification_service.settings') as mock_settings:
            
            mock_settings.AGENT_WEBHOOK_URL = "http://test.com"
            mock_settings.AGENT_API_KEY = "test_key"
            
            from app.services.agent_notification_service import AgentNotificationService
            
            service = AgentNotificationService()
            assert service.webhook_url == "http://test.com"

class TestMainApp:
    """Test main FastAPI application"""

    def test_main_app_creation(self):
        """Test that main app can be created"""
        with patch('app.main.lifespan'), \
             patch('app.api.audio_routes.router'), \
             patch('app.api.health_routes.router'):
            
            from app.main import create_app
            
            app = create_app()
            assert app is not None

    def test_cors_configuration(self):
        """Test CORS configuration"""
        with patch('app.main.lifespan'), \
             patch('app.api.audio_routes.router'), \
             patch('app.api.health_routes.router'), \
             patch('fastapi.middleware.cors.CORSMiddleware'):
            
            from app.main import create_app
            
            app = create_app()
            # Just test that app can be created with CORS
            assert app is not None

class TestIntegration:
    """Test integration between components"""

    def test_component_integration(self):
        """Test that major components can work together"""
        # Test that we can import all major components together
        from app.config.settings import settings
        from app.model_scripts.model_loader import ModelLoader
        from app.core.resource_manager import UnifiedResourceManager
        from app.core.text_chunker import IntelligentTextChunker
        
        # Test basic interaction
        loader = ModelLoader()
        rm = UnifiedResourceManager()
        chunker = IntelligentTextChunker()
        
        assert loader is not None
        assert rm is not None
        assert chunker is not None
        assert settings is not None

    def test_model_types_available(self):
        """Test that all expected model types are available"""
        expected_models = [
            'classifier_model',
            'ner_model', 
            'summarizer_model',
            'whisper_model',
            'translator_model',
            'qa_model'
        ]
        
        for model_name in expected_models:
            try:
                # Try to import each model
                if model_name == 'classifier_model':
                    from app.model_scripts.classifier_model import ClassifierModel
                elif model_name == 'ner_model':
                    from app.model_scripts.ner_model import NERModel
                elif model_name == 'summarizer_model':
                    from app.model_scripts.summarizer_model import SummarizationModel
                elif model_name == 'whisper_model':
                    from app.model_scripts.whisper_model import WhisperModel
                elif model_name == 'translator_model':
                    from app.model_scripts.translator_model import TranslationModel
                elif model_name == 'qa_model':
                    from app.model_scripts.qa_model import QAModel
                
                # If we get here, import succeeded
                assert True
            except ImportError:
                pytest.fail(f"Failed to import {model_name}")

    def test_task_registration(self):
        """Test that Celery tasks are properly registered"""
        with patch('celery.Celery') as mock_celery:
            mock_instance = MagicMock()
            mock_celery.return_value = mock_instance
            
            from app.celery_app import celery_app
            from app.tasks.audio_tasks import process_streaming_audio_task
            
            # Verify tasks exist
            assert process_streaming_audio_task is not None
            assert celery_app is not None