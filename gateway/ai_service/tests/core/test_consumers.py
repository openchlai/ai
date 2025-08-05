
import pytest
from channels.testing import WebsocketCommunicator
from django.urls import path
from core.consumers import AudioConsumer

application = type('Application', (),
    {'scope_prototypes': {'websocket.receive': {'type': 'websocket.receive', 'bytes': b''}}})

@pytest.mark.asyncio
async def test_audio_consumer_connection():
    """
    Test that the AudioConsumer can be connected to.
    """
    communicator = WebsocketCommunicator(AudioConsumer.as_asgi(), "/ws/audio/test-task-id/")
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_audio_consumer_disconnection():
    """
    Test that the AudioConsumer can be disconnected from.
    """
    communicator = WebsocketCommunicator(AudioConsumer.as_asgi(), "/ws/audio/test-task-id/")
    await communicator.connect()
    await communicator.disconnect()
    assert True
