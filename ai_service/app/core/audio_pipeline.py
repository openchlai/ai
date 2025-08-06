# app/core/audio_pipeline.py (Enhanced)
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from .resource_manager import resource_manager
from .request_queue import request_queue, RequestStatus
from ..models.model_loader import model_loader

logger = logging.getLogger(__name__)


class AudioPipelineService:
    """Orchestrates complete audio-to-insights pipeline with queue integration"""
    
    def __init__(self):
        self.is_ready = False
        self.processing_tasks: Dict[str, asyncio.Task] = {}
    
    def check_pipeline_readiness(self) -> Dict[str, Any]:
        """Check if all required models are ready"""
        required_models = ["whisper", "ner", "classifier_model", "translator", "summarizer","all_qa_distilbert_v1"]
        model_status = {}
        all_ready = True
        
        for model_name in required_models:
            is_ready = model_loader.is_model_ready(model_name)
            model_status[model_name] = is_ready
            if not is_ready:
                all_ready = False
        
        self.is_ready = all_ready
        
        return {
            "pipeline_ready": all_ready,
            "models": model_status,
            "missing_models": [name for name, ready in model_status.items() if not ready]
        }
    async def submit_audio_request(
        self, 
        audio_bytes: bytes, 
        filename: str,
        language: Optional[str] = None,
        include_translation: bool = True,
        include_insights: bool = True,
        background: bool = True
    ) -> Dict[str, Any]:
        """
        Submit audio processing request - returns immediately with request_id if background=True
        """
        
        # Check pipeline readiness
        readiness = self.check_pipeline_readiness()
        if not readiness["pipeline_ready"]:
            raise RuntimeError(f"Pipeline not ready. Missing models: {readiness['missing_models']}")
        
        if background:
            # Background processing - return request_id immediately
            request_id = await request_queue.add_request("audio_processing", priority=5)
            
            # Store request data (in production, use Redis or database)
            request_data = {
                "audio_bytes": audio_bytes,
                "filename": filename,
                "language": language,
                "include_translation": include_translation,
                "include_insights": include_insights
            }
            
            # Start background processing
            asyncio.create_task(
                self._process_audio_background(request_id, request_data)
            )
            # self.processing_tasks[request_id] = task
            
            return {
                "request_id": request_id,
                "status": "queued",
                "message": "Audio processing started. Check status at /queue/status/{request_id}",
                "estimated_time": "15-45 seconds",
                "status_endpoint": f"/queue/status/{request_id}"
            }
        else:
            # Synchronous processing with queue integration
            request_id = await request_queue.add_request("audio_processing_sync", priority=1)
            
            try:
                result = await self._process_audio_with_queue(
                    request_id, audio_bytes, filename, language, 
                    include_translation, include_insights
                )
                request_queue.complete_request(request_id, result=result)
                return result
                
            except Exception as e:
                request_queue.complete_request(request_id, error=str(e))
                raise
    
    # In _process_audio_background method
    async def _process_audio_background(self, request_id: str, request_data: Dict):
        logger.info(f"🔄 [{request_id}] Background processing started")
        
        try:
            # Update status to processing
            request_queue.update_request_status(request_id, "processing")
            
            result = await self._process_audio_with_queue(...)
            
            # Mark as completed
            logger.info(f"✅ [{request_id}] Completing request with result")
            request_queue.complete_request(request_id, result=result)
            logger.info(f"✅ [{request_id}] Request marked as completed")
            
        except Exception as e:
            logger.error(f"❌ [{request_id}] Background processing failed: {e}")
            request_queue.complete_request(request_id, error=str(e))
        
        # Verify final status
        final_status = request_queue.get_request_status(request_id)
        logger.info(f"🔍 [{request_id}] Final status: {final_status}")
        
        # finally:
        #     # Cleanup
        #     if request_id in self.processing_tasks:
        #         del self.processing_tasks[request_id]
    
    async def _process_audio_with_queue(
            self, 
            request_id: str,
            audio_bytes: bytes, 
            filename: str,
            language: Optional[str] = None,
            qa_threshold: Optional[int] = None,
            return_raw: Optional[bool] = False,
            include_translation: bool = True,
            include_insights: bool = True
        ) -> Dict[str, Any]:
            """
            Process audio with proper queue and resource management integration
            Enhanced with intelligent text chunking for long-form audio
            """
            
            start_time = datetime.now()
            processing_steps = {}
            
            try:
                # Update queue status - starting processing
                if request_id in request_queue.requests:
                    request_queue.requests[request_id].status = RequestStatus.PROCESSING
                
                # Step 1: Audio Transcription (GPU intensive - use resource manager)
                logger.info(f"🎙️ [{request_id}] Starting audio transcription...")
                step_start = datetime.now()
                
                # Proper resource management integration
                if not await resource_manager.acquire_gpu(request_id):
                    raise RuntimeError("Failed to acquire GPU resources")
                
                try:
                    whisper_model = model_loader.models.get("whisper")
                    transcript = whisper_model.transcribe_audio_bytes(audio_bytes, language=language)
                finally:
                    resource_manager.release_gpu(request_id)
                
                processing_steps["transcription"] = {
                    "duration": (datetime.now() - step_start).total_seconds(),
                    "status": "completed",
                    "output_length": len(transcript),
                    "chunking_applied": False  # Whisper handles its own chunking
                }
                logger.info(f"✅ [{request_id}] Transcription completed: {len(transcript)} characters")
                
                # Step 2: Enhanced Translation with Chunking Support
                translation = None
                translation_info = {}
                if include_translation:
                    logger.info(f"🌐 [{request_id}] Starting translation with chunking support...")
                    step_start = datetime.now()
                    
                    try:
                        translator_model = model_loader.models.get("translator")
                        
                        # Use chunking-aware translation
                        translation = translator_model.translate_with_fallback(transcript)
                        
                        # Get translation strategy info
                        translation_info = {
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "completed" if translation else "failed",
                            "output_length": len(translation) if translation else 0,
                            "strategy": "chunked" if len(transcript) > 2000 else "single_pass",
                            "estimated_chunks": self._estimate_chunks_needed(transcript, "translation")
                        }
                        
                        if translation:
                            logger.info(f"✅ [{request_id}] Translation completed: {len(translation)} characters ({translation_info['strategy']})")
                        else:
                            logger.warning(f"⚠️ [{request_id}] Translation failed, continuing without translation")
                        
                    except Exception as e:
                        logger.error(f"❌ [{request_id}] Translation failed: {e}")
                        translation_info = {
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "failed",
                            "error": str(e),
                            "fallback_applied": True
                        }
                        translation = None
                    
                    processing_steps["translation"] = translation_info
                
                # Step 3: Determine text for NLP models with length analysis
                nlp_text = translation if translation else transcript
                nlp_source = "translated_text" if translation else "original_transcript"
                nlp_text_length = len(nlp_text)
                
                logger.info(f"🧠 [{request_id}] Starting NLP analysis on {nlp_source} ({nlp_text_length} chars)...")
                
                # Step 4: Enhanced Parallel NLP Processing with Chunking
                async def run_ner():
                    step_start = datetime.now()
                    try:
                        ner_model = model_loader.models.get("ner")
                        entities = ner_model.extract_entities(nlp_text, flat=False)
                        
                        return {
                            "result": entities,
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "completed",
                            "strategy": "chunked" if nlp_text_length > 1600 else "single_pass",
                            "entities_found": len(entities) if entities else 0
                        }
                    except Exception as e:
                        logger.error(f"❌ [{request_id}] NER failed: {e}")
                        return {
                            "result": {},
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "failed",
                            "error": str(e)
                        }
                
                async def run_classifier():
                    step_start = datetime.now()
                    try:
                        classifier_model = model_loader.models.get("classifier_model")
                        
                        # Use chunking-aware classification
                        classification = classifier_model.classify_with_fallback(nlp_text)
                        
                        return {
                            "result": classification,
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "completed",
                            "strategy": "chunked" if nlp_text_length > 1200 else "single_pass",
                            "confidence": classification.get("confidence", 0) if classification else 0,
                            "aggregation_applied": nlp_text_length > 1200
                        }
                    except Exception as e:
                        logger.error(f"❌ [{request_id}] Classification failed: {e}")
                        return {
                            "result": {},
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "failed",
                            "error": str(e)
                        }
                
                async def run_summarization():
                    step_start = datetime.now()
                    try:
                        summarizer_model = model_loader.models.get("summarizer")
                        
                        # Use chunking-aware summarization with appropriate length
                        target_length = min(150, max(50, nlp_text_length // 20))
                        summary = summarizer_model.summarize_with_fallback(
                            nlp_text, 
                            max_length=target_length,
                            min_length=min(40, target_length // 2)
                        )
                        
                        return {
                            "result": summary,
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "completed",
                            "strategy": "hierarchical" if nlp_text_length > 2000 else "single_pass",
                            "summary_length": len(summary) if summary else 0,
                            "compression_ratio": round(len(summary) / nlp_text_length * 100, 1) if summary and nlp_text_length > 0 else 0
                        }
                    except Exception as e:
                        logger.error(f"❌ [{request_id}] Summarization failed: {e}")
                        return {
                            "result": "",
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "failed",
                            "error": str(e)
                        }
                

                async def run_qa_model():
                    step_start = datetime.now()
                    try:
                        qa_model = model_loader.get('all_qa_distilbert_v1')

                        # qa_scores = qa_model.predict(nlp_text)                        
                        qa_scores = qa_model.predict(nlp_text, qa_threshold, return_raw)
                        return {
                            "result":qa_scores,
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "completed",
                            "strategy": "chunked" if nlp_text_length > 1200 else "single_pass",
                            "confidence": qa_scores.get("confidence", 0) if qa_scores else 0,
                            "aggregation_applied": nlp_text_length > 1200
                        }
                    except Exception as e:
                        logger.error(f"❌ [{request_id}] QA Scoring failed: {e}")
                        return {
                            "result": {},
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "failed",
                            "error": str(e)
                        }

                # Run all NLP tasks in parallel with enhanced error handling
                ner_task, classifier_task, summary_task , qa_scoring_task = await asyncio.gather(
                    run_ner(),
                    run_classifier(), 
                    run_summarization(),
                    run_qa_model(),
                    return_exceptions=True
                )
                
                # Extract results with enhanced error handling
                entities = ner_task.get("result", {}) if isinstance(ner_task, dict) else {}
                classification = classifier_task.get("result", {}) if isinstance(classifier_task, dict) else {}
                summary = summary_task.get("result", "") if isinstance(summary_task, dict) else ""
                qa_scores = qa_scoring_task.get("result", "") if isinstance(qa_scoring_task, dict) else ""
                logger.info(f" QA Scores: {qa_scores}")

                # Log task results
                logger.info(f"🔍 [{request_id}] NER result: {entities}"
                            f" | Classifier result: {classification} | Summary length: {len(summary)}"
                            f" | QA Scores: {qa_scores}")
                # Enhanced processing steps logging
                processing_steps.update({
                    "ner": {
                        "duration": ner_task.get("duration", 0),
                        "status": ner_task.get("status", "failed"),
                        "strategy": ner_task.get("strategy", "unknown"),
                        "entities_found": ner_task.get("entities_found", 0),
                        "text_source": nlp_source,
                        "error": ner_task.get("error") if ner_task.get("status") == "failed" else None
                    },
                    "classification": {
                        "duration": classifier_task.get("duration", 0),
                        "status": classifier_task.get("status", "failed"),
                        "strategy": classifier_task.get("strategy", "unknown"),
                        "confidence": classifier_task.get("confidence", 0),
                        "aggregation_applied": classifier_task.get("aggregation_applied", False),
                        "text_source": nlp_source,
                        "error": classifier_task.get("error") if classifier_task.get("status") == "failed" else None
                    },
                    "summarization": {
                        "duration": summary_task.get("duration", 0),
                        "status": summary_task.get("status", "failed"),
                        "strategy": summary_task.get("strategy", "unknown"),
                        "summary_length": summary_task.get("summary_length", 0),
                        "compression_ratio": summary_task.get("compression_ratio", 0),
                        "text_source": nlp_source,
                        "error": summary_task.get("error") if summary_task.get("status") == "failed" else None
                    },
                    "qa_scorring":{
                        "duration": qa_scoring_task.get("duration", 0),
                        "status": qa_scoring_task.get("status", "failed"),
                        "strategy": qa_scoring_task.get("strategy", "unknown"),
                        "text_source": nlp_source,
                        "error": qa_scoring_task.get("error") if qa_scoring_task.get("status") == "failed" else None


                    }
                    
                    
                })
                
                # Calculate successful processing ratio
                successful_steps = sum(1 for step in [ner_task, classifier_task, summary_task, qa_scoring_task] 
                                    if isinstance(step, dict) and step.get("status") == "completed")
                processing_success_rate = (successful_steps / 3) * 100
                
                logger.info(f"✅ [{request_id}] NLP processing completed using {nlp_source} "
                        f"(Success rate: {processing_success_rate:.1f}%)")
                
                # Step 5: Enhanced Insights Generation
                insights = {}
                if include_insights:
                    logger.info(f"🔍 [{request_id}] Generating enhanced case insights...")
                    step_start = datetime.now()
                    
                    try:
                        insights = self._generate_insights(
                            transcript, translation, entities, classification, summary, qa_scores, processing_steps
                        )
                        processing_steps["insights"] = {
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "completed",
                            "insight_categories": len(insights.keys()) if insights else 0
                        }
                    except Exception as e:
                        logger.warning(f"⚠️ [{request_id}] Insights generation failed: {e}")
                        processing_steps["insights"] = {
                            "duration": (datetime.now() - step_start).total_seconds(),
                            "status": "failed",
                            "error": str(e)
                        }
                
                # Calculate total processing time
                total_processing_time = (datetime.now() - start_time).total_seconds()
                
                # Build enhanced response with chunking information
                result = {
                    "request_id": request_id,
                    "audio_info": {
                        "filename": filename,
                        "file_size_mb": round(len(audio_bytes) / (1024 * 1024), 2),
                        "language_specified": language,
                        "processing_time": total_processing_time
                    },
                    "transcript": transcript,
                    "translation": translation,
                    "nlp_processing_info": {
                        "text_used_for_nlp": nlp_source,
                        "nlp_text_length": nlp_text_length,
                        "chunking_analysis": {
                            "text_length_category": self._categorize_text_length(nlp_text_length),
                            "estimated_chunks": {
                                "translation": self._estimate_chunks_needed(nlp_text, "translation"),
                                "classification": self._estimate_chunks_needed(nlp_text, "classification"),
                                "summarization": self._estimate_chunks_needed(nlp_text, "summarization")
                            },
                            "processing_strategies_used": {
                                "translation": translation_info.get("strategy", "not_applicable"),
                                "ner": processing_steps["ner"]["strategy"],
                                "classification": processing_steps["classification"]["strategy"],
                                "summarization": processing_steps["summarization"]["strategy"]
                            }
                        },
                        "processing_success_rate": processing_success_rate
                    },
                    "entities": entities,
                    "classification": classification,
                    "summary": summary,
                    "qa_scores": qa_scores,
                    "insights": insights if include_insights else None,
                    "processing_steps": processing_steps,
                    "pipeline_info": {
                        "total_time": total_processing_time,
                        "models_used": ["whisper"] + (["translator"] if include_translation else []) + ["ner", "classifier", "summarizer", "qa_scorer"],
                        "text_flow": f"transcript → {nlp_source} → chunked_nlp_models",
                        "chunking_enabled": True,
                        "fallback_strategies_available": True,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                logger.info(f"🎉 [{request_id}] Enhanced audio pipeline finished in {total_processing_time:.2f}s "
                        f"(Success rate: {processing_success_rate:.1f}%)")
                return result
                
            except Exception as e:
                logger.error(f"❌ [{request_id}] Audio pipeline failed: {e}")
                raise RuntimeError(f"Audio pipeline processing failed: {str(e)}") 
        
    def _generate_insights(self, transcript: str, translation: Optional[str], 
                          entities: Dict, classification: Dict, summary: str, qa_scores: Dict, processing_steps: Dict = None) -> Dict[str, Any]:
        """Generate case insights from all processed data"""
        
        # Extract key information
        persons = entities.get("PERSON", [])
        locations = entities.get("LOC", []) + entities.get("GPE", [])
        organizations = entities.get("ORG", [])
        dates = entities.get("DATE", [])
        
        # Determine primary language
        primary_text = translation if translation else transcript
        
        # Calculate risk indicators
        risk_keywords = ["suicide", "abuse", "violence", "threat", "danger", "crisis", "emergency"]
        risk_score = sum(1 for keyword in risk_keywords if keyword.lower() in primary_text.lower())
        
        # Generate insights
        insights = {
            "case_overview": {
                "primary_language": "multilingual" if translation else "original",
                "key_entities": {
                    "people_mentioned": len(persons),
                    "locations_mentioned": len(locations),
                    "organizations_mentioned": len(organizations),
                    "dates_mentioned": len(dates)
                },
                "case_complexity": "high" if len(persons) > 2 or len(locations) > 1 else "medium" if len(persons) > 0 else "low"
            },
            "risk_assessment": {
                "risk_indicators_found": risk_score,
                "risk_level": "high" if risk_score >= 2 else "medium" if risk_score >= 1 else "low",
                "priority": classification.get("priority", "medium"),
                "confidence": classification.get("confidence", 0)
            },
            "key_information": {
                "main_category": classification.get("main_category", "unknown"),
                "sub_category": classification.get("sub_category", "unknown"),
                "intervention_needed": classification.get("intervention", "assessment_required"),
                "summary": summary[:200] + "..." if len(summary) > 200 else summary
            },
            "entities_detail": {
                "persons": persons[:5],  # Limit to first 5
                "locations": locations[:3],
                "organizations": organizations[:3],
                "key_dates": dates[:3]
            },
            "qa_analysis": {
                "qa_scores": qa_scores,
                "processing_info": processing_steps.get("qa_scoring", {}) if processing_steps else {}
            }
        }
        
        return insights

# Global instance
audio_pipeline = AudioPipelineService()