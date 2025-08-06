# app/streaming/websocket_server.py - WebSocket server for Asterisk
import asyncio
import logging
import numpy as np
from typing import Dict
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from .audio_buffer import AsteriskAudioBuffer
from ..tasks.audio_tasks import process_streaming_audio_task

logger = logging.getLogger(__name__)

class AsteriskWebSocketManager:
    """WebSocket manager for Asterisk audio connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, dict] = {}
        
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection from Asterisk"""
        await websocket.accept()
        
        client_info = websocket.client
        connection_id = f"ws_{client_info.host}:{client_info.port}:{datetime.now().strftime('%H%M%S')}"
        
        logger.info(f"🎙️ [WebSocket] Connection from {client_info} → {connection_id}")
        
        # Create buffer for this connection
        audio_buffer = AsteriskAudioBuffer()
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "buffer": audio_buffer,
            "client_info": client_info
        }
        
        # Protocol state
        uid_received = False
        uid_buffer = bytearray()
        
        try:
            while True:
                # Receive data from WebSocket
                data = await websocket.receive_bytes()
                
                if not uid_received:
                    # Handle UID protocol (same as TCP)
                    for byte in data:
                        if byte == 13:  # CR
                            uid_str = uid_buffer.decode('utf-8', errors='ignore')
                            logger.info(f"🆔 [WebSocket] uid={uid_str}")
                            uid_received = True
                            break
                        uid_buffer.append(byte)
                    continue
                
                # Process audio data (640 bytes = 20ms at 16kHz)
                if len(data) == 640:
                    audio_array = audio_buffer.add_chunk(data)
                    
                    if audio_array is not None:
                        # Submit to Celery for transcription
                        await self._submit_transcription(audio_array, connection_id)
                else:
                    logger.warning(f"⚠️ [WebSocket] Unexpected data size: {len(data)} bytes (expected 640)")
                    
        except WebSocketDisconnect:
            logger.info(f"🔌 [WebSocket] Connection closed by {client_info}")
        except Exception as e:
            logger.error(f"❌ [WebSocket] Error handling connection {connection_id}: {e}")
        finally:
            # Cleanup
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            logger.info(f"🧹 Cleaned up WebSocket connection {connection_id}")
            
    async def _submit_transcription(self, audio_array: np.ndarray, connection_id: str):
        """Submit transcription to Celery worker"""
        try:
            # Convert numpy array to bytes for Celery (same as TCP version)
            audio_bytes = (audio_array * 32768.0).astype(np.int16).tobytes()
            
            # Create synthetic filename
            timestamp = datetime.now().strftime("%H%M%S%f")[:-3]  # milliseconds
            filename = f"ws_stream_{connection_id}_{timestamp}.wav"
            
            # Submit to Celery task
            task = process_streaming_audio_task.delay(
                audio_bytes=audio_bytes,
                filename=filename,
                connection_id=connection_id,
                language="sw",  # Default to Swahili, can be made configurable
                sample_rate=16000,
                duration_seconds=5.0,
                is_streaming=True
            )
            
            logger.info(f"🎵 [WebSocket] Submitted transcription task {task.id} for {connection_id}")
            
        except Exception as e:
            logger.error(f"❌ [WebSocket] Failed to submit transcription for {connection_id}: {e}")
            
    def get_status(self) -> dict:
        """Get WebSocket server status"""
        return {
            "websocket_server_active": True,
            "active_connections": len(self.active_connections),
            "connections": {
                conn_id: {
                    "client": str(conn_data["client_info"]),
                    "buffer_stats": conn_data["buffer"].get_stats()
                }
                for conn_id, conn_data in self.active_connections.items()
            },
            "transcription_method": "celery_workers",
            "protocol": "websocket"
        }

# Global instance
websocket_manager = AsteriskWebSocketManager()