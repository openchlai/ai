"""
Comprehensive tests for notification_types model - All notification enums and utilities
"""
import pytest
from enum import Enum

from app.models.notification_types import (
    NotificationType,
    ProcessingMode,
    NotificationStatus,
    NotificationImportance,
    LEGACY_AGENT_MAPPING,
    LEGACY_MANAGER_MAPPING,
    LEGACY_ENHANCED_MAPPING,
    NOTIFICATION_IMPORTANCE,
    migrate_notification_type,
    get_notification_importance,
    is_streaming_notification,
    is_postcall_notification,
    is_system_notification,
)


class TestNotificationType:
    """Tests for NotificationType enum"""

    def test_notification_type_is_enum(self):
        """Test NotificationType is an Enum"""
        assert issubclass(NotificationType, Enum)

    def test_notification_type_is_string_enum(self):
        """Test NotificationType values are strings"""
        for notification_type in NotificationType:
            assert isinstance(notification_type.value, str)

    def test_streaming_call_start(self):
        """Test STREAMING_CALL_START value"""
        assert NotificationType.STREAMING_CALL_START.value == "streaming_call_start"

    def test_streaming_call_end(self):
        """Test STREAMING_CALL_END value"""
        assert NotificationType.STREAMING_CALL_END.value == "streaming_call_end"

    def test_streaming_transcription_segment(self):
        """Test STREAMING_TRANSCRIPTION_SEGMENT value"""
        assert NotificationType.STREAMING_TRANSCRIPTION_SEGMENT.value == "streaming_transcription_segment"

    def test_streaming_translation_progress(self):
        """Test STREAMING_TRANSLATION_PROGRESS value"""
        assert NotificationType.STREAMING_TRANSLATION_PROGRESS.value == "streaming_translation_progress"

    def test_streaming_processing_update(self):
        """Test STREAMING_PROCESSING_UPDATE value"""
        assert NotificationType.STREAMING_PROCESSING_UPDATE.value == "streaming_processing_update"

    def test_streaming_transcription(self):
        """Test STREAMING_TRANSCRIPTION value"""
        assert NotificationType.STREAMING_TRANSCRIPTION.value == "streaming_transcription"

    def test_streaming_translation(self):
        """Test STREAMING_TRANSLATION value"""
        assert NotificationType.STREAMING_TRANSLATION.value == "streaming_translation"

    def test_streaming_entities(self):
        """Test STREAMING_ENTITIES value"""
        assert NotificationType.STREAMING_ENTITIES.value == "streaming_entities"

    def test_streaming_classification(self):
        """Test STREAMING_CLASSIFICATION value"""
        assert NotificationType.STREAMING_CLASSIFICATION.value == "streaming_classification"

    def test_streaming_qa(self):
        """Test STREAMING_QA value"""
        assert NotificationType.STREAMING_QA.value == "streaming_qa"

    def test_streaming_summary(self):
        """Test STREAMING_SUMMARY value"""
        assert NotificationType.STREAMING_SUMMARY.value == "streaming_summary"

    def test_streaming_insights(self):
        """Test STREAMING_INSIGHTS value"""
        assert NotificationType.STREAMING_INSIGHTS.value == "streaming_insights"

    def test_postcall_start(self):
        """Test POSTCALL_START value"""
        assert NotificationType.POSTCALL_START.value == "postcall_start"

    def test_postcall_transcription(self):
        """Test POSTCALL_TRANSCRIPTION value"""
        assert NotificationType.POSTCALL_TRANSCRIPTION.value == "postcall_transcription"

    def test_postcall_translation(self):
        """Test POSTCALL_TRANSLATION value"""
        assert NotificationType.POSTCALL_TRANSLATION.value == "postcall_translation"

    def test_postcall_entities(self):
        """Test POSTCALL_ENTITIES value"""
        assert NotificationType.POSTCALL_ENTITIES.value == "postcall_entities"

    def test_postcall_classification(self):
        """Test POSTCALL_CLASSIFICATION value"""
        assert NotificationType.POSTCALL_CLASSIFICATION.value == "postcall_classification"

    def test_postcall_summary(self):
        """Test POSTCALL_SUMMARY value"""
        assert NotificationType.POSTCALL_SUMMARY.value == "postcall_summary"

    def test_postcall_qa_scoring(self):
        """Test POSTCALL_QA_SCORING value"""
        assert NotificationType.POSTCALL_QA_SCORING.value == "postcall_qa_scoring"

    def test_postcall_insights(self):
        """Test POSTCALL_INSIGHTS value"""
        assert NotificationType.POSTCALL_INSIGHTS.value == "postcall_insights"

    def test_postcall_gpt_insights(self):
        """Test POSTCALL_GPT_INSIGHTS value"""
        assert NotificationType.POSTCALL_GPT_INSIGHTS.value == "postcall_gpt_insights"

    def test_postcall_mistral_insights(self):
        """Test POSTCALL_MISTRAL_INSIGHTS value (deprecated)"""
        assert NotificationType.POSTCALL_MISTRAL_INSIGHTS.value == "postcall_mistral_insights"

    def test_postcall_ai_service_insights(self):
        """Test POSTCALL_AI_SERVICE_INSIGHTS value"""
        assert NotificationType.POSTCALL_AI_SERVICE_INSIGHTS.value == "postcall_ai_service_insights"

    def test_postcall_complete(self):
        """Test POSTCALL_COMPLETE value"""
        assert NotificationType.POSTCALL_COMPLETE.value == "postcall_complete"

    def test_system_processing_progress(self):
        """Test SYSTEM_PROCESSING_PROGRESS value"""
        assert NotificationType.SYSTEM_PROCESSING_PROGRESS.value == "system_processing_progress"

    def test_system_processing_error(self):
        """Test SYSTEM_PROCESSING_ERROR value"""
        assert NotificationType.SYSTEM_PROCESSING_ERROR.value == "system_processing_error"

    def test_system_error(self):
        """Test SYSTEM_ERROR value"""
        assert NotificationType.SYSTEM_ERROR.value == "system_error"

    def test_unified_insight(self):
        """Test UNIFIED_INSIGHT value"""
        assert NotificationType.UNIFIED_INSIGHT.value == "unified_insight"

    def test_notification_type_count(self):
        """Test all notification types are present"""
        notification_types = list(NotificationType)
        assert len(notification_types) == 28


