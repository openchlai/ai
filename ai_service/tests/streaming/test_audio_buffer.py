import pytest
import numpy as np
import logging
from unittest.mock import patch

from app.streaming.audio_buffer import AsteriskAudioBuffer, logger

@pytest.fixture
def audio_buffer():
    """Fixture to provide a fresh AsteriskAudioBuffer instance for each test"""
    return AsteriskAudioBuffer()

def create_mock_chunk(size: int, pattern: bytes = b'\x00') -> bytes:
    """Helper to create mock audio chunk of specified size"""
    return pattern * (size // len(pattern))

class TestAsteriskAudioBuffer:
    """Tests for the AsteriskAudioBuffer class"""

    def test_initialization(self, audio_buffer):
        """Test initialization with correct defaults"""
        assert audio_buffer.sample_rate == 16000
        assert audio_buffer.window_size_bytes == 160000
        assert len(audio_buffer.buffer) == 0
        assert audio_buffer.offset == 0
        assert audio_buffer.chunk_count == 0

    def test_add_chunk_no_window_ready(self, audio_buffer):
        """Test adding chunks without reaching 5-second window"""
        num_chunks = 499
        
        for _ in range(num_chunks):
            chunk = create_mock_chunk(320)
            result = audio_buffer.add_chunk(chunk)
            assert result is None
            
        assert audio_buffer.chunk_count == num_chunks
        assert len(audio_buffer.buffer) == num_chunks * 320
        assert audio_buffer.offset == 0

    def test_add_chunk_window_ready(self, audio_buffer):
        """Test window extraction when 5-second threshold is reached"""
        for _ in range(499):
            audio_buffer.add_chunk(create_mock_chunk(320))
        
        with patch.object(logger, 'debug') as mock_debug:
            chunk = create_mock_chunk(320, b'\x01\x02')
            audio_array = audio_buffer.add_chunk(chunk)
            
            assert isinstance(audio_array, np.ndarray)
            assert len(audio_array) == 80000
            assert audio_buffer.offset == 160000
            
            expected_sample = np.frombuffer(b'\x01\x02', np.int16)[0] / 32768.0
            # The new chunk's data should be at the very end of the window.
            # So, we check the last sample.
            assert np.isclose(audio_array[-1], expected_sample)
            
            mock_debug.assert_called_once()
            assert "5.0s" in mock_debug.call_args[0][0]

    def test_sliding_window_multiple_windows(self, audio_buffer):
        """Test sliding window produces multiple windows"""
        windows = []
        
        for i in range(1000):
            chunk = create_mock_chunk(320)
            result = audio_buffer.add_chunk(chunk)
            if result is not None:
                windows.append(result)
                
        assert len(windows) == 2
        assert audio_buffer.offset == 320000
        assert audio_buffer.chunk_count == 1000
        
    def test_buffer_reset_mechanism(self, audio_buffer):
        """Test buffer reset after accumulating enough data"""
        # Add enough chunks to trigger multiple windows AND have remaining data
        # This ensures there's actually data left to reset
        num_chunks = 5001  # This leaves some data after the 10th window
        
        for i in range(num_chunks):
            audio_buffer.add_chunk(create_mock_chunk(320))
        
        # The reset should have been triggered during the loop above
        # Check that buffer was actually reset by verifying offset is 0
        assert audio_buffer.offset == 0
        # And verify there's some remaining data
        assert len(audio_buffer.buffer) > 0
        
        # Alternative test: Manually verify reset behavior
        # by checking the buffer state after many chunks
        stats = audio_buffer.get_stats()
        assert stats["buffer_size_bytes"] < 160000 * 10  # Buffer was reset

    def test_add_chunk_different_sizes(self, audio_buffer):
        """Test that chunks of different sizes are accepted (no validation in original code)"""
        audio_buffer.add_chunk(create_mock_chunk(320))
        audio_buffer.add_chunk(create_mock_chunk(319))
        audio_buffer.add_chunk(create_mock_chunk(100))
        
        assert audio_buffer.chunk_count == 3
        assert len(audio_buffer.buffer) == 320 + 319 + 100

    def test_get_stats(self, audio_buffer):
        """Test statistics reporting"""
        stats = audio_buffer.get_stats()
        assert stats == {
            "buffer_size_bytes": 0,
            "buffer_duration_seconds": 0.0,
            "chunks_received": 0,
            "window_ready": False
        }
        
        for _ in range(250):
            audio_buffer.add_chunk(create_mock_chunk(320))
            
        stats = audio_buffer.get_stats()
        assert stats["buffer_size_bytes"] == 80000
        assert stats["buffer_duration_seconds"] == pytest.approx(2.5)
        assert stats["chunks_received"] == 250
        assert stats["window_ready"] is False
        
        for _ in range(250):
            audio_buffer.add_chunk(create_mock_chunk(320))
            
        stats = audio_buffer.get_stats()
        # The window is extracted, and the offset moves. The remaining data is not a full window.
        assert stats["window_ready"] is False
        
    def test_buffer_retains_data_after_window(self, audio_buffer):
        """Test buffer retains recent data after window extraction"""
        for _ in range(500):
            audio_buffer.add_chunk(create_mock_chunk(320))
            
        assert len(audio_buffer.buffer) == 500 * 320
        assert audio_buffer.offset == 160000
        
        audio_buffer.add_chunk(create_mock_chunk(320))
        assert len(audio_buffer.buffer) == 501 * 320
        assert audio_buffer.offset == 160000

    def test_audio_conversion_accuracy(self, audio_buffer):
        """Test audio conversion to float32 is correct"""
        max_positive = b'\xFF\x7F' * 160
        # Add 499 chunks to get the buffer to the 5-second mark
        for _ in range(499):
            audio_buffer.add_chunk(create_mock_chunk(320))

        # Add the chunk with the specific data to be at the end of the window
        audio_array = audio_buffer.add_chunk(max_positive)

        # The last sample of the returned array should be the max positive value
        assert np.isclose(audio_array[-1], 32767/32768, atol=1e-5)
        
        # Test min negative value (0x8000 = -32768)
        audio_buffer = AsteriskAudioBuffer()
        min_negative = b'\x00\x80' * 160
        for _ in range(499):
            audio_buffer.add_chunk(create_mock_chunk(320))
        audio_array = audio_buffer.add_chunk(min_negative)
        assert np.isclose(audio_array[-1], -1.0, atol=1e-5)