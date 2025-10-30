from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import logging

from ..model_scripts.model_loader import model_loader
from ..utils.text_utils import TranslationChunker

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
    """Translate text with automatic chunking for long inputs"""

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
        # Define translation tokenizer name for chunking
        tokenizer_name = "openchs/sw-en-opus-mt-mul-en-v1"
        
        # Initialize chunker with configuration
        chunker = TranslationChunker(
            tokenizer_name=tokenizer_name,
            max_tokens=512
        )
        
        # Count tokens
        token_count = chunker.count_tokens(request.text)
        MAX_SOURCE_LENGTH = 512
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct translation for short text
            translated = translator_model.translate(request.text)
            logger.info(f" Translated {len(request.text)} chars (no chunking needed)")
        else:
            # Chunking needed for long text
            logger.info(f" Applying chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            # Create chunks
            chunks = chunker.chunk_transcript(request.text)
            
            # Translate each chunk
            translated_chunks = []
            for i, chunk_info in enumerate(chunks):
                chunk_translated = translator_model.translate(chunk_info['text'])
                translated_chunks.append(chunk_translated)
                logger.debug(f"  Chunk {i+1}/{len(chunks)} translated")
            
            # Reconstruct final translation (joins with spaces)
            translated = chunker.reconstruct_translation(translated_chunks)
            
            logger.info(f" Processed {len(chunks)} chunks")
        


        # translated = translator_model.translate(request.text)
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
        model_info = translator_model.get_model_info()
        return {
            "status": "ready",
            "model_info": model_info
        }
    else:
        return {
            "status": "error",
            "message": "Translation model not found",
            "model_info": {"error": "Model instance not found"}
        }
