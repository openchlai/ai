"""
API endpoints for processing mode configuration and management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from ..core.processing_strategy_manager import processing_strategy_manager
from ..core.processing_modes import CallProcessingMode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/processing", tags=["Processing Mode"])

# Pydantic models for request/response
class ProcessingModeUpdateRequest(BaseModel):
    """Request model for updating processing mode configuration"""
    default_mode: Optional[str] = None
    realtime_config: Optional[Dict[str, Any]] = None
    postcall_config: Optional[Dict[str, Any]] = None

class CallProcessingRequest(BaseModel):
    """Request model for call-specific processing mode override"""
    call_id: str
    mode_override: Optional[str] = None
    call_context: Optional[Dict[str, Any]] = None

@router.get("/status")
async def get_processing_status():
    """Get current processing mode configuration and system capabilities"""
    try:
        capabilities = processing_strategy_manager.get_system_capabilities()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system_capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"❌ Failed to get processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")

@router.get("/modes")
async def get_available_modes():
    """Get list of available processing modes"""
    try:
        return {
            "available_modes": [
                {
                    "name": mode.value,
                    "description": _get_mode_description(mode)
                }
                for mode in CallProcessingMode
            ],
            "current_default": processing_strategy_manager.config.default_mode.value
        }
    except Exception as e:
        logger.error(f"❌ Failed to get available modes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available modes")

@router.post("/configure")
async def update_processing_configuration(request: ProcessingModeUpdateRequest):
    """Update processing mode configuration at runtime"""
    try:
        # Convert request to dictionary
        config_updates = {}
        
        if request.default_mode:
            config_updates["default_mode"] = request.default_mode
            
        if request.realtime_config:
            config_updates["realtime_config"] = request.realtime_config
            
        if request.postcall_config:
            config_updates["postcall_config"] = request.postcall_config
        
        # Apply configuration updates
        success = processing_strategy_manager.update_mode_configuration(config_updates)
        
        if success:
            logger.info(f"✅ Processing configuration updated successfully")
            return {
                "success": True,
                "message": "Processing configuration updated successfully",
                "updated_config": processing_strategy_manager.get_system_capabilities()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update configuration")
            
    except Exception as e:
        logger.error(f"❌ Failed to update processing configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@router.post("/plan")
async def create_call_processing_plan(request: CallProcessingRequest):
    """Create a processing plan for a specific call"""
    try:
        # Build call context
        call_context = {
            "call_id": request.call_id,
            **(request.call_context or {})
        }

        # Add mode override if provided
        if request.mode_override:
            call_context["mode_override"] = request.mode_override

        # Create processing plan with sensitive data removed
        processing_plan = processing_strategy_manager.get_sanitized_processing_plan(call_context)

        logger.info(f"📋 Created processing plan for call {request.call_id}: {processing_plan['processing_mode']}")

        return {
            "success": True,
            "processing_plan": processing_plan
        }

    except Exception as e:
        logger.error(f"❌ Failed to create processing plan for {request.call_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create processing plan")

@router.get("/statistics")
async def get_processing_statistics():
    """Get processing mode usage statistics"""
    try:
        stats = processing_strategy_manager.mode_usage_stats
        total_calls = sum(stats.values())
        
        # Calculate percentages
        percentages = {}
        if total_calls > 0:
            for mode, count in stats.items():
                percentages[mode] = round((count / total_calls) * 100, 2)
        
        return {
            "total_calls_processed": total_calls,
            "mode_usage_counts": stats,
            "mode_usage_percentages": percentages,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get processing statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.post("/test-mode/{mode}")
async def test_processing_mode(mode: str, call_id: Optional[str] = None):
    """Test a specific processing mode with a sample call"""
    try:
        # Validate mode
        valid_modes = [m.value for m in CallProcessingMode]
        if mode not in valid_modes:
            raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {valid_modes}")
        
        # Create test call context
        test_call_id = call_id or f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_context = {
            "call_id": test_call_id,
            "mode_override": mode,
            "duration_seconds": 120,
            "language": "sw",
            "transcript": "This is a test transcript for mode validation",
            "test_mode": True
        }
        
        # Create processing plan with sensitive data removed
        processing_plan = processing_strategy_manager.get_sanitized_processing_plan(test_context)

        # Validate the plan matches the requested mode
        if processing_plan["processing_mode"] != mode:
            logger.warning(f"⚠️ Mode override may have been adjusted by adaptive rules")

        return {
            "success": True,
            "test_call_id": test_call_id,
            "requested_mode": mode,
            "actual_mode": processing_plan["processing_mode"],
            "processing_plan": processing_plan,
            "test_completed": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to test processing mode {mode}: {e}")
        raise HTTPException(status_code=500, detail="Failed to test mode")

def _get_mode_description(mode: CallProcessingMode) -> str:
    """Get human-readable description for processing modes"""
    descriptions = {
        CallProcessingMode.REALTIME_ONLY: "Real-time transcription and progressive analysis only, no post-call processing",
        CallProcessingMode.POSTCALL_ONLY: "No real-time processing, comprehensive post-call analysis with audio download",
        CallProcessingMode.HYBRID: "Both real-time progressive analysis and enhanced post-call processing",
        CallProcessingMode.ADAPTIVE: "Dynamic mode selection based on call characteristics and content"
    }
    return descriptions.get(mode, "Unknown processing mode")

# Include the router in main app
from datetime import datetime