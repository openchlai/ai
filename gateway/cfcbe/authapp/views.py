from django.shortcuts import render

# Create your views here.
import pyotp
import json
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from whatsapp.views import send_whatsapp_message



User = get_user_model()

import random

# Simulated OTP storage
otp_store = {}

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
import logging

# Import necessary functions
from whatsapp.views import send_whatsapp_message  
from whatsapp.utils import get_access_token  

User = get_user_model()
otp_store = {}  # Temporary store for OTPs

class RequestOTPView(APIView):
    def post(self, request):
        whatsapp_number = request.data.get("whatsapp_number")
        org_id = 1  # Assuming org_id is provided in request

        if not org_id:
            return Response({"error": "Organization ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=whatsapp_number)
        except ObjectDoesNotExist:
            return Response(
                {"error": "User not found. Please register first."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Get access token dynamically
        access_token = get_access_token(org_id)
        if not access_token:
            return Response(
                {"error": "Failed to retrieve WhatsApp access token."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        otp_store[whatsapp_number] = otp  # Store OTP temporarily

        # Construct the message
        otp_message = f"Your OTP is: {otp}. It expires in 5 minutes."

        # Send OTP via WhatsApp
        try:
            send_whatsapp_message(
                access_token=access_token, 
                recipient=whatsapp_number, 
                message_type="text", 
                content=otp_message
            )
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Failed to send OTP: {e}")
            return Response(
                {"error": "Failed to send OTP. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


from rest_framework_simplejwt.tokens import RefreshToken

class VerifyOTPView(APIView):
    def post(self, request):
        whatsapp_number = request.data.get("whatsapp_number")
        otp = request.data.get("otp")

        # Check if OTP is correct
        if otp_store.get(whatsapp_number) == otp:
            user = User.objects.get(username=whatsapp_number)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Remove OTP after successful login
            del otp_store[whatsapp_number]

            return Response({
                "access": access_token,
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

class RegisterUserView(APIView):
    def post(self, request):
        whatsapp_number = request.data.get("whatsapp_number")
        name = request.data.get("name")
        password = request.data.get("password")

        if not whatsapp_number or not password:
            return Response({"error": "WhatsApp number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        if User.objects.filter(username=whatsapp_number).exists():
            return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User.objects.create_user(username=whatsapp_number, password=password, first_name=name)
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
