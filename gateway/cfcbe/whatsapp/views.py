# -----------------------------------------------
# 📌 IMPORTS AND CONFIGURATION
# -----------------------------------------------

import json
import logging
import requests
from datetime import datetime, timezone, timedelta

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models.signals import post_save
from django.dispatch import receiver

from cfcbe.settings import WHATSAPP_API_URL, WHATSAPP_PHONE_NUMBER_ID
from whatsapp.models import (
    WhatsAppCredential,
    Organization,
    Contact,
    WhatsAppMessage,
    WhatsAppMedia,
)
from .serializers import (
    WhatsAppMessageSerializer,
    WhatsAppMediaSerializer,
    ContactSerializer,
)
from .utils import (
    download_media,
    get_media_url_from_whatsapp,
    setup,
    # refresh_access_token,
)

# ✅ Setup Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------------------------------
# 📌 1. WEBHOOK VERIFICATION & MESSAGE HANDLING
# -----------------------------------------------

@csrf_exempt
def whatsapp_webhook(request):
    """
    Handles WhatsApp webhook requests.
    Supports:
    - GET (for webhook verification)
    - POST (for incoming message handling)
    """
    if request.method == "GET":
        return handle_verification_request(request)
    elif request.method == "POST":
        return handle_incoming_messages(request)
    else:
        logger.warning(f"Received invalid HTTP method: {request.method}")
        return HttpResponseBadRequest("Invalid HTTP method. Use GET or POST.")


def handle_verification_request(request):
    """
    Handles WhatsApp webhook verification.
    Returns the challenge response if the verification token is correct.
    """
    hub_mode = request.GET.get("hub.mode")
    hub_challenge = request.GET.get("hub.challenge")
    hub_verify_token = request.GET.get("hub.verify_token")

    logger.debug(
        f"Verification request received: mode={hub_mode}, token={hub_verify_token}"
    )

    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFICATION_TOKEN:
        logger.info("Webhook verified successfully.")
        return JsonResponse(int(hub_challenge), safe=False, status=200)

    return HttpResponseBadRequest("Verification failed. Invalid token.")


def handle_incoming_messages(request):
    """
    Handles incoming WhatsApp messages, extracts content, 
    and saves messages (and media if applicable) to the database.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.info(f"Incoming payload: {json.dumps(data, indent=4)}")

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                contacts = value.get("contacts", [])
                messages = value.get("messages", [])

                # Process each message
                for message in messages:
                    sender_wa_id = message.get("from")
                    message_type = message.get("type")
                    content = message.get("text", {}).get("body") if message_type == "text" else None
                    caption = message.get("caption", None)

                    # Extract contact name if available
                    contact_name = contacts[0].get("profile", {}).get("name") if contacts else None

                    # Ensure we have a sender ID
                    if not sender_wa_id:
                        logger.error("Message missing sender. Skipping.")
                        continue

                    # Create or get the contact
                    contact, _ = Contact.objects.get_or_create(
                        wa_id=sender_wa_id, defaults={"name": contact_name}
                    )

                    media_instance = handle_incoming_media(message, message_type)

                    # Save message to the database
                    whatsapp_message = WhatsAppMessage.objects.create(
                        sender=contact,
                        recipient=None,
                        message_type=message_type,
                        content=content,
                        caption=caption,
                        media=media_instance,
                        status="received",
                    )

                    logger.info(f"Saved incoming message: {whatsapp_message}")

        return JsonResponse({"status": "Success", "message": "Messages saved successfully"})

    except Exception as e:
        logger.error(f"Error handling incoming message: {str(e)}")
        return HttpResponseBadRequest(f"Error: {str(e)}")


def handle_incoming_media(message, message_type):
    """
    Handles media extraction from an incoming message.
    Downloads and saves media to WhatsAppMedia model.
    """
    if message_type in ["image", "video", "audio", "document"]:
        media_id = message.get(message_type, {}).get("id")
        mime_type = message.get(message_type, {}).get("mime_type")

        if media_id:
            media_url = get_media_url_from_whatsapp(media_id)
            if media_url:
                media_file = download_media(media_url, message_type, media_id)
                if media_file:
                    media_instance = WhatsAppMedia.objects.create(
                        media_type=message_type,
                        media_url=media_url,
                        media_mime_type=mime_type,
                    )
                    media_instance.media_file.save(media_file.name, media_file, save=True)
                    logger.info(f"Saved media file: {media_file.name}")
                    return media_instance

    return None


# -----------------------------------------------
# 📌 2. OUTGOING MESSAGE HANDLING
# -----------------------------------------------

@csrf_exempt
def send_message(request):
    """
    Handles sending WhatsApp messages and logs them to the database.
    Supports text and media messages.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logger.info(f"Outgoing message request: {json.dumps(data, indent=4)}")

            # Extract data from the request payload
            recipient_wa_id = data.get("recipient")
            message_type = data.get("message_type", "text")
            content = data.get("content", "")
            caption = data.get("caption", None)
            media_url = data.get("media_url", None)
            mime_type = data.get("mime_type", None)

            # Ensure recipient exists
            if not recipient_wa_id:
                logger.error("Recipient is missing. Cannot send message.")
                return JsonResponse({"status": "Error", "message": "Recipient is required"}, status=400)

            # Fetch access token and send message
            access_token = get_access_token(1)
            print(f"Access token in the send message: {access_token}")
            response = send_whatsapp_message(access_token, recipient_wa_id, message_type, content, caption, media_url)

            # Create or fetch recipient contact
            recipient, _ = Contact.objects.get_or_create(wa_id=recipient_wa_id)

            # Save the outgoing message in the database
            WhatsAppMessage.objects.create(
                sender=None,
                recipient=recipient,
                message_type=message_type,
                content=content,
                caption=caption,
                status="sent" if response.get("success") else "failed",
            )

            logger.info("Outgoing message saved successfully.")
            return JsonResponse({"status": "Success", "message": "Message sent and logged"})

        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=400)

