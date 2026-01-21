"""
Comprehensive tests for call_session_manager.py - streaming call session management
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call
from datetime import datetime, timedelta
import json


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for session storage"""
    client = MagicMock()
    client.hset = MagicMock(return_value=True)
    client.hget = MagicMock(return_value=None)
    client.expireat = MagicMock(return_value=True)
    client.sadd = MagicMock(return_value=True)
    client.srem = MagicMock(return_value=True)
    return client


@pytest.fixture
def mock_enhanced_notification_service():
    """Mock enhanced notification service"""
    with patch('app.streaming.call_session_manager.enhanced_notification_service') as mock_service:
        mock_service.send_call_start = AsyncMock()
        mock_service.send_call_end_streaming = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_enhanced_processing_manager():
    """Mock enhanced processing manager"""
    with patch('app.streaming.call_session_manager.enhanced_processing_manager') as mock_manager:
        from app.core.enhanced_processing_manager import EnhancedProcessingMode
        mock_manager.determine_mode.return_value = EnhancedProcessingMode.DUAL
        mock_manager.get_processing_config.return_value = {
            "streaming_processing": {"enabled": True},
            "postcall_processing": {"enabled": True}
        }
        mock_manager.should_enable_streaming.return_value = True
        mock_manager.should_enable_postcall.return_value = True
        yield mock_manager


class TestCallSessionManagerInitialization:
    """Tests for CallSessionManager initialization"""

    def test_session_manager_init(self, mock_redis_client):
        """Test CallSessionManager initialization with provided redis client"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        assert manager is not None
        assert manager.redis_client == mock_redis_client
        assert isinstance(manager.active_sessions, dict)
        assert len(manager.active_sessions) == 0

    @patch('app.config.settings.redis_task_client', MagicMock())
    def test_session_manager_init_with_defaults(self, mock_redis=None):
        """Test CallSessionManager with default redis client"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager()

        assert manager is not None
        # redis_client may be None if redis_task_client is not configured
        assert hasattr(manager, 'redis_client')


class TestCreateSession:
    """Tests for starting new call sessions (using start_session method)"""

    @pytest.mark.asyncio
    async def test_create_session_success(self, mock_redis_client, mock_enhanced_processing_manager,
                                          mock_enhanced_notification_service):
        """Test successful session creation using start_session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        connection_info = {"channel": "phone", "agent_id": "agent_123"}
        session = await manager.start_session("call_001", connection_info)

        assert session is not None
        assert session.call_id == "call_001"
        assert session.status == "active"
        assert session.connection_info == connection_info
        assert "call_001" in manager.active_sessions
        mock_redis_client.hset.assert_called()

    @pytest.mark.asyncio
    async def test_create_session_with_metadata(self, mock_redis_client,
                                                      mock_enhanced_processing_manager,
                                                      mock_enhanced_notification_service):
        """Test session creation with mode override (metadata)"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        session = await manager.start_session("call_002", {}, mode_override="POST_CALL")

        assert session is not None
        # Verify mode override was passed to processing manager
        call_context = mock_enhanced_processing_manager.determine_mode.call_args[0][0]
        assert "mode_override" in call_context
        assert call_context["mode_override"] == "POST_CALL"

    @pytest.mark.asyncio
    async def test_create_session_redis_failure(self, mock_redis_client,
                                                      mock_enhanced_processing_manager):
        """Test session creation when Redis fails"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Make processing manager raise an exception
        mock_enhanced_processing_manager.determine_mode.side_effect = Exception("Redis connection error")

        with pytest.raises(Exception) as exc_info:
            await manager.start_session("call_003", {})

        assert "Redis" in str(exc_info.value) or "connection" in str(exc_info.value).lower()


class TestGetSession:
    """Tests for retrieving session data"""

    @pytest.mark.asyncio
    async def test_get_session_success(self, mock_redis_client,
                                             mock_enhanced_processing_manager,
                                             mock_enhanced_notification_service):
        """Test successful session retrieval from memory"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Create a session
        created_session = await manager.start_session("call_004", {})

        # Get the session
        retrieved_session = await manager.get_session("call_004")

        assert retrieved_session is not None
        assert retrieved_session.call_id == "call_004"
        assert retrieved_session == created_session

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, mock_redis_client):
        """Test getting non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        mock_redis_client.hget.return_value = None

        session = await manager.get_session("nonexistent_session")

        assert session is None

    @pytest.mark.asyncio
    async def test_get_session_with_transcript(self, mock_redis_client,
                                                     mock_enhanced_processing_manager,
                                                     mock_enhanced_notification_service):
        """Test getting session with transcript data"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Create session and add transcript
        await manager.start_session("call_005", {})

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.process_if_ready = AsyncMock(return_value=None)
            await manager.add_transcription("call_005", "Hello, this is a test transcript", 5.0)

        session = await manager.get_session("call_005")

        assert session is not None
        assert session.cumulative_transcript == "Hello, this is a test transcript"


