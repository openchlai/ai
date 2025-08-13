# utils/silero_vad.py - Silero VAD for speech ratio decision-making

import torch
import numpy as np
import logging
from typing import Tuple, Dict, Any, List
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class SileroVAD:
    """Silero VAD for determining if audio should be transcribed based on speech ratio"""
    
    def __init__(self, speech_threshold: float = 0.6):
        """
        Initialize Silero VAD
        
        Args:
            speech_threshold: Minimum speech ratio (0.0-1.0) required to transcribe
        """
        self.speech_threshold = speech_threshold
        self.model = None
        self.utils = None
        self.is_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🎙️ SileroVAD initialized with {speech_threshold:.1%} speech threshold on {self.device}")
    
    def load_model(self) -> bool:
        """Load Silero VAD model"""
        try:
            logger.info("🔄 Loading Silero VAD model...")
            
            # Load Silero VAD model from torch hub
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False,  # Use PyTorch model for better compatibility
                verbose=False
            )
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info(f"✅ Silero VAD model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load Silero VAD model: {e}")
            self.is_loaded = False
            return False
    
    def analyze_speech_activity(self, audio_bytes: bytes, sample_rate: int = 16000) -> Tuple[bool, Dict[str, Any]]:
        """
        Analyze speech activity in audio and determine if it should be transcribed
        
        Args:
            audio_bytes: Raw PCM audio bytes (16-bit)
            sample_rate: Sample rate (default 16000)
        
        Returns:
            Tuple of (should_transcribe: bool, vad_info: dict)
        """
        if not self.is_loaded:
            if not self.load_model():
                return False, {"error": "Silero VAD model not loaded", "should_transcribe": False}
        
        try:
            # Convert audio bytes to float32 array
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_float32).to(self.device)
            
            # Get speech timestamps using Silero VAD
            with torch.no_grad():
                speech_timestamps = self.utils[0](audio_tensor, self.model, sampling_rate=sample_rate)
            
            # Calculate speech statistics
            total_duration = len(audio_float32) / sample_rate
            speech_duration = 0.0
            
            if speech_timestamps:
                # Sum up all speech segments (timestamps are in samples)
                for segment in speech_timestamps:
                    start_sample = segment['start']
                    end_sample = segment['end']
                    segment_duration = (end_sample - start_sample) / sample_rate
                    speech_duration += segment_duration
            
            speech_ratio = speech_duration / total_duration if total_duration > 0 else 0.0
            
            # Decision based on speech threshold
            should_transcribe = speech_ratio >= self.speech_threshold
            
            # Additional audio quality metrics
            audio_stats = {
                'peak': float(np.max(np.abs(audio_float32))),
                'rms': float(np.sqrt(np.mean(audio_float32**2))),
                'zero_crossings': int(np.sum(np.diff(np.signbit(audio_float32)))),
                'samples': len(audio_float32)
            }
            
            # Comprehensive VAD information
            vad_info = {
                'speech_ratio': float(speech_ratio),
                'total_duration': float(total_duration),
                'speech_duration': float(speech_duration),
                'silence_duration': float(total_duration - speech_duration),
                'speech_segments': len(speech_timestamps) if speech_timestamps else 0,
                'threshold': self.speech_threshold,
                'should_transcribe': should_transcribe,
                'audio_stats': audio_stats,
                'model_info': {
                    'model_type': 'silero_vad',
                    'device': str(self.device),
                    'sample_rate': sample_rate
                }
            }
            
            if not should_transcribe:
                vad_info['rejection_reason'] = f'speech ratio {speech_ratio:.1%} < {self.speech_threshold:.1%}'
            
            # Log decision
            if should_transcribe:
                logger.debug(f"✅ Silero VAD: ACCEPT - Speech ratio {speech_ratio:.1%} >= {self.speech_threshold:.1%} "
                           f"({speech_duration:.1f}s/{total_duration:.1f}s)")
            else:
                logger.info(f"🚫 Silero VAD: REJECT - Speech ratio {speech_ratio:.1%} < {self.speech_threshold:.1%} "
                          f"({speech_duration:.1f}s/{total_duration:.1f}s)")
            
            return should_transcribe, vad_info
            
        except Exception as e:
            logger.error(f"❌ Silero VAD analysis failed: {e}")
            return False, {
                "error": str(e),
                "should_transcribe": False,
                "fallback_reason": "vad_analysis_failed"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Silero VAD model information"""
        return {
            "model_name": "silero_vad",
            "model_type": "voice_activity_detection",
            "framework": "pytorch",
            "device": str(self.device) if self.device else None,
            "is_loaded": self.is_loaded,
            "speech_threshold": self.speech_threshold,
            "supported_sample_rates": [8000, 16000],
            "version": "v4.0",
            "repository": "snakers4/silero-vad"
        }

# Global instance for reuse
_silero_vad_instance = None

def get_silero_vad(speech_threshold: float = 0.6) -> SileroVAD:
    """Get or create global Silero VAD instance"""
    global _silero_vad_instance
    
    if _silero_vad_instance is None:
        _silero_vad_instance = SileroVAD(speech_threshold=speech_threshold)
    
    return _silero_vad_instance

def should_transcribe_audio(audio_bytes: bytes, sample_rate: int = 16000, 
                          speech_threshold: float = 0.6) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to determine if audio should be transcribed using Silero VAD
    
    Args:
        audio_bytes: Raw PCM audio bytes (16-bit)
        sample_rate: Sample rate (default 16000)
        speech_threshold: Minimum speech ratio required (default 0.6 = 60%)
    
    Returns:
        Tuple of (should_transcribe: bool, vad_info: dict)
    """
    vad = get_silero_vad(speech_threshold)
    return vad.analyze_speech_activity(audio_bytes, sample_rate)

# CLI testing interface
if __name__ == "__main__":
    import argparse
    import soundfile as sf
    import json
    
    parser = argparse.ArgumentParser(description="Silero VAD testing")
    parser.add_argument("audio_file", help="Audio file to analyze")
    parser.add_argument("--threshold", type=float, default=0.6, help="Speech threshold (0.0-1.0)")
    parser.add_argument("--output-json", help="Save VAD results to JSON file")
    
    args = parser.parse_args()
    
    # Load audio
    audio, sr = sf.read(args.audio_file)
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)  # Convert to mono
    
    # Convert to 16kHz if needed
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    
    # Convert to PCM bytes
    audio_int16 = (audio * 32768.0).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    
    # Run Silero VAD
    should_transcribe, vad_info = should_transcribe_audio(audio_bytes, 16000, args.threshold)
    
    print(f"Silero VAD Analysis Results:")
    print(f"  Should transcribe: {should_transcribe}")
    print(f"  Speech ratio: {vad_info.get('speech_ratio', 0):.1%}")
    print(f"  Speech duration: {vad_info.get('speech_duration', 0):.1f}s")
    print(f"  Total duration: {vad_info.get('total_duration', 0):.1f}s")
    print(f"  Speech segments: {vad_info.get('speech_segments', 0)}")
    
    if not should_transcribe:
        print(f"  Rejection reason: {vad_info.get('rejection_reason', 'unknown')}")
    
    # Save results
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(vad_info, f, indent=2)
        print(f"  Results saved to: {args.output_json}")