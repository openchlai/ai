# """
# Whisper Model Manager for dynamic model switching and translation strategy management
# Handles multiple whisper variants and coordinates with translation models
# """
# import logging
# import os
# import gc
# import torch
# from typing import Optional, Dict, Any, Tuple, List
# from datetime import datetime
# from enum import Enum

# logger = logging.getLogger(__name__)

# # class WhisperVariant(Enum):
# #     """Available Whisper model variants"""
# #     LARGE_V3 = "large_v3"          # Full model with built-in translation
# #     LARGE_TURBO = "large_turbo"    # Lighter model for transcription only

# # class TranslationStrategy(Enum):
# #     """Translation strategies"""
# #     WHISPER_BUILTIN = "whisper_builtin"    # Use Whisper's built-in translation
# #     CUSTOM_MODEL = "custom_model"          # Use separate translation model

# class WhisperModelManager:
#     """
#     Manages multiple Whisper model variants and coordinates translation strategies
#     Only one Whisper model is loaded in memory at a time
#     """
    
#     def __init__(self):
#         from ..config.settings import settings
        
#         self.settings = settings
#         # self.current_variant: Optional[WhisperVariant] = None
#         # self.current_strategy: Optional[TranslationStrategy] = None
#         self.whisper_model = settings.get_asr_model_id  # Loaded Whisper model instance
        
#         # Model paths
#         # self.variant_paths = {
#         #     WhisperVariant.LARGE_V3: settings.whisper_large_v3_path,
#         #     WhisperVariant.LARGE_TURBO: settings.whisper_large_turbo_path
#         # }
        
#         # Load initial configuration
#         self._load_initial_config()
        
#         logger.info(f"🎛️ WhisperModelManager initialized: {self.whisper_model}")
    
#     def _load_initial_config(self):
#         """Load initial configuration from settings"""
#         try:
#             # Parse variant from settings
#             variant_str = self.settings.whisper_model_variant.lower()
#             if variant_str == "large_v3":
#                 self.current_variant = WhisperVariant.LARGE_V3
#             elif variant_str == "large_turbo":
#                 self.current_variant = WhisperVariant.LARGE_TURBO
#             else:
#                 logger.warning(f"Unknown whisper variant '{variant_str}', defaulting to large_turbo")
#                 self.current_variant = WhisperVariant.LARGE_TURBO
            
#             # # Parse translation strategy
#             # strategy_str = self.settings.translation_strategy.lower()
#             # if strategy_str == "whisper_builtin":
#             #     self.current_strategy = TranslationStrategy.WHISPER_BUILTIN
#             # elif strategy_str == "custom_model":
#             #     self.current_strategy = TranslationStrategy.CUSTOM_MODEL
#             # else:
#             #     logger.warning(f"Unknown translation strategy '{strategy_str}', defaulting to custom_model")
#             #     self.current_strategy = TranslationStrategy.CUSTOM_MODEL

#             # Respect explicit translator configuration: prefer custom model when available
#             translation_backend = self.settings.translation_backend(include_translation=True)
#             if translation_backend == "hf" and self.current_strategy != TranslationStrategy.CUSTOM_MODEL:
#                 logger.info("🔁 Detected dedicated HF translation model; switching strategy to custom_model")
#                 self.current_strategy = TranslationStrategy.CUSTOM_MODEL
            
#             # Auto-upgrade to Large-V3 when whisper_builtin is configured
#             if self.current_strategy == TranslationStrategy.WHISPER_BUILTIN and self.current_variant != WhisperVariant.LARGE_V3:
#                 logger.info(f"🎯 Auto-upgrading from {self.current_variant.value} to large_v3 for built-in translation")
#                 self.current_variant = WhisperVariant.LARGE_V3
            
#             # Validate configuration combination (fallback safety)
#             if self.current_variant == WhisperVariant.LARGE_TURBO and self.current_strategy == TranslationStrategy.WHISPER_BUILTIN:
#                 logger.warning("⚠️ Invalid combination: large_turbo doesn't support built-in translation, switching to custom_model")
#                 self.current_strategy = TranslationStrategy.CUSTOM_MODEL
                
#         except Exception as e:
#             logger.error(f"❌ Failed to load whisper config: {e}")
#             # Safe defaults
#             self.current_variant = WhisperVariant.LARGE_TURBO
#             self.current_strategy = TranslationStrategy.CUSTOM_MODEL
    
#     def get_current_model_path(self) -> str:
#         """Get path to currently configured whisper model"""
#         return os.path.abspath(self.variant_paths[self.current_variant])
    
#     def is_model_loaded(self) -> bool:
#         """Check if whisper model is currently loaded"""
#         return self.whisper_model is not None and getattr(self.whisper_model, 'is_loaded', False)
    
