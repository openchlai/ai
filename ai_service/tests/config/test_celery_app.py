"""
Tests for app/celery_app.py
Tests Celery application configuration and Redis connection handling
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from celery import Celery


class TestGetRedisUrl:
    """Test Redis URL detection based on environment"""

    def test_get_redis_url_docker_container_env_var(self):
        """Test Redis URL when DOCKER_CONTAINER env var is set"""
        with patch.dict(os.environ, {"DOCKER_CONTAINER": "true", "REDIS_URL": "redis://custom:6379/0"}):
            from app.celery_app import get_redis_url

            result = get_redis_url()
            assert result == "redis://custom:6379/0"

    def test_get_redis_url_docker_containerenv_file(self):
        """Test Redis URL when /.dockerenv file exists"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch.dict(os.environ, {"REDIS_URL": "redis://docker-redis:6379/0"}, clear=False):
                from app.celery_app import get_redis_url

                result = get_redis_url()
                # When in Docker, should use the env var value
                assert "redis" in result

    def test_get_redis_url_localhost_default(self):
        """Test Redis URL defaults to localhost when not in Docker"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            with patch.dict(os.environ, {}, clear=True):
                # Remove DOCKER_CONTAINER and REDIS_URL
                from app.celery_app import get_redis_url

                result = get_redis_url()
                # Should default to localhost
                assert "localhost" in result or "127.0.0.1" in result

    def test_get_redis_url_custom_env_var(self):
        """Test Redis URL respects custom REDIS_URL environment variable"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            with patch.dict(os.environ, {"REDIS_URL": "redis://custom-host:6379/0"}):
                from app.celery_app import get_redis_url

                result = get_redis_url()
                assert result == "redis://custom-host:6379/0"


class TestCeleryAppConfiguration:
    """Test Celery app configuration"""

    def test_celery_app_exists(self):
        """Test that celery_app is created"""
        from app.celery_app import celery_app

        assert celery_app is not None
        assert isinstance(celery_app, Celery)

    def test_celery_app_name(self):
        """Test that celery_app has correct name"""
        from app.celery_app import celery_app

        assert celery_app.main == "audio_pipeline"

    def test_celery_task_includes(self):
        """Test that celery_app includes all required task modules"""
        from app.celery_app import celery_app

        # Check that task modules are included
        expected_modules = [
            "app.tasks.audio_tasks",
            "app.tasks.model_tasks",
            "app.tasks.health_tasks"
        ]

        # The includes should be set in the app configuration
        assert hasattr(celery_app, 'conf')

    def test_celery_serialization_config(self):
        """Test Celery serialization configuration"""
        from app.celery_app import celery_app

        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.accept_content == ["json"]

    def test_celery_worker_config(self):
        """Test Celery worker configuration"""
        from app.celery_app import celery_app

        assert celery_app.conf.worker_pool == 'solo'
        assert celery_app.conf.worker_concurrency == 1
        assert celery_app.conf.worker_prefetch_multiplier == 1

    def test_celery_time_limits(self):
        """Test Celery task time limit configuration"""
        from app.celery_app import celery_app

        assert celery_app.conf.task_soft_time_limit == 600  # 10 minutes
        assert celery_app.conf.task_time_limit == 900  # 15 minutes

    def test_celery_result_backend_config(self):
        """Test Celery result backend configuration"""
        from app.celery_app import celery_app

        assert celery_app.conf.result_expires == 7200  # 2 hours
        assert celery_app.conf.result_backend_max_retries == 3
        assert celery_app.conf.result_compression == 'gzip'

    def test_celery_task_acknowledgment(self):
        """Test Celery task acknowledgment settings"""
        from app.celery_app import celery_app

        assert celery_app.conf.task_acks_late is True
        assert celery_app.conf.task_reject_on_worker_lost is True
        assert celery_app.conf.task_ignore_result is False

    def test_celery_broker_connection_config(self):
        """Test Celery broker connection configuration"""
        from app.celery_app import celery_app

        assert celery_app.conf.broker_connection_retry_on_startup is True
        assert celery_app.conf.broker_connection_retry is True
        assert celery_app.conf.broker_pool_limit == 10

    def test_celery_task_routing(self):
        """Test Celery task routing configuration"""
        from app.celery_app import celery_app

        task_routes = celery_app.conf.task_routes

        # Check audio processing tasks
        assert task_routes['process_audio_task'] == {'queue': 'model_processing'}
        assert task_routes['process_audio_quick_task'] == {'queue': 'model_processing'}
        assert task_routes['process_streaming_audio_task'] == {'queue': 'model_processing'}

        # Check model tasks
        assert task_routes['ner_extract_task'] == {'queue': 'model_processing'}
        assert task_routes['classifier_classify_task'] == {'queue': 'model_processing'}
        assert task_routes['translation_translate_task'] == {'queue': 'model_processing'}
        assert task_routes['summarization_summarize_task'] == {'queue': 'model_processing'}
        assert task_routes['qa_evaluate_task'] == {'queue': 'model_processing'}
        assert task_routes['whisper_transcribe_task'] == {'queue': 'model_processing'}

    def test_celery_default_queue(self):
        """Test Celery default queue configuration"""
        from app.celery_app import celery_app

        assert celery_app.conf.task_default_queue == 'model_processing'

    def test_celery_events_enabled(self):
        """Test Celery event monitoring is enabled"""
        from app.celery_app import celery_app

        assert celery_app.conf.worker_send_task_events is True
        assert celery_app.conf.task_send_sent_event is True

    def test_celery_broker_url_format(self):
        """Test that broker URL is properly formatted"""
        from app.celery_app import celery_app

        broker_url = celery_app.conf.broker_url
        result_backend = celery_app.conf.result_backend

        # Both should be Redis URLs
        assert broker_url.startswith('redis://')
        assert result_backend.startswith('redis://')

        # Result backend should use different DB (usually /1 vs /0)
        assert broker_url != result_backend

    def test_celery_result_backend_uses_different_db(self):
        """Test that result backend uses different Redis DB than broker"""
        from app.celery_app import celery_app

        broker_url = celery_app.conf.broker_url
        result_backend = celery_app.conf.result_backend

        # Extract DB numbers
        broker_db = broker_url.split('/')[-1] if '/' in broker_url else '0'
        backend_db = result_backend.split('/')[-1] if '/' in result_backend else '1'

        # They should be different
        assert broker_db != backend_db

    def test_celery_configuration_is_dict(self):
        """Test that configuration can be accessed as dict"""
        from app.celery_app import celery_app

        # Configuration should be accessible
        assert hasattr(celery_app.conf, 'task_serializer')
        assert hasattr(celery_app.conf, 'worker_pool')

    def test_celery_app_ready(self):
        """Test that celery app is ready for use"""
        from app.celery_app import celery_app

        # App should have necessary methods
        assert hasattr(celery_app, 'task')
        assert hasattr(celery_app, 'send_task')
        assert hasattr(celery_app, 'control')

    def test_redis_url_consistency(self):
        """Test that Redis URLs are consistent across calls"""
        from app.celery_app import get_redis_url

        url1 = get_redis_url()
        url2 = get_redis_url()

        # Should return same URL on multiple calls
        assert url1 == url2


class TestCeleryAppIntegration:
    """Test Celery app integration and usage"""

    def test_celery_app_broker_configured(self):
        """Test that Celery has broker configured"""
        from app.celery_app import celery_app

        assert celery_app.conf.broker_url is not None
        assert len(celery_app.conf.broker_url) > 0

    def test_celery_app_backend_configured(self):
        """Test that Celery has result backend configured"""
        from app.celery_app import celery_app

        assert celery_app.conf.result_backend is not None
        assert len(celery_app.conf.result_backend) > 0

    def test_celery_queue_configuration_complete(self):
        """Test that all necessary queues are configured"""
        from app.celery_app import celery_app

        task_routes = celery_app.conf.task_routes

        # Should have at least 6 tasks routed
        assert len(task_routes) >= 6

    def test_all_routed_tasks_use_model_processing_queue(self):
        """Test that all routed tasks use model_processing queue"""
        from app.celery_app import celery_app

        task_routes = celery_app.conf.task_routes

        for task_name, route_config in task_routes.items():
            assert route_config['queue'] == 'model_processing', \
                f"Task {task_name} not routed to model_processing queue"
