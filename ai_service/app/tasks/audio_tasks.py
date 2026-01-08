# app/tasks/audio_tasks.py (Updated)
import json
import os
import socket
from celery import current_task
from celery.signals import worker_init
import numpy as np
from ..celery_app import celery_app
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from ..config.settings import redis_task_client


logger = logging.getLogger(__name__)

# Global model loader for Celery worker
worker_model_loader = None

# ============================================================================
# TEMPORARY DEMO WORKAROUND: Cached spacy model
# This is a temporary fix for demo purposes - DO NOT COMMIT
# ============================================================================
_cached_spacy_nlp = None

# ============================================================================
# TEMPORARY DEMO WORKAROUND: Ollama API Translation
# This is a temporary fix for demo purposes - DO NOT COMMIT
# ============================================================================
def _translate_via_ollama_api(text: str, timeout: int = 60) -> Optional[str]:
    """
    Call Ollama API for translation (TEMPORARY DEMO WORKAROUND)

    Args:
        text: Swahili text to translate to English
        timeout: Request timeout in seconds

    Returns:
        Translated English text, or None if API call fails
    """
    try:
        import requests

        # Ollama API endpoint (local network)
        api_url = "http://192.168.8.18:11434/api/generate"

        # Prepare the prompt (optimized for accurate dialogue translation)
        prompt = f"""You are a professional Swahili-to-English translator for child protection services. Translate the following Swahili conversation accurately.

CRITICAL TRANSLATION REQUIREMENTS:
1. Preserve EXACT meaning - do not change who said what or relationships mentioned
2. Keep all numbers, ages, names, and locations accurate
3. Maintain the dialogue structure if present
4. Translate LITERALLY - do not interpret or summarize
5. Keep family relationships exact (mume=husband, baba=father, etc.)
6. Output ONLY the English translation with no notes, labels, or explanations

SWAHILI TEXT:
{text}

ENGLISH TRANSLATION (direct, accurate, no commentary):"""

        # Prepare the payload
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }

        logger.info(f"🌐 Calling Ollama API for translation (text length: {len(text)} chars)")

        # Make the API call
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=timeout
        )

        # Check if request was successful
        response.raise_for_status()

        # Parse the response
        result = response.json()

        # Extract the translation from the 'response' field
        translation = result.get("response", "").strip()

        if translation:
            # Clean up common preambles that Mistral might add
            preambles_to_remove = [
                "My translation of the Swahili text is:",
                "The English translation is:",
                "English translation:",
                "Translation:",
                "Here is the translation:",
                "Here's the translation:",
                "The translation is:",
            ]

            for preamble in preambles_to_remove:
                if translation.startswith(preamble):
                    translation = translation[len(preamble):].strip()
                    logger.info(f"🧹 Removed preamble: '{preamble}'")
                    break

            # Clean up notes/commentary that Mistral might add at the end
            note_markers = [
                "\nNote:",
                "\n\nNote:",
                "\nWelcome Note:",
                "\n\nWelcome Note:",
                "\nAdditional context:",
                "\nExplanation:",
                "\nContext:",
            ]

            for marker in note_markers:
                if marker in translation:
                    # Remove everything from the marker onwards
                    translation = translation.split(marker)[0].strip()
                    logger.info(f"🧹 Removed note/commentary starting with: '{marker}'")
                    break

            logger.info(f"✅ Ollama API translation successful ({len(translation)} chars)")
            return translation
        else:
            logger.warning("⚠️ Ollama API returned empty response")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"❌ Ollama API timeout after {timeout}s")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("❌ Ollama API connection error (server unreachable)")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ollama API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error calling Ollama API: {e}")
        return None
# ============================================================================
# END TEMPORARY DEMO WORKAROUND
# ============================================================================

def _extract_entities_via_spacy_lg(text: str, flat: bool = False) -> Dict[str, list]:
    """
    Extract named entities using spacy en_core_web_lg model (TEMPORARY DEMO WORKAROUND)

    Args:
        text: Text to extract entities from
        flat: If False, returns grouped dict (like original NER model)

    Returns:
        Dictionary of entity_type -> list of entity texts
        Format matches the original NER model when flat=False
    """
    global _cached_spacy_nlp

    try:
        import spacy

        # Load the large spacy model (cached)
        if _cached_spacy_nlp is None:
            logger.info("🔍 Loading spacy en_core_web_lg for NER (first time)...")
            _cached_spacy_nlp = spacy.load("en_core_web_lg")
            logger.info("✅ Spacy model loaded and cached")
        else:
            logger.debug("Using cached spacy en_core_web_lg model")

        # Process the text
        doc = _cached_spacy_nlp(text.strip())

        # Group entities by type (matching original NER model format)
        entity_dict = {}
        for ent in doc.ents:
            if ent.label_ not in entity_dict:
                entity_dict[ent.label_] = []
            entity_dict[ent.label_].append(ent.text)

        logger.info(f"✅ Spacy NER extracted {len(entity_dict)} entity types with {sum(len(v) for v in entity_dict.values())} total entities")

        return entity_dict

    except ImportError:
        logger.error("❌ Spacy not available in environment")
        return None
    except OSError as e:
        logger.error(f"❌ Spacy model en_core_web_lg not found: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Spacy NER extraction failed: {e}")
        return None
# ============================================================================
# END TEMPORARY DEMO WORKAROUND
# ============================================================================

@worker_init.connect
def debug_worker_init(**kwargs):
    """Debug worker initialization paths"""
    logger.info("🔍 DEBUG: Worker initialization starting...")
    
    try:
        # Debug current working directory
        cwd = os.getcwd()
        logger.info(f"🔍 Worker CWD: {cwd}")
        
        # Debug settings import
        from ..config.settings import settings
        logger.info(f"🔍 Worker models_path: {settings.models_path}")
        logger.info(f"🔍 Worker models exists: {os.path.exists(settings.models_path)}")
        
        if os.path.exists(settings.models_path):
            contents = os.listdir(settings.models_path)
            logger.info(f"🔍 Worker models contents: {contents}")
        else:
            logger.error(f"🔍 Worker models directory NOT FOUND: {settings.models_path}")
            
            # Check if we can find it relatively
            for possible_path in ["./models", "../models", "models"]:
                if os.path.exists(possible_path):
                    logger.info(f"🔍 Found models at relative path: {os.path.abspath(possible_path)}")
                    
    except Exception as e:
        logger.error(f"🔍 Debug failed: {e}")
        
