import requests
from django.conf import settings

def send_whatsapp_message(phone_number, message):
    """
    Sends a WhatsApp message to a specific phone number.
    
    :param phone_number: The recipient's phone number (e.g., "+1234567890").
    :param message: The text message to send.
    :return: JSON response from the API.
    """
    url = f"{settings.WHATSAPP_API_URL}/v1/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
