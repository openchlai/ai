# app/core/streaming.py
import json
import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import redis.asyncio as redis
from ..config.settings import get_redis_url

logger = logging.getLogger(__name__)

class AudioStreamingService:
    """Redis pub/sub based streaming service for audio processing"""
    
    def __init__(self):
        self.redis_url = get_redis_url()
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub_client: Optional[redis.Redis] = None
    
    async def get_redis_client(self) -> redis.Redis:
        """Get or create Redis client for publishing"""
        if not self.redis_client:
            self.redis_client = redis.from_url(
                self.redis_url, 
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
        return self.redis_client
    
    async def get_pubsub_client(self) -> redis.Redis:
        """Get or create Redis client for subscribing"""
        if not self.pubsub_client:
            self.pubsub_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
        return self.pubsub_client
    
    def get_channel_name(self, task_id: str) -> str:
        """Get Redis channel name for a task"""
        return f"audio_stream:{task_id}"
    
    async def publish_progress(
        self, 
        task_id: str, 
        step: str, 
        progress: int, 
        message: str = None,
        partial_result: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Publish progress update to Redis channel"""
        try:
            redis_client = await self.get_redis_client()
            channel = self.get_channel_name(task_id)
            
            update = {
                "task_id": task_id,
                "step": step,
                "progress": progress,
                "timestamp": datetime.now().isoformat(),
                "message": message or f"Processing: {step}"
            }
            
            if partial_result:
                update["partial_result"] = partial_result
            
            if metadata:
                update["metadata"] = metadata
            
            # Publish to channel
            subscribers = await redis_client.publish(channel, json.dumps(update))
            
            if subscribers > 0:
                logger.debug(f"📡 Published {step} update for task {task_id} to {subscribers} subscribers")
            else:
                logger.debug(f"📡 Published {step} update for task {task_id} (no active subscribers)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish progress for task {task_id}: {e}")
            return False
    
    async def publish_partial_transcript(
        self, 
        task_id: str, 
        partial_text: str, 
        progress: int,
        is_final: bool = False
    ) -> bool:
        """Publish partial transcription results"""
        return await self.publish_progress(
            task_id=task_id,
            step="transcription",
            progress=progress,
            message="Transcribing audio..." if not is_final else "Transcription complete",
            partial_result={
                "transcript": partial_text,
                "is_final": is_final,
                "text_length": len(partial_text)
            }
        )
    
    async def publish_partial_translation(
        self, 
        task_id: str, 
        partial_translation: str, 
        progress: int,
        source_language: str = None,
        target_language: str = None,
        is_final: bool = False
    ) -> bool:
        """Publish partial translation results"""
        return await self.publish_progress(
            task_id=task_id,
            step="translation",
            progress=progress,
            message="Translating text..." if not is_final else "Translation complete",
            partial_result={
                "translation": partial_translation,
                "is_final": is_final,
                "source_language": source_language,
                "target_language": target_language,
                "text_length": len(partial_translation)
            }
        )
    
    async def publish_step_complete(
        self, 
        task_id: str, 
        step: str, 
        result: Dict[str, Any],
        progress: int,
        duration: float = None
    ) -> bool:
        """Publish step completion with full results"""
        metadata = {"duration": duration} if duration else {}
        
        return await self.publish_progress(
            task_id=task_id,
            step=f"{step}_complete",
            progress=progress,
            message=f"{step.title()} completed successfully",
            partial_result=result,
            metadata=metadata
        )
    
    async def publish_error(
        self, 
        task_id: str, 
        step: str, 
        error: str,
        progress: int = None
    ) -> bool:
        """Publish error update"""
        return await self.publish_progress(
            task_id=task_id,
            step=f"{step}_error",
            progress=progress or 0,
            message=f"Error in {step}: {error}",
            metadata={"error": error, "error_step": step}
        )
    
    async def publish_final_result(
        self, 
        task_id: str, 
        result: Dict[str, Any],
        total_duration: float
    ) -> bool:
        """Publish final processing result"""
        return await self.publish_progress(
            task_id=task_id,
            step="completed",
            progress=100,
            message="Audio processing completed successfully",
            partial_result=result,
            metadata={
                "total_duration": total_duration,
                "completed_at": datetime.now().isoformat()
            }
        )
    
    async def subscribe_to_task(
        self, 
        task_id: str,
        timeout: int = 600  # 10 minutes
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to task updates and yield them as they arrive"""
        pubsub_client = await self.get_pubsub_client()
        channel = self.get_channel_name(task_id)
        
        pubsub = pubsub_client.pubsub()
        
        try:
            await pubsub.subscribe(channel)
            logger.info(f"🔔 Subscribed to audio stream for task {task_id}")
            
            # Send initial subscription confirmation
            yield {
                "task_id": task_id,
                "status": "subscribed",
                "message": "Subscribed to audio processing stream",
                "timestamp": datetime.now().isoformat()
            }
            
            start_time = datetime.now()
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Parse the JSON message
                        update = json.loads(message["data"])
                        yield update
                        
                        # Break on completion or error
                        if update.get("step") in ["completed", "failed", "cancelled"]:
                            logger.info(f"🏁 Stream ended for task {task_id}: {update.get('step')}")
                            break
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Invalid JSON in stream for task {task_id}: {e}")
                        yield {
                            "task_id": task_id,
                            "status": "stream_error",
                            "error": "Invalid message format",
                            "timestamp": datetime.now().isoformat()
                        }
                
                # Check timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout:
                    logger.warning(f"⏰ Stream timeout for task {task_id} after {elapsed:.1f}s")
                    yield {
                        "task_id": task_id,
                        "status": "timeout",
                        "error": f"Stream timeout after {timeout} seconds",
                        "elapsed_time": elapsed,
                        "timestamp": datetime.now().isoformat()
                    }
                    break
        
        except Exception as e:
            logger.error(f"❌ Stream subscription error for task {task_id}: {e}")
            yield {
                "task_id": task_id,
                "status": "subscription_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
                logger.info(f"🔚 Unsubscribed from stream for task {task_id}")
            except Exception as e:
                logger.error(f"❌ Error closing subscription for task {task_id}: {e}")
    
    async def cleanup_task_channel(self, task_id: str) -> bool:
        """Clean up task channel (optional - Redis will auto-expire)"""
        try:
            redis_client = await self.get_redis_client()
            channel = self.get_channel_name(task_id)
            
            # Send final cleanup message
            cleanup_msg = {
                "task_id": task_id,
                "step": "cleanup",
                "message": "Task channel cleanup",
                "timestamp": datetime.now().isoformat()
            }
            
            await redis_client.publish(channel, json.dumps(cleanup_msg))
            logger.debug(f"🧹 Cleaned up channel for task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup channel for task {task_id}: {e}")
            return False
    
    async def close(self):
        """Close Redis connections"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            if self.pubsub_client:
                await self.pubsub_client.close()
            logger.info("🔌 Redis streaming connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis connections: {e}")

# Global instance
audio_streaming = AudioStreamingService()