@worker_init.connect
def init_worker(**kwargs):
    """Initialize models and connections when Celery worker starts"""
    global worker_model_loader
    
    logger.info("🔄 Initializing Celery worker...")
    
    try:
        # Step 1: Initialize Redis connections
        logger.info("📡 Initializing Redis connections...")
        from ..config.settings import initialize_redis
        redis_success = initialize_redis()
        if not redis_success:
            logger.warning("⚠️ Redis initialization failed, but continuing...")
        
        # Step 2: Debug worker context
        logger.info("🔍 DEBUG: Worker context analysis...")
        cwd = os.getcwd()
        logger.info(f"🔍 Worker CWD: {cwd}")
        
        # Step 3: Initialize settings and paths
        logger.info("📁 Initializing paths...")
        from ..config.settings import settings
        models_path = settings.initialize_paths()
        logger.info(f"🔍 Worker models_path: {models_path}")
        logger.info(f"🔍 Worker models exists: {os.path.exists(models_path)}")
        
        if os.path.exists(models_path):
            contents = os.listdir(models_path)
            logger.info(f"🔍 Worker models contents: {contents}")
        else:
            logger.error(f"🔍 Worker models directory NOT FOUND: {models_path}")
            
            # Check for alternative paths
            for possible_path in ["./models", "../models", "models", "/app/models"]:
                abs_path = os.path.abspath(possible_path)
                if os.path.exists(abs_path):
                    logger.info(f"🔍 Found models at alternative path: {abs_path}")
                    logger.info(f"🔍 Contents: {os.listdir(abs_path)}")
            
            # Don't fail completely - let model loading handle missing paths
            logger.warning("⚠️ Models directory not found, but continuing with model loading...")
        
        # Step 4: Create model loader instance
        logger.info("🤖 Creating ModelLoader instance...")
        from ..model_scripts.model_loader import ModelLoader
        worker_model_loader = ModelLoader()
        
        # Step 5: Load models asynchronously (converted to sync for Celery)
        logger.info("📦 Loading models in Celery worker...")
        import asyncio
        
        # Create new event loop for this worker process
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Load all models
        try:
            loop.run_until_complete(worker_model_loader.load_all_models())
        finally:
            # Don't close the loop - it might be needed later
            pass
        
        # Step 6: Verify model loading results
        ready_models = worker_model_loader.get_ready_models()
        implementable_models = worker_model_loader.get_implementable_models()
        blocked_models = worker_model_loader.get_blocked_models()
        failed_models = worker_model_loader.get_failed_models()
        
        logger.info("📊 Model loading summary:")
        logger.info(f"✅ Ready models: {ready_models}")
        logger.info(f"🔄 Implementable models: {implementable_models}")
        logger.info(f"🚫 Blocked models: {blocked_models}")
        logger.info(f"❌ Failed models: {failed_models}")
        
        # Step 7: Store worker information in Redis (optional)
        try:
            from ..config.settings import redis_task_client
            if redis_task_client:
                worker_info = {
                    "worker_id": os.getpid(),
                    "models_loaded": len(ready_models),
                    "ready_models": ready_models,
                    "startup_time": datetime.now().isoformat(),
                    "models_path": models_path
                }
                redis_task_client.hset(
                    "worker_info", 
                    f"worker_{os.getpid()}", 
                    json.dumps(worker_info)
                )
                logger.info(f"📋 Worker info stored in Redis for PID {os.getpid()}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to store worker info in Redis: {e}")
        
        # Step 8: Final status
        if len(ready_models) > 0:
            logger.info(f"✅ Worker initialization completed successfully!")
            logger.info(f"🚀 Worker ready to process tasks with {len(ready_models)} models")
        elif len(implementable_models) > 0:
            logger.warning(f"⚠️ Worker initialized but some models need dependencies")
            logger.info(f"🔧 Implementable models: {implementable_models}")
            logger.info(f"🚫 Missing dependencies for: {blocked_models}")
        else:
            logger.error(f"❌ Worker initialized but no models are ready!")
            logger.error(f"🚫 Blocked models: {blocked_models}")
            logger.error(f"❌ Failed models: {failed_models}")
            
            # Don't raise exception - let the worker start anyway
            logger.warning("⚠️ Worker will start but audio processing will fail until models are fixed")
        
    except Exception as e:
        logger.error(f"❌ Critical error during worker initialization: {e}")
        logger.exception("Full exception traceback:")
        
        # Store error information
        worker_model_loader = None
        
        # Try to store error info in Redis
        try:
            from ..config.settings import redis_task_client
            if redis_task_client:
                error_info = {
                    "worker_id": os.getpid(),
                    "error": str(e),
                    "error_time": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
                redis_task_client.hset(
                    "worker_errors",
                    f"worker_{os.getpid()}",
                    json.dumps(error_info)
                )
        except:
            pass  # Don't fail on Redis error logging
        
        # Don't raise the exception - let Celery start the worker anyway
        # The tasks will fail gracefully with "models not loaded" errors
        logger.warning("⚠️ Worker starting in degraded mode - tasks will fail until models are fixed")


def get_worker_models():
    """Get the worker's model loader instance"""
    global worker_model_loader
    return worker_model_loader


def get_worker_status():
    """Get detailed worker status for debugging"""
    global worker_model_loader
    
    if worker_model_loader is None:
        return {
            "status": "not_initialized",
            "error": "Worker models not loaded",
            "ready_models": []
        }
    
    try:
        return {
            "status": "ready",
            "ready_models": worker_model_loader.get_ready_models(),
            "implementable_models": worker_model_loader.get_implementable_models(),
            "blocked_models": worker_model_loader.get_blocked_models(),
            "failed_models": worker_model_loader.get_failed_models(),
            "worker_pid": os.getpid(),
            "models_path": worker_model_loader.models_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "worker_pid": os.getpid()
        }

def _send_pipeline_notifications(filename: str, result: Dict[str, Any], task_id: str):
    """
    Send notifications to the agent system after pipeline processing completes.
    This runs synchronously in the Celery worker.
    """
    try:
        # Extract call_id from filename (e.g., "call_1763027988.14_20251113_125949.wav16")
        call_id = None
        if filename and "call_" in filename:
            parts = filename.replace("call_", "").split("_")
            if parts:
                call_id = parts[0]  # e.g., "1763027988.14"

        if not call_id:
            logger.warning(f"Could not extract call_id from filename: {filename}")
            return

        logger.info(f"📤 Sending pipeline notifications for call {call_id}")

        # Import notification service
        from ..services.enhanced_notification_service import (
            notification_service as enhanced_notification_service,
            NotificationType,
            ProcessingMode,
            NotificationStatus
        )

        # Determine processing mode (default to post_call if not specified)
        processing_mode_value = "post_call"  # Default

        # Create async loop for sending notifications
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async def send_notifications():
            """Send all post-call notifications"""

            # 1. Send transcription notification
            if result.get('transcript'):
                await enhanced_notification_service.send_notification(
                    call_id=call_id,
                    notification_type=NotificationType.POST_CALL_TRANSCRIPTION,
                    processing_mode=ProcessingMode(processing_mode_value),
                    payload_data={
                        "transcript": result['transcript'],
                        "language": result.get('audio_info', {}).get('language_specified', 'sw'),
                        "transcript_length": len(result['transcript'])
                    }
                )
                logger.info(f"✅ Sent transcription notification for {call_id}")

            # 2. Send translation notification
            if result.get('translation'):
                await enhanced_notification_service.send_notification(
                    call_id=call_id,
                    notification_type=NotificationType.POST_CALL_TRANSLATION,
                    processing_mode=ProcessingMode(processing_mode_value),
                    payload_data={
                        "translation": result['translation'],
                        "source_language": "sw",
                        "target_language": "en",
                        "translation_length": len(result['translation'])
                    }
                )
                logger.info(f"✅ Sent translation notification for {call_id}")

            # 3. Send entities notification
            if result.get('entities'):
                await enhanced_notification_service.send_notification(
                    call_id=call_id,
                    notification_type=NotificationType.POST_CALL_ENTITIES,
                    processing_mode=ProcessingMode(processing_mode_value),
                    payload_data={
                        "entities": result['entities'],
                        "entities_count": len(result['entities'])
                    }
                )
                logger.info(f"✅ Sent entities notification for {call_id}")

            # 4. Send classification notification
            if result.get('classification'):
                await enhanced_notification_service.send_notification(
                    call_id=call_id,
                    notification_type=NotificationType.POST_CALL_CLASSIFICATION,
                    processing_mode=ProcessingMode(processing_mode_value),
                    payload_data={
                        "classification": result['classification']
                    }
                )
                logger.info(f"✅ Sent classification notification for {call_id}")

            # 5. Send QA scoring notification
            if result.get('qa_scores'):
                await enhanced_notification_service.send_notification(
                    call_id=call_id,
                    notification_type=NotificationType.POST_CALL_QA_SCORING,
                    processing_mode=ProcessingMode(processing_mode_value),
                    payload_data={
                        "qa_scores": result['qa_scores']
                    }
                )
                logger.info(f"✅ Sent QA scoring notification for {call_id}")

            # 6. Send summary notification
            if result.get('summary'):
                await enhanced_notification_service.send_notification(
                    call_id=call_id,
                    notification_type=NotificationType.POST_CALL_SUMMARY,
                    processing_mode=ProcessingMode(processing_mode_value),
                    payload_data={
                        "summary": result['summary'],
                        "insights": result.get('insights')
                    }
                )
                logger.info(f"✅ Sent summary notification for {call_id}")

            # 7. Send final completion notification
            await enhanced_notification_service.send_notification(
                call_id=call_id,
                notification_type=NotificationType.POST_CALL_COMPLETE,
                processing_mode=ProcessingMode(processing_mode_value),
                payload_data={
                    "processing_time": result.get('pipeline_info', {}).get('total_time', 0),
                    "models_used": result.get('pipeline_info', {}).get('models_used', []),
                    "status": "completed"
                },
                status=NotificationStatus.SUCCESS
            )
            logger.info(f"✅ Sent completion notification for {call_id}")

        # Run the async function
        if loop.is_running():
            # If event loop is already running (shouldn't happen in Celery worker)
            asyncio.create_task(send_notifications())
        else:
            # Run until complete
            loop.run_until_complete(send_notifications())

        logger.info(f"📤 All notifications sent successfully for call {call_id}")

    except Exception as e:
        logger.error(f"Failed to send pipeline notifications: {e}", exc_info=True)

@celery_app.task(bind=True, name="process_audio_task")
def process_audio_task(self, audio_bytes, filename, language=None, include_translation=True, include_insights=True, processing_mode=None):
    """Simplified error handling to avoid serialization issues"""
    
    # Store basic task info in Redis (not complex objects)
    task_info = {
        "task_id": self.request.id,
        "filename": filename,
        "started": datetime.now().isoformat(),
        "status": "processing"
    }
    
    try:
        redis_task_client.hset("active_audio_tasks", self.request.id, json.dumps(task_info))
    except Exception:
        pass  # Don't fail if Redis logging fails
    
    try:
        # MINIMAL state updates - only basic progress
        self.update_state(state="PROCESSING", meta={"progress": 10, "step": "starting"})
        
        # Get worker models
        models = get_worker_models()
        if not models:
            # SIMPLE error - no complex objects
            raise RuntimeError("Models not loaded in worker")
        
        # Process the audio
        result = _process_audio_sync_worker(
            self, models, audio_bytes, filename, language, 
            include_translation, include_insights
        )
        
        # Clean up Redis
        try:
            redis_task_client.hdel("active_audio_tasks", self.request.id)
        except Exception:
            pass
        
        # Return simple result - no complex nested objects
        return {
            "status": "completed",
            "filename": filename,
            "result": result  # Make sure this is JSON-serializable
        }
        
    except Exception as e:
        logger.error(f"Audio processing failed: {e}")
        
        # Clean up Redis
        try:
            redis_task_client.hdel("active_audio_tasks", self.request.id)
        except Exception:
            pass
        
        # SIMPLE error handling - no complex state updates
        error_msg = str(e)[:500]  # Limit error message length
        
        # Let Celery handle the failure automatically
        raise RuntimeError(error_msg)

def _process_audio_sync_worker(
    task_instance,
    models,  # Use worker models instead of global model_loader
    audio_bytes: bytes,
    filename: str,
    language: Optional[str],
    include_translation: bool,
    threshold: float = 0.5,
    return_raw: bool = False,
    include_insights: bool = True
) -> Dict[str, Any]:
    """
    Synchronous audio processing using worker models with Redis streaming
    """
    start_time = datetime.now()
    processing_steps = {}
    task_id = task_instance.request.id
    
    # Check if this is pre-transcribed text data
    transcript = None
    is_pretranscribed = False
    try:
        # Validate audio_bytes first
        if audio_bytes is None:
            raise ValueError("Audio bytes cannot be None - check if audio data is being passed correctly to the task")
        
        # Try to decode as JSON to check for pre-transcribed flag
        data_str = audio_bytes.decode('utf-8')
        transcript_data = json.loads(data_str)
        if isinstance(transcript_data, dict) and transcript_data.get('is_pretranscribed'):
            transcript = transcript_data.get('transcript', '')
            is_pretranscribed = True
            language = transcript_data.get('language', language)
            logger.info(f"🎯 Processing pre-transcribed text: {len(transcript)} characters")
    except (UnicodeDecodeError, json.JSONDecodeError):
        # Not pre-transcribed data, continue with normal audio processing
        pass
    
    # Initialize streaming (sync wrapper for async streaming service)
    import asyncio
    
    def publish_update(step, progress, message=None, partial_result=None, metadata=None):
        """Sync wrapper to publish streaming updates"""
        try:
            # Use synchronous Redis client for Celery worker compatibility
            import redis
            import json
            from datetime import datetime
            from ..config.settings import get_redis_url
            
            # Create synchronous Redis client
            redis_client = redis.from_url(get_redis_url(), decode_responses=True)
            
            # Build update message
            update = {
                "task_id": task_id,
                "step": step,
                "progress": progress,
                "timestamp": datetime.now().isoformat(),
                "message": message or f"Processing: {step}"
            }
            
            if partial_result:
                update["partial_result"] = partial_result
            
            if metadata:
                update["metadata"] = metadata
            
            # Publish to Redis channel
            channel = f"audio_stream:{task_id}"
            subscribers = redis_client.publish(channel, json.dumps(update))
            
            if subscribers > 0:
                logger.debug(f"📡 Published {step} update for task {task_id} to {subscribers} subscribers")
            
            redis_client.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to publish update for {step}: {e}")
    
    # Publish initial start
    publish_update("started", 5, f"Starting audio processing for {filename}")
    
    # Determine processing strategy BEFORE any processing
    from ..core.whisper_model_manager import whisper_model_manager
    should_use_whisper_translation = whisper_model_manager.should_use_whisper_translation() and include_translation
    
    # Initialize variables
    translation = None
    transcript = None
    
    # Step 1: Audio Processing (Transcription OR Direct Translation)
    if should_use_whisper_translation and not is_pretranscribed:
        # Use Whisper built-in translation - skip transcription, get English directly
        task_instance.update_state(
            state="PROCESSING", 
            meta={"step": "translation", "progress": 10}
        )
        
        publish_update("translation", 10, "Starting Whisper built-in translation...")
        logger.info("🌐 Using Whisper built-in translation (no intermediate transcription)")
        
        step_start = datetime.now()
        
        whisper_model = models.models.get("whisper")
        if not whisper_model:
            publish_update("translation_error", 10, "Whisper model not available")
            raise RuntimeError("Whisper model not available in worker")
        
        # Direct translation with task="translate"
        translation = whisper_model.transcribe_audio_bytes(audio_bytes, language=language, task="translate")
        transcript = None  # No transcript in translation mode
        
        translation_duration = (datetime.now() - step_start).total_seconds()
        
        # Publish translation result
        publish_update(
            "translation_complete",
            40,
            "Whisper built-in translation completed", 
            partial_result={"translation": translation, "is_final": True},
            metadata={"duration": translation_duration}
        )
        
        processing_steps["translation"] = {
            "duration": translation_duration,
            "status": "completed",
            "method": "whisper_builtin",
            "model": whisper_model_manager.current_variant.value,
            "output_length": len(translation)
        }
        
        # No transcription step in translation mode
        processing_steps["transcription"] = {
            "duration": 0,
            "status": "skipped",
            "reason": "direct_translation_mode",
            "output_length": 0
        }
        transcription_duration = 0
        
    else:
        # Standard transcription mode
        task_instance.update_state(
            state="PROCESSING",
            meta={"step": "transcription", "progress": 10}
        )
        
        step_start = datetime.now()
        
        if is_pretranscribed:
            # Skip transcription for pre-transcribed text
            publish_update("transcription", 30, "Using pre-transcribed text...")
            transcription_duration = 0.01  # Minimal time for pre-transcribed
            logger.info(f"✅ Using existing transcript: {len(transcript)} characters")
        else:
            # Normal audio transcription
            publish_update("transcription", 10, "Starting audio transcription...")
            
            whisper_model = models.models.get("whisper")
            if not whisper_model:
                publish_update("transcription_error", 10, "Whisper model not available")
                raise RuntimeError("Whisper model not available in worker")
            
            # Check if model supports streaming transcription
            if hasattr(whisper_model, 'transcribe_streaming'):
                # Stream partial transcription results
                transcript = ""
                for partial_transcript, progress_pct in whisper_model.transcribe_streaming(audio_bytes, language=language):
                    transcript = partial_transcript
                    stream_progress = 10 + int(progress_pct * 0.2)  # 10-30% range
                    publish_update(
                        "transcription", 
                        stream_progress, 
                        f"Transcribing... ({progress_pct:.1f}%)",
                        partial_result={"transcript": transcript, "is_final": False}
                    )
            else:
                # Fallback to regular transcription with task="transcribe"
                transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language, task="transcribe")
            
            # Calculate transcription duration for normal processing
            transcription_duration = (datetime.now() - step_start).total_seconds()
        
        # Publish final transcription
        publish_update(
            "transcription_complete", 
            30, 
            "Transcription completed",
            partial_result={"transcript": transcript, "is_final": True},
            metadata={"duration": transcription_duration}
        )
        
        processing_steps["transcription"] = {
            "duration": transcription_duration,
            "status": "completed",
            "output_length": len(transcript)
        }
    
    # Step 2: Translation (if enabled and not already done by Whisper)
    if include_translation and not should_use_whisper_translation:
        # Only do separate translation if we didn't already get it from Whisper
        task_instance.update_state(
            state="PROCESSING",
            meta={"step": "translation", "progress": 35}
        )
        
        step_start = datetime.now()
        should_use_custom_translation = whisper_model_manager.should_use_custom_translation()
        
        if should_use_custom_translation:
            # Use custom translation model
            publish_update("translation", 35, "Starting custom model translation...")
            
            try:
                translator_model = models.models.get("translator")
                if not translator_model:
                    publish_update("translation_error", 35, "Translator model not available")
                    raise RuntimeError("Translator model not available")
                
                # ============================================================
                # TEMPORARY DEMO WORKAROUND: Try Ollama API first
                # ============================================================
                translation = None
                translation_method = "unknown"

                # Attempt 1: Ollama API (DEMO WORKAROUND)
                try:
                    publish_update("translation", 37, "Trying Ollama API translation...")
                    translation = _translate_via_ollama_api(transcript)

                    if translation:
                        translation_method = "ollama_api"
                        logger.info(f"✅ Using Ollama API translation ({len(translation)} chars)")
                    else:
                        logger.warning("⚠️ Ollama API returned None, falling back to custom translator")
                except Exception as ollama_error:
                    logger.warning(f"⚠️ Ollama API error: {ollama_error}, falling back to custom translator")

                # Attempt 2: Fall back to original custom translation model if Ollama failed
                if translation is None:
                    logger.info("🔄 Falling back to custom translation model...")
                    publish_update("translation", 38, "Using custom translation model...")

                    # Check if model supports streaming translation
                    if hasattr(translator_model, 'translate_streaming'):
                        # Stream partial translation results
                        translation = ""
                        for partial_translation, progress_pct in translator_model.translate_streaming(transcript):
                            translation = partial_translation
                            stream_progress = 35 + int(progress_pct * 0.15)  # 35-50% range
                            publish_update(
                                "translation",
                                stream_progress,
                                f"Translating... ({progress_pct:.1f}%)",
                                partial_result={"translation": translation, "is_final": False}
                            )
                        translation_method = "custom_model_streaming"
                    else:
                        # Fallback to regular translation
                        translation = translator_model.translate(transcript)
                        translation_method = "custom_model"
                # ============================================================
                # END TEMPORARY DEMO WORKAROUND
                # ============================================================

                processing_steps["translation"] = {
                    "duration": (datetime.now() - step_start).total_seconds(),
                    "status": "completed",
                    "method": translation_method,  # Will show "ollama_api" or "custom_model"
                    "output_length": len(translation) if translation else 0
                }
                
            except Exception as e:
                logger.error(f"❌ Custom translation failed: {e}")
                translation = None
                processing_steps["translation"] = {
                    "duration": (datetime.now() - step_start).total_seconds(),
                    "status": "failed",
                    "method": "custom_model",
                    "error": str(e)
                }
        
        # Publish final translation result (if any translation was successful)
        if translation:
            translation_duration = (datetime.now() - step_start).total_seconds()
            publish_update(
                "translation_complete", 
                50, 
                "Translation completed",
                partial_result={"translation": translation, "is_final": True},
                metadata={"duration": translation_duration}
            )
            
            # Run QA analysis immediately after translation since translation is the input for QA
            if translation and translation.strip():
                try:
                    publish_update("qa_analysis", 52, "Running QA analysis on translation...")
                    qa_start = datetime.now()
                    
                    qa_score_model = models.models.get("all_qa_distilbert_v1")
                    if qa_score_model:
                        qa_score = qa_score_model.predict(translation, threshold=threshold, return_raw=return_raw)
                        qa_duration = (datetime.now() - qa_start).total_seconds()
                        
                        # Send QA update notification to agent immediately
                        try:
                            from ..services.agent_notification_service import agent_notification_service
                            # Extract call_id from filename or use task_id as fallback
                            call_id = filename.replace('.wav', '').replace('.mp3', '') if filename else task_id
                            processing_info = {
                                "duration": qa_duration,
                                "model_used": "all_qa_distilbert_v1",
                                "threshold": threshold,
                                "input_source": "translated_text",
                                "input_length": len(translation)
                            }
                            # Run async notification in event loop for Celery worker
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # Event loop is running, create task
                                    asyncio.create_task(
                                        # Commented out to reduce notification noise - handled by notification manager
                                        # agent_notification_service.send_qa_update(call_id, qa_score, processing_info)
                                    )
                                else:
                                    # No running loop, run directly
                                    loop.run_until_complete(
                                        # Commented out to reduce notification noise - handled by notification manager
                                        # agent_notification_service.send_qa_update(call_id, qa_score, processing_info)
                                    )
                            except RuntimeError:
                                # No event loop exists, create one
                                asyncio.run(
                                    # Commented out to reduce notification noise - handled by notification manager
                                    # agent_notification_service.send_qa_update(call_id, qa_score, processing_info)
                                )
                            logger.info(f"📤 Sent QA update notification for call {call_id} after translation")
                            publish_update("qa_complete", 55, "QA analysis completed and sent to agent")
                        except Exception as notify_error:
                            logger.error(f"❌ Failed to send QA notification for call {call_id}: {notify_error}")
                    else:
                        logger.warning("QA model not available for immediate analysis")
                except Exception as qa_error:
                    logger.error(f"❌ QA analysis failed after translation: {qa_error}")
        else:
            # Translation not requested
            logger.info("ℹ️ Translation skipped (not requested)")
            processing_steps["translation"] = {"status": "skipped"}
    
    # Step 3: NLP Processing
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "nlp_analysis", "progress": 55}
    )
    publish_update("nlp_analysis", 55, "Starting NLP analysis...")
    
    nlp_text = translation if translation else transcript
    nlp_source = "translated_text" if translation else "original_transcript"
    
    # NER
    publish_update("ner", 60, "Extracting named entities...")
    step_start = datetime.now()
    try:
        # ============================================================
        # TEMPORARY DEMO WORKAROUND: Try Spacy large model first
        # ============================================================
        entities = None
        ner_method = "unknown"

        # Attempt 1: Spacy en_core_web_lg (DEMO WORKAROUND)
        try:
            publish_update("ner", 61, "Trying spacy en_core_web_lg for NER...")
            entities = _extract_entities_via_spacy_lg(nlp_text, flat=False)

            if entities is not None:
                ner_method = "spacy_lg"
                logger.info(f"✅ Using spacy NER ({len(entities)} entity types)")
            else:
                logger.warning("⚠️ Spacy NER returned None, falling back to original NER model")
        except Exception as spacy_error:
            logger.warning(f"⚠️ Spacy NER error: {spacy_error}, falling back to original NER model")

        # Attempt 2: Fall back to original NER model if spacy failed
        if entities is None:
            logger.info("🔄 Falling back to original NER model...")
            publish_update("ner", 62, "Using original NER model...")

            ner_model = models.models.get("ner")
            if not ner_model:
                publish_update("ner_error", 60, "NER model not available")
                raise RuntimeError("NER model not available")
            entities = ner_model.extract_entities(nlp_text, flat=False)
            ner_method = "original_ner_model"
        # ============================================================
        # END TEMPORARY DEMO WORKAROUND
        # ============================================================

        ner_duration = (datetime.now() - step_start).total_seconds()
        publish_update(
            "ner_complete",
            65,
            f"Named entity extraction completed - found {len(entities)} entity types",
            partial_result={"entities": entities},
            metadata={"duration": ner_duration, "method": ner_method}
        )

        ner_status = {
            "result": entities,
            "duration": ner_duration,
            "status": "completed",
            "method": ner_method  # Track which method was used
        }
    except Exception as e:
        ner_duration = (datetime.now() - step_start).total_seconds()
        publish_update("ner_error", 60, f"NER failed: {str(e)}")
        ner_status = {
            "result": {},
            "duration": ner_duration,
            "status": "failed",
            "error": str(e)
        }
    
    # Classification
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "classification", "progress": 70}
    )
    publish_update("classification", 70, "Classifying content...")
    
    step_start = datetime.now()
    try:
        classifier_model = models.models.get("classifier_model")
        if not classifier_model:
            publish_update("classification_error", 70, "Classifier model not available")
            raise RuntimeError("Classifier model not available")
        classification = classifier_model.classify(nlp_text)
        
        classification_duration = (datetime.now() - step_start).total_seconds()
        publish_update(
            "classification_complete", 
            75, 
            f"Classification completed - category: {classification.get('main_category', 'unknown')}",
            partial_result={"classification": classification},
            metadata={"duration": classification_duration}
        )
        
        classifier_status = {
            "result": classification,
            "duration": classification_duration,
            "status": "completed"
        }
    except Exception as e:
        classification_duration = (datetime.now() - step_start).total_seconds()
        publish_update("classification_error", 70, f"Classification failed: {str(e)}")
        classifier_status = {
            "result": {},
            "duration": classification_duration,
            "status": "failed",
            "error": str(e)
        }
    
    # Summarization
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "summarization", "progress": 80}
    )
    publish_update("summarization", 80, "Generating summary...")
    
    step_start = datetime.now()
    try:
        summarizer_model = models.models.get("summarizer")
        if not summarizer_model:
            publish_update("summarization_error", 80, "Summarizer model not available")
            raise RuntimeError("Summarizer model not available")
        summary = summarizer_model.summarize(nlp_text)
        
        summarization_duration = (datetime.now() - step_start).total_seconds()
        publish_update(
            "summarization_complete", 
            85, 
            f"Summary generated ({len(summary)} characters)",
            partial_result={"summary": summary},
            metadata={"duration": summarization_duration}
        )
        
        summary_status = {
            "result": summary,
            "duration": summarization_duration,
            "status": "completed"
        }
    except Exception as e:
        summarization_duration = (datetime.now() - step_start).total_seconds()
        publish_update("summarization_error", 80, f"Summarization failed: {str(e)}")
        summary_status = {
            "result": "",
            "duration": summarization_duration,
            "status": "failed",
            "error": str(e)
        }  
 
    # QA Scoring
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "qa_scoring", "progress": 90}
    )
    publish_update("qa_scoring", 90, "Running quality assurance evaluation...")

    step_start = datetime.now()
    try:
        # ← FIXED: Import QA model directly (same as standalone QA endpoint)
        from ..model_scripts.qa_model import qa_model
        
        if not qa_model.is_ready():
            raise RuntimeError("QA model not ready")
        
        qa_score = qa_model.predict(nlp_text, threshold=threshold, return_raw=return_raw)

        qa_duration = (datetime.now() - step_start).total_seconds()
        
        publish_update(
            "qa_scoring_complete", 
            92, 
            "Quality assurance evaluation completed",
            partial_result={"qa_scores": qa_score},
            metadata={"duration": qa_duration}
        )
        
        logger.info(f"✅ QA Scoring completed in {qa_duration:.3f}s")
        
        qa_status = {
            "result": qa_score,
            "duration": qa_duration,
            "status": "completed"
        }

    except Exception as e:
        qa_duration = (datetime.now() - step_start).total_seconds()
        publish_update("qa_scoring_error", 90, f"QA scoring failed: {str(e)}")
        logger.error(f"❌ QA scoring failed: {e}")
        
        qa_status = {
            "result": {},
            "duration": qa_duration,
            "status": "failed",
            "error": str(e)
        }

    # Step 4: Insights (if enabled)
    insights = {}
    if include_insights:
        task_instance.update_state(
            state="PROCESSING",
            meta={"step": "insights", "progress": 90}
        )
        publish_update("insights", 90, "Generating insights...")
        
        # Generate insights (simplified version)
        entities = ner_status["result"]
        classification = classifier_status["result"]
        summary = summary_status["result"]
        qa_scores = qa_status["result"] if "result" in qa_status else {}
      
      
        insights = _generate_insights(transcript, translation, entities, classification, summary, qa_scores)
        logger.info(f"Generated insights: {insights}")

         
        publish_update(
            "insights_complete", 
            95, 
            "Insights generated successfully",
            partial_result={"insights": insights}
        )
    
    # Final result
    total_processing_time = (datetime.now() - start_time).total_seconds()
    
    result = {
        "audio_info": {
            "filename": filename,
            "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
            "language_specified": language,
            "processing_time": total_processing_time
        },
        "transcript": transcript,
        "translation": translation,
        "nlp_processing_info": {
            "text_used_for_nlp": nlp_source,
            "nlp_text_length": len(nlp_text)
        },
        "entities": ner_status["result"],
        "classification": classifier_status["result"],
        "qa_scores": qa_status["result"] if "result" in qa_status else {},

        "summary": summary_status["result"],
        "insights": insights if include_insights else None,
        "processing_steps": {
            "transcription": processing_steps["transcription"],
            "translation": processing_steps.get("translation"),
            "ner": {
                "duration": ner_status["duration"],
                "status": ner_status["status"],
                "entities_found": len(ner_status["result"]) if ner_status["result"] else 0
            },
            "classification": {
                "duration": classifier_status["duration"],
                "status": classifier_status["status"],
                "confidence": classifier_status["result"].get("confidence", 0) if classifier_status["result"] else 0
            },

            "qa_scoring": {  
                "duration": qa_status["duration"],
                "status": qa_status["status"],
                "evaluations_count": len(qa_status["result"]) if qa_status["result"] else 0
            },
            "summarization": {
                "duration": summary_status["duration"],
                "status": summary_status["status"],
                "summary_length": len(summary_status["result"]) if summary_status["result"] else 0
            }
        },
        "pipeline_info": {
            "total_time": total_processing_time,
            "models_used": ["whisper"] + (["translator"] if include_translation else []) + ["ner", "classifier", "summarizer", "all_qa_distilbert_v1"],
            "text_flow": f"transcript → {nlp_source} → nlp_models",
            "timestamp": datetime.now().isoformat(),
            "processed_by": "celery_worker"
        }
    }
    
    # Publish final result
    publish_update(
        "completed",
        100,
        f"Audio processing completed in {total_processing_time:.2f}s",
        partial_result=result,
        metadata={"total_duration": total_processing_time}
    )

    # Send notifications to agent system
    try:
        _send_pipeline_notifications(filename, result, task_id)
    except Exception as e:
        logger.error(f"Failed to send pipeline notifications: {e}")

    return result

