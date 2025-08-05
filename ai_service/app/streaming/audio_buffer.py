# app/streaming/audio_buffer.py
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AsteriskAudioBuffer:
    """Simple buffer for 16kHz 16-bit mono audio from Asterisk"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.window_size_bytes = 160000  # 5 seconds = 5 * 16000 * 2 bytes
        self.buffer = bytearray()
        self.offset = 0
        self.chunk_count = 0
        
    def add_chunk(self, chunk: bytes) -> Optional[np.ndarray]:
        """
        Add 20ms chunk (640 bytes), return audio array when 5-second window ready
        """
        self.buffer.extend(chunk)
        self.chunk_count += 1
        current_size = len(self.buffer)
        
        # Check if we have 5 seconds of audio (exactly like original aii_server.py)
        if (current_size - self.offset) >= self.window_size_bytes:
            # Extract exactly 5 seconds from the current offset
            window_start = self.offset
            window_end = self.offset + self.window_size_bytes
            window_data = self.buffer[window_start:window_end]
            
            # Convert to numpy array (your specified format)
            audio_array = np.frombuffer(window_data, np.int16).flatten().astype(np.float32) / 32768.0
            
            # Sliding window - move offset forward by 5 seconds
            self.offset += self.window_size_bytes
            
            # Reset buffer when it gets too large (keep only recent data)
            if current_size >= self.window_size_bytes * 10:  # Reset after 50 seconds
                # Keep only the most recent 5 seconds of data  
                recent_data = self.buffer[self.offset:]
                self.buffer = bytearray(recent_data)
                self.offset = 0
                logger.info(f"🔄 Buffer reset after 50 seconds")
                
            logger.debug(f"🎵 Audio window ready: {len(audio_array)} samples ({len(audio_array)/16000:.1f}s)")
            return audio_array
            
        return None
        
    def get_stats(self) -> dict:
        """Get buffer statistics"""
        return {
            "buffer_size_bytes": len(self.buffer),
            "buffer_duration_seconds": len(self.buffer) / (self.sample_rate * 2),
            "chunks_received": self.chunk_count,
            "window_ready": (len(self.buffer) - self.offset) >= self.window_size_bytes
        }