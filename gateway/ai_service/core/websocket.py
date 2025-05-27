import asyncio
import websockets
import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# WebSocket configuration
WS_URL = "wss://demo-openchs.bitz-itc.com:8384/ami/sync?c=-2"
AUDIO_RETRIEVE = "https://demo-openchs.bitz-itc.com/helpline/api/calls/UNIQUEID?file=wav&"

calls = []

async def listen():
    while True:  # Outer loop for reconnection
        try:
            async with websockets.connect(WS_URL) as websocket:
                logger.info("Connected to WebSocket server")
                
                while True:  # Inner loop for message processing
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if 'channels' in data:
                            chans = list(data['channels'].keys())
                            for channel in chans:
                                if 'trunk_test_outbound' in data['channels'][channel]:
                                    if channel not in calls:
                                        calls.append(channel)
                                        logger.info(f"New call detected: {channel}")
                            
                            # Check for ended calls
                            for call in calls[:]:  # Create a copy for iteration
                                if call not in chans:
                                    logger.info(f"Call ended: {call}")
                                    audio_url = AUDIO_RETRIEVE.replace("UNIQUEID", call)
                                    os.system(f"curl -X GET '{audio_url}' -o {call}.wav")
                                    calls.remove(call)
                                    logger.info(f"Updated Call List: {calls}")

                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("WebSocket connection closed, reconnecting...")
                        break
                    except json.JSONDecodeError:
                        logger.error("Failed to decode message as JSON")
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}, retrying in 5 seconds...")
            await asyncio.sleep(5)

def start_websocket_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(listen())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()