# Add the quick task with similar pattern
@celery_app.task(bind=True, name="process_audio_quick_task")
def process_audio_quick_task(
    self,
    audio_bytes: bytes,
    filename: str,
    language: Optional[str] = None
):
    """
    Celery task for quick audio analysis
    """
    try:
        self.update_state(
            state="PROCESSING",
            meta={
                "step": "quick_analysis",
                "filename": filename,
                "progress": 0
            }
        )
        
        # Get worker models
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in Celery worker")
        
        # Quick processing (no translation, no insights)
        result = _process_audio_sync_worker(
            self, models, audio_bytes, filename, language, threshold=0.5, return_raw=False,
            include_translation=False, include_insights=False
        )
        
        # Extract essentials for quick response
        classification = result.get("classification", {})
        qa_scores = result.get("qa_scores", {})

        insights = result.get("insights", {})
        risk_assessment = insights.get("risk_assessment", {}) if insights else {}
        
        quick_result = {
            "transcript": result["transcript"],
            "summary": result["summary"],
            "main_category": classification.get("main_category", "unknown"),
            "priority": classification.get("priority", "medium"),
            "risk_level": risk_assessment.get("risk_level", "unknown"),
            "processing_time": result["pipeline_info"]["total_time"],
            # "qa_scores": qa_scores,

        }
        
        return {
            "status": "completed",
            "filename": filename,
            "result": quick_result
        }
        
    except Exception as e:
        logger.error(f"Quick audio processing task failed: {e}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "filename": filename,
                "error_type": type(e).__name__
            }
        )
        raise e

