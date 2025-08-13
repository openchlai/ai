# app/streaming/tcp_server.py - Updated to use Celery and Call Session Management
import asyncio
import logging
import numpy as np
from typing import Dict, Optional
from datetime import datetime

from .audio_buffer import AsteriskAudioBuffer
from .call_session_manager import call_session_manager
from ..tasks.audio_tasks import process_streaming_audio_task  # Use your existing Celery tasks
# Robust imports for utils (handle both development and Celery worker environments)
try:
    from utils.call_data_logger import get_call_logger, finalize_call_logger
    from utils.live_audio_streamer import get_live_audio_streamer
except ImportError:
    # Fallback: add project root to path and retry
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from utils.call_data_logger import get_call_logger, finalize_call_logger
    from utils.live_audio_streamer import get_live_audio_streamer

logger = logging.getLogger(__name__)

class AsteriskTCPServer:
    """TCP server for Asterisk audio input - uses Celery workers"""
    
    def __init__(self, model_loader=None, window_duration: float = 15.0, enable_overlapping: bool = True):
        # Don't need model_loader anymore - we'll use Celery
        self.active_connections: Dict[str, Dict] = {}  # Maps call_id to connection info
        self.server = None
        
        # Configurable audio buffer settings for better Whisper performance
        self.window_duration = window_duration  # Default 15 seconds for better Whisper accuracy
        self.enable_overlapping = enable_overlapping
        
        # Enhanced logging and streaming configuration
        import os
        self.enable_call_logging = os.getenv("ENABLE_CALL_DATA_LOGGING", "true").lower() == "true"
        self.enable_tcp_packet_logging = os.getenv("ENABLE_TCP_PACKET_LOGGING", "true").lower() == "true"
        self.enable_live_streaming = os.getenv("ENABLE_LIVE_AUDIO_STREAMING", "true").lower() == "true"
        
        # Initialize live audio streamer
        self.live_streamer = get_live_audio_streamer() if self.enable_live_streaming else None
        
        logger.info(f"🎙️ TCP Server configured: {window_duration}s windows, overlapping: {enable_overlapping}")
        logger.info(f"📝 Call logging: {self.enable_call_logging}, TCP packet logging: {self.enable_tcp_packet_logging}")
        logger.info(f"🎵 Live streaming: {self.enable_live_streaming}")
        
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle Asterisk connection with enhanced logging and call session management"""
        client_addr = writer.get_extra_info('peername')
        temp_connection_id = f"{client_addr[0]}:{client_addr[1]}:{datetime.now().strftime('%H%M%S')}"
        
        logger.info(f"🎙️ [client] Connection from {client_addr} → {temp_connection_id}")
        
        # Protocol state
        uid_buffer = bytearray()
        audio_mode = False
        call_id: Optional[str] = None
        call_session = None
        audio_buffer = None
        call_logger = None  # Will be created when call_id is known
        
        try:
            packet_count = 0
            while True:
                # Receive audio data - flexible size to handle TCP fragmentation
                # Common patterns: 168, 240, 88, 320 bytes due to network fragmentation
                data = await reader.read(4096)  # Read up to 4KB, handle variable chunk sizes
                packet_count += 1
                
                if not data:
                    logger.info(f"🔌 [client] Connection closed by {client_addr}")
                    break
                
                # Log TCP packet if logging enabled and we have a call logger
                if self.enable_tcp_packet_logging and call_logger:
                    call_phase = "uid_negotiation" if not audio_mode else "audio_streaming"
                    call_logger.log_tcp_packet(data, is_audio_data=audio_mode, call_phase=call_phase)
                
                # Enhanced header inspection and fragmentation monitoring
                if packet_count <= 20:  # Monitor more packets for fragmentation patterns
                    logger.info(f"🔍 [pkt-{packet_count:02d}] {len(data)} bytes | "
                               f"Hex: {data[:32].hex()[:32]}{'...' if len(data) > 16 else ''}")
                    
                    # Detailed analysis for first few packets
                    if packet_count <= 5:
                        logger.info(f"🔍 [pkt-{packet_count:02d}] ASCII: {data[:min(64, len(data))].decode('ascii', errors='replace')}")
                        
                        # Look for potential call ID patterns
                        if b'CALL' in data or b'call' in data:
                            logger.info(f"🔍 [pkt-{packet_count:02d}] CALL keyword found")
                        if any(char.isdigit() for char in data.decode('ascii', errors='ignore')):
                            logger.info(f"🔍 [pkt-{packet_count:02d}] Digits found")
                
                # Track fragmentation patterns for debugging
                if audio_buffer and packet_count % 50 == 0:  # Log every 50 packets
                    stats = audio_buffer.get_stats()
                    chunk_dist = stats["chunk_statistics"]["chunk_size_distribution"]
                    logger.info(f"📊 [fragmentation] Packet {packet_count}: "
                               f"Chunk sizes: {dict(sorted(chunk_dist.items(), key=lambda x: -x[1])[:5])}")
                
                if not audio_mode:
                    # Handle UID protocol - extract call ID
                    for byte in data:
                        if byte == 13:  # CR
                            call_id = uid_buffer.decode('utf-8', errors='ignore')
                            logger.info(f"🆔 [client] call_id={call_id}")
                            
                            # Initialize call logger if logging enabled
                            if self.enable_call_logging:
                                call_logger = get_call_logger(call_id, create_if_not_exists=True)
                                if call_logger:
                                    logger.info(f"📁 Call logging enabled for {call_id} at {call_logger.get_call_directory()}")
                                else:
                                    logger.warning(f"⚠️ Failed to create call logger for {call_id}")
                            
                            # Start call session
                            try:
                                connection_info = {
                                    'client_addr': client_addr,
                                    'temp_connection_id': temp_connection_id,
                                    'start_time': datetime.now().isoformat()
                                }
                                call_session = await call_session_manager.start_session(call_id, connection_info)
                                
                                # Create audio buffer for this call with configured settings
                                audio_buffer = AsteriskAudioBuffer(
                                    window_duration_seconds=self.window_duration,
                                    enable_overlapping=self.enable_overlapping
                                )
                                
                                # Start live audio streaming if enabled
                                if self.enable_live_streaming and self.live_streamer:
                                    stream_metadata = {
                                        'client_addr': str(client_addr),
                                        'window_duration': self.window_duration,
                                        'overlapping_enabled': self.enable_overlapping
                                    }
                                    self.live_streamer.start_call_stream(call_id, stream_metadata)
                                
                                # Track active connection
                                self.active_connections[call_id] = {
                                    'audio_buffer': audio_buffer,
                                    'client_addr': client_addr,
                                    'session': call_session,
                                    'call_logger': call_logger  # Add call logger to connection info
                                }
                                
                                audio_mode = True
                                break
                                
                            except Exception as e:
                                logger.error(f"❌ Failed to start call session for {call_id}: {e}")
                                return  # Close connection on session start failure
                                
                        uid_buffer.append(byte)
                    continue
                
                # Process audio data (only if we have call_id and audio_buffer)
                if call_id and audio_buffer:
                    audio_array = audio_buffer.add_chunk(data)
                    
                    if audio_array is not None:
                        # Log audio segment if call logging is enabled
                        segment_id = None
                        if self.enable_call_logging and call_logger:
                            # Convert audio array to bytes for logging
                            audio_bytes = (audio_array * 32768.0).astype(np.int16).tobytes()
                            buffer_stats = audio_buffer.get_stats()
                            duration = len(audio_array) / 16000  # 16kHz sample rate
                            
                            segment_id, chunk_filename = call_logger.log_audio_segment(
                                audio_bytes=audio_bytes,
                                duration_seconds=duration,
                                sample_rate=16000,
                                buffer_stats=buffer_stats
                            )
                            
                            logger.info(f"🎵 Audio segment {segment_id} logged for call {call_id}: "
                                       f"{duration:.1f}s → {chunk_filename}")
                        
                        # Stream audio chunk if live streaming is enabled
                        if self.enable_live_streaming and self.live_streamer:
                            stream_metadata = {
                                'segment_id': segment_id,
                                'buffer_stats': buffer_stats if 'buffer_stats' in locals() else None
                            }
                            await self.live_streamer.stream_audio_chunk(
                                call_id=call_id,
                                audio_array=audio_array,
                                sample_rate=16000,
                                metadata=stream_metadata
                            )
                        
                        # Submit to Celery for transcription with call session tracking
                        await self._submit_transcription(audio_array, call_id)
                    
        except Exception as e:
            logger.error(f"❌ [client] Error handling connection {temp_connection_id}: {e}")
        finally:
            # Cleanup connection and end call session
            if call_id:
                try:
                    # Stop live audio streaming if enabled
                    if self.enable_live_streaming and self.live_streamer:
                        stream_summary = self.live_streamer.stop_call_stream(call_id)
                        if stream_summary:
                            logger.info(f"🎵 Live streaming stopped for {call_id}: "
                                       f"{stream_summary.get('total_chunks', 0)} chunks, "
                                       f"{stream_summary.get('total_duration_seconds', 0):.1f}s")
                    
                    # Finalize call logger if enabled
                    if self.enable_call_logging and call_logger:
                        summary_file = call_logger.finalize_call()
                        if summary_file:
                            logger.info(f"📊 Call summary generated for {call_id}: {summary_file}")
                        
                        # Remove from global registry (function already imported at top)
                        finalize_call_logger(call_id)
                    
                    # End call session
                    await call_session_manager.end_session(call_id, reason="connection_closed")
                    
                    # Remove from active connections
                    if call_id in self.active_connections:
                        del self.active_connections[call_id]
                        
                    logger.info(f"🧹 Cleaned up call session {call_id}")
                except Exception as e:
                    logger.error(f"❌ Error cleaning up call session {call_id}: {e}")
            
            writer.close()
            await writer.wait_closed()
            logger.info(f"🧹 Connection closed: {temp_connection_id}")
            
    async def _submit_transcription(self, audio_array: np.ndarray, call_id: str):
        """Submit transcription to Celery worker with call session tracking"""
        try:
            # Convert numpy array to bytes for Celery
            audio_bytes = (audio_array * 32768.0).astype(np.int16).tobytes()
            
            # Create synthetic filename using call ID
            timestamp = datetime.now().strftime("%H%M%S%f")[:-3]  # milliseconds
            filename = f"call_{call_id}_{timestamp}.wav"
            
            # Get environment-based configuration
            import os
            debug_save_audio = os.getenv("ASTERISK_DEBUG_SAVE_AUDIO", "true").lower() == "true"
            enable_vad = os.getenv("ASTERISK_ENABLE_VAD", "true").lower() == "true"
            enable_auto_language = os.getenv("ASTERISK_ENABLE_AUTO_LANGUAGE", "false").lower() == "true"
            
            # Submit to streaming transcription task with actual window duration and configuration
            task = process_streaming_audio_task.delay(
                audio_bytes=audio_bytes,
                filename=filename,
                connection_id=call_id,  # Now using call_id
                language="sw",
                sample_rate=16000,
                duration_seconds=self.window_duration,  # Use configured duration
                is_streaming=True,
                debug_save_audio=debug_save_audio,
                enable_auto_language=enable_auto_language
            )
            
            logger.info(f"🎵 Submitted transcription task {task.id} for call {call_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to submit transcription for call {call_id}: {e}")
            
    async def start_server(self, host: str = "0.0.0.0", port: int = 8300):
        """Start TCP server"""
        try:
            self.server = await asyncio.start_server(
                self.handle_connection, 
                host, 
                port
            )
            
            logger.info(f"🚀 [Main] Asterisk TCP server listening on {host}:{port}")
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"❌ Failed to start TCP server: {e}")
            raise
            
    async def stop_server(self):
        """Stop server gracefully"""
        if self.server:
            logger.info("🛑 Stopping Asterisk TCP server...")
            self.server.close()
            await self.server.wait_closed()
            logger.info("✅ Asterisk TCP server stopped")
            
    def get_status(self) -> dict:
        """Get server status with call session information"""
        connection_stats = {}
        for call_id, conn_info in self.active_connections.items():
            connection_stats[call_id] = {
                "audio_buffer_stats": conn_info['audio_buffer'].get_stats(),
                "client_addr": str(conn_info['client_addr']),
                "session_status": conn_info['session'].status if conn_info['session'] else "unknown"
            }
        
        return {
            "server_running": self.server is not None,
            "active_calls": len(self.active_connections),
            "active_connections": len(self.active_connections),
            "call_sessions": connection_stats,
            "transcription_method": "celery_workers",
            "tcp_port": 8300
        }