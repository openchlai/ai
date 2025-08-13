# utils/audio_debug.py - Audio Quality Analysis Utility for Debugging Whisper Hallucinations

import os
import sys
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AudioQualityAnalyzer:
    """Analyze audio quality to diagnose Whisper transcription issues"""
    
    def __init__(self):
        self.sample_rate = 16000  # Whisper's expected sample rate
        
    def analyze_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive audio quality analysis"""
        try:
            # Load audio file
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            
            # Basic statistics
            duration = len(audio_data) / sr
            peak = float(np.max(np.abs(audio_data)))
            rms = float(np.sqrt(np.mean(audio_data**2)))
            
            # Audio quality metrics
            analysis = {
                "file_info": {
                    "path": file_path,
                    "duration": duration,
                    "samples": len(audio_data),
                    "sample_rate": sr
                },
                "amplitude_stats": {
                    "peak": peak,
                    "rms": rms,
                    "dynamic_range": peak / (rms + 1e-8),
                    "clipping_ratio": float(np.sum(np.abs(audio_data) > 0.99) / len(audio_data))
                },
                "silence_analysis": self._analyze_silence(audio_data),
                "spectral_analysis": self._analyze_spectrum(audio_data, sr),
                "voice_activity": self._detect_voice_activity(audio_data, sr),
                "quality_issues": self._detect_quality_issues(audio_data, sr),
                "whisper_readiness": self._assess_whisper_readiness(audio_data, sr, duration)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze audio file {file_path}: {e}")
            return {"error": str(e)}
    
    def _analyze_silence(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Analyze silence patterns in audio"""
        # Different silence thresholds
        silence_thresholds = [0.001, 0.005, 0.01, 0.05]
        silence_analysis = {}
        
        for threshold in silence_thresholds:
            silence_mask = np.abs(audio_data) < threshold
            silence_ratio = float(np.sum(silence_mask) / len(audio_data))
            silence_analysis[f"silence_ratio_{threshold}"] = silence_ratio
        
        # Silence segment analysis
        silence_segments = self._find_silence_segments(audio_data, threshold=0.01)
        silence_analysis.update({
            "silence_segments_count": len(silence_segments),
            "longest_silence_duration": max([seg[1] - seg[0] for seg in silence_segments], default=0) / self.sample_rate,
            "total_silence_duration": sum([seg[1] - seg[0] for seg in silence_segments]) / self.sample_rate
        })
        
        return silence_analysis
    
    def _find_silence_segments(self, audio_data: np.ndarray, threshold: float = 0.01) -> List[Tuple[int, int]]:
        """Find continuous silence segments"""
        silence_mask = np.abs(audio_data) < threshold
        
        # Find segment boundaries
        diff = np.diff(np.concatenate(([False], silence_mask, [False])).astype(int))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        
        return list(zip(starts, ends))
    
    def _analyze_spectrum(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze frequency spectrum characteristics"""
        # Compute FFT
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        magnitude = np.abs(fft)
        
        # Focus on positive frequencies
        positive_freq_idx = freqs >= 0
        freqs = freqs[positive_freq_idx]
        magnitude = magnitude[positive_freq_idx]
        
        # Frequency band analysis
        def get_band_energy(low_freq: float, high_freq: float) -> float:
            band_idx = (freqs >= low_freq) & (freqs <= high_freq)
            return float(np.sum(magnitude[band_idx]) / np.sum(magnitude) * 100) if np.sum(magnitude) > 0 else 0
        
        return {
            "fundamental_freq": float(freqs[np.argmax(magnitude)] if len(magnitude) > 0 else 0),
            "spectral_centroid": float(np.sum(freqs * magnitude) / np.sum(magnitude)) if np.sum(magnitude) > 0 else 0,
            "low_freq_energy": get_band_energy(0, 300),      # Low frequency noise
            "speech_energy": get_band_energy(300, 3400),     # Speech range
            "high_freq_energy": get_band_energy(3400, 8000), # High frequency content
            "spectral_rolloff": self._calculate_spectral_rolloff(freqs, magnitude),
            "zero_crossing_rate": float(np.sum(np.diff(np.signbit(audio_data))) / len(audio_data))
        }
    
    def _calculate_spectral_rolloff(self, freqs: np.ndarray, magnitude: np.ndarray, rolloff_percent: float = 0.85) -> float:
        """Calculate spectral rolloff frequency"""
        if np.sum(magnitude) == 0:
            return 0.0
        
        cumulative_energy = np.cumsum(magnitude)
        total_energy = cumulative_energy[-1]
        rolloff_threshold = rolloff_percent * total_energy
        
        rolloff_idx = np.where(cumulative_energy >= rolloff_threshold)[0]
        return float(freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else freqs[-1])
    
    def _detect_voice_activity(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Simple voice activity detection"""
        # Frame-based analysis
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.01 * sr)     # 10ms hop
        
        frames = librosa.util.frame(audio_data, frame_length=frame_length, hop_length=hop_length, axis=0)
        
        # Energy-based VAD
        frame_energy = np.sum(frames**2, axis=0)
        energy_threshold = np.percentile(frame_energy, 30)  # Bottom 30% as silence
        
        voice_frames = frame_energy > energy_threshold
        voice_ratio = float(np.sum(voice_frames) / len(voice_frames))
        
        return {
            "voice_activity_ratio": voice_ratio,
            "total_frames": len(voice_frames),
            "voice_frames": int(np.sum(voice_frames)),
            "energy_threshold": float(energy_threshold),
            "frame_length_ms": frame_length / sr * 1000,
            "hop_length_ms": hop_length / sr * 1000
        }
    
    def _detect_quality_issues(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Detect common audio quality issues that affect Whisper"""
        issues = {}
        
        # Clipping detection
        clipping_threshold = 0.95
        clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
        issues["clipping"] = {
            "detected": clipped_samples > 0,
            "clipped_samples": int(clipped_samples),
            "clipping_ratio": float(clipped_samples / len(audio_data))
        }
        
        # DC offset detection
        dc_offset = float(np.mean(audio_data))
        issues["dc_offset"] = {
            "detected": abs(dc_offset) > 0.1,
            "offset_value": dc_offset
        }
        
        # Low signal level detection
        rms = float(np.sqrt(np.mean(audio_data**2)))
        issues["low_signal"] = {
            "detected": rms < 0.001,
            "rms_level": rms,
            "rms_db": float(20 * np.log10(rms + 1e-8))
        }
        
        # High noise floor detection
        # Use bottom 10% of energy as noise floor estimate
        frame_energy = np.sum(librosa.util.frame(audio_data, frame_length=1024, hop_length=512, axis=0)**2, axis=0)
        noise_floor = np.percentile(frame_energy, 10)
        signal_energy = np.percentile(frame_energy, 90)
        snr_estimate = float(10 * np.log10((signal_energy + 1e-8) / (noise_floor + 1e-8)))
        
        issues["noise"] = {
            "estimated_snr_db": snr_estimate,
            "high_noise": snr_estimate < 10,  # SNR less than 10dB indicates noisy audio
            "noise_floor": float(noise_floor),
            "signal_energy": float(signal_energy)
        }
        
        return issues
    
    def _assess_whisper_readiness(self, audio_data: np.ndarray, sr: int, duration: float) -> Dict[str, Any]:
        """Assess if audio is suitable for Whisper transcription"""
        readiness = {}
        
        # Duration check
        readiness["duration_ok"] = duration >= 1.0  # Whisper needs at least 1 second
        readiness["optimal_duration"] = 15.0 <= duration <= 30.0  # Optimal range
        
        # Signal quality check
        rms = float(np.sqrt(np.mean(audio_data**2)))
        readiness["signal_level_ok"] = 0.001 <= rms <= 0.5  # Good signal level range
        
        # Voice activity check
        voice_analysis = self._detect_voice_activity(audio_data, sr)
        readiness["voice_activity_ok"] = voice_analysis["voice_activity_ratio"] > 0.1
        
        # Quality issues check
        quality_issues = self._detect_quality_issues(audio_data, sr)
        readiness["no_clipping"] = not quality_issues["clipping"]["detected"]
        readiness["good_snr"] = quality_issues["noise"]["estimated_snr_db"] > 6
        
        # Overall assessment
        checks = [
            readiness["duration_ok"],
            readiness["signal_level_ok"], 
            readiness["voice_activity_ok"],
            readiness["no_clipping"],
            readiness["good_snr"]
        ]
        
        readiness["overall_score"] = float(sum(checks) / len(checks))
        readiness["whisper_ready"] = readiness["overall_score"] >= 0.6
        
        # Recommendations
        recommendations = []
        if not readiness["duration_ok"]:
            recommendations.append("Audio too short - consider buffering longer segments")
        if not readiness["signal_level_ok"]:
            if rms < 0.001:
                recommendations.append("Signal level too low - check audio gain")
            else:
                recommendations.append("Signal level too high - risk of clipping")
        if not readiness["voice_activity_ok"]:
            recommendations.append("Low voice activity - mostly silence detected")
        if readiness["good_snr"]:
            recommendations.append("High noise level - consider noise reduction")
        if quality_issues["clipping"]["detected"]:
            recommendations.append("Audio clipping detected - check input levels")
        
        readiness["recommendations"] = recommendations
        
        return readiness

class RealTimeBatchComparator:
    """Compare real-time audio chunks with batch processed equivalents"""
    
    def __init__(self):
        self.analyzer = AudioQualityAnalyzer()
        
    def compare_audio_sets(self, real_time_dir: str, batch_file: str) -> Dict[str, Any]:
        """Compare quality metrics between real-time chunks and batch file"""
        
        comparison = {
            "batch_analysis": {},
            "realtime_analysis": [],
            "comparison_metrics": {},
            "recommendations": []
        }
        
        try:
            # Analyze batch file
            if os.path.exists(batch_file):
                comparison["batch_analysis"] = self.analyzer.analyze_audio_file(batch_file)
            
            # Analyze real-time chunks
            realtime_files = []
            if os.path.exists(real_time_dir):
                realtime_files = sorted([f for f in os.listdir(real_time_dir) if f.endswith('.wav')])
            
            for file in realtime_files[:10]:  # Analyze first 10 chunks
                file_path = os.path.join(real_time_dir, file)
                analysis = self.analyzer.analyze_audio_file(file_path)
                analysis["filename"] = file
                comparison["realtime_analysis"].append(analysis)
            
            # Generate comparison metrics
            if comparison["batch_analysis"] and comparison["realtime_analysis"]:
                comparison["comparison_metrics"] = self._generate_comparison_metrics(
                    comparison["batch_analysis"],
                    comparison["realtime_analysis"]
                )
                
                comparison["recommendations"] = self._generate_recommendations(
                    comparison["comparison_metrics"]
                )
        
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            comparison["error"] = str(e)
        
        return comparison
    
    def _generate_comparison_metrics(self, batch_analysis: Dict, realtime_analyses: List[Dict]) -> Dict:
        """Generate comparison metrics between batch and real-time"""
        
        if not realtime_analyses:
            return {"error": "No real-time analyses available"}
        
        # Average real-time metrics
        rt_metrics = {
            "avg_duration": np.mean([a.get("file_info", {}).get("duration", 0) for a in realtime_analyses]),
            "avg_rms": np.mean([a.get("amplitude_stats", {}).get("rms", 0) for a in realtime_analyses]),
            "avg_peak": np.mean([a.get("amplitude_stats", {}).get("peak", 0) for a in realtime_analyses]),
            "avg_voice_activity": np.mean([a.get("voice_activity", {}).get("voice_activity_ratio", 0) for a in realtime_analyses]),
            "avg_whisper_readiness": np.mean([a.get("whisper_readiness", {}).get("overall_score", 0) for a in realtime_analyses])
        }
        
        # Batch metrics
        batch_metrics = {
            "duration": batch_analysis.get("file_info", {}).get("duration", 0),
            "rms": batch_analysis.get("amplitude_stats", {}).get("rms", 0),
            "peak": batch_analysis.get("amplitude_stats", {}).get("peak", 0),
            "voice_activity": batch_analysis.get("voice_activity", {}).get("voice_activity_ratio", 0),
            "whisper_readiness": batch_analysis.get("whisper_readiness", {}).get("overall_score", 0)
        }
        
        # Calculate differences
        differences = {}
        for key in rt_metrics:
            if key.startswith("avg_"):
                batch_key = key[4:]  # Remove "avg_" prefix
                if batch_key in batch_metrics:
                    differences[f"{batch_key}_diff"] = rt_metrics[key] - batch_metrics[batch_key]
                    differences[f"{batch_key}_ratio"] = (rt_metrics[key] / (batch_metrics[batch_key] + 1e-8))
        
        return {
            "realtime_avg": rt_metrics,
            "batch": batch_metrics,
            "differences": differences
        }
    
    def _generate_recommendations(self, comparison_metrics: Dict) -> List[str]:
        """Generate recommendations based on comparison"""
        
        recommendations = []
        differences = comparison_metrics.get("differences", {})
        
        # Duration recommendations
        if abs(differences.get("duration_diff", 0)) > 2:
            recommendations.append("Significant duration difference between real-time chunks and batch - check buffering strategy")
        
        # Signal level recommendations  
        if differences.get("rms_ratio", 1) < 0.5:
            recommendations.append("Real-time audio has much lower signal level than batch - check audio preprocessing")
        elif differences.get("rms_ratio", 1) > 2:
            recommendations.append("Real-time audio has much higher signal level than batch - possible gain mismatch")
        
        # Voice activity recommendations
        if differences.get("voice_activity_diff", 0) < -0.3:
            recommendations.append("Real-time chunks have significantly less voice activity - may be capturing mostly silence")
        
        # Whisper readiness recommendations
        if differences.get("whisper_readiness_diff", 0) < -0.2:
            recommendations.append("Real-time audio quality significantly worse for Whisper - implement audio preprocessing")
        
        return recommendations

def analyze_debug_directory(debug_dir: str = "/tmp/debug_audio_chunks") -> Dict[str, Any]:
    """Analyze all debug audio files in directory"""
    
    analyzer = AudioQualityAnalyzer()
    results = {
        "directory": debug_dir,
        "timestamp": datetime.now().isoformat(),
        "files_analyzed": 0,
        "analyses": [],
        "summary": {}
    }
    
    if not os.path.exists(debug_dir):
        results["error"] = f"Debug directory {debug_dir} does not exist"
        return results
    
    # Get all WAV files
    wav_files = [f for f in os.listdir(debug_dir) if f.endswith('.wav')]
    wav_files.sort()  # Sort by filename (includes timestamp)
    
    analyses = []
    for wav_file in wav_files:
        file_path = os.path.join(debug_dir, wav_file)
        analysis = analyzer.analyze_audio_file(file_path)
        analysis["filename"] = wav_file
        analyses.append(analysis)
    
    results["files_analyzed"] = len(analyses)
    results["analyses"] = analyses
    
    # Generate summary statistics
    if analyses:
        results["summary"] = _generate_summary_stats(analyses)
    
    return results

def _generate_summary_stats(analyses: List[Dict]) -> Dict[str, Any]:
    """Generate summary statistics from multiple audio analyses"""
    
    valid_analyses = [a for a in analyses if "error" not in a]
    
    if not valid_analyses:
        return {"error": "No valid analyses"}
    
    # Extract metrics for summary
    durations = [a.get("file_info", {}).get("duration", 0) for a in valid_analyses]
    rms_values = [a.get("amplitude_stats", {}).get("rms", 0) for a in valid_analyses]
    voice_activities = [a.get("voice_activity", {}).get("voice_activity_ratio", 0) for a in valid_analyses]
    whisper_scores = [a.get("whisper_readiness", {}).get("overall_score", 0) for a in valid_analyses]
    
    return {
        "total_files": len(valid_analyses),
        "duration_stats": {
            "mean": float(np.mean(durations)),
            "std": float(np.std(durations)),
            "min": float(np.min(durations)),
            "max": float(np.max(durations))
        },
        "rms_stats": {
            "mean": float(np.mean(rms_values)),
            "std": float(np.std(rms_values)),
            "min": float(np.min(rms_values)),
            "max": float(np.max(rms_values))
        },
        "voice_activity_stats": {
            "mean": float(np.mean(voice_activities)),
            "std": float(np.std(voice_activities)),
            "min": float(np.min(voice_activities)),
            "max": float(np.max(voice_activities))
        },
        "whisper_readiness_stats": {
            "mean": float(np.mean(whisper_scores)),
            "std": float(np.std(whisper_scores)),
            "ready_count": int(np.sum([s > 0.6 for s in whisper_scores])),
            "ready_percentage": float(np.mean([s > 0.6 for s in whisper_scores]) * 100)
        }
    }

# Command line interface for debugging
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio Quality Debug Tool")
    parser.add_argument("--debug-dir", default="/tmp/debug_audio_chunks", help="Debug audio directory")
    parser.add_argument("--batch-file", help="Batch audio file for comparison")
    parser.add_argument("--output", help="Output JSON file for results")
    
    args = parser.parse_args()
    
    if args.batch_file:
        # Compare real-time vs batch
        comparator = RealTimeBatchComparator()
        results = comparator.compare_audio_sets(args.debug_dir, args.batch_file)
    else:
        # Analyze debug directory only
        results = analyze_debug_directory(args.debug_dir)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))