def _generate_insights(transcript: str, translation: Optional[str], 
                      entities: Dict, classification: Dict, summary: str, qa_scores: Dict) -> Dict[str, Any]:
    """Generate basic insights from processed data including QA evaluation"""
    
    persons = entities.get("PERSON", [])
    locations = entities.get("LOC", []) + entities.get("GPE", [])
    organizations = entities.get("ORG", [])
    dates = entities.get("DATE", [])
    
    primary_text = translation if translation else transcript
    
    # Basic risk assessment
    risk_keywords = ["suicide", "abuse", "violence", "threat", "danger", "crisis", "emergency"]
    risk_score = sum(1 for keyword in risk_keywords if keyword.lower() in primary_text.lower())
    
    # Calculate QA summary metrics if QA scores are available
    qa_summary = None
    if qa_scores and isinstance(qa_scores, dict):
        total_metrics = 0
        passed_metrics = 0
        
        for category, metrics in qa_scores.items():
            if isinstance(metrics, list):
                for metric in metrics:
                    total_metrics += 1
                    if metric.get("prediction", False):
                        passed_metrics += 1
        
        if total_metrics > 0:
            pass_rate = (passed_metrics / total_metrics) * 100
            qa_summary = {
                "total_metrics_evaluated": total_metrics,
                "metrics_passed": passed_metrics,
                "metrics_failed": total_metrics - passed_metrics,
                "pass_rate_percentage": round(pass_rate, 1),
                "overall_quality": "excellent" if pass_rate >= 80 else "good" if pass_rate >= 60 else "fair" if pass_rate >= 40 else "needs_improvement"
            }
    
    return {
        "case_overview": {
            "primary_language": "multilingual" if translation else "original",
            "key_entities": {
                "people_mentioned": len(persons),
                "locations_mentioned": len(locations),
                "organizations_mentioned": len(organizations),
                "dates_mentioned": len(dates)
            },
            "case_complexity": "high" if len(persons) > 2 or len(locations) > 1 else "medium" if len(persons) > 0 else "low"
        },
        "risk_assessment": {
            "risk_indicators_found": risk_score,
            "risk_level": "high" if risk_score >= 2 else "medium" if risk_score >= 1 else "low",
            "priority": classification.get("priority", "medium"),
            "confidence": classification.get("confidence", 0)
        },
        "key_information": {
            "main_category": classification.get("main_category", "unknown"),
            "sub_category": classification.get("sub_category", "unknown"),
            "intervention_needed": classification.get("intervention", "assessment_required"),
            "summary": summary[:200] + "..." if len(summary) > 200 else summary
        },
        "entities_detail": {
            "persons": persons[:5],
            "locations": locations[:3],
            "organizations": organizations[:3],
            "key_dates": dates[:3]
        },
        "quality_assurance": qa_summary if qa_summary else {
            "status": "not_evaluated",
            "message": "QA evaluation not available"
        }
    }
    
