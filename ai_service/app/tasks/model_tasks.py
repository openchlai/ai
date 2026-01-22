import logging
from datetime import datetime
from typing import Dict, Any, Optional
from celery.signals import worker_init
import os

from ..celery_app import celery_app
from ..model_scripts.model_loader import model_loader
from ..utils.text_utils import (
    NERChunker,
    ClassificationChunker,
    ClassificationAggregator,
    SummarizationChunker,
    TranslationChunker
)
from ..core.metrics import (
    track_model_time,
    model_processing_seconds,
    model_operations_total,
    update_model_status
)

logger = logging.getLogger(__name__)

# Global model loader for Celery worker
worker_model_loader = None


@worker_init.connect
def initialize_model_worker(**kwargs):
    """Initialize models when worker starts"""
    global worker_model_loader
    
    logger.info(" Initializing model worker for individual model tasks...")
    
    try:
        from ..model_scripts.model_loader import ModelLoader
        
        worker_model_loader = ModelLoader()
        
        # Use synchronous loading method
        success = worker_model_loader.load_all_models_sync()
        
        if success:
            ready_models = worker_model_loader.get_ready_models()
            logger.info(f" Model worker initialized with {len(ready_models)} models: {ready_models}")
            
            if len(ready_models) == 0:
                logger.error(" WARNING: No models were loaded successfully!")
                logger.error(f"Failed models: {worker_model_loader.get_failed_models()}")
                logger.error(f"Blocked models: {worker_model_loader.get_blocked_models()}")
        else:
            logger.error(" Model loading failed")
            worker_model_loader = None
        
    except Exception as e:
        logger.error(f" Failed to initialize model worker: {e}")
        logger.exception("Full traceback:")
        worker_model_loader = None


def get_worker_model_loader():
    """Get the worker's model loader instance"""
    global worker_model_loader
    if worker_model_loader is None:
        raise RuntimeError("Model loader not initialized in worker")
    return worker_model_loader



# NER TASK

