from typing import Optional, List
from django.utils import timezone
from webhook_handler.models import Conversation, Contact

class ConversationService:
    """
    Manages the creation, retrieval, and updating of conversation state.
    
    This service ensures that messages from the same sender are grouped together
    and context is maintained across multiple interactions.
    """
    
    def get_or_create_conversation(self, sender_id: str, platform: str) -> Conversation:
        """
        Find or create a conversation for a sender.
        
        Args:
            sender_id: ID of the sender
            platform: Platform identifier
            
        Returns:
            The conversation object
        """
        # Generate a unique conversation ID
        conversation_id = f"{platform}:{sender_id}"
        
        # Try to get an existing active conversation
        conversation = Conversation.objects.filter(
            conversation_id=conversation_id,
            is_active=True
        ).first()
        
        # If no active conversation exists, create a new one
        if not conversation:
            conversation = Conversation.objects.create(
                conversation_id=conversation_id,
                sender_id=sender_id,
                platform=platform,
                is_active=True,
                last_activity=timezone.now()
            )
            
            # If this is a WhatsApp conversation, link to Contact if it exists
            if platform == 'whatsapp':
                contact = Contact.objects.filter(wa_id=sender_id).first()
                if contact and not contact.conversation:
                    contact.conversation = conversation
                    contact.save(update_fields=['conversation'])
        else:
            # Update last activity time
            conversation.last_activity = timezone.now()
            conversation.save(update_fields=['last_activity'])
        
        return conversation
    
    def close_conversation(self, conversation_id: str) -> bool:
        """
        Mark a conversation as inactive.
        
        Args:
            conversation_id: Unique ID of the conversation
            
        Returns:
            True if successful, False otherwise
        """
        conversation = Conversation.objects.filter(
            conversation_id=conversation_id
        ).first()
        
        if conversation:
            conversation.is_active = False
            conversation.save(update_fields=['is_active'])
            return True
        
        return False
    
    def get_conversations_for_sender(self, sender_id: str, platform: str = None) -> List[Conversation]:
        """
        Retrieve all conversations for a sender.
        
        Args:
            sender_id: ID of the sender
            platform: Optional platform filter
            
        Returns:
            List of conversation objects
        """
        query = {'sender_id': sender_id}
        
        if platform:
            query['platform'] = platform
        
        return list(Conversation.objects.filter(**query).order_by('-last_activity'))
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[dict]:
        """
        Retrieve conversation history.
        
        Collects messages from various platform-specific models based on the conversation.
        
        Args:
            conversation_id: Unique ID of the conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in chronological order
        """
        conversation = Conversation.objects.filter(conversation_id=conversation_id).first()
        if not conversation:
            return []
        
        # Get platform and sender_id from conversation
        platform = conversation.platform
        sender_id = conversation.sender_id
        
        messages = []
        
        # Get webhook messages (generic)
        webhook_messages = conversation.messages.all().order_by('timestamp')[:limit]
        for message in webhook_messages:
            messages.append({
                'id': message.message_id,
                'sender_id': message.sender_id,
                'content': message.content,
                'timestamp': message.timestamp,
                'type': message.message_type,
                'media_url': message.media_url,
                'platform': platform
            })
        
        # Get platform-specific messages
        if platform == 'webform':
            # Get complaint messages
            complaints = conversation.complaints.all().order_by('created_at')[:limit]
            for complaint in complaints:
                messages.append({
                    'id': str(complaint.complaint_id),
                    'sender_id': str(complaint.session_id),
                    'content': complaint.complaint_text,
                    'timestamp': complaint.created_at,
                    'type': 'complaint',
                    'media_url': complaint.complaint_image.url if complaint.complaint_image else None,
                    'platform': 'webform'
                })
                
        elif platform == 'whatsapp':
            # Get WhatsApp messages
            whatsapp_messages = conversation.whatsapp_messages.all().order_by('timestamp')[:limit]
            for message in whatsapp_messages:
                messages.append({
                    'id': message.id,
                    'sender_id': message.sender,
                    'recipient_id': message.recipient.wa_id if message.recipient else None,
                    'content': message.content,
                    'timestamp': message.timestamp,
                    'type': message.message_type,
                    'media_url': message.media.media_url if message.media else None,
                    'platform': 'whatsapp'
                })
        
        # Sort messages by timestamp
        messages.sort(key=lambda x: x['timestamp'])
        
        return messages