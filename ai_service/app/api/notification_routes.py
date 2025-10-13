"""
API endpoints for notification management and configuration
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import logging
from datetime import datetime

from ..core.notification_manager import notification_manager, NotificationMode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification Management"])

# Pydantic models for requests
class NotificationModeUpdateRequest(BaseModel):
    """Request model for updating notification mode"""
    mode: str  # all, results_only, critical_only, disabled

class NotificationTestRequest(BaseModel):
    """Request model for testing notifications"""
    call_id: str = "test_call_123"
    notification_type: str = "call_start"
    include_results: bool = True

@router.get("/status")
async def get_notification_status():
    """Get current notification system status and configuration"""
    try:
        status = notification_manager.get_status()
        return {
            "timestamp": datetime.now().isoformat(),
            "notification_system": status
        }
    except Exception as e:
        logger.error(f"❌ Failed to get notification status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/modes")
async def get_available_modes():
    """Get available notification modes and their descriptions"""
    try:
        return {
            "available_modes": [
                {
                    "name": "all",
                    "description": "Send all notifications (progress, intermediate, results)"
                },
                {
                    "name": "results_only", 
                    "description": "Only send notifications with actual results (default)"
                },
                {
                    "name": "critical_only",
                    "description": "Only send call start/end and final results"
                },
                {
                    "name": "disabled",
                    "description": "No notifications sent"
                }
            ],
            "current_mode": notification_manager.current_mode.value,
            "mode_explanations": {
                "all": "🔔 All updates: Every transcript segment, progress update, and result",
                "results_only": "📊 Results only: Translation, entities, QA scores, summaries, insights", 
                "critical_only": "🚨 Critical only: Call start/end and final processing results",
                "disabled": "🔇 Disabled: No notifications sent to agent system"
            }
        }
    except Exception as e:
        logger.error(f"❌ Failed to get notification modes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get modes: {str(e)}")

@router.post("/configure")
async def update_notification_mode(request: NotificationModeUpdateRequest):
    """Update notification mode at runtime"""
    try:
        old_mode = notification_manager.current_mode.value
        success = notification_manager.update_mode(request.mode)
        
        if success:
            return {
                "success": True,
                "message": f"Notification mode updated from '{old_mode}' to '{request.mode}'",
                "previous_mode": old_mode,
                "new_mode": request.mode,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to update mode to '{request.mode}'")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update notification mode: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update mode: {str(e)}")

@router.get("/statistics")
async def get_notification_statistics():
    """Get notification statistics and filtering metrics"""
    try:
        stats = notification_manager.stats
        
        # Calculate filtering efficiency
        total = stats["total_considered"] 
        sent = stats["total_sent"]
        filtered = stats["total_filtered"]
        
        efficiency = {
            "total_considered": total,
            "total_sent": sent,
            "total_filtered": filtered,
            "filter_rate_percent": round((filtered / total * 100) if total > 0 else 0, 2),
            "send_rate_percent": round((sent / total * 100) if total > 0 else 0, 2)
        }
        
        return {
            "current_mode": notification_manager.current_mode.value,
            "summary": efficiency,
            "by_notification_type": stats["by_type"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get notification statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/statistics/reset")
async def reset_notification_statistics():
    """Reset notification statistics"""
    try:
        notification_manager.reset_statistics()
        return {
            "success": True,
            "message": "Notification statistics reset",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to reset statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset statistics: {str(e)}")

@router.post("/test")
async def test_notification_filtering(request: NotificationTestRequest):
    """Test notification filtering with different scenarios"""
    try:
        from ..core.notification_manager import NotificationType
        
        # Try to parse notification type
        try:
            notification_type = NotificationType(request.notification_type.lower())
        except ValueError:
            available_types = [t.value for t in NotificationType]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid notification type. Available: {available_types}"
            )
        
        # Test if notification would be sent
        would_send = notification_manager.should_send_notification(
            notification_type, 
            has_results=request.include_results
        )
        
        # Create test payload
        test_payload = {
            "test_notification": True,
            "timestamp": datetime.now().isoformat()
        }
        
        if request.include_results:
            test_payload["test_results"] = {
                "sample_data": "This is test result data",
                "score": 85.5
            }
        
        result = {
            "test_scenario": {
                "call_id": request.call_id,
                "notification_type": request.notification_type,
                "include_results": request.include_results,
                "current_mode": notification_manager.current_mode.value
            },
            "filtering_result": {
                "would_send": would_send,
                "reason": "allowed" if would_send else "filtered_by_current_mode"
            },
            "mode_behavior": {
                "all": True,  # ALL mode would send everything
                "results_only": would_send if request.include_results else notification_manager._is_critical_notification(notification_type),
                "critical_only": notification_manager._is_critical_notification(notification_type),
                "disabled": False  # DISABLED mode sends nothing
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to test notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test notification: {str(e)}")

@router.get("/types")
async def get_notification_types():
    """Get all available notification types and their categories"""
    try:
        from ..core.notification_manager import NotificationType
        
        # Categorize notification types
        progress_types = [
            NotificationType.CALL_START,
            NotificationType.TRANSCRIPT_SEGMENT, 
            NotificationType.TRANSLATION_PROGRESS,
            NotificationType.PROCESSING_UPDATE
        ]
        
        result_types = [
            NotificationType.TRANSLATION_COMPLETE,
            NotificationType.ENTITY_RESULTS,
            NotificationType.CLASSIFICATION_RESULTS,
            NotificationType.QA_RESULTS,
            NotificationType.SUMMARY_RESULTS,
            NotificationType.INSIGHTS_RESULTS,
            NotificationType.GPT_INSIGHTS_RESULTS
        ]
        
        critical_types = [
            NotificationType.CALL_END,
            NotificationType.PROCESSING_ERROR,
            NotificationType.UNIFIED_INSIGHT
        ]
        
        return {
            "notification_types": {
                "progress_notifications": [t.value for t in progress_types],
                "result_notifications": [t.value for t in result_types], 
                "critical_notifications": [t.value for t in critical_types]
            },
            "filtering_behavior": {
                "all": "Sends all types",
                "results_only": "Sends result_notifications + critical_notifications",
                "critical_only": "Sends critical_notifications only",
                "disabled": "Sends no notifications"
            },
            "total_types": len(list(NotificationType))
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get notification types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get types: {str(e)}")