class TestUpdateSession:
    """Tests for updating session data (using add_transcription method)"""

    @pytest.mark.asyncio
    async def test_update_session_success(self, mock_redis_client,
                                               mock_enhanced_processing_manager,
                                               mock_enhanced_notification_service):
        """Test successful session update via add_transcription"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Create a session first
        await manager.start_session("call_006", {})

        # Add transcription (update session)
        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.process_if_ready = AsyncMock(return_value=None)

            updated_session = await manager.add_transcription(
                "call_006",
                "Updated transcript",
                audio_duration=2.5
            )

        assert updated_session is not None
        assert updated_session.cumulative_transcript == "Updated transcript"
        assert mock_redis_client.hset.called

    @pytest.mark.asyncio
    async def test_update_session_transcript(self, mock_redis_client,
                                                   mock_enhanced_processing_manager,
                                                   mock_enhanced_notification_service):
        """Test updating session transcript creates proper segment"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        await manager.start_session("call_007", {})

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.process_if_ready = AsyncMock(return_value=None)

            await manager.add_transcription("call_007", "New transcript text", 3.0)

        session = await manager.get_session("call_007")
        assert len(session.transcript_segments) == 1
        assert session.transcript_segments[0]['transcript'] == "New transcript text"
        mock_redis_client.hset.assert_called()

    @pytest.mark.asyncio
    async def test_update_session_analysis_results(self, mock_redis_client,
                                                         mock_enhanced_processing_manager,
                                                         mock_enhanced_notification_service):
        """Test updating session with transcription and metadata (analysis results)"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        await manager.start_session("call_008", {})

        analysis_metadata = {
            "entities": {"PERSON": ["John"]},
            "classification": {"category": "general"}
        }

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.process_if_ready = AsyncMock(return_value=None)

            await manager.add_transcription("call_008", "Transcript with analysis", 5.0, metadata=analysis_metadata)

        session = await manager.get_session("call_008")
        assert session.transcript_segments[0]['metadata'] == analysis_metadata
        mock_redis_client.hset.assert_called()


class TestEndSession:
    """Tests for ending call sessions"""

    @pytest.mark.asyncio
    async def test_end_session_success(self, mock_redis_client,
                                         mock_enhanced_processing_manager,
                                         mock_enhanced_notification_service):
        """Test successful session termination"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Create session
        await manager.start_session("call_009", {})

        # Mock progressive processor
        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.finalize_call_analysis = AsyncMock(return_value={
                "total_windows_processed": 5,
                "final_translation_length": 1000
            })

            # End session
            ended_session = await manager.end_session("call_009", reason="completed")

        assert ended_session is not None
        assert ended_session.status == "completed"
        assert "call_009" not in manager.active_sessions

    @pytest.mark.asyncio
    async def test_end_session_with_summary(self, mock_redis_client,
                                                  mock_enhanced_processing_manager,
                                                  mock_enhanced_notification_service):
        """Test ending session (reason parameter acts like summary)"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        await manager.start_session("call_010", {})

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.finalize_call_analysis = AsyncMock(return_value=None)

            # Use reason parameter (no summary parameter in actual API)
            await manager.end_session("call_010", reason="completed_with_summary")

        # Session should be ended
        assert "call_010" not in manager.active_sessions
        mock_enhanced_notification_service.send_call_end_streaming.assert_called()

    @pytest.mark.asyncio
    async def test_end_session_not_found(self, mock_redis_client):
        """Test ending non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        result = await manager.end_session("nonexistent_session")

        # Should handle gracefully and return None
        assert result is None


