from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import logging

from ..model_scripts.model_loader import model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translate", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    translated: str
    processing_time: float
    model_info: Dict
    timestamp: str

@router.post("/", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    if not model_loader.is_model_ready("translator"):
        raise HTTPException(
            status_code=503,
            detail="Translation model not ready. Check /health/models for status."
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text input cannot be empty"
        )

    try:
        start_time = datetime.now()

        translator_model = model_loader.models.get("translator")
        if not translator_model:
            raise HTTPException(
                status_code=503,
                detail="Translator model not available"
            )

        translated = translator_model.translate(request.text)
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = translator_model.get_model_info()

        logger.info(f"Translated {len(request.text)} chars in {processing_time:.3f}s")

        return TranslationResponse(
            translated=translated,
            processing_time=processing_time,
            model_info=model_info,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.get("/info")
async def get_translation_info():
    if not model_loader.is_model_ready("translator"):
        return {
            "status": "not_ready",
            "message": "Translation model not loaded"
        }

    translator_model = model_loader.models.get("translator")
    if translator_model:
        return {
            "status": "ready",
            "model_info": translator_model.get_model_info()
        }
    else:
        return {
            "status": "error",
            "message": "Translation model not found"
        }
