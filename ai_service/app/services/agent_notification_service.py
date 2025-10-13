# app/services/agent_notification_service.py
import asyncio
import aiohttp
import json
import base64
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from enum import Enum

logger = logging.getLogger(__name__)

class UpdateType(Enum):
    CALL_START = "call_start"
    TRANSCRIPT_SEGMENT = "transcript_segment" 
    TRANSLATION_UPDATE = "translation_update"
    ENTITY_UPDATE = "entity_update"
    CLASSIFICATION_UPDATE = "classification_update"
    QA_UPDATE = "qa_update"
    CALL_END = "call_end"
    CALL_SUMMARY = "call_summary"
    CALL_INSIGHTS = "call_insights"
    GPT_INSIGHTS = "gpt_insights"
    ERROR = "error"

class AgentNotificationService:
    """Service to send real-time call updates to agent endpoint"""
    
    def __init__(self):
        # Import settings here to avoid circular imports
        from ..config.settings import settings
        
        # Configuration from settings
        self.asterisk_server_ip = settings.asterisk_server_ip
        self.endpoint_url = settings.notification_endpoint_url
        self.auth_endpoint_url = settings.notification_auth_endpoint_url
        self.basic_auth = settings.notification_basic_auth
        
        # Dynamic token management
        self.bearer_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.token_refresh_threshold = 300  # Refresh 5 minutes before expiry
        
        # HTTP session for connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting and retry settings from configuration
        self.max_retries = settings.notification_max_retries
        self.retry_delay = 1.0  # seconds
        self.request_timeout = float(settings.notification_request_timeout)
        
    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                ssl=False,  # Disable SSL verification for self-signed certs
                limit=10,   # Connection pool limit
                limit_per_host=5
            )
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _fetch_auth_token(self) -> Optional[str]:
        """Fetch authentication token from auth endpoint"""
        try:
            await self._ensure_session()
            
            headers = {
                "Authorization": f"Basic {self.basic_auth}"
            }
            
            logger.info("🔑 Fetching auth token from endpoint...")
            
            async with self.session.get(
                self.auth_endpoint_url,
                headers=headers,
                ssl=False  # Disable SSL verification
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse token from response structure: {"ss":[["token",...]],...}
                    if "ss" in data and isinstance(data["ss"], list) and len(data["ss"]) > 0:
                        ss_array = data["ss"][0]  # First array in ss
                        if isinstance(ss_array, list) and len(ss_array) > 0:
                            token = ss_array[0]  # First element is the token
                            
                            if token and len(token) > 10:  # Basic validation
                                logger.info(f"🔑 Successfully fetched auth token: {token[:8]}...")
                                
                                # Set token expiry (assume 1 hour, adjust as needed)
                                self.token_expires_at = datetime.now() + timedelta(hours=1)
                                
                                return token
                            else:
                                logger.error("🔑 Invalid token format received")
                        else:
                            logger.error("🔑 Invalid ss array structure")
                    else:
                        logger.error("🔑 Invalid response structure - missing 'ss' array")
                        logger.debug(f"Response data: {data}")
                else:
                    error_text = await response.text()
                    logger.error(f"🔑 Auth request failed: HTTP {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"🔑 Failed to fetch auth token: {e}")
        
        return None
    
    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid authentication token"""
        now = datetime.now()
        
        # Check if we need to refresh token
        needs_refresh = (
            self.bearer_token is None or
            self.token_expires_at is None or
            (self.token_expires_at - now).total_seconds() < self.token_refresh_threshold
        )
        
        if needs_refresh:
            logger.info("🔑 Token refresh needed, fetching new token...")
            new_token = await self._fetch_auth_token()
            
            if new_token:
                self.bearer_token = new_token
                return True
            else:
                logger.error("🔑 Failed to obtain valid auth token")
                return False
        
        return True
    
    def _generate_message_id(self, call_id: str, update_type: UpdateType) -> str:
        """Generate unique message ID for debugging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        uuid_part = str(uuid.uuid4())[:8]
        return f"{call_id}_{update_type.value}_{timestamp}_{uuid_part}"
    
    def _create_base64_message(self, payload: Dict[str, Any]) -> str:
        """Create base64 encoded message from payload"""
        json_message = json.dumps(payload, ensure_ascii=False)
        
        # Log the JSON payload before encoding
        logger.info(f"📋 [agent] JSON payload to be sent: {json_message}")
        
        encoded_bytes = base64.b64encode(json_message.encode('utf-8'))
        return encoded_bytes.decode('utf-8')
    
    async def _send_notification(self, call_id: str, update_type: UpdateType, 
                                payload: Dict[str, Any], retries: int = 0) -> bool:
        """Send notification to agent endpoint with retry logic"""
        
        try:
            await self._ensure_session()
            
            # Ensure we have a valid auth token
            if not await self._ensure_valid_token():
                logger.error(f"❌ Cannot send {update_type.value} for call {call_id}: No valid auth token")
                return False
            
            # Generate unique message ID
            message_id = self._generate_message_id(call_id, update_type)
            
            # Create timestamp
            timestamp = datetime.now().isoformat()
            
            # Encode message payload
            encoded_message = self._create_base64_message(payload)
            
            # Build request body
            request_body = {
                "channel": "aii",
                "session_id": call_id,
                "message_id": message_id,
                "timestamp": timestamp,
                "from": "gateway",
                "mime": "application/json",
                "message": encoded_message
            }
            
            # Set headers
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            # Send request
            async with self.session.post(
                self.endpoint_url, 
                json=request_body, 
                headers=headers
            ) as response:
                
                if 200 <= response.status < 300:  # Accept all 2xx success codes
                    logger.info(f"📤 [agent] Sent {update_type.value} update for call {call_id} "
                               f"(message_id: {message_id}) - HTTP {response.status}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ [agent] Failed to send {update_type.value} for call {call_id}: "
                                f"HTTP {response.status} - {error_text}")
                    return False
        
        except asyncio.TimeoutError:
            logger.error(f"⏰ [agent] Timeout sending {update_type.value} for call {call_id}")
            return False
        except aiohttp.ClientError as e:
            logger.error(f"🌐 [agent] Network error sending {update_type.value} for call {call_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ [agent] Unexpected error sending {update_type.value} for call {call_id}: {e}")
            return False
    
    async def send_call_start(self, call_id: str, connection_info: Dict[str, Any]) -> bool:
        """Notify agent that a new call has started"""
        payload = {
            "update_type": "call_start",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "connection_info": connection_info,
            "status": "active"
        }
        
        return await self._send_notification(call_id, UpdateType.CALL_START, payload)
    
    async def send_transcript_segment(self, call_id: str, segment_data: Dict[str, Any], 
                                    cumulative_transcript: str) -> bool:
        """Send new transcript segment to agent"""
        payload = {
            "update_type": "transcript_segment",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "segment": segment_data,
            "cumulative_transcript": cumulative_transcript,
            "transcript_length": len(cumulative_transcript)
        }
        
        return await self._send_notification(call_id, UpdateType.TRANSCRIPT_SEGMENT, payload)
    
    async def send_translation_update(self, call_id: str, window_id: int, 
                                    translation: str, cumulative_translation: str) -> bool:
        """Send translation update to agent"""
        payload = {
            "update_type": "translation_update", 
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "window_id": window_id,
            "window_translation": translation,
            "cumulative_translation": cumulative_translation,
            "translation_length": len(cumulative_translation)
        }
        
        return await self._send_notification(call_id, UpdateType.TRANSLATION_UPDATE, payload)
    
    async def send_entity_update(self, call_id: str, window_id: int, 
                               entities: Dict[str, Any], entity_evolution: list) -> bool:
        """Send entity extraction update to agent"""
        payload = {
            "update_type": "entity_update",
            "call_id": call_id, 
            "timestamp": datetime.now().isoformat(),
            "window_id": window_id,
            "entities": entities,
            "entity_count": sum(len(entity_list) for entity_list in entities.values()) if entities else 0,
            "entity_evolution": entity_evolution[-5:],  # Last 5 evolution steps
            "key_entities": {
                "persons": entities.get("PERSON", [])[:5] if entities else [],
                "locations": entities.get("LOC", [])[:3] if entities else [],
                "organizations": entities.get("ORG", [])[:3] if entities else []
            }
        }
        
        return await self._send_notification(call_id, UpdateType.ENTITY_UPDATE, payload)
    
    async def send_classification_update(self, call_id: str, window_id: int,
                                       classification: Dict[str, Any], classification_evolution: list) -> bool:
        """Send classification update to agent"""
        payload = {
            "update_type": "classification_update",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(), 
            "window_id": window_id,
            "classification": classification,
            "main_category": classification.get("main_category", "unknown") if classification else "unknown",
            "confidence": classification.get("confidence", 0) if classification else 0,
            "priority": classification.get("priority", "medium") if classification else "medium",
            "classification_evolution": classification_evolution[-5:],  # Last 5 evolution steps
            "confidence_trend": [c.get("confidence", 0) for c in classification_evolution[-3:]]  # Last 3 confidences
        }
        
        return await self._send_notification(call_id, UpdateType.CLASSIFICATION_UPDATE, payload)
    
    async def send_qa_update(self, call_id: str, qa_scores: Dict[str, Any], 
                           processing_info: Dict[str, Any] = None) -> bool:
        """Send QA analysis results to agent"""
        payload = {
            "update_type": "qa_update",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "qa_scores": qa_scores,
            "overall_qa_score": self._extract_overall_qa_score(qa_scores),
            "performance_grade": self._get_performance_grade(self._extract_overall_qa_score(qa_scores)),
            "processing_info": processing_info or {},
            "status": "completed"
        }
        
        return await self._send_notification(call_id, UpdateType.QA_UPDATE, payload)
    
    async def send_call_end(self, call_id: str, reason: str, final_stats: Dict[str, Any]) -> bool:
        """Notify agent that call has ended"""
        payload = {
            "update_type": "call_end",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "end_reason": reason,
            "final_stats": final_stats,
            "status": "completed"
        }
        
        return await self._send_notification(call_id, UpdateType.CALL_END, payload)
    
    async def send_call_summary(self, call_id: str, summary: str, final_analysis: Dict[str, Any]) -> bool:
        """Send final call summary to agent"""
        payload = {
            "update_type": "call_summary",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "final_analysis": final_analysis,
            "processing_complete": True
        }
        
        return await self._send_notification(call_id, UpdateType.CALL_SUMMARY, payload)
    
    async def send_call_insights(self, call_id: str, insights: Dict[str, Any]) -> bool:
        """Send call insights analysis to agent"""
        payload = {
            "update_type": "call_insights",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "processing_complete": True
        }
        
        return await self._send_notification(call_id, UpdateType.CALL_INSIGHTS, payload)
    
    async def send_gpt_insights(self, call_id: str, insights: Dict[str, Any]) -> bool:
        """Send GPT-generated case insights to agent"""
        payload = {
            "update_type": "gpt_insights",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "insights": insights,
            "processing_complete": True
        }
        
        return await self._send_notification(call_id, UpdateType.GPT_INSIGHTS, payload)
    
    async def send_unified_insight(self, call_id: str, pipeline_result: Dict[str, Any], 
                                 audio_info: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Send unified insight with complete pipeline results"""
        payload = {
            "update_type": "unified_insight",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "pipeline_result": pipeline_result,
            "audio_quality_info": audio_info,
            "processing_metadata": metadata,
            "processing_complete": True
        }
        
        return await self._send_notification(call_id, UpdateType.CALL_INSIGHTS, payload)
    
    async def send_error_notification(self, call_id: str, error_type: str, 
                                    error_message: str, error_context: Dict[str, Any] = None) -> bool:
        """Send error notification to agent"""
        payload = {
            "update_type": "error",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "error_context": error_context or {},
            "status": "error"
        }
        
        return await self._send_notification(call_id, UpdateType.ERROR, payload)
    
    # Batch notification methods for efficiency
    async def send_progressive_update(self, call_id: str, window_id: int, 
                                    window_data: Dict[str, Any]) -> bool:
        """Send comprehensive progressive update (translation + entities + classification)"""
        payload = {
            "update_type": "progressive_update",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "window_id": window_id,
            "window_data": window_data,
            "processing_complete": True
        }
        
        return await self._send_notification(call_id, UpdateType.TRANSLATION_UPDATE, payload)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Check health of agent notification service"""
        try:
            await self._ensure_session()
            
            # Check token status
            token_status = await self._ensure_valid_token()
            
            return {
                "service": "agent_notification_service",
                "status": "healthy" if token_status else "degraded",
                "endpoint": self.endpoint_url,
                "auth_endpoint": self.auth_endpoint_url,
                "session_active": self.session and not self.session.closed,
                "token_status": {
                    "has_token": self.bearer_token is not None,
                    "token_preview": self.bearer_token[:8] + "..." if self.bearer_token else None,
                    "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
                    "time_to_expiry": (self.token_expires_at - datetime.now()).total_seconds() if self.token_expires_at else None
                },
                "configuration": {
                    "asterisk_server_ip": self.asterisk_server_ip,
                    "max_retries": self.max_retries,
                    "request_timeout": self.request_timeout,
                    "token_refresh_threshold": self.token_refresh_threshold
                }
            }
        except Exception as e:
            return {
                "service": "agent_notification_service", 
                "status": "unhealthy",
                "error": str(e),
                "endpoint": self.endpoint_url,
                "auth_endpoint": self.auth_endpoint_url
            }
    
    def _extract_overall_qa_score(self, qa_scores: Dict[str, Any]) -> float:
        """Extract overall QA score from QA results"""
        if not qa_scores:
            return 0.0
            
        # If it's already processed with overall_qa_score
        if isinstance(qa_scores, dict) and 'overall_qa_score' in qa_scores:
            return float(qa_scores['overall_qa_score'])
            
        # Calculate from detailed scores
        if isinstance(qa_scores, dict) and 'detailed_scores' in qa_scores:
            detailed = qa_scores['detailed_scores']
            if isinstance(detailed, dict):
                scores = []
                for category_data in detailed.values():
                    if isinstance(category_data, dict) and 'score_percent' in category_data:
                        scores.append(category_data['score_percent'])
                return sum(scores) / len(scores) if scores else 0.0
                
        # Calculate from raw QA model output format
        if isinstance(qa_scores, dict):
            category_scores = []
            for category, submetrics in qa_scores.items():
                if isinstance(submetrics, list):
                    # Count passed submetrics
                    passed = sum(1 for sm in submetrics if sm.get('prediction', False))
                    total = len(submetrics)
                    if total > 0:
                        category_scores.append((passed / total) * 100)
            return sum(category_scores) / len(category_scores) if category_scores else 0.0
            
        return 0.0
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert QA score to performance grade"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Average" 
        elif score >= 60:
            return "Below Average"
        else:
            return "Poor"

# Global service instance
agent_notification_service = AgentNotificationService()