# app/streaming/tcp_server.py - Updated to use Celery and Call Session Management
import asyncio
import logging
import numpy as np
from typing import Dict, Optional
from datetime import datetime

from .audio_buffer import AsteriskAudioBuffer
from .call_session_manager import call_session_manager
from ..tasks.audio_tasks import process_streaming_audio_task  # Use your existing Celery tasks

logger = logging.getLogger(__name__)

class AsteriskTCPServer:
    """TCP server for Asterisk audio input - uses Celery workers"""
    
    def __init__(self, model_loader=None):
        # Don't need model_loader anymore - we'll use Celery
        self.active_connections: Dict[str, Dict] = {}  # Maps call_id to connection info
        self.server = None
        
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle Asterisk connection with call session management"""
        client_addr = writer.get_extra_info('peername')
        temp_connection_id = f"{client_addr[0]}:{client_addr[1]}:{datetime.now().strftime('%H%M%S')}"
        
        logger.info(f"🎙️ [client] Connection from {client_addr} → {temp_connection_id}")
        
        # Protocol state
        uid_buffer = bytearray()
        audio_mode = False
        call_id: Optional[str] = None
        call_session = None
        audio_buffer = None
        
        try:
            packet_count = 0
            while True:
                # Receive 10ms SLIN (320 bytes) - mixed-mono with both parties
                data = await reader.read(320)
                packet_count += 1
                
                if not data:
                    logger.info(f"🔌 [client] Connection closed by {client_addr}")
                    break
                
                # Header inspection - log first few packets in detail
                if packet_count <= 10:
                    logger.info(f"🔍 [header] Packet {packet_count}: {len(data)} bytes")
                    logger.info(f"🔍 [header] Hex dump: {data[:min(64, len(data))].hex()}")
                    logger.info(f"🔍 [header] ASCII: {data[:min(64, len(data))].decode('ascii', errors='replace')}")
                    
                    # Look for potential call ID patterns
                    if b'CALL' in data or b'call' in data:
                        logger.info(f"🔍 [header] CALL keyword found in packet {packet_count}")
                    if any(char.isdigit() for char in data.decode('ascii', errors='ignore')):
                        logger.info(f"🔍 [header] Digits found in packet {packet_count}")
                
                if not audio_mode:
                    # Handle UID protocol - extract call ID
                    for byte in data:
                        if byte == 13:  # CR
                            call_id = uid_buffer.decode('utf-8', errors='ignore')
                            logger.info(f"🆔 [client] call_id={call_id}")
                            
                            # Start call session
                            try:
                                connection_info = {
                                    'client_addr': client_addr,
                                    'temp_connection_id': temp_connection_id,
                                    'start_time': datetime.now().isoformat()
                                }
                                call_session = await call_session_manager.start_session(call_id, connection_info)
                                
                                # Create audio buffer for this call
                                audio_buffer = AsteriskAudioBuffer()
                                
                                # Track active connection
                                self.active_connections[call_id] = {
                                    'audio_buffer': audio_buffer,
                                    'client_addr': client_addr,
                                    'session': call_session
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
                        # Submit to Celery for transcription with call session tracking
                        await self._submit_transcription(audio_array, call_id)
                    
        except Exception as e:
            logger.error(f"❌ [client] Error handling connection {temp_connection_id}: {e}")
        finally:
            # Cleanup connection and end call session
            if call_id:
                try:
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
            
            # Submit to streaming transcription task
            task = process_streaming_audio_task.delay(
                audio_bytes=audio_bytes,
                filename=filename,
                connection_id=call_id,  # Now using call_id
                language="sw",
                sample_rate=16000,
                duration_seconds=5.0,
                is_streaming=True
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