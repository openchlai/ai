"""Health check tasks for Celery workers"""
import socket
from typing import Dict, Any
from ..celery_app import celery_app

@celery_app.task(name="health_check_models")
def health_check_models() -> Dict[str, Any]:
    """Check which models are loaded on this Celery worker"""
    try:
        from ..model_scripts.model_loader import model_loader
        
        # Get ready models
        ready_models = model_loader.get_ready_models()
        
        return {
            "worker_host": socket.gethostname(),
            "status": "healthy",
            "models_loaded": {
                "qa": "qa" in ready_models,
                "classifier": "classifier_model" in ready_models,
                "ner": "ner" in ready_models,
                "summarizer": "summarizer" in ready_models,
                "translator": "translator" in ready_models,
                "whisper": "whisper" in ready_models,
            },
            "ready_models": ready_models,
            "total_ready_models": len(ready_models)
        }
    except Exception as e:
        return {
            "worker_host": socket.gethostname(),
            "status": "error",
            "error": str(e),
            "models_loaded": {
                "qa": False,
                "classifier": False,
                "ner": False,
                "summarizer": False,
                "translator": False,
                "whisper": False,
            },
            "ready_models": [],
            "total_ready_models": 0
        }