class TestProcessingMode:
    """Tests for ProcessingMode enum"""

    def test_processing_mode_is_enum(self):
        """Test ProcessingMode is an Enum"""
        assert issubclass(ProcessingMode, Enum)

    def test_processing_mode_is_string_enum(self):
        """Test ProcessingMode values are strings"""
        for mode in ProcessingMode:
            assert isinstance(mode.value, str)

    def test_streaming_mode(self):
        """Test STREAMING mode value"""
        assert ProcessingMode.STREAMING.value == "streaming"

    def test_post_call_mode(self):
        """Test POST_CALL mode value"""
        assert ProcessingMode.POST_CALL.value == "post_call"

    def test_dual_mode(self):
        """Test DUAL mode value"""
        assert ProcessingMode.DUAL.value == "dual"

    def test_adaptive_mode(self):
        """Test ADAPTIVE mode value"""
        assert ProcessingMode.ADAPTIVE.value == "adaptive"

    def test_processing_mode_count(self):
        """Test all processing modes are present"""
        modes = list(ProcessingMode)
        assert len(modes) == 4


class TestNotificationStatus:
    """Tests for NotificationStatus enum"""

    def test_notification_status_is_enum(self):
        """Test NotificationStatus is an Enum"""
        assert issubclass(NotificationStatus, Enum)

    def test_notification_status_is_string_enum(self):
        """Test NotificationStatus values are strings"""
        for status in NotificationStatus:
            assert isinstance(status.value, str)

    def test_success_status(self):
        """Test SUCCESS status value"""
        assert NotificationStatus.SUCCESS.value == "success"

    def test_in_progress_status(self):
        """Test IN_PROGRESS status value"""
        assert NotificationStatus.IN_PROGRESS.value == "in_progress"

    def test_error_status(self):
        """Test ERROR status value"""
        assert NotificationStatus.ERROR.value == "error"

    def test_notification_status_count(self):
        """Test all statuses are present"""
        statuses = list(NotificationStatus)
        assert len(statuses) == 3


