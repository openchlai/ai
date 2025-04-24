from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class StandardMessage:
    """
    Standardized message format aligned with endpoint formats.
    
    This class represents the common structure between different endpoint formats
    (messaging endpoint and cases endpoint) to provide a consistent internal representation.
    """
    
    # Common fields that directly map to endpoint formats
    source: str               # 'whatsapp', 'webform', etc. (maps to 'channel'/'src')
    source_uid: str           # Sender identifier (maps to 'session_id'/'src_uid')
    source_address: str       # Sender address (maps to 'from'/'src_address')
    message_id: str           # Unique message identifier (maps to 'message_id'/'src_callid')
    source_timestamp: float   # Unix timestamp (maps to 'timestamp'/'src_ts')
    content: str              # The message content (will be encoded for messaging endpoint)
    platform: str             # Internal platform identifier (may be different from source)
    content_type: str = "text/plain"  # MIME type for the content
    media_url: Optional[str] = None  # URL to any media content
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the StandardMessage to a dictionary."""
        return {
            'source': self.source,
            'source_uid': self.source_uid,
            'source_address': self.source_address,
            'message_id': self.message_id,
            'source_timestamp': self.source_timestamp,
            'content': self.content,
            'content_type': self.content_type,
            'platform': self.platform,
            'media_url': self.media_url,
            'metadata': self.metadata
        }
    
    def get_iso_timestamp(self) -> str:
        """
        Convert the Unix timestamp to ISO format.
        Useful for the messaging endpoint format.
        """
        return datetime.fromtimestamp(self.source_timestamp).isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StandardMessage':
        """Create a StandardMessage from a dictionary."""
        return cls(
            source=data['source'],
            source_uid=data['source_uid'],
            source_address=data['source_address'],
            message_id=data['message_id'],
            source_timestamp=data['source_timestamp'],
            content=data['content'],
            platform=data['platform'],
            content_type=data.get('content_type', 'text/plain'),
            media_url=data.get('media_url'),
            metadata=data.get('metadata', {})
        )