#     def get_loaded_variant_info(self) -> Dict[str, Any]:
#         """Get standardized information about currently loaded model variant"""
        
#         info = {
#             "model_type": "whisper_variant_info",
#             "loaded": self.is_model_loaded(),
#             "load_time": None, # Not directly tracked by manager for this level
#             "device": self.whisper_model.device if self.whisper_model else None,
#             "error": self.whisper_model.error if self.whisper_model else None,
#         }

#         details = {
#             "variant": self.current_variant.value if self.current_variant else None,
#             "strategy": self.current_strategy.value if self.current_strategy else None,
#             "model_path": self.get_current_model_path(),
#             "supports_builtin_translation": self.current_variant == WhisperVariant.LARGE_V3,
#             # "translation_strategy_active": self.current_strategy.value,
#         }

#         if self.is_model_loaded():
#             details["model_info"] = self.whisper_model.get_model_info()
        
#         info["details"] = details
#         return info
    
#     async def load_whisper_model(self, force_reload: bool = False) -> bool:
#         """
#         Load the currently configured whisper model
        
#         Args:
#             force_reload: Force reload even if model is already loaded
            
#         Returns:
#             True if successful, False otherwise
#         """
#         try:
#             # Check if already loaded and no reload needed
#             if self.is_model_loaded() and not force_reload:
#                 logger.info(f"✅ Whisper model already loaded: {self.current_variant.value}")
#                 return True
            
#             # Unload existing model if any
#             await self._unload_current_model()
            
#             # Update symlink to point to current variant
#             self._update_symlink()
            
#             # Create new WhisperModel instance with specific path
#             from ..model_scripts.whisper_model import WhisperModel
            
#             model_path = self.get_current_model_path()
#             logger.info(f"🎙️ Loading Whisper {self.current_variant.value} from {model_path}")
            
#             # Enable translation for Large-V3, disable for Large-Turbo
#             enable_translation = (self.current_variant == WhisperVariant.LARGE_V3)
            
#             self.whisper_model = WhisperModel(
#                 model_path=model_path,
#                 enable_translation=enable_translation
#             )
            
#             logger.info(f"🎯 Model configuration: translation_enabled={enable_translation}")
            
#             # Load the model
#             success = self.whisper_model.load()
            
#             if success:
#                 logger.info(f"✅ Successfully loaded Whisper {self.current_variant.value}")
#                 logger.info(f"🎯 Translation strategy: {self.current_strategy.value}")
#                 return True
#             else:
#                 logger.error(f"❌ Failed to load Whisper {self.current_variant.value}")
#                 self.whisper_model = None
#                 return False
                
#         except Exception as e:
#             logger.error(f"❌ Error loading Whisper model: {e}")
#             self.whisper_model = None
#             return False
    
#     async def switch_model_variant(self, new_variant: WhisperVariant, 
#                                  new_strategy: Optional[TranslationStrategy] = None) -> bool:
#         """
#         Switch to a different Whisper model variant
        
#         Args:
#             new_variant: The whisper variant to switch to
#             new_strategy: Optional new translation strategy
            
#         Returns:
#             True if successful, False otherwise
#         """
#         try:
#             # Validate the combination
#             if new_variant == WhisperVariant.LARGE_TURBO and new_strategy == TranslationStrategy.WHISPER_BUILTIN:
#                 logger.error("❌ Invalid combination: large_turbo doesn't support built-in translation")
#                 return False
            
#             # Check if model path exists
#             new_model_path = self.variant_paths[new_variant]
#             if not os.path.exists(new_model_path):
#                 logger.error(f"❌ Model path doesn't exist: {new_model_path}")
#                 return False
            
#             logger.info(f"🔄 Switching from {self.current_variant.value} to {new_variant.value}")
            
#             # Update configuration
#             old_variant = self.current_variant
#             old_strategy = self.current_strategy
            
#             self.current_variant = new_variant
#             if new_strategy:
#                 self.current_strategy = new_strategy
            
#             # Reload the model
#             success = await self.load_whisper_model(force_reload=True)
            
#             if success:
#                 logger.info(f"✅ Successfully switched to Whisper {new_variant.value}")
#                 return True
#             else:
#                 # Rollback on failure
#                 logger.error(f"❌ Failed to switch models, rolling back")
#                 self.current_variant = old_variant
#                 self.current_strategy = old_strategy
#                 await self.load_whisper_model(force_reload=True)
#                 return False
                
#         except Exception as e:
#             logger.error(f"❌ Error switching Whisper variant: {e}")
#             return False
    