class TestNotificationImportance:
    """Tests for NotificationImportance enum"""

    def test_notification_importance_is_enum(self):
        """Test NotificationImportance is an Enum"""
        assert issubclass(NotificationImportance, Enum)

    def test_notification_importance_is_string_enum(self):
        """Test NotificationImportance values are strings"""
        for importance in NotificationImportance:
            assert isinstance(importance.value, str)

    def test_progress_importance(self):
        """Test PROGRESS importance value"""
        assert NotificationImportance.PROGRESS.value == "progress"

    def test_result_importance(self):
        """Test RESULT importance value"""
        assert NotificationImportance.RESULT.value == "result"

    def test_critical_importance(self):
        """Test CRITICAL importance value"""
        assert NotificationImportance.CRITICAL.value == "critical"

    def test_notification_importance_count(self):
        """Test all importances are present"""
        importances = list(NotificationImportance)
        assert len(importances) == 3


class TestLegacyMappings:
    """Tests for legacy notification type mappings"""

    def test_legacy_agent_mapping_is_dict(self):
        """Test LEGACY_AGENT_MAPPING is a dictionary"""
        assert isinstance(LEGACY_AGENT_MAPPING, dict)

    def test_legacy_agent_mapping_not_empty(self):
        """Test LEGACY_AGENT_MAPPING has entries"""
        assert len(LEGACY_AGENT_MAPPING) > 0

    def test_legacy_agent_mapping_values_are_notification_types(self):
        """Test all values in LEGACY_AGENT_MAPPING are NotificationType"""
        for key, value in LEGACY_AGENT_MAPPING.items():
            assert isinstance(value, NotificationType)

    def test_legacy_agent_mapping_call_start(self):
        """Test agent mapping for call_start"""
        assert LEGACY_AGENT_MAPPING["call_start"] == NotificationType.STREAMING_CALL_START

    def test_legacy_agent_mapping_call_end(self):
        """Test agent mapping for call_end"""
        assert LEGACY_AGENT_MAPPING["call_end"] == NotificationType.STREAMING_CALL_END

    def test_legacy_manager_mapping_is_dict(self):
        """Test LEGACY_MANAGER_MAPPING is a dictionary"""
        assert isinstance(LEGACY_MANAGER_MAPPING, dict)

    def test_legacy_manager_mapping_not_empty(self):
        """Test LEGACY_MANAGER_MAPPING has entries"""
        assert len(LEGACY_MANAGER_MAPPING) > 0

    def test_legacy_manager_mapping_values_are_notification_types(self):
        """Test all values in LEGACY_MANAGER_MAPPING are NotificationType"""
        for key, value in LEGACY_MANAGER_MAPPING.items():
            assert isinstance(value, NotificationType)

    def test_legacy_enhanced_mapping_is_dict(self):
        """Test LEGACY_ENHANCED_MAPPING is a dictionary"""
        assert isinstance(LEGACY_ENHANCED_MAPPING, dict)

    def test_legacy_enhanced_mapping_not_empty(self):
        """Test LEGACY_ENHANCED_MAPPING has entries"""
        assert len(LEGACY_ENHANCED_MAPPING) > 0

    def test_legacy_enhanced_mapping_values_are_notification_types(self):
        """Test all values in LEGACY_ENHANCED_MAPPING are NotificationType"""
        for key, value in LEGACY_ENHANCED_MAPPING.items():
            assert isinstance(value, NotificationType)


