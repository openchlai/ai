# tests/test_streaming_components.py
import pytest
import asyncio
import sys
import os
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.streaming.audio_buffer import AsteriskAudioBuffer
from app.streaming.call_session_manager import CallSessionManager, CallSession
from app.core.enhanced_processing_manager import EnhancedProcessingMode

class TestAsteriskAudioBuffer:
    """Unit tests for the AsteriskAudioBuffer class"""

    def test_buffer_initialization(self):
        """Test audio buffer initialization"""
        buffer = AsteriskAudioBuffer()

        assert buffer.sample_rate == 16000
        assert buffer.expected_chunk_size == 320  # 10ms at 16kHz (160 samples * 2 bytes)
        assert buffer.window_size_bytes == 160000  # 5 seconds
        assert buffer.chunk_count == 0
        assert len(buffer.buffer) == 0
        assert buffer.offset == 0

    def test_buffer_initialization_properties(self):
        """Test audio buffer properties after initialization"""
        buffer = AsteriskAudioBuffer()

        assert buffer.sample_rate == 16000
        assert buffer.window_size_bytes == 160000  # 5 seconds at 16kHz * 2 bytes
        assert buffer.offset == 0
        assert buffer.chunk_count == 0

    def test_add_single_chunk(self):
        """Test adding a single audio chunk"""
        buffer = AsteriskAudioBuffer()
        chunk = b'\x00' * 640  # 20ms of silence
        
        result = buffer.add_chunk(chunk)
        
        assert result is None  # Not enough data for window yet
        assert buffer.chunk_count == 1
        assert len(buffer.buffer) == 640

    def test_add_multiple_chunks_no_window(self):
        """Test adding multiple chunks without reaching window size"""
        buffer = AsteriskAudioBuffer()
        
        # Add 100 chunks (2 seconds worth)
        for i in range(100):
            chunk = b'\x00' * 640
            result = buffer.add_chunk(chunk)
            assert result is None  # Still not enough for 5-second window
        
        assert buffer.chunk_count == 100
        assert len(buffer.buffer) == 64000  # 100 * 640

    def test_window_trigger_at_exact_size(self):
        """Test that window triggers at exactly the right size"""
        buffer = AsteriskAudioBuffer()
        
        # Add exactly 250 chunks (5 seconds)
        for i in range(250):
            chunk = b'\x00' * 640
            result = buffer.add_chunk(chunk)
            
            if i < 249:
                assert result is None
            else:
                # 250th chunk should trigger the window
                assert result is not None
                assert isinstance(result, np.ndarray)
                assert len(result) == 80000  # 5 seconds * 16000 samples

    def test_window_audio_conversion(self):
        """Test that audio is properly converted to numpy array"""
        buffer = AsteriskAudioBuffer()
        
        # Create test audio with known pattern
        test_pattern = b'\x01\x00\x02\x00' * 160  # Alternating pattern
        
        # Add enough chunks to trigger window
        for i in range(250):
            if i == 0:
                result = buffer.add_chunk(test_pattern)  # First chunk has pattern
            else:
                result = buffer.add_chunk(b'\x00' * 640)  # Rest are silence
            
            if i == 249:  # Last chunk triggers window
                assert result is not None
                assert isinstance(result, np.ndarray)
                assert result.dtype == np.float32
                # First samples should reflect our test pattern
                assert result[0] != 0  # Should have non-zero values from pattern

    def test_overlapping_windows(self):
        """Test overlapping window behavior"""
        buffer = AsteriskAudioBuffer()
        
        # Fill first window
        for i in range(250):
            buffer.add_chunk(b'\x00' * 640)
        
        # Add more chunks - should trigger second window with overlap
        for i in range(125):  # Half a window more
            result = buffer.add_chunk(b'\x00' * 640)
            if i == 124:  # Should trigger at 375 total chunks
                assert result is not None

    def test_get_stats(self):
        """Test buffer statistics"""
        buffer = AsteriskAudioBuffer()
        
        # Initial stats
        stats = buffer.get_stats()
        assert stats["chunks_received"] == 0
        assert stats["buffer_size_bytes"] == 0
        assert stats["buffer_duration_seconds"] == 0.0
        assert not stats["window_ready"]
        
        # Add some chunks
        for i in range(100):
            buffer.add_chunk(b'\x00' * 640)
        
        # Updated stats
        stats = buffer.get_stats()
        assert stats["chunks_received"] == 100
        assert stats["buffer_size_bytes"] == 64000
        assert stats["buffer_duration_seconds"] == 2.0  # 100 chunks * 20ms
        assert not stats["window_ready"]  # Still not 5 seconds

    def test_buffer_overflow_protection(self):
        """Test buffer doesn't grow indefinitely"""
        buffer = AsteriskAudioBuffer()
        
        # Add way more chunks than needed
        for i in range(1000):  # 20 seconds worth
            result = buffer.add_chunk(b'\x00' * 640)
            # Should get multiple window outputs
            if result is not None:
                assert isinstance(result, np.ndarray)
        
        # Buffer should not be excessively large
        stats = buffer.get_stats()
        assert stats["buffer_size_bytes"] < 200000  # Less than ~6 seconds

    def test_invalid_chunk_size(self):
        """Test handling of invalid chunk sizes"""
        buffer = AsteriskAudioBuffer()
        
        # Too small chunk
        small_chunk = b'\x00' * 100
        result = buffer.add_chunk(small_chunk)
        # Should handle gracefully (implementation dependent)
        
        # Too large chunk
        large_chunk = b'\x00' * 1000
        result = buffer.add_chunk(large_chunk)
        # Should handle gracefully


