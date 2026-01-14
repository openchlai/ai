#!/usr/bin/env python3
"""
Mock Asterisk Server for Testing AI Service

Simulates Asterisk TCP audio streaming using real audio files.
Supports real-time streaming and can trigger post-call processing.

Usage:
    # Stream single call
    python scripts/mock_asterisk.py --audio-folder /path/to/audio --count 1

    # Stream 5 calls with 15-second stagger
    python scripts/mock_asterisk.py --audio-folder /path/to/audio --count 5 --interval 15

    # Fast mode (10x speed)
    python scripts/mock_asterisk.py --audio-folder /path/to/audio --speed 10

    # Post-call mode (just trigger end event, no streaming)
    python scripts/mock_asterisk.py --mode post-call --audio-folder /path/to/audio
"""

import argparse
import asyncio
import logging
import os
import random
import socket
import struct
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import glob

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the app directory to Python path for settings import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@dataclass
class AudioFile:
    """Represents a loaded audio file ready for streaming"""
    path: str
    filename: str
    pcm_bytes: bytes
    sample_rate: int
    duration_seconds: float
    num_samples: int


class AudioFileLoader:
    """Loads and converts audio files to PCM format for streaming"""

    TARGET_SAMPLE_RATE = 16000  # 16kHz for Whisper
    TARGET_DTYPE = np.int16     # 16-bit signed integers

    def __init__(self, audio_folder: str):
        self.audio_folder = Path(audio_folder)
        if not self.audio_folder.exists():
            raise ValueError(f"Audio folder does not exist: {audio_folder}")

        self.audio_files: List[AudioFile] = []
        self._load_audio_files()

    def _load_audio_files(self):
        """Scan folder and load all supported audio files"""
        supported_extensions = ['*.wav', '*.WAV', '*.mp3', '*.MP3', '*.gsm', '*.GSM', '*.ogg', '*.OGG']

        audio_paths = []
        for ext in supported_extensions:
            audio_paths.extend(self.audio_folder.glob(ext))

        if not audio_paths:
            raise ValueError(f"No audio files found in {self.audio_folder}")

        logger.info(f"Found {len(audio_paths)} audio files in {self.audio_folder}")

        for path in sorted(audio_paths):
            try:
                audio_file = self._load_single_file(path)
                self.audio_files.append(audio_file)
                logger.info(f"  Loaded: {path.name} ({audio_file.duration_seconds:.1f}s)")
            except Exception as e:
                logger.warning(f"  Failed to load {path.name}: {e}")

    def _load_single_file(self, path: Path) -> AudioFile:
        """Load a single audio file and convert to PCM"""
        import wave

        # For WAV files, try wave module first
        if path.suffix.lower() == '.wav':
            try:
                return self._load_wav_file(path)
            except wave.Error as e:
                # File has .wav extension but isn't a valid WAV (e.g., Ogg with wrong extension)
                logger.warning(f"  {path.name} has .wav extension but isn't valid WAV format, trying ffmpeg conversion...")
                return self._convert_with_ffmpeg(path)
        else:
            # For other formats, try using scipy or ffmpeg
            return self._load_with_scipy(path)

    def _load_wav_file(self, path: Path) -> AudioFile:
        """Load WAV file using standard library"""
        import wave

        with wave.open(str(path), 'rb') as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()

            # Read raw audio data
            raw_data = wav.readframes(n_frames)

        # Convert to numpy array
        if sample_width == 1:
            dtype = np.int8
        elif sample_width == 2:
            dtype = np.int16
        elif sample_width == 4:
            dtype = np.int32
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")

        audio = np.frombuffer(raw_data, dtype=dtype)

        # Convert to mono if stereo
        if n_channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1).astype(dtype)

        # Convert to float for resampling
        audio_float = audio.astype(np.float32) / np.iinfo(dtype).max

        # Resample if needed
        if framerate != self.TARGET_SAMPLE_RATE:
            audio_float = self._resample(audio_float, framerate, self.TARGET_SAMPLE_RATE)

        # Convert back to int16
        audio_int16 = (audio_float * 32767).astype(np.int16)

        # Convert to bytes (big-endian for Asterisk protocol)
        pcm_bytes = audio_int16.astype('>i2').tobytes()

        duration = len(audio_int16) / self.TARGET_SAMPLE_RATE

        return AudioFile(
            path=str(path),
            filename=path.name,
            pcm_bytes=pcm_bytes,
            sample_rate=self.TARGET_SAMPLE_RATE,
            duration_seconds=duration,
            num_samples=len(audio_int16)
        )

    def _load_with_scipy(self, path: Path) -> AudioFile:
        """Load audio file using scipy (for non-WAV formats)"""
        try:
            from scipy.io import wavfile
            from scipy import signal

            # For GSM, MP3, OGG or other formats, use ffmpeg
            if path.suffix.lower() in ['.gsm', '.mp3', '.ogg']:
                return self._convert_with_ffmpeg(path)

            sample_rate, audio = wavfile.read(str(path))

            # Handle stereo
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)

            # Normalize to float
            if audio.dtype == np.int16:
                audio_float = audio.astype(np.float32) / 32768.0
            elif audio.dtype == np.int32:
                audio_float = audio.astype(np.float32) / 2147483648.0
            else:
                audio_float = audio.astype(np.float32)

            # Resample if needed
            if sample_rate != self.TARGET_SAMPLE_RATE:
                audio_float = self._resample(audio_float, sample_rate, self.TARGET_SAMPLE_RATE)

            # Convert to int16 bytes
            audio_int16 = (audio_float * 32767).astype(np.int16)
            pcm_bytes = audio_int16.astype('>i2').tobytes()

            duration = len(audio_int16) / self.TARGET_SAMPLE_RATE

            return AudioFile(
                path=str(path),
                filename=path.name,
                pcm_bytes=pcm_bytes,
                sample_rate=self.TARGET_SAMPLE_RATE,
                duration_seconds=duration,
                num_samples=len(audio_int16)
            )

        except ImportError:
            raise ImportError("scipy required for non-WAV files: pip install scipy")

    def _convert_with_ffmpeg(self, path: Path) -> AudioFile:
        """Convert audio file using ffmpeg subprocess"""
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Use ffmpeg to convert to WAV
            cmd = [
                'ffmpeg', '-y', '-i', str(path),
                '-ar', str(self.TARGET_SAMPLE_RATE),
                '-ac', '1',
                '-f', 'wav',
                tmp_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")

            # Load the converted WAV
            return self._load_wav_file(Path(tmp_path))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        if orig_sr == target_sr:
            return audio

        try:
            from scipy import signal
            num_samples = int(len(audio) * target_sr / orig_sr)
            return signal.resample(audio, num_samples)
        except ImportError:
            # Simple linear interpolation fallback
            duration = len(audio) / orig_sr
            target_samples = int(duration * target_sr)
            indices = np.linspace(0, len(audio) - 1, target_samples)
            return np.interp(indices, np.arange(len(audio)), audio)

    def get_audio_file(self, index: int) -> AudioFile:
        """Get audio file by index (wraps around)"""
        return self.audio_files[index % len(self.audio_files)]

    def __len__(self):
        return len(self.audio_files)


class AsteriskMockClient:
    """Simulates an Asterisk client streaming audio to TCP server"""

    CHUNK_SIZE = 320  # 10ms at 16kHz, 16-bit = 160 samples * 2 bytes
    CHUNK_DURATION_MS = 10  # 10 milliseconds per chunk

    def __init__(self, server_host: str, server_port: int, speed_multiplier: float = 1.0):
        self.server_host = server_host
        self.server_port = server_port
        self.speed_multiplier = speed_multiplier
        self.call_id: Optional[str] = None
        self.socket: Optional[socket.socket] = None

    @staticmethod
    def generate_call_id(sequence: int = 0) -> str:
        """Generate Asterisk-style call ID: {timestamp}.{sequence} with random offsets"""
        # Add random offset to timestamp to simulate different call start times
        timestamp = int(time.time()) + random.randint(0, 9999)
        # Add random offset to sequence to ensure uniqueness
        sequence_with_offset = sequence + random.randint(0, 999)
        return f"{timestamp}.{sequence_with_offset}"

    async def connect(self) -> bool:
        """Connect to TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.socket.setblocking(False)
            logger.info(f"Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def send_call_id(self, call_id: str):
        """Send call ID with CR terminator (Asterisk protocol)"""
        self.call_id = call_id
        uid_data = call_id.encode('utf-8') + b'\r'  # CR terminator

        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.socket, uid_data)
        logger.info(f"Sent call ID: {call_id}")

    async def stream_audio(self, audio_file: AudioFile, progress_callback=None):
        """Stream audio file in 10ms chunks"""
        pcm_bytes = audio_file.pcm_bytes
        total_chunks = len(pcm_bytes) // self.CHUNK_SIZE
        chunk_delay = (self.CHUNK_DURATION_MS / 1000) / self.speed_multiplier

        logger.info(f"Streaming {audio_file.filename}: {audio_file.duration_seconds:.1f}s "
                    f"({total_chunks} chunks, {self.speed_multiplier}x speed)")

        loop = asyncio.get_event_loop()
        start_time = time.time()
        chunks_sent = 0

        for i in range(0, len(pcm_bytes), self.CHUNK_SIZE):
            chunk = pcm_bytes[i:i + self.CHUNK_SIZE]

            # Pad last chunk if needed
            if len(chunk) < self.CHUNK_SIZE:
                chunk = chunk + b'\x00' * (self.CHUNK_SIZE - len(chunk))

            try:
                await loop.sock_sendall(self.socket, chunk)
                chunks_sent += 1

                # Progress update every 5 seconds of audio
                if chunks_sent % 500 == 0:  # 500 chunks = 5 seconds
                    elapsed = time.time() - start_time
                    audio_time = chunks_sent * self.CHUNK_DURATION_MS / 1000
                    logger.info(f"  [{self.call_id}] Progress: {audio_time:.1f}s / "
                                f"{audio_file.duration_seconds:.1f}s (elapsed: {elapsed:.1f}s)")

                    if progress_callback:
                        progress_callback(chunks_sent, total_chunks)

                # Wait between chunks (simulates real-time)
                await asyncio.sleep(chunk_delay)

            except Exception as e:
                logger.error(f"Error sending chunk {chunks_sent}: {e}")
                break

        elapsed = time.time() - start_time
        logger.info(f"Finished streaming {self.call_id}: {chunks_sent} chunks in {elapsed:.1f}s")

        return chunks_sent

    async def disconnect(self):
        """Close connection"""
        if self.socket:
            try:
                self.socket.close()
                logger.info(f"Disconnected call {self.call_id}")
            except Exception as e:
                logger.warning(f"Error closing socket: {e}")
            self.socket = None


class MockOrchestrator:
    """Manages multiple concurrent mock calls"""

    def __init__(
        self,
        audio_loader: AudioFileLoader,
        server_host: str,
        server_port: int,
        speed_multiplier: float = 1.0
    ):
        self.audio_loader = audio_loader
        self.server_host = server_host
        self.server_port = server_port
        self.speed_multiplier = speed_multiplier
        self.active_calls: List[AsteriskMockClient] = []
        self.completed_calls: List[dict] = []

    async def run_single_call(self, audio_index: int, call_sequence: int) -> dict:
        """Run a single mock call"""
        audio_file = self.audio_loader.get_audio_file(audio_index)
        call_id = AsteriskMockClient.generate_call_id(call_sequence)

        client = AsteriskMockClient(
            self.server_host,
            self.server_port,
            self.speed_multiplier
        )

        result = {
            "call_id": call_id,
            "audio_file": audio_file.filename,
            "duration": audio_file.duration_seconds,
            "success": False,
            "chunks_sent": 0,
            "start_time": None,
            "end_time": None
        }

        try:
            self.active_calls.append(client)
            result["start_time"] = datetime.now().isoformat()

            # Connect
            if not await client.connect():
                result["error"] = "Connection failed"
                return result

            # Send call ID
            await client.send_call_id(call_id)

            # Small delay to let server process UID
            await asyncio.sleep(0.1)

            # Stream audio
            chunks_sent = await client.stream_audio(audio_file)
            result["chunks_sent"] = chunks_sent
            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Call {call_id} failed: {e}")
        finally:
            await client.disconnect()
            result["end_time"] = datetime.now().isoformat()
            if client in self.active_calls:
                self.active_calls.remove(client)
            self.completed_calls.append(result)

        return result

    async def run_multiple_calls(
        self,
        num_calls: int,
        stagger_interval: float = 15.0
    ):
        """Run multiple calls with staggered start times"""
        logger.info(f"Starting {num_calls} mock calls with {stagger_interval}s interval")

        tasks = []
        for i in range(num_calls):
            # Start call
            task = asyncio.create_task(
                self.run_single_call(audio_index=i, call_sequence=i)
            )
            tasks.append(task)

            # Wait before starting next call (except for last one)
            if i < num_calls - 1:
                logger.info(f"Waiting {stagger_interval}s before starting next call...")
                await asyncio.sleep(stagger_interval)

        # Wait for all calls to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Summary
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        logger.info(f"\n{'='*50}")
        logger.info(f"Mock Session Complete: {successful}/{num_calls} calls successful")

        for i, result in enumerate(results):
            if isinstance(result, dict):
                status = "OK" if result.get("success") else "FAILED"
                logger.info(f"  Call {i+1}: {result.get('call_id')} - {status} "
                            f"({result.get('audio_file')}, {result.get('chunks_sent')} chunks)")
            else:
                logger.error(f"  Call {i+1}: Error - {result}")

        return results


def get_server_port() -> int:
    """Get TCP server port from settings or environment"""
    try:
        from app.config.settings import settings
        return settings.streaming_port
    except ImportError:
        return int(os.getenv('STREAMING_PORT', '8300'))


def main():
    parser = argparse.ArgumentParser(
        description='Mock Asterisk Server for AI Service Testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stream a single call
  python mock_asterisk.py --audio-folder ./test_audio --count 1

  # Stream 5 calls with 15-second stagger
  python mock_asterisk.py --audio-folder ./test_audio --count 5 --interval 15

  # Fast mode for quick testing (10x speed)
  python mock_asterisk.py --audio-folder ./test_audio --speed 10

  # Specify server connection
  python mock_asterisk.py --audio-folder ./test_audio --host localhost --port 8300
        """
    )

    parser.add_argument(
        '--audio-folder', '-a',
        required=True,
        help='Path to folder containing audio files (WAV, MP3, GSM)'
    )

    parser.add_argument(
        '--count', '-n',
        type=int,
        default=1,
        help='Number of concurrent calls to simulate (default: 1)'
    )

    parser.add_argument(
        '--interval', '-i',
        type=float,
        default=15.0,
        help='Seconds between starting each call (default: 15)'
    )

    parser.add_argument(
        '--speed', '-s',
        type=float,
        default=1.0,
        help='Speed multiplier for streaming (default: 1.0 = real-time, 10 = 10x faster)'
    )

    parser.add_argument(
        '--host', '-H',
        default='localhost',
        help='TCP server host (default: localhost)'
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=None,
        help='TCP server port (default: from settings or 8300)'
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['realtime', 'post-call'],
        default='realtime',
        help='Processing mode: realtime (stream audio) or post-call (trigger download)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get port
    port = args.port or get_server_port()

    print(f"""
{'='*60}
    Asterisk Mock Client
{'='*60}
    Audio Folder: {args.audio_folder}
    Server:       {args.host}:{port}
    Calls:        {args.count}
    Interval:     {args.interval}s
    Speed:        {args.speed}x
    Mode:         {args.mode}
{'='*60}
""")

    if args.mode == 'post-call':
        print("Post-call mode not yet implemented. Use --mode realtime")
        return

    try:
        # Load audio files
        loader = AudioFileLoader(args.audio_folder)

        if len(loader) == 0:
            print("No audio files found!")
            return

        # Create orchestrator
        orchestrator = MockOrchestrator(
            audio_loader=loader,
            server_host=args.host,
            server_port=port,
            speed_multiplier=args.speed
        )

        # Run mock calls
        asyncio.run(orchestrator.run_multiple_calls(
            num_calls=args.count,
            stagger_interval=args.interval
        ))

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
