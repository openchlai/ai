import pytest
import asyncio
import numpy as np
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import WebSocketDisconnect

from app.streaming.websocket_server import AsteriskWebSocketManager

@pytest.fixture
def websocket_manager():
    """Fixture to provide an AsteriskWebSocketManager instance"""
    return AsteriskWebSocketManager()

@pytest.fixture
def mock_websocket():
    """Mock WebSocket"""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.receive_bytes = AsyncMock()
    
    # Mock client info
    client_mock = Mock()
    client_mock.host = "192.168.1.100"
    client_mock.port = 12345
    websocket.client = client_mock
    
    return websocket

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

class TestAsteriskWebSocketManager:
    """Tests for AsteriskWebSocketManager class"""
    
    def test_initialization(self, websocket_manager):
        """Test AsteriskWebSocketManager initialization"""
        assert websocket_manager.active_connections == {}

    @pytest.mark.asyncio
    async def test_handle_websocket_initialization(self, websocket_manager, mock_websocket):
        """Test WebSocket connection initialization"""
        # Mock to disconnect immediately
        mock_websocket.receive_bytes.side_effect = WebSocketDisconnect()
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer') as mock_buffer_class:
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify WebSocket was accepted
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_websocket_uid_extraction(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test UID extraction from WebSocket data"""
        uid = "test_call_123"
        
        # Simulate UID data followed by WebSocket disconnect
        mock_websocket.receive_bytes.side_effect = [
            uid.encode('utf-8') + b'\r',  # UID with CR
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer):
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify connection was tracked and cleaned up
        assert len(websocket_manager.active_connections) == 0  

    @pytest.mark.asyncio
    async def test_handle_websocket_audio_processing(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test audio data processing through WebSocket"""
        uid = "test_call_123"
        audio_data = b'\x00' * 640  # 640 bytes for 20ms SLIN
        audio_array = np.array([0.1, 0.2, 0.3] * 1000, dtype=np.float32)
        
        mock_audio_buffer.add_chunk.return_value = audio_array  # Return audio array (window ready)
        
        # Simulate UID, then audio data, then disconnect
        mock_websocket.receive_bytes.side_effect = [
            uid.encode('utf-8') + b'\r',  # UID
            audio_data,  # Audio data
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch.object(websocket_manager, '_submit_transcription') as mock_submit:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify audio buffer was used
        mock_audio_buffer.add_chunk.assert_called_once_with(audio_data)
        
        # Verify transcription was submitted
        mock_submit.assert_called_once()
        call_args = mock_submit.call_args[0]
        assert np.array_equal(call_args[0], audio_array)
        assert call_args[1].startswith("ws_192.168.1.100:12345:")

    @pytest.mark.asyncio
    async def test_handle_websocket_unexpected_data_size(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test handling of unexpected data sizes"""
        uid = "test_call_123"
        wrong_size_data = b'\x00' * 500  
        
        # Simulate UID, then wrong-sized data, then disconnect
        mock_websocket.receive_bytes.side_effect = [
            uid.encode('utf-8') + b'\r',  # UID
            wrong_size_data,  # Wrong size data
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch('app.streaming.websocket_server.logger') as mock_logger:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify warning was logged
        warning_calls = [call for call in mock_logger.warning.call_args_list 
                        if "Unexpected data size" in str(call)]
        assert len(warning_calls) >= 1
        
        # Verify audio buffer was NOT used for wrong-sized data
        mock_audio_buffer.add_chunk.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_websocket_uid_multiple_bytes(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test UID extraction with data split across multiple receives"""
        uid = "test_call_123"
        
        # Split UID across multiple receives
        mock_websocket.receive_bytes.side_effect = [
            b'test_',  # Partial UID
            b'call_',  # Continue UID  
            b'123\r',  # Complete UID with CR
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch('app.streaming.websocket_server.logger') as mock_logger:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify UID was logged correctly
        uid_log_calls = [call for call in mock_logger.info.call_args_list 
                        if "uid=test_call_123" in str(call)]
        assert len(uid_log_calls) >= 1

    @pytest.mark.asyncio
    async def test_handle_websocket_exception_handling(self, websocket_manager, mock_websocket):
        """Test exception handling during WebSocket processing"""
        # Mock to raise exception during receive
        mock_websocket.receive_bytes.side_effect = Exception("WebSocket error")
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer'), \
             patch('app.streaming.websocket_server.logger') as mock_logger:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify error was logged
        error_calls = [call for call in mock_logger.error.call_args_list 
                      if "Error handling connection" in str(call)]
        assert len(error_calls) >= 1

    @pytest.mark.asyncio
    async def test_handle_websocket_connection_tracking(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test that connections are properly tracked"""
        uid = "test_call_123"
        
        # Use a custom side effect that keeps the connection alive after UID
        async def mock_receive_sequence():
            # First call: return UID
            if not hasattr(mock_receive_sequence, 'call_count'):
                mock_receive_sequence.call_count = 0
            
            if mock_receive_sequence.call_count == 0:
                mock_receive_sequence.call_count += 1
                return uid.encode('utf-8') + b'\r'
            else:
                # For subsequent calls, wait a bit then raise WebSocketDisconnect
                await asyncio.sleep(0.1)
                raise WebSocketDisconnect()
        
        mock_websocket.receive_bytes.side_effect = mock_receive_sequence
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer):
            # Start connection handling in background task
            task = asyncio.create_task(websocket_manager.handle_websocket(mock_websocket))
            
            # Give it time to process UID and set up connection
            await asyncio.sleep(0.05)
            
            # Verify connection was added
            assert len(websocket_manager.active_connections) == 1
            
            connection_id = list(websocket_manager.active_connections.keys())[0]
            connection_data = websocket_manager.active_connections[connection_id]
            assert connection_data["websocket"] == mock_websocket
            assert connection_data["buffer"] == mock_audio_buffer
            assert connection_data["client_info"] == mock_websocket.client
            
            # Wait for the task to complete (it should finish due to WebSocketDisconnect)
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except (asyncio.TimeoutError, WebSocketDisconnect):
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Verify connection was cleaned up
            assert len(websocket_manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_submit_transcription_success(self, websocket_manager):
        """Test successful transcription submission"""
        connection_id = "ws_192.168.1.100:12345:123456"
        audio_array = np.array([0.1, 0.2, 0.3] * 1000, dtype=np.float32)
        
        mock_task = Mock()
        mock_task.id = "task_123"
        
        with patch('app.streaming.websocket_server.process_streaming_audio_task') as mock_task_func:
            mock_task_func.delay.return_value = mock_task
            
            await websocket_manager._submit_transcription(audio_array, connection_id)
        
        # Verify task was submitted with correct parameters
        mock_task_func.delay.assert_called_once()
        call_kwargs = mock_task_func.delay.call_args.kwargs
        
        assert 'audio_bytes' in call_kwargs
        assert call_kwargs['connection_id'] == connection_id
        assert call_kwargs['language'] == "sw"
        assert call_kwargs['sample_rate'] == 16000
        assert call_kwargs['duration_seconds'] == 5.0
        assert call_kwargs['is_streaming'] is True
        
        # Verify audio conversion
        expected_audio_bytes = (audio_array * 32768.0).astype(np.int16).tobytes()
        assert call_kwargs['audio_bytes'] == expected_audio_bytes
        
        # Verify filename format
        filename = call_kwargs['filename']
        assert filename.startswith(f"ws_stream_{connection_id}_")
        assert filename.endswith(".wav")

    @pytest.mark.asyncio
    async def test_submit_transcription_failure(self, websocket_manager):
        """Test transcription submission failure handling"""
        connection_id = "ws_test_connection"
        audio_array = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        with patch('app.streaming.websocket_server.process_streaming_audio_task') as mock_task_func, \
             patch('app.streaming.websocket_server.logger') as mock_logger:
            
            mock_task_func.delay.side_effect = Exception("Task submission failed")
            
            # Should not raise exception, just log error
            await websocket_manager._submit_transcription(audio_array, connection_id)
        
        # Verify error was logged
        error_calls = [call for call in mock_logger.error.call_args_list 
                      if "Failed to submit transcription" in str(call)]
        assert len(error_calls) >= 1

    def test_get_status_no_connections(self, websocket_manager):
        """Test status when no connections are active"""
        status = websocket_manager.get_status()
        
        assert status['websocket_server_active'] is True
        assert status['active_connections'] == 0
        assert status['connections'] == {}
        assert status['transcription_method'] == "celery_workers"
        assert status['protocol'] == "websocket"

    def test_get_status_with_connections(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test status with active connections"""
        connection_id = "ws_192.168.1.100:12345:123456"
        
        # Set up active connection
        websocket_manager.active_connections[connection_id] = {
            "websocket": mock_websocket,
            "buffer": mock_audio_buffer,
            "client_info": mock_websocket.client
        }
        
        status = websocket_manager.get_status()
        
        assert status['websocket_server_active'] is True
        assert status['active_connections'] == 1
        assert connection_id in status['connections']
        
        connection_data = status['connections'][connection_id]
        assert 'client' in connection_data
        assert 'buffer_stats' in connection_data
        assert connection_data['buffer_stats'] == mock_audio_buffer.get_stats.return_value

    @pytest.mark.asyncio
    async def test_audio_processing_no_uid(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test that audio processing doesn't occur without UID"""
        # Simulate direct audio data without UID phase
        audio_data = b'\x00' * 640
        
        mock_websocket.receive_bytes.side_effect = [
            audio_data,  # Audio data without UID
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch.object(websocket_manager, '_submit_transcription') as mock_submit:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify transcription was not submitted (no UID received)
        mock_submit.assert_not_called()

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_disconnect(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test proper cleanup when WebSocket disconnects"""
        uid = "test_call_123"
        
        mock_websocket.receive_bytes.side_effect = [
            uid.encode('utf-8') + b'\r',  # UID
            WebSocketDisconnect()  # Immediate disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer):
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify connection was cleaned up
        assert len(websocket_manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_exception(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test proper cleanup when exception occurs"""
        uid = "test_call_123"
        
        mock_websocket.receive_bytes.side_effect = [
            uid.encode('utf-8') + b'\r',  # UID
            Exception("Unexpected error")  # Exception
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer):
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify connection was cleaned up even on exception
        assert len(websocket_manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_multiple_audio_chunks_processing(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test processing multiple audio chunks"""
        uid = "test_call_123"
        audio_data = b'\x00' * 640
        audio_array = np.array([0.1, 0.2, 0.3] * 1000, dtype=np.float32)
        
        # First chunk returns None, second returns audio array
        mock_audio_buffer.add_chunk.side_effect = [None, audio_array]
        
        mock_websocket.receive_bytes.side_effect = [
            uid.encode('utf-8') + b'\r',  # UID
            audio_data,  # First audio chunk
            audio_data,  # Second audio chunk  
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch.object(websocket_manager, '_submit_transcription') as mock_submit:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify audio buffer was called twice
        assert mock_audio_buffer.add_chunk.call_count == 2
        
        # Verify transcription was submitted only once (when audio_array was returned)
        mock_submit.assert_called_once()

    def test_filename_generation_format(self, websocket_manager):
        """Test that generated filenames follow expected format"""
        connection_id = "ws_192.168.1.100:12345:123456"
        audio_array = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        with patch('app.streaming.websocket_server.process_streaming_audio_task') as mock_task_func, \
             patch('app.streaming.websocket_server.datetime') as mock_datetime:
            
            # Mock datetime to return predictable timestamp - need to mock the actual format used
            mock_now = Mock()
            mock_now.strftime.return_value = "123456789"  # This gets truncated to "123456" by [:-3]
            mock_datetime.now.return_value = mock_now
            
            mock_task_func.delay.return_value = Mock(id="task_123")
            
            asyncio.run(websocket_manager._submit_transcription(audio_array, connection_id))
        
        # Verify filename format
        call_kwargs = mock_task_func.delay.call_args.kwargs
        filename = call_kwargs['filename']
        assert filename.startswith(f"ws_stream_{connection_id}_")
        assert filename.endswith(".wav")
        # The actual code uses [:-3] which truncates to "123456"
        assert "123456" in filename

    @pytest.mark.asyncio
    async def test_audio_conversion_accuracy(self, websocket_manager):
        """Test audio data conversion accuracy"""
        connection_id = "test_connection"
        
        # Test specific audio values
        test_audio = np.array([0.5, -0.5, 0.0, 1.0, -1.0], dtype=np.float32)
        expected_bytes = (test_audio * 32768.0).astype(np.int16).tobytes()
        
        with patch('app.streaming.websocket_server.process_streaming_audio_task') as mock_task_func:
            mock_task_func.delay.return_value = Mock(id="task_123")
            
            await websocket_manager._submit_transcription(test_audio, connection_id)
        
        # Verify exact audio conversion
        call_kwargs = mock_task_func.delay.call_args.kwargs
        assert call_kwargs['audio_bytes'] == expected_bytes

    @pytest.mark.asyncio
    async def test_concurrent_connections(self, websocket_manager):
        """Test handling multiple concurrent WebSocket connections"""
        # Create multiple mock websockets
        websockets = []
        for i in range(3):
            ws = AsyncMock()
            ws.accept = AsyncMock()
            client_mock = Mock()
            client_mock.host = f"192.168.1.{100 + i}"
            client_mock.port = 12345 + i
            ws.client = client_mock
            ws.receive_bytes.side_effect = [
                f"call_{i}".encode('utf-8') + b'\r',
                WebSocketDisconnect()
            ]
            websockets.append(ws)
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer'):
            # Handle all connections concurrently
            tasks = [websocket_manager.handle_websocket(ws) for ws in websockets]
            await asyncio.gather(*tasks)
        
        # All connections should be cleaned up
        assert len(websocket_manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_uid_with_no_carriage_return(self, websocket_manager, mock_websocket, mock_audio_buffer):
        """Test UID handling when no carriage return is received"""
        # Send UID data without carriage return, then disconnect
        mock_websocket.receive_bytes.side_effect = [
            b'incomplete_uid_data',  # UID without CR
            WebSocketDisconnect()  # Disconnect
        ]
        
        with patch('app.streaming.websocket_server.AsteriskAudioBuffer', return_value=mock_audio_buffer), \
             patch('app.streaming.websocket_server.logger') as mock_logger:
            
            await websocket_manager.handle_websocket(mock_websocket)
        
        # Verify no UID was logged (no CR received)
        uid_log_calls = [call for call in mock_logger.info.call_args_list 
                        if "uid=" in str(call)]
        assert len(uid_log_calls) == 0