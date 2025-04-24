from django.core.mail import send_mail, get_connection
from django.conf import settings
import logging
import socket
import time

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails through the system with enhanced error handling."""
    
    @staticmethod
    def send_otp_email(recipient_email, otp):
        """
        Send an email with OTP for verification.
        
        Args:
            recipient_email: Email address to send to
            otp: One-time password to include in the email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "Your Gateway Integration Verification Code"
        message = f"""
        Hello,
        
        Your verification code for the Unified Communication Gateway integration is:
        
        {otp}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Regards,
        The UCG Team
        """
        
        sender_email = settings.DEFAULT_FROM_EMAIL
        
        # Debug information
        logger.info(f"Attempting to send email to {recipient_email}")
        logger.info(f"Using EMAIL_HOST: {settings.EMAIL_HOST}")
        logger.info(f"Using EMAIL_PORT: {settings.EMAIL_PORT}")
        logger.info(f"Using EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        logger.info(f"Using EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        
        # Print OTP generation info for debugging
        print(f"\nAttempting to send OTP email to {recipient_email}")
        print(f"Generated OTP: {otp}")
        
        # First try: Standard approach
        try:
            # First make sure we can even reach the mail server
            EmailService._check_mail_server_connectivity()
            
            # Try to send the email with timeout protection
            send_mail(
                subject,
                message,
                sender_email,
                [recipient_email],
                fail_silently=False
            )
            
            logger.info(f"OTP email sent to {recipient_email}")
            print(f"SUCCESS: OTP email sent to {recipient_email}")
            print(f"Email content: {message}")
            print(f"Sender email: {sender_email}")
            print(f"Recipient email: {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"First attempt failed: {str(e)}")
            print(f"First attempt failed: {str(e)}")
            
            # Second try: Custom connection with different settings
            try:
                logger.info("Trying alternative connection method...")
                print("Trying alternative connection method...")
                
                # Get a custom connection with explicit timeout
                connection = EmailService._get_alternative_connection()
                
                # Try sending with the custom connection
                success = send_mail(
                    subject,
                    message,
                    sender_email,
                    [recipient_email],
                    fail_silently=False,
                    connection=connection
                )
                
                if success:
                    logger.info(f"Second attempt succeeded: OTP email sent to {recipient_email}")
                    print(f"Second attempt succeeded: OTP email sent to {recipient_email}")
                    return True
                    
            except Exception as e2:
                logger.error(f"Second attempt also failed: {str(e2)}")
                print(f"Second attempt also failed: {str(e2)}")
                
                # For development/testing environment, return True even if email fails
                # This allows testing to continue without email
                if settings.DEBUG:
                    logger.warning("DEBUG mode is on - treating email as sent for testing purposes")
                    print("DEBUG mode is on - treating email as sent for testing purposes")
                    print(f"The OTP that would have been sent is: {otp}")
                    return True
            
            # If we get here, both attempts failed and we're not in DEBUG mode
            return False
    
    @staticmethod
    def _check_mail_server_connectivity():
        """Check if the mail server is reachable."""
        try:
            host = settings.EMAIL_HOST
            port = settings.EMAIL_PORT
            
            # Create a socket connection to test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            
            logger.info(f"Testing connection to {host}:{port}")
            print(f"Testing connection to {host}:{port}")
            result = sock.connect_ex((host, port))
            
            if result == 0:
                logger.info(f"Connection to {host}:{port} successful")
                print(f"Connection to {host}:{port} successful")
            else:
                logger.error(f"Cannot connect to {host}:{port} - error code {result}")
                print(f"Cannot connect to {host}:{port} - error code {result}")
                
            sock.close()
            
        except Exception as e:
            logger.error(f"Error checking mail server connectivity: {str(e)}")
            print(f"Error checking mail server connectivity: {str(e)}")
    
    @staticmethod
    def _get_alternative_connection():
        """
        Get an alternative email connection with different settings.
        This tries a different approach if the standard one fails.
        """
        # Try with explicit SSL settings
        if settings.EMAIL_PORT == 465:
            use_ssl = True
            use_tls = False
        else:
            use_ssl = False
            use_tls = settings.EMAIL_PORT == 587
            
        connection = get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=30  # Longer timeout
        )
        
        return connection