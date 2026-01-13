"""
Unified Notification Types for AI Service

This module consolidates notification types from three previously separate services:
- AgentNotificationService (legacy v1.0 format)
- EnhancedNotificationService (v2.0 format)
- NotificationManager (filtering layer)

All notification types are now defined in a single source of truth with clear
naming conventions and backward compatibility mappings.
"""
from enum import Enum
from typing import Dict


class NotificationType(str, Enum):
    """
    Unified notification types for all services.

    Naming Convention:
    - STREAMING_* for real-time/progressive updates during calls
    - POSTCALL_* for post-call analysis results
    - SYSTEM_* for system-level events (errors, status)
    """

    # ===== STREAMING (Real-time) Notifications =====
    # Call lifecycle
    STREAMING_CALL_START = "streaming_call_start"
    STREAMING_CALL_END = "streaming_call_end"

    # Progressive updates (no results, just progress)
    STREAMING_TRANSCRIPTION_SEGMENT = "streaming_transcription_segment"
    STREAMING_TRANSLATION_PROGRESS = "streaming_translation_progress"
    STREAMING_PROCESSING_UPDATE = "streaming_processing_update"

    # Progressive results (contain actual results)
    STREAMING_TRANSCRIPTION = "streaming_transcription"
    STREAMING_TRANSLATION = "streaming_translation"
    STREAMING_ENTITIES = "streaming_entities"
    STREAMING_CLASSIFICATION = "streaming_classification"
    STREAMING_QA = "streaming_qa"
    STREAMING_SUMMARY = "streaming_summary"
    STREAMING_INSIGHTS = "streaming_insights"

    # ===== POST-CALL (Batch) Notifications =====
    POSTCALL_START = "postcall_start"
    POSTCALL_TRANSCRIPTION = "postcall_transcription"
    POSTCALL_TRANSLATION = "postcall_translation"
    POSTCALL_ENTITIES = "postcall_entities"
    POSTCALL_CLASSIFICATION = "postcall_classification"
    POSTCALL_SUMMARY = "postcall_summary"
    POSTCALL_QA_SCORING = "postcall_qa_scoring"
    POSTCALL_INSIGHTS = "postcall_insights"
    POSTCALL_GPT_INSIGHTS = "postcall_gpt_insights"
    POSTCALL_COMPLETE = "postcall_complete"

    # ===== SYSTEM Notifications =====
    SYSTEM_PROCESSING_PROGRESS = "system_processing_progress"
    SYSTEM_PROCESSING_ERROR = "system_processing_error"
    SYSTEM_ERROR = "system_error"

    # ===== UNIFIED Notifications =====
    # Combined insights from multiple sources
    UNIFIED_INSIGHT = "unified_insight"


class ProcessingMode(str, Enum):
    """
    Defines the processing mode for a call.

    Used to indicate how the call is being processed and which notification
    types are expected.
    """
    STREAMING = "streaming"      # Real-time processing during call
    POST_CALL = "post_call"       # Batch processing after call completion
    DUAL = "dual"                 # Both streaming and post-call
    ADAPTIVE = "adaptive"         # System decides based on call characteristics


class NotificationStatus(str, Enum):
    """
    Defines the status/outcome of a notification or processing operation.
    """
    SUCCESS = "success"
    IN_PROGRESS = "in_progress"
    ERROR = "error"


class NotificationImportance(str, Enum):
    """
    Categorizes notifications by importance for filtering purposes.

    Used by NotificationManager to implement filtering modes.
    """
    PROGRESS = "progress"         # Progress updates (frequent, no results)
    RESULT = "result"             # Contains actual results (valuable)
    CRITICAL = "critical"         # Always important (call start/end, errors)


# ===== BACKWARD COMPATIBILITY MAPPINGS =====

