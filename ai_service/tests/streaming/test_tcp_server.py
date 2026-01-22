import pytest
import asyncio
import numpy as np
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from io import BytesIO

from app.streaming.tcp_server import AsteriskTCPServer

@pytest.fixture
def tcp_server():
    """Fixture to provide an AsteriskTCPServer instance"""
    return AsteriskTCPServer()

@pytest.fixture
def mock_reader():
    """Mock StreamReader"""
    reader = AsyncMock()
    return reader

@pytest.fixture
def mock_writer():
    """Mock StreamWriter"""
    writer = AsyncMock()
    writer.get_extra_info = Mock(return_value=('192.168.1.100', 12345))
    writer.close = Mock()
    writer.wait_closed = AsyncMock()
    return writer

@pytest.fixture
def mock_call_session():
    """Mock call session"""
    session = Mock()
    session.call_id = "test_call_123"
    session.status = "active"
    return session

@pytest.fixture
def mock_audio_buffer():
    """Mock audio buffer"""
    buffer = Mock()
    buffer.add_chunk.return_value = None  # Default: no window ready
    buffer.get_stats.return_value = {
        "buffer_size_bytes": 80000,
        "buffer_duration_seconds": 2.5,
        "chunks_received": 250,
        "window_ready": False
    }
    return buffer

