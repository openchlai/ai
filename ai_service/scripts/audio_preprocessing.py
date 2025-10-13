#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Preprocessing Script for AI Service
==========================================

This script handles two-stage audio preprocessing with intelligent chunking,
quality analysis, and integration with the existing ai_service infrastructure.

Usage:
    python scripts/audio_preprocessing_clean.py /path/to/audio/files --batch-name "batch_001"
    python scripts/audio_preprocessing_clean.py /path/to/audio/files --stage1-speech-ratio 0.6 --stage1-vad-snr 8
"""

import os
import sys
import argparse
import hashlib
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import numpy as np
import librosa
import soundfile as sf
import webrtcvad
from scipy import signal

# Add the ai_service app to Python path for imports
sys.path.append(str(Path(__file__).parent.parent / 'app'))

# Fixed imports to match actual codebase structure
try:
    from config.settings import Settings
    settings = Settings()
except ImportError:
    print("Warning: Could not import settings, using defaults")
    class MockSettings:
        log_level = "INFO"
        temp_path = "./temp"
    settings = MockSettings()

logger = logging.getLogger(__name__)


@dataclass
class AudioEvaluation:
    """Results of audio quality evaluation"""
    duration: float
    speech_ratio: float
    vad_snr_db: float
    speech_segments_count: int
    passes_threshold: bool


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('audio_preprocessing.log', mode='a')
        ]
    )


class AudioPreprocessor:
    """Enhanced audio preprocessor for ai_service integration"""
    
    def __init__(self, 
                 workspace_dir: str = "audio_workspace",
                 stage1_speech_ratio: float = 0.7,
                 stage1_vad_snr: float = 10.0,
                 stage2_speech_ratio: float = 0.9,
                 stage2_vad_snr: float = 25.0):
        """
        Initialize preprocessor with configurable thresholds
        
        Args:
            workspace_dir: Directory for processing workspace
            stage1_speech_ratio: Minimum speech ratio for original files
            stage1_vad_snr: Minimum VAD SNR for original files (dB)
            stage2_speech_ratio: Minimum speech ratio for chunks
            stage2_vad_snr: Minimum VAD SNR for chunks (dB)
        """
        self.workspace_dir = Path(workspace_dir)
        self.setup_workspace()
        
        # Audio processing parameters
        self.target_sr = 16000  # Target sample rate
        self.frame_duration_ms = 30  # VAD frame duration
        self.hop_length = 512
        self.n_fft = 2048
        
        # Quality thresholds
        self.stage1_speech_ratio = stage1_speech_ratio
        self.stage1_vad_snr = stage1_vad_snr
        self.stage2_speech_ratio = stage2_speech_ratio
        self.stage2_vad_snr = stage2_vad_snr
        
        # Chunking parameters
        self.min_chunk_duration = 3.0
        self.max_chunk_duration = 30.0
        self.target_chunk_duration = 12.0
        self.chunk_tolerance = 2.0
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
        # Database setup
        self.setup_database()
        
        logger.info(f"Preprocessor initialized with workspace: {self.workspace_dir}")
        logger.info(f"Stage 1 thresholds: speech_ratio >= {stage1_speech_ratio:.1%}, VAD SNR >= {stage1_vad_snr:.1f} dB")
        logger.info(f"Stage 2 thresholds: speech_ratio >= {stage2_speech_ratio:.1%}, VAD SNR >= {stage2_vad_snr:.1f} dB")
    
    def setup_workspace(self):
        """Create workspace directory structure"""
        directories = [
            'original_audio',
            'chunks', 
            'final_chunks',
            'metadata',
            'exports'
        ]
        
        for directory in directories:
            (self.workspace_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        os.chmod(self.workspace_dir, 0o700)
    
    def setup_database(self):
        """Initialize SQLite database for tracking"""
        self.db_path = self.workspace_dir / 'metadata' / 'preprocessing.db'
        
        with sqlite3.connect(self.db_path) as conn:
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Processing batches table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processing_batches (
                    batch_id TEXT PRIMARY KEY,
                    batch_name TEXT,
                    source_directory TEXT,
                    created_at TEXT,
                    total_files INTEGER,
                    stage1_passed INTEGER,
                    chunks_created INTEGER,
                    stage2_passed INTEGER,
                    status TEXT DEFAULT 'processing',
                    stage1_avg_speech_ratio REAL,
                    stage1_avg_vad_snr REAL,
                    stage1_total_duration_hours REAL,
                    stage2_avg_speech_ratio REAL,
                    stage2_avg_vad_snr REAL,
                    stage2_total_duration_hours REAL,
                    processing_time_minutes REAL,
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
                    processed_at TEXT,
                    FOREIGN KEY (file_id) REFERENCES original_files (file_id)
                )
            ''')
    
    def get_db_connection(self):
        """Get database connection with timeout"""
        return sqlite3.connect(self.db_path, timeout=30.0)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file for deduplication"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
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
    
    def process_single_file(self, audio_path: str, batch_id: str) -> Dict:
        """Process a single audio file through both stages"""
        file_name = Path(audio_path).name
        file_id = f"{batch_id}_{hashlib.md5(file_name.encode()).hexdigest()[:12]}"
        
        logger.info(f"Processing: {file_name}")
        
        try:
            # Calculate file hash for deduplication
            file_hash = self.calculate_file_hash(audio_path)
            
            # Stage 1: Evaluate original file
            original_eval = self.evaluate_audio(audio_path, stage="original")
            
            # Save original evaluation to database
            with self.get_db_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO original_files 
                    (file_id, batch_id, file_name, file_path, file_hash, duration, 
                     sample_rate, speech_ratio, vad_snr_db, speech_segments_count, 
                     passes_stage1, processed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id, batch_id, file_name, str(audio_path), file_hash,
                    float(original_eval.duration), self.target_sr,
                    float(original_eval.speech_ratio), float(original_eval.vad_snr_db),
                    int(original_eval.speech_segments_count),
                    1 if original_eval.passes_threshold else 0,
                    datetime.now().isoformat()
                ))
            
            result = {
                'file_name': file_name,
                'original_evaluation': original_eval,
                'passes_stage1': original_eval.passes_threshold,
                'chunks_created': 0,
                'chunks_passed_stage2': 0,
                'chunk_details': []
            }
            
            if not original_eval.passes_threshold:
                logger.warning(f"FAIL {file_name} failed Stage 1 quality check")
                return result
            
            logger.info(f"PASS {file_name} passed Stage 1 quality check")
            
            # Stage 2: Generate and evaluate chunks
            y, sr = librosa.load(audio_path, sr=self.target_sr)
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
            chunk_times = self.generate_smart_chunks(audio_path, frames, frame_length)
            result['chunks_created'] = len(chunk_times)
            
            # Process each chunk
            for i, (start_time, end_time) in enumerate(chunk_times):
                # Generate anonymized name
                anonymized_name = f"chunk_{uuid.uuid4().hex[:12]}"
                chunk_id = f"{file_id}_chunk_{i:03d}"
                
                # Extract chunk
                chunk_path = self.extract_and_save_chunk(
                    audio_path, start_time, end_time, chunk_id, anonymized_name
                )
                
                if not chunk_path:
                    continue
                
                # Evaluate chunk quality
                chunk_eval = self.evaluate_audio(chunk_path, stage="chunk")
                
                final_chunk_path = ""
                if chunk_eval.passes_threshold:
                    # Copy to final_chunks directory
                    final_chunk_path = str(self.workspace_dir / 'final_chunks' / f"{anonymized_name}.wav")
                    import shutil
                    shutil.copy2(chunk_path, final_chunk_path)
                    result['chunks_passed_stage2'] += 1
                    logger.info(f"  PASS Chunk {i+1}/{len(chunk_times)} passed Stage 2")
                else:
                    logger.info(f"  FAIL Chunk {i+1}/{len(chunk_times)} failed Stage 2")
                
                # Save chunk to database
                with self.get_db_connection() as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO chunks
                        (chunk_id, anonymized_name, file_id, start_time, end_time, duration,
                         speech_ratio, vad_snr_db, speech_segments_count, passes_stage2,
                         chunk_path, final_chunk_path, processed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        chunk_id, anonymized_name, file_id,
                        float(start_time), float(end_time), float(chunk_eval.duration),
                        float(chunk_eval.speech_ratio), float(chunk_eval.vad_snr_db),
                        int(chunk_eval.speech_segments_count),
                        1 if chunk_eval.passes_threshold else 0,
                        chunk_path, final_chunk_path, datetime.now().isoformat()
                    ))
                
                result['chunk_details'].append({
                    'chunk_index': i,
                    'anonymized_name': anonymized_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'evaluation': chunk_eval,
                    'passes_stage2': chunk_eval.passes_threshold
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}")
            return {
                'file_name': file_name,
                'error': str(e),
                'chunks_created': 0,
                'chunks_passed_stage2': 0
            }
    
    def extract_and_save_chunk(self, audio_path: str, start_time: float, end_time: float,
                              chunk_id: str, anonymized_name: str) -> str:
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
            chunk_path = self.workspace_dir / 'chunks' / chunk_filename
            sf.write(chunk_path, y, sr)
            
            return str(chunk_path)
            
        except Exception as e:
            logger.error(f"Error extracting chunk: {e}")
            return ""
    
    def process_directory(self, directory_path: str, batch_name: str = None, 
                         max_files: int = None) -> Dict:
        """Process all audio files in a directory"""
        processing_start_time = datetime.now()
        
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Find audio files
        audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac', '.ogg']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(list(directory.glob(f"*{ext}")))
            audio_files.extend(list(directory.glob(f"*{ext.upper()}")))
        
        if not audio_files:
            raise ValueError(f"No audio files found in {directory_path}")
        
        # Limit files if requested
        if max_files is not None and max_files > 0:
            audio_files = audio_files[:max_files]
            logger.info(f"Limited to first {max_files} files")
        
        # Create batch
        if batch_name is None:
            batch_name = f"batch_{directory.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        batch_id = f"{batch_name}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Starting batch processing: {batch_name}")
        logger.info(f"Source directory: {directory_path}")
        logger.info(f"Files to process: {len(audio_files)}")
        
        # Initialize batch in database
        with self.get_db_connection() as conn:
            conn.execute('''
                INSERT INTO processing_batches 
                (batch_id, batch_name, source_directory, created_at, total_files, thresholds_used)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                batch_id, batch_name, str(directory_path), datetime.now().isoformat(),
                len(audio_files), 
                f"S1: {self.stage1_speech_ratio:.1%}/{self.stage1_vad_snr:.1f}dB, "
                f"S2: {self.stage2_speech_ratio:.1%}/{self.stage2_vad_snr:.1f}dB"
            ))
        
        # Process files
        results = []
        stage1_passed = 0
        total_chunks = 0
        stage2_passed = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"Processing file {i}/{len(audio_files)}: {audio_file.name}")
            
            result = self.process_single_file(str(audio_file), batch_id)
            results.append(result)
            
            if result.get('passes_stage1', False):
                stage1_passed += 1
            
            total_chunks += result.get('chunks_created', 0)
            stage2_passed += result.get('chunks_passed_stage2', 0)
        
        # Calculate processing time
        processing_end_time = datetime.now()
        processing_time = (processing_end_time - processing_start_time).total_seconds() / 60
        
        # Update batch status
        with self.get_db_connection() as conn:
            conn.execute('''
                UPDATE processing_batches 
                SET stage1_passed = ?, chunks_created = ?, stage2_passed = ?,
                    processing_time_minutes = ?, status = 'completed'
                WHERE batch_id = ?
            ''', (stage1_passed, total_chunks, stage2_passed, processing_time, batch_id))
        
        summary = {
            'batch_id': batch_id,
            'batch_name': batch_name,
            'total_files': len(audio_files),
            'stage1_passed': stage1_passed,
            'chunks_created': total_chunks,
            'stage2_passed': stage2_passed,
            'processing_time_minutes': processing_time,
            'results': results
        }
        
        logger.info(f"Batch processing completed!")
        logger.info(f"Summary: {stage1_passed}/{len(audio_files)} files passed Stage 1")
        logger.info(f"Generated {total_chunks} chunks, {stage2_passed} passed Stage 2")
        logger.info(f"Processing time: {processing_time:.1f} minutes")
        
        return summary


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Audio preprocessing with two-stage quality analysis and Label Studio export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default thresholds
  python scripts/audio_preprocessing_clean.py /path/to/audio/files
  
  # Custom batch name and file limit
  python scripts/audio_preprocessing_clean.py /path/to/audio/files --batch-name "test_batch" --max-files 10
  
  # Lenient Stage 1 thresholds
  python scripts/audio_preprocessing_clean.py /path/to/audio/files --stage1-speech-ratio 0.6 --stage1-vad-snr 8
        """
    )
    
    parser.add_argument("directory", help="Directory containing audio files")
    parser.add_argument("--batch-name", help="Custom batch name")
    parser.add_argument("--workspace", default="audio_workspace",
                       help="Workspace directory (default: audio_workspace)")
    parser.add_argument("--max-files", type=int, default=None,
                       help="Maximum number of files to process")
    
    # Stage 1 threshold arguments
    parser.add_argument("--stage1-speech-ratio", type=float, default=0.7,
                       help="Stage 1: Minimum speech ratio (default: 0.7)")
    parser.add_argument("--stage1-vad-snr", type=float, default=10.0,
                       help="Stage 1: Minimum VAD SNR in dB (default: 10.0)")
    
    # Stage 2 threshold arguments
    parser.add_argument("--stage2-speech-ratio", type=float, default=0.9,
                       help="Stage 2: Minimum speech ratio (default: 0.9)")
    parser.add_argument("--stage2-vad-snr", type=float, default=25.0,
                       help="Stage 2: Minimum VAD SNR in dB (default: 25.0)")
    
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    try:
        # Initialize processor
        processor = AudioPreprocessor(
            workspace_dir=args.workspace,
            stage1_speech_ratio=args.stage1_speech_ratio,
            stage1_vad_snr=args.stage1_vad_snr,
            stage2_speech_ratio=args.stage2_speech_ratio,
            stage2_vad_snr=args.stage2_vad_snr
        )
        
        # Process directory
        results = processor.process_directory(
            args.directory,
            args.batch_name,
            args.max_files
        )
        
        print(f"\nProcessing complete!")
        print(f"Final chunks location: {processor.workspace_dir / 'final_chunks'}")
        print(f"Database location: {processor.db_path}")
        print(f"{results['stage2_passed']} high-quality chunks ready for annotation")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()