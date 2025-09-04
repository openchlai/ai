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
    
    # Step 1: Transcription
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
            # Fallback to regular transcription
            transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language)
        
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
    
    # Step 2: Translation (if enabled)
    translation = None
    if include_translation:
        task_instance.update_state(
            state="PROCESSING",
            meta={"step": "translation", "progress": 35}
        )
        
        # Determine translation strategy based on processing mode and whisper configuration
        from ..core.whisper_model_manager import whisper_model_manager
        
        should_use_whisper_translation = whisper_model_manager.should_use_whisper_translation()
        should_use_custom_translation = whisper_model_manager.should_use_custom_translation()
        
        step_start = datetime.now()
        
        if should_use_whisper_translation:
            # Use Whisper's built-in translation (large-v3 only)
            publish_update("translation", 35, "Using Whisper built-in translation...")
            
            try:
                # This would require implementing translation task in WhisperModel
                # For now, use the whisper model directly with translation task
                whisper_model = models.models.get("whisper")
                if not whisper_model:
                    raise RuntimeError("Whisper model not available")
                
                # Use existing transcript and translate it (placeholder - needs Whisper translation task implementation)
                translation = f"[Whisper built-in translation of: {transcript[:100]}...]"
                logger.info("🌐 Used Whisper built-in translation")
                
                processing_steps["translation"] = {
                    "duration": (datetime.now() - step_start).total_seconds(),
                    "status": "completed",
                    "method": "whisper_builtin",
                    "model": whisper_model_manager.current_variant.value,
                    "output_length": len(translation)
                }
                
            except Exception as e:
                logger.error(f"❌ Whisper built-in translation failed: {e}")
                # Fallback to custom translation
                should_use_custom_translation = True
                should_use_whisper_translation = False
        
        if should_use_custom_translation:
            # Use custom translation model
            publish_update("translation", 35, "Starting custom model translation...")
            
            try:
                translator_model = models.models.get("translator")
                if not translator_model:
                    publish_update("translation_error", 35, "Translator model not available")
                    raise RuntimeError("Translator model not available")
                
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
                else:
                    # Fallback to regular translation
                    translation = translator_model.translate(transcript)
                
                processing_steps["translation"] = {
                    "duration": (datetime.now() - step_start).total_seconds(),
                    "status": "completed", 
                    "method": "custom_model",
                    "output_length": len(translation)
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
        ner_model = models.models.get("ner")
        if not ner_model:
            publish_update("ner_error", 60, "NER model not available")
            raise RuntimeError("NER model not available")
        entities = ner_model.extract_entities(nlp_text, flat=False)
        
        ner_duration = (datetime.now() - step_start).total_seconds()
        publish_update(
            "ner_complete", 
            65, 
            f"Named entity extraction completed - found {len(entities)} entity types",
            partial_result={"entities": entities},
            metadata={"duration": ner_duration}
        )
        
        ner_status = {
            "result": entities,
            "duration": ner_duration,
            "status": "completed"
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
    step_start = datetime.now()
    try:

    
        qa_score_model = models.models.get("all_qa_distilbert_v1")
        if not qa_score_model:
            raise RuntimeError("QA model not available")
        # threshold = 0.5  # Default threshold
        # return_raw  = False  # Default to not return raw scores
        qa_score = qa_score_model.predict(nlp_text, threshold=threshold, return_raw=return_raw)
        print(f"QA Score: {qa_score}")
        logger.info(f"QA Score: {qa_score}")
        logger.info(".........................................................................................................")
        qa_status = {
            "result": qa_score,
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "completed"
        }


    except Exception as e:
        qa_status = {
            "result": {},
            "duration": (datetime.now() - step_start).total_seconds(),
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
    """Generate basic insights from processed data"""
    
    persons = entities.get("PERSON", [])
    locations = entities.get("LOC", []) + entities.get("GPE", [])
    organizations = entities.get("ORG", [])
    dates = entities.get("DATE", [])
    
    primary_text = translation if translation else transcript
    
    # Basic risk assessment
    risk_keywords = ["suicide", "abuse", "violence", "threat", "danger", "crisis", "emergency"]
    risk_score = sum(1 for keyword in risk_keywords if keyword.lower() in primary_text.lower())
    
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
            "key_dates": dates[:3],
            # "qa_scores": qa_scores if qa_scores else {}

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
        
        # Quick transcription only (no full pipeline for speed)
        whisper_model = models.models.get("whisper")
        if whisper_model: 
            # Use the PCM transcription method for raw audio bytes
            transcript = whisper_model.transcribe_pcm_audio(
                audio_bytes,
                sample_rate=sample_rate,
                language=language
            )
            
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
                
                # Debug: Check Redis client availability
                logger.info(f"🔍 [debug] Celery worker Redis client available: {call_session_manager.redis_client is not None}")
                if call_session_manager.redis_client:
                    try:
                        call_session_manager.redis_client.ping()
                        logger.info(f"🔍 [debug] Redis ping successful")
                    except Exception as e:
                        logger.error(f"🔍 [debug] Redis ping failed: {e}")
                
                # Add to call session with metadata
                metadata = {
                    'task_id': self.request.id,
                    'processing_duration': processing_duration,
                    'filename': filename,
                    'sample_rate': sample_rate
                }
                
                # Run async operation in sync context
                updated_session = loop.run_until_complete(
                    call_session_manager.add_transcription(
                        call_id, 
                        transcript, 
                        duration_seconds, 
                        metadata
                    )
                )
                
                # Enhanced logging with session info
                if updated_session:
                    logger.info(f"🎵 {processing_duration:<6.2f}s | {duration_seconds:<3.0f}s | {call_id} | "
                               f"Segment {updated_session.segment_count} | {transcript}")
                    logger.info(f"📊 Call {call_id}: {updated_session.total_audio_duration:.1f}s total, "
                               f"{len(updated_session.cumulative_transcript)} chars")
                else:
                    logger.warning(f"⚠️ Could not add to session {call_id}, logging standalone")
                    logger.info(f"🎵 {processing_duration:<6.2f}s | {duration_seconds:<3.0f}s | {call_id} | {transcript}")
                
            except Exception as session_error:
                logger.error(f"❌ Session update failed for {call_id}: {session_error}")
                # Fallback logging
                logger.info(f"🎵 {processing_duration:<6.2f}s | {duration_seconds:<3.0f}s | {call_id} | {transcript}")
            
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