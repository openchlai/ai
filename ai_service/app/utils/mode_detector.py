"""Utility to detect if running in API Server mode or Standalone mode"""
from typing import Literal

def get_execution_mode() -> Literal["api_server", "standalone"]:
    """
    Determine if we're in API Server mode (models on Celery) or Standalone mode (models local)
    
    Returns:
        "api_server" if models are on Celery workers
        "standalone" if models are loaded locally in FastAPI
    """
    from ..config.settings import settings
    
    # Primary detection based on settings
    if not settings.enable_model_loading:
        return "api_server"
    
    # Secondary check - verify if models are actually loaded locally
    try:
        from ..model_scripts.model_loader import model_loader
        
        # Check if any critical models are loaded locally
        ready_models = model_loader.get_ready_models()
        has_local_models = len(ready_models) > 0
        
        return "standalone" if has_local_models else "api_server"
        
    except Exception:
        # If model_loader is not available, fall back to settings
        return "standalone" if settings.enable_model_loading else "api_server"

def is_api_server_mode() -> bool:
    """Check if running in API Server mode (models on Celery)"""
    return get_execution_mode() == "api_server"

def is_standalone_mode() -> bool:
    """Check if running in Standalone mode (models loaded locally)"""
    return get_execution_mode() == "standalone"