# views.py

import json
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from cfcbe.settings import WHATSAPP_CLIENT_ID, WHATSAPP_CLIENT_SECRET
from whatsapp.models import WhatsAppCredential, Organization

logger = logging.getLogger(__name__)

@csrf_exempt
def generate_long_lived_token_view(request):
    """API view to accept a short-lived token, exchange it for a long-lived token,
    and save it in the WhatsAppCredential model."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    try:
        data = json.loads(request.body)
        short_lived_token = data.get("short_lived_token")
        org_id = data.get("org_id")

        if not short_lived_token or not org_id:
            return JsonResponse({"error": "short_lived_token and org_id are required."}, status=400)

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return JsonResponse({"error": "Organization not found."}, status=404)

        # Exchange the short-lived token for a long-lived token
        exchange_url = (
            f"https://graph.facebook.com/v19.0/oauth/access_token"
            f"?grant_type=fb_exchange_token"
            f"&client_id={WHATSAPP_CLIENT_ID}"
            f"&client_secret={WHATSAPP_CLIENT_SECRET}"
            f"&fb_exchange_token={short_lived_token}"
        )

        response = requests.get(exchange_url)
        response_data = response.json()

        if response.status_code != 200 or "access_token" not in response_data:
            error_message = response_data.get("error", {}).get("message", "Unknown error")
            logger.error(f"❌ Failed to generate long-lived token: {error_message}")
            return JsonResponse({"error": error_message}, status=400)

        long_lived_token = response_data["access_token"]

        creds, created = WhatsAppCredential.objects.update_or_create(
            organization=organization,
            defaults={
                "access_token": long_lived_token,
                "token_expiry": datetime.now(timezone.utc) + timedelta(days=60),
            }
        )

        logger.info(f"✅ Successfully stored long-lived token for org {org_id}.")

        return JsonResponse({
            "message": "Long-lived token generated successfully.",
            "long_lived_token": long_lived_token,
            "token_expiry": creds.token_expiry.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return JsonResponse({"error": "Internal server error."}, status=500)


# views.py
from .TokenManager import get_access_token
import requests
import logging
import requests

def send_whatsapp_message(access_token, recipient, message_type, content=None, caption=None, media_url=None):
    """Sends a message via the WhatsApp API."""
    endpoint_url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Log the header to verify it's correct
    print("Authorization Header:", headers["Authorization"])

    request_body = {
        "messaging_product": "whatsapp",
        "to": recipient,
    }

    if message_type == "text":
        request_body["type"] = "text"
        request_body["text"] = {"body": content}
    elif message_type in ["image", "video", "audio", "document"]:
        request_body["type"] = message_type
        request_body[message_type] = {"link": media_url}
        if caption:
            request_body[message_type]["caption"] = caption

    try:
        # Log request data for debugging
        print("Request Headers:", headers)
        print("Request Body:", request_body)

        response = requests.post(endpoint_url, json=request_body, headers=headers)

        # Log the response for debugging
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)

        response.raise_for_status()

        return {"success": True, "response": response.json()}
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return {"success": False, "error": str(e)}


# -----------------------------------------------
# 📌 3. API VIEWS
# -----------------------------------------------

class IncomingMessageList(generics.ListAPIView):
    """API endpoint for viewing incoming messages."""
    queryset = WhatsAppMessage.objects.filter(recipient=None)
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["sender", "message_type", "status"]


class OutgoingMessageList(generics.ListAPIView):
    """API endpoint for viewing outgoing messages."""
    queryset = WhatsAppMessage.objects.filter(sender=None)
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["recipient", "message_type", "status"]


class ContactList(generics.ListCreateAPIView):
    """API endpoint for managing contacts."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["wa_id"]

class WhatsAppMessageList(generics.ListCreateAPIView):
    queryset = WhatsAppMessage.objects.all()
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["sender", "recipient", "message_type", "status"]
class WhatsAppMediaList(generics.ListCreateAPIView):
    queryset = WhatsAppMedia.objects.all()
    serializer_class = WhatsAppMediaSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["media_type"]