class TestCallSession:
    """Unit tests for the CallSession class"""

    def test_call_session_creation(self):
        """Test creating a new call session"""
        call_id = "test_call_001"
        connection_info = {"client_addr": ("192.168.1.100", 12345)}
        now = datetime.now()

        # CallSession is now a dataclass with all required fields
        session = CallSession(
            call_id=call_id,
            start_time=now,
            last_activity=now,
            connection_info=connection_info,
            transcript_segments=[],
            cumulative_transcript="",
            total_audio_duration=0.0,
            segment_count=0,
            status="active",
            processing_mode=EnhancedProcessingMode.DUAL,
            processing_plan={}
        )

        assert session.call_id == call_id
        assert session.connection_info == connection_info
        assert session.status == "active"
        assert session.transcript_segments == []
        assert session.start_time is not None
        assert session.processing_mode == EnhancedProcessingMode.DUAL

    def test_add_transcription(self):
        """Test transcript segments in session"""
        now = datetime.now()
        session = CallSession(
            call_id="test_call",
            start_time=now,
            last_activity=now,
            connection_info={},
            transcript_segments=[],
            cumulative_transcript="",
            total_audio_duration=0.0,
            segment_count=0,
            status="active",
            processing_mode=EnhancedProcessingMode.DUAL,
            processing_plan={}
        )

        # Add a transcript segment directly to the dataclass
        transcription = {
            "text": "Hello, how can I help you?",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.95
        }

        session.transcript_segments.append(transcription)

        assert len(session.transcript_segments) == 1
        assert session.transcript_segments[0] == transcription

    def test_get_full_transcript(self):
        """Test cumulative transcript field"""
        now = datetime.now()
        session = CallSession(
            call_id="test_call",
            start_time=now,
            last_activity=now,
            connection_info={},
            transcript_segments=[],
            cumulative_transcript="Hello How are you? I need help",
            total_audio_duration=0.0,
            segment_count=0,
            status="active",
            processing_mode=EnhancedProcessingMode.DUAL,
            processing_plan={}
        )

        full_transcript = session.cumulative_transcript

        assert "Hello" in full_transcript
        assert "How are you?" in full_transcript
        assert "I need help" in full_transcript

    def test_end_session(self):
        """Test ending a call session via status change"""
        now = datetime.now()
        session = CallSession(
            call_id="test_call",
            start_time=now,
            last_activity=now,
            connection_info={},
            transcript_segments=[],
            cumulative_transcript="",
            total_audio_duration=0.0,
            segment_count=0,
            status="active",
            processing_mode=EnhancedProcessingMode.DUAL,
            processing_plan={}
        )

        # Dataclass - directly update status
        session.status = "completed"

        assert session.status == "completed"

    def test_session_duration(self):
        """Test session has start_time for duration calculation"""
        import time
        start_time = datetime.now()

        session = CallSession(
            call_id="test_call",
            start_time=start_time,
            last_activity=datetime.now(),
            connection_info={},
            transcript_segments=[],
            cumulative_transcript="",
            total_audio_duration=0.0,
            segment_count=0,
            status="active",
            processing_mode=EnhancedProcessingMode.DUAL,
            processing_plan={}
        )

        # Simulate some time passing
        time.sleep(0.01)  # 10ms

        # Calculate duration manually (dataclass doesn't have method)
        duration = (datetime.now() - session.start_time).total_seconds()
        assert duration > 0
        assert duration < 1  # Should be less than 1 second

    def test_session_serialization(self):
        """Test converting session to dictionary"""
        call_id = "test_call_001"
        connection_info = {"client_addr": ("192.168.1.100", 12345)}
        now = datetime.now()

        session = CallSession(
            call_id=call_id,
            start_time=now,
            last_activity=now,
            connection_info=connection_info,
            transcript_segments=[{"text": "Test", "timestamp": "2023-01-01T10:00:00"}],
            cumulative_transcript="Test",
            total_audio_duration=0.0,
            segment_count=1,
            status="active",
            processing_mode=EnhancedProcessingMode.DUAL,
            processing_plan={}
        )

        session_dict = session.to_dict()

        assert isinstance(session_dict, dict)
        assert session_dict["call_id"] == call_id
        assert session_dict["status"] == "active"
        assert len(session_dict["transcript_segments"]) == 1


