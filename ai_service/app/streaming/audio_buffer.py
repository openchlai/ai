# app/streaming/audio_buffer.py
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AsteriskAudioBuffer:
    """Enhanced buffer for 16kHz 16-bit mixed-mono audio from Asterisk with configurable windows"""
    
    def __init__(self, window_duration_seconds: float = 5.0, enable_overlapping: bool = True):
        self.sample_rate = 16000
        self.window_duration = window_duration_seconds
        self.window_size_bytes = int(window_duration_seconds * self.sample_rate * 2)  # 2 bytes per sample
        self.buffer = bytearray()
        self.offset = 0
        self.chunk_count = 0
        
        # Enhanced buffering options
        self.enable_overlapping = enable_overlapping
        self.overlap_ratio = 0.25 if enable_overlapping else 0  # 25% overlap between windows
        self.overlap_bytes = int(self.window_size_bytes * self.overlap_ratio)
        
        # Flexible chunk sizes - observed patterns from TCP fragmentation
        self.common_chunk_sizes = {168, 240, 88, 320}  # Common sizes we've observed
        self.target_chunk_size = 320  # Ideal 10ms chunk size (160 samples * 2 bytes)
        self.size_statistics = {}  # Track frequency of different chunk sizes
        
        logger.info(f"🎵 AudioBuffer initialized: {window_duration_seconds}s windows, "
                   f"{self.window_size_bytes} bytes, overlap: {self.overlap_ratio*100:.0f}%")
        
    def add_chunk(self, chunk: bytes) -> Optional[np.ndarray]:
        """
        Add variable-size audio chunks, return audio array when window duration is ready
        Mixed-mono audio contains both caller and agent voices in one channel
        Handles TCP fragmentation patterns: 168+168+240=576, 168+88=256, etc.
        Supports configurable window duration and overlapping for better Whisper performance
        """
        chunk_size = len(chunk)
        
        # Track chunk size statistics
        self.size_statistics[chunk_size] = self.size_statistics.get(chunk_size, 0) + 1
        
        # Log chunk size patterns occasionally for monitoring
        if self.chunk_count > 0 and self.chunk_count % 100 == 0:
            total_chunks = sum(self.size_statistics.values())
            size_breakdown = {size: count/total_chunks*100 for size, count in self.size_statistics.items()}
            logger.info(f"📊 Chunk size distribution after {total_chunks} chunks: {size_breakdown}")
        
        self.buffer.extend(chunk)
        self.chunk_count += 1
        current_size = len(self.buffer)
        
        # Check if we have enough audio for configured window duration
        if (current_size - self.offset) >= self.window_size_bytes:
            # Extract window data from the current offset
            window_start = self.offset
            window_end = self.offset + self.window_size_bytes
            window_data = self.buffer[window_start:window_end]
            
            # Convert to numpy array (same format as Whisper preprocessing)
            audio_array = np.frombuffer(window_data, np.int16).flatten().astype(np.float32) / 32768.0
            
            # Calculate step size for next window (with overlap support)
            if self.enable_overlapping:
                step_size = self.window_size_bytes - self.overlap_bytes
            else:
                step_size = self.window_size_bytes
            
            # Move offset forward by step size
            self.offset += step_size
            
            # Reset buffer when it gets too large (keep only recent data)
            max_buffer_duration = max(50.0, self.window_duration * 10)  # At least 50s or 10x window duration
            max_buffer_size = int(max_buffer_duration * self.sample_rate * 2)
            
            if current_size >= max_buffer_size:
                # Keep only the most recent data
                recent_data = self.buffer[self.offset:]
                self.buffer = bytearray(recent_data)
                self.offset = 0
                logger.info(f"🔄 Buffer reset after {max_buffer_duration:.0f} seconds")
                
            logger.debug(f"🎵 Audio window ready: {len(audio_array)} samples "
                        f"({len(audio_array)/self.sample_rate:.1f}s, overlap: {self.overlap_ratio*100:.0f}%)")
            return audio_array
            
        return None
        
    def get_stats(self) -> dict:
        """Get buffer statistics including chunk size patterns and configuration"""
        return {
            "configuration": {
                "window_duration_seconds": self.window_duration,
                "window_size_bytes": self.window_size_bytes,
                "enable_overlapping": self.enable_overlapping,
                "overlap_ratio": self.overlap_ratio,
                "overlap_bytes": self.overlap_bytes
            },
            "buffer_state": {
                "buffer_size_bytes": len(self.buffer),
                "buffer_duration_seconds": len(self.buffer) / (self.sample_rate * 2),
                "current_offset": self.offset,
                "window_ready": (len(self.buffer) - self.offset) >= self.window_size_bytes,
                "bytes_until_window": max(0, self.window_size_bytes - (len(self.buffer) - self.offset))
            },
            "chunk_statistics": {
                "chunks_received": self.chunk_count,
                "chunk_size_distribution": self.size_statistics,
                "average_chunk_size": sum(size * count for size, count in self.size_statistics.items()) / max(1, sum(self.size_statistics.values())),
                "most_common_chunk_size": max(self.size_statistics.keys(), key=self.size_statistics.get) if self.size_statistics else 0
            }
        }