from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging

from .models import EmailVerification, Organization
from .token_manager import TokenManager
from .services.email_service import EmailService

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def request_email_verification(request):
    """
    Request an email verification OTP.
    
    POST parameters:
        email: Company email to verify
        organization_name: Name of the organization
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        organization_name = data.get('organization_name')
        
        if not email or not organization_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Email and organization name are required'
            }, status=400)
        
        # Create verification entry and generate OTP
        verification = EmailVerification.create_verification(email)
        print(f"Generated OTP: {verification.otp}")
        
        # Send OTP via email
        email_sent = EmailService.send_otp_email(email, verification.otp)
        # print(f"Email sent status: {email_sent}")
        if not email_sent:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send verification email'
            }, status=500)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Verification code sent to provided email',
            'email': email,
            'expires_at': verification.expires_at.isoformat()
        })
        
    except Exception as e:
        logger.exception(f"Error in email verification request: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_and_issue_token(request):
    """
    Verify OTP and issue an authentication token.
    
    POST parameters:
        email: Email that received the OTP
        otp: The verification code sent to the email
        organization_name: Name of the organization
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        organization_name = data.get('organization_name')
        
        if not email or not otp or not organization_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Email, OTP, and organization name are required'
            }, status=400)
        
        # Find the most recent verification for this email
        try:
            verification = EmailVerification.objects.filter(
                email=email,
                is_verified=False
            ).latest('created_at')
        except EmailVerification.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'No pending verification found for this email'
            }, status=404)
        
        # Check if OTP is valid
        if not verification.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': 'Verification has expired, please request a new code'
            }, status=400)
        
        # Verify OTP
        if verification.otp != otp:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid verification code'
            }, status=400)
        
        # Mark as verified
        verification.is_verified = True
        verification.save()
        
        # Generate JWT token
        token_data = TokenManager.generate_token(organization_name, email)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Email verified successfully',
            'token': token_data['token'],
            'organization_id': token_data['organization_id'],
            'expires': token_data['expires']
        })
        
    except Exception as e:
        logger.exception(f"Error in OTP verification: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)