# Mapping from old AgentNotificationService UpdateType to new NotificationType
LEGACY_AGENT_MAPPING: Dict[str, NotificationType] = {
    # Old UpdateType enum values → New NotificationType
    "call_start": NotificationType.STREAMING_CALL_START,
    "transcript_segment": NotificationType.STREAMING_TRANSCRIPTION_SEGMENT,
    "translation_update": NotificationType.STREAMING_TRANSLATION,
    "entity_update": NotificationType.STREAMING_ENTITIES,
    "classification_update": NotificationType.STREAMING_CLASSIFICATION,
    "qa_update": NotificationType.STREAMING_QA,
    "call_end": NotificationType.STREAMING_CALL_END,
    "call_summary": NotificationType.STREAMING_SUMMARY,
    "call_insights": NotificationType.STREAMING_INSIGHTS,
    "gpt_insights": NotificationType.POSTCALL_GPT_INSIGHTS,
    "error": NotificationType.SYSTEM_ERROR,
}

# Mapping from old NotificationManager NotificationType to new NotificationType
LEGACY_MANAGER_MAPPING: Dict[str, NotificationType] = {
    # Progress notifications
    "call_start": NotificationType.STREAMING_CALL_START,
    "transcript_segment": NotificationType.STREAMING_TRANSCRIPTION_SEGMENT,
    "translation_progress": NotificationType.STREAMING_TRANSLATION_PROGRESS,
    "processing_update": NotificationType.STREAMING_PROCESSING_UPDATE,

    # Result notifications
    "translation_complete": NotificationType.STREAMING_TRANSLATION,
    "entity_results": NotificationType.STREAMING_ENTITIES,
    "classification_results": NotificationType.STREAMING_CLASSIFICATION,
    "qa_results": NotificationType.STREAMING_QA,
    "summary_results": NotificationType.STREAMING_SUMMARY,
    "insights_results": NotificationType.STREAMING_INSIGHTS,
    "gpt_insights_results": NotificationType.POSTCALL_GPT_INSIGHTS,

    # Critical notifications
    "call_end": NotificationType.STREAMING_CALL_END,
    "processing_error": NotificationType.SYSTEM_PROCESSING_ERROR,
    "unified_insight": NotificationType.UNIFIED_INSIGHT,
}

# Mapping from old EnhancedNotificationService NotificationType to new (mostly 1:1)
LEGACY_ENHANCED_MAPPING: Dict[str, NotificationType] = {
    # Streaming
    "call_start": NotificationType.STREAMING_CALL_START,
    "transcription_update": NotificationType.STREAMING_TRANSCRIPTION,
    "translation_update": NotificationType.STREAMING_TRANSLATION,
    "entity_update": NotificationType.STREAMING_ENTITIES,
    "classification_update": NotificationType.STREAMING_CLASSIFICATION,
    "call_end_streaming": NotificationType.STREAMING_CALL_END,

    # Post-call
    "post_call_start": NotificationType.POSTCALL_START,
    "post_call_transcription": NotificationType.POSTCALL_TRANSCRIPTION,
    "post_call_translation": NotificationType.POSTCALL_TRANSLATION,
    "post_call_entities": NotificationType.POSTCALL_ENTITIES,
    "post_call_classification": NotificationType.POSTCALL_CLASSIFICATION,
    "post_call_summary": NotificationType.POSTCALL_SUMMARY,
    "post_call_qa_scoring": NotificationType.POSTCALL_QA_SCORING,
    "post_call_complete": NotificationType.POSTCALL_COMPLETE,

    # Status
    "processing_progress": NotificationType.SYSTEM_PROCESSING_PROGRESS,
    "processing_error": NotificationType.SYSTEM_PROCESSING_ERROR,
}


# ===== IMPORTANCE CLASSIFICATION =====

