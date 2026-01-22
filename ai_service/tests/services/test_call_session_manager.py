import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import asdict

from app.streaming.call_session_manager import CallSessionManager, CallSession
from app.config.settings import settings

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = Mock()
    redis_mock.hset = Mock()
    redis_mock.hget = Mock()
    redis_mock.sadd = Mock()
    redis_mock.srem = Mock()
    redis_mock.expireat = Mock()
    return redis_mock

@pytest.fixture
def session_manager(mock_redis):
    """Fixture to provide a CallSessionManager instance with mocked Redis"""
    return CallSessionManager(redis_client=mock_redis)

@pytest.fixture
def sample_connection_info():
    """Sample connection info for testing"""
    return {
        "source_ip": "192.168.1.100",
        "source_port": 5060,
        "protocol": "SIP",
        "user_agent": "Asterisk"
    }

@pytest.fixture
def sample_call_session():
    """Sample CallSession for testing"""
    now = datetime.now()
    return CallSession(
        call_id="test_call_123",
        start_time=now,
        last_activity=now,
        connection_info={"source_ip": "192.168.1.100"},
        transcript_segments=[],
        cumulative_transcript="",
        total_audio_duration=0.0,
        segment_count=0,
        status='active'
    )

class TestCallSession:
    """Tests for the CallSession dataclass"""
    
    def test_call_session_initialization(self, sample_call_session):
        """Test CallSession initialization"""
        assert sample_call_session.call_id == "test_call_123"
        assert sample_call_session.status == 'active'
        assert sample_call_session.segment_count == 0
        assert sample_call_session.total_audio_duration == 0.0
        assert len(sample_call_session.transcript_segments) == 0
        assert sample_call_session.cumulative_transcript == ""
    
    def test_to_dict_conversion(self, sample_call_session):
        """Test conversion to dictionary with ISO format dates"""
        result = sample_call_session.to_dict()
        
        assert isinstance(result, dict)
        assert result['call_id'] == "test_call_123"
        assert result['status'] == 'active'
        # Check that dates are converted to ISO format strings
        assert isinstance(result['start_time'], str)
        assert isinstance(result['last_activity'], str)
        # Verify ISO format
        datetime.fromisoformat(result['start_time'])  # Should not raise exception
        datetime.fromisoformat(result['last_activity'])  # Should not raise exception
    
    def test_from_dict_conversion(self, sample_call_session):
        """Test creation from dictionary"""
        # Convert to dict and back
        data = sample_call_session.to_dict()
        restored_session = CallSession.from_dict(data)
        
        assert restored_session.call_id == sample_call_session.call_id
        assert restored_session.status == sample_call_session.status
        assert isinstance(restored_session.start_time, datetime)
        assert isinstance(restored_session.last_activity, datetime)

