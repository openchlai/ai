import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from .models import Email
import requests
import logging
import json
import base64


def fetch_emails(email_address, email_password, imap_host="mail.bitz-itc.com"):
    try:
        # Connect to the IMAP server
        server = imaplib.IMAP4_SSL(imap_host)
        server.login(email_address, email_password)
        server.select("inbox")

        # Search for all emails
        status, messages = server.search(None, "ALL")
        email_ids = messages[0].split()

        for e_id in email_ids:
            # Fetch the email
            status, msg_data = server.fetch(e_id, "(RFC822)")
            if status != "OK":
                continue  # Skip if fetching fails

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode email headers
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            sender, encoding = decode_header(msg["From"])[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or "utf-8")

            recipient = email_address  # Emails fetched are for this account

            # Extract the email date
            date_header = msg["Date"]
            received_date = None
            if date_header:
                try:
                    received_date = parsedate_to_datetime(date_header)
                except Exception as e:
                    print(f"Error parsing email date: {e}")
                    continue  # Skip this email if the date is invalid

            # Extract email body
            body = extract_email_body(msg)

            # Save to the database if it doesn't already exist
            if not Email.objects.filter(
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                received_date=received_date,
                raw_message=raw_email,
            ).exists():
                Email.objects.create(
                    sender=sender,
                    recipient=recipient,
                    subject=subject,
                    body=body,
                    received_date=received_date,
                    raw_message=raw_email,
                )

        # Close the server connection
        server.close()
        server.logout()

    except Exception as e:
        print(f"An error occurred: {e}")

def extract_email_body(msg):
    """
    Extracts the email body, ignoring non-text parts like images.
    """
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            # Check for text content
            if part.get_content_type() in ["text/plain", "text/html"]:
                try:
                    # Decode the payload to a string
                    body += part.get_payload(decode=True).decode("utf-8", errors="replace")
                except Exception as e:
                    logging.error(f"Failed to decode part: {e}")
    else:
        # For non-multipart messages
        try:
            if msg.get_content_type() in ["text/plain", "text/html"]:
                body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception as e:
            logging.error(f"Failed to decode body: {e}")
    return body


def forward_email_to_main_system(email):
    """
    Sends the email details to the main system via a POST request.
    :param email: Email object to be forwarded
    """
    # API configuration
    api_url = "https://demo-openchs.bitz-itc.com/helpline/api/msg/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sci9de994iddqlmj8fv7r1js74",
    }

    # Sanitize and construct payload
    # def sanitize_text(text):
    #     if text:
    #         return text.encode("utf-8", errors="replace").decode("utf-8")
    #     return text

    # payload = {
    #     "sender": sanitize_text(email.sender),
    #     "recipient": sanitize_text(email.recipient),
    #     "subject": sanitize_text(email.subject),
    #     "body": sanitize_text(email.body),
    #     "received_date": email.received_date.isoformat(),
    #     "is_read": email.is_read,
    # }

    # logging.info(f"The email is: {email}")

    try:
        # Base64 encoding (Fix: Remove `.encode("utf-8")`)
        logging.info(f"Payload: {email.raw_message}")
        encoded_data = base64.b64encode(email.raw_message).decode("utf-8")  # Fix applied

        # Construct complaint payload
        complaint = {
            "channel": "email",
            "timestamp": email.received_date.isoformat(),
            "session_id": email.id,
            "message_id": str(email.id),
            "from": email.sender,
            "message": encoded_data,  # Correctly Base64 encoded email
            "mime": "text/plain",
        }

        # Send POST request
        response = requests.post(api_url, json=complaint, headers=headers)
        logging.info(f"API Response: {response.status_code}, {response.text}")
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e} - Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to forward email: {email.subject}. Error: {e}")
