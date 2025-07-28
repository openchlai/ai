# app/tasks/audio_tasks.py (Updated)
import json
import os
import socket
from celery import current_task
from celery.signals import worker_init
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
        from ..models.model_loader import ModelLoader
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
def process_audio_task(self, audio_bytes, filename, language=None, include_translation=True, include_insights=True):
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
    include_insights: bool
) -> Dict[str, Any]:
    """
    Synchronous audio processing using worker models
    """
    start_time = datetime.now()
    processing_steps = {}
    
    # Step 1: Transcription
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "transcription", "progress": 10}
    )
    
    step_start = datetime.now()
    whisper_model = models.models.get("whisper")
    if not whisper_model:
        raise RuntimeError("Whisper model not available in worker")
        
    transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language)
    
    processing_steps["transcription"] = {
        "duration": (datetime.now() - step_start).total_seconds(),
        "status": "completed",
        "output_length": len(transcript)
    }
    
    # Step 2: Translation (if enabled)
    translation = None
    if include_translation:
        task_instance.update_state(
            state="PROCESSING",
            meta={"step": "translation", "progress": 30}
        )
        
        step_start = datetime.now()
        try:
            translator_model = models.models.get("translator")
            if translator_model:
                translation = translator_model.translate(transcript)
                
                processing_steps["translation"] = {
                    "duration": (datetime.now() - step_start).total_seconds(),
                    "status": "completed",
                    "output_length": len(translation)
                }
            else:
                raise RuntimeError("Translator model not available")
        except Exception as e:
            processing_steps["translation"] = {
                "duration": (datetime.now() - step_start).total_seconds(),
                "status": "failed",
                "error": str(e)
            }
            translation = None
    
    # Step 3: NLP Processing
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "nlp_analysis", "progress": 50}
    )
    
    nlp_text = translation if translation else transcript
    nlp_source = "translated_text" if translation else "original_transcript"
    
    # NER
    step_start = datetime.now()
    try:
        ner_model = models.models.get("ner")
        if not ner_model:
            raise RuntimeError("NER model not available")
        entities = ner_model.extract_entities(nlp_text, flat=False)
        ner_status = {
            "result": entities,
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "completed"
        }
    except Exception as e:
        ner_status = {
            "result": {},
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "failed",
            "error": str(e)
        }
    
    # Classification
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "classification", "progress": 70}
    )
    
    step_start = datetime.now()
    try:
        classifier_model = models.models.get("classifier_model")
        if not classifier_model:
            raise RuntimeError("Classifier model not available")
        classification = classifier_model.classify(nlp_text)
        classifier_status = {
            "result": classification,
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "completed"
        }
    except Exception as e:
        classifier_status = {
            "result": {},
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "failed",
            "error": str(e)
        }
    
    # Summarization
    task_instance.update_state(
        state="PROCESSING",
        meta={"step": "summarization", "progress": 85}
    )
    
    step_start = datetime.now()
    try:
        summarizer_model = models.models.get("summarizer")
        if not summarizer_model:
            raise RuntimeError("Summarizer model not available")
        summary = summarizer_model.summarize(nlp_text)
        summary_status = {
            "result": summary,
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "completed"
        }
    except Exception as e:
        summary_status = {
            "result": "",
            "duration": (datetime.now() - step_start).total_seconds(),
            "status": "failed",
            "error": str(e)
        }
    
    # Step 4: Insights (if enabled)
    insights = {}
    if include_insights:
        task_instance.update_state(
            state="PROCESSING",
            meta={"step": "insights", "progress": 95}
        )
        
        # Generate insights (simplified version)
        entities = ner_status["result"]
        classification = classifier_status["result"]
        summary = summary_status["result"]
        
        insights = _generate_insights(transcript, translation, entities, classification, summary)
    
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
            "models_used": ["whisper"] + (["translator"] if include_translation else []) + ["ner", "classifier", "summarizer"],
            "text_flow": f"transcript → {nlp_source} → nlp_models",
            "timestamp": datetime.now().isoformat(),
            "processed_by": "celery_worker"
        }
    }
    
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
            self, models, audio_bytes, filename, language, 
            include_translation=False, include_insights=False
        )
        
        # Extract essentials for quick response
        classification = result.get("classification", {})
        insights = result.get("insights", {})
        risk_assessment = insights.get("risk_assessment", {}) if insights else {}
        
        quick_result = {
            "transcript": result["transcript"],
            "summary": result["summary"],
            "main_category": classification.get("main_category", "unknown"),
            "priority": classification.get("priority", "medium"),
            "risk_level": risk_assessment.get("risk_level", "unknown"),
            "processing_time": result["pipeline_info"]["total_time"]
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
                      entities: Dict, classification: Dict, summary: str) -> Dict[str, Any]:
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
            "key_dates": dates[:3]
        }
    }