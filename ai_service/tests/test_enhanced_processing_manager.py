import pytest
from unittest.mock import MagicMock, patch
from app.core.enhanced_processing_manager import EnhancedProcessingManager, EnhancedProcessingMode
from app.config.settings import Settings

@pytest.fixture
def mock_settings():
    """Fixture to mock settings for testing."""
    mock = MagicMock(spec=Settings)
    mock.default_processing_mode = "dual"
    mock.enable_streaming_processing = True
    mock.enable_postcall_processing = True
    mock.adaptive_short_call_threshold = 30
    mock.adaptive_long_call_threshold = 600
    mock.adaptive_high_priority_keywords = "emergency,urgent,critical,suicide,violence,abuse"
    mock.streaming_transcription_interval = 5
    mock.streaming_translation_interval = 30
    mock.streaming_entity_update_interval = 30
    mock.streaming_classification_update_interval = 30
    mock.postcall_enable_insights = True
    mock.postcall_enable_qa_scoring = True
    mock.postcall_enable_summary = True
    mock.postcall_processing_timeout = 300
    mock.notification_version = "2.0"
    mock.site_id = "test_site"
    mock.enable_ui_metadata = True
    mock.notification_endpoint_url = "http://test-notification-url.com"
    mock.notification_auth_endpoint_url = "http://test-auth-url.com"
    mock.notification_basic_auth = "test_basic_auth"
    mock.use_base64_encoding = False
    mock.notification_request_timeout = 10
    return mock

@pytest.fixture
def manager(mock_settings):
    """Fixture to create an EnhancedProcessingManager instance with mocked settings."""
    with patch('app.core.enhanced_processing_manager.settings', new=mock_settings):
        yield EnhancedProcessingManager()

def test_initialization(manager):
    """Test that the manager initializes correctly."""
    assert manager.mode_stats == {mode.value: 0 for mode in EnhancedProcessingMode}

def test_determine_mode_default_dual(manager):
    """Test default mode determination when no adaptive rules apply."""
    call_context = {"call_id": "test_call_1"}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.DUAL
    assert manager.mode_stats[EnhancedProcessingMode.DUAL.value] == 1

def test_determine_mode_override(manager):
    """Test mode determination with an explicit override."""
    call_context = {"call_id": "test_call_2", "mode_override": "streaming"}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.STREAMING
    assert manager.mode_stats[EnhancedProcessingMode.STREAMING.value] == 1

def test_determine_mode_adaptive_short_call(manager, mock_settings):
    """Test adaptive mode for a short call."""
    mock_settings.default_processing_mode = "adaptive"
    call_context = {"call_id": "test_call_3", "duration_seconds": 15}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.STREAMING
    assert manager.mode_stats[EnhancedProcessingMode.STREAMING.value] == 1

def test_determine_mode_adaptive_long_call(manager, mock_settings):
    """Test adaptive mode for a long call."""
    mock_settings.default_processing_mode = "adaptive"
    call_context = {"call_id": "test_call_4", "duration_seconds": 700}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.POST_CALL
    assert manager.mode_stats[EnhancedProcessingMode.POST_CALL.value] == 1

def test_determine_mode_adaptive_high_priority(manager, mock_settings):
    """Test adaptive mode for a high priority call."""
    mock_settings.default_processing_mode = "adaptive"
    call_context = {"call_id": "test_call_5", "priority": "high"}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.DUAL
    assert manager.mode_stats[EnhancedProcessingMode.DUAL.value] == 1

def test_determine_mode_adaptive_high_complexity(manager, mock_settings):
    """Test adaptive mode for a high complexity call."""
    mock_settings.default_processing_mode = "adaptive"
    call_context = {"call_id": "test_call_6", "complexity": "high"}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.DUAL
    assert manager.mode_stats[EnhancedProcessingMode.DUAL.value] == 1

def test_determine_mode_adaptive_high_priority_keyword(manager, mock_settings):
    """Test adaptive mode for a call with a high priority keyword in transcript."""
    mock_settings.default_processing_mode = "adaptive"
    call_context = {"call_id": "test_call_7", "transcript": "This is an emergency situation."}
    mode = manager.determine_mode(call_context)
    assert mode == EnhancedProcessingMode.DUAL
    assert manager.mode_stats[EnhancedProcessingMode.DUAL.value] == 1

def test_should_enable_streaming(manager, mock_settings):
    """Test should_enable_streaming logic."""
    assert manager.should_enable_streaming(EnhancedProcessingMode.STREAMING) is True
    assert manager.should_enable_streaming(EnhancedProcessingMode.DUAL) is True
    assert manager.should_enable_streaming(EnhancedProcessingMode.POST_CALL) is False

    mock_settings.enable_streaming_processing = False
    assert manager.should_enable_streaming(EnhancedProcessingMode.STREAMING) is False
    assert manager.should_enable_streaming(EnhancedProcessingMode.DUAL) is False

def test_should_enable_postcall(manager, mock_settings):
    """Test should_enable_postcall logic."""
    assert manager.should_enable_postcall(EnhancedProcessingMode.POST_CALL) is True
    assert manager.should_enable_postcall(EnhancedProcessingMode.DUAL) is True
    assert manager.should_enable_postcall(EnhancedProcessingMode.STREAMING) is False

    mock_settings.enable_postcall_processing = False
    assert manager.should_enable_postcall(EnhancedProcessingMode.POST_CALL) is False
    assert manager.should_enable_postcall(EnhancedProcessingMode.DUAL) is False

def test_get_processing_config(manager):
    """Test retrieval of processing configuration."""
    config = manager.get_processing_config(EnhancedProcessingMode.DUAL)
    assert config["mode"] == "dual"
    assert config["streaming_enabled"] is True
    assert config["postcall_enabled"] is True
    assert config["streaming_config"] is not None
    assert config["postcall_config"] is not None
    assert config["streaming_config"]["transcription_interval"] == 5

    config_streaming = manager.get_processing_config(EnhancedProcessingMode.STREAMING)
    assert config_streaming["streaming_enabled"] is True
    assert config_streaming["postcall_enabled"] is False
    assert config_streaming["postcall_config"] is None

def test_get_mode_statistics(manager):
    """Test mode statistics tracking."""
    manager.determine_mode({"call_id": "stat_call_1", "mode_override": "streaming"})
    manager.determine_mode({"call_id": "stat_call_2", "mode_override": "post_call"})
    manager.determine_mode({"call_id": "stat_call_3", "mode_override": "dual"})
    
    stats = manager.get_mode_statistics()
    assert stats[EnhancedProcessingMode.STREAMING.value] == 1
    assert stats[EnhancedProcessingMode.POST_CALL.value] == 1
    assert stats[EnhancedProcessingMode.DUAL.value] == 1
