# app/tasks/inference_tasks.py - Lightweight Model Inference Tasks
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from celery import current_task
from ..celery_app import celery_app

logger = logging.getLogger(__name__)

def get_worker_models():
    """Get the worker's model loader instance"""
    from .audio_tasks import get_worker_models
    return get_worker_models()

# Whisper Model Inference Tasks

@celery_app.task(bind=True, name="whisper_transcribe_inference")
def whisper_transcribe_inference(self, audio_bytes: bytes, language: Optional[str] = None, task_type: str = "transcribe"):
    """
    Lightweight Whisper transcription inference task
    
    Args:
        audio_bytes: Audio data as bytes
        language: Language code (e.g., 'en', 'sw', 'auto')
        task_type: 'transcribe' or 'translate'
    
    Returns:
        Dict with transcript, language, processing_time, model_info
    """
    start_time = datetime.now()
    
    try:
        # Simple progress update - avoid complex meta
        self.update_state(state="PROGRESS", meta={"progress": 10})
        
        # Get worker models
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        # Select appropriate Whisper model based on task type
        if task_type == "translate":
            whisper_model = models.models.get("whisper_translation")
            if not whisper_model or not whisper_model.is_ready():
                # Fallback to regular whisper if translation model not available
                whisper_model = models.models.get("whisper")
                task_type = "transcribe"  # Change task since regular model doesn't translate
                logger.warning("Translation model not available, falling back to transcription")
        else:
            whisper_model = models.models.get("whisper")
        
        if not whisper_model or not whisper_model.is_ready():
            raise RuntimeError("Whisper model not available or not ready")
        
        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 30})
        
        # Perform transcription/translation
        if task_type == "translate" and hasattr(whisper_model, 'enable_translation') and whisper_model.enable_translation:
            # Use Whisper translation capability
            transcript = whisper_model.transcribe_audio_bytes(
                audio_bytes, 
                language=language or "sw",  # Default to Swahili for translation
                task="translate"
            )
        else:
            # Regular transcription (force task_type to transcribe if model doesn't support translation)
            if task_type == "translate":
                logger.warning("Translation requested but model doesn't support it, falling back to transcription")
                task_type = "transcribe"
            
            transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language)
        
        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 90})
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = whisper_model.get_model_info()
        
        # Audio info
        audio_info = {
            "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
            "processing_time": processing_time
        }
        
        result = {
            "transcript": transcript,
            "language": language,
            "task_type": task_type,
            "processing_time": processing_time,
            "model_info": {
                "model_name": model_info.get("model_name", "whisper"),
                "version": model_info.get("version", "unknown"),
                "device": model_info.get("device", "unknown"),
                "current_model_id": model_info.get("current_model_id", "unknown")
            },
            "audio_info": audio_info,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Whisper inference completed in {processing_time:.2f}s: {len(transcript)} characters")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Whisper inference failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Don't update state - let Celery handle the failure naturally
        # Just raise a simple exception
        raise Exception(error_msg)

@celery_app.task(bind=True, name="whisper_get_info")
def whisper_get_info(self):
    """Get Whisper model information"""
    try:
        models = get_worker_models()
        if not models:
            return {"status": "error", "message": "Models not loaded in worker"}
        
        whisper_model = models.models.get("whisper")
        whisper_translation_model = models.models.get("whisper_translation")
        
        result = {"models": {}}
        
        if whisper_model and whisper_model.is_ready():
            result["models"]["whisper"] = {
                "status": "ready",
                "model_info": whisper_model.get_model_info()
            }
        else:
            result["models"]["whisper"] = {
                "status": "not_ready",
                "message": "Whisper model not loaded"
            }
        
        if whisper_translation_model and whisper_translation_model.is_ready():
            result["models"]["whisper_translation"] = {
                "status": "ready", 
                "model_info": whisper_translation_model.get_model_info()
            }
        else:
            result["models"]["whisper_translation"] = {
                "status": "not_ready",
                "message": "Whisper translation model not loaded"
            }
        
        result["worker_status"] = "healthy"
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get Whisper info: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="whisper_get_languages")
def whisper_get_languages(self):
    """Get supported languages"""
    try:
        models = get_worker_models()
        if not models:
            return {"error": "Models not loaded in worker"}
        
        whisper_model = models.models.get("whisper")
        if whisper_model and whisper_model.is_ready():
            return {
                "supported_languages": whisper_model.get_supported_languages(),
                "total_supported": "99+ languages",
                "note": "Whisper supports many more languages beyond this list"
            }
        else:
            return {"error": "Whisper model not ready"}
            
    except Exception as e:
        logger.error(f"❌ Failed to get languages: {e}")
        return {"error": str(e)}

# NER Model Inference Task

