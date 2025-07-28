import asyncio
import base64
import wave
import websockets
import json

async def send_audio_buffer():
    uri = "ws://localhost:8000/realtime/transcribe"

    # Read WAV file as raw PCM bytes
    with wave.open('2.wav', 'rb') as wav_file:
        audio_data = wav_file.readframes(wav_file.getnframes())

    # Encode to base64
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')

    # Prepare message
    message = {
        "type": "audio_data",
        "data": audio_b64,
        "format": "pcm_s16le",
        "sample_rate": 16000,
        "language": "en"
    }

    async with websockets.connect(uri) as websocket:
        # Wait for connection_established message
        response = await websocket.recv()
        print("Server:", response)

        # Send audio buffer
        await websocket.send(json.dumps(message))

        # Print responses (transcription, status, etc.)
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                print("Server:", response)
            except asyncio.TimeoutError:
                break

if __name__ == "__main__":
    asyncio.run(send_audio_buffer())