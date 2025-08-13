# app/streaming/call_session_manager.py
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
import asyncio
import aiohttp
import os

from ..config.settings import redis_task_client
from .progressive_processor import progressive_processor

logger = logging.getLogger(__name__)

# Import agent notification service
try:
    from ..services.agent_notification_service import agent_notification_service
    AGENT_NOTIFICATIONS_ENABLED = True
except ImportError:
    AGENT_NOTIFICATIONS_ENABLED = False
    logger.warning("Agent notification service not available")

@dataclass
class CallSession:
    """Represents an active call session"""
    call_id: str
    start_time: datetime
    last_activity: datetime
    connection_info: Dict
    transcript_segments: List[Dict]
    cumulative_transcript: str
    total_audio_duration: float
    segment_count: int
    status: str  # 'active', 'completed', 'timeout'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CallSession':
        """Create from dictionary"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)

class CallSessionManager:
    """Manages multiple simultaneous call sessions with cumulative transcription"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis_task_client
        self.active_sessions: Dict[str, CallSession] = {}
        self.session_timeout = timedelta(minutes=30)  # Timeout inactive sessions
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self._cleanup_task = None
        
    async def start_session(self, call_id: str, connection_info: Dict) -> CallSession:
        """Start a new call session"""
        try:
            now = datetime.now()
            
            session = CallSession(
                call_id=call_id,
                start_time=now,
                last_activity=now,
                connection_info=connection_info,
                transcript_segments=[],
                cumulative_transcript="",
                total_audio_duration=0.0,
                segment_count=0,
                status='active'
            )
            
            # Store in memory
            self.active_sessions[call_id] = session
            
            # Store in Redis for persistence
            self._store_session_in_redis(session)
            
            logger.info(f"📞 [session] Started call session: {call_id}")
            logger.info(f"📞 [session] Active sessions: {len(self.active_sessions)}")
            
            # Send call start notification to agent
            if AGENT_NOTIFICATIONS_ENABLED:
                try:
                    await agent_notification_service.send_call_start(call_id, connection_info)
                except Exception as e:
                    logger.error(f"❌ Failed to send call start notification for {call_id}: {e}")
            
            # Start cleanup task if not running
            if self._cleanup_task is None:
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to start session {call_id}: {e}")
            raise
    
    async def add_transcription(self, call_id: str, transcript: str, 
                              audio_duration: float, metadata: Dict = None) -> Optional[CallSession]:
        """Add transcription segment to call session"""
        try:
            session = await self.get_session(call_id)
            if not session:
                logger.warning(f"⚠️ [session] No active session found for call {call_id}")
                return None
            
            now = datetime.now()
            
            # Create transcript segment
            segment = {
                'segment_id': session.segment_count + 1,
                'timestamp': now.isoformat(),
                'transcript': transcript.strip(),
                'audio_duration': audio_duration,
                'metadata': metadata or {}
            }
            
            # Update session
            session.transcript_segments.append(segment)
            session.segment_count += 1
            session.total_audio_duration += audio_duration
            session.last_activity = now
            
            # Update cumulative transcript with smart concatenation
            session.cumulative_transcript = self._concatenate_transcript(
                session.cumulative_transcript, 
                transcript.strip()
            )
            
            # Trigger progressive processing (translation, NER, classification)
            try:
                processed_window = await progressive_processor.process_if_ready(
                    call_id, 
                    session.cumulative_transcript
                )
                
                if processed_window:
                    logger.info(f"🧠 [session] Progressive processing completed window {processed_window.window_id} for call {call_id}")
                    
                    # Add processing info to segment metadata
                    segment['metadata']['progressive_window'] = processed_window.window_id
                    segment['metadata']['window_processed'] = True
                
            except Exception as e:
                logger.error(f"❌ Progressive processing failed for call {call_id}: {e}")
            
            # Store updated session
            self._store_session_in_redis(session)
            
            # Send transcript segment notification to agent
            if AGENT_NOTIFICATIONS_ENABLED:
                try:
                    await agent_notification_service.send_transcript_segment(
                        call_id, 
                        segment, 
                        session.cumulative_transcript
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to send transcript segment notification for {call_id}: {e}")
            
            logger.info(f"📝 [session] Added segment {segment['segment_id']} to call {call_id}")
            logger.info(f"📝 [session] Transcript length: {len(session.cumulative_transcript)} chars")
            logger.info(f"📝 [session] Total duration: {session.total_audio_duration:.1f}s")
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to add transcription to session {call_id}: {e}")
            return None
    
    def _concatenate_transcript(self, existing: str, new_text: str) -> str:
        """Smart concatenation of transcript segments"""
        if not existing:
            return new_text
        
        if not new_text:
            return existing
        
        # Remove redundant repetitions at boundaries
        existing_words = existing.lower().split()
        new_words = new_text.lower().split()
        
        # Check for overlap (last few words of existing match first few words of new)
        max_overlap = min(5, len(existing_words), len(new_words))
        overlap_found = 0
        
        for i in range(1, max_overlap + 1):
            if existing_words[-i:] == new_words[:i]:
                overlap_found = i
        
        if overlap_found > 0:
            # Remove overlapping words from new text
            final_new_words = new_text.split()[overlap_found:]
            if final_new_words:
                return existing + " " + " ".join(final_new_words)
            else:
                return existing
        else:
            # No overlap, simple concatenation
            return existing + " " + new_text
    
    async def get_session(self, call_id: str) -> Optional[CallSession]:
        """Get active session by call ID"""
        # Try Redis first for cross-process compatibility
        try:
            session_data = self._get_session_from_redis(call_id)
            if session_data:
                session = CallSession.from_dict(session_data)
                # Update in-memory cache
                self.active_sessions[call_id] = session
                return session
        except Exception as e:
            logger.error(f"❌ Failed to retrieve session {call_id} from Redis: {e}")
        
        # Fallback to memory (for same-process access)
        if call_id in self.active_sessions:
            return self.active_sessions[call_id]
        
        return None
    
    async def end_session(self, call_id: str, reason: str = "completed") -> Optional[CallSession]:
        """End call session and prepare for AI pipeline processing"""
        try:
            session = await self.get_session(call_id)
            if not session:
                logger.warning(f"⚠️ [session] No session found to end: {call_id}")
                return None
            
            # Update session status
            session.status = reason
            session.last_activity = datetime.now()
            
            # Store final session state
            self._store_session_in_redis(session)
            
            # Finalize progressive processing and trigger summarization
            try:
                final_analysis = await progressive_processor.finalize_call_analysis(call_id)
                if final_analysis:
                    logger.info(f"📋 [session] Progressive analysis finalized for call {call_id}")
                    logger.info(f"📊 [session] Analysis summary: {final_analysis['total_windows_processed']} windows, "
                               f"{final_analysis['final_translation_length']} chars translated")
            except Exception as e:
                logger.error(f"❌ Failed to finalize progressive analysis for call {call_id}: {e}")
            
            # Download and process complete audio file from Asterisk server
            audio_download_task = None
            try:
                audio_download_task = await self._download_and_process_audio(session)
            except Exception as e:
                logger.error(f"❌ Failed to download/process audio for {call_id}: {e}")

            # Trigger AI pipeline processing if transcript is substantial (fallback)
            ai_task = None
            if len(session.cumulative_transcript.strip()) > 50:  # Minimum threshold
                ai_task = await self._trigger_ai_pipeline(session)
            
            # Wait for AI pipeline completion and send summary/insights
            if ai_task and AGENT_NOTIFICATIONS_ENABLED:
                try:
                    await self._wait_and_send_ai_results(call_id, ai_task)
                except Exception as e:
                    logger.error(f"❌ Failed to send AI results for {call_id}: {e}")
            
            # Send call end notification to agent
            if AGENT_NOTIFICATIONS_ENABLED:
                try:
                    final_stats = {
                        'duration': session.total_audio_duration,
                        'segments': session.segment_count,
                        'transcript_length': len(session.cumulative_transcript),
                        'start_time': session.start_time.isoformat(),
                        'end_time': session.last_activity.isoformat()
                    }
                    await agent_notification_service.send_call_end(call_id, reason, final_stats)
                except Exception as e:
                    logger.error(f"❌ Failed to send call end notification for {call_id}: {e}")
            
            # Remove from active sessions
            if call_id in self.active_sessions:
                del self.active_sessions[call_id]
            
            logger.info(f"📞 [session] Ended call session: {call_id} (reason: {reason})")
            logger.info(f"📊 [session] Final stats - Duration: {session.total_audio_duration:.1f}s, "
                       f"Segments: {session.segment_count}, "
                       f"Transcript: {len(session.cumulative_transcript)} chars")
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to end session {call_id}: {e}")
            return None
    
    async def _trigger_ai_pipeline(self, session: CallSession):
        """Trigger full AI pipeline processing for completed call"""
        try:
            from ..tasks.audio_tasks import process_audio_task
            
            # Create synthetic audio filename for the complete call
            filename = f"call_{session.call_id}_{session.start_time.strftime('%Y%m%d_%H%M%S')}.transcript"
            
            # Since we already have the transcript, pass it directly as text
            # Use a special marker to indicate this is pre-transcribed text
            transcript_data = {
                'transcript': session.cumulative_transcript,
                'is_pretranscribed': True,
                'language': 'sw'
            }
            transcript_bytes = json.dumps(transcript_data).encode('utf-8')
            
            # Submit to full AI pipeline with pre-transcribed flag
            task = process_audio_task.delay(
                audio_bytes=transcript_bytes,
                filename=filename,
                language="sw",  # Could be stored in session metadata
                include_translation=True,
                include_insights=True
            )
            
            # Store task reference in session metadata
            session_key = f"call_session:{session.call_id}"
            pipeline_info = {
                'task_id': task.id,
                'submitted_at': datetime.now().isoformat(),
                'status': 'processing'
            }
            
            if self.redis_client:
                self.redis_client.hset(
                    session_key, 
                    'ai_pipeline', 
                    json.dumps(pipeline_info)
                )
            
            logger.info(f"🤖 [session] Triggered AI pipeline for call {session.call_id}, task: {task.id}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger AI pipeline for session {session.call_id}: {e}")
            return None
    
    async def _wait_and_send_ai_results(self, call_id: str, ai_task):
        """Wait for AI pipeline completion and send summary/insights to agent"""
        try:
            import asyncio
            from celery.result import AsyncResult
            
            logger.info(f"📊 [session] Waiting for AI pipeline completion for call {call_id}, task: {ai_task.id}")
            
            # Wait for task completion with timeout
            timeout_seconds = 300  # 5 minutes timeout
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout_seconds:
                # Check task status
                result = AsyncResult(ai_task.id)
                
                if result.ready():
                    if result.successful():
                        # Task completed successfully
                        ai_result = result.result
                        logger.info(f"✅ [session] AI pipeline completed for call {call_id}")
                        
                        # Extract results from the task output
                        if isinstance(ai_result, dict) and 'result' in ai_result:
                            pipeline_result = ai_result['result']
                            summary = pipeline_result.get('summary', '')
                            insights = pipeline_result.get('insights', {})
                            
                            # Send call summary notification (with QA summary only)
                            if summary and len(summary.strip()) > 10:
                                try:
                                    # Extract QA scores for summary reference
                                    qa_scores = pipeline_result.get('qa_scores', {})
                                    overall_qa_score = self._extract_overall_qa_score(qa_scores)
                                    
                                    # Create final analysis data with QA summary reference
                                    final_analysis = {
                                        'transcript_length': len(pipeline_result.get('transcript', '')),
                                        'translation_available': bool(pipeline_result.get('translation')),
                                        'translation_input_for_qa': bool(pipeline_result.get('translation')),  # Clarify QA input
                                        'entities_found': len(pipeline_result.get('entities', {})),
                                        'classification': pipeline_result.get('classification', {}),
                                        'processing_time': pipeline_result.get('pipeline_info', {}).get('total_time', 0),
                                        'qa_summary': {
                                            'overall_score': overall_qa_score,
                                            'performance_grade': self._get_performance_grade(overall_qa_score),
                                            'note': 'Detailed QA analysis available in insights notification'
                                        }
                                    }
                                    
                                    await agent_notification_service.send_call_summary(call_id, summary, final_analysis)
                                    logger.info(f"📋 [session] Sent call summary with QA summary for {call_id}")
                                except Exception as e:
                                    logger.error(f"❌ Failed to send call summary for {call_id}: {e}")
                            
                            # Send insights notification with full QA analysis
                            if insights and isinstance(insights, dict):
                                try:
                                    # Add comprehensive QA analysis to insights
                                    qa_scores = pipeline_result.get('qa_scores', {})
                                    if qa_scores:
                                        insights['qa_analysis'] = {
                                            'input_source': 'translated_text' if pipeline_result.get('translation') else 'original_transcript',
                                            'overall_score': self._extract_overall_qa_score(qa_scores),
                                            'detailed_scores': qa_scores,
                                            'performance_summary': self._summarize_qa_performance(qa_scores),
                                            'coaching_recommendations': self._generate_coaching_recommendations(qa_scores)
                                        }
                                    
                                    await self._send_insights_notification(call_id, insights)
                                    logger.info(f"💡 [session] Sent insights with full QA analysis for {call_id}")
                                except Exception as e:
                                    logger.error(f"❌ Failed to send insights for {call_id}: {e}")
                                    
                            # Generate and send Mistral GPT insights
                            try:
                                from ..services.insights_service import generate_case_insights
                                
                                transcript = pipeline_result.get('transcript', '')
                                if transcript and len(transcript.strip()) > 50:
                                    logger.info(f"🧠 [session] Generating Mistral GPT insights for call {call_id}")
                                    gpt_insights = generate_case_insights(transcript)
                                    
                                    # Send GPT insights notification
                                    await agent_notification_service.send_gpt_insights(call_id, gpt_insights)
                                    logger.info(f"🤖 [session] Sent Mistral GPT insights for {call_id}")
                                else:
                                    logger.warning(f"⚠️ [session] Transcript too short for GPT insights generation: {len(transcript)} chars")
                                    
                            except Exception as e:
                                logger.error(f"❌ Failed to generate/send GPT insights for {call_id}: {e}")
                            
                        break
                    else:
                        # Task failed
                        logger.error(f"❌ [session] AI pipeline failed for call {call_id}: {result.info}")
                        break
                
                # Wait before checking again
                await asyncio.sleep(2)
            else:
                # Timeout occurred
                logger.warning(f"⏰ [session] AI pipeline timeout for call {call_id} after {timeout_seconds}s")
                
        except Exception as e:
            logger.error(f"❌ Failed to wait for AI results for {call_id}: {e}")
    
    async def _send_insights_notification(self, call_id: str, insights: dict):
        """Send insights as a structured notification to agent system"""
        try:
            # Create insights payload similar to other notifications
            payload = {
                "update_type": "call_insights",
                "call_id": call_id,
                "timestamp": datetime.now().isoformat(),
                "insights": insights,
                "insight_summary": {
                    "case_complexity": insights.get("case_overview", {}).get("case_complexity", "unknown"),
                    "risk_level": insights.get("risk_assessment", {}).get("risk_level", "unknown"),
                    "key_entities": insights.get("case_overview", {}).get("key_entities", {}),
                    "recommendations": insights.get("recommendations", {})
                },
                "processing_complete": True
            }
            
            # Use existing notification infrastructure
            from ..services.agent_notification_service import UpdateType
            return await agent_notification_service._send_notification(call_id, UpdateType.CALL_INSIGHTS, payload)
            
        except Exception as e:
            logger.error(f"❌ Failed to send insights notification for {call_id}: {e}")
            return False
    
    def _extract_overall_qa_score(self, qa_scores: dict) -> float:
        """Extract overall QA score from detailed results"""
        try:
            if not qa_scores or not isinstance(qa_scores, dict):
                return 0.0
            
            # Check if there's an overall_qa_score field (from score_transcript method)
            if 'overall_qa_score' in qa_scores:
                return float(qa_scores['overall_qa_score'])
            
            # Calculate from detailed scores if available
            if 'detailed_scores' in qa_scores:
                detailed = qa_scores['detailed_scores']
                scores = []
                for category, data in detailed.items():
                    if isinstance(data, dict) and 'score_percent' in data:
                        scores.append(data['score_percent'])
                
                return sum(scores) / len(scores) if scores else 0.0
            
            # Fallback: calculate from head results (from predict method)
            total_probs = []
            for head_name, submetrics in qa_scores.items():
                if isinstance(submetrics, list):
                    for submetric in submetrics:
                        if isinstance(submetric, dict) and 'probability' in submetric:
                            total_probs.append(submetric['probability'])
            
            return (sum(total_probs) / len(total_probs) * 100) if total_probs else 0.0
            
        except Exception as e:
            logger.error(f"Failed to extract overall QA score: {e}")
            return 0.0
    
    def _summarize_qa_performance(self, qa_scores: dict) -> dict:
        """Create a summary of QA performance by category"""
        try:
            summary = {
                'strengths': [],
                'areas_for_improvement': [],
                'category_scores': {},
                'metrics_passed': 0,
                'total_metrics': 0
            }
            
            if not qa_scores or not isinstance(qa_scores, dict):
                return summary
            
            # Handle detailed_scores format (from score_transcript method)
            if 'detailed_scores' in qa_scores:
                detailed = qa_scores['detailed_scores']
                for category, data in detailed.items():
                    if isinstance(data, dict):
                        score = data.get('score_percent', 0)
                        summary['category_scores'][category] = score
                        
                        if score >= 80:
                            summary['strengths'].append(category)
                        elif score < 60:
                            summary['areas_for_improvement'].append(category)
                        
                        # Count metrics
                        submetrics = data.get('submetrics', [])
                        for submetric in submetrics:
                            summary['total_metrics'] += 1
                            if submetric.get('passed', False):
                                summary['metrics_passed'] += 1
            
            # Handle head results format (from predict method)
            else:
                for head_name, submetrics in qa_scores.items():
                    if isinstance(submetrics, list):
                        passed_count = 0
                        total_count = len(submetrics)
                        
                        for submetric in submetrics:
                            if isinstance(submetric, dict):
                                summary['total_metrics'] += 1
                                if submetric.get('prediction', False):
                                    passed_count += 1
                                    summary['metrics_passed'] += 1
                        
                        # Calculate category score
                        category_score = (passed_count / total_count * 100) if total_count > 0 else 0
                        summary['category_scores'][head_name] = category_score
                        
                        if category_score >= 80:
                            summary['strengths'].append(head_name)
                        elif category_score < 60:
                            summary['areas_for_improvement'].append(head_name)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize QA performance: {e}")
            return {
                'strengths': [],
                'areas_for_improvement': [],
                'category_scores': {},
                'metrics_passed': 0,
                'total_metrics': 0
            }
    
    def _get_performance_grade(self, overall_score: float) -> str:
        """Convert overall QA score to performance grade"""
        if overall_score >= 90:
            return 'A+'
        elif overall_score >= 85:
            return 'A'
        elif overall_score >= 80:
            return 'B+'
        elif overall_score >= 75:
            return 'B'
        elif overall_score >= 70:
            return 'C+'
        elif overall_score >= 65:
            return 'C'
        elif overall_score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_coaching_recommendations(self, qa_scores: dict) -> list:
        """Generate actionable coaching recommendations based on QA scores"""
        recommendations = []
        
        try:
            performance_summary = self._summarize_qa_performance(qa_scores)
            category_scores = performance_summary.get('category_scores', {})
            areas_for_improvement = performance_summary.get('areas_for_improvement', [])
            
            # Generate specific recommendations based on weak areas
            for category in areas_for_improvement:
                score = category_scores.get(category, 0)
                
                if category == 'opening':
                    recommendations.append({
                        'area': 'Call Opening',
                        'current_score': score,
                        'recommendation': 'Use proper greeting and introduction at start of call',
                        'priority': 'high'
                    })
                
                elif category == 'listening':
                    recommendations.append({
                        'area': 'Active Listening',
                        'current_score': score,
                        'recommendation': 'Focus on not interrupting, showing empathy, and paraphrasing caller concerns',
                        'priority': 'high'
                    })
                
                elif category == 'proactiveness':
                    recommendations.append({
                        'area': 'Proactive Service',
                        'current_score': score,
                        'recommendation': 'Take initiative to solve additional issues and confirm caller satisfaction',
                        'priority': 'medium'
                    })
                
                elif category == 'resolution':
                    recommendations.append({
                        'area': 'Problem Resolution',
                        'current_score': score,
                        'recommendation': 'Ensure accurate information, proper steps, and clear explanations',
                        'priority': 'high'
                    })
                
                elif category == 'hold':
                    recommendations.append({
                        'area': 'Hold Etiquette',
                        'current_score': score,
                        'recommendation': 'Always explain before placing on hold and thank caller for waiting',
                        'priority': 'medium'
                    })
                
                elif category == 'closing':
                    recommendations.append({
                        'area': 'Call Closing',
                        'current_score': score,
                        'recommendation': 'Use proper closing phrases and ensure caller satisfaction before ending',
                        'priority': 'high'
                    })
            
            # Add positive reinforcement for strong areas
            strengths = performance_summary.get('strengths', [])
            if strengths:
                recommendations.append({
                    'area': 'Strengths to Maintain',
                    'current_score': max([category_scores.get(s, 0) for s in strengths] or [0]),
                    'recommendation': f'Continue excellent performance in: {", ".join(strengths)}',
                    'priority': 'maintain'
                })
            
        except Exception as e:
            logger.error(f"Failed to generate coaching recommendations: {e}")
            recommendations.append({
                'area': 'General',
                'current_score': 0,
                'recommendation': 'Review call recording for improvement opportunities',
                'priority': 'medium'
            })
        
        return recommendations
    
    async def get_all_active_sessions(self) -> List[CallSession]:
        """Get all active sessions"""
        return list(self.active_sessions.values())
    
    async def get_session_stats(self) -> Dict:
        """Get statistics about all sessions"""
        active_count = len(self.active_sessions)
        total_duration = sum(s.total_audio_duration for s in self.active_sessions.values())
        total_segments = sum(s.segment_count for s in self.active_sessions.values())
        
        return {
            'active_sessions': active_count,
            'total_audio_duration': total_duration,
            'total_segments': total_segments,
            'average_duration_per_session': total_duration / active_count if active_count > 0 else 0,
            'session_list': [s.call_id for s in self.active_sessions.values()]
        }
    
    def _store_session_in_redis(self, session: CallSession):
        """Store session in Redis for persistence"""
        # Ensure we have a Redis client
        if not self.redis_client:
            from ..config.settings import redis_task_client
            self.redis_client = redis_task_client
            
        if not self.redis_client:
            logger.warning(f"🔍 [session] Redis client not available for storing session {session.call_id}")
            return
        
        try:
            session_key = f"call_session:{session.call_id}"
            session_data = session.to_dict()
            
            # Store main session data
            self.redis_client.hset(session_key, 'data', json.dumps(session_data))
            
            # Set expiration (keep for 24 hours after last activity)
            expire_time = int((session.last_activity + timedelta(hours=24)).timestamp())
            self.redis_client.expireat(session_key, expire_time)
            
            # Add to active sessions set
            if session.status == 'active':
                self.redis_client.sadd('active_call_sessions', session.call_id)
            else:
                self.redis_client.srem('active_call_sessions', session.call_id)
                
            logger.debug(f"🔍 [session] Successfully stored session {session.call_id} in Redis")
                
        except Exception as e:
            logger.error(f"❌ Failed to store session {session.call_id} in Redis: {e}")
    
    def _get_session_from_redis(self, call_id: str) -> Optional[Dict]:
        """Retrieve session from Redis"""
        # Ensure we have a Redis client
        if not self.redis_client:
            from ..config.settings import redis_task_client
            self.redis_client = redis_task_client
            
        if not self.redis_client:
            logger.warning(f"🔍 [session] Redis client not available for session {call_id}")
            return None
        
        try:
            session_key = f"call_session:{call_id}"
            session_json = self.redis_client.hget(session_key, 'data')
            
            if session_json:
                logger.debug(f"🔍 [session] Found session {call_id} in Redis")
                return json.loads(session_json)
            else:
                logger.debug(f"🔍 [session] No Redis data found for session {call_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to retrieve session {call_id} from Redis: {e}")
        
        return None
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of inactive sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_inactive_sessions()
            except asyncio.CancelledError:
                logger.info("📞 [session] Cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Session cleanup error: {e}")
    
    async def _cleanup_inactive_sessions(self):
        """Clean up sessions that have been inactive too long"""
        now = datetime.now()
        timeout_threshold = now - self.session_timeout
        
        inactive_sessions = []
        
        for call_id, session in list(self.active_sessions.items()):
            if session.last_activity < timeout_threshold:
                inactive_sessions.append(call_id)
        
        for call_id in inactive_sessions:
            logger.info(f"🧹 [session] Cleaning up inactive session: {call_id}")
            await self.end_session(call_id, reason="timeout")
        
        if inactive_sessions:
            logger.info(f"🧹 [session] Cleaned up {len(inactive_sessions)} inactive sessions")
    
    async def _download_and_process_audio(self, session: CallSession):
        """Download complete audio file from Asterisk server via SCP and process through full pipeline"""
        try:
            call_id = session.call_id
            logger.info(f"📥 [download] Starting SCP audio download for call {call_id}")
            
            # Use SCP downloader with GSM to WAV conversion
            from utils.scp_audio_downloader import download_and_convert_audio
            
            audio_bytes, download_info = await download_and_convert_audio(
                call_id=call_id, 
                convert_to_wav=True  # Convert GSM to WAV for better Whisper processing
            )
            
            if audio_bytes is not None:
                logger.info(f"✅ [download] Successfully downloaded {download_info['file_size_mb']:.2f}MB "
                           f"audio file for call {call_id} via SCP")
                logger.info(f"📊 [download] Format: {download_info['format']}, "
                           f"Original: {download_info.get('original_size_mb', 'N/A')}MB")
                
                # Store download metadata in session for debugging
                session.audio_download_info = download_info
                
                # Submit to full audio processing pipeline
                return await self._process_downloaded_audio(session, audio_bytes, download_info)
                
            else:
                logger.error(f"❌ [download] SCP download failed for call {call_id}: {download_info.get('error', 'unknown')}")
                return None
                        
        except Exception as e:
            logger.error(f"❌ [download] Unexpected error downloading audio for call {session.call_id}: {e}")
            return None
    
    async def _process_downloaded_audio(self, session: CallSession, audio_bytes: bytes, download_info: Dict[str, Any]):
        """Process downloaded audio through the full /audio/process pipeline"""
        try:
            from ..tasks.audio_tasks import process_audio_task
            
            # Create filename from call information
            filename = f"call_{session.call_id}_{session.start_time.strftime('%Y%m%d_%H%M%S')}.wav"
            
            logger.info(f"🎵 [pipeline] Processing downloaded audio for call {session.call_id} ({len(audio_bytes)} bytes)")
            
            # Submit to full audio processing pipeline (same as /audio/process endpoint)
            task = process_audio_task.delay(
                audio_bytes=audio_bytes,
                filename=filename,
                language="sw",  # Could be configurable
                include_translation=True,
                include_insights=True
            )
            
            # Store task reference in session metadata for tracking
            session_key = f"call_session:{session.call_id}"
            audio_pipeline_info = {
                'audio_task_id': task.id,
                'download_method': 'scp',
                'download_info': download_info,
                'audio_size_bytes': len(audio_bytes),
                'submitted_at': datetime.now().isoformat(),
                'status': 'processing',
                'processing_type': 'full_audio_analysis'
            }
            
            if self.redis_client:
                self.redis_client.hset(
                    session_key, 
                    'audio_pipeline', 
                    json.dumps(audio_pipeline_info)
                )
            
            logger.info(f"🤖 [pipeline] Submitted full audio processing for call {session.call_id}, task: {task.id}")
            logger.info(f"📊 [pipeline] Audio analysis will provide higher quality results than streaming transcripts")
            
            # Wait for processing completion and generate enhanced insights
            if AGENT_NOTIFICATIONS_ENABLED:
                asyncio.create_task(self._wait_and_generate_enhanced_insights(
                    session, task, audio_bytes, download_info
                ))
            
            return task
            
        except Exception as e:
            logger.error(f"❌ [pipeline] Failed to process downloaded audio for call {session.call_id}: {e}")
            return None
    
    async def _wait_and_generate_enhanced_insights(self, session: CallSession, audio_task, audio_bytes: bytes, download_info: Dict[str, Any]):
        """Wait for audio processing completion and generate enhanced Mistral insights"""
        try:
            from celery.result import AsyncResult
            from ..services.insights_service import generate_enhanced_audio_insights
            
            call_id = session.call_id
            logger.info(f"🔍 [enhanced] Waiting for audio processing completion for call {call_id}, task: {audio_task.id}")
            
            # Wait for audio task completion with timeout
            timeout_seconds = 600  # 10 minutes timeout for audio processing
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout_seconds:
                # Check task status
                result = AsyncResult(audio_task.id)
                
                if result.ready():
                    if result.successful():
                        # Audio processing completed successfully
                        audio_result = result.result
                        logger.info(f"✅ [enhanced] Audio processing completed for call {call_id}")
                        
                        # Extract results from the audio task output
                        if isinstance(audio_result, dict) and 'result' in audio_result:
                            pipeline_result = audio_result['result']
                            
                            # Get enhanced transcript and other data
                            enhanced_transcript = pipeline_result.get('transcript', '')
                            translation = pipeline_result.get('translation', '')
                            entities = pipeline_result.get('entities', {})
                            classification = pipeline_result.get('classification', {})
                            qa_scores = pipeline_result.get('qa_scores', {})
                            summary = pipeline_result.get('summary', '')
                            
                            # Audio quality information from SCP download
                            audio_quality_info = {
                                'file_size_mb': download_info.get('file_size_mb', round(len(audio_bytes) / (1024 * 1024), 2)),
                                'download_method': download_info.get('method', 'scp'),
                                'audio_format': download_info.get('format', 'unknown'),
                                'original_size_mb': download_info.get('original_size_mb'),
                                'conversion_successful': download_info.get('conversion_successful', False),
                                'server': download_info.get('server', 'unknown'),
                                'processing_time': pipeline_result.get('pipeline_info', {}).get('total_time', 0)
                            }
                            
                            # Generate enhanced insights using original streaming transcript vs enhanced
                            original_transcript = session.cumulative_transcript
                            
                            if enhanced_transcript and len(enhanced_transcript.strip()) > 50:
                                logger.info(f"🧠 [enhanced] Generating enhanced Mistral insights for call {call_id}")
                                logger.info(f"📊 [enhanced] Original: {len(original_transcript)} chars, Enhanced: {len(enhanced_transcript)} chars")
                                
                                try:
                                    # Generate enhanced insights using original vs enhanced comparison
                                    enhanced_insights = generate_enhanced_audio_insights(
                                        original_transcript=original_transcript,
                                        enhanced_transcript=enhanced_transcript,
                                        translation=translation,
                                        entities=entities,
                                        classification=classification,
                                        qa_scores=qa_scores,
                                        summary=summary,
                                        audio_quality_info=audio_quality_info
                                    )
                                    
                                    # Add enhanced insights to pipeline result
                                    pipeline_result['enhanced_insights'] = enhanced_insights
                                    
                                    # Send unified insight notification with complete results
                                    processing_metadata = {
                                        'original_transcript_length': len(original_transcript),
                                        'enhanced_transcript_length': len(enhanced_transcript),
                                        'quality_improvement': 'high_fidelity_audio_based',
                                        'processing_type': 'complete_audio_pipeline',
                                        'download_method': 'scp',
                                        'audio_format': audio_quality_info.get('audio_format', 'unknown')
                                    }
                                    
                                    await agent_notification_service.send_unified_insight(
                                        call_id=call_id,
                                        pipeline_result=pipeline_result,
                                        audio_quality_info=audio_quality_info,
                                        processing_metadata=processing_metadata
                                    )
                                    
                                    logger.info(f"🤖 [unified] Sent comprehensive unified insights for call {call_id}")
                                    logger.info(f"📊 [unified] Includes: transcript, translation, entities, classification, QA, summary, insights")
                                    
                                except Exception as insights_error:
                                    logger.error(f"❌ Failed to generate/send unified insights for {call_id}: {insights_error}")
                            else:
                                logger.warning(f"⚠️ [enhanced] Enhanced transcript too short for insights generation: {len(enhanced_transcript)} chars")
                                
                                # Still send unified insight with available data (no enhanced insights)
                                try:
                                    processing_metadata = {
                                        'original_transcript_length': len(original_transcript),
                                        'enhanced_transcript_length': len(enhanced_transcript),
                                        'quality_improvement': 'limited_due_to_short_transcript',
                                        'processing_type': 'basic_audio_pipeline',
                                        'download_method': 'scp',
                                        'audio_format': audio_quality_info.get('audio_format', 'unknown')
                                    }
                                    
                                    await agent_notification_service.send_unified_insight(
                                        call_id=call_id,
                                        pipeline_result=pipeline_result,
                                        audio_quality_info=audio_quality_info,
                                        processing_metadata=processing_metadata
                                    )
                                    
                                    logger.info(f"🤖 [unified] Sent basic unified insights for call {call_id} (short transcript)")
                                    
                                except Exception as basic_error:
                                    logger.error(f"❌ Failed to send basic unified insights for {call_id}: {basic_error}")
                        
                        break
                    else:
                        # Audio processing failed
                        logger.error(f"❌ [enhanced] Audio processing failed for call {call_id}: {result.info}")
                        break
                
                # Wait before checking again
                await asyncio.sleep(5)  # Check every 5 seconds
            else:
                # Timeout occurred
                logger.warning(f"⏰ [enhanced] Audio processing timeout for call {call_id} after {timeout_seconds}s")
                
        except Exception as e:
            logger.error(f"❌ Failed to wait for enhanced insights for {call_id}: {e}")
    
    async def _send_enhanced_insights_notification(self, call_id: str, enhanced_insights: dict, audio_quality_info: dict):
        """Send enhanced insights notification to agent system"""
        try:
            # Create enhanced insights payload
            payload = {
                "update_type": "enhanced_audio_insights",
                "call_id": call_id,
                "timestamp": datetime.now().isoformat(),
                "insights": enhanced_insights,
                "audio_quality": audio_quality_info,
                "insight_summary": {
                    "analysis_type": enhanced_insights.get("analysis_metadata", {}).get("analysis_type", "enhanced_audio_based"),
                    "confidence_level": enhanced_insights.get("analysis_metadata", {}).get("confidence_level", "high"),
                    "quality_improvement": enhanced_insights.get("analysis_metadata", {}).get("transcript_quality_improvement", "unknown"),
                    "complexity_level": enhanced_insights.get("advanced_classification", {}).get("complexity_level", "unknown"),
                    "intervention_urgency": enhanced_insights.get("advanced_classification", {}).get("intervention_urgency", "unknown"),
                    "risk_levels": {
                        "suicide_risk": enhanced_insights.get("comprehensive_risk_assessment", {}).get("suicide_risk_level", "unknown"),
                        "violence_risk": enhanced_insights.get("comprehensive_risk_assessment", {}).get("violence_risk_level", "unknown")
                    }
                },
                "processing_complete": True,
                "supersedes_streaming_insights": True
            }
            
            # Use existing notification infrastructure
            from ..services.agent_notification_service import UpdateType
            return await agent_notification_service._send_notification(call_id, UpdateType.CALL_INSIGHTS, payload)
            
        except Exception as e:
            logger.error(f"❌ Failed to send enhanced insights notification for {call_id}: {e}")
            return False

# Global session manager instance
call_session_manager = CallSessionManager()