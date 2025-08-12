# app/streaming/progressive_processor.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import asyncio
import json

logger = logging.getLogger(__name__)

# Import notification service
try:
    from ..services.agent_notification_service import agent_notification_service
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    logger.warning("Agent notification service not available")

@dataclass
class ProcessingWindow:
    """Represents a translation/processing window"""
    window_id: int
    start_position: int  # Character position in cumulative transcript
    end_position: int
    text_content: str
    timestamp: datetime
    translation: Optional[str] = None
    entities: Optional[Dict] = None
    classification: Optional[Dict] = None
    processing_duration: float = 0.0
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass 
class ProgressiveAnalysis:
    """Tracks progressive analysis for a call"""
    call_id: str
    windows: List[ProcessingWindow]
    cumulative_translation: str
    latest_entities: Dict
    latest_classification: Dict
    entity_evolution: List[Dict]  # Track how entities change over time
    classification_evolution: List[Dict]  # Track how classification changes
    processing_stats: Dict
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['windows'] = [w.to_dict() for w in self.windows]
        return data

class ProgressiveProcessor:
    """Handles progressive translation, NER, and classification during calls"""
    
    def __init__(self):
        # Configuration
        self.min_window_chars = 150  # Minimum chars to trigger processing
        self.target_window_chars = 300  # Target window size
        self.overlap_chars = 50  # Overlap between windows for context
        self.processing_interval = timedelta(seconds=30)  # Min time between processing
        
        # Track processing state per call
        self.call_analyses: Dict[str, ProgressiveAnalysis] = {}
        
    async def should_process_window(self, call_id: str, transcript: str) -> bool:
        """Determine if we should create a new processing window"""
        
        if call_id not in self.call_analyses:
            # First window - process if we have minimum content
            return len(transcript.strip()) >= self.min_window_chars
        
        analysis = self.call_analyses[call_id] 
        
        # Check if enough new content since last window
        if not analysis.windows:
            return len(transcript.strip()) >= self.min_window_chars
            
        last_window = analysis.windows[-1]
        new_content_length = len(transcript) - last_window.end_position
        
        # Check content threshold
        if new_content_length < self.min_window_chars:
            return False
            
        # Check time threshold
        time_since_last = datetime.now() - last_window.timestamp
        if time_since_last < self.processing_interval:
            return False
            
        return True
    
    def create_processing_window(self, call_id: str, transcript: str) -> ProcessingWindow:
        """Create a new processing window with context"""
        
        if call_id not in self.call_analyses:
            self.call_analyses[call_id] = ProgressiveAnalysis(
                call_id=call_id,
                windows=[],
                cumulative_translation="",
                latest_entities={},
                latest_classification={},
                entity_evolution=[],
                classification_evolution=[],
                processing_stats={}
            )
        
        analysis = self.call_analyses[call_id]
        window_id = len(analysis.windows) + 1
        
        if not analysis.windows:
            # First window - use from beginning
            start_pos = 0
            end_pos = min(len(transcript), self.target_window_chars)
        else:
            # Subsequent windows - use overlap for context
            last_window = analysis.windows[-1]
            start_pos = max(0, last_window.end_position - self.overlap_chars)
            end_pos = len(transcript)
            
            # Don't make window too large
            if end_pos - start_pos > self.target_window_chars * 2:
                end_pos = start_pos + self.target_window_chars
        
        window_text = transcript[start_pos:end_pos].strip()
        
        window = ProcessingWindow(
            window_id=window_id,
            start_position=start_pos,
            end_position=end_pos,
            text_content=window_text,
            timestamp=datetime.now()
        )
        
        analysis.windows.append(window)
        logger.info(f"📊 Created processing window {window_id} for call {call_id}: "
                   f"{len(window_text)} chars ({start_pos}-{end_pos})")
        
        return window
    
    async def process_window(self, call_id: str, window: ProcessingWindow, client_ip: str = "192.168.10.1") -> ProcessingWindow:
        """Process a window through translation, NER, and classification"""
        
        start_time = datetime.now()
        
        try:
            # Import models (in async context)
            from ..tasks.audio_tasks import get_worker_models
            
            # Get worker models in async context
            models = await self._get_models_async()
            if not models:
                raise RuntimeError("Models not available for progressive processing")
            
            # Step 1: Translation
            translator_model = models.models.get("translator")
            if translator_model and window.text_content:
                logger.info(f"🌐 Translating window {window.window_id} for call {call_id}")
                window.translation = translator_model.translate(window.text_content)
            
            # Step 2: NER on translated text (or original if no translation)
            ner_text = window.translation if window.translation else window.text_content
            ner_model = models.models.get("ner")
            if ner_model and ner_text:
                logger.info(f"🏷️ Extracting entities from window {window.window_id} for call {call_id}")
                window.entities = ner_model.extract_entities(ner_text, flat=False)
            
            # Step 3: Classification on translated text
            classifier_model = models.models.get("classifier_model") 
            if classifier_model and ner_text:
                logger.info(f"📊 Classifying window {window.window_id} for call {call_id}")
                window.classification = classifier_model.classify(ner_text)
            
            window.processing_duration = (datetime.now() - start_time).total_seconds()
            
            # Update cumulative analysis
            await self._update_cumulative_analysis(call_id, window)
            
            # Send real-time updates to agent
            await self._send_agent_notifications(call_id, window, client_ip)
            
            logger.info(f"✅ Processed window {window.window_id} for call {call_id} in {window.processing_duration:.2f}s")
            
            return window
            
        except Exception as e:
            logger.error(f"❌ Failed to process window {window.window_id} for call {call_id}: {e}")
            window.processing_duration = (datetime.now() - start_time).total_seconds()
            return window
    
    async def _get_models_async(self):
        """Get models in async context"""
        try:
            # Run sync function in thread pool
            import asyncio
            from ..tasks.audio_tasks import get_worker_models
            
            loop = asyncio.get_event_loop()
            models = await loop.run_in_executor(None, get_worker_models)
            return models
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return None
    
    async def _update_cumulative_analysis(self, call_id: str, window: ProcessingWindow):
        """Update cumulative analysis with new window results"""
        
        analysis = self.call_analyses[call_id]
        
        # Update cumulative translation with smart concatenation
        if window.translation:
            analysis.cumulative_translation = self._merge_translation(
                analysis.cumulative_translation, 
                window.translation,
                window.start_position > 0  # Has overlap if not first window
            )
        
        # Update latest entities and track evolution
        if window.entities:
            # Track entity evolution
            entity_snapshot = {
                'window_id': window.window_id,
                'timestamp': window.timestamp.isoformat(),
                'entities': window.entities,
                'entity_count': sum(len(entities) for entities in window.entities.values())
            }
            analysis.entity_evolution.append(entity_snapshot)
            analysis.latest_entities = window.entities
        
        # Update latest classification and track evolution
        if window.classification:
            # Track classification evolution  
            classification_snapshot = {
                'window_id': window.window_id,
                'timestamp': window.timestamp.isoformat(),
                'classification': window.classification,
                'main_category': window.classification.get('main_category', 'unknown'),
                'confidence': window.classification.get('confidence', 0)
            }
            analysis.classification_evolution.append(classification_snapshot)
            analysis.latest_classification = window.classification
        
        # Update processing stats
        analysis.processing_stats = {
            'total_windows': len(analysis.windows),
            'total_processing_time': sum(w.processing_duration for w in analysis.windows),
            'average_processing_time': sum(w.processing_duration for w in analysis.windows) / len(analysis.windows),
            'cumulative_translation_length': len(analysis.cumulative_translation),
            'latest_entity_types': list(analysis.latest_entities.keys()) if analysis.latest_entities else [],
            'classification_trend': [c['main_category'] for c in analysis.classification_evolution[-5:]]  # Last 5
        }
    
    def _merge_translation(self, existing: str, new_translation: str, has_overlap: bool) -> str:
        """Merge translations with overlap handling"""
        
        if not existing:
            return new_translation
        
        if not new_translation:
            return existing
        
        if not has_overlap:
            # No overlap, simple concatenation
            return existing + " " + new_translation
        
        # Try to find overlap and merge intelligently
        existing_words = existing.split()
        new_words = new_translation.split()
        
        # Look for overlap (last few words of existing match first few words of new)
        max_overlap = min(10, len(existing_words), len(new_words))
        best_overlap = 0
        
        for overlap_size in range(max_overlap, 0, -1):
            existing_end = existing_words[-overlap_size:]
            new_start = new_words[:overlap_size]
            
            # Check for exact match or high similarity
            if existing_end == new_start:
                best_overlap = overlap_size
                break
        
        if best_overlap > 0:
            # Remove overlapping words from new translation
            merged_new_words = new_words[best_overlap:]
            if merged_new_words:
                return existing + " " + " ".join(merged_new_words)
            else:
                return existing
        else:
            # No overlap found, concatenate with separator
            return existing + " " + new_translation
    
    async def process_if_ready(self, call_id: str, transcript: str, client_ip: str = "192.168.10.1") -> Optional[ProcessingWindow]:
        """Check if ready and process new window if needed"""
        
        try:
            if await self.should_process_window(call_id, transcript):
                window = self.create_processing_window(call_id, transcript)
                processed_window = await self.process_window(call_id, window, client_ip)
                
                # Store analysis in Redis for persistence
                await self._store_analysis_in_redis(call_id)
                
                return processed_window
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Progressive processing failed for call {call_id}: {e}")
            return None
    
    async def finalize_call_analysis(self, call_id: str) -> Optional[Dict]:
        """Finalize analysis when call ends - trigger summarization"""
        
        if call_id not in self.call_analyses:
            logger.warning(f"No analysis found for call {call_id}")
            return None
        
        analysis = self.call_analyses[call_id]
        
        try:
            # Trigger summarization if we have substantial content
            if len(analysis.cumulative_translation) > 100:
                summary = await self._generate_final_summary(call_id, analysis)
                analysis.processing_stats['final_summary'] = summary
            
            # Create final analysis report
            final_report = {
                'call_id': call_id,
                'total_windows_processed': len(analysis.windows),
                'final_translation_length': len(analysis.cumulative_translation),
                'final_entities': analysis.latest_entities,
                'final_classification': analysis.latest_classification,
                'entity_evolution_count': len(analysis.entity_evolution),
                'classification_changes': len(set(c['main_category'] for c in analysis.classification_evolution)),
                'processing_stats': analysis.processing_stats,
                'finalized_at': datetime.now().isoformat()
            }
            
            logger.info(f"📋 Finalized analysis for call {call_id}: "
                       f"{final_report['total_windows_processed']} windows, "
                       f"{final_report['final_translation_length']} chars translated")
            
            # Send call summary notification to agent if summary was generated
            if NOTIFICATIONS_ENABLED and summary:
                try:
                    await agent_notification_service.send_call_summary(call_id, summary, final_report)
                except Exception as e:
                    logger.error(f"❌ Failed to send call summary notification for {call_id}: {e}")
            
            # Store final report
            await self._store_final_report(call_id, final_report)
            
            # Cleanup memory
            del self.call_analyses[call_id]
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Failed to finalize analysis for call {call_id}: {e}")
            return None
    
    async def _generate_final_summary(self, call_id: str, analysis: ProgressiveAnalysis) -> Optional[str]:
        """Generate final summary of the call"""
        
        try:
            models = await self._get_models_async()
            if not models:
                return None
            
            summarizer_model = models.models.get("summarizer")
            if not summarizer_model:
                logger.warning(f"Summarizer model not available for call {call_id}")
                return None
            
            # Use full cumulative translation for best summary
            text_to_summarize = analysis.cumulative_translation or ""
            
            if len(text_to_summarize.strip()) < 50:
                logger.warning(f"Text too short for summarization: {len(text_to_summarize)} chars")
                return None
            
            logger.info(f"📝 Generating final summary for call {call_id} ({len(text_to_summarize)} chars)")
            summary = summarizer_model.summarize(text_to_summarize)
            
            logger.info(f"✅ Generated summary for call {call_id}: {len(summary)} chars")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate summary for call {call_id}: {e}")
            return None
    
    async def _store_analysis_in_redis(self, call_id: str):
        """Store progressive analysis in Redis"""
        try:
            from ..config.settings import redis_task_client
            
            if not redis_task_client or call_id not in self.call_analyses:
                return
            
            analysis = self.call_analyses[call_id]
            analysis_data = analysis.to_dict()
            
            redis_key = f"progressive_analysis:{call_id}"
            redis_task_client.set(redis_key, json.dumps(analysis_data), ex=3600*24)  # 24h expiry
            
        except Exception as e:
            logger.error(f"Failed to store analysis in Redis for {call_id}: {e}")
    
    async def _store_final_report(self, call_id: str, report: Dict):
        """Store final analysis report"""
        try:
            from ..config.settings import redis_task_client
            
            if redis_task_client:
                redis_key = f"final_analysis:{call_id}"
                redis_task_client.set(redis_key, json.dumps(report), ex=3600*24*7)  # 7 days expiry
                
        except Exception as e:
            logger.error(f"Failed to store final report for {call_id}: {e}")
    
    async def _send_agent_notifications(self, call_id: str, window: ProcessingWindow, client_ip: str = "192.168.10.1"):
        """Send real-time updates to agent endpoint"""
        
        if not NOTIFICATIONS_ENABLED:
            return
        
        try:
            analysis = self.call_analyses[call_id]
            
            # Send translation update if available
            if window.translation:
                await agent_notification_service.send_translation_update(
                    call_id=call_id,
                    window_id=window.window_id,
                    translation=window.translation,
                    cumulative_translation=analysis.cumulative_translation,
                    client_ip=client_ip
                )
            
            # Send entity update if available
            if window.entities:
                await agent_notification_service.send_entity_update(
                    call_id=call_id,
                    window_id=window.window_id,
                    entities=window.entities,
                    entity_evolution=analysis.entity_evolution,
                    client_ip=client_ip
                )
            
            # Send classification update if available
            if window.classification:
                await agent_notification_service.send_classification_update(
                    call_id=call_id,
                    window_id=window.window_id,
                    classification=window.classification,
                    classification_evolution=analysis.classification_evolution,
                    client_ip=client_ip
                )
            
            logger.info(f"📤 Sent agent notifications for window {window.window_id}, call {call_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send agent notifications for call {call_id}: {e}")
    
    def get_call_analysis(self, call_id: str) -> Optional[ProgressiveAnalysis]:
        """Get current analysis for a call"""
        return self.call_analyses.get(call_id)

# Global instance
progressive_processor = ProgressiveProcessor()