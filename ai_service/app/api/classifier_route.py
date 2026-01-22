from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from datetime import datetime
from ..model_scripts.model_loader import model_loader
from ..utils.mode_detector import is_api_server_mode, get_execution_mode
from typing import List, Dict, Optional
from celery.result import AsyncResult
from ..tasks.model_tasks import classifier_classify_task
from ..celery_app import celery_app
from .models import ErrorResponse, ErrorCodes, create_error_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/classifier", tags=["classifier"])


class ConfidenceScores(BaseModel):
    main_category: Optional[float] = None
    sub_category: Optional[float] = None
    sub_category_2: Optional[float] = None 
    intervention: Optional[float] = None
    priority: Optional[float] = None


class ChunkPrediction(BaseModel):
    chunk_index: int
    token_count: int
    sentence_count: int
    position_ratio: float
    main_category: str
    sub_category: str
    sub_category_2: Optional[str] = None  
    intervention: str
    priority: str
    confidence_scores: ConfidenceScores


class ClassifierRequest(BaseModel):
    narrative: str


class ClassifierResponse(BaseModel):
    main_category: str
    sub_category: str
    sub_category_2: Optional[str] = None  
    intervention: str
    priority: str
    confidence_scores: ConfidenceScores
    chunks_processed: int
    chunk_predictions: Optional[List[ChunkPrediction]] = None
    processing_time: float
    model_info: dict
    timestamp: str


class ClassifierTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: str
    status_endpoint: str


class ClassifierTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[ClassifierResponse] = None
    error: Optional[str] = None
    progress: Optional[Dict] = None


@router.post(
    "/classify",
    response_model=ClassifierTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {
            "description": "Classification task accepted and queued for processing",
            "model": ClassifierTaskResponse
        },
        400: {
            "description": "Invalid input (empty narrative)",
            "model": ErrorResponse
        },
        503: {
            "description": "Classifier model not ready (standalone mode only)",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error during task submission",
            "model": ErrorResponse
        }
    }
)
async def classify_narrative(request: ClassifierRequest):
    """
    Classify case narrative into categories (async via Celery).

    This endpoint analyzes case narratives and classifies them into:
    - **Main Category**: Primary case type (abuse, neglect, etc.)
    - **Sub Category**: Specific sub-type
    - **Intervention**: Recommended intervention type
    - **Priority**: Case urgency level

    **Workflow:**
    1. POST to /classifier/classify with narrative text
    2. Receive task_id in response
    3. Poll /classifier/task/{task_id} for results

    **Processing Time:** Usually 10-30 seconds depending on narrative length

    Returns:
        ClassifierTaskResponse: Task ID and status endpoint for polling
    """

    if is_api_server_mode():
        # API Server mode - delegate to Celery worker
        # Skip local model check as models are on workers
        pass
    else:
        # Standalone mode - check local model
        if not model_loader.is_model_ready("classifier_model"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=create_error_response(
                    error_code=ErrorCodes.MODEL_NOT_READY,
                    message="Classifier model not ready. Check /health/models for status.",
                    detail="Model failed to load or is currently initializing"
                ).model_dump()
            )

    if not request.narrative.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                error_code=ErrorCodes.INVALID_INPUT,
                message="Narrative input cannot be empty",
                field="narrative"
            ).model_dump()
        )

    try:
        start_time = datetime.now()

        task = classifier_classify_task.apply_async(
            args=[request.narrative],
            queue='model_processing'
        )


        logger.info(f"📤 Classification task submitted: {task.id}")

        return ClassifierTaskResponse(
            task_id=task.id,
            status="queued",
            message="Classification started. Check status at /classifier/task/{task_id}",
            estimated_time="10-30 seconds",
            status_endpoint=f"/classifier/task/{task.id}"
        )

    except Exception as e:
        logger.error(f"Failed to submit classification task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                error_code=ErrorCodes.TASK_SUBMISSION_FAILED,
                message="Failed to submit classification task",
                detail=str(e)
            ).model_dump()
        )


@router.get("/task/{task_id}", response_model=ClassifierTaskStatusResponse)
async def get_classifier_task_status(task_id: str):
    """Get classification task status"""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            return ClassifierTaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress={"message": "Task is queued"}
            )
        
        elif task_result.state == 'PROCESSING':
            return ClassifierTaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=task_result.info or {}
            )
        
        elif task_result.state == 'SUCCESS':
            result = task_result.result
            
            classifier_response = ClassifierResponse(
                main_category=result['main_category'],
                sub_category=result['sub_category'],
                sub_category_2=result.get('sub_category_2'), 
                intervention=result['intervention'],
                priority=result['priority'],
                confidence_scores=ConfidenceScores(**result['confidence_scores']),
                chunks_processed=result['chunks_processed'],
                chunk_predictions=result.get('chunk_predictions'),
                processing_time=result['processing_time'],
                model_info=result['model_info'],
                timestamp=result['timestamp']
            )

            return ClassifierTaskStatusResponse(
                task_id=task_id,
                status="success",
                result=classifier_response
            )
        
        elif task_result.state == 'FAILURE':
            return ClassifierTaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(task_result.info)
            )
        
        else:
            return ClassifierTaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                progress={"message": f"Task state: {task_result.state}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking task")

@router.get("/info")
async def get_classifier_info():
    """Get classifier model information"""
    if is_api_server_mode():
        # API Server mode - models are on Celery workers
        return {
            "status": "api_server_mode",
            "message": "Classifier model loaded on Celery workers",
            "model_info": {"mode": "api_server"}
        }
    else:
        # Standalone mode - check local model
        if not model_loader.is_model_ready("classifier_model"):
            return {
                "status": "not_ready",
                "message": "Classifier model not loaded"
            }

        classifier = model_loader.models.get("classifier_model")
        if classifier:
            model_info = classifier.get_model_info()
            return {
                "status": "ready",
                "model_info": model_info
            }
        else:
            return {
                "status": "error",
                "message": "Classifier model not found",
                "model_info": {"error": "Model instance not found"}
            }

@router.post("/demo")
async def classifier_demo():
    """Demo endpoint with sample narrative"""
    demo_narrative = (
        "On 2023-05-15 a girl (age 16) from District X called to report sexual abuse by her stepfather. "
        "She is currently 2 months pregnant and being forced to abort. The stepfather has threatened to "
        "kill her if she doesn't comply. Her mother is also being abused."
    )
    
    request = ClassifierRequest(narrative=demo_narrative)
    return await classify_narrative(request)
