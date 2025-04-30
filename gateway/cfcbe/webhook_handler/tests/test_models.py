from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import uuid

from webhook_handler.models import (
    Conversation, WebhookMessage, Organization, EmailVerification,
    Person, Complaint, CaseNote, ComplaintStatus, Notification,
    Voicenote, Contact, WhatsAppMedia, WhatsAppMessage, WhatsAppResponse,
    WhatsAppCredential
)

class ConversationModelTestCase(TestCase):
    """Tests for the Conversation model"""
    
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test-conversation-123",
            sender_id="sender-123",
            platform="whatsapp",
            is_active=True,
            metadata={"key": "value"}
        )
    
    def test_conversation_creation(self):
        """Test conversation model creation and string representation"""
        self.assertEqual(self.conversation.conversation_id, "test-conversation-123")
        self.assertEqual(self.conversation.sender_id, "sender-123")
        self.assertEqual(self.conversation.platform, "whatsapp")
        self.assertTrue(self.conversation.is_active)
        self.assertEqual(self.conversation.metadata, {"key": "value"})
        
        # Test string representation
        self.assertEqual(str(self.conversation), "whatsapp conversation with sender-123")


class WebhookMessageModelTestCase(TestCase):
    """Tests for the WebhookMessage model"""
    
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test-conversation-123",
            sender_id="sender-123",
            platform="whatsapp"
        )
        
        self.message = WebhookMessage.objects.create(
            message_id="msg-123",
            conversation=self.conversation,
            sender_id="sender-123",
            platform="whatsapp",
            content="Hello, world!",
            message_type="text",
            metadata={"key": "value"}
        )
    
    def test_webhook_message_creation(self):
        """Test webhook message model creation and string representation"""
        self.assertEqual(self.message.message_id, "msg-123")
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.sender_id, "sender-123")
        self.assertEqual(self.message.platform, "whatsapp")
        self.assertEqual(self.message.content, "Hello, world!")
        self.assertEqual(self.message.message_type, "text")
        self.assertEqual(self.message.metadata, {"key": "value"})
        
        # Test string representation
        self.assertEqual(str(self.message), "Message from sender-123 on whatsapp")


class OrganizationModelTestCase(TestCase):
    """Tests for the Organization model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            email="test@example.com",
            phone="1234567890"
        )
    
    def test_organization_creation(self):
        """Test organization model creation and string representation"""
        self.assertEqual(self.organization.name, "Test Organization")
        self.assertEqual(self.organization.email, "test@example.com")
        self.assertEqual(self.organization.phone, "1234567890")
        self.assertTrue(self.organization.is_active)
        
        # Test string representation
        self.assertEqual(str(self.organization), "Test Organization")


class EmailVerificationModelTestCase(TestCase):
    """Tests for the EmailVerification model"""
    
    def setUp(self):
        self.email = "test@example.com"
        self.verification = EmailVerification.create_verification(self.email)
    
    def test_email_verification_creation(self):
        """Test email verification model creation and string representation"""
        self.assertEqual(self.verification.email, self.email)
        self.assertEqual(len(self.verification.otp), 6)
        self.assertTrue(self.verification.otp.isdigit())
        self.assertFalse(self.verification.is_verified)
        self.assertGreater(self.verification.expires_at, timezone.now())
        
        # Test string representation
        self.assertEqual(str(self.verification), f"Verification for {self.email}")
    
    def test_is_valid_method(self):
        """Test is_valid method for verification validity"""
        # Valid verification
        self.assertTrue(self.verification.is_valid())
        
        # Invalid when verified
        self.verification.is_verified = True
        self.verification.save()
        self.assertFalse(self.verification.is_valid())
        
        # Invalid when expired
        self.verification.is_verified = False
        self.verification.expires_at = timezone.now() - timedelta(minutes=1)
        self.verification.save()
        self.assertFalse(self.verification.is_valid())


class PersonModelTestCase(TestCase):
    """Tests for the Person model"""
    
    def setUp(self):
        self.person = Person.objects.create(
            name="John Doe",
            age=30,
            gender="Male",
            additional_info="Some additional information"
        )
    
    def test_person_creation(self):
        """Test person model creation and string representation"""
        self.assertEqual(self.person.name, "John Doe")
        self.assertEqual(self.person.age, 30)
        self.assertEqual(self.person.gender, "Male")
        self.assertEqual(self.person.additional_info, "Some additional information")
        
        # Test string representation
        self.assertEqual(str(self.person), "John Doe")


class ComplaintModelTestCase(TestCase):
    """Tests for the Complaint model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            email="test@example.com"
        )
        
        self.conversation = Conversation.objects.create(
            conversation_id="test-conversation-123",
            sender_id="sender-123",
            platform="webform"
        )
        
        self.victim = Person.objects.create(
            name="Victim Name",
            age=25,
            gender="Female"
        )
        
        self.perpetrator = Person.objects.create(
            name="Perpetrator Name",
            age=35,
            gender="Male"
        )
        
        self.complaint = Complaint.objects.create(
            reporter_nickname="Anonymous Reporter",
            case_category="HARASSMENT",
            complaint_text="This is a test complaint",
            conversation=self.conversation,
            organization=self.organization,
            victim=self.victim,
            perpetrator=self.perpetrator
        )
    
    def test_complaint_creation(self):
        """Test complaint model creation and string representation"""
        self.assertIsNotNone(self.complaint.complaint_id)
        self.assertEqual(self.complaint.reporter_nickname, "Anonymous Reporter")
        self.assertEqual(self.complaint.case_category, "HARASSMENT")
        self.assertEqual(self.complaint.complaint_text, "This is a test complaint")
        self.assertEqual(self.complaint.conversation, self.conversation)
        self.assertEqual(self.complaint.organization, self.organization)
        self.assertEqual(self.complaint.victim, self.victim)
        self.assertEqual(self.complaint.perpetrator, self.perpetrator)
        
        # Test string representation
        self.assertEqual(str(self.complaint), 
                        f"Complaint {self.complaint.complaint_id} by Anonymous Reporter")


