"""
AI Service Load Testing Framework
==================================

Comprehensive load testing for all AI service endpoints with configurable
parameters for duration, users, and spawn rate.

Usage:
    # Quick test (5 minutes, 10 users)
    locust -f load_test.py --host=http://localhost:8125

    # Production load test (30 minutes, 50 users)
    locust -f load_test.py --host=http://localhost:8125 \\
        --users=50 --spawn-rate=5 --run-time=30m --headless

    # Extended stress test (1 hour, 100 users)
    locust -f load_test.py --host=http://localhost:8125 \\
        --users=100 --spawn-rate=10 --run-time=1h --headless
"""

import os
import random
import time
from pathlib import Path
from locust import HttpUser, task, between, events


class AIServiceUser(HttpUser):
    """
    Simulates a user interacting with the AI Service pipeline.
    Tests all major endpoints with realistic workloads.
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Initialize test data on user startup"""
        self.audio_files = self._discover_audio_files()
        self.test_texts = [
            "The child reported feeling unsafe at home.",
            "Family requires immediate intervention and support services.",
            "Case worker conducted home visit and assessment.",
            "Parent expressed willingness to participate in counseling.",
        ]

    def _discover_audio_files(self):
        """Discover available test audio files"""
        audio_dir = Path("test_audio")

        if not audio_dir.exists():
            print(f"Warning: {audio_dir} not found. Audio tests will be skipped.")
            return []

        audio_files = list(audio_dir.glob("*.wav"))
        if not audio_files:
            print(f"Warning: No .wav files found in {audio_dir}")
            return []

        print(f"Found {len(audio_files)} audio files for testing")
        return [str(f) for f in audio_files]

    # ========================================================================
    # HEALTH CHECK ENDPOINTS (Weight: 10%)
    # ========================================================================

    @task(5)
    def health_check(self):
        """Basic health check"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="GET /health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def detailed_health_check(self):
        """Detailed health check with model status"""
        with self.client.get(
            "/health/detailed",
            catch_response=True,
            name="GET /health/detailed"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Detailed health failed: {response.status_code}")

    # ========================================================================
    # AUDIO PROCESSING ENDPOINTS (Weight: 20%)
    # ========================================================================

    @task(10)
    def audio_analyze(self):
        """Full audio analysis pipeline"""
        if not self.audio_files:
            return  # Skip if no audio files available

        audio_file = random.choice(self.audio_files)

        try:
            with open(audio_file, 'rb') as f:
                files = {'file': (os.path.basename(audio_file), f, 'audio/wav')}

                with self.client.post(
                    "/audio/analyze",
                    files=files,
                    catch_response=True,
                    name="POST /audio/analyze",
                    timeout=120  # 2 minutes for large audio files
                ) as response:
                    if response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Audio analyze failed: {response.status_code}")
        except Exception as e:
            print(f"Error in audio_analyze: {e}")

    @task(10)
    def whisper_transcribe(self):
        """Whisper transcription endpoint"""
        if not self.audio_files:
            return

        audio_file = random.choice(self.audio_files)

        try:
            with open(audio_file, 'rb') as f:
                files = {'file': (os.path.basename(audio_file), f, 'audio/wav')}

                with self.client.post(
                    "/whisper/transcribe",
                    files=files,
                    catch_response=True,
                    name="POST /whisper/transcribe",
                    timeout=120
                ) as response:
                    if response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"Whisper failed: {response.status_code}")
        except Exception as e:
            print(f"Error in whisper_transcribe: {e}")

    # ========================================================================
    # TEXT PROCESSING ENDPOINTS (Weight: 60%)
    # ========================================================================

    @task(15)
    def classifier_classify(self):
        """Text classification endpoint"""
        text = random.choice(self.test_texts)

        with self.client.post(
            "/classifier/classify",
            json={"text": text, "threshold": 0.5},
            catch_response=True,
            name="POST /classifier/classify",
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 422:
                response.failure(f"Classifier failed: 422")
            else:
                response.failure(f"Classifier failed: {response.status_code}")

    @task(15)
    def ner_extract(self):
        """Named entity recognition endpoint"""
        text = random.choice(self.test_texts)

        with self.client.post(
            "/ner/extract",
            json={"text": text},
            catch_response=True,
            name="POST /ner/extract",
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"NER failed: {response.status_code}")

    @task(12)
    def qa_evaluate(self):
        """QA evaluation endpoint"""
        text = random.choice(self.test_texts)

        with self.client.post(
            "/qa/evaluate",
            json={"transcript": text, "threshold": 0.5},
            catch_response=True,
            name="POST /qa/evaluate",
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"QA failed: {response.status_code}")

    @task(10)
    def translate_text(self):
        """Translation endpoint (Swahili to English)"""
        text = "Mtoto anasema anajisikia si salama nyumbani."

        with self.client.post(
            "/translate/",
            json={
                "text": text,
                "source_lang": "sw",
                "target_lang": "en"
            },
            catch_response=True,
            name="POST /translate/ (sw->en)",
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Translation failed: {response.status_code}")

    @task(10)
    def summarize_text(self):
        """Text summarization endpoint"""
        text = " ".join(self.test_texts)

        with self.client.post(
            "/summarize/",
            json={
                "text": text,
                "max_length": 150,
                "min_length": 50
            },
            catch_response=True,
            name="POST /summarize/",
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.failure(f"Summarization failed: 404")
            else:
                response.failure(f"Summarization failed: {response.status_code}")

    # ========================================================================
    # INFO ENDPOINTS (Weight: 10%)
    # ========================================================================

    @task(3)
    def get_classifier_info(self):
        """Get classifier model info"""
        with self.client.get(
            "/classifier/info",
            catch_response=True,
            name="GET /classifier/info"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Classifier info failed: {response.status_code}")

    @task(3)
    def get_ner_info(self):
        """Get NER model info"""
        with self.client.get(
            "/ner/info",
            catch_response=True,
            name="GET /ner/info"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"NER info failed: {response.status_code}")

    @task(2)
    def get_whisper_languages(self):
        """Get supported Whisper languages"""
        with self.client.get(
            "/whisper/languages",
            catch_response=True,
            name="GET /whisper/languages"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Whisper languages failed: {response.status_code}")

    @task(2)
    def get_translation_languages(self):
        """Get supported translation languages"""
        with self.client.get(
            "/translate/languages",
            catch_response=True,
            name="GET /translate/languages"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.failure(f"Languages endpoint failed: 404")
            else:
                response.failure(f"Languages endpoint failed: {response.status_code}")


# ========================================================================
# EVENT HANDLERS
# ========================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test configuration when test starts"""
    print("\n" + "="*80)
    print("AI SERVICE LOAD TEST STARTING")
    print("="*80)
    print(f"Host: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print(f"Duration: {environment.runner.run_time if hasattr(environment.runner, 'run_time') else 'Unlimited'}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test summary when test completes"""
    print("\n" + "="*80)
    print("AI SERVICE LOAD TEST COMPLETED")
    print("="*80)

    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Error rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    print(f"Avg response time: {stats.total.avg_response_time:.0f}ms")
    print(f"P50 response time: {stats.total.get_response_time_percentile(0.5):.0f}ms")
    print(f"P95 response time: {stats.total.get_response_time_percentile(0.95):.0f}ms")
    print(f"P99 response time: {stats.total.get_response_time_percentile(0.99):.0f}ms")
    print("="*80 + "\n")
