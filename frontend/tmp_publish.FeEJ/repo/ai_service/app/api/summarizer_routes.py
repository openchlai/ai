from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import logging

from ..model_scripts.model_loader import model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/summarizer", tags=["summarizer"])


# Request model
class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 256


# Response model
class SummarizationResponse(BaseModel):
    summary: str
    processing_time: float
    model_info: Dict
    timestamp: str


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text_endpoint(request: SummarizationRequest):
    """Summarize a given text"""

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")

    if not model_loader.is_model_ready("summarizer"):
        raise HTTPException(
            status_code=503,
            detail="Summarizer model not ready. Check /health/models for status."
        )

    summarizer_model = model_loader.models.get("summarizer")
    if not summarizer_model:
        raise HTTPException(status_code=503, detail="Summarizer model not available")

    try:
        start_time = datetime.now()

        # Generate summary
        summary = summarizer_model.summarize(request.text, max_length=request.max_length)

        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = summarizer_model.get_model_info()

        logger.info(f"✅ Summarizer processed {len(request.text)} characters in {processing_time:.2f}s")

        return SummarizationResponse(
            summary=summary,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.exception("❌ Summarization failed")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/info")
async def get_summarizer_info():
    """Get summarizer model information"""
    if not model_loader.is_model_ready("summarizer"):
        return {"status": "not_ready", "message": "Summarizer model not loaded"}

    summarizer_model = model_loader.models.get("summarizer")
    if summarizer_model:
        return {"status": "ready", "model_info": summarizer_model.get_model_info()}
    return {"status": "error", "message": "Summarizer model not found"}


@router.post("/demo", response_model=SummarizationResponse)
async def summarizer_demo():
    """Demo endpoint with sample text"""
    demo_text = (
        "Artificial intelligence (AI) refers to the simulation of human intelligence "
        "in machines that are programmed to think and learn like humans. It is a field "
        "of computer science that aims to create systems capable of performing tasks that "
        "normally require human intelligence, such as visual perception, speech recognition, "
        "decision-making, and language translation."
    )

    request = SummarizationRequest(text=demo_text, max_length=60)
    return await summarize_text_endpoint(request)
