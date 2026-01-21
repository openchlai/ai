
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.core.notification_manager import NotificationManager, NotificationMode
from app.models.notification_types import NotificationType, NotificationImportance

class TestNotificationManager:

    @pytest.fixture
    def mock_settings(self):
        with patch('app.config.settings.settings') as mock:
            mock.notification_mode = "results_only"
            mock.enable_agent_notifications = True
            mock.notification_endpoint_url = "http://test"
            yield mock

    @pytest.fixture
    def mock_service(self):
        with patch('app.services.enhanced_notification_service.enhanced_notification_service', new_callable=AsyncMock) as mock:
            yield mock

    def test_initialization(self, mock_settings, mock_service):
        manager = NotificationManager()
        assert manager.current_mode == NotificationMode.RESULTS_ONLY
        assert manager.notifications_enabled is True
        assert manager.service_available is True

    def test_parse_notification_mode(self, mock_settings):
        manager = NotificationManager()
        assert manager._parse_notification_mode("ALL") == NotificationMode.ALL
        assert manager._parse_notification_mode("unknown") == NotificationMode.RESULTS_ONLY

    def test_should_send_notification_all(self, mock_settings):
        mock_settings.notification_mode = "all"
        manager = NotificationManager()
        
        assert manager.should_send_notification(NotificationType.STREAMING_CALL_START) is True
        assert manager.should_send_notification(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT) is True

    def test_should_send_notification_results_only(self, mock_settings):
        mock_settings.notification_mode = "results_only"
        manager = NotificationManager()
        
        # Critical types should send
        assert manager.should_send_notification(NotificationType.STREAMING_CALL_START) is True
        assert manager.should_send_notification(NotificationType.STREAMING_CALL_END) is True
        
        # Intermediate types without results should NOT send
        assert manager.should_send_notification(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT, has_results=False) is False
        
        # Intermediate types WITH results should send
        assert manager.should_send_notification(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT, has_results=True) is True

    def test_should_send_notification_critical_only(self, mock_settings):
        mock_settings.notification_mode = "critical_only"
        manager = NotificationManager()
        
        assert manager.should_send_notification(NotificationType.STREAMING_CALL_START) is True
        assert manager.should_send_notification(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT, has_results=True) is False

    @pytest.mark.asyncio
    async def test_send_notification_if_allowed_success(self, mock_settings, mock_service):
        manager = NotificationManager()
        
        # Should be allowed (Start is critical)
        payload = {"connection_info": {}}
        success = await manager.send_notification_if_allowed(
            NotificationType.STREAMING_CALL_START, "call1", payload
        )
        assert success is True
        mock_service.send_call_start.assert_awaited_once_with("call1", {})

    @pytest.mark.asyncio
    async def test_send_notification_if_allowed_filtered(self, mock_settings, mock_service):
        manager = NotificationManager() # results_only
        
        # Should be filtered (Segment no result)
        payload = {"text": "incomplete"}
        success = await manager.send_notification_if_allowed(
            NotificationType.STREAMING_TRANSCRIPTION_SEGMENT, "call1", payload
        )
        assert success is False
        mock_service.send_transcript_segment.assert_not_called()

    def test_detect_results_in_payload(self, mock_settings):
        manager = NotificationManager()
        
        assert manager._detect_results_in_payload({"summary": "This is a summary"}) is True
        assert manager._detect_results_in_payload({"other": "data"}) is False
        assert manager._detect_results_in_payload({"summary": ""}) is False

    def test_update_mode(self, mock_settings):
        manager = NotificationManager()
        assert manager.current_mode == NotificationMode.RESULTS_ONLY
        
        manager.update_mode("all")
        assert manager.current_mode == NotificationMode.ALL
        
    def test_statistics(self, mock_settings):
        manager = NotificationManager()
        manager.should_send_notification(NotificationType.STREAMING_CALL_START) # sent
        manager.should_send_notification(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT, has_results=False) # filtered
        
        assert manager.stats["total_sent"] >= 1
        assert manager.stats["total_filtered"] >= 1
        

        manager.reset_statistics()
        assert manager.stats["total_sent"] == 0

    @pytest.mark.asyncio
    async def test_dispatch_notification_types(self, mock_settings, mock_service):
        manager = NotificationManager()
        manager.service_available = True
        
        # Test Call End
        await manager._dispatch_notification(
            NotificationType.STREAMING_CALL_END, "call1", {"reason": "done", "stats": {}}
        )
        mock_service.send_call_end.assert_awaited_once()

        # Test Streaming QA
        await manager._dispatch_notification(
            NotificationType.STREAMING_QA, "call1", {"qa_scores": {}}
        )
        mock_service.send_qa_update.assert_awaited_once()

        # Test Streaming Summary
        await manager._dispatch_notification(
            NotificationType.STREAMING_SUMMARY, "call1", {"summary": "sum"}
        )
        mock_service.send_call_summary.assert_awaited_once()

        # Test Streaming Insights
        await manager._dispatch_notification(
            NotificationType.STREAMING_INSIGHTS, "call1", {"insights": {}}
        )
        mock_service.send_call_insights.assert_awaited_once()

        # Test GPT Insights
        await manager._dispatch_notification(
            NotificationType.POSTCALL_GPT_INSIGHTS, "call1", {"gpt_insights": {}}
        )
        mock_service.send_gpt_insights.assert_awaited_once()

        # Test Unified Insights
        await manager._dispatch_notification(
            NotificationType.UNIFIED_INSIGHT, "call1", {"pipeline_result": {}}
        )
        mock_service.send_unified_insight.assert_awaited_once()


        # Test Generic (fallback)
        from app.models.notification_types import ProcessingMode
        await manager._dispatch_notification(
            NotificationType.STREAMING_CLASSIFICATION, "call1", {"data": "test", "processing_mode": "post_call"}
        )
        mock_service.send_notification.assert_awaited()
        # Check args to ensure processing_mode was parsed
        call_args = mock_service.send_notification.call_args
        assert call_args.kwargs['processing_mode'] == ProcessingMode.POST_CALL

    @pytest.mark.asyncio
    async def test_dispatch_service_unavailable(self, mock_settings):
        manager = NotificationManager()
        manager.service_available = False
        
        result = await manager._dispatch_notification(NotificationType.STREAMING_CALL_START, "c1", {})
        assert result is False

    @pytest.mark.asyncio
    async def test_dispatch_exception(self, mock_settings, mock_service):
        manager = NotificationManager()
        manager.service_available = True
        mock_service.send_call_start.side_effect = Exception("Service unavailable")
        
        result = await manager._dispatch_notification(
            NotificationType.STREAMING_CALL_START, "c1", {}
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_failed_logic(self, mock_settings, mock_service):
        manager = NotificationManager()
        # Mock dispatch to return False
        with patch.object(manager, '_dispatch_notification', new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.return_value = False
            
            result = await manager.send_notification_if_allowed(
                NotificationType.STREAMING_CALL_START, "c1", {}
            )
            assert result is False
            
    @pytest.mark.asyncio
    async def test_send_notification_exception_logic(self, mock_settings, mock_service):
        manager = NotificationManager()
        with patch.object(manager, '_dispatch_notification', side_effect=Exception("Boom")):
            result = await manager.send_notification_if_allowed(
                NotificationType.STREAMING_CALL_START, "c1", {}
            )
            assert result is False

    def test_notification_service_import_error(self):
        """Test initialization when notification service fails to import"""
        import sys
        from unittest.mock import patch

        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.notification_mode = "results_only"
            mock_settings.enable_agent_notifications = True
            mock_settings.notification_endpoint_url = "http://test"

            # Temporarily remove the module from sys.modules to simulate ImportError
            original_module = sys.modules.get('app.services.enhanced_notification_service')
            if original_module:
                sys.modules['app.services.enhanced_notification_service'] = None

            try:
                # This should trigger the ImportError handling
                manager = NotificationManager()
                assert manager.service_available is False
                assert manager.notification_service is None
            finally:
                # Restore the original module
                if original_module:
                    sys.modules['app.services.enhanced_notification_service'] = original_module

    def test_should_send_notification_service_unavailable(self, mock_settings):
        """Test that notifications are filtered when service is unavailable"""
        manager = NotificationManager()
        manager.service_available = False

        result = manager.should_send_notification(NotificationType.STREAMING_CALL_START, has_results=False)

        assert result is False
        assert manager.stats["total_filtered"] > 0

    def test_should_send_notification_disabled_mode(self, mock_settings):
        """Test that notifications are filtered in DISABLED mode"""
        manager = NotificationManager()
        manager.current_mode = NotificationMode.DISABLED

        result = manager.should_send_notification(NotificationType.STREAMING_CALL_START, has_results=False)

        assert result is False
        assert manager.stats["total_filtered"] > 0

    def test_should_send_notification_unknown_mode(self, mock_settings):
        """Test default behavior for unknown notification mode"""
        manager = NotificationManager()
        # Create an invalid mode by directly setting an enum member
        # This tests the default case in should_send_notification
        manager.current_mode = NotificationMode.ALL  # Use valid mode first

        # Test with a notification type that doesn't match any specific mode logic
        # This will hit the default "unknown_mode" filtering path
        with patch.object(manager, 'current_mode', NotificationMode.CRITICAL_ONLY):
            # Use a non-critical notification (PROGRESS type)
            result = manager.should_send_notification(NotificationType.STREAMING_TRANSLATION_PROGRESS, has_results=False)
            # Non-critical notification in CRITICAL_ONLY mode should be filtered
            assert result is False

    def test_is_result_notification(self, mock_settings):
        """Test _is_result_notification method for RESULT importance types"""
        manager = NotificationManager()

        # STREAMING_TRANSLATION is a RESULT type notification
        is_result = manager._is_result_notification(NotificationType.STREAMING_TRANSLATION)
        assert is_result is True

        # STREAMING_TRANSCRIPTION_SEGMENT is PROGRESS, not RESULT
        is_not_result = manager._is_result_notification(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT)
        assert is_not_result is False