@celery_app.task(bind=True, name="ner_extract_inference")
def ner_extract_inference(self, text: str, flat: bool = False):
    """
    Lightweight NER entity extraction inference task
    
    Args:
        text: Input text for entity extraction
        flat: Whether to return flat list or grouped by entity type
    
    Returns:
        Dict with entities, processing_time, model_info
    """
    start_time = datetime.now()
    
    try:
        self.update_state(state="PROGRESS", meta={"progress": 20})
        
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        ner_model = models.models.get("ner")
        if not ner_model or not ner_model.is_ready():
            raise RuntimeError("NER model not available or not ready")
        
        self.update_state(state="PROGRESS", meta={"progress": 50})
        
        # Extract entities
        entities = ner_model.extract_entities(text, flat=flat)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "entities": entities,
            "text_length": len(text),
            "entity_count": len(entities) if flat else sum(len(v) for v in entities.values()),
            "processing_time": processing_time,
            "model_info": {
                "model_name": "ner",
                "processed_text_length": len(text)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ NER inference completed in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"NER inference failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Let Celery handle the failure naturally
        raise Exception(error_msg)

# Translation Model Inference Task

@celery_app.task(bind=True, name="translator_inference")
def translator_inference(self, text: str, source_lang: str = "auto", target_lang: str = "en"):
    """
    Lightweight translation inference task
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
    
    Returns:
        Dict with translation, processing_time, model_info
    """
    start_time = datetime.now()
    
    try:
        self.update_state(state="PROGRESS", meta={"progress": 20})
        
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        translator_model = models.models.get("translator")
        if not translator_model or not translator_model.is_ready():
            raise RuntimeError("Translator model not available or not ready")
        
        self.update_state(state="PROGRESS", meta={"progress": 50})
        
        # Perform translation
        translation = translator_model.translate(text)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "translation": translation,
            "source_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "processing_time": processing_time,
            "model_info": {
                "model_name": "translator",
                "input_length": len(text),
                "output_length": len(translation)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Translation inference completed in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Translation inference failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Let Celery handle the failure naturally
        raise Exception(error_msg)

# Summarizer Model Inference Task

@celery_app.task(bind=True, name="summarizer_inference")
def summarizer_inference(self, text: str, max_length: Optional[int] = None, min_length: Optional[int] = None):
    """
    Lightweight summarization inference task
    
    Args:
        text: Text to summarize
        max_length: Maximum summary length
        min_length: Minimum summary length
    
    Returns:
        Dict with summary, processing_time, model_info
    """
    start_time = datetime.now()
    
    try:
        self.update_state(state="PROGRESS", meta={"progress": 20})
        
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        summarizer_model = models.models.get("summarizer")
        if not summarizer_model or not summarizer_model.is_ready():
            raise RuntimeError("Summarizer model not available or not ready")
        
        self.update_state(state="PROGRESS", meta={"progress": 50})
        
        # Perform summarization
        summary = summarizer_model.summarize(text)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "summary": summary,
            "source_text": text,
            "processing_time": processing_time,
            "model_info": {
                "model_name": "summarizer",
                "input_length": len(text),
                "output_length": len(summary),
                "compression_ratio": round(len(summary) / len(text), 3) if text else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Summarization inference completed in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Summarization inference failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Let Celery handle the failure naturally
        raise Exception(error_msg)

# Classifier Model Inference Task

@celery_app.task(bind=True, name="classifier_inference")
def classifier_inference(self, text: str):
    """
    Lightweight classification inference task
    
    Args:
        text: Text to classify
    
    Returns:
        Dict with classification, processing_time, model_info
    """
    start_time = datetime.now()
    
    try:
        self.update_state(state="PROGRESS", meta={"progress": 20})
        
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        classifier_model = models.models.get("classifier_model")
        if not classifier_model or not classifier_model.is_ready():
            raise RuntimeError("Classifier model not available or not ready")
        
        self.update_state(state="PROGRESS", meta={"progress": 50})
        
        # Perform classification
        classification = classifier_model.classify(text)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "classification": classification,
            "text": text,
            "processing_time": processing_time,
            "model_info": {
                "model_name": "classifier",
                "input_length": len(text)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Classification inference completed in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Classification inference failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Let Celery handle the failure naturally
        raise Exception(error_msg)

# QA Model Inference Task

@celery_app.task(bind=True, name="qa_inference")
def qa_inference(self, text: str, threshold: float = 0.5, return_raw: bool = False):
    """
    Lightweight QA scoring inference task
    
    Args:
        text: Text to analyze for QA scoring
        threshold: Confidence threshold
        return_raw: Whether to return raw scores
    
    Returns:
        Dict with qa_scores, processing_time, model_info
    """
    start_time = datetime.now()
    
    try:
        self.update_state(state="PROGRESS", meta={"progress": 20})
        
        models = get_worker_models()
        if not models:
            raise RuntimeError("Models not loaded in worker")
        
        qa_model = models.models.get("all_qa_distilbert_v1")
        if not qa_model or not qa_model.is_ready():
            raise RuntimeError("QA model not available or not ready")
        
        self.update_state(state="PROGRESS", meta={"progress": 50})
        
        # Perform QA scoring
        qa_scores = qa_model.predict(text, return_raw=return_raw)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "qa_scores": qa_scores,
            "text": text,
            "threshold": threshold,
            "return_raw": return_raw,
            "processing_time": processing_time,
            "model_info": {
                "model_name": "all_qa_distilbert_v1",
                "input_length": len(text)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ QA inference completed in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"QA inference failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Let Celery handle the failure naturally
        raise Exception(error_msg)