class TestCallSessionManager:
    """Tests for the CallSessionManager class"""
    
    def test_initialization(self, mock_redis):
        """Test CallSessionManager initialization"""
        manager = CallSessionManager(redis_client=mock_redis)

        assert manager.redis_client == mock_redis
        assert manager.active_sessions == {}
        assert manager.session_timeout == timedelta(minutes=30)
        assert manager.cleanup_interval == settings.cleanup_interval
        assert manager._cleanup_task is None
    
    def test_initialization_without_redis(self):
        """Test initialization without Redis client"""
        with patch('app.streaming.call_session_manager.redis_task_client', None):
            manager = CallSessionManager()
            assert manager.redis_client is None

    @pytest.mark.asyncio
    async def test_start_session_success(self, session_manager, mock_redis, sample_connection_info):
        """Test successful session start"""
        call_id = "test_call_123"

        with patch('app.streaming.call_session_manager.enhanced_notification_service') as mock_notification:
            mock_notification.send_call_start = AsyncMock()

            session = await session_manager.start_session(call_id, sample_connection_info)

        # Verify session creation
        assert session.call_id == call_id
        assert session.status == 'active'
        assert session.connection_info == sample_connection_info
        assert session.segment_count == 0

        # Verify session stored in memory
        assert call_id in session_manager.active_sessions
        assert session_manager.active_sessions[call_id] == session

        # Verify Redis calls
        mock_redis.hset.assert_called()
        mock_redis.expireat.assert_called()
        mock_redis.sadd.assert_called_with('active_call_sessions', call_id)

    @pytest.mark.asyncio
    async def test_add_transcription_success(self, session_manager, sample_call_session):
        """Test successful transcription addition"""
        # Add session to manager
        session_manager.active_sessions[sample_call_session.call_id] = sample_call_session

        transcript = "Hello world"
        audio_duration = 2.5
        metadata = {"confidence": 0.95}

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor, \
             patch('app.streaming.call_session_manager.enhanced_processing_manager') as mock_processing_mgr:
            mock_processor.process_if_ready = AsyncMock(return_value=None)
            mock_processing_mgr.should_enable_streaming = Mock(return_value=False)

            result = await session_manager.add_transcription(
                sample_call_session.call_id,
                transcript,
                audio_duration,
                metadata
            )

        # Verify session was updated
        assert result is not None
        assert result.segment_count == 1
        assert result.total_audio_duration == 2.5
        assert result.cumulative_transcript == "Hello world"
        assert len(result.transcript_segments) == 1

        # Verify segment details
        segment = result.transcript_segments[0]
        assert segment['segment_id'] == 1
        assert segment['transcript'] == "Hello world"
        assert segment['audio_duration'] == 2.5

    @pytest.mark.asyncio
    async def test_add_transcription_no_session(self, session_manager):
        """Test transcription addition when no session exists"""
        result = await session_manager.add_transcription("nonexistent_call", "text", 1.0)
        assert result is None

    @pytest.mark.asyncio
    async def test_add_transcription_with_progressive_processing(self, session_manager, sample_call_session):
        """Test transcription addition with progressive processing"""
        session_manager.active_sessions[sample_call_session.call_id] = sample_call_session

        # Mock progressive processor
        mock_window = Mock()
        mock_window.window_id = "window_1"

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor, \
             patch('app.streaming.call_session_manager.enhanced_processing_manager') as mock_processing_mgr:
            mock_processor.process_if_ready = AsyncMock(return_value=mock_window)
            mock_processing_mgr.should_enable_streaming = Mock(return_value=True)

            result = await session_manager.add_transcription(
                sample_call_session.call_id,
                "Hello world",
                2.5
            )

        # Verify progressive processing metadata was added
        segment = result.transcript_segments[0]
        assert segment['metadata']['progressive_window'] == "window_1"
        assert segment['metadata']['window_processed'] is True

    def test_concatenate_transcript_no_existing(self, session_manager):
        """Test transcript concatenation with no existing text"""
        result = session_manager._concatenate_transcript("", "Hello world")
        assert result == "Hello world"

    def test_concatenate_transcript_no_new(self, session_manager):
        """Test transcript concatenation with no new text"""
        result = session_manager._concatenate_transcript("Hello", "")
        assert result == "Hello"

    def test_concatenate_transcript_no_overlap(self, session_manager):
        """Test transcript concatenation with no overlap"""
        result = session_manager._concatenate_transcript("Hello", "world")
        assert result == "Hello world"

    def test_concatenate_transcript_with_overlap(self, session_manager):
        """Test transcript concatenation with word overlap"""
        existing = "Hello world how"
        new_text = "how are you"
        result = session_manager._concatenate_transcript(existing, new_text)
        assert result == "Hello world how are you"

    def test_concatenate_transcript_full_overlap(self, session_manager):
        """Test transcript concatenation with complete overlap"""
        existing = "Hello world"
        new_text = "world"
        result = session_manager._concatenate_transcript(existing, new_text)
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_get_session_from_memory(self, session_manager, sample_call_session):
        """Test getting session from memory"""
        session_manager.active_sessions[sample_call_session.call_id] = sample_call_session
        
        result = await session_manager.get_session(sample_call_session.call_id)
        assert result == sample_call_session

    @pytest.mark.asyncio
    async def test_get_session_from_redis(self, session_manager, mock_redis, sample_call_session):
        """Test getting session from Redis when not in memory"""
        # Mock Redis to return session data
        session_data = sample_call_session.to_dict()
        mock_redis.hget.return_value = json.dumps(session_data)
        
        result = await session_manager.get_session(sample_call_session.call_id)
        
        assert result is not None
        assert result.call_id == sample_call_session.call_id
        # Verify session was added to memory cache
        assert sample_call_session.call_id in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, session_manager, mock_redis):
        """Test getting non-existent session"""
        mock_redis.hget.return_value = None
        
        result = await session_manager.get_session("nonexistent_call")
        assert result is None

    @pytest.mark.asyncio
    async def test_end_session_success(self, session_manager, sample_call_session):
        """Test successful session ending"""
        session_manager.active_sessions[sample_call_session.call_id] = sample_call_session
        sample_call_session.cumulative_transcript = "This is a substantial transcript with enough content for processing"

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor, \
             patch('app.streaming.call_session_manager.enhanced_processing_manager') as mock_processing_mgr, \
             patch('app.streaming.call_session_manager.enhanced_notification_service') as mock_notification:
            mock_processor.finalize_call_analysis = AsyncMock(return_value=None)
            mock_processing_mgr.should_enable_postcall = Mock(return_value=False)
            mock_notification.send_call_end_streaming = AsyncMock()

            result = await session_manager.end_session(sample_call_session.call_id, "completed")

        # Verify session status updated
        assert result.status == "completed"

        # Verify session removed from active sessions
        assert sample_call_session.call_id not in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_end_session_short_transcript(self, session_manager, sample_call_session):
        """Test ending session with short transcript"""
        session_manager.active_sessions[sample_call_session.call_id] = sample_call_session
        sample_call_session.cumulative_transcript = "Short"  # Under 50 char threshold

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor, \
             patch('app.streaming.call_session_manager.enhanced_processing_manager') as mock_processing_mgr, \
             patch('app.streaming.call_session_manager.enhanced_notification_service') as mock_notification:
            mock_processor.finalize_call_analysis = AsyncMock(return_value=None)
            mock_processing_mgr.should_enable_postcall = Mock(return_value=False)
            mock_notification.send_call_end_streaming = AsyncMock()

            result = await session_manager.end_session(sample_call_session.call_id, "completed")

        # Verify session was ended
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_end_session_not_found(self, session_manager):
        """Test ending non-existent session"""
        result = await session_manager.end_session("nonexistent_call")
        assert result is None

    @pytest.mark.asyncio
    async def test_trigger_ai_pipeline(self, session_manager, sample_call_session, mock_redis):
        """Test AI pipeline triggering"""
        sample_call_session.cumulative_transcript = "This is a test transcript for AI processing"
        
        # Mock the task
        mock_task = Mock()
        mock_task.id = "task_123"
        
        with patch('app.tasks.audio_tasks.process_audio_task') as mock_process_task:
            mock_process_task.delay.return_value = mock_task
            
            await session_manager._trigger_ai_pipeline(sample_call_session)
        
        # Verify task was submitted
        mock_process_task.delay.assert_called_once()
        call_args = mock_process_task.delay.call_args
        
        # Verify parameters
        assert 'audio_bytes' in call_args.kwargs
        assert 'filename' in call_args.kwargs
        assert 'language' in call_args.kwargs
        assert call_args.kwargs['include_translation'] is True
        assert call_args.kwargs['include_insights'] is True
        
        # Verify Redis storage
        mock_redis.hset.assert_called()

    @pytest.mark.asyncio
    async def test_get_all_active_sessions(self, session_manager, sample_call_session):
        """Test getting all active sessions"""
        session_manager.active_sessions["call_1"] = sample_call_session
        session_manager.active_sessions["call_2"] = sample_call_session
        
        result = await session_manager.get_all_active_sessions()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_session_stats(self, session_manager):
        """Test getting session statistics"""
        # Create test sessions
        session1 = Mock()
        session1.total_audio_duration = 10.0
        session1.segment_count = 5
        session1.call_id = "call_1"
        
        session2 = Mock()
        session2.total_audio_duration = 20.0
        session2.segment_count = 8
        session2.call_id = "call_2"
        
        session_manager.active_sessions = {"call_1": session1, "call_2": session2}
        
        stats = await session_manager.get_session_stats()
        
        assert stats['active_sessions'] == 2
        assert stats['total_audio_duration'] == 30.0
        assert stats['total_segments'] == 13
        assert stats['average_duration_per_session'] == 15.0
        assert stats['session_list'] == ["call_1", "call_2"]

    @pytest.mark.asyncio
    async def test_get_session_stats_empty(self, session_manager):
        """Test getting statistics with no active sessions"""
        stats = await session_manager.get_session_stats()
        
        assert stats['active_sessions'] == 0
        assert stats['total_audio_duration'] == 0
        assert stats['total_segments'] == 0
        assert stats['average_duration_per_session'] == 0
        assert stats['session_list'] == []

    def test_store_session_in_redis(self, session_manager, mock_redis, sample_call_session):
        """Test storing session in Redis"""
        session_manager._store_session_in_redis(sample_call_session)
        
        # Verify Redis calls
        mock_redis.hset.assert_called()
        mock_redis.expireat.assert_called()
        mock_redis.sadd.assert_called_with('active_call_sessions', sample_call_session.call_id)

    def test_store_session_in_redis_no_client(self, sample_call_session):
        """Test storing session without Redis client"""
        manager = CallSessionManager(redis_client=None)
        
        # Should not raise exception, just log warning
        manager._store_session_in_redis(sample_call_session)

    def test_get_session_from_redis(self, session_manager, mock_redis, sample_call_session):
        """Test retrieving session from Redis"""
        session_data = sample_call_session.to_dict()
        mock_redis.hget.return_value = json.dumps(session_data)
        
        result = session_manager._get_session_from_redis(sample_call_session.call_id)
        
        assert result is not None
        assert result['call_id'] == sample_call_session.call_id
        mock_redis.hget.assert_called_with(f"call_session:{sample_call_session.call_id}", 'data')

    def test_get_session_from_redis_no_data(self, session_manager, mock_redis):
        """Test retrieving non-existent session from Redis"""
        mock_redis.hget.return_value = None
        
        result = session_manager._get_session_from_redis("nonexistent_call")
        assert result is None

    def test_get_session_from_redis_no_client(self, sample_call_session):
        """Test retrieving session without Redis client"""
        manager = CallSessionManager(redis_client=None)
        
        result = manager._get_session_from_redis(sample_call_session.call_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_cleanup_inactive_sessions(self, session_manager, mock_redis):
        """Test cleanup of inactive sessions"""
        # Create old session
        old_time = datetime.now() - timedelta(hours=1)
        old_session = Mock()
        old_session.call_id = "old_call"
        old_session.last_activity = old_time
        
        # Create recent session
        recent_session = Mock()
        recent_session.call_id = "recent_call"
        recent_session.last_activity = datetime.now()
        
        session_manager.active_sessions = {
            "old_call": old_session,
            "recent_call": recent_session
        }
        
        with patch.object(session_manager, 'end_session', new_callable=AsyncMock) as mock_end:
            await session_manager._cleanup_inactive_sessions()
        
        # Verify only old session was ended
        mock_end.assert_called_once_with("old_call", reason="timeout")

    @pytest.mark.asyncio
    async def test_periodic_cleanup_cancellation(self, session_manager):
        """Test periodic cleanup task cancellation"""
        # Start the cleanup task
        session_manager._cleanup_task = asyncio.create_task(session_manager._periodic_cleanup())
        
        # Cancel it immediately
        session_manager._cleanup_task.cancel()
        
        # Wait for cancellation
        with pytest.raises(asyncio.CancelledError):
            await session_manager._cleanup_task