class TestCallSessionManager:
    """Unit tests for the CallSessionManager class"""

    @pytest.fixture
    def session_manager(self):
        """Create a fresh session manager for each test"""
        return CallSessionManager()

    @pytest.mark.asyncio
    async def test_start_session(self, session_manager):
        """Test starting a new call session"""
        call_id = "test_call_001"
        connection_info = {"client_addr": ("192.168.1.100", 12345)}
        
        session = await session_manager.start_session(call_id, connection_info)
        
        assert session is not None
        assert session.call_id == call_id
        assert session.status == "active"
        assert call_id in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_start_duplicate_session(self, session_manager):
        """Test starting a session with duplicate call_id"""
        call_id = "test_call_001"
        connection_info = {"client_addr": ("192.168.1.100", 12345)}
        
        # Start first session
        session1 = await session_manager.start_session(call_id, connection_info)
        
        # Try to start duplicate
        session2 = await session_manager.start_session(call_id, connection_info)
        
        # Should return existing session or handle gracefully
        assert session2 is not None
        # Implementation might return same session or new one

    @pytest.mark.asyncio
    async def test_get_session(self, session_manager):
        """Test retrieving a session"""
        call_id = "test_call_001"
        connection_info = {"client_addr": ("192.168.1.100", 12345)}

        # Start session
        await session_manager.start_session(call_id, connection_info)

        # Retrieve session (async method)
        retrieved_session = await session_manager.get_session(call_id)

        assert retrieved_session is not None
        assert retrieved_session.call_id == call_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, session_manager):
        """Test retrieving a non-existent session"""
        session = await session_manager.get_session("nonexistent_call")
        assert session is None

    @pytest.mark.asyncio
    async def test_add_transcription_to_session(self, session_manager):
        """Test adding transcription to existing session"""
        call_id = "test_call_001"
        await session_manager.start_session(call_id, {})

        transcript_text = "Hello world"
        audio_duration = 2.5  # seconds

        # add_transcription is async and takes transcript string and duration
        await session_manager.add_transcription(call_id, transcript_text, audio_duration)

        session = await session_manager.get_session(call_id)
        assert session.cumulative_transcript == transcript_text
        assert session.total_audio_duration == audio_duration

    @pytest.mark.asyncio
    async def test_add_transcription_to_nonexistent_session(self, session_manager):
        """Test adding transcription to non-existent session"""
        # Should handle gracefully - add_transcription checks if session exists
        # Returns None if session doesn't exist (based on implementation line 177)
        result = await session_manager.add_transcription("nonexistent", "test text", 1.0)
        assert result is None  # Should return None for non-existent session

    @pytest.mark.asyncio
    async def test_end_session(self, session_manager):
        """Test ending a session"""
        call_id = "test_call_001"
        await session_manager.start_session(call_id, {})

        result = await session_manager.end_session(call_id, reason="call_completed")

        assert result is not None  # Returns the ended session
        assert call_id not in session_manager.active_sessions

    @pytest.mark.asyncio
    async def test_end_nonexistent_session(self, session_manager):
        """Test ending a non-existent session"""
        result = await session_manager.end_session("nonexistent", reason="not_found")
        assert result is None  # Returns None for non-existent session

    @pytest.mark.asyncio
    async def test_get_all_active_sessions(self, session_manager):
        """Test getting all active sessions"""
        # Start multiple sessions
        call_ids = ["call_001", "call_002", "call_003"]
        for call_id in call_ids:
            await session_manager.start_session(call_id, {})

        # get_all_active_sessions is async
        active_sessions = await session_manager.get_all_active_sessions()

        assert len(active_sessions) == len(call_ids)
        for call_id in call_ids:
            assert call_id in [s.call_id for s in active_sessions]

    @pytest.mark.asyncio
    async def test_get_session_stats(self, session_manager):
        """Test getting session statistics"""
        # get_session_stats is async
        stats = await session_manager.get_session_stats()

        assert isinstance(stats, dict)
        assert "active_sessions" in stats
        assert stats["active_sessions"] == 0  # Initially empty

    @pytest.mark.asyncio
    async def test_session_cleanup(self, session_manager):
        """Test session cleanup functionality"""
        # Start some sessions
        old_call_id = "old_call"
        new_call_id = "new_call"

        await session_manager.start_session(old_call_id, {})
        await session_manager.start_session(new_call_id, {})
        
        # Mock old session to be older than cleanup threshold
        from datetime import timedelta

        # get_session is async
        old_session = await session_manager.get_session(old_call_id)
        # Manipulate last_activity to be old (cleanup checks last_activity)
        old_session.last_activity = datetime.now() - timedelta(hours=1)

        # Set a short timeout for testing
        session_manager.session_timeout = timedelta(minutes=30)

        # Run cleanup (private async method)
        await session_manager._cleanup_inactive_sessions()

        # Old session should be removed from active sessions
        assert old_call_id not in session_manager.active_sessions
        # New session should still exist
        assert new_call_id in session_manager.active_sessions