class NotificationModelTestCase(TestCase):
    """Tests for the Notification model"""
    
    def setUp(self):
        self.complaint = Complaint.objects.create(
            reporter_nickname="Anonymous",
            case_category="HARASSMENT",
            complaint_text="Test complaint"
        )
        
        self.notification = Notification.objects.create(
            complaint=self.complaint,
            message="Your complaint has been received"
        )
    
    def test_notification_creation(self):
        """Test notification model creation and string representation"""
        self.assertIsNotNone(self.notification.notification_id)
        self.assertEqual(self.notification.complaint, self.complaint)
        self.assertEqual(self.notification.message, "Your complaint has been received")
        self.assertFalse(self.notification.is_read)
        
        # Test string representation
        self.assertEqual(str(self.notification), 
                        f"Notification for Complaint {self.complaint.complaint_id}")


class WhatsAppMessageModelTestCase(TestCase):
    """Tests for the WhatsAppMessage model"""
    
    def setUp(self):
        self.contact = Contact.objects.create(
            wa_id="1234567890",
            name="Test Contact"
        )
        
        self.conversation = Conversation.objects.create(
            conversation_id="test-conversation-123",
            sender_id="sender-123",
            platform="whatsapp"
        )
        
        self.webhook_message = WebhookMessage.objects.create(
            message_id="msg-123",
            conversation=self.conversation,
            sender_id="sender-123",
            platform="whatsapp",
            content="Hello, world!"
        )
        
        self.whatsapp_message = WhatsAppMessage.objects.create(
            sender="sender-123",
            recipient=self.contact,
            conversation=self.conversation,
            webhook_message=self.webhook_message,
            message_type="text",
            content="Hello, world!",
            status="pending"
        )
    
    def test_whatsapp_message_creation(self):
        """Test WhatsApp message model creation and string representation"""
        self.assertEqual(self.whatsapp_message.sender, "sender-123")
        self.assertEqual(self.whatsapp_message.recipient, self.contact)
        self.assertEqual(self.whatsapp_message.conversation, self.conversation)
        self.assertEqual(self.whatsapp_message.webhook_message, self.webhook_message)
        self.assertEqual(self.whatsapp_message.message_type, "text")
        self.assertEqual(self.whatsapp_message.content, "Hello, world!")
        self.assertEqual(self.whatsapp_message.status, "pending")
        
        # Test string representation
        self.assertEqual(str(self.whatsapp_message), 
                        f"Message from sender-123 to {self.contact} (text, pending)")
    
    def test_status_methods(self):
        """Test WhatsApp message status update methods"""
        # Test mark_as_sent
        self.whatsapp_message.mark_as_sent()
        self.assertEqual(self.whatsapp_message.status, "sent")
        
        # Test mark_as_delivered
        self.whatsapp_message.mark_as_delivered()
        self.assertEqual(self.whatsapp_message.status, "delivered")
        
        # Test mark_as_read
        self.whatsapp_message.mark_as_read()
        self.assertEqual(self.whatsapp_message.status, "read")
        
        # Test mark_as_failed
        self.whatsapp_message.mark_as_failed()
        self.assertEqual(self.whatsapp_message.status, "failed")


class WhatsAppCredentialModelTestCase(TestCase):
    """Tests for the WhatsAppCredential model"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            email="test@example.com"
        )
        
        self.credential = WhatsAppCredential.objects.create(
            organization=self.organization,
            client_id="client-123",
            client_secret="secret-123",
            business_id="business-123",
            phone_number_id="phone-123",
            access_token="token-123"
        )
    
    def test_whatsapp_credential_creation(self):
        """Test WhatsApp credential model creation and string representation"""
        self.assertEqual(self.credential.organization, self.organization)
        self.assertEqual(self.credential.client_id, "client-123")
        self.assertEqual(self.credential.client_secret, "secret-123")
        self.assertEqual(self.credential.business_id, "business-123")
        self.assertEqual(self.credential.phone_number_id, "phone-123")
        self.assertEqual(self.credential.access_token, "token-123")
        
        # Test string representation
        self.assertEqual(str(self.credential), 
                       f"WhatsApp Credentials for {self.organization.name}")