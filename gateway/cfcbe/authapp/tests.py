from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from authapp.views import otp_store  # Import the in-memory OTP store

User = get_user_model()

class AuthAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.request_otp_url = reverse("request-otp")
        self.verify_otp_url = reverse("verify-otp")

        self.whatsapp_number = "1234567890"
        self.valid_user_data = {
            "whatsapp_number": self.whatsapp_number,
            "name": "Test User",
            "password": "testpass123"
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_register_user_already_exists(self):
        User.objects.create_user(username=self.whatsapp_number, password="testpass123")
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("authapp.views.send_whatsapp_message")
    @patch("authapp.views.get_access_token", return_value="fake-token")
    def test_request_otp_success(self, mock_get_token, mock_send_msg):
        User.objects.create_user(username=self.whatsapp_number, password="testpass123")
        response = self.client.post(self.request_otp_url, {
            "whatsapp_number": self.whatsapp_number
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_send_msg.assert_called_once()

    def test_request_otp_user_not_found(self):
        response = self.client.post(self.request_otp_url, {
            "whatsapp_number": "0000000000"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("authapp.views.get_access_token", return_value="fake-token")
    def test_verify_otp_success(self, mock_get_token):
        # Create user and manually inject OTP
        User.objects.create_user(username=self.whatsapp_number, password="testpass123")
        otp_store[self.whatsapp_number] = "654321"

        response = self.client.post(self.verify_otp_url, {
            "whatsapp_number": self.whatsapp_number,
            "otp": "654321"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_verify_otp_invalid(self):
        User.objects.create_user(username=self.whatsapp_number, password="testpass123")
        otp_store[self.whatsapp_number] = "123456"

        response = self.client.post(self.verify_otp_url, {
            "whatsapp_number": self.whatsapp_number,
            "otp": "999999"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
