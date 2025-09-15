import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..model_scripts.qa_model import qa_model

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/qa", tags=["quality_assurance"])

# --- Pydantic Models ---
class QARequest(BaseModel):
    transcript: str = Field(..., min_length=10, description="The call center transcript to be evaluated.")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Classification threshold. Uses model default if not provided.")
    return_raw: bool = Field(False, description="If true, include raw prediction probabilities in the response.")

class SubmetricResult(BaseModel):
    submetric: str
    prediction: bool
    score: str
    probability: Optional[float] = None

class QAResponse(BaseModel):
    evaluations: Dict[str, List[SubmetricResult]]
    processing_time: float
    model_info: dict
    timestamp: str

# --- API Endpoints ---
@router.post("/evaluate", response_model=QAResponse)
async def evaluate_transcript(request: QARequest):
    """Evaluate call center transcript against QA metrics"""
    
    if not qa_model.is_ready():
        raise HTTPException(
            status_code=503, 
            detail="QA model not ready. Check /health/models for status."
        )
    
    if not request.transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty"
        )
    
    try:
        start_time = datetime.now()
        
        evaluation = qa_model.predict(
            request.transcript,
            threshold=request.threshold,
            return_raw=request.return_raw
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = qa_model.get_model_info()
        
        # logger.info(f"QA evaluation processed {len(request.transcript)} chars in {processing_time:.3f}s")
        
        return QAResponse(
            evaluations=evaluation,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"QA evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )
    

@router.get("/info")
async def get_qa_info():
    """Get QA model information"""
    if not qa_model.is_ready():
        # Return the error from the model if loading failed
        return {"status": "not_ready", "message": "QA model not loaded", "error": qa_model.error}

    return {"status": "ready", "model_info": qa_model.get_model_info()}

@router.post("/demo")
async def qa_demo():
    """Demo endpoint with sample transcript"""
    demo_transcript = (
        "Agent: Good morning! Thank you for calling TechSupport. My name is Alex. How can I help you today? "
        "Customer: Hi, I'm having issues with my internet connection. "
        "Agent: I'm sorry to hear that. Let me help you with that. Could you please tell me what exactly is happening? "
        "Customer: It keeps disconnecting every few minutes. "
        "Agent: I understand how frustrating that must be. Let me check your connection settings. "
        "Could you please hold for a moment while I investigate this? "
        "Agent: Thank you for holding. I've found the issue. "
        "I'll guide you through the steps to fix it. First, please open your network settings..."
    )
    
    request = QARequest(transcript=demo_transcript, return_raw=True)
    return await evaluate_transcript(request)
