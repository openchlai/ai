#!/usr/bin/env python3
"""
Unit tests for TCP streaming components
"""
import pytest
import asyncio
import numpy as np
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.streaming.tcp_server import AsteriskTCPServer
from app.streaming.audio_buffer import AsteriskAudioBuffer


class TestAsteriskAudioBuffer:
    """Test the audio buffer component"""
    
    def test_buffer_initialization(self):
        """Test buffer is properly initialized"""
        buffer = AsteriskAudioBuffer()
        assert buffer.sample_rate == 16000
        assert buffer.window_size_bytes == 160000  # 5 seconds
        assert buffer.chunk_count == 0
        assert len(buffer.buffer) == 0
        
    def test_single_chunk_no_output(self):
        """Test single chunk doesn't trigger output"""
        buffer = AsteriskAudioBuffer()
        chunk = b'\x00' * 640  # 20ms of silence
        
        result = buffer.add_chunk(chunk)
        assert result is None  # Not enough data yet
        assert buffer.chunk_count == 1
        assert len(buffer.buffer) == 640
        
    def test_five_second_window_triggers_output(self):
        """Test 5-second window triggers audio output"""
        buffer = AsteriskAudioBuffer()
        
        # Add 250 chunks of 20ms = 5 seconds
        for i in range(250):
            chunk = b'\x00' * 640
            result = buffer.add_chunk(chunk)
            
            if i < 249:  # First 249 chunks
                assert result is None
            else:  # 250th chunk triggers output
                assert result is not None
                assert isinstance(result, np.ndarray)
                assert len(result) == 80000  # 5 seconds * 16000 samples
                
    def test_buffer_stats(self):
        """Test buffer statistics"""
        buffer = AsteriskAudioBuffer()
        
        # Add some chunks
        for i in range(100):
            buffer.add_chunk(b'\x00' * 640)
            
        stats = buffer.get_stats()
        assert stats["chunks_received"] == 100
        assert stats["buffer_size_bytes"] == 64000
        assert stats["buffer_duration_seconds"] == 2.0
        assert not stats["window_ready"]  # Not 5 seconds yet


class TestAsteriskTCPServer:
    """Test the TCP server component"""
    
    @pytest.fixture
    def server(self):
        """Create a TCP server instance"""
        return AsteriskTCPServer()
        
    def test_server_initialization(self, server):
        """Test server is properly initialized"""
        assert server.active_connections == {}
        assert server.server is None
        
    def test_connection_tracking(self, server):
        """Test connection ID generation and tracking"""
        # Mock connection details
        client_addr = ('192.168.1.100', 12345)
        
        # This would be called in handle_connection
        connection_id = f"{client_addr[0]}:{client_addr[1]}:{datetime.now().strftime('%H%M%S')}"
        
        assert client_addr[0] in connection_id
        assert str(client_addr[1]) in connection_id
        
    def test_get_status(self, server):
        """Test server status reporting"""
        status = server.get_status()
        
        assert "server_running" in status
        assert "active_connections" in status
        assert "tcp_port" in status
        assert status["tcp_port"] == 8300
        assert status["transcription_method"] == "celery_workers"
        
    @pytest.mark.asyncio
    async def test_submit_transcription(self, server):
        """Test transcription submission"""
        # Create mock audio data
        audio_array = np.random.random(80000).astype(np.float32)
        connection_id = "test_connection_123"

        # Create a mock call session
        mock_session = Mock()
        mock_session.processing_plan = {"realtime_processing": {"enabled": True}}

        with patch('app.streaming.tcp_server.process_streaming_audio_task') as mock_task_func, \
             patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager:

            mock_session_manager.get_session = AsyncMock(return_value=mock_session)
            mock_task_func.delay.return_value.id = "test_task_456"

            await server._submit_transcription(audio_array, connection_id)

            # Verify task was submitted
            mock_task_func.delay.assert_called_once()
            call_kwargs = mock_task_func.delay.call_args.kwargs

            assert call_kwargs["connection_id"] == connection_id
            assert call_kwargs["language"] == "sw"
            assert call_kwargs["sample_rate"] == 16000
            assert call_kwargs["is_streaming"] is True


@pytest.mark.asyncio
class TestTCPProtocol:
    """Test TCP protocol handling"""
    
    async def test_uid_protocol_parsing(self):
        """Test UID protocol parsing"""
        server = AsteriskTCPServer()
        
        # Mock reader/writer
        mock_reader = AsyncMock()
        mock_writer = Mock()
        mock_writer.get_extra_info.return_value = ('192.168.1.100', 12345)
        mock_writer.close = Mock()
        mock_writer.wait_closed = AsyncMock()
        
        # Simulate UID data followed by CR
        uid_data = b"test_uid_12345\r"
        audio_data = b'\x00' * 640  # First audio chunk
        
        # Mock read sequence: UID first, then audio
        mock_reader.read.side_effect = [uid_data, audio_data, b'']  # Empty = connection closed
        
        with patch.object(server, '_submit_transcription') as mock_submit:
            await server.handle_connection(mock_reader, mock_writer)
            
        # Verify connection was handled
        mock_writer.close.assert_called_once()
        
    async def test_audio_chunk_processing(self):
        """Test audio chunk processing after UID"""
        server = AsteriskTCPServer()

        # Mock the audio buffer to return audio array on first call
        mock_audio_array = np.random.random(80000).astype(np.float32)

        with patch('app.streaming.tcp_server.AsteriskAudioBuffer') as mock_buffer_class, \
             patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager:

            mock_buffer = Mock()
            mock_buffer.add_chunk.return_value = mock_audio_array  # Simulate 5-second window ready
            mock_buffer_class.return_value = mock_buffer

            # Mock call session
            mock_session = Mock()
            mock_session.processing_plan = {"realtime_processing": {"enabled": True}}
            mock_session_manager.start_session = AsyncMock(return_value=mock_session)
            mock_session_manager.end_session = AsyncMock(return_value=mock_session)
            mock_session_manager.get_session = AsyncMock(return_value=mock_session)

            with patch.object(server, '_submit_transcription') as mock_submit:
                # Mock reader/writer
                mock_reader = AsyncMock()
                mock_writer = Mock()
                mock_writer.get_extra_info.return_value = ('192.168.1.100', 12345)
                mock_writer.close = Mock()
                mock_writer.wait_closed = AsyncMock()

                # Simulate protocol: UID + CR, then audio chunk, then close
                mock_reader.read.side_effect = [
                    b"test_uid\r",  # UID
                    b'\x00' * 640,  # Audio chunk
                    b''  # Connection closed
                ]

                await server.handle_connection(mock_reader, mock_writer)

                # Verify audio was processed
                mock_buffer.add_chunk.assert_called_once_with(b'\x00' * 640)
                # Call_id is 'test_uid' extracted from the UID line
                mock_submit.assert_called_once_with(mock_audio_array, 'test_uid')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])