class TestAsteriskTCPServer:
    """Tests for AsteriskTCPServer class"""
    
    def test_initialization(self, tcp_server):
        """Test AsteriskTCPServer initialization"""
        assert tcp_server.active_connections == {}
        assert tcp_server.server is None

    @pytest.mark.asyncio
    async def test_handle_connection_initialization(self, tcp_server, mock_reader, mock_writer):
        """Test connection handling initialization"""
        # Mock the reader to return empty data (connection close)
        mock_reader.read.return_value = b''
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer') as mock_buffer_class:
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify connection cleanup
        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_connection_uid_extraction(self, tcp_server, mock_reader, mock_writer, mock_call_session, mock_audio_buffer):
        """Test UID extraction and call session creation"""
        call_id = "test_call_123"
        
        # Simulate UID data followed by CR (carriage return) then empty data (connection close)
        mock_reader.read.side_effect = [
            call_id.encode('utf-8') + b'\r',  # UID with CR
            b''  # Connection close
        ]
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer', return_value=mock_audio_buffer):
            
            mock_session_manager.start_session = AsyncMock(return_value=mock_call_session)
            mock_session_manager.end_session = AsyncMock(return_value=mock_call_session)
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify call session was started
        mock_session_manager.start_session.assert_called_once()
        call_args = mock_session_manager.start_session.call_args
        assert call_args[0][0] == call_id  # First argument should be call_id
        
        # Verify connection info
        connection_info = call_args[0][1]
        assert 'client_addr' in connection_info
        assert 'temp_connection_id' in connection_info
        assert 'start_time' in connection_info
        
        # Verify call session was ended
        mock_session_manager.end_session.assert_called_once_with(call_id, reason="connection_closed")

    @pytest.mark.asyncio
    async def test_handle_connection_audio_processing(self, tcp_server, mock_reader, mock_writer, mock_call_session, mock_audio_buffer):
        """Test audio data processing"""
        call_id = "test_call_123"
        
        # Mock audio data (640 bytes for 20ms SLIN)
        audio_data = b'\x00' * 640
        audio_array = np.array([0.1, 0.2, 0.3] * 1000, dtype=np.float32)  # Mock audio array
        
        mock_audio_buffer.add_chunk.return_value = audio_array  # Return audio array (window ready)
        
        # Simulate UID, then audio data, then connection close
        mock_reader.read.side_effect = [
            call_id.encode('utf-8') + b'\r',  # UID
            audio_data,  # Audio data
            b''  # Connection close
        ]
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch.object(tcp_server, '_submit_transcription') as mock_submit:
            
            mock_session_manager.start_session = AsyncMock(return_value=mock_call_session)
            mock_session_manager.end_session = AsyncMock(return_value=mock_call_session)
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify audio buffer was used
        mock_audio_buffer.add_chunk.assert_called_once_with(audio_data)
        
        # Verify transcription was submitted
        mock_submit.assert_called_once_with(audio_array, call_id)

    @pytest.mark.asyncio
    async def test_handle_connection_session_start_failure(self, tcp_server, mock_reader, mock_writer):
        """Test handling of call session start failure"""
        call_id = "test_call_123"
        
        mock_reader.read.return_value = call_id.encode('utf-8') + b'\r'
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer'):
            
            mock_session_manager.start_session = AsyncMock(side_effect=Exception("Session start failed"))
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify connection was closed due to session start failure
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_connection_header_inspection(self, tcp_server, mock_reader, mock_writer):
        """Test header inspection logging for first 10 packets"""
        # Create mock data for multiple packets
        test_data = [b'CALL123\r'] + [b'\x00' * 640] * 12  # UID + 12 audio packets
        
        mock_reader.read.side_effect = test_data + [b'']  # Add connection close
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer') as mock_buffer_class, \
             patch('app.streaming.tcp_server.logger') as mock_logger:
            
            mock_session_manager.start_session = AsyncMock(return_value=Mock())
            mock_session_manager.end_session = AsyncMock(return_value=Mock())
            mock_buffer_class.return_value.add_chunk.return_value = None
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify header inspection logging occurred
        header_log_calls = [call for call in mock_logger.info.call_args_list 
                           if 'header' in str(call) and 'Packet' in str(call)]
        assert len(header_log_calls) >= 10  # Should log first 10 packets total

    @pytest.mark.asyncio
    async def test_submit_transcription_success(self, tcp_server, mock_call_session):
        """Test successful transcription submission"""
        call_id = "test_call_123"
        audio_array = np.array([0.1, 0.2, 0.3] * 1000, dtype=np.float32)

        mock_task = Mock()
        mock_task.id = "task_123"

        with patch('app.streaming.tcp_server.process_streaming_audio_task') as mock_task_func, \
             patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager:

            mock_session_manager.get_session = AsyncMock(return_value=mock_call_session)
            mock_task_func.delay.return_value = mock_task

            await tcp_server._submit_transcription(audio_array, call_id)

        # Verify task was submitted with correct parameters
        mock_task_func.delay.assert_called_once()
        call_kwargs = mock_task_func.delay.call_args.kwargs

        assert 'audio_bytes' in call_kwargs
        assert call_kwargs['connection_id'] == call_id
        assert call_kwargs['language'] == "sw"
        assert call_kwargs['sample_rate'] == 16000
        assert call_kwargs['duration_seconds'] == 5.0
        assert call_kwargs['is_streaming'] is True

        # Verify audio conversion
        expected_audio_bytes = (audio_array * 32768.0).astype(np.int16).tobytes()
        assert call_kwargs['audio_bytes'] == expected_audio_bytes

    @pytest.mark.asyncio
    async def test_submit_transcription_failure(self, tcp_server, mock_call_session):
        """Test transcription submission failure handling"""
        call_id = "test_call_123"
        audio_array = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        with patch('app.streaming.tcp_server.process_streaming_audio_task') as mock_task_func, \
             patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.logger') as mock_logger:

            mock_session_manager.get_session = AsyncMock(return_value=mock_call_session)
            mock_task_func.delay.side_effect = Exception("Task submission failed")

            # Should not raise exception, just log error
            await tcp_server._submit_transcription(audio_array, call_id)

        # Verify error was logged
        error_calls = [call for call in mock_logger.error.call_args_list
                      if "Failed to submit transcription" in str(call)]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_start_server_success(self, tcp_server):
        """Test successful server start"""
        mock_server = AsyncMock()
        mock_server.serve_forever = AsyncMock()

        with patch('asyncio.start_server', return_value=mock_server) as mock_start:
            # Use a context manager to simulate the server context
            mock_server.__aenter__ = AsyncMock(return_value=mock_server)
            mock_server.__aexit__ = AsyncMock(return_value=None)

            # Start server in a task and cancel it quickly to avoid infinite serve_forever
            server_task = asyncio.create_task(tcp_server.start_server())
            await asyncio.sleep(0.01)  # Let it start
            server_task.cancel()

            try:
                await server_task
            except asyncio.CancelledError:
                pass  # Expected when we cancel

        # Verify server was created with correct parameters (default host/port from tcp_server)
        mock_start.assert_called_once_with(tcp_server.handle_connection, tcp_server.host, tcp_server.port)

    @pytest.mark.asyncio
    async def test_start_server_failure(self, tcp_server):
        """Test server start failure"""
        with patch('asyncio.start_server', side_effect=Exception("Server start failed")):
            with pytest.raises(Exception, match="Server start failed"):
                await tcp_server.start_server()

    @pytest.mark.asyncio
    async def test_stop_server(self, tcp_server):
        """Test server stop"""
        mock_server = Mock()
        mock_server.close = Mock()
        mock_server.wait_closed = AsyncMock()
        
        tcp_server.server = mock_server
        
        await tcp_server.stop_server()
        
        mock_server.close.assert_called_once()
        mock_server.wait_closed.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_stop_server_no_server(self, tcp_server):
        """Test stopping server when no server is running"""
        # Should not raise exception
        await tcp_server.stop_server()

    
    def test_get_status_no_connections(self, tcp_server):
        """Test status when no connections are active"""
        status = tcp_server.get_status()

        assert status['server_running'] is False
        assert status['active_calls'] == 0
        assert status['call_sessions'] == {}
        assert status['transcription_method'] == "celery_workers"  
        assert status['tcp_port'] == 8300
        
    def test_get_status_with_connections(self, tcp_server, mock_audio_buffer, mock_call_session):
        """Test status with active connections"""
        call_id = "test_call_123"
        client_addr = ('192.168.1.100', 12345)
        
        # Set up active connection
        tcp_server.active_connections[call_id] = {
            'audio_buffer': mock_audio_buffer,
            'client_addr': client_addr,
            'session': mock_call_session
        }
        
        # Mock server as running
        tcp_server.server = Mock()
        
        status = tcp_server.get_status()
        
        assert status['server_running'] is True
        assert status['active_calls'] == 1
        assert call_id in status['call_sessions']
        
        call_stats = status['call_sessions'][call_id]
        assert 'audio_buffer_stats' in call_stats
        assert call_stats['client_addr'] == str(client_addr)
        assert call_stats['session_status'] == "active"

    def test_get_status_with_connections_no_session(self, tcp_server, mock_audio_buffer):
        """Test status with active connections but no session"""
        call_id = "test_call_123"
        client_addr = ('192.168.1.100', 12345)
        
        # Set up active connection without session
        tcp_server.active_connections[call_id] = {
            'audio_buffer': mock_audio_buffer,
            'client_addr': client_addr,
            'session': None
        }
        
        status = tcp_server.get_status()
        
        call_stats = status['call_sessions'][call_id]
        assert call_stats['session_status'] == "unknown"

    @pytest.mark.asyncio
    async def test_handle_connection_exception_during_processing(self, tcp_server, mock_reader, mock_writer):
        """Test exception handling during connection processing"""
        # Mock reader to raise exception during read
        mock_reader.read.side_effect = Exception("Connection error")
        
        with patch('app.streaming.tcp_server.logger') as mock_logger:
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify error was logged
        error_calls = [call for call in mock_logger.error.call_args_list 
                      if "Error handling connection" in str(call)]
        assert len(error_calls) >= 1
        
        # Verify connection cleanup
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_connection_cleanup_failure(self, tcp_server, mock_reader, mock_writer, mock_call_session):
        """Test handling of cleanup failures"""
        call_id = "test_call_123"
        
        mock_reader.read.side_effect = [
            call_id.encode('utf-8') + b'\r',  # UID
            b''  # Connection close
        ]
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer'), \
             patch('app.streaming.tcp_server.logger') as mock_logger:
            
            mock_session_manager.start_session = AsyncMock(return_value=mock_call_session)
            mock_session_manager.end_session = AsyncMock(side_effect=Exception("Cleanup failed"))
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify cleanup error was logged
        error_calls = [call for call in mock_logger.error.call_args_list 
                      if "Error cleaning up call session" in str(call)]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_uid_buffer_handling_multiple_bytes(self, tcp_server, mock_reader, mock_writer, mock_call_session):
        """Test UID buffer handling with call ID split across multiple reads"""
        call_id = "test_call_123"
        
        # Split call ID across multiple reads
        mock_reader.read.side_effect = [
            b'test_',  # Partial UID
            b'call_',  # Continue UID
            b'123\r',  # Complete UID with CR
            b''  # Connection close
        ]
        
        with patch('app.streaming.tcp_server.call_session_manager') as mock_session_manager, \
             patch('app.streaming.tcp_server.AsteriskAudioBuffer'):
            
            mock_session_manager.start_session = AsyncMock(return_value=mock_call_session)
            mock_session_manager.end_session = AsyncMock(return_value=mock_call_session)
            
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify call session was started with correct call_id
        mock_session_manager.start_session.assert_called_once()
        assert mock_session_manager.start_session.call_args[0][0] == call_id

    @pytest.mark.asyncio
    async def test_audio_mode_without_call_id(self, tcp_server, mock_reader, mock_writer):
        """Test that audio processing doesn't occur without call_id"""
        # Simulate direct audio data without UID phase
        audio_data = b'\x00' * 640
        
        mock_reader.read.side_effect = [
            audio_data,  # Audio data without UID
            b''  # Connection close
        ]
        
        with patch.object(tcp_server, '_submit_transcription') as mock_submit:
            await tcp_server.handle_connection(mock_reader, mock_writer)
        
        # Verify transcription was not submitted
        mock_submit.assert_not_called()

    def test_filename_generation_format(self, tcp_server):
        """Test that generated filenames follow expected format"""
        call_id = "test_call_123"
        audio_array = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        # Mock session manager to return a valid session with realtime processing enabled
        from unittest.mock import AsyncMock
        mock_session = Mock()
        mock_session.processing_plan = {
            "realtime_processing": {"enabled": True}
        }
        mock_session.processing_mode = "streaming"

        with patch('app.streaming.tcp_server.process_streaming_audio_task') as mock_task_func, \
             patch('app.streaming.tcp_server.datetime') as mock_datetime, \
             patch('app.streaming.tcp_server.call_session_manager.get_session', new_callable=AsyncMock, return_value=mock_session):

            # Mock datetime to return predictable timestamp
            mock_datetime.now.return_value.strftime.return_value = "123456789"

            mock_task_func.delay.return_value = Mock(id="task_123")

            asyncio.run(tcp_server._submit_transcription(audio_array, call_id))

        # Verify filename format
        call_kwargs = mock_task_func.delay.call_args.kwargs
        filename = call_kwargs['filename']
        assert filename.startswith(f"call_{call_id}_")
        assert filename.endswith(".wav")