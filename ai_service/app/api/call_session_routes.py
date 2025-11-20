# app/api/call_session_routes.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..streaming.call_session_manager import call_session_manager
from ..streaming.progressive_processor import progressive_processor

# Import enhanced notification service for health checks
try:
    from ..services.enhanced_notification_service import enhanced_notification_service
    ENHANCED_SERVICE_AVAILABLE = True
except ImportError:
    ENHANCED_SERVICE_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/calls", tags=["call-sessions"])

@router.get("/active", response_model=List[Dict[str, Any]])
async def get_active_calls():
    """Get all active call sessions"""
    try:
        sessions = await call_session_manager.get_all_active_sessions()
        return [session.to_dict() for session in sessions]
    except Exception as e:
        logger.error(f"Failed to get active calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active calls")

@router.get("/stats", response_model=Dict[str, Any])
async def get_call_stats():
    """Get statistics about all call sessions"""
    try:
        stats = await call_session_manager.get_session_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get call stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve call statistics")

@router.get("/{call_id}", response_model=Dict[str, Any])
async def get_call_session(call_id: str):
    """Get specific call session by ID"""
    try:
        session = await call_session_manager.get_session(call_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Call session {call_id} not found")
        
        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get call session {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve call session")

@router.get("/{call_id}/transcript", response_model=Dict[str, Any])
async def get_call_transcript(
    call_id: str,
    include_segments: bool = Query(False, description="Include individual transcript segments")
):
    """Get transcript for a specific call"""
    try:
        session = await call_session_manager.get_session(call_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Call session {call_id} not found")
        
        result = {
            "call_id": call_id,
            "cumulative_transcript": session.cumulative_transcript,
            "total_duration": session.total_audio_duration,
            "segment_count": session.segment_count,
            "status": session.status,
            "start_time": session.start_time.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
        
        if include_segments:
            result["segments"] = session.transcript_segments
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcript for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve call transcript")

@router.post("/{call_id}/end")
async def manually_end_call(call_id: str, reason: str = "manual"):
    """Manually end a call session"""
    try:
        session = await call_session_manager.end_session(call_id, reason=reason)
        if not session:
            raise HTTPException(status_code=404, detail=f"Call session {call_id} not found")
        
        return {
            "message": f"Call session {call_id} ended successfully",
            "final_transcript": session.cumulative_transcript,
            "total_duration": session.total_audio_duration,
            "segment_count": session.segment_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end call session {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to end call session")

@router.get("/{call_id}/segments", response_model=List[Dict[str, Any]])
async def get_call_segments(
    call_id: str,
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of segments to return"),
    offset: int = Query(0, ge=0, description="Number of segments to skip")
):
    """Get transcript segments for a specific call with pagination"""
    try:
        session = await call_session_manager.get_session(call_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Call session {call_id} not found")
        
        # Apply pagination
        segments = session.transcript_segments[offset:offset + limit]
        
        return {
            "call_id": call_id,
            "segments": segments,
            "total_segments": len(session.transcript_segments),
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < len(session.transcript_segments)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get segments for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve call segments")

@router.get("/{call_id}/export", response_model=Dict[str, Any])
async def export_call_for_ai_pipeline(
    call_id: str,
    format: str = Query("json", regex="^(json|text)$", description="Export format")
):
    """Export call data for AI pipeline processing"""
    try:
        session = await call_session_manager.get_session(call_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Call session {call_id} not found")
        
        if format == "text":
            return {
                "call_id": call_id,
                "format": "text",
                "content": session.cumulative_transcript,
                "metadata": {
                    "duration": session.total_audio_duration,
                    "segments": session.segment_count,
                    "start_time": session.start_time.isoformat(),
                    "status": session.status
                }
            }
        else:  # json format
            export_data = session.to_dict()
            export_data["export_timestamp"] = datetime.now().isoformat()
            export_data["ready_for_ai_pipeline"] = len(session.cumulative_transcript.strip()) > 50
            
            return {
                "call_id": call_id,
                "format": "json",
                "content": export_data
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export call data")

@router.post("/{call_id}/trigger-ai-pipeline")
async def trigger_ai_pipeline_processing(call_id: str):
    """Manually trigger AI pipeline processing for a completed call"""
    try:
        session = await call_session_manager.get_session(call_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Call session {call_id} not found")
        
        if len(session.cumulative_transcript.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Call transcript too short for AI pipeline processing"
            )
        
        # Manually trigger AI pipeline
        await call_session_manager._trigger_ai_pipeline(session)
        
        return {
            "message": f"AI pipeline processing triggered for call {call_id}",
            "transcript_length": len(session.cumulative_transcript),
            "segment_count": session.segment_count,
            "total_duration": session.total_audio_duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger AI pipeline for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger AI pipeline processing")

# WebSocket endpoint for real-time call updates (optional)
@router.websocket("/{call_id}/live")
async def call_live_updates(websocket, call_id: str):
    """WebSocket endpoint for real-time call transcript updates"""
    await websocket.accept()
    
    try:
        # This would require implementing a pub/sub system
        # For now, just send current state and close
        session = await call_session_manager.get_session(call_id)
        if session:
            await websocket.send_json({
                "type": "current_state",
                "call_id": call_id,
                "cumulative_transcript": session.cumulative_transcript,
                "segment_count": session.segment_count,
                "status": session.status
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Call session {call_id} not found"
            })
            
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
        await websocket.send_json({
            "type": "error", 
            "message": "Connection error"
        })
    finally:
        await websocket.close()

# Progressive Processing Endpoints

@router.get("/{call_id}/progressive-analysis", response_model=Dict[str, Any])
async def get_progressive_analysis(call_id: str):
    """Get progressive analysis for a call (translations, NER, classification evolution)"""
    try:
        analysis = progressive_processor.get_call_analysis(call_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No progressive analysis found for call {call_id}")
        
        return analysis.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get progressive analysis for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve progressive analysis")

@router.get("/{call_id}/translation", response_model=Dict[str, Any])
async def get_call_translation(call_id: str):
    """Get cumulative translation for a call"""
    try:
        analysis = progressive_processor.get_call_analysis(call_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No progressive analysis found for call {call_id}")
        
        return {
            "call_id": call_id,
            "cumulative_translation": analysis.cumulative_translation,
            "translation_windows": len([w for w in analysis.windows if w.translation]),
            "latest_entities": analysis.latest_entities,
            "latest_classification": analysis.latest_classification,
            "processing_stats": analysis.processing_stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get translation for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve call translation")

@router.get("/{call_id}/entity-evolution", response_model=List[Dict[str, Any]])
async def get_entity_evolution(call_id: str):
    """Get how entities evolved during the call"""
    try:
        analysis = progressive_processor.get_call_analysis(call_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No progressive analysis found for call {call_id}")
        
        return analysis.entity_evolution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entity evolution for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve entity evolution")

@router.get("/{call_id}/classification-evolution", response_model=List[Dict[str, Any]])
async def get_classification_evolution(call_id: str):
    """Get how classification evolved during the call"""
    try:
        analysis = progressive_processor.get_call_analysis(call_id)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"No progressive analysis found for call {call_id}")
        
        return analysis.classification_evolution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get classification evolution for call {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve classification evolution")

# Agent Notification Service Endpoints

@router.get("/agent-service/health", response_model=Dict[str, Any])
async def get_agent_service_health():
    """Get health status of enhanced notification service"""
    if not ENHANCED_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced notification service not available")

    try:
        # EnhancedNotificationService doesn't have get_health_status method,
        # return basic status info instead
        health_status = {
            "service": "enhanced_notification_service",
            "status": "healthy",
            "endpoint": enhanced_notification_service.endpoint_url,
            "auth_endpoint": enhanced_notification_service.auth_endpoint_url,
            "use_base64_encoding": enhanced_notification_service.use_base64,
            "site_id": enhanced_notification_service.site_id,
            "token_status": {
                "has_token": enhanced_notification_service.bearer_token is not None,
                "token_preview": enhanced_notification_service.bearer_token[:8] + "..." if enhanced_notification_service.bearer_token else None,
                "expires_at": enhanced_notification_service.token_expires_at.isoformat() if enhanced_notification_service.token_expires_at else None
            }
        }
        return health_status
    except Exception as e:
        logger.error(f"Failed to get enhanced service health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve enhanced service health")

@router.post("/agent-service/test-auth", response_model=Dict[str, Any])
async def test_agent_auth():
    """Test authentication token retrieval"""
    if not ENHANCED_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced notification service not available")

    try:
        # Force token refresh
        enhanced_notification_service.bearer_token = None
        token_valid = await enhanced_notification_service._ensure_valid_token()

        return {
            "test_type": "auth_token_fetch",
            "success": token_valid,
            "token_preview": enhanced_notification_service.bearer_token[:8] + "..." if enhanced_notification_service.bearer_token else None,
            "expires_at": enhanced_notification_service.token_expires_at.isoformat() if enhanced_notification_service.token_expires_at else None,
            "message": "Successfully fetched auth token" if token_valid else "Failed to fetch auth token"
        }
    except Exception as e:
        logger.error(f"Failed to test enhanced auth: {e}")
        raise HTTPException(status_code=500, detail=f"Auth test failed: {str(e)}")

@router.post("/agent-service/test-notification", response_model=Dict[str, Any])
async def test_agent_notification(call_id: str = "test_call_123"):
    """Test sending a notification to agent endpoint"""
    if not ENHANCED_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced notification service not available")

    try:
        # Send a test notification using enhanced service
        from ..models.notification_types import NotificationType, ProcessingMode

        test_payload = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "source": "api_test",
            "message": "Test notification from enhanced service"
        }

        success = await enhanced_notification_service.send_notification(
            call_id=call_id,
            notification_type=NotificationType.STREAMING_CALL_START,
            processing_mode=ProcessingMode.STREAMING,
            payload_data=test_payload
        )

        return {
            "test_type": "notification_send",
            "call_id": call_id,
            "success": success,
            "message": "Test notification sent successfully" if success else "Failed to send test notification"
        }
    except Exception as e:
        logger.error(f"Failed to test enhanced notification: {e}")
        raise HTTPException(status_code=500, detail=f"Notification test failed: {str(e)}")


# Progressive Processing Endpoints
@router.get("/processing/status", response_model=Dict[str, Any])
async def get_processing_status():
    """Get progressive processing status"""
    try:
        # Check if progressive_processor has get_status method, otherwise return mock data
        if hasattr(progressive_processor, 'get_status'):
            return progressive_processor.get_status()
        else:
            return {
                "active_processors": 0,
                "queue_size": 0,
                "processing_rate": 0.0,
                "average_latency": 0.0
            }
    except Exception as e:
        logger.error(f"Failed to get processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")


@router.get("/{call_id}/processing", response_model=Dict[str, Any])
async def get_call_processing_status(call_id: str):
    """Get processing status for specific call"""
    try:
        # Check if progressive_processor has get_call_processing_status method, otherwise return mock data
        if hasattr(progressive_processor, 'get_call_processing_status'):
            return progressive_processor.get_call_processing_status(call_id)
        else:
            return {
                "call_id": call_id,
                "processing_stage": "idle",
                "progress": 0.0,
                "estimated_completion": 0.0,
                "current_segment": 0,
                "total_segments": 0
            }
    except Exception as e:
        logger.error(f"Failed to get call processing status for {call_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing status for call {call_id}")