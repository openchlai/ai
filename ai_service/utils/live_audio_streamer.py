# utils/live_audio_streamer.py - Real-time audio streaming and monitoring

import asyncio
import json
import logging
import numpy as np
import soundfile as sf
import tempfile
import os
import base64
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Set, List
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class AudioStreamChunk:
    """Information about a streamed audio chunk"""
    call_id: str
    chunk_id: int
    timestamp: datetime
    duration_seconds: float
    sample_rate: int
    audio_b64: str  # Base64 encoded audio data
    format: str = "wav"
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class TranscriptionUpdate:
    """Real-time transcription update"""
    call_id: str
    segment_id: int
    timestamp: datetime
    transcript: str
    processing_duration: float
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class LiveAudioStreamer:
    """
    Real-time audio streaming system for monitoring and debugging
    
    Provides:
    - Live audio streaming via WebSocket
    - Real-time transcription overlay
    - Audio quality monitoring
    - Call session correlation
    """
    
    def __init__(self, max_clients: int = 10, buffer_size: int = 1024 * 64):
        self.max_clients = max_clients
        self.buffer_size = buffer_size
        
        # Active WebSocket connections
        self.ws_connections: Dict[str, Set] = {}  # call_id -> set of websockets
        self.global_connections: Set = set()      # Global monitoring connections
        
        # Audio streaming state
        self.active_streams: Dict[str, Dict] = {}  # call_id -> stream info
        self.chunk_counters: Dict[str, int] = {}   # call_id -> chunk_id
        
        # Configuration
        self.enable_streaming = os.getenv("ENABLE_LIVE_AUDIO_STREAMING", "true").lower() == "true"
        self.audio_format = os.getenv("LIVE_AUDIO_FORMAT", "wav")  # wav, mp3, ogg
        self.streaming_sample_rate = int(os.getenv("LIVE_AUDIO_SAMPLE_RATE", "16000"))
        
        logger.info(f"🎵 Live audio streamer initialized: "
                   f"streaming={self.enable_streaming}, "
                   f"format={self.audio_format}, "
                   f"rate={self.streaming_sample_rate}Hz")
    
    def is_streaming_enabled(self) -> bool:
        """Check if streaming is enabled"""
        return self.enable_streaming
    
    def start_call_stream(self, call_id: str, metadata: Dict[str, Any] = None) -> bool:
        """Start streaming for a specific call"""
        if not self.enable_streaming:
            return False
            
        try:
            self.active_streams[call_id] = {
                "start_time": datetime.now(timezone.utc),
                "metadata": metadata or {},
                "total_chunks": 0,
                "total_duration": 0.0,
                "active": True
            }
            
            self.chunk_counters[call_id] = 0
            self.ws_connections[call_id] = set()
            
            logger.info(f"🎵 Started audio streaming for call {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start streaming for call {call_id}: {e}")
            return False
    
    async def stream_audio_chunk(self, call_id: str, audio_array: np.ndarray, 
                                sample_rate: int = 16000, metadata: Dict[str, Any] = None) -> bool:
        """Stream an audio chunk to connected clients"""
        if not self.enable_streaming or call_id not in self.active_streams:
            return False
        
        try:
            # Update chunk counter
            self.chunk_counters[call_id] += 1
            chunk_id = self.chunk_counters[call_id]
            
            # Calculate duration
            duration = len(audio_array) / sample_rate
            
            # Convert audio to the desired streaming format
            audio_b64 = await self._encode_audio_for_streaming(
                audio_array, sample_rate, self.audio_format
            )
            
            if not audio_b64:
                return False
            
            # Create stream chunk
            stream_chunk = AudioStreamChunk(
                call_id=call_id,
                chunk_id=chunk_id,
                timestamp=datetime.now(timezone.utc),
                duration_seconds=duration,
                sample_rate=self.streaming_sample_rate,
                audio_b64=audio_b64,
                format=self.audio_format
            )
            
            # Update stream statistics
            stream_info = self.active_streams[call_id]
            stream_info["total_chunks"] += 1
            stream_info["total_duration"] += duration
            stream_info["last_chunk_time"] = datetime.now(timezone.utc)
            
            # Send to connected WebSocket clients
            await self._broadcast_audio_chunk(call_id, stream_chunk, metadata)
            
            logger.debug(f"🎵 Streamed chunk {chunk_id} for call {call_id}: "
                        f"{duration:.2f}s, {len(audio_array)} samples")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stream audio chunk for call {call_id}: {e}")
            return False
    
    async def _encode_audio_for_streaming(self, audio_array: np.ndarray, 
                                        sample_rate: int, format: str) -> Optional[str]:
        """Encode audio data for streaming"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Resample if needed
            if sample_rate != self.streaming_sample_rate:
                # Simple resampling (you might want to use librosa.resample for better quality)
                ratio = self.streaming_sample_rate / sample_rate
                new_length = int(len(audio_array) * ratio)
                audio_array = np.interp(
                    np.linspace(0, len(audio_array), new_length),
                    np.arange(len(audio_array)),
                    audio_array
                )
            
            # Write audio file
            sf.write(temp_path, audio_array, self.streaming_sample_rate, format=format.upper())
            
            # Read as base64
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Cleanup
            os.unlink(temp_path)
            
            return audio_b64
            
        except Exception as e:
            logger.error(f"❌ Failed to encode audio for streaming: {e}")
            return None
    
    async def _broadcast_audio_chunk(self, call_id: str, chunk: AudioStreamChunk, 
                                   metadata: Dict[str, Any] = None):
        """Broadcast audio chunk to connected WebSocket clients"""
        if not self.ws_connections.get(call_id) and not self.global_connections:
            return
        
        # Prepare message
        message = {
            "type": "audio_chunk",
            "data": chunk.to_dict()
        }
        
        if metadata:
            message["metadata"] = metadata
        
        message_json = json.dumps(message)
        
        # Send to call-specific connections
        if call_id in self.ws_connections:
            await self._send_to_websockets(self.ws_connections[call_id], message_json)
        
        # Send to global monitoring connections
        await self._send_to_websockets(self.global_connections, message_json)
    
    async def stream_transcription_update(self, call_id: str, segment_id: int, 
                                        transcript: str, processing_duration: float,
                                        confidence: Optional[float] = None):
        """Stream transcription update to connected clients"""
        if not self.enable_streaming:
            return
        
        try:
            update = TranscriptionUpdate(
                call_id=call_id,
                segment_id=segment_id,
                timestamp=datetime.now(timezone.utc),
                transcript=transcript,
                processing_duration=processing_duration,
                confidence=confidence
            )
            
            message = {
                "type": "transcription_update",
                "data": update.to_dict()
            }
            
            message_json = json.dumps(message)
            
            # Send to call-specific connections
            if call_id in self.ws_connections:
                await self._send_to_websockets(self.ws_connections[call_id], message_json)
            
            # Send to global monitoring connections
            await self._send_to_websockets(self.global_connections, message_json)
            
            logger.debug(f"📝 Streamed transcription update for call {call_id}: '{transcript[:50]}...'")
            
        except Exception as e:
            logger.error(f"❌ Failed to stream transcription update: {e}")
    
    async def _send_to_websockets(self, websockets: Set, message: str):
        """Send message to a set of WebSocket connections"""
        if not websockets:
            return
        
        # Send to all connections, remove closed ones
        closed_connections = set()
        for ws in websockets:
            try:
                await ws.send(message)
            except Exception as e:
                logger.debug(f"🔌 WebSocket connection closed: {e}")
                closed_connections.add(ws)
        
        # Remove closed connections
        for ws in closed_connections:
            websockets.discard(ws)
    
    def add_websocket_connection(self, websocket, call_id: Optional[str] = None):
        """Add a WebSocket connection for streaming"""
        if call_id:
            if call_id not in self.ws_connections:
                self.ws_connections[call_id] = set()
            self.ws_connections[call_id].add(websocket)
            logger.info(f"🔌 Added WebSocket connection for call {call_id}")
        else:
            self.global_connections.add(websocket)
            logger.info(f"🔌 Added global WebSocket connection")
    
    def remove_websocket_connection(self, websocket, call_id: Optional[str] = None):
        """Remove a WebSocket connection"""
        try:
            if call_id and call_id in self.ws_connections:
                self.ws_connections[call_id].discard(websocket)
                if not self.ws_connections[call_id]:
                    del self.ws_connections[call_id]
                logger.info(f"🔌 Removed WebSocket connection for call {call_id}")
            else:
                self.global_connections.discard(websocket)
                logger.info(f"🔌 Removed global WebSocket connection")
        except Exception as e:
            logger.error(f"❌ Error removing WebSocket connection: {e}")
    
    def stop_call_stream(self, call_id: str) -> Dict[str, Any]:
        """Stop streaming for a call and return summary"""
        if call_id not in self.active_streams:
            return {}
        
        try:
            stream_info = self.active_streams[call_id]
            stream_info["active"] = False
            stream_info["end_time"] = datetime.now(timezone.utc)
            
            # Calculate summary
            total_duration = stream_info.get("total_duration", 0.0)
            total_chunks = stream_info.get("total_chunks", 0)
            
            summary = {
                "call_id": call_id,
                "total_chunks": total_chunks,
                "total_duration_seconds": total_duration,
                "average_chunk_duration": total_duration / total_chunks if total_chunks > 0 else 0,
                "start_time": stream_info["start_time"].isoformat(),
                "end_time": stream_info["end_time"].isoformat()
            }
            
            # Notify connected clients that stream ended
            asyncio.create_task(self._broadcast_stream_end(call_id, summary))
            
            # Cleanup
            if call_id in self.ws_connections:
                del self.ws_connections[call_id]
            if call_id in self.chunk_counters:
                del self.chunk_counters[call_id]
            if call_id in self.active_streams:
                del self.active_streams[call_id]
            
            logger.info(f"🏁 Stopped audio streaming for call {call_id}: "
                       f"{total_chunks} chunks, {total_duration:.1f}s")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to stop streaming for call {call_id}: {e}")
            return {"error": str(e)}
    
    async def _broadcast_stream_end(self, call_id: str, summary: Dict[str, Any]):
        """Broadcast stream end notification"""
        message = {
            "type": "stream_end",
            "call_id": call_id,
            "summary": summary
        }
        
        message_json = json.dumps(message)
        await self._send_to_websockets(self.global_connections, message_json)
    
    def get_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active streams"""
        return {
            call_id: {
                **stream_info,
                "start_time": stream_info["start_time"].isoformat(),
                "last_chunk_time": stream_info.get("last_chunk_time", {}).isoformat() 
                    if stream_info.get("last_chunk_time") else None,
                "connected_clients": len(self.ws_connections.get(call_id, set()))
            }
            for call_id, stream_info in self.active_streams.items()
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global streaming statistics"""
        return {
            "enabled": self.enable_streaming,
            "active_streams": len(self.active_streams),
            "global_connections": len(self.global_connections),
            "call_specific_connections": sum(len(conns) for conns in self.ws_connections.values()),
            "total_connections": len(self.global_connections) + sum(len(conns) for conns in self.ws_connections.values()),
            "audio_format": self.audio_format,
            "sample_rate": self.streaming_sample_rate
        }

# Global instance
_live_audio_streamer: Optional[LiveAudioStreamer] = None

def get_live_audio_streamer() -> Optional[LiveAudioStreamer]:
    """Get the global live audio streamer instance"""
    global _live_audio_streamer
    
    if _live_audio_streamer is None:
        enable_streaming = os.getenv("ENABLE_LIVE_AUDIO_STREAMING", "true").lower() == "true"
        if enable_streaming:
            _live_audio_streamer = LiveAudioStreamer()
        else:
            return None
    
    return _live_audio_streamer

def cleanup_live_audio_streamer():
    """Cleanup the global live audio streamer"""
    global _live_audio_streamer
    if _live_audio_streamer:
        # Close all active streams
        for call_id in list(_live_audio_streamer.active_streams.keys()):
            _live_audio_streamer.stop_call_stream(call_id)
        _live_audio_streamer = None

# CLI utilities
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Audio Streamer utilities")
    parser.add_argument("--test-encoding", help="Test audio encoding with file")
    parser.add_argument("--format", default="wav", help="Audio format for testing")
    
    args = parser.parse_args()
    
    if args.test_encoding:
        # Test audio encoding
        streamer = LiveAudioStreamer()
        
        # Load test audio
        audio_data, sample_rate = sf.read(args.test_encoding)
        
        # Test encoding
        asyncio.run(streamer._encode_audio_for_streaming(audio_data, sample_rate, args.format))
        print(f"✅ Successfully encoded {args.test_encoding} as {args.format}")
    else:
        print("Use --help for available options")