@celery_app.task(bind=True, name="ner_extract_task")
def ner_extract_task(self, text: str, flat: bool = True) -> Dict[str, Any]:
    """
    Extract named entities from text using Celery task

    Args:
        text: Input text for NER
        flat: Return flat list (True) or grouped by label (False)

    Returns:
        Dictionary with entities, processing time, and model info
    """
    start_time = datetime.now()
    try:
        # Update task state
        self.update_state(state='PROCESSING', meta={'status': 'Extracting entities...'})

        # Get model loader
        loader = get_worker_model_loader()

        if not loader.is_model_ready("ner"):
            model_operations_total.labels(model="ner", operation="extract", status="failure").inc()
            raise RuntimeError("NER model not ready")

        ner_model = loader.models.get("ner")
        if not ner_model:
            model_operations_total.labels(model="ner", operation="extract", status="failure").inc()
            raise RuntimeError("NER model not available")
        
        # Initialize chunker
        tokenizer_name = "distilbert-base-uncased"
        chunker = NERChunker(tokenizer_name=tokenizer_name, max_tokens=512)
        
        # Count tokens
        token_count = chunker.count_tokens(text)
        MAX_SOURCE_LENGTH = 512
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct entity extraction
            entities = ner_model.extract_entities(text, flat=flat)
            logger.info(f" NER processed {len(text)} chars (no chunking)")
        else:
            # Chunking needed
            logger.info(f"📦 Chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            chunks = chunker.chunk_transcript(text)
            chunk_entities = []
            
            for i, chunk_info in enumerate(chunks):
                chunk_ent = ner_model.extract_entities(chunk_info['text'], flat=True)
                chunk_entities.append(chunk_ent)
                logger.debug(f"  Chunk {i+1}/{len(chunks)}: {len(chunk_ent)} entities")
            
            # Reconstruct entities
            entities = chunker.reconstruct_entities(chunk_entities, chunks, flat=flat)
            logger.info(f" Processed {len(chunks)} chunks, {len(entities)} entities")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = ner_model.get_model_info()

        # Track metrics
        model_processing_seconds.labels(model="ner", operation="extract").observe(processing_time)
        model_operations_total.labels(model="ner", operation="extract", status="success").inc()

        return {
            "entities": entities,
            "processing_time": processing_time,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat(),
            "task_id": self.request.id
        }

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_processing_seconds.labels(model="ner", operation="extract").observe(processing_time)
        model_operations_total.labels(model="ner", operation="extract", status="failure").inc()
        logger.error(f" NER task failed: {e}")
        raise



# CLASSIFIER TASK

@celery_app.task(bind=True, name="classifier_classify_task")
def classifier_classify_task(self, narrative: str) -> Dict[str, Any]:
    """
    Classify case narrative using Celery task

    Args:
        narrative: Case narrative text

    Returns:
        Dictionary with classification results
    """
    start_time = datetime.now()
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Classifying narrative...'})

        loader = get_worker_model_loader()

        if not loader.is_model_ready("classifier_model"):
            model_operations_total.labels(model="classifier", operation="classify", status="failure").inc()
            raise RuntimeError("Classifier model not ready")

        classifier = loader.models.get("classifier_model")
        if not classifier:
            model_operations_total.labels(model="classifier", operation="classify", status="failure").inc()
            raise RuntimeError("Classifier model not available")
        
        # Initialize chunker
        tokenizer_name = "distilbert-base-uncased"
        chunker = ClassificationChunker(
            tokenizer_name=tokenizer_name,
            max_tokens=512,
            overlap_tokens=150
        )
        
        token_count = chunker.count_tokens(narrative)
        MAX_SOURCE_LENGTH = 512
        
        logger.info(f"🔍 Classification: {token_count} tokens")
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct classification
            classification = classifier.classify(narrative)

            aggregated_result = {
                'main_category': classification['main_category'],
                'sub_category': classification['sub_category'],
                'sub_category_2': classification.get('sub_category_2'),  # ← FIXED: Include top-2 subcategory
                'intervention': classification['intervention'],
                'priority': classification['priority'],
                'confidence_scores': classification.get('confidence_breakdown', {}),
                'chunks_processed': 1,
                'chunk_predictions': None
            }


        else:
            # Chunking needed
            logger.info(f"📦 Chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            chunks = chunker.chunk_transcript(narrative)
            chunk_predictions = []
            
            for i, chunk_info in enumerate(chunks):
                logger.info(f" Processing chunk {i+1}/{len(chunks)}")
                chunk_classification = classifier.classify(chunk_info['text'])
                
                chunk_pred = {
                    'main_category': chunk_classification['main_category'],
                    'sub_category': chunk_classification['sub_category'],
                    'sub_category_2': chunk_classification.get('sub_category_2'), 
                    'intervention': chunk_classification['intervention'],
                    'priority': chunk_classification['priority'],
                    'confidence_scores': chunk_classification.get('confidence_breakdown', {})
                }
                chunk_predictions.append(chunk_pred)
            
            # Aggregate predictions
            aggregator = ClassificationAggregator()
            aggregated_result = aggregator.aggregate_case_classification(chunk_predictions)
            aggregated_result['chunks_processed'] = len(chunks)
            
            # Build chunk prediction objects
            chunk_pred_objects = []
            for i, chunk in enumerate(chunks):
                chunk_pred_objects.append({
                    'chunk_index': chunk['chunk_index'],
                    'token_count': chunk['token_count'],
                    'sentence_count': chunk['sentence_count'],
                    'position_ratio': chunk['position_ratio'],
                    **chunk_predictions[i]
                })
            
            aggregated_result['chunk_predictions'] = chunk_pred_objects
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = classifier.get_model_info()

        # Track metrics
        model_processing_seconds.labels(model="classifier", operation="classify").observe(processing_time)
        model_operations_total.labels(model="classifier", operation="classify", status="success").inc()

        logger.info(f" Classification complete: {processing_time:.3f}s")

        return {
            **aggregated_result,
            "processing_time": processing_time,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat(),
            "task_id": self.request.id
        }

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_processing_seconds.labels(model="classifier", operation="classify").observe(processing_time)
        model_operations_total.labels(model="classifier", operation="classify", status="failure").inc()
        logger.error(f" Classification task failed: {e}")
        raise



# TRANSLATION TASK

@celery_app.task(bind=True, name="translation_translate_task")
def translation_translate_task(self, text: str) -> Dict[str, Any]:
    """
    Translate text using Celery task

    Args:
        text: Text to translate

    Returns:
        Dictionary with translation results
    """
    start_time = datetime.now()
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Translating text...'})

        loader = get_worker_model_loader()

        if not loader.is_model_ready("translator"):
            model_operations_total.labels(model="translator", operation="translate", status="failure").inc()
            raise RuntimeError("Translation model not ready")

        translator_model = loader.models.get("translator")
        if not translator_model:
            model_operations_total.labels(model="translator", operation="translate", status="failure").inc()
            raise RuntimeError("Translator model not available")
        
        # Initialize chunker
        tokenizer_name = "openchs/sw-en-opus-mt-mul-en-v1"
        chunker = TranslationChunker(tokenizer_name=tokenizer_name, max_tokens=512)
        
        token_count = chunker.count_tokens(text)
        MAX_SOURCE_LENGTH = 512
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct translation
            translated = translator_model.translate(text)
            logger.info(f" Translated {len(text)} chars (no chunking)")
        else:
            # Chunking needed
            logger.info(f"📦 Chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            chunks = chunker.chunk_transcript(text)
            translated_chunks = []
            
            for i, chunk_info in enumerate(chunks):
                chunk_translated = translator_model.translate(chunk_info['text'])
                translated_chunks.append(chunk_translated)
                logger.debug(f"  Chunk {i+1}/{len(chunks)} translated")
            
            # Reconstruct translation
            translated = chunker.reconstruct_translation(translated_chunks)
            logger.info(f" Processed {len(chunks)} chunks")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = translator_model.get_model_info()

        # Track metrics
        model_processing_seconds.labels(model="translator", operation="translate").observe(processing_time)
        model_operations_total.labels(model="translator", operation="translate", status="success").inc()

        logger.info(f" Translation complete: {processing_time:.3f}s")

        return {
            "translated": translated,
            "processing_time": processing_time,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat(),
            "task_id": self.request.id
        }

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_processing_seconds.labels(model="translator", operation="translate").observe(processing_time)
        model_operations_total.labels(model="translator", operation="translate", status="failure").inc()
        logger.error(f" Translation task failed: {e}")
        raise



# SUMMARIZATION TASK

@celery_app.task(bind=True, name="summarization_summarize_task")
def summarization_summarize_task(self, text: str, max_length: int = 256) -> Dict[str, Any]:
    """
    Summarize text using Celery task

    Args:
        text: Text to summarize
        max_length: Maximum summary length

    Returns:
        Dictionary with summary results
    """
    start_time = datetime.now()
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Summarizing text...'})

        loader = get_worker_model_loader()

        if not loader.is_model_ready("summarizer"):
            model_operations_total.labels(model="summarizer", operation="summarize", status="failure").inc()
            raise RuntimeError("Summarizer model not ready")

        summarizer_model = loader.models.get("summarizer")
        if not summarizer_model:
            model_operations_total.labels(model="summarizer", operation="summarize", status="failure").inc()
            raise RuntimeError("Summarizer model not available")
        
        # Initialize chunker
        tokenizer_name = "openchs/sum-flan-t5-base-synthetic-v1"
        chunker = SummarizationChunker(
            tokenizer_name=tokenizer_name,
            max_tokens=512,
            overlap_tokens=0
        )
        
        prompt_prefix = "Summarize the following child helpline case call transcript: "
        full_input = prompt_prefix + text
        token_count = chunker.count_tokens(full_input)
        MAX_SOURCE_LENGTH = 512
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct summarization
            summary = summarizer_model.summarize(text, max_length=max_length)
        else:
            # Chunking needed
            logger.info(f"📦 Chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            chunks = chunker.chunk_transcript(text)
            chunk_summaries = []
            
            for i, chunk_info in enumerate(chunks):
                chunk_summary = summarizer_model.summarize(
                    chunk_info['text'], 
                    max_length=max_length
                )
                chunk_summaries.append(chunk_summary)
            
            # Reconstruct summary
            summary = chunker.reconstruct_summary(chunk_summaries)
            logger.info(f" Processed {len(chunks)} chunks")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = summarizer_model.get_model_info()

        # Track metrics
        model_processing_seconds.labels(model="summarizer", operation="summarize").observe(processing_time)
        model_operations_total.labels(model="summarizer", operation="summarize", status="success").inc()

        logger.info(f" Summarization complete: {processing_time:.2f}s")

        return {
            "summary": summary,
            "processing_time": processing_time,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat(),
            "task_id": self.request.id
        }

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_processing_seconds.labels(model="summarizer", operation="summarize").observe(processing_time)
        model_operations_total.labels(model="summarizer", operation="summarize", status="failure").inc()
        logger.error(f" Summarization task failed: {e}")
        raise


# QA TASK
@celery_app.task(bind=True, name="qa_evaluate_task")
def qa_evaluate_task(
    self,
    transcript: str,
    threshold: Optional[float] = None,
    return_raw: bool = False
) -> Dict[str, Any]:
    """
    Evaluate transcript for quality assurance using Celery task

    Args:
        transcript: Call transcript to evaluate
        threshold: Classification threshold
        return_raw: Include raw probabilities

    Returns:
        Dictionary with QA evaluation results
    """
    start_time = datetime.now()
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Evaluating transcript...'})

        loader = get_worker_model_loader()

        # Import QA model
        from ..model_scripts.qa_model import qa_model

        if not qa_model.is_ready():
            model_operations_total.labels(model="qa", operation="evaluate", status="failure").inc()
            raise RuntimeError("QA model not ready")
        
        # Initialize chunker
        tokenizer_name = "distilbert-base-uncased"
        chunker = ClassificationChunker(
            tokenizer_name=tokenizer_name,
            max_tokens=512,
            overlap_tokens=150
        )
        
        token_count = chunker.count_tokens(transcript)
        MAX_SOURCE_LENGTH = 512
        
        if token_count <= MAX_SOURCE_LENGTH:
            # Direct evaluation
            logger.info(f"✅ QA evaluation - no chunking: {token_count} tokens")
            evaluation_result = qa_model.predict(
                transcript,
                threshold=threshold,
                return_raw=return_raw
            )
        else:
            # Chunking needed
            logger.info(f"📦 QA chunking: {token_count} tokens > {MAX_SOURCE_LENGTH}")
            
            chunks = chunker.chunk_transcript(transcript)
            
            # Evaluate each chunk
            chunk_predictions = []
            for i, chunk_item in enumerate(chunks):
                logger.info(f"  Processing chunk {i+1}/{len(chunks)}")
                
                chunk_result = qa_model.predict(
                    chunk_item['text'],
                    threshold=threshold,
                    return_raw=True
                )
                chunk_predictions.append(chunk_result)
            
            # Aggregate results
            logger.info(f"🔗 Aggregating {len(chunk_predictions)} predictions")
            aggregator = ClassificationAggregator()
            aggregated_result = aggregator.aggregate_qa_scoring(chunk_predictions)
            
            if aggregated_result and aggregated_result['success']:
                evaluation_result = aggregated_result['predictions']
            else:
                # Fallback aggregation
                logger.error("QA aggregation failed, using fallback")
                evaluation_result = _fallback_qa_aggregation(chunk_predictions)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = qa_model.get_model_info()

        # Track metrics
        model_processing_seconds.labels(model="qa", operation="evaluate").observe(processing_time)
        model_operations_total.labels(model="qa", operation="evaluate", status="success").inc()

        logger.info(f"✅ QA evaluation complete: {processing_time:.3f}s")

        return {
            "evaluations": evaluation_result,
            "processing_time": processing_time,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat(),
            "task_id": self.request.id
        }

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_processing_seconds.labels(model="qa", operation="evaluate").observe(processing_time)
        model_operations_total.labels(model="qa", operation="evaluate", status="failure").inc()
        logger.error(f"❌ QA task failed: {e}")
        raise

def _fallback_qa_aggregation(chunk_predictions):
    """Fallback aggregation for QA if primary method fails"""
    if not chunk_predictions:
        return {}
    
    aggregated_result = {}
    first_chunk = chunk_predictions[0]
    
    for category, metrics in first_chunk.items():
        if not isinstance(metrics, list):
            continue
            
        aggregated_result[category] = []
        
        for metric_idx, metric_template in enumerate(metrics):
            metric_name = metric_template['submetric']
            predictions = []
            probabilities = []
            
            for chunk_pred in chunk_predictions:
                if category in chunk_pred and isinstance(chunk_pred[category], list):
                    if metric_idx < len(chunk_pred[category]):
                        chunk_metric = chunk_pred[category][metric_idx]
                        if chunk_metric['submetric'] == metric_name:
                            predictions.append(chunk_metric['prediction'])
                            probabilities.append(chunk_metric.get('probability', 0.5))
            
            if predictions:
                final_prediction = sum(predictions) > len(predictions) / 2
                avg_probability = sum(probabilities) / len(probabilities)
                
                aggregated_result[category].append({
                    'submetric': metric_name,
                    'prediction': final_prediction,
                    'score': '✓' if final_prediction else '✗',
                    'probability': float(avg_probability)
                })
    
    return aggregated_result



# WHISPER TASK (for audio transcription)

@celery_app.task(bind=True, name="whisper_transcribe_task")
def whisper_transcribe_task(
    self,
    audio_bytes: bytes,
    filename: str,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribe audio using Celery task

    Args:
        audio_bytes: Audio file bytes
        filename: Original filename
        language: Language code or 'auto'

    Returns:
        Dictionary with transcription results
    """
    start_time = datetime.now()
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Transcribing audio...'})

        loader = get_worker_model_loader()

        if not loader.is_model_ready("whisper"):
            model_operations_total.labels(model="whisper", operation="transcribe", status="failure").inc()
            raise RuntimeError("Whisper model not ready")

        whisper_model = loader.models.get("whisper")
        if not whisper_model:
            model_operations_total.labels(model="whisper", operation="transcribe", status="failure").inc()
            raise RuntimeError("Whisper model not available")
        
        # Transcribe audio
        transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        model_info = whisper_model.get_model_info()

        # Audio info
        audio_info = {
            "filename": filename,
            "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
            "format": os.path.splitext(filename)[1].lower()
        }

        # Track metrics
        model_processing_seconds.labels(model="whisper", operation="transcribe").observe(processing_time)
        model_operations_total.labels(model="whisper", operation="transcribe", status="success").inc()

        logger.info(f"🎙️ Transcribed {filename} in {processing_time:.2f}s")

        return {
            "transcript": transcript,
            "language": language,
            "processing_time": processing_time,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat(),
            "audio_info": audio_info,
            "task_id": self.request.id
        }

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        model_processing_seconds.labels(model="whisper", operation="transcribe").observe(processing_time)
        model_operations_total.labels(model="whisper", operation="transcribe", status="failure").inc()
        logger.error(f" Whisper task failed: {e}")
        raise