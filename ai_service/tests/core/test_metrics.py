
import pytest
import time
from unittest.mock import patch, MagicMock
# We need to import the metrics module to patch its attributes
import app.core.metrics as metrics

class TestMetrics:

    def test_metrics_exist(self):
        """Test that metric objects are instantiated"""
        assert metrics.api_requests_total is not None
        assert metrics.model_processing_seconds is not None
        assert metrics.celery_queue_length is not None

    def test_track_model_time_decorator_success(self):
        """Test decorator records success metrics"""
        
        # Patch the specific metric objects used in the decorator
        with patch.object(metrics, 'model_processing_seconds') as mock_hist, \
             patch.object(metrics, 'model_operations_total') as mock_counter:
            
            # Create a dummy decorated function
            @metrics.track_model_time("test_model", "test_op")
            def successful_func():
                return "result"
            
            # Execute
            result = successful_func()
            
            # Assertions
            assert result == "result"
            
            # Check histogram observation (latency)
            mock_hist.labels.assert_called_with(model="test_model", operation="test_op")
            mock_hist.labels.return_value.observe.assert_called_once()
            
            # Check counter increment (success)
            mock_counter.labels.assert_called_with(model="test_model", operation="test_op", status="success")
            mock_counter.labels.return_value.inc.assert_called_once()

    def test_track_model_time_decorator_failure(self):
        """Test decorator records failure metrics"""
        
        with patch.object(metrics, 'model_processing_seconds') as mock_hist, \
             patch.object(metrics, 'model_operations_total') as mock_counter:
            
            @metrics.track_model_time("test_model", "test_op")
            def failing_func():
                raise ValueError("Boom")
            
            # Execute and expect error
            with pytest.raises(ValueError):
                failing_func()
            
            # Check histogram observation (latency still recorded)
            mock_hist.labels.return_value.observe.assert_called_once()
            
            # Check counter increment (failure)
            mock_counter.labels.assert_called_with(model="test_model", operation="test_op", status="failure")
            mock_counter.labels.return_value.inc.assert_called_once()

    @pytest.mark.asyncio
    async def test_track_api_time_decorator(self):
        """Test async API time decorator"""
        
        with patch.object(metrics, 'api_active_requests') as mock_gauge, \
             patch.object(metrics, 'api_request_duration_seconds') as mock_hist:
            
            @metrics.track_api_time("/test/endpoint")
            async def async_endpoint():
                return "async_result"
            
            result = await async_endpoint()
            assert result == "async_result"
            
            # Check active requests gauge (inc then dec)
            mock_gauge.labels.assert_called_with(endpoint="/test/endpoint")
            mock_gauge.labels.return_value.inc.assert_called_once()
            mock_gauge.labels.return_value.dec.assert_called_once()
            
            # Check usage histogram
            mock_hist.labels.assert_called_with(method="POST", endpoint="/test/endpoint")
            mock_hist.labels.return_value.observe.assert_called_once()


    def test_update_functions(self):
        """Test helper update functions"""
        
        with patch.object(metrics, 'celery_queue_length') as mock_q:
            metrics.update_queue_metrics("default", 5)
            mock_q.labels.assert_called_with(queue="default")
            mock_q.labels.return_value.set.assert_called_with(5)
            
        with patch.object(metrics, 'model_loaded') as mock_loaded:
            metrics.update_model_status("ner", True)
            mock_loaded.labels.assert_called_with(model="ner")
            mock_loaded.labels.return_value.set.assert_called_with(1)
            
            metrics.update_model_status("ner", False)
            mock_loaded.labels.return_value.set.assert_called_with(0)

        with patch.object(metrics, 'celery_workers_online') as mock_workers:
            metrics.update_worker_count(3)
            mock_workers.set.assert_called_with(3)

        with patch.object(metrics, 'api_upload_size_bytes') as mock_upload:
            metrics.record_upload_size("/upload", 1024)
            mock_upload.labels.assert_called_with(endpoint="/upload")
            mock_upload.labels.return_value.observe.assert_called_with(1024)

        with patch.object(metrics, 'streaming_active_sessions') as mock_sessions:
            metrics.update_streaming_sessions("call", 2)
            mock_sessions.labels.assert_called_with(type="call")
            mock_sessions.labels.return_value.set.assert_called_with(2)

        with patch.object(metrics, 'streaming_latency_seconds') as mock_latency:
            metrics.record_streaming_latency("transcription", 0.5)
            mock_latency.labels.assert_called_with(session_type="transcription")
            mock_latency.labels.return_value.observe.assert_called_with(0.5)

    def test_initialize_metrics(self):
        """Test initialization logging"""
        with patch.object(metrics, 'app_info') as mock_info:
            metrics.initialize_metrics("TestApp", "1.0", "Site1")
            
            mock_info.info.assert_called_with({
                'app_name': 'TestApp',
                'version': '1.0',
                'site_id': 'Site1'
            })
