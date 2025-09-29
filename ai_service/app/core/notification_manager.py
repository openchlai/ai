"""
Notification Manager for selective agent notification filtering and management
"""
import logging
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationMode(Enum):
    """Notification filtering modes"""
    ALL = "all"                    # Send all notifications (progress, intermediate, results)  
    RESULTS_ONLY = "results_only"  # Only send notifications with actual results
    CRITICAL_ONLY = "critical_only" # Only call start/end and final results
    DISABLED = "disabled"          # No notifications sent

class NotificationType(Enum):
    """Types of notifications categorized by importance"""
    # Progress notifications (frequent, no results)
    CALL_START = "call_start"
    TRANSCRIPT_SEGMENT = "transcript_segment"
    TRANSLATION_PROGRESS = "translation_progress" 
    PROCESSING_UPDATE = "processing_update"
    
    # Result notifications (contain actual results)
    TRANSLATION_COMPLETE = "translation_complete"
    ENTITY_RESULTS = "entity_results"
    CLASSIFICATION_RESULTS = "classification_results"
    QA_RESULTS = "qa_results"
    SUMMARY_RESULTS = "summary_results"
    INSIGHTS_RESULTS = "insights_results"
    GPT_INSIGHTS_RESULTS = "gpt_insights_results"
    
    # Critical notifications (always important)
    CALL_END = "call_end"
    PROCESSING_ERROR = "processing_error"
    UNIFIED_INSIGHT = "unified_insight"

