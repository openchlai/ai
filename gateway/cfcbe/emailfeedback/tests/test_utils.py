from datetime import datetime
from django.test import TestCase
from emailfeedback.models import Email
from emailfeedback.utils import fetch_emails, extract_email_body, forward_email_to_main_system
from unittest.mock import patch, MagicMock
from django.utils.timezone import make_aware
from django.db.models.signals import post_save
from emailfeedback.signals import forward_email
import email
from email.message import EmailMessage
import requests

class EmailUtilsTest(TestCase):
    def setUp(self):
        # Disconnect signal to prevent side effects
        post_save.disconnect(forward_email, sender=Email)
        self.email = Email.objects.create(
            sender="test@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="This is a test email body.",
            received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
            is_read=False,
            raw_message=b"test raw message"
        )

    def tearDown(self):
        # Reconnect signal
        post_save.connect(forward_email, sender=Email)

    @patch("emailfeedback.utils.imaplib.IMAP4_SSL")
    def test_fetch_emails_success(self, mock_imap):
        # Mock IMAP server and email fetching
        mock_server = MagicMock()
        mock_imap.return_value = mock_server
        mock_server.login.return_value = ("OK", [])
        mock_server.select.return_value = ("OK", [])
        mock_server.search.return_value = ("OK", [b"1"])
        mock_server.fetch.return_value = ("OK", [(b"1", b"Subject: Test\nFrom: test@example.com\nDate: Mon, 21 Jan 2025 10:00:00 +0000\n\nTest body")])

        # Call the function
        fetch_emails("test@example.com", "password")

        # Assert email was saved
        self.assertTrue(Email.objects.filter(subject="Test").exists())
        email_obj = Email.objects.get(subject="Test")
        self.assertEqual(email_obj.sender, "test@example.com")
        self.assertEqual(email_obj.recipient, "test@example.com")
        self.assertEqual(email_obj.body, "Test body")

        # Assert IMAP interactions
        mock_server.login.assert_called_with("test@example.com", "password")
        mock_server.select.assert_called_with("inbox")
        mock_server.close.assert_called_once()
        mock_server.logout.assert_called_once()

    @patch("emailfeedback.utils.imaplib.IMAP4_SSL")
    def test_fetch_emails_failure(self, mock_imap):
        # Mock IMAP connection failure
        mock_imap.side_effect = Exception("Connection failed")

        # Clear any existing emails
        Email.objects.all().delete()

        # Call the function and ensure no emails are saved
        fetch_emails("test@example.com", "password")
        self.assertFalse(Email.objects.exists())

    def test_extract_email_body_text(self):
        # Create a simple text email
        msg = EmailMessage()
        msg.set_content("This is a text email")
        body = extract_email_body(msg)
        self.assertEqual(body, "This is a text email\n")

    def test_extract_email_body_multipart(self):
        # Create a multipart email with text and HTML
        msg = EmailMessage()
        msg.make_mixed()
        msg.add_alternative("Text part", subtype="plain")
        msg.add_alternative("<p>HTML part</p>", subtype="html")
        body = extract_email_body(msg)
        self.assertIn("Text part", body)
        self.assertIn("<p>HTML part</p>", body)

    def test_extract_email_body_decode_error(self):
        # Mock a message with a decode error
        msg = MagicMock()
        msg.is_multipart.return_value = False
        msg.get_content_type.return_value = "text/plain"
        msg.get_payload.side_effect = Exception("Decode error")
        body = extract_email_body(msg)
        self.assertEqual(body, "")

    @patch("emailfeedback.utils.requests.post")
    def test_forward_email_success(self, mock_post):
        # Mock successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '{"status": "success"}'

        # Call the function
        forward_email_to_main_system(self.email)

        # Assert the request was made with correct payload
        expected_payload = {
            "channel": "email",
            "timestamp": self.email.received_date.isoformat(),
            "session_id": self.email.id,
            "message_id": str(self.email.id),
            "from": self.email.sender,
            "message": "dGVzdCByYXcgbWVzc2FnZQ==",  # Base64 of b"test raw message"
            "mime": "text/plain",
        }
        mock_post.assert_called_with(
            "https://demo-openchs.bitz-itc.com/helpline/api/msg/",
            json=expected_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sci9de994iddqlmj8fv7r1js74",
            },
        )

    @patch("emailfeedback.utils.requests.post")
    def test_forward_email_failure(self, mock_post):
        # Mock HTTP error
        mock_post.side_effect = requests.exceptions.HTTPError("API error")

        # Call the function and ensure it handles the error gracefully
        forward_email_to_main_system(self.email)
        mock_post.assert_called_once()