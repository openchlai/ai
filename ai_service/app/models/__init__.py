"""
Data models and shared types for the AI service.
"""
from .notification_types import (
    NotificationType,
    ProcessingMode,
    NotificationStatus,
    # Backward compatibility aliases
    LEGACY_AGENT_MAPPING,
    LEGACY_MANAGER_MAPPING
)

__all__ = [
    "NotificationType",
    "ProcessingMode",
    "NotificationStatus",
    "LEGACY_AGENT_MAPPING",
    "LEGACY_MANAGER_MAPPING"
]