# Add to app/tasks/audio_tasks.py

@celery_app.task(bind=True, name="process_streaming_audio_task")
def process_streaming_audio_task(
    self,
    audio_bytes: bytes,
    filename: str,
    connection_id: str,  # Now call_id from Asterisk
    language: str = "sw",
    sample_rate: int = 16000,
    duration_seconds: float = 5.0,
    is_streaming: bool = True
):
    """
    Process real-time streaming audio chunks from Asterisk with call session tracking
    Mixed-mono audio (both caller and agent voices) in 5-second windows from 10ms chunks
    Quick transcription only for low latency, adds to cumulative transcript
    """
    
    try:
        # Get worker models (your existing function)
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        start_time = datetime.now()
        call_id = connection_id  # connection_id is now actually call_id
        
        # Quick processing (transcription OR translation based on strategy)
        from ..core.whisper_model_manager import whisper_model_manager
        should_use_whisper_translation = whisper_model_manager.should_use_whisper_translation()
        
        whisper_model = models.models.get("whisper")
        if whisper_model: 
            # Choose task based on translation strategy
            task = "translate" if should_use_whisper_translation else "transcribe"
            
            # Use the PCM processing method with appropriate task
            result = whisper_model.transcribe_pcm_audio(
                audio_bytes,
                sample_rate=sample_rate,
                language=language,
                task=task
            )
            
            # Set transcript or translation based on task
            if should_use_whisper_translation:
                transcript = None  # No transcript in translation mode
                translation = result
            else:
                transcript = result
                translation = None
            
            processing_duration = (datetime.now() - start_time).total_seconds()
            
            # Add transcription to call session (async operation in sync context)
            try:
                import asyncio
                
                # Get or create event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Import session manager and add transcription
                from ..streaming.call_session_manager import call_session_manager
                
                # Skip Redis debug logs for streaming to reduce verbosity
                
                # Add to call session with metadata
                metadata = {
                    'task_id': self.request.id,
                    'processing_duration': processing_duration,
                    'filename': filename,
                    'sample_rate': sample_rate
                }
                
                # Only add to session if we have actual content (not empty/filtered)
                content_to_add = translation if should_use_whisper_translation else transcript
                
                if content_to_add:  # Only process non-empty content
                    # Run async operation in sync context with retry for race condition
                    updated_session = None
                    for retry in range(3):  # Try up to 3 times
                        try:
                            updated_session = loop.run_until_complete(
                                call_session_manager.add_transcription(
                                    call_id, 
                                    content_to_add,  # Use translation or transcript 
                                    duration_seconds, 
                                    metadata
                                )
                            )
                            if updated_session:
                                break
                            
                            # If session not found and this is first attempt, wait briefly for session creation
                            if retry < 2:
                                logger.debug(f"🔄 Session {call_id} not ready, retry {retry + 1}/3 after 500ms")
                                import time
                                time.sleep(0.5)
                                
                        except Exception as session_error:
                            logger.error(f"❌ Session operation failed for {call_id} (retry {retry + 1}/3): {session_error}")
                            if retry == 2:  # Last attempt
                                raise
                            import time
                            time.sleep(0.5)
                else:
                    logger.debug(f"📭 Skipping empty content for call {call_id}")
                    updated_session = None
                
                # Concise logging for streaming chunks
                if updated_session:
                    content_for_log = translation if should_use_whisper_translation else transcript
                    if content_for_log:  # Only log non-empty content
                        logger.info(f"📡 {call_id} {updated_session.segment_count}/{updated_session.total_audio_duration:.0f}s: {content_for_log}")
                    else:
                        logger.debug(f"📡 {call_id} {updated_session.segment_count}: (silent)")
                elif content_to_add:  # Only warn if we had content but couldn't add to session
                    logger.warning(f"⚠️ Could not add to session {call_id}")
                # If no content and no session update, that's expected - no warning needed
                
            except Exception as session_error:
                logger.error(f"❌ Session update failed for {call_id}: {session_error}")
            
            return {
                "call_id": call_id,
                "transcript": transcript,
                "processing_duration": processing_duration,
                "audio_duration": duration_seconds,
                "timestamp": datetime.now().isoformat(),
                "session_updated": True
            }
        else:
            logger.warning(f"⚠️ Whisper model not available in worker")
            return {"error": "Whisper model not loaded"}
        
    except Exception as e:
        logger.error(f"❌ Streaming transcription failed: {e}")
        raise


