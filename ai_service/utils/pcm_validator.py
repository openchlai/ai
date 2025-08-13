# utils/pcm_validator.py - PCM Audio Format Validation for debugging Whisper issues

import numpy as np
import logging
import soundfile as sf
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)

class PCMAudioValidator:
    """Validate PCM audio format conversion accuracy"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        
    def validate_pcm_conversion(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Validate PCM bytes conversion matches expected format"""
        
        validation_result = {
            "input_info": {
                "bytes_length": len(audio_bytes),
                "expected_samples": len(audio_bytes) // 2,  # 16-bit = 2 bytes per sample
                "expected_duration": (len(audio_bytes) // 2) / self.sample_rate
            },
            "conversion_test": {},
            "format_validation": {},
            "whisper_compatibility": {},
            "issues_detected": [],
            "recommendations": []
        }
        
        try:
            # Test the actual conversion used in the pipeline
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # Validate conversion results
            validation_result["conversion_test"] = {
                "int16_samples": len(audio_int16),
                "float32_samples": len(audio_float32),
                "samples_match": len(audio_int16) == len(audio_float32),
                "int16_range": (int(np.min(audio_int16)), int(np.max(audio_int16))),
                "float32_range": (float(np.min(audio_float32)), float(np.max(audio_float32))),
                "conversion_factor": 32768.0,
                "duration_seconds": len(audio_float32) / self.sample_rate
            }
            
            # Format validation
            validation_result["format_validation"] = self._validate_audio_format(audio_float32)
            
            # Whisper compatibility check
            validation_result["whisper_compatibility"] = self._check_whisper_compatibility(
                audio_float32, validation_result["conversion_test"]["duration_seconds"]
            )
            
            # Detect common issues
            issues = self._detect_conversion_issues(audio_bytes, audio_int16, audio_float32)
            validation_result["issues_detected"] = issues
            
            # Generate recommendations
            validation_result["recommendations"] = self._generate_recommendations(validation_result)
            
        except Exception as e:
            validation_result["error"] = str(e)
            logger.error(f"PCM validation failed: {e}")
        
        return validation_result
    
    def _validate_audio_format(self, audio_array: np.ndarray) -> Dict[str, Any]:
        """Validate audio format characteristics"""
        return {
            "dtype": str(audio_array.dtype),
            "shape": audio_array.shape,
            "is_mono": len(audio_array.shape) == 1,
            "sample_count": len(audio_array),
            "amplitude_range": {
                "min": float(np.min(audio_array)),
                "max": float(np.max(audio_array)),
                "peak": float(np.max(np.abs(audio_array))),
                "rms": float(np.sqrt(np.mean(audio_array**2)))
            },
            "is_normalized": np.max(np.abs(audio_array)) <= 1.0,
            "has_clipping": np.any(np.abs(audio_array) > 0.99),
            "dc_offset": float(np.mean(audio_array)),
            "zero_crossings": int(np.sum(np.diff(np.signbit(audio_array))))
        }
    
    def _check_whisper_compatibility(self, audio_array: np.ndarray, duration: float) -> Dict[str, Any]:
        """Check if audio format is compatible with Whisper requirements"""
        
        compatibility = {
            "sample_rate_ok": self.sample_rate == 16000,  # Whisper expects 16kHz
            "dtype_ok": audio_array.dtype == np.float32,  # Whisper expects float32
            "amplitude_ok": np.max(np.abs(audio_array)) <= 1.0,  # Normalized range
            "duration_ok": duration >= 0.1,  # Minimum duration for processing
            "mono_ok": len(audio_array.shape) == 1,  # Mono audio
            "finite_values": np.all(np.isfinite(audio_array)),  # No NaN or inf values
        }
        
        # Overall compatibility score
        compatibility["overall_compatible"] = all(compatibility.values())
        compatibility["compatibility_score"] = sum(compatibility.values()) / len(compatibility)
        
        return compatibility
    
    def _detect_conversion_issues(self, audio_bytes: bytes, audio_int16: np.ndarray, audio_float32: np.ndarray) -> list:
        """Detect common PCM conversion issues"""
        issues = []
        
        # Check byte length alignment
        if len(audio_bytes) % 2 != 0:
            issues.append({
                "type": "alignment_error",
                "severity": "high",
                "description": "Audio bytes length not aligned to 16-bit samples",
                "details": f"Byte length: {len(audio_bytes)} (should be even)"
            })
        
        # Check for endianness issues
        expected_samples = len(audio_bytes) // 2
        actual_samples = len(audio_int16)
        if expected_samples != actual_samples:
            issues.append({
                "type": "sample_count_mismatch",
                "severity": "high",
                "description": "Sample count doesn't match expected value",
                "details": f"Expected: {expected_samples}, Got: {actual_samples}"
            })
        
        # Check for overflow/underflow in conversion
        int16_max = np.max(np.abs(audio_int16))
        float32_max = np.max(np.abs(audio_float32))
        expected_float_max = int16_max / 32768.0
        
        if abs(float32_max - expected_float_max) > 1e-6:
            issues.append({
                "type": "conversion_precision_error",
                "severity": "medium",
                "description": "Conversion precision doesn't match expected value",
                "details": f"Expected max: {expected_float_max:.6f}, Got: {float32_max:.6f}"
            })
        
        # Check for unusual amplitude distributions
        if float32_max < 0.001:
            issues.append({
                "type": "very_low_amplitude",
                "severity": "high",
                "description": "Audio amplitude extremely low",
                "details": f"Peak amplitude: {float32_max:.6f} (may be all silence)"
            })
        
        # Check for constant values (potential silence or DC)
        if np.std(audio_float32) < 1e-6:
            issues.append({
                "type": "constant_audio",
                "severity": "high", 
                "description": "Audio appears to be constant (silence or DC offset)",
                "details": f"Standard deviation: {np.std(audio_float32):.8f}"
            })
        
        # Check for potential byte order issues
        # Try alternative byte order and see if it looks more reasonable
        try:
            alt_int16 = np.frombuffer(audio_bytes, dtype='>i2')  # Big-endian
            alt_float32 = alt_int16.astype(np.float32) / 32768.0
            
            # If alternative byte order gives more reasonable amplitude range
            if (np.std(alt_float32) > np.std(audio_float32) * 2 and 
                0.01 < np.max(np.abs(alt_float32)) < 0.8):
                issues.append({
                    "type": "potential_endianness_issue", 
                    "severity": "medium",
                    "description": "Alternative byte order may be more appropriate",
                    "details": f"Current std: {np.std(audio_float32):.6f}, Alt std: {np.std(alt_float32):.6f}"
                })
        except:
            pass  # Ignore errors in alternative conversion test
        
        return issues
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> list:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        issues = validation_result.get("issues_detected", [])
        compatibility = validation_result.get("whisper_compatibility", {})
        format_info = validation_result.get("format_validation", {})
        
        # High priority issues
        high_severity_issues = [i for i in issues if i.get("severity") == "high"]
        if high_severity_issues:
            recommendations.append({
                "priority": "high",
                "action": "Fix critical PCM conversion issues",
                "details": [issue["description"] for issue in high_severity_issues]
            })
        
        # Whisper compatibility issues
        if not compatibility.get("overall_compatible", False):
            incompatible_items = [k for k, v in compatibility.items() 
                                if isinstance(v, bool) and not v and k != "overall_compatible"]
            if incompatible_items:
                recommendations.append({
                    "priority": "high",
                    "action": "Fix Whisper compatibility issues",
                    "details": incompatible_items
                })
        
        # Audio quality recommendations
        amplitude_info = format_info.get("amplitude_range", {})
        peak = amplitude_info.get("peak", 0)
        rms = amplitude_info.get("rms", 0)
        
        if peak < 0.01:
            recommendations.append({
                "priority": "medium",
                "action": "Increase audio gain - signal too weak",
                "details": f"Peak amplitude: {peak:.4f} (target: 0.1-0.8)"
            })
        elif peak > 0.95:
            recommendations.append({
                "priority": "medium", 
                "action": "Reduce audio gain - risk of clipping",
                "details": f"Peak amplitude: {peak:.4f} (target: 0.1-0.8)"
            })
        
        if rms > 0 and peak / rms > 20:  # Very high peak-to-RMS ratio
            recommendations.append({
                "priority": "low",
                "action": "Check for impulse noise or sparse audio content",
                "details": f"Peak/RMS ratio: {peak/rms:.1f} (high dynamic range)"
            })
        
        # DC offset check
        dc_offset = format_info.get("dc_offset", 0)
        if abs(dc_offset) > 0.01:
            recommendations.append({
                "priority": "low",
                "action": "Remove DC offset from audio",
                "details": f"DC offset: {dc_offset:.4f}"
            })
        
        return recommendations
    
    def compare_with_reference(self, audio_bytes: bytes, reference_file: str) -> Dict[str, Any]:
        """Compare PCM conversion with a reference audio file"""
        comparison = {
            "pcm_analysis": {},
            "reference_analysis": {},
            "comparison_metrics": {},
            "similarity_score": 0.0
        }
        
        try:
            # Analyze PCM conversion
            comparison["pcm_analysis"] = self.validate_pcm_conversion(audio_bytes)
            
            # Load and analyze reference file
            if os.path.exists(reference_file):
                ref_audio, ref_sr = sf.read(reference_file)
                
                # Ensure mono
                if len(ref_audio.shape) > 1:
                    ref_audio = np.mean(ref_audio, axis=1)
                
                # Resample if needed (basic resampling)
                if ref_sr != self.sample_rate:
                    # Simple resampling for testing (not production quality)
                    ratio = self.sample_rate / ref_sr
                    new_length = int(len(ref_audio) * ratio)
                    ref_audio = np.interp(
                        np.linspace(0, len(ref_audio), new_length),
                        np.arange(len(ref_audio)),
                        ref_audio
                    )
                
                comparison["reference_analysis"] = self._validate_audio_format(ref_audio)
                
                # Compare the two
                pcm_audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                comparison["comparison_metrics"] = self._compare_audio_arrays(pcm_audio, ref_audio)
                
            else:
                comparison["error"] = f"Reference file not found: {reference_file}"
                
        except Exception as e:
            comparison["error"] = str(e)
            logger.error(f"Reference comparison failed: {e}")
        
        return comparison
    
    def _compare_audio_arrays(self, audio1: np.ndarray, audio2: np.ndarray) -> Dict[str, Any]:
        """Compare two audio arrays for similarity"""
        
        # Ensure same length for comparison (truncate to shorter)
        min_len = min(len(audio1), len(audio2))
        a1 = audio1[:min_len]
        a2 = audio2[:min_len]
        
        # Basic comparison metrics
        mse = float(np.mean((a1 - a2) ** 2))
        correlation = float(np.corrcoef(a1, a2)[0, 1]) if min_len > 1 else 0.0
        
        # Amplitude comparison
        rms1 = np.sqrt(np.mean(a1**2))
        rms2 = np.sqrt(np.mean(a2**2)) 
        rms_ratio = rms1 / (rms2 + 1e-8)
        
        # Spectral comparison (basic)
        fft1 = np.fft.fft(a1)
        fft2 = np.fft.fft(a2)
        spectral_distance = float(np.mean(np.abs(fft1 - fft2)))
        
        return {
            "length_comparison": {
                "audio1_samples": len(audio1),
                "audio2_samples": len(audio2),
                "compared_samples": min_len,
                "length_match": len(audio1) == len(audio2)
            },
            "similarity_metrics": {
                "mse": mse,
                "correlation": correlation,
                "rms_ratio": rms_ratio,
                "spectral_distance": spectral_distance
            },
            "amplitude_comparison": {
                "rms1": float(rms1),
                "rms2": float(rms2),
                "peak1": float(np.max(np.abs(a1))),
                "peak2": float(np.max(np.abs(a2)))
            },
            "quality_assessment": {
                "high_correlation": correlation > 0.8,
                "low_mse": mse < 0.01,
                "similar_amplitude": 0.5 < rms_ratio < 2.0,
                "overall_similar": correlation > 0.8 and mse < 0.01
            }
        }
    
    def save_debug_audio(self, audio_bytes: bytes, output_dir: str = "/tmp/pcm_debug") -> str:
        """Save PCM audio as WAV file for manual inspection"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PCM bytes to audio array
        audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        
        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"pcm_debug_{timestamp}.wav"
        filepath = os.path.join(output_dir, filename)
        
        # Save as WAV
        sf.write(filepath, audio_float32, self.sample_rate)
        
        logger.info(f"PCM debug audio saved: {filepath}")
        return filepath

def validate_streaming_pcm_conversion(audio_bytes: bytes, call_id: str = "test") -> Dict[str, Any]:
    """Convenience function to validate PCM conversion used in streaming pipeline"""
    
    validator = PCMAudioValidator()
    result = validator.validate_pcm_conversion(audio_bytes)
    
    # Add call context
    result["call_context"] = {
        "call_id": call_id,
        "pipeline": "streaming_audio_task",
        "conversion_method": "numpy_frombuffer_int16_to_float32"
    }
    
    # Save debug file if issues detected
    if result.get("issues_detected"):
        debug_file = validator.save_debug_audio(audio_bytes)
        result["debug_file"] = debug_file
    
    return result

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Validate PCM audio format")
    parser.add_argument("--test-file", help="Test PCM file (raw bytes)")
    parser.add_argument("--reference", help="Reference WAV file for comparison")
    parser.add_argument("--output", help="Output JSON file for results")
    
    args = parser.parse_args()
    
    if args.test_file:
        # Read PCM bytes from file
        with open(args.test_file, 'rb') as f:
            pcm_bytes = f.read()
        
        validator = PCMAudioValidator()
        
        if args.reference:
            # Compare with reference
            results = validator.compare_with_reference(pcm_bytes, args.reference)
        else:
            # Just validate format
            results = validator.validate_pcm_conversion(pcm_bytes)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2))
    else:
        # Create test data
        print("Creating test PCM data...")
        
        # Generate test audio (sine wave)
        sample_rate = 16000
        duration = 5.0
        samples = int(duration * sample_rate)
        t = np.linspace(0, duration, samples, False)
        test_audio = (np.sin(2 * np.pi * 440 * t) * 0.3).astype(np.float32)
        
        # Convert to PCM bytes (as done in pipeline)
        test_pcm_bytes = (test_audio * 32768.0).astype(np.int16).tobytes()
        
        # Validate
        validator = PCMAudioValidator()
        results = validator.validate_pcm_conversion(test_pcm_bytes)
        
        print("Test Results:")
        print(json.dumps(results, indent=2))