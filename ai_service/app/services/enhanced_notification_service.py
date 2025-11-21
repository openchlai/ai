"""
Enhanced Notification Service for v2.0 Payloads

This service is responsible for creating, validating, and sending standardized
notification payloads to the helpline's frontend or any other consuming service.
It supports different processing modes, notification types, and encoding options.
"""
import asyncio
import base64
import httpx
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, Optional, List, Literal

from pydantic import BaseModel, Field

from app.config.settings import settings

# Suppress SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add these imports with the existing imports
from ..db.session import SessionLocal
from ..db.repositories.feedback_repository import FeedbackRepository

# Configure logging
logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    """Defines the types of notifications that can be sent."""
    # Streaming
    CALL_START = "call_start"
    TRANSCRIPTION_UPDATE = "transcription_update"
    TRANSLATION_UPDATE = "translation_update"
    ENTITY_UPDATE = "entity_update"
    CLASSIFICATION_UPDATE = "classification_update"
    CALL_END_STREAMING = "call_end_streaming"

    # Post-call
    POST_CALL_START = "post_call_start"
    POST_CALL_TRANSCRIPTION = "post_call_transcription"
    POST_CALL_TRANSLATION = "post_call_translation"
    POST_CALL_ENTITIES = "post_call_entities"
    POST_CALL_CLASSIFICATION = "post_call_classification"
    POST_CALL_SUMMARY = "post_call_summary"
    POST_CALL_QA_SCORING = "post_call_qa_scoring"
    POST_CALL_COMPLETE = "post_call_complete"

    # Status
    PROCESSING_PROGRESS = "processing_progress"
    PROCESSING_ERROR = "processing_error"

class ProcessingMode(str, Enum):
    """Defines the processing modes for a call."""
    STREAMING = "streaming"
    POST_CALL = "post_call"
    DUAL = "dual"
    ADAPTIVE = "adaptive"

class NotificationStatus(str, Enum):
    """Defines the status of the notification payload."""
    SUCCESS = "success"
    IN_PROGRESS = "in_progress"
    ERROR = "error"

class UIMetadata(BaseModel):
    """UI-specific metadata to guide frontend rendering."""
    priority: int = Field(1, description="Priority for display (1-5, 1 is highest)")
    display_panel: str = Field("main", description="Target panel for this info")
    requires_action: bool = Field(False, description="Requires user action")
    alert_type: Optional[str] = Field(None, description="Alert type (info, warning, critical)")

class ErrorPayload(BaseModel):
    """Standardized error payload."""
    error_type: str
    error_message: str
    component: str

class NotificationV2(BaseModel):
    """Standardized v2.0 notification payload schema."""
    version: Literal["2.0"] = "2.0"  # Use Literal instead of const
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    processing_mode: ProcessingMode
    call_metadata: Dict[str, Any]
    notification_type: NotificationType
    payload: Dict[str, Any]
    status: NotificationStatus = NotificationStatus.SUCCESS
    error: Optional[ErrorPayload] = None
    ui_metadata: Optional[UIMetadata] = None