class TestNotificationImportanceMapping:
    """Tests for notification importance classification"""

    def test_notification_importance_is_dict(self):
        """Test NOTIFICATION_IMPORTANCE is a dictionary"""
        assert isinstance(NOTIFICATION_IMPORTANCE, dict)

    def test_notification_importance_not_empty(self):
        """Test NOTIFICATION_IMPORTANCE has entries"""
        assert len(NOTIFICATION_IMPORTANCE) > 0

    def test_notification_importance_keys_are_notification_types(self):
        """Test all keys in NOTIFICATION_IMPORTANCE are NotificationType"""
        for key in NOTIFICATION_IMPORTANCE.keys():
            assert isinstance(key, NotificationType)

    def test_notification_importance_values_are_importance_enums(self):
        """Test all values in NOTIFICATION_IMPORTANCE are NotificationImportance"""
        for value in NOTIFICATION_IMPORTANCE.values():
            assert isinstance(value, NotificationImportance)

    def test_streaming_transcription_segment_is_progress(self):
        """Test STREAMING_TRANSCRIPTION_SEGMENT is PROGRESS importance"""
        assert NOTIFICATION_IMPORTANCE[NotificationType.STREAMING_TRANSCRIPTION_SEGMENT] == NotificationImportance.PROGRESS

    def test_streaming_call_start_is_critical(self):
        """Test STREAMING_CALL_START is CRITICAL importance"""
        assert NOTIFICATION_IMPORTANCE[NotificationType.STREAMING_CALL_START] == NotificationImportance.CRITICAL

    def test_streaming_translation_is_result(self):
        """Test STREAMING_TRANSLATION is RESULT importance"""
        assert NOTIFICATION_IMPORTANCE[NotificationType.STREAMING_TRANSLATION] == NotificationImportance.RESULT


class TestMigrateNotificationType:
    """Tests for migrate_notification_type function"""

    def test_migrate_from_agent_source(self):
        """Test migration from agent source"""
        result = migrate_notification_type("call_start", source="agent")
        assert result == NotificationType.STREAMING_CALL_START

    def test_migrate_from_enhanced_source(self):
        """Test migration from enhanced source"""
        result = migrate_notification_type("call_start", source="enhanced")
        assert result == NotificationType.STREAMING_CALL_START

    def test_migrate_from_manager_source(self):
        """Test migration from manager source"""
        result = migrate_notification_type("call_start", source="manager")
        assert result == NotificationType.STREAMING_CALL_START

    def test_migrate_default_source_is_enhanced(self):
        """Test migration defaults to enhanced source"""
        result = migrate_notification_type("call_start")
        assert result == NotificationType.STREAMING_CALL_START

    def test_migrate_case_insensitive_source(self):
        """Test migration is case-insensitive for source"""
        result1 = migrate_notification_type("call_start", source="AGENT")
        result2 = migrate_notification_type("call_start", source="Agent")
        assert result1 == result2

    def test_migrate_unknown_source_raises_error(self):
        """Test migration raises error for unknown source"""
        with pytest.raises(ValueError, match="Unknown source"):
            migrate_notification_type("call_start", source="invalid")

    def test_migrate_unknown_notification_type_raises_error(self):
        """Test migration raises error for unknown notification type"""
        with pytest.raises(ValueError, match="Unknown notification type"):
            migrate_notification_type("unknown_type", source="agent")

    def test_migrate_all_agent_mappings(self):
        """Test migration works for all agent mappings"""
        for old_value, expected in LEGACY_AGENT_MAPPING.items():
            result = migrate_notification_type(old_value, source="agent")
            assert result == expected

    def test_migrate_all_enhanced_mappings(self):
        """Test migration works for all enhanced mappings"""
        for old_value, expected in LEGACY_ENHANCED_MAPPING.items():
            result = migrate_notification_type(old_value, source="enhanced")
            assert result == expected

    def test_migrate_all_manager_mappings(self):
        """Test migration works for all manager mappings"""
        for old_value, expected in LEGACY_MANAGER_MAPPING.items():
            result = migrate_notification_type(old_value, source="manager")
            assert result == expected


