import argparse
import logging
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config.settings import settings
from .api import health_routes, ner_routes, translator_routes, summarizer_routes, classifier_route, whisper_routes, audio_routes, call_session_routes, qa_route, processing_mode_routes, whisper_model_routes, notification_routes, agent_feedback_routes
from .model_scripts.model_loader import model_loader
from .core.resource_manager import resource_manager
from .streaming.tcp_server import AsteriskTCPServer
from .streaming.websocket_server import websocket_manager

from .config.settings import settings

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
    global asterisk_server
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize paths
    settings.initialize_paths()
    
    # Initialize database tables
    logger.info("🗄️ Initializing database...")
    try:
        from .db.session import init_db
        init_db()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

    # Initialize Redis connections (needed for both API server and worker modes)
    logger.info("📡 Initializing Redis connections...")
    try:
        from .config.settings import initialize_redis
        redis_success = initialize_redis()
        if redis_success:
            logger.info("✅ Redis connections initialized")
        else:
            logger.warning("⚠️ Redis initialization failed")
    except Exception as e:
        logger.error(f"❌ Redis initialization error: {e}")
    
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
    
    # 🆕 Start Asterisk TCP server if enabled
    if os.getenv("ENABLE_ASTERISK_TCP", "true").lower() == "true":
        try:
            logger.info("🎙️ Starting Asterisk TCP listener...")
            asterisk_server = AsteriskTCPServer(
                host=settings.streaming_host,
                port=settings.streaming_port
            )
            
            # Start TCP listener in background
            asyncio.create_task(asterisk_server.start_server())
            logger.info(f"🎙️ Asterisk TCP listener started on port {settings.streaming_port} - waiting for connections")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Asterisk TCP listener: {e}")
    else:
        logger.info("🔇 Asterisk TCP listener disabled")
    
    logger.info("Application startup complete")
    
    yield  # Application runs here
    
    # SHUTDOWN
    logger.info("Application shutdown")
    
    # 🆕 Stop Asterisk TCP server
    if asterisk_server:
        try:
            await asterisk_server.stop_server()
            logger.info("🔌 Asterisk TCP listener stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping Asterisk TCP listener: {e}")
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
app.include_router(ner_routes.router)
app.include_router(translator_routes.router)
app.include_router(summarizer_routes.router)
app.include_router(classifier_route.router)
app.include_router(whisper_routes.router)
app.include_router(audio_routes.router)
app.include_router(call_session_routes.router)
app.include_router(qa_route.router)
app.include_router(processing_mode_routes.router)
app.include_router(whisper_model_routes.router)
app.include_router(notification_routes.router)
app.include_router(agent_feedback_routes.router)

@app.websocket("/audio/stream")
async def websocket_audio_stream(websocket: WebSocket):
    """WebSocket endpoint for Asterisk audio streaming"""
    await websocket_manager.handle_websocket(websocket)

@app.get("/asterisk/status")
async def asterisk_status():
    """Get Asterisk TCP and WebSocket listener status"""
    tcp_status = asterisk_server.get_status() if asterisk_server else {"error": "TCP listener not running"}
    ws_status = websocket_manager.get_status()
    
    return {
        "tcp_server": tcp_status,
        "websocket_server": ws_status
    }


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
            "asterisk_status": "/asterisk/status",
            "websocket_audio_stream": f"ws://localhost:{settings.app_port}/audio/stream",
            "call_sessions": "/api/v1/calls",
            "active_calls": "/api/v1/calls/active",
            "call_stats": "/api/v1/calls/stats",
            "qa_predict": "/qa/predict",
            "notification_status": "/api/v1/notifications/status",
            "notification_configure": "/api/v1/notifications/configure",
            "notification_statistics": "/api/v1/notifications/statistics",
            "agent_feedback_update": "/api/v1/agent-feedback/update",
            "agent_feedback_by_call": "/api/v1/agent-feedback/call/{call_id}",
            "agent_feedback_statistics": "/api/v1/agent-feedback/statistics",
            "agent_feedback_health": "/api/v1/agent-feedback/health"

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
    
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='AI Pipeline Server')
    parser.add_argument('--enable-streaming', action='store_true', 
                       help='Enable streaming server on port 8300')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Override settings based on command line args
    if args.enable_streaming:
        settings.enable_streaming = True
        logger.info("🎙️ Streaming mode enabled via command line")
    
    # Log the configuration
    logger.info(f"Configuration - Streaming: {getattr(settings, 'enable_streaming', False)}")

    # Get port from settings (configurable via APP_PORT env var, defaults to 8125)
    port = settings.app_port

    # If streaming is enabled, we need to start both FastAPI and streaming server
    if getattr(settings, 'enable_streaming', False):
        logger.info(f"🎙️ Starting with streaming support - FastAPI on {port}, Streaming on {settings.streaming_port}")
        # For now, just start FastAPI - we'll add streaming server in Task 1.3
        # TODO: Add streaming server startup here in Task 1.3
    else:
        logger.info(f"📦 Starting FastAPI only on port {port}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )