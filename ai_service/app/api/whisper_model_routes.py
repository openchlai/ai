# """
# API endpoints for Whisper model management and dynamic switching
# """
# from fastapi import APIRouter, HTTPException
# from typing import Dict, Any
# from pydantic import BaseModel
# import logging
# from datetime import datetime

# from ..core.whisper_model_manager import whisper_model_manager, WhisperVariant, TranslationStrategy

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api/v1/models/whisper", tags=["Whisper Model Management"])

# # Pydantic models for requests
# class WhisperSwitchRequest(BaseModel):
#     """Request model for switching Whisper configuration"""
#     variant: str  # "large_v3" or "large_turbo"
#     strategy: str  # "whisper_builtin" or "custom_model"

# class WhisperTranscribeRequest(BaseModel):
#     """Request model for transcription with strategy"""
#     text: str
#     language: str = "sw"

# @router.get("/status")
# async def get_whisper_status():
#     """Get current Whisper model status and configuration"""
#     try:
#         status = await whisper_model_manager.get_model_status()
#         return {
#             "timestamp": datetime.now().isoformat(),
#             "whisper_status": status
#         }
#     except Exception as e:
#         logger.error(f"❌ Failed to get Whisper status: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# @router.get("/configurations")
# async def get_available_configurations():
#     """Get all available Whisper variant and translation strategy combinations"""
#     try:
#         return {
#             "available_combinations": whisper_model_manager.get_available_combinations(),
#             "current_configuration": {
#                 "variant": whisper_model_manager.current_variant.value if whisper_model_manager.current_variant else None,
#                 "strategy": whisper_model_manager.current_strategy.value if whisper_model_manager.current_strategy else None
#             },
#             "model_paths": {
#                 "large_v3": whisper_model_manager.variant_paths[WhisperVariant.LARGE_V3],
#                 "large_turbo": whisper_model_manager.variant_paths[WhisperVariant.LARGE_TURBO]
#             }
#         }
#     except Exception as e:
#         logger.error(f"❌ Failed to get configurations: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to get configurations: {str(e)}")

# @router.post("/switch")
# async def switch_whisper_configuration(request: WhisperSwitchRequest):
#     """Switch Whisper model variant and translation strategy"""
#     try:
#         logger.info(f"🔄 Switching Whisper to {request.variant} + {request.strategy}")
        
#         # Perform the switch
#         success, message = await whisper_model_manager.switch_configuration(request.variant, request.strategy)
        
#         if success:
#             return {
#                 "success": True,
#                 "message": message,
#                 "new_configuration": {
#                     "variant": whisper_model_manager.current_variant.value,
#                     "strategy": whisper_model_manager.current_strategy.value
#                 },
#                 "timestamp": datetime.now().isoformat()
#             }
#         else:
#             raise HTTPException(status_code=400, detail=message)
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Failed to switch Whisper configuration: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to switch configuration: {str(e)}")

# @router.post("/reload")
# async def reload_whisper_model():
#     """Force reload the current Whisper model (useful after manual model updates)"""
#     try:
#         logger.info("🔄 Force reloading current Whisper model")
        
#         success = await whisper_model_manager.load_whisper_model(force_reload=True)
        
#         if success:
#             return {
#                 "success": True,
#                 "message": f"Successfully reloaded Whisper {whisper_model_manager.current_variant.value}",
#                 "configuration": whisper_model_manager.get_loaded_variant_info(),
#                 "timestamp": datetime.now().isoformat()
#             }
#         else:
#             raise HTTPException(status_code=500, detail="Failed to reload Whisper model")
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Failed to reload Whisper model: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")

# # @router.get("/translation-strategy")
# # async def get_translation_strategy():
# #     """Get current translation strategy and recommendations"""
# #     try:
# #         current_variant = whisper_model_manager.current_variant
# #         current_strategy = whisper_model_manager.current_strategy
        
# #         return {
# #             "current_strategy": current_strategy.value if current_strategy else None,
# #             "current_variant": current_variant.value if current_variant else None,
# #             "uses_whisper_translation": whisper_model_manager.should_use_whisper_translation(),
# #             "uses_custom_translation": whisper_model_manager.should_use_custom_translation(),
# #             "recommended_strategy": whisper_model_manager.get_recommended_translation_strategy(current_variant).value if current_variant else None,
# #             "strategy_explanation": {
# #                 "whisper_builtin": "Use Whisper large-v3's built-in translation (faster, one model)",
# #                 "custom_model": "Use separate custom translation model (more control, supports any whisper variant)"
# #             }
# #         }
        
# #     except Exception as e:
# #         logger.error(f"❌ Failed to get translation strategy: {e}")
# #         raise HTTPException(status_code=500, detail=f"Failed to get strategy: {str(e)}")

# @router.post("/test-transcription")
# async def test_current_configuration(language: str = "sw"):
#     """Test transcription with current Whisper configuration"""
#     try:
#         if not whisper_model_manager.is_model_loaded():
#             raise HTTPException(status_code=503, detail="No Whisper model loaded")
        
#         # Create test audio data (small silent audio)
#         import numpy as np
#         import io
#         import wave
        
#         # Generate 1 second of silence at 16kHz
#         sample_rate = 16000
#         duration = 1.0
#         samples = np.zeros(int(sample_rate * duration), dtype=np.float32)
        
#         # Convert to WAV bytes
#         buffer = io.BytesIO()
#         with wave.open(buffer, 'wb') as wav_file:
#             wav_file.setnchannels(1)  # Mono
#             wav_file.setsampwidth(2)  # 16-bit
#             wav_file.setframerate(sample_rate)
#             wav_file.writeframes((samples * 32767).astype(np.int16).tobytes())
        
#         test_audio_bytes = buffer.getvalue()
        
#         # Test transcription
#         result = whisper_model_manager.transcribe_with_strategy(test_audio_bytes, language)
        
#         return {
#             "test_successful": True,
#             "configuration": {
#                 "variant": whisper_model_manager.current_variant.value,
#                 "strategy": whisper_model_manager.current_strategy.value
#             },
#             "test_result": result,
#             "timestamp": datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Transcription test failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Transcription test failed: {str(e)}")

# @router.get("/memory-usage")
# async def get_whisper_memory_usage():
#     """Get memory usage information for Whisper models"""
#     try:
#         import torch
#         import psutil
#         import os
        
#         memory_info = {
#             "system_memory": {
#                 "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
#                 "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
#                 "used_percent": psutil.virtual_memory().percent
#             },
#             "process_memory": {
#                 "current_process_mb": round(psutil.Process(os.getpid()).memory_info().rss / (1024**2), 2)
#             }
#         }
        
#         if torch.cuda.is_available():
#             memory_info["gpu_memory"] = {
#                 "allocated_mb": round(torch.cuda.memory_allocated() / (1024**2), 2),
#                 "reserved_mb": round(torch.cuda.memory_reserved() / (1024**2), 2),
#                 "total_mb": round(torch.cuda.get_device_properties(0).total_memory / (1024**2), 2)
#             }
#         else:
#             memory_info["gpu_memory"] = {"available": False}
        
#         memory_info["whisper_model_loaded"] = whisper_model_manager.is_model_loaded()
#         memory_info["current_variant"] = whisper_model_manager.current_variant.value if whisper_model_manager.current_variant else None
        
#         return memory_info
        
#     except Exception as e:
#         logger.error(f"❌ Failed to get memory usage: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to get memory info: {str(e)}")

# # Include import for datetime at the top
# from datetime import datetime