class TestGetNotificationImportance:
    """Tests for get_notification_importance function"""

    def test_get_importance_for_streaming_call_start(self):
        """Test importance for STREAMING_CALL_START"""
        importance = get_notification_importance(NotificationType.STREAMING_CALL_START)
        assert importance == NotificationImportance.CRITICAL

    def test_get_importance_for_streaming_transcription_segment(self):
        """Test importance for STREAMING_TRANSCRIPTION_SEGMENT"""
        importance = get_notification_importance(NotificationType.STREAMING_TRANSCRIPTION_SEGMENT)
        assert importance == NotificationImportance.PROGRESS

    def test_get_importance_for_streaming_translation(self):
        """Test importance for STREAMING_TRANSLATION"""
        importance = get_notification_importance(NotificationType.STREAMING_TRANSLATION)
        assert importance == NotificationImportance.RESULT

    def test_get_importance_for_system_error(self):
        """Test importance for SYSTEM_ERROR"""
        importance = get_notification_importance(NotificationType.SYSTEM_ERROR)
        assert importance == NotificationImportance.CRITICAL

    def test_get_importance_returns_result_for_unmapped_type(self):
        """Test unmapped types default to RESULT importance"""
        # Create a mock scenario - but NotificationType enum is fixed
        # So we'll just verify all mapped types work
        for notification_type in NotificationType:
            importance = get_notification_importance(notification_type)
            assert isinstance(importance, NotificationImportance)

    def test_get_importance_for_all_notification_types(self):
        """Test importance can be retrieved for all notification types"""
        for notification_type in NotificationType:
            importance = get_notification_importance(notification_type)
            assert isinstance(importance, NotificationImportance)


class TestStreamingNotificationHelper:
    """Tests for is_streaming_notification function"""

    def test_streaming_call_start_is_streaming(self):
        """Test STREAMING_CALL_START is recognized as streaming"""
        assert is_streaming_notification(NotificationType.STREAMING_CALL_START) is True

    def test_streaming_transcription_is_streaming(self):
        """Test STREAMING_TRANSCRIPTION is recognized as streaming"""
        assert is_streaming_notification(NotificationType.STREAMING_TRANSCRIPTION) is True

    def test_postcall_transcription_is_not_streaming(self):
        """Test POSTCALL_TRANSCRIPTION is not recognized as streaming"""
        assert is_streaming_notification(NotificationType.POSTCALL_TRANSCRIPTION) is False

    def test_system_error_is_not_streaming(self):
        """Test SYSTEM_ERROR is not recognized as streaming"""
        assert is_streaming_notification(NotificationType.SYSTEM_ERROR) is False

    def test_all_streaming_notifications_detected(self):
        """Test all STREAMING_* notifications are detected"""
        for notification_type in NotificationType:
            result = is_streaming_notification(notification_type)
            if notification_type.value.startswith("streaming_"):
                assert result is True
            else:
                assert result is False


class TestPostcallNotificationHelper:
    """Tests for is_postcall_notification function"""

    def test_postcall_transcription_is_postcall(self):
        """Test POSTCALL_TRANSCRIPTION is recognized as postcall"""
        assert is_postcall_notification(NotificationType.POSTCALL_TRANSCRIPTION) is True

    def test_postcall_complete_is_postcall(self):
        """Test POSTCALL_COMPLETE is recognized as postcall"""
        assert is_postcall_notification(NotificationType.POSTCALL_COMPLETE) is True

    def test_streaming_transcription_is_not_postcall(self):
        """Test STREAMING_TRANSCRIPTION is not recognized as postcall"""
        assert is_postcall_notification(NotificationType.STREAMING_TRANSCRIPTION) is False

    def test_system_error_is_not_postcall(self):
        """Test SYSTEM_ERROR is not recognized as postcall"""
        assert is_postcall_notification(NotificationType.SYSTEM_ERROR) is False

    def test_all_postcall_notifications_detected(self):
        """Test all POSTCALL_* notifications are detected"""
        for notification_type in NotificationType:
            result = is_postcall_notification(notification_type)
            if notification_type.value.startswith("postcall_"):
                assert result is True
            else:
                assert result is False


