import logging
from datetime import datetime, timedelta, timezone
import requests
from cfcbe.settings import WHATSAPP_API_URL, WHATSAPP_CLIENT_ID, WHATSAPP_CLIENT_SECRET
from whatsapp.models import WhatsAppCredential

logger = logging.getLogger(__name__)

# Ensure that the datetime object is aware (with timezone info)
def ensure_aware_datetime(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)  # Convert naive datetime to aware datetime in UTC
    return dt
import requests
import requests

def check_token_validity(access_token):
    """
    Use Facebook's API to check if the access token is valid and fetch expiry info.
    """
    url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={access_token}"
    response = requests.get(url)
    
    # Print out the full response for debugging purposes
    print(f"Response from checking token: {response}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            return data["data"]
        else:
            print("Error in response data:", data)
            return None
    else:
        print(f"Error response {response.status_code}: {response.text}")
        return None

def is_long_term_token(token_info):
    """
    Check if the token is long-term by comparing the expiry timestamp.
    Typically long-term tokens are valid for ~60 days.
    """
    expiry_time = datetime.utcfromtimestamp(token_info["expires_at"])
    current_time = datetime.utcnow()
    # Check if the expiry time is within ~60 days, indicating a long-term token
    if expiry_time - current_time > timedelta(days=50):
        return True  # Long-term token
    else:
        return False  # Short-term token
def get_access_token(org_id):
    """
    Retrieve the access token for the given organization. If expired or short-term, refresh it.
    """
    creds = WhatsAppCredential.objects.filter(organization_id=org_id).first()

    if not creds:
        logger.error(f"No credentials found for org {org_id}.")
        return None
    
    # Ensure token_expiry is aware datetime
    token_expiry = ensure_aware_datetime(creds.token_expiry)

    # Ensure current time is aware datetime
    current_time = datetime.now(timezone.utc)

    # Check if the token has expired
    if token_expiry < current_time:
        logger.warning(f"Access token for org {org_id} expired. Refreshing token...")
        # Token is expired, so refresh it
        new_token = refresh_access_token(org_id)
        print("🔑 New token:", new_token)
        
        if new_token:
            # Update the access token with the new one
            creds.access_token = new_token
            creds.token_expiry = datetime.now(timezone.utc) + timedelta(days=60)  # Set new expiry date (60 days)
            creds.save()  # Save the updated WhatsAppCredential in the database
            logger.info(f"Updated access token for org {org_id}.")
            return new_token
        else:
            logger.error(f"Failed to refresh the access token for org {org_id}. Using the default token.")
            return get_default_token()  # If refresh fails, fall back to default token

    else:
        # Token is not expired yet, but we need to check its validity
        token_info = check_token_validity(creds.access_token)

        if token_info and "data" in token_info and token_info["data"].get("is_valid"):
            # If the token is still valid, use the stored one
            logger.info(f"Using stored access token for org {org_id}.")
            print("🔑 Token info:", token_info)
            return creds.access_token
        else:
            logger.info(f"Short-term token or invalid token detected for org {org_id}, refreshing token...")
            return refresh_access_token(org_id)



import logging
from datetime import datetime, timedelta
import requests
from cfcbe.settings import WHATSAPP_ACCESS_TOKEN, WHATSAPP_CLIENT_ID, WHATSAPP_CLIENT_SECRET
from whatsapp.models import WhatsAppCredential

logger = logging.getLogger(__name__)

def refresh_access_token(org_id):
    """
    Refresh the access token using the refresh token, or use the default token if refresh fails.
    """
    
    print("Assigning Whatsapp Credetials to cred")
    creds = WhatsAppCredential.objects.filter(organization_id=org_id).first()

    if not creds:
        logger.error(f"No credentials found for org {org_id}.")
        return None

    # Exchange the short-lived token for a long-lived one
    exchange_url = f"https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={WHATSAPP_CLIENT_ID}&client_secret={WHATSAPP_CLIENT_SECRET}&fb_exchange_token={creds.access_token}"

    try:
        response = requests.get(exchange_url)
        response_data = response.json()

        if response.status_code != 200 or "access_token" not in response_data:
            logger.error(f"Failed to refresh access token for org {org_id}: {response_data}")
            # If refresh fails, update creds with default token and return it
            creds.access_token = WHATSAPP_ACCESS_TOKEN  # Update with the default token from settings
            creds.token_expiry = datetime.now() + timedelta(days=60)  # Set expiry for 60 days
            creds.save()  # Save the updated credentials
            logger.info(f"Access token refreshed with default token for org {org_id}.")
            return WHATSAPP_ACCESS_TOKEN  # Return the default token
        else:
            # If successful, update the credentials
            new_access_token = response_data["access_token"]
            creds.access_token = new_access_token  # Update with the new token
            creds.token_expiry = datetime.now() + timedelta(days=60)  # Set expiry 60 days from now
            creds.save()  # Save the updated credentials

            logger.info(f"Access token refreshed successfully for org {org_id}.")
            return new_access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while refreshing access token for org {org_id}: {str(e)}")
        # If there's an exception, update creds with default token and return it
        creds.access_token = WHATSAPP_ACCESS_TOKEN  # Update with the default token from settings
        creds.token_expiry = datetime.now() + timedelta(days=60)  # Set expiry for 60 days
        creds.save()  # Save the updated credentials
        return WHATSAPP_ACCESS_TOKEN  # Return the default token
    except Exception as e:
        logger.error(f"Unexpected error while refreshing access token for org {org_id}: {str(e)}")
        # If there's an unexpected error, update creds with default token and return it
        creds.access_token = WHATSAPP_ACCESS_TOKEN  # Update with the default token from settings
        creds.token_expiry = datetime.now() + timedelta(days=60)  # Set expiry for 60 days
        creds.save()  # Save the updated credentials
        return WHATSAPP_ACCESS_TOKEN  # Return the default token


def get_default_token():
    """
    Retrieve the default access token defined in settings.py.
    """
    logger.info("Using default access token from settings.py.")
    return WHATSAPP_API_URL  # Make sure to return the correct value here, depending on your settings
