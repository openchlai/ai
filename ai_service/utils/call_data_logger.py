# utils/call_data_logger.py - Comprehensive per-call data logging system

import os
import json
import logging
import soundfile as sf
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class TCPPacketInfo:
    """Information about a TCP packet"""
    packet_id: int
    timestamp: datetime
    size_bytes: int
    hex_preview: str  # First 32 bytes as hex
    ascii_preview: str  # First 64 bytes as ASCII (with errors replaced)
    is_audio_data: bool
    call_phase: str  # 'uid_negotiation', 'audio_streaming'
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class AudioSegmentInfo:
    """Information about an audio processing segment"""
    segment_id: int
    timestamp: datetime
    duration_seconds: float
    sample_rate: int
    audio_size_bytes: int
    chunk_filename: str
    buffer_stats: Dict[str, Any]
    vad_info: Optional[Dict[str, Any]]
    quality_metrics: Dict[str, Any]
    processing_status: str  # 'pending', 'processed', 'rejected'
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class TranscriptionInfo:
    """Information about a transcription attempt"""
    transcription_id: int
    segment_id: int  # Links to AudioSegmentInfo
    timestamp: datetime
    transcript_text: str
    processing_duration: float
    whisper_params: Dict[str, Any]
    confidence_metrics: Optional[Dict[str, Any]]
    rejected_by_vad: bool
    language_used: Optional[str]
    audio_correlation: Dict[str, Any]  # Audio characteristics for this transcription
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class CallDataLogger:
    """Comprehensive logging system for individual call sessions"""
    
    def __init__(self, call_id: str, base_log_dir: str = "/tmp/ai_service_logs/calls"):
        self.call_id = call_id
        self.base_log_dir = base_log_dir
        self.start_time = datetime.now(timezone.utc)
        
        # Create call-specific directory structure
        timestamp_str = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.call_dir = Path(base_log_dir) / f"call_{call_id}_{timestamp_str}"
        self.audio_chunks_dir = self.call_dir / "audio_chunks"
        
        # Data storage
        self.tcp_packets: List[TCPPacketInfo] = []
        self.audio_segments: List[AudioSegmentInfo] = []
        self.transcriptions: List[TranscriptionInfo] = []
        
        # Counters
        self.packet_counter = 0
        self.segment_counter = 0
        self.transcription_counter = 0
        
        # Initialize directory structure
        self._setup_directory_structure()
        
        # Initialize log files
        self._setup_log_files()
        
        logger.info(f"📁 Call data logger initialized for {call_id} at {self.call_dir}")
    
    def _setup_directory_structure(self):
        """Create directory structure for call logging"""
        try:
            self.call_dir.mkdir(parents=True, exist_ok=True)
            self.audio_chunks_dir.mkdir(exist_ok=True)
            
            # Create subdirectories for organization
            (self.call_dir / "logs").mkdir(exist_ok=True)
            (self.call_dir / "analysis").mkdir(exist_ok=True)
            
            logger.info(f"📁 Created logging directory: {self.call_dir}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create logging directory {self.call_dir}: {e}")
            raise
    
    def _setup_log_files(self):
        """Initialize structured log files"""
        try:
            # Create individual log files for different data types
            self.tcp_log_file = self.call_dir / "logs" / "tcp_packets.jsonl"
            self.audio_log_file = self.call_dir / "logs" / "audio_segments.jsonl"
            self.transcription_log_file = self.call_dir / "logs" / "transcriptions.jsonl"
            self.vad_log_file = self.call_dir / "logs" / "vad_decisions.jsonl"
            
            # Create header information
            call_metadata = {
                "call_id": self.call_id,
                "logger_version": "1.0",
                "start_time": self.start_time.isoformat(),
                "log_directory": str(self.call_dir),
                "created_by": "ai_service_call_logger"
            }
            
            # Write metadata to a summary file
            with open(self.call_dir / "call_metadata.json", 'w') as f:
                json.dump(call_metadata, f, indent=2)
                
            logger.info(f"📄 Initialized log files for call {self.call_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize log files: {e}")
            raise
    
    def log_tcp_packet(self, packet_data: bytes, is_audio_data: bool = False, call_phase: str = "unknown") -> int:
        """Log TCP packet information with timing"""
        try:
            self.packet_counter += 1
            
            # Create packet info
            packet_info = TCPPacketInfo(
                packet_id=self.packet_counter,
                timestamp=datetime.now(timezone.utc),
                size_bytes=len(packet_data),
                hex_preview=packet_data[:32].hex(),
                ascii_preview=packet_data[:64].decode('ascii', errors='replace'),
                is_audio_data=is_audio_data,
                call_phase=call_phase
            )
            
            # Store in memory
            self.tcp_packets.append(packet_info)
            
            # Write to log file immediately (for real-time monitoring)
            with open(self.tcp_log_file, 'a') as f:
                f.write(json.dumps(packet_info.to_dict()) + '\n')
            
            # Log to main logger every 50 packets to avoid spam
            if self.packet_counter % 50 == 0:
                logger.info(f"📦 Logged {self.packet_counter} TCP packets for call {self.call_id}")
            
            return packet_info.packet_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log TCP packet for call {self.call_id}: {e}")
            return -1
    
    def log_audio_segment(self, audio_bytes: bytes, duration_seconds: float, 
                         sample_rate: int = 16000, buffer_stats: Dict[str, Any] = None,
                         vad_info: Dict[str, Any] = None) -> tuple[int, str]:
        """
        Log audio segment and save as WAV file
        
        Returns:
            tuple: (segment_id, audio_filename)
        """
        try:
            self.segment_counter += 1
            
            # Create unique filename for audio chunk
            timestamp_str = datetime.now().strftime("%H%M%S_%f")[:-3]  # Include milliseconds
            chunk_filename = f"chunk_{self.segment_counter:03d}_{duration_seconds:.1f}s_{timestamp_str}.wav"
            chunk_filepath = self.audio_chunks_dir / chunk_filename
            
            # Convert audio bytes to numpy array and save as WAV
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # Save audio file
            sf.write(str(chunk_filepath), audio_float32, sample_rate)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_audio_quality_metrics(audio_float32, sample_rate)
            
            # Create segment info
            segment_info = AudioSegmentInfo(
                segment_id=self.segment_counter,
                timestamp=datetime.now(timezone.utc),
                duration_seconds=duration_seconds,
                sample_rate=sample_rate,
                audio_size_bytes=len(audio_bytes),
                chunk_filename=chunk_filename,
                buffer_stats=buffer_stats or {},
                vad_info=vad_info,
                quality_metrics=quality_metrics,
                processing_status="pending"
            )
            
            # Store in memory
            self.audio_segments.append(segment_info)
            
            # Write to log file
            with open(self.audio_log_file, 'a') as f:
                f.write(json.dumps(segment_info.to_dict()) + '\n')
            
            # Write VAD info separately if available
            if vad_info:
                vad_entry = {
                    "segment_id": self.segment_counter,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "call_id": self.call_id,
                    "vad_decision": vad_info
                }
                with open(self.vad_log_file, 'a') as f:
                    f.write(json.dumps(vad_entry) + '\n')
            
            logger.info(f"🎵 Logged audio segment {self.segment_counter} for call {self.call_id}: "
                       f"{duration_seconds:.1f}s, {len(audio_bytes)} bytes → {chunk_filename}")
            
            return segment_info.segment_id, chunk_filename
            
        except Exception as e:
            logger.error(f"❌ Failed to log audio segment for call {self.call_id}: {e}")
            return -1, ""
    
    def _calculate_audio_quality_metrics(self, audio_array: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Calculate comprehensive audio quality metrics"""
        try:
            duration = len(audio_array) / sample_rate
            peak = float(np.max(np.abs(audio_array)))
            rms = float(np.sqrt(np.mean(audio_array**2)))
            
            # Silence analysis
            silence_threshold = 0.01
            silence_ratio = float(np.sum(np.abs(audio_array) < silence_threshold) / len(audio_array))
            
            # Zero crossing rate
            zero_crossings = int(np.sum(np.diff(np.signbit(audio_array))))
            zcr = zero_crossings / len(audio_array)
            
            # Dynamic range
            dynamic_range = peak / (rms + 1e-8)
            
            # Clipping detection
            clipping_ratio = float(np.sum(np.abs(audio_array) > 0.99) / len(audio_array))
            
            return {
                "duration_seconds": duration,
                "peak_amplitude": peak,
                "rms_amplitude": rms,
                "dynamic_range": dynamic_range,
                "silence_ratio": silence_ratio,
                "zero_crossing_rate": zcr,
                "clipping_ratio": clipping_ratio,
                "sample_count": len(audio_array),
                "estimated_snr_db": float(20 * np.log10(rms + 1e-8)) if rms > 0 else -100.0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate audio quality metrics: {e}")
            return {"error": str(e)}
    
    def log_transcription(self, segment_id: int, transcript: str, processing_duration: float,
                         whisper_params: Dict[str, Any] = None, rejected_by_vad: bool = False,
                         language_used: str = None, confidence_metrics: Dict[str, Any] = None) -> int:
        """Log transcription result with correlation to audio segment"""
        try:
            self.transcription_counter += 1
            
            # Find corresponding audio segment for correlation
            audio_correlation = {}
            corresponding_segment = None
            for segment in self.audio_segments:
                if segment.segment_id == segment_id:
                    corresponding_segment = segment
                    audio_correlation = {
                        "audio_duration": segment.duration_seconds,
                        "audio_quality": segment.quality_metrics,
                        "vad_applied": segment.vad_info is not None,
                        "chunk_filename": segment.chunk_filename
                    }
                    break
            
            # Create transcription info
            transcription_info = TranscriptionInfo(
                transcription_id=self.transcription_counter,
                segment_id=segment_id,
                timestamp=datetime.now(timezone.utc),
                transcript_text=transcript,
                processing_duration=processing_duration,
                whisper_params=whisper_params or {},
                confidence_metrics=confidence_metrics,
                rejected_by_vad=rejected_by_vad,
                language_used=language_used,
                audio_correlation=audio_correlation
            )
            
            # Update audio segment status
            if corresponding_segment:
                corresponding_segment.processing_status = "rejected" if rejected_by_vad else "processed"
            
            # Store in memory
            self.transcriptions.append(transcription_info)
            
            # Write to log file
            with open(self.transcription_log_file, 'a') as f:
                f.write(json.dumps(transcription_info.to_dict()) + '\n')
            
            # Log summary
            transcript_preview = transcript[:100] + "..." if len(transcript) > 100 else transcript
            logger.info(f"📝 Logged transcription {self.transcription_counter} for call {self.call_id}: "
                       f"'{transcript_preview}' (segment {segment_id}, {processing_duration:.2f}s)")
            
            return transcription_info.transcription_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log transcription for call {self.call_id}: {e}")
            return -1
    
    def update_audio_segment_status(self, segment_id: int, status: str, additional_info: Dict[str, Any] = None):
        """Update the processing status of an audio segment"""
        try:
            for segment in self.audio_segments:
                if segment.segment_id == segment_id:
                    segment.processing_status = status
                    if additional_info:
                        # Add additional info to quality metrics or buffer stats
                        segment.quality_metrics.update(additional_info.get('quality_updates', {}))
                    break
            
            logger.debug(f"Updated segment {segment_id} status to '{status}' for call {self.call_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update segment status: {e}")
    
    def generate_call_summary(self) -> Dict[str, Any]:
        """Generate comprehensive call summary"""
        try:
            end_time = datetime.now(timezone.utc)
            call_duration = (end_time - self.start_time).total_seconds()
            
            # Calculate statistics
            total_audio_duration = sum(segment.duration_seconds for segment in self.audio_segments)
            total_transcriptions = len(self.transcriptions)
            successful_transcriptions = len([t for t in self.transcriptions if not t.rejected_by_vad])
            rejected_by_vad = len([t for t in self.transcriptions if t.rejected_by_vad])
            
            # Audio quality statistics
            if self.audio_segments:
                avg_quality = {}
                quality_keys = ['peak_amplitude', 'rms_amplitude', 'silence_ratio', 'zero_crossing_rate']
                for key in quality_keys:
                    values = [segment.quality_metrics.get(key, 0) for segment in self.audio_segments 
                             if segment.quality_metrics and key in segment.quality_metrics]
                    if values:
                        avg_quality[f'avg_{key}'] = float(np.mean(values))
                        avg_quality[f'std_{key}'] = float(np.std(values))
            else:
                avg_quality = {}
            
            # Processing statistics
            transcription_times = [t.processing_duration for t in self.transcriptions]
            avg_processing_time = float(np.mean(transcription_times)) if transcription_times else 0.0
            
            summary = {
                "call_metadata": {
                    "call_id": self.call_id,
                    "start_time": self.start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "total_call_duration_seconds": call_duration,
                    "log_directory": str(self.call_dir)
                },
                "tcp_statistics": {
                    "total_packets": len(self.tcp_packets),
                    "audio_packets": len([p for p in self.tcp_packets if p.is_audio_data]),
                    "total_data_bytes": sum(p.size_bytes for p in self.tcp_packets)
                },
                "audio_statistics": {
                    "total_segments": len(self.audio_segments),
                    "total_audio_duration_seconds": total_audio_duration,
                    "average_segment_duration": total_audio_duration / len(self.audio_segments) if self.audio_segments else 0,
                    "audio_quality_metrics": avg_quality
                },
                "transcription_statistics": {
                    "total_transcription_attempts": total_transcriptions,
                    "successful_transcriptions": successful_transcriptions,
                    "rejected_by_vad": rejected_by_vad,
                    "success_rate": successful_transcriptions / total_transcriptions if total_transcriptions > 0 else 0,
                    "average_processing_time_seconds": avg_processing_time
                },
                "file_locations": {
                    "tcp_log": str(self.tcp_log_file),
                    "audio_log": str(self.audio_log_file),
                    "transcription_log": str(self.transcription_log_file),
                    "vad_log": str(self.vad_log_file),
                    "audio_chunks_directory": str(self.audio_chunks_dir)
                }
            }
            
            # Save summary to file
            summary_file = self.call_dir / "call_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📊 Generated call summary for {self.call_id}: "
                       f"{total_transcriptions} transcriptions, "
                       f"{total_audio_duration:.1f}s audio, "
                       f"{successful_transcriptions}/{total_transcriptions} success rate")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate call summary for {self.call_id}: {e}")
            return {"error": str(e)}
    
    def finalize_call(self) -> str:
        """Finalize call logging and return summary file path"""
        try:
            summary = self.generate_call_summary()
            summary_file = self.call_dir / "call_summary.json"
            
            logger.info(f"🏁 Finalized call logging for {self.call_id} at {self.call_dir}")
            logger.info(f"📁 Call data: {len(self.tcp_packets)} packets, "
                       f"{len(self.audio_segments)} audio segments, "
                       f"{len(self.transcriptions)} transcriptions")
            
            return str(summary_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to finalize call logging: {e}")
            return ""
    
    def get_call_directory(self) -> str:
        """Get the call's logging directory path"""
        return str(self.call_dir)
    
    def get_audio_chunks_directory(self) -> str:
        """Get the directory containing audio chunks"""
        return str(self.audio_chunks_dir)
    
    def list_audio_files(self) -> List[str]:
        """List all audio files for this call"""
        try:
            audio_files = []
            for segment in self.audio_segments:
                audio_file_path = self.audio_chunks_dir / segment.chunk_filename
                if audio_file_path.exists():
                    audio_files.append(str(audio_file_path))
            
            return sorted(audio_files)
            
        except Exception as e:
            logger.error(f"❌ Failed to list audio files: {e}")
            return []

# Global registry for active call loggers
_active_call_loggers: Dict[str, CallDataLogger] = {}

def get_call_logger(call_id: str, create_if_not_exists: bool = True) -> Optional[CallDataLogger]:
    """Get or create a call logger for the given call ID"""
    global _active_call_loggers
    
    if call_id in _active_call_loggers:
        return _active_call_loggers[call_id]
    elif create_if_not_exists:
        try:
            # Check if logging is enabled
            enable_logging = os.getenv("ENABLE_CALL_DATA_LOGGING", "true").lower() == "true"
            if not enable_logging:
                return None
            
            # Create new logger
            call_logger = CallDataLogger(call_id)
            _active_call_loggers[call_id] = call_logger
            return call_logger
            
        except Exception as e:
            logger.error(f"❌ Failed to create call logger for {call_id}: {e}")
            return None
    else:
        return None

def finalize_call_logger(call_id: str) -> Optional[str]:
    """Finalize and remove call logger, return summary file path"""
    global _active_call_loggers
    
    if call_id in _active_call_loggers:
        call_logger = _active_call_loggers[call_id]
        summary_file = call_logger.finalize_call()
        del _active_call_loggers[call_id]
        return summary_file
    else:
        return None

def cleanup_old_call_logs(retention_days: int = 7):
    """Clean up old call logs based on retention policy"""
    try:
        base_log_dir = os.getenv("CALL_LOGS_DIRECTORY", "/tmp/ai_service_logs/calls")
        if not os.path.exists(base_log_dir):
            return
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleaned_count = 0
        for call_dir in Path(base_log_dir).iterdir():
            if call_dir.is_dir() and call_dir.name.startswith("call_"):
                try:
                    # Parse timestamp from directory name
                    # Format: call_{call_id}_{YYYYMMDD_HHMMSS}
                    parts = call_dir.name.split('_')
                    if len(parts) >= 3:
                        timestamp_str = '_'.join(parts[-2:])  # Get date_time part
                        call_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        
                        if call_date < cutoff_date:
                            # Remove old call directory
                            import shutil
                            shutil.rmtree(call_dir)
                            cleaned_count += 1
                            logger.info(f"🧹 Cleaned up old call log: {call_dir.name}")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process call directory {call_dir}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} old call log directories")
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup old call logs: {e}")

# Command line interface for call log analysis
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Call Data Logger utilities")
    parser.add_argument("--cleanup-old-logs", action="store_true", help="Clean up old call logs")
    parser.add_argument("--retention-days", type=int, default=7, help="Retention period in days")
    parser.add_argument("--analyze-call", help="Analyze specific call directory")
    parser.add_argument("--list-calls", action="store_true", help="List all logged calls")
    
    args = parser.parse_args()
    
    if args.cleanup_old_logs:
        cleanup_old_call_logs(args.retention_days)
    elif args.analyze_call:
        # Analyze specific call (placeholder for future implementation)
        print(f"Analyzing call: {args.analyze_call}")
    elif args.list_calls:
        # List all calls (placeholder for future implementation)
        base_log_dir = os.getenv("CALL_LOGS_DIRECTORY", "/tmp/ai_service_logs/calls")
        if os.path.exists(base_log_dir):
            call_dirs = [d.name for d in Path(base_log_dir).iterdir() if d.is_dir() and d.name.startswith("call_")]
            print(f"Found {len(call_dirs)} call log directories:")
            for call_dir in sorted(call_dirs):
                print(f"  {call_dir}")
        else:
            print(f"No call logs directory found at {base_log_dir}")
    else:
        print("Use --help for available options")