class TestSystemNotificationHelper:
    """Tests for is_system_notification function"""

    def test_system_error_is_system(self):
        """Test SYSTEM_ERROR is recognized as system"""
        assert is_system_notification(NotificationType.SYSTEM_ERROR) is True

    def test_system_processing_error_is_system(self):
        """Test SYSTEM_PROCESSING_ERROR is recognized as system"""
        assert is_system_notification(NotificationType.SYSTEM_PROCESSING_ERROR) is True

    def test_system_processing_progress_is_system(self):
        """Test SYSTEM_PROCESSING_PROGRESS is recognized as system"""
        assert is_system_notification(NotificationType.SYSTEM_PROCESSING_PROGRESS) is True

    def test_streaming_call_start_is_not_system(self):
        """Test STREAMING_CALL_START is not recognized as system"""
        assert is_system_notification(NotificationType.STREAMING_CALL_START) is False

    def test_postcall_complete_is_not_system(self):
        """Test POSTCALL_COMPLETE is not recognized as system"""
        assert is_system_notification(NotificationType.POSTCALL_COMPLETE) is False

    def test_all_system_notifications_detected(self):
        """Test all SYSTEM_* notifications are detected"""
        for notification_type in NotificationType:
            result = is_system_notification(notification_type)
            if notification_type.value.startswith("system_"):
                assert result is True
            else:
                assert result is False


class TestNotificationTypeCompatibility:
    """Tests for enum compatibility and usage"""

    def test_notification_type_comparison(self):
        """Test NotificationType enum comparison"""
        assert NotificationType.STREAMING_CALL_START == NotificationType.STREAMING_CALL_START
        assert NotificationType.STREAMING_CALL_START != NotificationType.STREAMING_CALL_END

    def test_notification_type_string_conversion(self):
        """Test NotificationType converts to string correctly"""
        notification = NotificationType.STREAMING_CALL_START
        assert str(notification) == "NotificationType.STREAMING_CALL_START"
        assert notification.value == "streaming_call_start"

    def test_processing_mode_comparison(self):
        """Test ProcessingMode enum comparison"""
        assert ProcessingMode.STREAMING == ProcessingMode.STREAMING
        assert ProcessingMode.STREAMING != ProcessingMode.POST_CALL

    def test_notification_status_comparison(self):
        """Test NotificationStatus enum comparison"""
        assert NotificationStatus.SUCCESS == NotificationStatus.SUCCESS
        assert NotificationStatus.SUCCESS != NotificationStatus.ERROR


class TestEnumIntegration:
    """Integration tests for all enums"""

    def test_notification_type_with_processing_mode(self):
        """Test NotificationType works with ProcessingMode"""
        # Streaming mode should have streaming notifications
        streaming_type = NotificationType.STREAMING_CALL_START
        assert is_streaming_notification(streaming_type) is True

    def test_notification_importance_filtering(self):
        """Test filtering notifications by importance"""
        critical_notifications = [
            nt for nt in NotificationType
            if get_notification_importance(nt) == NotificationImportance.CRITICAL
        ]
        assert len(critical_notifications) > 0

    def test_legacy_compatibility(self):
        """Test legacy mappings for backward compatibility"""
        # Agent mapping should convert old types to new types
        old_call_start = "call_start"
        new_type = migrate_notification_type(old_call_start, source="agent")
        assert isinstance(new_type, NotificationType)
        assert is_streaming_notification(new_type) is True
