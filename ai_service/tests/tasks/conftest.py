"""
Pytest configuration for tasks testing module.
Shared fixtures and test configurations for Celery tasks.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime


# ===== CELERY TASK FIXTURES =====

@pytest.fixture
def mock_celery_app():
    """Fixture for mocked Celery app"""
    celery = MagicMock()
    celery.send_task = MagicMock(return_value=MagicMock(id="test_task_id"))
    celery.AsyncResult = MagicMock(return_value=MagicMock(
        state="SUCCESS",
        result={"status": "completed"},
        id="test_task_id"
    ))
    return celery


@pytest.fixture
def mock_task_context():
    """Mock Celery task context - used for @task.request access"""
    task = MagicMock()
    task.request.id = "test-task-123"
    task.request.hostname = "worker.local"
    task.update_state = MagicMock()
    task.name = "app.tasks.audio_tasks.process_audio_task"
    return task


@pytest.fixture
def celery_task_context(mock_task_context):
    """Provides task context with proper mock for Celery task execution"""
    with patch('app.celery_app.celery_app') as mock_celery:
        mock_celery.current_task = mock_task_context
        yield mock_task_context


# ===== REDIS/BROKER FIXTURES =====

@pytest.fixture
def mock_redis_connection():
    """Fixture for mocked Redis connection"""
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.flushdb = AsyncMock(return_value=True)
    redis.hset = AsyncMock(return_value=1)
    redis.hget = AsyncMock(return_value=None)
    redis.hgetall = AsyncMock(return_value={})
    redis.expire = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_broker_connection():
    """Fixture for mocked Celery broker connection"""
    broker = MagicMock()
    broker.connection_error = None
    broker.is_connected = True
    broker.ping.return_value = True
    return broker


@pytest.fixture
def mock_result_backend():
    """Fixture for mocked Celery result backend"""
    backend = MagicMock()
    backend.get = MagicMock(return_value={"status": "success"})
    backend.set = MagicMock(return_value=True)
    backend.delete = MagicMock(return_value=True)
    return backend


# ===== MODEL LOADER FIXTURES =====

@pytest.fixture
def mock_worker_model_loader():
    """Fixture for mocked worker model loader (used in tasks)"""
    loader = MagicMock()

    # Mock model availability
    loader.models = {
        "whisper": MagicMock(name="whisper_model"),
        "translator": MagicMock(name="translator_model"),
        "ner": MagicMock(name="ner_model"),
        "classifier_model": MagicMock(name="classifier_model"),
        "summarizer": MagicMock(name="summarizer_model"),
        "qa": MagicMock(name="qa_model"),
    }

    # Mock model status methods
    loader.is_model_ready = MagicMock(return_value=True)
    loader.get_ready_models = MagicMock(return_value=list(loader.models.keys()))
    loader.get_failed_models = MagicMock(return_value=[])
    loader.get_model_info = MagicMock(return_value={"status": "ready"})

    # Configure specific model behaviors
    loader.models["whisper"].transcribe_audio_bytes = MagicMock(return_value={
        "text": "Test transcript",
        "segments": [{"start": 0, "end": 5, "text": "Test transcript"}]
    })

    loader.models["translator"].translate = MagicMock(return_value="Translated text")

    loader.models["ner"].extract_entities = MagicMock(return_value={
        "PERSON": ["John"],
        "ORG": ["Acme"]
    })

    loader.models["classifier_model"].classify = MagicMock(return_value={
        "main_category": "general",
        "sub_category": "general",
        "confidence": 0.95,
        "priority": "low"
    })

    loader.models["summarizer"].summarize = MagicMock(return_value="Summary of test")

    loader.models["qa"].evaluate = MagicMock(return_value={
        "overall_score": 0.85,
        "categories": {}
    })

    return loader


@pytest.fixture
def mock_model_loader():
    """Fixture for mocked API server model loader (when enable_model_loading=False)"""
    loader = MagicMock()
    loader.is_model_ready = MagicMock(return_value=False)  # Models not loaded in API server
    loader.get_ready_models = MagicMock(return_value=[])
    loader.models = {}
    return loader


# ===== AUDIO/FILE FIXTURES =====

@pytest.fixture
def sample_audio_bytes():
    """Fixture for sample audio bytes (WAV format)"""
    # Minimal valid WAV file header + some audio data
    wav_header = b'RIFF'  # Chunk ID
    wav_header += (36).to_bytes(4, 'little')  # Chunk size
    wav_header += b'WAVE'  # Format
    wav_header += b'fmt '  # Subchunk1 ID
    wav_header += (16).to_bytes(4, 'little')  # Subchunk1 size
    wav_header += (1).to_bytes(2, 'little')  # Audio format (PCM)
    wav_header += (1).to_bytes(2, 'little')  # Num channels
    wav_header += (16000).to_bytes(4, 'little')  # Sample rate
    wav_header += (32000).to_bytes(4, 'little')  # Byte rate
    wav_header += (2).to_bytes(2, 'little')  # Block align
    wav_header += (16).to_bytes(2, 'little')  # Bits per sample
    wav_header += b'data'  # Subchunk2 ID
    wav_header += (0).to_bytes(4, 'little')  # Subchunk2 size
    return wav_header


@pytest.fixture
def sample_audio_chunk():
    """Fixture for sample audio chunk (20ms of silence)"""
    return b'\x00' * 640


# ===== INSIGHTS/NOTIFICATION FIXTURES =====

@pytest.fixture
def mock_insights_service():
    """Fixture for mocked insights service"""
    insights = AsyncMock()
    insights.generate_case_insights = AsyncMock(return_value={
        "summary": "Test insights",
        "key_themes": ["test"],
        "recommendations": ["Test recommendation"]
    })
    insights.extract_case_metadata = AsyncMock(return_value={
        "case_id": "test_case",
        "persons_involved": ["John"]
    })
    return insights


@pytest.fixture
def mock_notification_service():
    """Fixture for mocked notification service"""
    notifications = AsyncMock()
    notifications.send_notification = AsyncMock(return_value=True)
    notifications.send_streaming_transcription = AsyncMock(return_value=True)
    notifications.send_streaming_entities = AsyncMock(return_value=True)
    notifications.send_streaming_classification = AsyncMock(return_value=True)
    notifications.send_postcall_complete = AsyncMock(return_value=True)
    notifications.send_error_notification = AsyncMock(return_value=True)
    return notifications


@pytest.fixture
def mock_call_session_manager():
    """Fixture for mocked call session manager"""
    manager = AsyncMock()
    manager.create_session = AsyncMock(return_value="session_123")
    manager.get_session = AsyncMock(return_value={
        "session_id": "session_123",
        "status": "active"
    })
    manager.update_session = AsyncMock(return_value=True)
    manager.end_session = AsyncMock(return_value=True)
    manager.publish_update = AsyncMock(return_value=True)
    manager.store_result = AsyncMock(return_value=True)
    return manager


@pytest.fixture
def mock_text_chunker():
    """Fixture for mocked text chunker"""
    chunker = MagicMock()
    chunker.chunk_text = MagicMock(return_value=[
        MagicMock(text="Chunk 1", token_count=10),
        MagicMock(text="Chunk 2", token_count=8)
    ])
    chunker.chunk_and_aggregate = MagicMock(return_value={
        "aggregated_result": "Test result",
        "confidence": 0.95
    })
    return chunker


# ===== RESOURCE MANAGEMENT FIXTURES =====

@pytest.fixture
def mock_resource_manager():
    """Fixture for mocked resource manager"""
    resources = MagicMock()
    resources.get_gpu_info = MagicMock(return_value={
        "available_memory": 8000,
        "used_memory": 2000,
        "total_memory": 10000,
        "utilization": 20
    })
    resources.get_system_info = MagicMock(return_value={
        "cpu_percent": 30,
        "memory_percent": 40,
        "disk_percent": 50
    })
    resources.acquire_gpu = MagicMock(return_value=True)
    resources.release_gpu = MagicMock(return_value=True)
    resources.is_gpu_available = MagicMock(return_value=True)
    return resources


# ===== AUTO-USE FIXTURES =====

@pytest.fixture(autouse=True)
def patch_celery_tasks(monkeypatch, mock_worker_model_loader):
    """Auto-patch Celery tasks and model loaders for all tests in this module"""
    # Patch worker model loader
    monkeypatch.setattr(
        'app.tasks.audio_tasks.worker_model_loader',
        mock_worker_model_loader
    )
    monkeypatch.setattr(
        'app.tasks.model_tasks.worker_model_loader',
        mock_worker_model_loader
    )

    # Patch Redis connection
    monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379/0')


@pytest.fixture(autouse=True)
def patch_async_fixtures():
    """Auto-patch AsyncMock to properly handle coroutines"""
    # This ensures AsyncMock coroutines are properly awaited
    import asyncio

    original_coroutine = asyncio.iscoroutine

    def patched_iscoroutine(obj):
        # Treat AsyncMock return values as coroutines
        if isinstance(obj, AsyncMock) or hasattr(obj, '_mock_name'):
            return False
        return original_coroutine(obj)

    yield  # Tests run here
    # Cleanup is not needed for this patch
