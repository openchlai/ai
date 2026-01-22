
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from app.core.streaming import AudioStreamingService

class TestAudioStreamingService:


    @pytest.fixture
    def mock_redis(self):
        with patch('app.core.streaming.redis.from_url') as mock_from_url, \
             patch('app.core.streaming.get_redis_url', return_value="redis://test"):
            
            # mock_client needs to handle async methods (publish) and sync methods (pubsub)
            mock_client = AsyncMock()
            mock_from_url.return_value = mock_client
            
            # publish returns number of subscribers (int)
            mock_client.publish.return_value = 1
            
            # pubsub() is synchronous, returns a PubSub object
            mock_pubsub = MagicMock()
            mock_client.pubsub = MagicMock(return_value=mock_pubsub)
            
            # subscribe/unsubscribe are async methods on PubSub
            mock_pubsub.subscribe = AsyncMock()
            mock_pubsub.unsubscribe = AsyncMock()
            mock_pubsub.close = AsyncMock()
            
            yield mock_client

    @pytest.mark.asyncio
    async def test_publish_progress(self, mock_redis):
        service = AudioStreamingService()
        
        success = await service.publish_progress("task1", "step1", 50, "working")
        
        assert success is True
        mock_redis.publish.assert_called_once()
        
        # Verify call args
        args = mock_redis.publish.call_args
        channel, message = args[0]
        assert channel == "audio_stream:task1"
        data = json.loads(message)
        assert data["task_id"] == "task1"
        assert data["step"] == "step1"
        assert data["progress"] == 50

    @pytest.mark.asyncio
    async def test_publish_progress_error(self, mock_redis):
        mock_redis.publish.side_effect = Exception("Connection error")
        service = AudioStreamingService()
        
        success = await service.publish_progress("task1", "step1", 50)
        assert success is False

    @pytest.mark.asyncio
    async def test_publish_partial_transcript(self, mock_redis):
        service = AudioStreamingService()
        
        await service.publish_partial_transcript("task1", "hello", 10)
        
        # Check that it calls publish
        mock_redis.publish.assert_called()
        args = mock_redis.publish.call_args
        data = json.loads(args[0][1])
        assert data["step"] == "transcription"
        assert data["partial_result"]["transcript"] == "hello"

    @pytest.mark.asyncio
    async def test_publish_step_complete(self, mock_redis):
        service = AudioStreamingService()
        
        await service.publish_step_complete("task1", "analysis", {"score": 9}, 100)
        
        mock_redis.publish.assert_called()
        args = mock_redis.publish.call_args
        data = json.loads(args[0][1])
        assert data["step"] == "analysis_complete"
        assert data["partial_result"]["score"] == 9


    @pytest.mark.asyncio
    async def test_subscribe_to_task(self, mock_redis):
        service = AudioStreamingService()
        mock_pubsub = mock_redis.pubsub.return_value
        
        msg1 = {"type": "message", "data": json.dumps({"step": "processing", "progress": 50})}
        msg2 = {"type": "message", "data": json.dumps({"step": "completed", "progress": 100})}
        
        async def message_generator():
            yield msg1
            yield msg2
            
        # mock_pubsub.listen is a method that returns the generator
        mock_pubsub.listen.side_effect = message_generator
        
        # Consume the generator
        updates = []
        async for update in service.subscribe_to_task("task1"):
            updates.append(update)
            
        assert len(updates) == 3 # Initial sub confirmation + msg1 + msg2
        assert updates[0]["status"] == "subscribed"
        assert updates[1]["step"] == "processing"
        assert updates[2]["step"] == "completed"
    
    @pytest.mark.asyncio
    async def test_subscribe_timout(self, mock_redis):
        # Skip this test logic complexity for now and just ensure it handles expected flow
        # Testing timeouts with async generators in mocks is unstable
        pass


    @pytest.mark.asyncio
    async def test_publish_partial_translation(self, mock_redis):
        service = AudioStreamingService()
        await service.publish_partial_translation("task1", "hola", 20, "en", "es")
        
        mock_redis.publish.assert_called()
        args = mock_redis.publish.call_args
        data = json.loads(args[0][1])
        assert data["step"] == "translation"
        assert data["partial_result"]["translation"] == "hola"
        assert data["partial_result"]["source_language"] == "en"

    @pytest.mark.asyncio
    async def test_publish_error(self, mock_redis):
        service = AudioStreamingService()
        await service.publish_error("task1", "process", "Boom", 50)
        
        mock_redis.publish.assert_called()
        args = mock_redis.publish.call_args
        data = json.loads(args[0][1])
        assert data["step"] == "process_error"
        assert data["message"] == "Error in process: Boom"

    @pytest.mark.asyncio
    async def test_publish_final_result(self, mock_redis):
        service = AudioStreamingService()
        await service.publish_final_result("task1", {"transcription": "done"}, 1.5)
        
        mock_redis.publish.assert_called()
        args = mock_redis.publish.call_args
        data = json.loads(args[0][1])
        assert data["step"] == "completed"
        assert data["progress"] == 100
        assert data["metadata"]["total_duration"] == 1.5

    @pytest.mark.asyncio
    async def test_subscribe_error_handling(self, mock_redis):
        service = AudioStreamingService()
        mock_pubsub = mock_redis.pubsub.return_value
        
        # Simulate JSON decode error
        bad_msg = {"type": "message", "data": "invalid_json{"}
        
        async def message_generator():
            yield bad_msg
            
        mock_pubsub.listen.side_effect = message_generator
        
        updates = []
        async for update in service.subscribe_to_task("task1"):
            updates.append(update)
            
        assert len(updates) == 2 # 1 sub confirmation + 1 error msg
        assert updates[1]["status"] == "stream_error"

    @pytest.mark.asyncio
    async def test_cleanup_exception(self, mock_redis):
        service = AudioStreamingService()
        mock_redis.publish.side_effect = Exception("Redis down")
        
        success = await service.cleanup_task_channel("task1")
        assert success is False

    @pytest.mark.asyncio
    async def test_close_exception(self, mock_redis):
        service = AudioStreamingService()
        await service.get_redis_client()

        mock_redis.close.side_effect = Exception("Close failed")
        # Should not raise
        await service.close()

    @pytest.mark.asyncio
    async def test_publish_progress_no_subscribers(self, mock_redis):
        """Test publish_progress when no subscribers are active (line 80)"""
        service = AudioStreamingService()
        mock_redis.publish.return_value = 0  # No active subscribers

        success = await service.publish_progress("task1", "step1", 50, "working")

        assert success is True
        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_timeout(self, mock_redis):
        """Test subscribe_to_task with timeout (lines 236-248)"""
        import asyncio
        service = AudioStreamingService()
        mock_pubsub = mock_redis.pubsub.return_value

        # Create a generator that yields messages but never completes
        async def message_generator():
            # Keep yielding non-message types to trigger timeout
            for i in range(100):
                yield {"type": "subscribe"}
                await asyncio.sleep(0.001)  # Small delay

        mock_pubsub.listen.side_effect = message_generator

        # Set a very short timeout
        updates = []
        async for update in service.subscribe_to_task("task1", timeout=0.05):
            updates.append(update)

        # Should get subscription confirmation + timeout message
        assert len(updates) >= 2
        assert updates[0]["status"] == "subscribed"
        # Last message should be timeout
        assert updates[-1]["status"] == "timeout"

    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe_error(self, mock_redis):
        """Test subscribe_to_task with error in finally block (lines 260-261)"""
        service = AudioStreamingService()
        mock_pubsub = mock_redis.pubsub.return_value

        # Make unsubscribe fail
        mock_pubsub.unsubscribe.side_effect = Exception("Unsubscribe failed")

        msg = {"type": "message", "data": json.dumps({"step": "completed", "progress": 100})}

        async def message_generator():
            yield msg

        mock_pubsub.listen.side_effect = message_generator

        # Should not raise, just log error
        updates = []
        async for update in service.subscribe_to_task("task1"):
            updates.append(update)

        # Should still get updates
        assert len(updates) >= 2

    @pytest.mark.asyncio
    async def test_cleanup_task_channel_success(self, mock_redis):
        """Test successful cleanup_task_channel (lines 278-279)"""
        service = AudioStreamingService()
        mock_redis.publish.return_value = 1

        success = await service.cleanup_task_channel("task1")

        assert success is True
        mock_redis.publish.assert_called_once()
        args = mock_redis.publish.call_args
        data = json.loads(args[0][1])
        assert data["step"] == "cleanup"

    @pytest.mark.asyncio
    async def test_close_both_clients(self, mock_redis):
        """Test close() with both redis and pubsub clients (lines 290-292)"""
        service = AudioStreamingService()
        # Initialize both clients
        await service.get_redis_client()
        await service.get_pubsub_client()

        # Should close both without raising
        await service.close()

        # Both close methods should be called
        assert mock_redis.close.call_count == 2
