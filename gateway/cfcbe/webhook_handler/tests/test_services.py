from unittest.mock import patch, MagicMock
from django.test import TestCase

from webhook_handler.services.conversation_service import ConversationService
from webhook_handler.services.email_service import EmailService
from webhook_handler.models import (
    Conversation, WebhookMessage, Contact, WhatsAppMessage
)

class ConversationServiceTestCase(TestCase):
    """Tests for the ConversationService class"""
    
    def setUp(self):
        # Create test data for conversations
        self.conversation = Conversation.objects.create(
            conversation_id="test-convo-123",
            sender_id="user123",
            platform="whatsapp",
            is_active=True
        )
        
        self.message = WebhookMessage.objects.create(
            message_id="msg-123",
            conversation=self.conversation,
            sender_id="user123",
            platform="whatsapp",
            content="Test message"
        )
    
    def test_get_or_create_conversation(self):
        """Test getting an existing conversation or creating a new one"""
        # Test getting existing conversation
        conversation, created = ConversationService.get_or_create_conversation(
            sender_id="user123",
            platform="whatsapp"
        )
        
        self.assertEqual(conversation, self.conversation)
        self.assertFalse(created)
        
        # Test creating a new conversation
        new_conversation, created = ConversationService.get_or_create_conversation(
            sender_id="newuser456",
            platform="whatsapp"
        )
        
        self.assertNotEqual(new_conversation, self.conversation)
        self.assertEqual(new_conversation.sender_id, "newuser456")
        self.assertEqual(new_conversation.platform, "whatsapp")
        self.assertTrue(new_conversation.is_active)
        self.assertTrue(created)
    
    def test_add_message_to_conversation(self):
        """Test adding a message to a conversation"""
        # Add a new message to the existing conversation
        message = ConversationService.add_message_to_conversation(
            conversation=self.conversation,
            message_id="msg-456",
            content="Another test message",
            message_type="text"
        )
        
        # Verify the message was created correctly
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.message_id, "msg-456")
        self.assertEqual(message.sender_id, self.conversation.sender_id)
        self.assertEqual(message.platform, self.conversation.platform)
        self.assertEqual(message.content, "Another test message")
        self.assertEqual(message.message_type, "text")
    
    def test_update_conversation_activity(self):
        """Test updating a conversation's last activity timestamp"""
        # Get the initial timestamp
        initial_timestamp = self.conversation.last_activity
        
        # Update the conversation activity
        ConversationService.update_conversation_activity(self.conversation)
        
        # Refresh from the database
        self.conversation.refresh_from_db()
        
        # Verify the timestamp was updated
        self.assertGreater(self.conversation.last_activity, initial_timestamp)
    
    def test_mark_conversation_inactive(self):
        """Test marking a conversation as inactive"""
        # Verify the conversation is active initially
        self.assertTrue(self.conversation.is_active)
        
        # Mark the conversation as inactive
        ConversationService.mark_conversation_inactive(self.conversation)
        
        # Refresh from the database
        self.conversation.refresh_from_db()
        
        # Verify the conversation is now inactive
        self.assertFalse(self.conversation.is_active)
    
    def test_get_recent_messages(self):
        """Test retrieving recent messages from a conversation"""
        # Add additional messages to the conversation
        WebhookMessage.objects.create(
            message_id="msg-456",
            conversation=self.conversation,
            sender_id="user123",
            platform="whatsapp",
            content="Second message"
        )
        
        WebhookMessage.objects.create(
            message_id="msg-789",
            conversation=self.conversation,
            sender_id="user123",
            platform="whatsapp",
            content="Third message"
        )
        
        # Get recent messages (limit to 2)
        messages = ConversationService.get_recent_messages(self.conversation, limit=2)
        
        # Verify we got the expected number of messages
        self.assertEqual(len(messages), 2)
        
        # Verify they are the most recent messages (ordered by timestamp, which should be
        # in reverse chronological order by default)
        self.assertEqual(messages[0].message_id, "msg-789")
        self.assertEqual(messages[1].message_id, "msg-456")


class EmailServiceTestCase(TestCase):
    """Tests for the EmailService class"""
    
    @patch('webhook_handler.services.email_service.send_mail')
    def test_send_otp_email(self, mock_send_mail):
        """Test sending OTP email"""
        # Mock successful email sending
        mock_send_mail.return_value = 1
        
        # Call the service method
        result = EmailService.send_otp_email("test@example.com", "123456")
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify send_mail was called with the correct arguments
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        
        # Verify the email subject and recipient
        self.assertIn("Verification Code", kwargs['subject'])
        self.assertEqual(kwargs['recipient_list'], ["test@example.com"])
        self.assertIn("123456", kwargs['message'])
    
    @patch('webhook_handler.services.email_service.send_mail')
    def test_send_otp_email_failure(self, mock_send_mail):
        """Test handling of email sending failure"""
        # Mock email sending failure
        mock_send_mail.return_value = 0
        
        # Call the service method
        result = EmailService.send_otp_email("test@example.com", "123456")
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify send_mail was called
        mock_send_mail.assert_called_once()