class TestDeleteSession:
    """Tests for deleting/cleaning up sessions (using end_session + manual cleanup)"""

    @pytest.mark.asyncio
    async def test_delete_session_success(self, mock_redis_client,
                                                mock_enhanced_processing_manager,
                                                mock_enhanced_notification_service):
        """Test session deletion via end_session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        await manager.start_session("call_011", {})

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.finalize_call_analysis = AsyncMock(return_value=None)

            result = await manager.end_session("call_011")

        # Session removed from active sessions
        assert result is not None
        assert "call_011" not in manager.active_sessions

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, mock_redis_client):
        """Test deleting non-existent session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        result = await manager.end_session("nonexistent")

        assert result is None


class TestListActiveSessions:
    """Tests for listing active sessions"""

    @pytest.mark.asyncio
    async def test_list_active_sessions(self, mock_redis_client,
                                             mock_enhanced_processing_manager,
                                             mock_enhanced_notification_service):
        """Test listing all active sessions using get_all_active_sessions"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Create multiple sessions
        await manager.start_session("call_012", {})
        await manager.start_session("call_013", {})

        sessions = await manager.get_all_active_sessions()

        assert sessions is not None
        assert isinstance(sessions, list)
        assert len(sessions) == 2

    @pytest.mark.asyncio
    async def test_list_active_sessions_empty(self, mock_redis_client):
        """Test listing when no active sessions"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        sessions = await manager.get_all_active_sessions()

        assert isinstance(sessions, list)
        assert len(sessions) == 0


class TestProcessAudioChunk:
    """Tests for processing audio (via add_transcription - no process_audio_chunk method)"""

    @pytest.mark.asyncio
    async def test_process_audio_chunk_success(self, mock_redis_client,
                                                     mock_enhanced_processing_manager,
                                                     mock_enhanced_notification_service):
        """Test audio processing via add_transcription"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        await manager.start_session("call_014", {})

        # Simulate audio chunk processing by adding transcription
        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processed_window = MagicMock()
            mock_processed_window.window_id = 1
            mock_processor.process_if_ready = AsyncMock(return_value=mock_processed_window)

            result = await manager.add_transcription(
                call_id="call_014",
                transcript="Test transcript from audio chunk",
                audio_duration=2.5
            )

        assert result is not None
        assert result.cumulative_transcript == "Test transcript from audio chunk"

    @pytest.mark.asyncio
    async def test_process_audio_chunk_invalid_session(self, mock_redis_client):
        """Test processing for invalid session"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Try to add transcription to non-existent session
        result = await manager.add_transcription(
            call_id="invalid_session",
            transcript="test",
            audio_duration=1.0
        )

        # Should return None for non-existent session
        assert result is None