#     async def _unload_current_model(self):
#         """Unload currently loaded model to free memory"""
#         if self.whisper_model:
#             try:
#                 # Clear model references
#                 if hasattr(self.whisper_model, 'model') and self.whisper_model.model:
#                     del self.whisper_model.model
#                 if hasattr(self.whisper_model, 'processor') and self.whisper_model.processor:
#                     del self.whisper_model.processor
#                 if hasattr(self.whisper_model, 'pipe') and self.whisper_model.pipe:
#                     del self.whisper_model.pipe
                
#                 self.whisper_model = None
                
#                 # Force garbage collection
#                 gc.collect()
#                 if torch.cuda.is_available():
#                     torch.cuda.empty_cache()
                
#                 logger.info("🗑️ Unloaded previous Whisper model and cleared memory")
                
#             except Exception as e:
#                 logger.error(f"⚠️ Error during model unload: {e}")
    
#     def _update_symlink(self):
#         """Update the whisper symlink to point to current variant"""
#         try:
#             symlink_path = os.path.abspath(self.settings.whisper_active_symlink)
#             target_path = os.path.basename(self.get_current_model_path())
            
#             # Remove existing symlink
#             if os.path.islink(symlink_path):
#                 os.unlink(symlink_path)
#             elif os.path.exists(symlink_path):
#                 logger.warning(f"⚠️ {symlink_path} exists but is not a symlink, removing")
#                 os.remove(symlink_path)
            
#             # Create new symlink
#             os.symlink(target_path, symlink_path)
            
#             logger.info(f"🔗 Updated symlink: whisper -> {target_path}")
            
#         except Exception as e:
#             logger.error(f"❌ Failed to update whisper symlink: {e}")
    
#     def should_use_whisper_translation(self) -> bool:
#         """Determine if whisper should handle translation or if custom model should be used"""
#         return (
#             self.current_strategy == TranslationStrategy.WHISPER_BUILTIN and 
#             self.current_variant == WhisperVariant.LARGE_V3
#         )
    
#     def should_use_custom_translation(self) -> bool:
#         """Determine if custom translation model should be used"""
#         return self.current_strategy == TranslationStrategy.CUSTOM_MODEL
    
#     # def get_recommended_translation_strategy(self, variant: WhisperVariant) -> TranslationStrategy:
#     #     """Get recommended translation strategy for a given variant"""
#     #     if variant == WhisperVariant.LARGE_V3:
#     #         # Large-v3 can do both, prefer built-in for speed
#     #         return TranslationStrategy.WHISPER_BUILTIN
#     #     else:
#     #         # Large-turbo can only do transcription
#     #         return TranslationStrategy.CUSTOM_MODEL
    
#     def get_available_combinations(self) -> List[Dict[str, str]]:
#         """Get all valid whisper variant + translation strategy combinations"""
#         return [
#             {
#                 "variant": "large_turbo",
#                 "strategy": "custom_model", 
#                 "description": "Fast transcription + custom translation model"
#             },
#             {
#                 "variant": "large_v3",
#                 "strategy": "whisper_builtin",
#                 "description": "Whisper large-v3 transcription + built-in translation"
#             },
#             {
#                 "variant": "large_v3", 
#                 "strategy": "custom_model",
#                 "description": "Whisper large-v3 transcription + custom translation model"
#             }
#         ]
    
#     def transcribe_with_strategy(self, audio_bytes: bytes, language: str = "sw") -> Dict[str, Any]:
#         """
#         Transcribe audio with current strategy configuration
        
#         Returns:
#             Dict containing transcript and translation based on current strategy
#         """
#         if not self.is_model_loaded():
#             raise RuntimeError("No Whisper model loaded")
        
#         try:
#             start_time = datetime.now()
            
#             # Always get transcript
#             transcript = self.whisper_model.transcribe_audio_bytes(audio_bytes, language)
            
#             result = {
#                 "transcript": transcript,
#                 "translation": None,
#                 "variant_used": self.current_variant.value,
#                 "strategy_used": self.current_strategy.value,
#                 "processing_time_seconds": (datetime.now() - start_time).total_seconds()
#             }
            
#             # Handle translation based on strategy
#             if self.should_use_whisper_translation():
#                 # Use Whisper's built-in translation (large-v3 only)
#                 logger.info(f"🌐 Using Whisper built-in translation")
#                 try:
#                     # Re-process with translation task
#                     translation = self._transcribe_with_translation_task(audio_bytes, language)
#                     result["translation"] = translation
#                     result["translation_source"] = "whisper_builtin"
#                 except Exception as e:
#                     logger.error(f"❌ Whisper translation failed: {e}")
#                     result["translation_error"] = str(e)
            
#             elif self.should_use_custom_translation():
#                 # Translation will be handled by separate translation model
#                 logger.info(f"🌐 Custom translation model will handle translation")
#                 result["translation_source"] = "custom_model_pending"
#                 result["requires_custom_translation"] = True
            
#             return result
            
