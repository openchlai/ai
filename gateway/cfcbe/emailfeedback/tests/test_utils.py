from datetime import datetime
from django.test import TestCase
from emailfeedback.models import Email
from emailfeedback.utils import forward_email_to_main_system
from unittest.mock import patch
from django.utils.timezone import make_aware


class ForwardEmailToMainSystemTest(TestCase):
    def setUp(self):
        # Set up test data with a datetime object for `received_date`
        self.email = Email.objects.create(
            sender="test@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="This is a test email body.",
            received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),  # Use datetime object
            is_read=False,
        )

    @patch("emailfeedback.utils.requests.post")
    def test_forward_email_success(self, mock_post):
        # Mock successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        response = forward_email_to_main_system(self.email)

        # Assert that the request was made
        mock_post.assert_called_once()
        # Validate the payload
        expected_payload = {
            "sender": self.email.sender,
            "recipient": self.email.recipient,
            "subject": self.email.subject,
            "body": self.email.body,
            "received_date": self.email.received_date.isoformat(),  # No error here
            "is_read": self.email.is_read,
        }
        mock_post.assert_called_with(
            "https://demo-openchs.bitz-itc.com/helpline/api/msg/",
            json=expected_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me",
            },
        )
        # Assert response
        self.assertEqual(response, {"status": "success"})