# Map notification types to their importance level
NOTIFICATION_IMPORTANCE: Dict[NotificationType, NotificationImportance] = {
    # Progress notifications (frequent, no results)
    NotificationType.STREAMING_TRANSCRIPTION_SEGMENT: NotificationImportance.PROGRESS,
    NotificationType.STREAMING_TRANSLATION_PROGRESS: NotificationImportance.PROGRESS,
    NotificationType.STREAMING_PROCESSING_UPDATE: NotificationImportance.PROGRESS,
    NotificationType.SYSTEM_PROCESSING_PROGRESS: NotificationImportance.PROGRESS,

    # Result notifications (contain actual results)
    NotificationType.STREAMING_TRANSCRIPTION: NotificationImportance.RESULT,
    NotificationType.STREAMING_TRANSLATION: NotificationImportance.RESULT,
    NotificationType.STREAMING_ENTITIES: NotificationImportance.RESULT,
    NotificationType.STREAMING_CLASSIFICATION: NotificationImportance.RESULT,
    NotificationType.STREAMING_QA: NotificationImportance.RESULT,
    NotificationType.STREAMING_SUMMARY: NotificationImportance.RESULT,
    NotificationType.STREAMING_INSIGHTS: NotificationImportance.RESULT,
    NotificationType.POSTCALL_TRANSCRIPTION: NotificationImportance.RESULT,
    NotificationType.POSTCALL_TRANSLATION: NotificationImportance.RESULT,
    NotificationType.POSTCALL_ENTITIES: NotificationImportance.RESULT,
    NotificationType.POSTCALL_CLASSIFICATION: NotificationImportance.RESULT,
    NotificationType.POSTCALL_SUMMARY: NotificationImportance.RESULT,
    NotificationType.POSTCALL_QA_SCORING: NotificationImportance.RESULT,
    NotificationType.POSTCALL_INSIGHTS: NotificationImportance.RESULT,
    NotificationType.POSTCALL_GPT_INSIGHTS: NotificationImportance.RESULT,
    NotificationType.UNIFIED_INSIGHT: NotificationImportance.RESULT,

    # Critical notifications (always important)
    NotificationType.STREAMING_CALL_START: NotificationImportance.CRITICAL,
    NotificationType.STREAMING_CALL_END: NotificationImportance.CRITICAL,
    NotificationType.POSTCALL_START: NotificationImportance.CRITICAL,
    NotificationType.POSTCALL_COMPLETE: NotificationImportance.CRITICAL,
    NotificationType.SYSTEM_PROCESSING_ERROR: NotificationImportance.CRITICAL,
    NotificationType.SYSTEM_ERROR: NotificationImportance.CRITICAL,
}


# ===== UTILITY FUNCTIONS =====

def migrate_notification_type(
    old_value: str,
    source: str = "enhanced"
) -> NotificationType:
    """
    Migrate an old notification type value to the new unified enum.

    Args:
        old_value: The old notification type string
        source: Which service it came from ("agent", "enhanced", "manager")

    Returns:
        The corresponding new NotificationType

    Raises:
        ValueError: If old_value is not found in the mapping
    """
    mapping = {
        "agent": LEGACY_AGENT_MAPPING,
        "enhanced": LEGACY_ENHANCED_MAPPING,
        "manager": LEGACY_MANAGER_MAPPING,
    }.get(source.lower())

    if mapping is None:
        raise ValueError(f"Unknown source: {source}")

    if old_value not in mapping:
        raise ValueError(f"Unknown notification type '{old_value}' for source '{source}'")

    return mapping[old_value]


def get_notification_importance(notification_type: NotificationType) -> NotificationImportance:
    """
    Get the importance level of a notification type.

    Args:
        notification_type: The notification type to check

    Returns:
        The importance level (PROGRESS, RESULT, or CRITICAL)

    Defaults to RESULT if not explicitly categorized.
    """
    return NOTIFICATION_IMPORTANCE.get(notification_type, NotificationImportance.RESULT)


def is_streaming_notification(notification_type: NotificationType) -> bool:
    """Check if a notification type is for streaming (real-time) updates."""
    return notification_type.value.startswith("streaming_")


def is_postcall_notification(notification_type: NotificationType) -> bool:
    """Check if a notification type is for post-call analysis."""
    return notification_type.value.startswith("postcall_")


def is_system_notification(notification_type: NotificationType) -> bool:
    """Check if a notification type is a system-level event."""
    return notification_type.value.startswith("system_")