@celery_app.task(bind=True)
def process_feedback_audio_task(self, call_id: str, agent_id: str, feedback_notes: str = ""):
    """
    Background task for processing audio based on agent feedback
    
    This task:
    1. Downloads audio file using existing SCP infrastructure
    2. Runs 2-stage audio preprocessing with quality filtering
    3. Uploads only high-quality chunks to S3
    4. Returns S3 URLs for Label Studio integration
    """
    
    logger.info(f"Starting feedback audio processing for call {call_id} (agent: {agent_id})")
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'call_id': call_id,
                'stage': 'downloading',
                'message': 'Downloading audio file...',
                'progress': 10
            }
        )
        
        # Step 1: Download audio file using existing SCP infrastructure
        from ..utils.scp_audio_downloader import download_audio_via_scp
        
        audio_bytes, download_info = asyncio.run(download_audio_via_scp(call_id))
        
        if not audio_bytes:
            error_msg = f"Failed to download audio for call {call_id}: {download_info.get('error', 'Unknown error')}"
            logger.error(error_msg)
            # raise Exception(error_msg)
            raise RuntimeError(error_msg)

        
        logger.info(f"Downloaded audio file: {download_info.get('file_size_mb', 0):.1f} MB")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'call_id': call_id,
                'stage': 'preprocessing',
                'message': 'Processing audio and filtering quality chunks...',
                'progress': 30
            }
        )
        
        # Step 2: Save audio to temporary file for preprocessing
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        try:
            # Step 3: Run preprocessing using the service
            from ..services.audio_preprocessing_service import audio_preprocessing_service
            
            result = asyncio.run(audio_preprocessing_service.process_audio_file(
                audio_file_path=temp_audio_path,
                call_id=call_id,
                agent_id=agent_id,
                feedback_notes=feedback_notes
            ))
            
            # Update task state
            self.update_state(
                state='PROGRESS',
                meta={
                    'call_id': call_id,
                    'stage': 'uploading',
                    'message': f'Uploading {result.quality_chunks} quality chunks to S3...',
                    'progress': 70
                }
            )
            
            if not result.success:
                error_msg = f"Audio preprocessing failed: {result.error_message}"
                logger.error(error_msg)
                # raise Exception(error_msg)
                raise RuntimeError(error_msg)
            
            # TODO: Step 4: Create Label Studio tasks (integrate with existing process)
            # This would typically call your existing Label Studio integration
            # For now, just log the S3 URLs
            logger.info(f"Quality chunks uploaded to S3: {len(result.s3_urls)} URLs")
            for url in result.s3_urls:
                logger.debug(f"S3 URL: {url}")
            
            # Final update
            self.update_state(
                state='PROGRESS',
                meta={
                    'call_id': call_id,
                    'stage': 'completed',
                    'message': 'Audio preprocessing completed successfully',
                    'progress': 100
                }
            )
            
            # Return final result
            return {
                'success': True,
                'call_id': call_id,
                'agent_id': agent_id,
                'batch_id': result.batch_id,
                'total_chunks': result.total_chunks,
                'quality_chunks': result.quality_chunks,
                's3_urls': result.s3_urls,
                'processing_time_seconds': result.processing_time_seconds,
                'download_info': download_info,
                'message': f'Successfully processed {result.quality_chunks}/{result.total_chunks} quality chunks'
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
                
    except Exception as e:
        return handle_task_error(self, f"Processing failed for call {call_id}: {e}", call_id)
    # except Exception as e:
    #     logger.error(f"Feedback audio processing failed for call {call_id}: {e}")
        
        # Update task state to failure
        # self.update_state(
        #     state='FAILURE',
        #     meta={
        #         'call_id': call_id,
        #         'error': str(e),
        #         'message': f'Processing failed: {str(e)}'
        #     }
        # )
        
        raise

def handle_task_error(self, error_msg, call_id=None):
    """Consistent error handling for all Celery tasks"""
    logger.error(error_msg)
    # log and re-raise - let Celery handle the state
    raise RuntimeError(error_msg)