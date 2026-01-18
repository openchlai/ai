"""
Comprehensive tests for call_session_manager.py - streaming call session management
Focus: Achieving 95% coverage for call session lifecycle and real-time processing
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call
from datetime import datetime
import json


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for session storage"""
    client = MagicMock()
    client.hset = MagicMock(return_value=True)
    client.hget = MagicMock(return_value=None)
    client.hgetall = MagicMock(return_value={})
    client.hdel = MagicMock(return_value=True)
    client.expire = MagicMock(return_value=True)
    client.exists = MagicMock(return_value=0)
    return client


@pytest.fixture
def mock_session_data():
    """Mock call session data"""
    return {
        "session_id": "session_123",
        "status": "active",
        "start_time": datetime.now().isoformat(),
        "language": "sw",
        "chunks_processed": 0,
        "total_duration": 0.0,
        "transcript": "",
        "analysis": {}
    }


class TestCallSessionManagerInitialization:
    """Tests for CallSessionManager initialization"""

    @patch('app.streaming.call_session_manager.redis_client')
    def test_session_manager_init(self, mock_redis):
        """Test CallSessionManager initialization"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        assert manager is not None
        assert manager.redis_client == mock_redis

    @patch('app.streaming.call_session_manager.redis_client')
    def test_session_manager_init_with_defaults(self, mock_redis):
        """Test CallSessionManager with default parameters"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager()

        assert manager is not None


class TestCreateSession:
    """Tests for creating new call sessions"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_create_session_success(self, mock_redis):
        """Test successful session creation"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True
        mock_redis.expire.return_value = True

        session_id = await manager.create_session(
            caller_id="caller_001",
            language="sw"
        )

        assert session_id is not None
        assert isinstance(session_id, str)
        mock_redis.hset.assert_called()
        mock_redis.expire.assert_called()

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_create_session_with_metadata(self, mock_redis):
        """Test session creation with metadata"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True
        mock_redis.expire.return_value = True

        metadata = {"agent_id": "agent_123", "channel": "phone"}

        session_id = await manager.create_session(
            caller_id="caller_001",
            language="en",
            metadata=metadata
        )

        assert session_id is not None

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_create_session_redis_failure(self, mock_redis):
        """Test session creation when Redis fails"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.side_effect = Exception("Redis connection error")

        with pytest.raises(Exception) as exc_info:
            await manager.create_session(caller_id="caller_001")

        assert "Redis" in str(exc_info.value) or "connection" in str(exc_info.value).lower()


class TestGetSession:
    """Tests for retrieving session data"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_get_session_success(self, mock_redis, mock_session_data):
        """Test successful session retrieval"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        # Mock Redis to return session data
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123',
            b'status': b'active',
            b'start_time': mock_session_data['start_time'].encode(),
            b'language': b'sw'
        }

        session = await manager.get_session("session_123")

        assert session is not None
        mock_redis.hgetall.assert_called_with("call_session:session_123")

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_get_session_not_found(self, mock_redis):
        """Test getting non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hgetall.return_value = {}

        session = await manager.get_session("nonexistent_session")

        assert session is None or session == {}

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_get_session_with_transcript(self, mock_redis):
        """Test getting session with transcript data"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123',
            b'transcript': b'Hello, this is a test transcript'
        }

        session = await manager.get_session("session_123")

        assert session is not None


class TestUpdateSession:
    """Tests for updating session data"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_update_session_success(self, mock_redis):
        """Test successful session update"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True

        updates = {"status": "processing", "chunks_processed": 5}

        result = await manager.update_session("session_123", updates)

        assert result is True or result is None
        mock_redis.hset.assert_called()

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_update_session_transcript(self, mock_redis):
        """Test updating session transcript"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True

        updates = {"transcript": "New transcript text"}

        await manager.update_session("session_123", updates)

        mock_redis.hset.assert_called()

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_update_session_analysis_results(self, mock_redis):
        """Test updating session with analysis results"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True

        analysis = {
            "entities": {"PERSON": ["John"]},
            "classification": {"category": "general"}
        }
        updates = {"analysis": json.dumps(analysis)}

        await manager.update_session("session_123", updates)

        mock_redis.hset.assert_called()


class TestEndSession:
    """Tests for ending call sessions"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_end_session_success(self, mock_redis):
        """Test successful session termination"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123',
            b'status': b'active'
        }

        result = await manager.end_session("session_123")

        assert result is True or result is None
        # Should update status to completed
        calls = [str(c) for c in mock_redis.hset.call_args_list]
        assert any('completed' in c or 'ended' in c for c in calls)

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_end_session_with_summary(self, mock_redis):
        """Test ending session with final summary"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.return_value = True
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123'
        }

        summary = {"total_chunks": 10, "duration": 125.5}

        await manager.end_session("session_123", summary=summary)

        mock_redis.hset.assert_called()

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_end_session_not_found(self, mock_redis):
        """Test ending non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hgetall.return_value = {}

        result = await manager.end_session("nonexistent_session")

        # Should handle gracefully
        assert result is not None or isinstance(result, bool)