class EnhancedNotificationService:
    """Service to send standardized v2.0 notifications."""
    
    def __init__(self):
        self.endpoint_url = settings.notification_endpoint_url
        self.auth_endpoint_url = settings.notification_auth_endpoint_url
        self.basic_auth = settings.notification_basic_auth
        self.bearer_token = None
        self.token_expires_at = None
        self.token_refresh_threshold = 300  # 5 minutes
        self.use_base64 = settings.use_base64_encoding
        self.site_id = settings.site_id

        # Create async HTTP client (disable SSL verification for self-signed certs)
        self.client = httpx.AsyncClient(
            timeout=settings.notification_request_timeout,
            verify=False  # Disable SSL verification for self-signed certificates
        )

        # Payload logging configuration
        self.enable_payload_logging = settings.enable_agent_payload_logging
        self.payload_log_file = settings.agent_payload_log_file

        # Initialize payload logging if enabled
        if self.enable_payload_logging:
            self._initialize_payload_logging()

        logger.info("✅ EnhancedNotificationService initialized")

    def _initialize_payload_logging(self):
        """Initialize payload logging file and directory."""
        try:
            import os
            log_dir = os.path.dirname(self.payload_log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # Create or verify the log file exists
            if not os.path.exists(self.payload_log_file):
                with open(self.payload_log_file, 'w') as f:
                    # Write header comment
                    f.write(f"# Agent Payload Log - Started at {datetime.now().isoformat()}\n")
                    f.write("# Each line is a JSON object representing a notification payload\n")
                    f.write("# Format: JSONL (JSON Lines) - one object per line\n")

            logger.info(f"📝 Payload logging enabled: {self.payload_log_file}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize payload logging: {e}")
            self.enable_payload_logging = False

    def _log_payload(self, payload: Dict[str, Any], request_body: Dict[str, Any]):
        """
        Log payload to file for UI development.

        Args:
            payload: The original notification payload (v2.0 format)
            request_body: The actual request body being sent (may be wrapped in base64)
        """
        if not self.enable_payload_logging:
            return

        try:
            log_entry = {
                "logged_at": datetime.now().isoformat(),
                "notification_type": payload.get("notification_type"),
                "call_id": payload.get("call_metadata", {}).get("call_id"),
                "message_id": payload.get("message_id"),
                "processing_mode": payload.get("processing_mode"),
                "use_base64_encoding": self.use_base64,
                "original_payload": payload,
                "request_body": request_body
            }

            # Append to JSONL file
            with open(self.payload_log_file, 'a') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

            logger.debug(f"📝 Logged payload: {payload.get('notification_type')} for call {log_entry['call_id']}")

        except Exception as e:
            logger.error(f"❌ Failed to log payload: {e}")

    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid bearer token."""
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
                logger.warning("⚠️ Failed to obtain valid auth token, using basic auth")
                return False
        
        return True
    
    async def _fetch_auth_token(self) -> Optional[str]:
        """Fetch bearer token from auth endpoint."""
        try:
            headers = {
                "Authorization": f"Basic {self.basic_auth}",
                "Content-Type": "application/json"
            }

            # Debug logging
            logger.info(f"🔐 [token] Fetching token from: {self.auth_endpoint_url}")
            logger.info(f"🔐 [token] Headers: Authorization=Basic {self.basic_auth[:20]}..., Content-Type={headers['Content-Type']}")

            response = await self.client.post(
                self.auth_endpoint_url,
                headers=headers
            )

            # Debug response
            logger.info(f"🔐 [token] Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"🔐 [token] Response keys: {list(data.keys())}")

                token = data.get("access_token") or data.get("token")

                if token:
                    # Set expiration (default 1 hour if not provided)
                    expires_in = data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                    logger.info("✅ Successfully fetched bearer token")
                    return token
                else:
                    logger.error(f"❌ No token found in response. Keys: {list(data.keys())}")
            else:
                # Log detailed error response
                try:
                    error_body = response.text
                    logger.error(f"❌ Failed to fetch token: HTTP {response.status_code}")
                    logger.error(f"❌ Response body: {error_body[:500]}")
                except:
                    logger.error(f"❌ Failed to fetch token: HTTP {response.status_code} (couldn't read response body)")

            return None

        except Exception as e:
            logger.error(f"❌ Error fetching auth token: {e}", exc_info=True)
            return None
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        await self._ensure_valid_token()
        
        return {
            "Authorization": f"Bearer {self.bearer_token}" if self.bearer_token else f"Basic {self.basic_auth}",
            "Content-Type": "application/json"
        }

    def _create_base_payload(
        self,
        call_id: str,
        notification_type: NotificationType,
        processing_mode: ProcessingMode,
        payload_data: Dict[str, Any],
        status: NotificationStatus = NotificationStatus.SUCCESS,
        error_info: Optional[Dict[str, str]] = None,
        ui_metadata: Optional[Dict[str, Any]] = None,
        call_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized base payload structure."""
        
        full_call_metadata = {
            "call_id": call_id,
            "site_id": settings.site_id,
            **(call_metadata or {})
        }
        
        base_payload = {
            "version": "2.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_mode": processing_mode.value,
            "call_metadata": full_call_metadata,
            "notification_type": notification_type.value,
            "payload": payload_data,
            "status": status.value,
            "error": error_info,
            "ui_metadata": ui_metadata
        }
        
        return base_payload

    async def _send_notification(self, data: Dict[str, Any]) -> bool:
        """Send notification with retry logic."""
        headers = await self._get_auth_headers()

        # Prepare request body
        if self.use_base64:
            json_string = json.dumps(data, ensure_ascii=False)
            encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
            request_body = {
                "channel": "aii",
                "session_id": data["call_metadata"]["call_id"],
                "message_id": data["message_id"],
                "timestamp": data["timestamp"],
                "from": "gateway",
                "mime": "application/json",
                "message": encoded
            }
            logger.info(f"📤 [notify] Using base64 encoding, wrapper keys: {list(request_body.keys())}")
            logger.info(f"📤 [notify] Original payload keys: {list(data.keys())}")
        else:
            request_body = data
            logger.info(f"📤 [notify] Using direct JSON, payload keys: {list(request_body.keys())}")

        logger.info(f"📤 [notify] Sending to: {self.endpoint_url}")
        logger.info(f"📤 [notify] Notification type: {data.get('notification_type')}")

        # Log payload for UI development
        self._log_payload(data, request_body)
        
        # Retry logic
        retry_attempts = getattr(settings, 'notification_retry_attempts', 3)
        retry_delay = getattr(settings, 'notification_retry_delay', 2)
        
        for attempt in range(retry_attempts):
            try:
                response = await self.client.post(
                    self.endpoint_url,
                    json=request_body,
                    headers=headers
                )
                response.raise_for_status()
                
                logger.info(
                    f"✅ Sent {data['notification_type']} for call {data['call_metadata']['call_id']}"
                )
                return True
                
            except httpx.HTTPStatusError as e:
                # Log detailed error information
                try:
                    error_body = e.response.text
                    logger.error(
                        f"❌ HTTP Error (attempt {attempt + 1}/{retry_attempts}): "
                        f"{e.response.status_code} - Response: {error_body[:500]}"
                    )
                except:
                    logger.error(
                        f"❌ HTTP Error (attempt {attempt + 1}/{retry_attempts}): "
                        f"{e.response.status_code}"
                    )
            except httpx.RequestError as e:
                logger.error(
                    f"❌ Request Error (attempt {attempt + 1}/{retry_attempts}): {e}"
                )
            
            if attempt < retry_attempts - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))
        
        logger.error(f"❌ Failed to send notification after {retry_attempts} attempts")
        return False

    async def send_notification(
        self,
        call_id: str,
        notification_type: NotificationType,
        processing_mode: ProcessingMode,
        payload_data: Dict[str, Any],
        call_metadata: Optional[Dict[str, Any]] = None,
        status: NotificationStatus = NotificationStatus.SUCCESS,
        error_info: Optional[Dict[str, str]] = None,
        ui_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Constructs and sends a standardized notification."""
        try:
            payload = self._create_base_payload(
                call_id=call_id,
                notification_type=notification_type,
                processing_mode=processing_mode,
                payload_data=payload_data,
                status=status,
                error_info=error_info,
                ui_metadata=ui_metadata,
                call_metadata=call_metadata or {}
            )
            
            return await self._send_notification(payload)
            
        except Exception as e:
            logger.error(f"❌ Failed to construct notification for {call_id}: {e}")
            return False

    # Helper methods for specific notification types
    async def send_streaming_transcription(
        self,
        call_id: str,
        segment_text: str,
        cumulative_transcript: str,
        **metadata
    ) -> bool:
        """Send streaming transcription update."""
        
        payload_data = {
            "segment_text": segment_text,
            "cumulative_transcript": cumulative_transcript,
            "segment_id": metadata.get("segment_id"),
            "word_count": len(segment_text.split()),
            "confidence_score": metadata.get("confidence", 0.90)
        }
        
        ui_metadata = {
            "priority": 1,
            "display_panel": "transcript",
            "requires_action": False
        }
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.TRANSCRIPTION_UPDATE,
            processing_mode=ProcessingMode.STREAMING,
            payload_data=payload_data,
            call_metadata=metadata,
            ui_metadata=ui_metadata
        )
    
    async def send_streaming_translation(
        self,
        call_id: str,
        window_text: str,
        cumulative_translation: str,
        **metadata
    ) -> bool:
        """Send streaming translation update."""
        
        payload_data = {
            "window_text": window_text,
            "cumulative_translation": cumulative_translation,
            "window_id": metadata.get("window_id"),
            "word_count": len(window_text.split())
        }
        
        ui_metadata = {
            "priority": 2,
            "display_panel": "translation"
        }
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.TRANSLATION_UPDATE,
            processing_mode=ProcessingMode.STREAMING,
            payload_data=payload_data,
            call_metadata=metadata,
            ui_metadata=ui_metadata
        )

    async def send_streaming_entities(
        self,
        call_id: str,
        entities: Dict,
        **metadata
    ) -> bool:
        """Send streaming entities update."""
        
        payload_data = {
            "entities": entities,
            "entity_count": sum(len(e) for e in entities.values()) if isinstance(entities, dict) else 0
        }
        
        ui_metadata = {
            "priority": 1,
            "display_panel": "entities"
        }
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.ENTITY_UPDATE,
            processing_mode=ProcessingMode.STREAMING,
            payload_data=payload_data,
            call_metadata=metadata,
            ui_metadata=ui_metadata
        )

    async def send_streaming_classification(
        self,
        call_id: str,
        classification: Dict,
        **metadata
    ) -> bool:
        """Send streaming classification update."""
        
        payload_data = {
            "classification": classification
        }
        
        ui_metadata = {
            "priority": 1,
            "display_panel": "classification",
            "alert_type": "warning" if classification.get("urgency") == "high" else "info"
        }
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.CLASSIFICATION_UPDATE,
            processing_mode=ProcessingMode.STREAMING,
            payload_data=payload_data,
            call_metadata=metadata,
            ui_metadata=ui_metadata
        )

    async def send_call_start(
        self,
        call_id: str,
        processing_mode: ProcessingMode,
        processing_config: Dict,
        **metadata
    ) -> bool:
        """Send call start notification - DISABLED."""
        logger.debug(f"🔕 call_start notification disabled for call {call_id}")
        return True  # Return success without sending

    async def send_call_end_streaming(
        self,
        call_id: str,
        cumulative_transcript: str,
        processing_mode: ProcessingMode,
        **metadata
    ) -> bool:
        """Send call end streaming notification - DISABLED."""
        logger.debug(f"🔕 call_end_streaming notification disabled for call {call_id}")
        return True  # Return success without sending

    async def send_postcall_transcription(
        self,
        call_id: str,
        full_transcript: str,
        **metadata
    ) -> bool:
        """Send post-call transcription."""
        
        payload_data = {
            "full_transcript": full_transcript,
            "word_count": len(full_transcript.split()),
            "confidence_score": metadata.get("confidence_score", 0.95)
        }
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.POST_CALL_TRANSCRIPTION,
            processing_mode=ProcessingMode.POST_CALL,
            payload_data=payload_data,
            call_metadata=metadata
        )

    async def send_postcall_complete(
        self,
        call_id: str,
        unified_insights: Dict,
        pipeline_results: Dict,
        **metadata
    ) -> bool:
        """Send post-call complete notification."""
    
        # ✨ ADD THIS: Create feedback entries for all completed tasks
        processing_mode = metadata.get('processing_mode', 'post_call')
        await self.create_feedback_entries(call_id, pipeline_results, processing_mode)
    
        # Existing notification logic continues below
        payload_data = {
            "unified_insights": unified_insights,
            "pipeline_results": pipeline_results
        }
    
        ui_metadata = {
            "priority": 1,
            "display_panel": "insights",
            "requires_action": True
        }
    
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.POST_CALL_COMPLETE,
            processing_mode=ProcessingMode.POST_CALL,
            payload_data=payload_data,
            call_metadata=metadata,
            ui_metadata=ui_metadata
        )
    async def send_progress_update(
        self,
        call_id: str,
        stage: str,
        progress_percent: int,
        **metadata
    ) -> bool:
        """Send progress update."""
        
        payload_data = {
            "stage": stage,
            "progress_percent": progress_percent
        }
        
        mode = metadata.get("processing_mode", ProcessingMode.POST_CALL)
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.PROCESSING_PROGRESS,
            processing_mode=mode,
            payload_data=payload_data,
            call_metadata=metadata,
            status=NotificationStatus.IN_PROGRESS
        )

    async def send_error_notification(
        self,
        call_id: str,
        error_type: str,
        error_message: str,
        component: str,
        **metadata
    ) -> bool:
        """Send error notification."""
        
        error_info = {
            "error_type": error_type,
            "error_message": error_message,
            "component": component
        }
        
        mode = metadata.get("processing_mode", ProcessingMode.POST_CALL)
        
        return await self.send_notification(
            call_id=call_id,
            notification_type=NotificationType.PROCESSING_ERROR,
            processing_mode=mode,
            payload_data={},
            call_metadata=metadata,
            status=NotificationStatus.ERROR,
            error_info=error_info
        )

    async def create_feedback_entries(self, call_id: str, pipeline_results: Dict[str, Any], processing_mode: str = None):
        """
        Create initial feedback entries for all tasks when processing completes.
        Called automatically when sending notifications.
    
        Args:
            call_id: Unique call identifier
            pipeline_results: Complete pipeline results containing all task outputs
            processing_mode: Processing mode used
        """
        try:
            db = SessionLocal()

            # Map of task names to their results in pipeline output
            task_mapping = {
                'transcription': pipeline_results.get('transcript'),
                'classification': pipeline_results.get('classification'),
                'ner': pipeline_results.get('entities'),
                'summarization': pipeline_results.get('summary'),
                'translation': pipeline_results.get('translation'),
                'qa': pipeline_results.get('qa_analysis') or pipeline_results.get('qa_scores'),
            }

            created_count = 0
            for task, prediction in task_mapping.items():
                # Create feedback entry if task was attempted (even if result is empty)
                # Skip only if prediction is explicitly None (task was skipped)
                if prediction is not None:
                    # Ensure we have a valid prediction object (convert empty to appropriate type)
                    if prediction == {} or prediction == "" or prediction == []:
                        # Keep empty results as-is for feedback
                        pass

                    feedback = FeedbackRepository.create_initial_feedback(
                        db=db,
                        call_id=call_id,
                        task=task,
                        prediction=prediction if prediction else {},  # Use empty dict if falsy
                        processing_mode=processing_mode,
                        model_version=None  # Can be enhanced to track versions
                    )
                    if feedback:
                        created_count += 1

            db.close()
            logger.info(f"✅ Created {created_count} feedback entries for call {call_id}")

        except Exception as e:
            logger.error(f"❌ Failed to create feedback entries: {e}")

    
  
# Singleton instance
notification_service = EnhancedNotificationService()
enhanced_notification_service = notification_service  # Alias for backward compatibility