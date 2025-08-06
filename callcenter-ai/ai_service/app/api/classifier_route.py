from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime

from ..models.model_loader import model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/classifier", tags=["classifier"])

class ClassifierRequest(BaseModel):
    narrative: str

class ClassifierResponse(BaseModel):
    main_category: str
    sub_category: str
    intervention: str
    priority: str
    processing_time: float
    model_info: dict
    timestamp: str

@router.post("/classify", response_model=ClassifierResponse)
async def classify_narrative(request: ClassifierRequest):
    """Classify case narrative into categories"""
    
    # Check if classifier model is loaded
    if not model_loader.is_model_ready("classifier_model"):
        raise HTTPException(
            status_code=503, 
            detail="Classifier model not ready. Check /health/models for status."
        )
    
    if not request.narrative.strip():
        raise HTTPException(
            status_code=400,
            detail="Narrative input cannot be empty"
        )
    
    try:
        start_time = datetime.now()
        
        # Get the loaded classifier model
        classifier = model_loader.models.get("classifier_model")
        if not classifier:
            raise HTTPException(
                status_code=503,
                detail="Classifier model not available"
            )
        
        # Classify narrative
        classification = classifier.classify(request.narrative)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Get model info
        model_info = classifier.get_model_info()
        
        logger.info(f"Classifier processed {len(request.narrative)} chars in {processing_time:.3f}s")
        
        return ClassifierResponse(
            **classification,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )

@router.get("/info")
async def get_classifier_info():
    """Get classifier model information"""
    if not model_loader.is_model_ready("classifier_model"):
        return {
            "status": "not_ready",
            "message": "Classifier model not loaded"
        }

    classifier = model_loader.models.get("classifier_model")
    if classifier:
        return {
            "status": "ready",
            "model_info": classifier.get_model_info()
        }
    else:
        return {
            "status": "error",
            "message": "Classifier model not found"
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