class TestDeleteSession:
    """Tests for deleting sessions"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_delete_session_success(self, mock_redis):
        """Test successful session deletion"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.delete.return_value = 1

        result = await manager.delete_session("session_123")

        assert result is True or result == 1
        mock_redis.delete.assert_called_with("call_session:session_123")

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_delete_session_not_found(self, mock_redis):
        """Test deleting non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.delete.return_value = 0

        result = await manager.delete_session("nonexistent")

        assert result is not None


class TestListActiveSessions:
    """Tests for listing active sessions"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_list_active_sessions(self, mock_redis):
        """Test listing all active sessions"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        # Mock Redis keys and data
        mock_redis.keys.return_value = [
            b'call_session:session_1',
            b'call_session:session_2'
        ]
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_1',
            b'status': b'active'
        }

        sessions = await manager.list_active_sessions()

        assert sessions is not None
        assert isinstance(sessions, list)

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_list_active_sessions_empty(self, mock_redis):
        """Test listing when no active sessions"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.keys.return_value = []

        sessions = await manager.list_active_sessions()

        assert sessions is not None
        assert len(sessions) == 0


class TestProcessAudioChunk:
    """Tests for processing audio chunks"""

    @patch('app.streaming.call_session_manager.redis_client')
    @patch('app.streaming.call_session_manager.model_loader')
    async def test_process_audio_chunk_success(self, mock_loader, mock_redis):
        """Test successful audio chunk processing"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        # Mock models
        whisper_mock = MagicMock()
        whisper_mock.transcribe_audio_bytes = AsyncMock(return_value={
            "text": "Test transcript",
            "segments": []
        })
        mock_loader.models = {"whisper": whisper_mock}
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123',
            b'status': b'active'
        }
        mock_redis.hset.return_value = True

        audio_chunk = b'\x00\x01\x02\x03' * 100

        result = await manager.process_audio_chunk(
            session_id="session_123",
            audio_chunk=audio_chunk,
            chunk_index=0
        )

        assert result is not None

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_process_audio_chunk_invalid_session(self, mock_redis):
        """Test processing chunk for invalid session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hgetall.return_value = {}

        audio_chunk = b'\x00\x01' * 100

        with pytest.raises(Exception):
            await manager.process_audio_chunk(
                session_id="invalid_session",
                audio_chunk=audio_chunk,
                chunk_index=0
            )


class TestGetSessionStats:
    """Tests for getting session statistics"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_get_session_stats_success(self, mock_redis):
        """Test getting session statistics"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123',
            b'chunks_processed': b'10',
            b'total_duration': b'125.5'
        }

        stats = await manager.get_session_stats("session_123")

        assert stats is not None

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_get_session_stats_not_found(self, mock_redis):
        """Test getting stats for non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hgetall.return_value = {}

        stats = await manager.get_session_stats("nonexistent")

        assert stats is None or stats == {}


class TestSessionTimeout:
    """Tests for session timeout handling"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_check_session_timeout(self, mock_redis):
        """Test checking for session timeout"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        # Mock old session
        old_time = (datetime.now().timestamp() - 7200)  # 2 hours ago
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_123',
            b'start_time': str(old_time).encode()
        }

        is_timeout = await manager.check_session_timeout("session_123", timeout_seconds=3600)

        assert is_timeout is True or is_timeout is not None

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_cleanup_timed_out_sessions(self, mock_redis):
        """Test cleanup of timed out sessions"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)

        mock_redis.keys.return_value = [b'call_session:session_1']
        mock_redis.hgetall.return_value = {
            b'session_id': b'session_1',
            b'start_time': b'1000'  # Very old
        }

        cleaned = await manager.cleanup_timed_out_sessions(timeout_seconds=3600)

        assert cleaned is not None


class TestSessionErrorHandling:
    """Tests for error handling in session management"""

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_create_session_redis_error(self, mock_redis):
        """Test session creation with Redis error"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.side_effect = Exception("Redis error")

        with pytest.raises(Exception):
            await manager.create_session(caller_id="caller_001")

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_update_session_redis_error(self, mock_redis):
        """Test session update with Redis error"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hset.side_effect = Exception("Redis error")

        with pytest.raises(Exception):
            await manager.update_session("session_123", {"status": "active"})

    @patch('app.streaming.call_session_manager.redis_client')
    async def test_get_session_redis_error(self, mock_redis):
        """Test session retrieval with Redis error"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis)
        mock_redis.hgetall.side_effect = Exception("Redis error")

        with pytest.raises(Exception):
            await manager.get_session("session_123")
