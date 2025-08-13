#!/usr/bin/env python3
# scripts/test_whisper_fixes.py - Test script for Whisper hallucination debugging

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WhisperFixTester:
    """Test suite for validating Whisper hallucination fixes"""
    
    def __init__(self):
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "tests_run": [],
            "summary": {}
        }
    
    def test_audio_buffer_configurations(self):
        """Test different audio buffer configurations"""
        logger.info("🧪 Testing audio buffer configurations...")
        
        from app.streaming.audio_buffer import AsteriskAudioBuffer
        import numpy as np
        
        # Test configurations
        configs = [
            {"duration": 5.0, "overlapping": False, "name": "Original 5s"},
            {"duration": 15.0, "overlapping": False, "name": "Fixed 15s"},
            {"duration": 15.0, "overlapping": True, "name": "Enhanced 15s + overlap"},
            {"duration": 30.0, "overlapping": True, "name": "Optimal 30s + overlap"}
        ]
        
        test_results = []
        
        for config in configs:
            logger.info(f"Testing: {config['name']}")
            
            buffer = AsteriskAudioBuffer(
                window_duration_seconds=config['duration'],
                enable_overlapping=config['overlapping']
            )
            
            # Simulate audio chunks (320 bytes = 10ms at 16kHz)
            chunk_size = 320
            chunks_needed = int((config['duration'] * 16000 * 2) / chunk_size)
            
            windows_generated = 0
            total_chunks = chunks_needed + 50  # Add extra chunks to test windowing
            
            for i in range(total_chunks):
                # Create dummy audio chunk (silence for testing)
                dummy_chunk = b'\x00' * chunk_size
                result = buffer.add_chunk(dummy_chunk)
                
                if result is not None:
                    windows_generated += 1
                    if windows_generated == 1:  # Log first window
                        logger.info(f"  First window: {len(result)} samples, "
                                   f"{len(result)/16000:.1f}s duration")
            
            stats = buffer.get_stats()
            
            test_result = {
                "config": config,
                "windows_generated": windows_generated,
                "buffer_stats": stats,
                "chunks_processed": total_chunks
            }
            test_results.append(test_result)
            
            logger.info(f"  Result: {windows_generated} windows from {total_chunks} chunks")
        
        self.results["tests_run"].append({
            "test_name": "audio_buffer_configurations",
            "results": test_results
        })
        
        return test_results
    
    def test_whisper_parameters(self):
        """Test Whisper model parameters for different audio lengths"""
        logger.info("🧪 Testing Whisper model parameters...")
        
        try:
            from app.model_scripts.whisper_model import WhisperModel
            import numpy as np
            
            # Create test audio arrays of different durations
            sample_rate = 16000
            test_durations = [5.0, 10.0, 15.0, 20.0, 30.0]
            
            test_results = []
            
            # Initialize Whisper model (if available)
            whisper = WhisperModel()
            
            # Check if model is available
            if not whisper._check_local_model_exists():
                logger.warning("Whisper model not available locally, skipping model tests")
                test_results.append({
                    "status": "skipped",
                    "reason": "Whisper model not available"
                })
            else:
                logger.info("Loading Whisper model for testing...")
                if not whisper.load():
                    logger.error("Failed to load Whisper model")
                    test_results.append({
                        "status": "failed",
                        "reason": "Failed to load Whisper model"
                    })
                else:
                    for duration in test_durations:
                        logger.info(f"Testing {duration}s audio duration...")
                        
                        # Create test audio (sine wave for actual audio content)
                        samples = int(duration * sample_rate)
                        t = np.linspace(0, duration, samples, False)
                        # Mix of frequencies to simulate speech-like content
                        frequency = 440  # A4 note
                        test_audio = (np.sin(2 * np.pi * frequency * t) * 0.1).astype(np.float32)
                        
                        try:
                            # Test transcription with different chunking settings
                            start_time = datetime.now()
                            
                            # Convert to PCM bytes for testing
                            pcm_bytes = (test_audio * 32768.0).astype(np.int16).tobytes()
                            
                            transcript = whisper.transcribe_pcm_audio(
                                pcm_bytes,
                                sample_rate=sample_rate,
                                language="sw",
                                enable_chunking=True
                            )
                            
                            processing_time = (datetime.now() - start_time).total_seconds()
                            
                            test_result = {
                                "duration": duration,
                                "processing_time": processing_time,
                                "transcript_length": len(transcript),
                                "transcript_sample": transcript[:100],  # First 100 chars
                                "status": "success"
                            }
                            
                            logger.info(f"  {duration}s: {processing_time:.2f}s processing, "
                                       f"{len(transcript)} chars output")
                            
                        except Exception as e:
                            test_result = {
                                "duration": duration,
                                "status": "error",
                                "error": str(e)
                            }
                            logger.error(f"  {duration}s: Failed - {e}")
                        
                        test_results.append(test_result)
            
            self.results["tests_run"].append({
                "test_name": "whisper_parameters",
                "results": test_results
            })
            
            return test_results
            
        except ImportError as e:
            logger.error(f"Failed to import Whisper components: {e}")
            return [{"status": "import_error", "error": str(e)}]
    
    def test_audio_quality_analysis(self):
        """Test the audio quality analysis utility"""
        logger.info("🧪 Testing audio quality analysis utility...")
        
        try:
            from utils.audio_debug import AudioQualityAnalyzer, analyze_debug_directory
            import numpy as np
            import soundfile as sf
            import tempfile
            
            analyzer = AudioQualityAnalyzer()
            
            # Create test audio files with different characteristics
            test_files = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                sample_rate = 16000
                
                # Test 1: Good quality audio
                duration = 5.0
                samples = int(duration * sample_rate)
                t = np.linspace(0, duration, samples, False)
                good_audio = np.sin(2 * np.pi * 440 * t) * 0.3  # Clean sine wave
                good_file = os.path.join(temp_dir, "good_audio.wav")
                sf.write(good_file, good_audio, sample_rate)
                test_files.append(("good_audio", good_file))
                
                # Test 2: Noisy audio
                noisy_audio = good_audio + np.random.normal(0, 0.05, samples)  # Add noise
                noisy_file = os.path.join(temp_dir, "noisy_audio.wav")
                sf.write(noisy_file, noisy_audio, sample_rate)
                test_files.append(("noisy_audio", noisy_file))
                
                # Test 3: Very quiet audio
                quiet_audio = good_audio * 0.001  # Very low volume
                quiet_file = os.path.join(temp_dir, "quiet_audio.wav")
                sf.write(quiet_file, quiet_audio, sample_rate)
                test_files.append(("quiet_audio", quiet_file))
                
                # Test 4: Mostly silence
                silence_audio = np.zeros(samples)
                silence_audio[samples//2:samples//2+1000] = good_audio[samples//2:samples//2+1000] * 0.1
                silence_file = os.path.join(temp_dir, "mostly_silence.wav")
                sf.write(silence_file, silence_audio, sample_rate)
                test_files.append(("mostly_silence", silence_file))
                
                # Analyze each test file
                test_results = []
                
                for test_name, file_path in test_files:
                    logger.info(f"Analyzing {test_name}...")
                    
                    try:
                        analysis = analyzer.analyze_audio_file(file_path)
                        
                        # Extract key metrics
                        whisper_ready = analysis.get("whisper_readiness", {}).get("whisper_ready", False)
                        overall_score = analysis.get("whisper_readiness", {}).get("overall_score", 0)
                        voice_activity = analysis.get("voice_activity", {}).get("voice_activity_ratio", 0)
                        
                        test_result = {
                            "test_name": test_name,
                            "whisper_ready": whisper_ready,
                            "overall_score": overall_score,
                            "voice_activity_ratio": voice_activity,
                            "status": "success",
                            "full_analysis": analysis
                        }
                        
                        logger.info(f"  {test_name}: Ready={whisper_ready}, Score={overall_score:.2f}, "
                                   f"Voice={voice_activity:.2f}")
                        
                    except Exception as e:
                        test_result = {
                            "test_name": test_name,
                            "status": "error",
                            "error": str(e)
                        }
                        logger.error(f"  {test_name}: Failed - {e}")
                    
                    test_results.append(test_result)
            
            self.results["tests_run"].append({
                "test_name": "audio_quality_analysis",
                "results": test_results
            })
            
            return test_results
            
        except ImportError as e:
            logger.error(f"Failed to import audio analysis components: {e}")
            return [{"status": "import_error", "error": str(e)}]
    
    def test_tcp_server_configuration(self):
        """Test TCP server with different configurations"""
        logger.info("🧪 Testing TCP server configurations...")
        
        try:
            from app.streaming.tcp_server import AsteriskTCPServer
            
            # Test different configurations
            configs = [
                {"window_duration": 5.0, "overlapping": False, "name": "Original"},
                {"window_duration": 15.0, "overlapping": True, "name": "Enhanced"},
                {"window_duration": 30.0, "overlapping": True, "name": "Optimal"}
            ]
            
            test_results = []
            
            for config in configs:
                logger.info(f"Testing TCP server: {config['name']}")
                
                try:
                    server = AsteriskTCPServer(
                        window_duration=config['window_duration'],
                        enable_overlapping=config['overlapping']
                    )
                    
                    # Test server status
                    status = server.get_status()
                    
                    test_result = {
                        "config": config,
                        "status": "success",
                        "server_status": status
                    }
                    
                    logger.info(f"  {config['name']}: Server initialized successfully")
                    
                except Exception as e:
                    test_result = {
                        "config": config,
                        "status": "error",
                        "error": str(e)
                    }
                    logger.error(f"  {config['name']}: Failed - {e}")
                
                test_results.append(test_result)
            
            self.results["tests_run"].append({
                "test_name": "tcp_server_configuration",
                "results": test_results
            })
            
            return test_results
            
        except ImportError as e:
            logger.error(f"Failed to import TCP server components: {e}")
            return [{"status": "import_error", "error": str(e)}]
    
    def generate_summary(self):
        """Generate test summary and recommendations"""
        logger.info("📊 Generating test summary...")
        
        total_tests = len(self.results["tests_run"])
        successful_tests = 0
        failed_tests = 0
        
        recommendations = []
        
        for test in self.results["tests_run"]:
            test_name = test["test_name"]
            test_results = test["results"]
            
            # Count successful vs failed sub-tests
            sub_successes = sum(1 for r in test_results if r.get("status") == "success")
            sub_failures = sum(1 for r in test_results if r.get("status", "success") != "success")
            
            if sub_successes > sub_failures:
                successful_tests += 1
                logger.info(f"✅ {test_name}: {sub_successes}/{len(test_results)} sub-tests passed")
            else:
                failed_tests += 1
                logger.warning(f"❌ {test_name}: {sub_failures}/{len(test_results)} sub-tests failed")
        
        # Generate recommendations based on test results
        if any("audio_buffer_configurations" in t["test_name"] for t in self.results["tests_run"]):
            recommendations.append("Use 15-30 second windows with overlap for better Whisper performance")
        
        if any("whisper_parameters" in t["test_name"] for t in self.results["tests_run"]):
            recommendations.append("Enable chunking for audio segments longer than 10 seconds")
        
        if any("audio_quality_analysis" in t["test_name"] for t in self.results["tests_run"]):
            recommendations.append("Implement audio quality checks before sending to Whisper")
        
        summary = {
            "total_test_suites": total_tests,
            "successful_test_suites": successful_tests,
            "failed_test_suites": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "recommendations": recommendations
        }
        
        self.results["summary"] = summary
        
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Total test suites: {total_tests}")
        logger.info(f"   Successful: {successful_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success rate: {summary['success_rate']*100:.1f}%")
        
        if recommendations:
            logger.info("💡 Recommendations:")
            for rec in recommendations:
                logger.info(f"   - {rec}")
        
        return summary
    
    def run_all_tests(self):
        """Run all test suites"""
        logger.info("🚀 Starting Whisper hallucination debugging tests...")
        
        # Run test suites
        self.test_audio_buffer_configurations()
        self.test_whisper_parameters()
        self.test_audio_quality_analysis()
        self.test_tcp_server_configuration()
        
        # Generate summary
        summary = self.generate_summary()
        
        return self.results
    
    def save_results(self, output_file: str = None):
        """Save test results to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"whisper_debug_test_results_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {output_file}")
        return output_file

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Whisper hallucination fixes")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests
    tester = WhisperFixTester()
    results = tester.run_all_tests()
    
    # Save results
    output_file = tester.save_results(args.output)
    
    # Print final status
    summary = results["summary"]
    success_rate = summary["success_rate"]
    
    if success_rate >= 0.8:
        logger.info("🎉 Most tests passed! Fixes appear to be working.")
    elif success_rate >= 0.5:
        logger.warning("⚠️ Some tests failed. Review results for improvements.")
    else:
        logger.error("❌ Many tests failed. Significant issues remain.")
    
    print(f"\nResults saved to: {output_file}")
    print(f"Success rate: {success_rate*100:.1f}%")

if __name__ == "__main__":
    main()