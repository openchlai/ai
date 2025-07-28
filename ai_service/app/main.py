import logging
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config.settings import settings
from .api import health_routes, queue_routes, ner_routes, translator_routes, summarizer_routes, classifier_route, whisper_routes, audio_routes, realtime_routes
from .models.model_loader import model_loader
from .core.resource_manager import resource_manager

# Only import Celery if we're not the main API server
if settings.enable_model_loading:
    from .celery_app import celery_app
    from .core.celery_monitor import celery_monitor

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize paths
    settings.initialize_paths()
    
    # API server doesn't need Celery monitoring or model loading
    if settings.enable_model_loading:
        logger.info("🔄 Worker mode - loading models and starting Celery monitoring...")
        
        # Start Celery event monitoring
        try:
            from .core.celery_monitor import celery_monitor
            celery_monitor.start_monitoring()
            logger.info("✅ Event monitoring started")
        except Exception as e:
            logger.warning(f"⚠️ Event monitoring failed to start: {e}")
        
        # Initialize models
        logger.info("✅ Model loading enabled - starting model initialization...")
        await model_loader.load_all_models()
    else:
        logger.info("🌐 API server mode - models handled by Celery workers")
    
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Container-Baked AI Pipeline for Multi-Modal Processing",
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router)
app.include_router(queue_routes.router)
app.include_router(ner_routes.router)
app.include_router(translator_routes.router)
app.include_router(summarizer_routes.router)
app.include_router(classifier_route.router)
app.include_router(whisper_routes.router)
app.include_router(audio_routes.router)
app.include_router(realtime_routes.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "site_id": settings.site_id,
        "status": "running",
        "mode": "worker" if settings.enable_model_loading else "api_server",
        "endpoints": {
            "health": "/health",
            "detailed_health": "/health/detailed", 
            "models": "/health/models",
            "resources": "/health/resources",
            "queue": "/queue/status",
            "whisper": "/whisper/transcribe",
            "complete_audio_pipeline": "/audio/process",
            "quick_audio_analysis": "/audio/analyze",
            "celery_status": "/health/celery/status",
            "realtime_status": "/realtime/status",
            "realtime_transcribe": "/realtime/transcribe"
        }
    }

@app.get("/info")
async def app_info():
    """Application information"""
    gpu_info = resource_manager.get_gpu_info()
    system_info = resource_manager.get_system_info()
    
    # Check Celery status if available
    celery_status = {"status": "not_applicable", "note": "API server mode"}
    if settings.enable_model_loading and 'celery_app' in globals():
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            celery_status = {
                "workers_online": len(stats) if stats else 0,
                "broker_url": celery_app.conf.broker_url,
                "status": "healthy" if stats else "no_workers"
            }
        except Exception as e:
            celery_status = {
                "workers_online": 0,
                "status": "error",
                "error": str(e)
            }
        
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "site_id": settings.site_id,
            "debug": settings.debug,
            "mode": "worker" if settings.enable_model_loading else "api_server"
        },
        "celery": celery_status,
        "system": system_info,
        "gpu": gpu_info
    }

if __name__ == "__main__":
    # Use different ports for API vs Worker
    port = 8123 if not settings.enable_model_loading else 8123
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )