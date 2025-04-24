# 🚀 WhatsApp Integration in Django

## 📌 Overview
This document outlines the step-by-step process of integrating WhatsApp messaging in a Django application. It includes webhook setup, message handling, token management, and sending messages.

---

## 🎯 **1. Webhook Setup and Verification**
- **Function:** `whatsapp_webhook(request)`
- **Purpose:** Verify webhook and handle incoming messages.
- **Logic:**
  - If `GET`: Verify the webhook using `hub.mode` and `hub.verify_token`.
  - If `POST`: Process incoming messages.
  - Log errors if verification fails.

---

## 📥 **2. Handle Incoming Messages**
- **Function:** `handle_incoming_messages(request)`
- **Purpose:** Process messages received via WhatsApp.
- **Logic:**
  - Parse request body JSON.
  - Extract sender ID (`wa_id`), message type (`text`, `image`, `video`, `document`, etc.), and content.
  - Create/update **Contact** model.
  - If media:
    - Extract media ID.
    - Retrieve media URL using `get_media_url_from_whatsapp(media_id)`.
    - Download and save media using `download_media()`.
  - Save message in `WhatsAppMessage` with `status="received"`.

✅ **Outcome:** Messages (and media, if applicable) are saved to the database.

---

## 🔐 **3. Token Handling**
- **Functions:**  
  - `get_access_token(org_id)`
  - `refresh_access_token(org_id)`
  - `generate_long_lived_token_view(request)`

- **Purpose:** Ensure valid access tokens for API calls.
- **Logic:**
  - `get_access_token()`: Retrieves stored access token.
  - If expired (`401 Unauthorized`):
    - `refresh_access_token()`: Requests a new token.
    - If refresh fails, log error and halt messaging.
  - `generate_long_lived_token_view()`: Exchanges a short-lived token for a long-lived token.

✅ **Outcome:** Always have a valid access token ready for API calls.

---

## 📤 **4. Send Outgoing Messages**
- **Function:** `send_message(request)`
- **Helper Function:** `send_whatsapp_message(access_token, recipient, message_type, content, caption, media_url)`
- **Purpose:** Deliver messages via WhatsApp API.
- **Logic:**
  - Extract recipient, message type, content, media (if applicable).
  - Validate recipient.
  - Get access token.
  - Prepare message payload.
  - Make a `POST` request to WhatsApp API.
  - Handle errors (`401 Unauthorized` → Refresh token and retry).
  - Save message in `WhatsAppMessage` (`status="sent"` or `"failed"`).
  - Save media in `WhatsAppMedia` (if applicable).

✅ **Outcome:** Message is sent (or logs failure if unsuccessful).

---

## 🔁 **5. Auto-Send Messages on Creation**
- **Signal Function:** `send_whatsapp_message_on_create(sender, instance, created, **kwargs)`
- **Purpose:** Automatically trigger WhatsApp messages.
- **Logic:**
  - If a new `WhatsAppMessage` instance is created and has a recipient:
    - Fetch access token.
    - Call `send_whatsapp_message()`.
    - Log the response.

✅ **Outcome:** Messages are automatically sent when created.

---

## 🔍 **6. Data Views & Filters**
- **API Views:**
  - `IncomingMessageList`: Lists incoming messages.
  - `OutgoingMessageList`: Lists outgoing messages.
  - `WhatsAppMessageList`: Lists all messages.
  - `WhatsAppMediaList`: Lists saved media files.
  - `ContactList`: Lists WhatsApp contacts.

- **Purpose:** Provide API access to stored WhatsApp messages, media, and contacts.

✅ **Outcome:** Messages, media, and contacts can be queried easily.

---

## 🔥 **7. Error Handling & Retries**
- **Purpose:** Ensure system resilience.
- **Logic:**
  - **For sending messages:**
    - `401 Unauthorized` → Auto-refresh token and retry.
    - Timeout or network errors → Implement retry logic with exponential backoff.
  - **For webhook failures:** Log payload for later retry.
  - Log all errors for debugging.

✅ **Outcome:** System handles temporary failures gracefully.

---

## 🏁 **Final Outcome**
By implementing these steps, the system is capable of:
- ✅ Webhook verification.
- ✅ Contact and media handling.
- ✅ Token refresh and long-lived token management.
- ✅ Manual and automatic message sending.
- ✅ API access for stored messages.
- ✅ Robust error handling and retries.

---

## 🔥 **Future Enhancements**
- **Message Templates:** Predefined replies (e.g., OTPs, confirmations).
- **Read Receipts:** Track when a user reads messages.
- **Bulk Messaging:** Send messages to multiple contacts with rate limiting.
- **Chatbot Integration:** Automate replies for common queries.

🚀 **Next Steps:** Implement retries, optimize database queries, or add chatbot support.