#         except Exception as e:
#             logger.error(f"❌ Transcription with strategy failed: {e}")
#             raise
    
#     def _transcribe_with_translation_task(self, audio_bytes: bytes, language: str) -> str:
#         """Use Whisper's built-in translation capability (large-v3 only)"""
#         if self.current_variant != WhisperVariant.LARGE_V3:
#             raise RuntimeError("Built-in translation only available with large-v3 variant")
        
#         if not self.whisper_model or not self.whisper_model.is_ready():
#             raise RuntimeError("Whisper model not loaded or not ready")
        
#         try:
#             logger.info("🌐 Using Whisper built-in translation to English")
#             # Use WhisperModel with translation task
#             result = self.whisper_model.transcribe_audio_bytes(audio_bytes, language=language, task="translate")
#             logger.info(f"✅ Whisper built-in translation completed: {len(result)} characters")
#             return result
            
#         except Exception as e:
#             logger.error(f"❌ Whisper translation failed: {e}")
#             raise
    
#     async def get_model_status(self) -> Dict[str, Any]:
#         """Get comprehensive status of whisper models and configuration"""
        
#         info = {
#             "model_type": "whisper_manager",
#             "loaded": self.is_model_loaded(),
#             "load_time": None, # Not directly tracked by manager
#             "device": self.whisper_model.device if self.whisper_model else None,
#             "error": self.whisper_model.error if self.whisper_model else None,
#         }

#         details = {
#             "current_configuration": {
#                 "variant": self.current_variant.value if self.current_variant else None,
#                 "strategy": self.current_strategy.value if self.current_strategy else None,
#                 "model_loaded": self.is_model_loaded()
#             },
#             "available_variants": [v.value for v in WhisperVariant],
#             "available_strategies": [s.value for s in TranslationStrategy],
#             "valid_combinations": self.get_available_combinations(),
#             "model_paths": {
#                 "large_v3": os.path.abspath(self.variant_paths[WhisperVariant.LARGE_V3]),
#                 "large_turbo": os.path.abspath(self.variant_paths[WhisperVariant.LARGE_TURBO]),
#                 "symlink": os.path.abspath(self.settings.whisper_active_symlink)
#             },
#             "model_status": {
#                 "large_v3_available": os.path.exists(self.variant_paths[WhisperVariant.LARGE_V3]),
#                 "large_turbo_available": os.path.exists(self.variant_paths[WhisperVariant.LARGE_TURBO]),
#                 "current_model_path": self.get_current_model_path() if self.current_variant else None
#             },
#             "loaded_model_info": self.get_loaded_variant_info(),
#             "memory_status": {
#                 "cuda_available": torch.cuda.is_available(),
#                 "cuda_memory_allocated": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0,
#                 "cuda_memory_reserved": torch.cuda.memory_reserved() if torch.cuda.is_available() else 0
#             }
#         }
#         info["details"] = details
#         return info
    
#     async def switch_configuration(self, variant: str, strategy: str) -> Tuple[bool, str]:
#         """
#         Switch whisper configuration (variant + translation strategy)
        
#         Args:
#             variant: "large_v3" or "large_turbo"
#             strategy: "whisper_builtin" or "custom_model"
            
#         Returns:
#             Tuple of (success, message)
#         """
#         try:
#             # Parse and validate inputs
#             try:
#                 new_variant = WhisperVariant(variant)
#             except ValueError:
#                 return False, f"Invalid variant: {variant}. Must be 'large_v3' or 'large_turbo'"
            
#             try:
#                 new_strategy = TranslationStrategy(strategy)
#             except ValueError:
#                 return False, f"Invalid strategy: {strategy}. Must be 'whisper_builtin' or 'custom_model'"
            
#             # Validate combination
#             if new_variant == WhisperVariant.LARGE_TURBO and new_strategy == TranslationStrategy.WHISPER_BUILTIN:
#                 return False, "Invalid combination: large_turbo doesn't support built-in translation"
            
#             # Check if model exists
#             model_path = self.variant_paths[new_variant]
#             if not os.path.exists(model_path):
#                 return False, f"Model not found: {model_path}"
            
#             # Perform the switch
#             success = await self.switch_model_variant(new_variant, new_strategy)
            
#             if success:
#                 message = f"Successfully switched to {variant} with {strategy} translation"
#                 logger.info(f"✅ {message}")
#                 return True, message
#             else:
#                 message = f"Failed to switch to {variant}"
#                 logger.error(f"❌ {message}")
#                 return False, message
                
#         except Exception as e:
#             error_msg = f"Error switching configuration: {str(e)}"
#             logger.error(f"❌ {error_msg}")
#             return False, error_msg

# # Global whisper model manager instance
# whisper_model_manager = WhisperModelManager()