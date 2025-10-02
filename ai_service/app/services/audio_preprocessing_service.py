"""
Audio Preprocessing Service for Agent Feedback Loop
==================================================

This service handles audio preprocessing with intelligent chunking, quality analysis,
and S3 upload integration for the agent feedback workflow.
"""

import asyncio
import hashlib
import logging
import sqlite3
import uuid
import tempfile
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import numpy as np
import librosa
import soundfile as sf
import webrtcvad
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AudioEvaluation:
    """Results of audio quality evaluation"""
    duration: float
    speech_ratio: float
    vad_snr_db: float
    speech_segments_count: int
    passes_threshold: bool


@dataclass
class PreprocessingResult:
    """Results of complete preprocessing operation"""
    success: bool
    batch_id: str
    original_file_path: str
    total_chunks: int
    quality_chunks: int
    s3_urls: List[str]
    processing_time_seconds: float
    error_message: Optional[str] = None


class AudioPreprocessingService:
    """Service for audio preprocessing with S3 integration"""
    
    def __init__(self):
        """Initialize the audio preprocessing service"""
        self.target_sr = 16000  # Target sample rate
        self.frame_duration_ms = 30  # VAD frame duration
        
        # Quality thresholds from settings
        self.stage1_speech_ratio = settings.stage1_speech_ratio_threshold
        self.stage1_vad_snr = settings.stage1_vad_snr_threshold
        self.stage2_speech_ratio = settings.stage2_speech_ratio_threshold
        self.stage2_vad_snr = settings.stage2_vad_snr_threshold
        
        # Chunking parameters from settings
        self.min_chunk_duration = settings.min_chunk_duration
        self.max_chunk_duration = settings.max_chunk_duration
        self.target_chunk_duration = settings.target_chunk_duration
        self.chunk_tolerance = settings.chunk_tolerance
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
        # Initialize S3 client
        self._s3_client = None
        
        logger.info(f"AudioPreprocessingService initialized")
        logger.info(f"Stage 1 thresholds: speech_ratio >= {self.stage1_speech_ratio:.1%}, VAD SNR >= {self.stage1_vad_snr:.1f} dB")
        logger.info(f"Stage 2 thresholds: speech_ratio >= {self.stage2_speech_ratio:.1%}, VAD SNR >= {self.stage2_vad_snr:.1f} dB")
    
    @property
    def s3_client(self):
        """Lazy initialize S3 client"""
        if self._s3_client is None:
            try:
                self._s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
            except NoCredentialsError:
                logger.error("AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
                raise
        return self._s3_client
    
    def setup_workspace(self, workspace_dir: Path) -> None:
        """Create workspace directory structure"""
        directories = [
            'original_audio',
            'chunks', 
            'final_chunks',
            'metadata',
            'exports'
        ]
        
        for directory in directories:
            (workspace_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        os.chmod(workspace_dir, 0o700)
    
    def setup_database(self, workspace_dir: Path) -> Path:
        """Initialize SQLite database for tracking"""
        db_path = workspace_dir / 'metadata' / 'preprocessing.db'
        
        with sqlite3.connect(db_path) as conn:
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Processing batches table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processing_batches (
                    batch_id TEXT PRIMARY KEY,
                    call_id TEXT,
                    agent_id TEXT,
                    feedback_notes TEXT,
                    created_at TEXT,
                    total_chunks INTEGER,
                    quality_chunks INTEGER,
                    processing_time_seconds REAL,
                    s3_urls TEXT,
                    status TEXT DEFAULT 'processing',
                    thresholds_used TEXT
                )
            ''')
            
            # Original files table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS original_files (
                    file_id TEXT PRIMARY KEY,
                    batch_id TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    file_hash TEXT,
                    duration REAL,
                    sample_rate INTEGER,
                    speech_ratio REAL,
                    vad_snr_db REAL,
                    speech_segments_count INTEGER,
                    passes_stage1 INTEGER,
                    processed_at TEXT,
                    FOREIGN KEY (batch_id) REFERENCES processing_batches (batch_id)
                )
            ''')
            
            # Chunks table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    anonymized_name TEXT,
                    file_id TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration REAL,
                    speech_ratio REAL,
                    vad_snr_db REAL,
                    speech_segments_count INTEGER,
                    passes_stage2 INTEGER,
                    chunk_path TEXT,
                    final_chunk_path TEXT,
                    s3_url TEXT,
                    processed_at TEXT,
                    FOREIGN KEY (file_id) REFERENCES original_files (file_id)
                )
            ''')
        
        return db_path
    
    def evaluate_audio(self, audio_path: str, stage: str = "original") -> AudioEvaluation:
        """Evaluate audio quality using VAD and SNR analysis"""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.target_sr)
            duration = len(y) / sr
            
            if duration < 0.5:
                return AudioEvaluation(duration, 0.0, -np.inf, 0, False)
            
            # VAD analysis
            frame_length = int(sr * self.frame_duration_ms / 1000)
            frames = []
            speech_frames = 0
            
            for i in range(0, len(y) - frame_length, frame_length):
                frame = y[i:i + frame_length]
                
                # Convert to 16-bit PCM for VAD
                frame_16bit = (frame * 32767).astype(np.int16).tobytes()
                
                try:
                    is_speech = self.vad.is_speech(frame_16bit, sr)
                    frames.append(is_speech)
                    if is_speech:
                        speech_frames += 1
                except:
                    frames.append(False)
            
            # Calculate speech ratio
            speech_ratio = speech_frames / len(frames) if frames else 0.0
            
            # Count speech segments
            speech_segments = self._count_segments(frames)
            
            # Calculate VAD-based SNR
            vad_snr_db = self._calculate_vad_snr(y, frames, frame_length)
            
            # Determine if passes threshold
            if stage == "original":
                passes_threshold = (speech_ratio >= self.stage1_speech_ratio and 
                                 vad_snr_db >= self.stage1_vad_snr)
            else:  # stage == "chunk"
                passes_threshold = (speech_ratio >= self.stage2_speech_ratio and 
                                 vad_snr_db >= self.stage2_vad_snr)
            
            return AudioEvaluation(
                duration=duration,
                speech_ratio=speech_ratio,
                vad_snr_db=vad_snr_db,
                speech_segments_count=speech_segments,
                passes_threshold=passes_threshold
            )
            
        except Exception as e:
            logger.error(f"Error evaluating {audio_path}: {e}")
            return AudioEvaluation(0.0, 0.0, -np.inf, 0, False)
    
    def _count_segments(self, frames: List[bool]) -> int:
        """Count number of speech segments"""
        if not frames:
            return 0
        
        segments = 0
        in_segment = False
        
        for frame in frames:
            if frame and not in_segment:
                segments += 1
                in_segment = True
            elif not frame:
                in_segment = False
        
        return segments
    
    def _calculate_vad_snr(self, audio: np.ndarray, speech_frames: List[bool], 
                          frame_length: int) -> float:
        """Calculate SNR using VAD to identify speech vs noise"""
        try:
            speech_energy = []
            noise_energy = []
            
            for i, is_speech in enumerate(speech_frames):
                start_idx = i * frame_length
                end_idx = min(start_idx + frame_length, len(audio))
                frame = audio[start_idx:end_idx]
                
                energy = np.sum(frame ** 2)
                
                if is_speech:
                    speech_energy.append(energy)
                else:
                    noise_energy.append(energy)
            
            if not speech_energy or not noise_energy:
                return -np.inf
            
            avg_speech_energy = np.mean(speech_energy)
            avg_noise_energy = np.mean(noise_energy)
            
            if avg_noise_energy <= 0:
                return 50.0  # Very high SNR
            
            snr_linear = avg_speech_energy / avg_noise_energy
            snr_db = 10 * np.log10(snr_linear) if snr_linear > 0 else -np.inf
            
            return snr_db
            
        except Exception as e:
            logger.error(f"Error calculating VAD SNR: {e}")
            return -np.inf
    
    def generate_smart_chunks(self, audio_path: str, speech_frames: List[bool], 
                             frame_length: int) -> List[Tuple[float, float]]:
        """Generate intelligent chunks based on speech patterns"""
        y, sr = librosa.load(audio_path, sr=self.target_sr)
        duration = len(y) / sr
        
        if duration <= self.max_chunk_duration:
            return [(0, duration)]
        
        # Convert frame-based speech detection to time-based
        frame_duration = frame_length / sr
        
        chunks = []
        current_start = 0
        
        while current_start < duration:
            # Find target end time
            target_end = current_start + self.target_chunk_duration
            
            if target_end >= duration:
                # Final chunk
                if duration - current_start >= self.min_chunk_duration:
                    chunks.append((current_start, duration))
                break
            
            # Look for optimal split point around target
            search_start = max(current_start + self.min_chunk_duration,
                             target_end - self.chunk_tolerance)
            search_end = min(duration, target_end + self.chunk_tolerance)
            
            # Find best split point (silence or low speech activity)
            best_split = target_end
            min_activity = float('inf')
            
            for t in np.arange(search_start, search_end, 0.1):
                frame_idx = int(t / frame_duration)
                if frame_idx < len(speech_frames):
                    # Count speech frames in surrounding window
                    window_start = max(0, frame_idx - 5)
                    window_end = min(len(speech_frames), frame_idx + 5)
                    activity = sum(speech_frames[window_start:window_end])
                    
                    if activity < min_activity:
                        min_activity = activity
                        best_split = t
            
            current_end = best_split
            
            # Ensure minimum chunk duration
            if current_end - current_start >= self.min_chunk_duration:
                chunks.append((current_start, current_end))
            
            current_start = current_end
            
            if current_start >= duration:
                break
        
        return chunks
    
    def extract_and_save_chunk(self, audio_path: str, start_time: float, end_time: float,
                              workspace_dir: Path, anonymized_name: str) -> str:
        """Extract chunk from audio and save with anonymized name"""
        try:
            # Load and extract chunk
            y, sr = librosa.load(audio_path, sr=self.target_sr,
                               offset=start_time, duration=end_time - start_time)
            
            # Normalize audio
            if np.max(np.abs(y)) > 0:
                y = y / np.max(np.abs(y)) * 0.8
            
            # Save chunk
            chunk_filename = f"{anonymized_name}.wav"
            chunk_path = workspace_dir / 'chunks' / chunk_filename
            sf.write(chunk_path, y, sr)
            
            return str(chunk_path)
            
        except Exception as e:
            logger.error(f"Error extracting chunk: {e}")
            return ""
    
    async def upload_to_s3(self, file_path: str, s3_key: str) -> Optional[str]:
        """Upload file to S3 and return public URL"""
        try:
            # Upload file
            self.s3_client.upload_file(file_path, settings.s3_bucket_name, s3_key)
            
            # Generate public URL (or use presigned URL for temporary access)
            if settings.s3_presigned_url_expiry > 0:
                # Use presigned URL for temporary access
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': settings.s3_bucket_name, 'Key': s3_key},
                    ExpiresIn=settings.s3_presigned_url_expiry
                )
            else:
                # Use public URL (requires public bucket)
                url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Uploaded to S3: {s3_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return None
    
    async def upload_quality_chunks_to_s3(self, workspace_dir: Path, call_id: str) -> List[str]:
        """Upload only chunks that passed Stage 2 filters to S3"""
        final_chunks_dir = workspace_dir / 'final_chunks'
        s3_urls = []
        
        if not final_chunks_dir.exists():
            logger.warning(f"Final chunks directory not found: {final_chunks_dir}")
            return s3_urls
        
        for chunk_file in final_chunks_dir.glob('*.wav'):
            # Create S3 key: feedback-chunks/call_id/chunk_name.wav
            s3_key = f"{settings.s3_audio_prefix}/{call_id}/{chunk_file.name}"
            
            # Upload to S3
            s3_url = await self.upload_to_s3(str(chunk_file), s3_key)
            if s3_url:
                s3_urls.append(s3_url)
        
        logger.info(f"Uploaded {len(s3_urls)} quality chunks to S3 for call {call_id}")
        return s3_urls
    
    async def process_audio_file(self, audio_file_path: str, call_id: str, 
                                agent_id: str, feedback_notes: str = "") -> PreprocessingResult:
        """Process audio file through complete preprocessing pipeline"""
        start_time = datetime.now()
        
        # Create temporary workspace
        with tempfile.TemporaryDirectory(prefix=f"feedback_{call_id}_") as temp_dir:
            workspace_dir = Path(temp_dir)
            self.setup_workspace(workspace_dir)
            db_path = self.setup_database(workspace_dir)
            
            # Generate batch ID
            batch_id = f"feedback_{call_id}_{uuid.uuid4().hex[:8]}"
            
            try:
                # Stage 1: Evaluate original file
                original_eval = self.evaluate_audio(audio_file_path, stage="original")
                
                # Save to database
                with sqlite3.connect(db_path) as conn:
                    conn.execute('''
                        INSERT INTO processing_batches 
                        (batch_id, call_id, agent_id, feedback_notes, created_at, thresholds_used)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        batch_id, call_id, agent_id, feedback_notes, 
                        datetime.now().isoformat(),
                        f"S1: {self.stage1_speech_ratio:.1%}/{self.stage1_vad_snr:.1f}dB, "
                        f"S2: {self.stage2_speech_ratio:.1%}/{self.stage2_vad_snr:.1f}dB"
                    ))
                
                if not original_eval.passes_threshold:
                    logger.warning(f"Audio file {call_id} failed Stage 1 quality check")
                    return PreprocessingResult(
                        success=False,
                        batch_id=batch_id,
                        original_file_path=audio_file_path,
                        total_chunks=0,
                        quality_chunks=0,
                        s3_urls=[],
                        processing_time_seconds=0,
                        error_message="Audio failed Stage 1 quality check"
                    )
                
                logger.info(f"Audio file {call_id} passed Stage 1 quality check")
                
                # Stage 2: Generate and evaluate chunks
                y, sr = librosa.load(audio_file_path, sr=self.target_sr)
                frame_length = int(sr * self.frame_duration_ms / 1000)
                
                # Get speech frame detection for chunking
                frames = []
                for i in range(0, len(y) - frame_length, frame_length):
                    frame = y[i:i + frame_length]
                    frame_16bit = (frame * 32767).astype(np.int16).tobytes()
                    try:
                        is_speech = self.vad.is_speech(frame_16bit, sr)
                        frames.append(is_speech)
                    except:
                        frames.append(False)
                
                # Generate chunks
                chunk_times = self.generate_smart_chunks(audio_file_path, frames, frame_length)
                total_chunks = len(chunk_times)
                quality_chunks = 0
                
                # Process each chunk
                for i, (start_time_chunk, end_time_chunk) in enumerate(chunk_times):
                    # Generate anonymized name
                    anonymized_name = f"chunk_{uuid.uuid4().hex[:12]}"
                    
                    # Extract chunk
                    chunk_path = self.extract_and_save_chunk(
                        audio_file_path, start_time_chunk, end_time_chunk, 
                        workspace_dir, anonymized_name
                    )
                    
                    if not chunk_path:
                        continue
                    
                    # Evaluate chunk quality
                    chunk_eval = self.evaluate_audio(chunk_path, stage="chunk")
                    
                    if chunk_eval.passes_threshold:
                        # Copy to final_chunks directory
                        final_chunk_path = workspace_dir / 'final_chunks' / f"{anonymized_name}.wav"
                        import shutil
                        shutil.copy2(chunk_path, final_chunk_path)
                        quality_chunks += 1
                        logger.debug(f"Chunk {i+1}/{total_chunks} passed Stage 2")
                    else:
                        logger.debug(f"Chunk {i+1}/{total_chunks} failed Stage 2")
                
                # Upload quality chunks to S3
                s3_urls = []
                if quality_chunks > 0:
                    s3_urls = await self.upload_quality_chunks_to_s3(workspace_dir, call_id)
                
                # Update database with results
                processing_time_seconds = (datetime.now() - start_time).total_seconds()
                with sqlite3.connect(db_path) as conn:
                    conn.execute('''
                        UPDATE processing_batches 
                        SET total_chunks = ?, quality_chunks = ?, processing_time_seconds = ?,
                            s3_urls = ?, status = 'completed'
                        WHERE batch_id = ?
                    ''', (total_chunks, quality_chunks, processing_time_seconds,
                          ','.join(s3_urls), batch_id))
                
                logger.info(f"Processing completed for {call_id}: {quality_chunks}/{total_chunks} chunks uploaded to S3")
                
                return PreprocessingResult(
                    success=True,
                    batch_id=batch_id,
                    original_file_path=audio_file_path,
                    total_chunks=total_chunks,
                    quality_chunks=quality_chunks,
                    s3_urls=s3_urls,
                    processing_time_seconds=processing_time_seconds
                )
                
            except Exception as e:
                logger.error(f"Error processing audio file {call_id}: {e}")
                return PreprocessingResult(
                    success=False,
                    batch_id=batch_id,
                    original_file_path=audio_file_path,
                    total_chunks=0,
                    quality_chunks=0,
                    s3_urls=[],
                    processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                    error_message=str(e)
                )


# Global service instance
audio_preprocessing_service = AudioPreprocessingService()