class NotificationManager:
    """
    Manages selective notification filtering based on configured modes
    """
    
    def __init__(self):
        from ..config.settings import settings
        
        self.settings = settings
        self.current_mode = self._parse_notification_mode(settings.notification_mode)
        self.notifications_enabled = settings.enable_agent_notifications
        
        # Import notification service
        try:
            from ..services.agent_notification_service import agent_notification_service
            self.notification_service = agent_notification_service
            self.service_available = True
        except ImportError:
            self.notification_service = None
            self.service_available = False
            logger.warning("⚠️ Agent notification service not available")
        
        # Statistics
        self.stats = {
            "total_considered": 0,
            "total_sent": 0,
            "total_filtered": 0,
            "by_type": {}
        }
        
        logger.info(f"🔔 NotificationManager initialized: mode={self.current_mode.value}, enabled={self.notifications_enabled}")
    
    def _parse_notification_mode(self, mode_str: str) -> NotificationMode:
        """Parse notification mode string to enum"""
        try:
            return NotificationMode(mode_str.lower())
        except ValueError:
            logger.warning(f"⚠️ Invalid notification mode '{mode_str}', defaulting to results_only")
            return NotificationMode.RESULTS_ONLY
    
    def should_send_notification(self, notification_type: NotificationType, has_results: bool = False) -> bool:
        """
        Determine if a notification should be sent based on current mode
        
        Args:
            notification_type: Type of notification
            has_results: Whether the notification contains actual results
            
        Returns:
            True if notification should be sent
        """
        self.stats["total_considered"] += 1
        
        # Global disable check
        if not self.notifications_enabled or not self.service_available:
            self._record_filtered(notification_type, "globally_disabled")
            return False
        
        # Mode-specific filtering
        if self.current_mode == NotificationMode.DISABLED:
            self._record_filtered(notification_type, "mode_disabled")
            return False
        
        elif self.current_mode == NotificationMode.ALL:
            # Send everything
            self._record_sent(notification_type)
            return True
        
        elif self.current_mode == NotificationMode.RESULTS_ONLY:
            # Send only if it has results or is critical
            if self._is_critical_notification(notification_type) or has_results:
                self._record_sent(notification_type)
                return True
            else:
                self._record_filtered(notification_type, "no_results")
                return False
        
        elif self.current_mode == NotificationMode.CRITICAL_ONLY:
            # Send only critical notifications
            if self._is_critical_notification(notification_type):
                self._record_sent(notification_type)
                return True
            else:
                self._record_filtered(notification_type, "not_critical")
                return False
        
        # Default: don't send
        self._record_filtered(notification_type, "unknown_mode")
        return False
    
    def _is_critical_notification(self, notification_type: NotificationType) -> bool:
        """Check if notification type is considered critical"""
        critical_types = {
            NotificationType.CALL_START,
            NotificationType.CALL_END,
            NotificationType.PROCESSING_ERROR,
            NotificationType.UNIFIED_INSIGHT
        }
        return notification_type in critical_types
    
    def _is_result_notification(self, notification_type: NotificationType) -> bool:
        """Check if notification type typically contains results"""
        result_types = {
            NotificationType.TRANSLATION_COMPLETE,
            NotificationType.ENTITY_RESULTS,
            NotificationType.CLASSIFICATION_RESULTS,
            NotificationType.QA_RESULTS,
            NotificationType.SUMMARY_RESULTS,
            NotificationType.INSIGHTS_RESULTS,
            NotificationType.GPT_INSIGHTS_RESULTS,
            NotificationType.UNIFIED_INSIGHT
        }
        return notification_type in result_types
    
    def _record_sent(self, notification_type: NotificationType):
        """Record that a notification was sent"""
        self.stats["total_sent"] += 1
        type_name = notification_type.value
        if type_name not in self.stats["by_type"]:
            self.stats["by_type"][type_name] = {"sent": 0, "filtered": 0}
        self.stats["by_type"][type_name]["sent"] += 1
    
    def _record_filtered(self, notification_type: NotificationType, reason: str):
        """Record that a notification was filtered"""
        self.stats["total_filtered"] += 1
        type_name = notification_type.value
        if type_name not in self.stats["by_type"]:
            self.stats["by_type"][type_name] = {"sent": 0, "filtered": 0}
        self.stats["by_type"][type_name]["filtered"] += 1
        
        logger.debug(f"🚫 Filtered {notification_type.value}: {reason}")
    
    async def send_notification_if_allowed(self, notification_type: NotificationType, 
                                         call_id: str, payload: Dict[str, Any], 
                                         has_results: bool = None) -> bool:
        """
        Send notification only if allowed by current filtering mode
        
        Args:
            notification_type: Type of notification
            call_id: Call ID 
            payload: Notification payload
            has_results: Override for result detection (auto-detect if None)
            
        Returns:
            True if notification was sent
        """
        
        # Auto-detect if notification has results
        if has_results is None:
            has_results = self._detect_results_in_payload(payload)
        
        # Check if notification should be sent
        if not self.should_send_notification(notification_type, has_results):
            return False
        
        # Send notification
        try:
            # Map notification types to service methods
            success = await self._dispatch_notification(notification_type, call_id, payload)
            
            if success:
                logger.debug(f"✅ Sent {notification_type.value} notification for call {call_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to send {notification_type.value} notification for call {call_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending {notification_type.value} notification for call {call_id}: {e}")
            return False
    
    def _detect_results_in_payload(self, payload: Dict[str, Any]) -> bool:
        """Auto-detect if payload contains actual results"""
        result_indicators = [
            "translation", "summary", "insights", "entities", "classification", 
            "qa_scores", "qa_analysis", "gpt_insights", "results", "analysis"
        ]
        
        # Check if payload contains any result fields with meaningful content
        for key in result_indicators:
            if key in payload:
                value = payload[key]
                if value and (
                    (isinstance(value, str) and len(value.strip()) > 10) or
                    (isinstance(value, dict) and len(value) > 0) or
                    (isinstance(value, list) and len(value) > 0)
                ):
                    return True
        
        return False
    
    async def _dispatch_notification(self, notification_type: NotificationType, 
                                   call_id: str, payload: Dict[str, Any]) -> bool:
        """Dispatch notification to appropriate service method"""
        
        if not self.service_available:
            return False
        
        try:
            # Map notification types to service methods
            if notification_type == NotificationType.CALL_START:
                connection_info = payload.get("connection_info", {})
                return await self.notification_service.send_call_start(call_id, connection_info)
            
            elif notification_type == NotificationType.CALL_END:
                reason = payload.get("reason", "completed")
                stats = payload.get("stats", {})
                return await self.notification_service.send_call_end(call_id, reason, stats)
            
            elif notification_type == NotificationType.TRANSCRIPT_SEGMENT:
                segment = payload.get("segment", {})
                cumulative = payload.get("cumulative_transcript", "")
                return await self.notification_service.send_transcript_segment(call_id, segment, cumulative)
            
            elif notification_type == NotificationType.QA_RESULTS:
                qa_scores = payload.get("qa_scores", {})
                processing_info = payload.get("processing_info", {})
                return await self.notification_service.send_qa_update(call_id, qa_scores, processing_info)
            
            elif notification_type == NotificationType.SUMMARY_RESULTS:
                summary = payload.get("summary", "")
                analysis = payload.get("analysis", {})
                return await self.notification_service.send_call_summary(call_id, summary, analysis)
            
            elif notification_type == NotificationType.INSIGHTS_RESULTS:
                insights = payload.get("insights", {})
                return await self.notification_service.send_call_insights(call_id, insights)
            
            elif notification_type == NotificationType.GPT_INSIGHTS_RESULTS:
                gpt_insights = payload.get("gpt_insights", {})
                return await self.notification_service.send_gpt_insights(call_id, gpt_insights)
            
            elif notification_type == NotificationType.UNIFIED_INSIGHT:
                pipeline_result = payload.get("pipeline_result", {})
                audio_info = payload.get("audio_quality_info", {})
                metadata = payload.get("processing_metadata", {})
                return await self.notification_service.send_unified_insight(call_id, pipeline_result, audio_info, metadata)
            
            else:
                # Generic notification dispatch
                from ..services.agent_notification_service import UpdateType
                update_type = UpdateType(notification_type.value) if hasattr(UpdateType, notification_type.value.upper()) else UpdateType.ERROR
                return await self.notification_service._send_notification(call_id, update_type, payload)
        
        except Exception as e:
            logger.error(f"❌ Error dispatching {notification_type.value} notification: {e}")
            return False
    
    def update_mode(self, new_mode: str) -> bool:
        """Update notification mode at runtime"""
        try:
            old_mode = self.current_mode
            self.current_mode = self._parse_notification_mode(new_mode)
            
            logger.info(f"🔔 Notification mode updated: {old_mode.value} → {self.current_mode.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update notification mode: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current notification manager status"""
        return {
            "enabled": self.notifications_enabled,
            "mode": self.current_mode.value,
            "service_available": self.service_available,
            "statistics": self.stats,
            "available_modes": [mode.value for mode in NotificationMode],
            "configuration": {
                "endpoint_url": self.settings.notification_endpoint_url,
                "timeout": self.settings.notification_request_timeout,
                "max_retries": self.settings.notification_max_retries
            }
        }
    
    def reset_statistics(self):
        """Reset notification statistics"""
        self.stats = {
            "total_considered": 0,
            "total_sent": 0,
            "total_filtered": 0,
            "by_type": {}
        }
        logger.info("📊 Notification statistics reset")

# Global notification manager instance
notification_manager = NotificationManager()