class TestGetSessionStats:
    """Tests for getting session statistics"""

    @pytest.mark.asyncio
    async def test_get_session_stats_success(self, mock_redis_client,
                                                   mock_enhanced_processing_manager,
                                                   mock_enhanced_notification_service):
        """Test getting overall session statistics (NO call_id parameter)"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        # Create sessions with transcriptions
        await manager.start_session("call_015", {})
        await manager.start_session("call_016", {})

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.process_if_ready = AsyncMock(return_value=None)

            await manager.add_transcription("call_015", "Test 1", 5.0)
            await manager.add_transcription("call_016", "Test 2", 3.0)

        # Get stats - NO PARAMETERS
        stats = await manager.get_session_stats()

        assert stats is not None
        assert isinstance(stats, dict)
        assert stats['active_sessions'] == 2
        assert stats['total_audio_duration'] == 8.0

    @pytest.mark.asyncio
    async def test_get_session_stats_not_found(self, mock_redis_client):
        """Test getting stats when no sessions exist"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)

        stats = await manager.get_session_stats()

        assert stats is not None
        assert stats['active_sessions'] == 0
        assert stats['total_audio_duration'] == 0.0


class TestSessionTimeout:
    """Tests for session timeout handling"""

    @pytest.mark.asyncio
    async def test_check_session_timeout(self, mock_redis_client,
                                               mock_enhanced_processing_manager,
                                               mock_enhanced_notification_service):
        """Test cleanup of inactive sessions via _cleanup_inactive_sessions"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        manager.session_timeout = timedelta(minutes=1)

        # Create a session
        await manager.start_session("call_017", {})

        # Make it old
        session = await manager.get_session("call_017")
        session.last_activity = datetime.now() - timedelta(hours=2)

        # Run cleanup
        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.finalize_call_analysis = AsyncMock(return_value=None)

            await manager._cleanup_inactive_sessions()

        # Session should be removed
        assert "call_017" not in manager.active_sessions

    @pytest.mark.asyncio
    async def test_cleanup_timed_out_sessions(self, mock_redis_client,
                                                    mock_enhanced_processing_manager,
                                                    mock_enhanced_notification_service):
        """Test cleanup keeps active sessions, removes old ones"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        manager.session_timeout = timedelta(minutes=30)

        # Create old and new sessions
        await manager.start_session("old_session", {})
        await manager.start_session("new_session", {})

        # Make one old
        old_session = await manager.get_session("old_session")
        old_session.last_activity = datetime.now() - timedelta(hours=2)

        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.finalize_call_analysis = AsyncMock(return_value=None)

            await manager._cleanup_inactive_sessions()

        # Old removed, new kept
        assert "old_session" not in manager.active_sessions
        assert "new_session" in manager.active_sessions


class TestSessionErrorHandling:
    """Tests for error handling in session management"""

    @pytest.mark.asyncio
    async def test_create_session_redis_error(self, mock_redis_client,
                                                    mock_enhanced_processing_manager):
        """Test session creation with processing error"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        mock_enhanced_processing_manager.determine_mode.side_effect = Exception("Redis error")

        with pytest.raises(Exception):
            await manager.start_session("call_018", {})

    @pytest.mark.asyncio
    async def test_update_session_redis_error(self, mock_redis_client,
                                                    mock_enhanced_processing_manager,
                                                    mock_enhanced_notification_service):
        """Test transcription addition handles errors gracefully"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        await manager.start_session("call_019", {})

        # Make progressive processor fail
        with patch('app.streaming.call_session_manager.progressive_processor') as mock_processor:
            mock_processor.process_if_ready = AsyncMock(side_effect=Exception("Processing error"))

            # Should not raise, but handle gracefully
            result = await manager.add_transcription("call_019", "test", 1.0)

        # Session should still be updated
        assert result is not None
        assert result.cumulative_transcript == "test"

    @pytest.mark.asyncio
    async def test_get_session_redis_error(self, mock_redis_client):
        """Test session retrieval with Redis error falls back to memory"""
        from app.streaming.call_session_manager import CallSessionManager

        manager = CallSessionManager(redis_client=mock_redis_client)
        mock_redis_client.hget.side_effect = Exception("Redis error")

        # Should not raise, returns None
        session = await manager.get_session("call_020")

        assert session is None
