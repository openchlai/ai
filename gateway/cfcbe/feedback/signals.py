import json
import logging
import base64
import requests
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Notification
import time

API_URL = "https://demo-openchs.bitz-itc.com/helpline/api/cases/"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.BEARER_TOKEN}",
}

@receiver(post_save, sender=Complaint)
def create_notification(sender, instance, created, **kwargs):
    if created:
        print(f"Signal triggered for complaint: {instance.complaint_id}, created: {created}")
        transaction.on_commit(lambda: generate_notification(instance))

def generate_notification(instance):
    """
    Generates a notification for a given complaint instance and sends the data to an external API.

    This function refreshes the instance from the database, constructs a payload with the complaint
    details, and sends it to a predefined API endpoint. It also creates a notification record in the
    local database.

    Parameters:
    instance (Complaint): The complaint instance for which the notification is generated. It contains
                          details about the victim and perpetrator involved in the complaint.

    Returns:
    None: This function does not return any value. It performs operations such as sending data to an
          API and creating a notification record in the database.
    """
    instance.refresh_from_db()

    victim = instance.victim
    perpetrator = instance.perpetrator
    
    # Generate timestamp in Unix format with milliseconds
    current_time = time.time()
    unix_timestamp = f"{current_time:.3f}"
    
    # Create a unique ID based on the session ID
    source_uid = f"walkin-100-{unix_timestamp.replace('.', '')}"
    
    # Prepare client (victim) data
    client_data = {
        "fname": victim.name if victim and victim.name else "",
        "age_t": "0",
        "age": str(victim.age) if victim and victim.age else "",
        "dob": "",  # You may calculate this from age if needed
        "age_group_id": "361953",  # Default value - adjust as needed
        "location_id": "258783",  # Default value - adjust as needed
        "sex_id": "",
        "landmark": "",
        "nationality_id": "",
        "national_id_type_id": "",
        "national_id": "",
        "lang_id": "",
        "tribe_id": "",
        "phone": "",
        "phone2": "",
        "email": "",
        ".id": "86164"  # Default value or generate if needed
    }
    
    # Create gender mapping
    gender_mapping = {
        "male": "121",  # Assuming these are the correct IDs
        "female": "122",
        # Add other mappings as needed
    }
    
    # Prepare perpetrator data
    perpetrator_data = {
        "fname": perpetrator.name if perpetrator and perpetrator.name else "",
        "age_t": "0",
        "age": str(perpetrator.age) if perpetrator and perpetrator.age else "",
        "dob": "",  # You may calculate this from age if needed
        "age_group_id": "361955",  # Default value - adjust as needed
        "age_group": "31-45",  # Default or calculate based on age
        "location_id": "",
        "sex_id": gender_mapping.get(perpetrator.gender.lower() if perpetrator and perpetrator.gender else "", ""),
        "sex": f"^{perpetrator.gender.capitalize()}" if perpetrator and perpetrator.gender else "",
        "landmark": "",
        "nationality_id": "",
        "national_id_type_id": "",
        "national_id": "",
        "lang_id": "",
        "tribe_id": "",
        "phone": "",
        "phone2": "",
        "email": "",
        "relationship_id": "",
        "shareshome_id": "",
        "health_id": "",
        "employment_id": "",
        "marital_id": "",
        "guardian_fullname": "",
        "notes": "",
        ".id": ""
    }

    # Construct new payload format
    new_payload = {
        "src": "walkin",
        "src_uid": source_uid,
        "src_address": "",
        "src_uid2": f"{source_uid}-2",
        "src_usr": "100",
        "src_vector": "2",
        "src_callid": source_uid,
        "src_ts": unix_timestamp,
        
        "reporter": client_data,
        
        "clients_case": [
            client_data
        ],
        
        "perpetrators_case": [
            perpetrator_data
        ],
        
        "attachments_case": [],
        
        "services": [],
        
        "knowabout116_id": "",
        
        "case_category_id": "362484",  # Default or map from instance.case_category
        
        "narrative": instance.complaint_text if instance.complaint_text else "---",
        
        "plan": "---",
        
        "justice_id": "",
        
        "assessment_id": "",
        
        "priority": "1",
        
        "status": "1",
        
        "escalated_to_id": "0"
    }

    print(f"Sending new payload: {json.dumps(new_payload, indent=2)}")

    # Create Notification
    message = (
        f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} "
        f"in the category {instance.case_category}."
    )
    Notification.objects.create(complaint=instance, message=message)

    # Send to API
    try:
        response = requests.post(API_URL, headers=HEADERS, json=new_payload)
        print(f"API Response: {response.status_code}, {response.text}")

        if response.status_code == 201:
            response_data = response.json()
            # Update logic to extract message_id based on the new response format
            message_id = response_data.get("id", "")  # Adjust based on actual API response
            if message_id:
                instance.message_id_ref = message_id
                instance.save(update_fields=["message_id_ref"])
                logging.info(f"message_id_ref saved: {message_id}")
            else:
                logging.error("message_id not found in API response.")
        else:
            logging.error(f"API call failed: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send complaint to API: {e}")
    victim = instance.victim
    perpetrator = instance.perpetrator
    
    # Generate timestamp in Unix format with milliseconds
    current_time = time.time()
    unix_timestamp = f"{current_time:.3f}"
    
    # Create a unique ID based on the session ID
    source_uid = f"walkin-100-{unix_timestamp.replace('.', '')}"
    
    # Prepare client (victim) data
    client_data = {
        "fname": victim.name if victim and victim.name else "",
        "age_t": "0",
        "age": str(victim.age) if victim and victim.age else "",
        "dob": "",  # You may calculate this from age if needed
        "age_group_id": "361953",  # Default value - adjust as needed
        "location_id": "258783",  # Default value - adjust as needed
        "sex_id": "",
        "landmark": "",
        "nationality_id": "",
        "national_id_type_id": "",
        "national_id": "",
        "lang_id": "",
        "tribe_id": "",
        "phone": "",
        "phone2": "",
        "email": "",
        ".id": "86164"  # Default value or generate if needed
    }
    
    # Create gender mapping
    gender_mapping = {
        "male": "121",  # Assuming these are the correct IDs
        "female": "122",
        # Add other mappings as needed
    }
    
    # Prepare perpetrator data
    perpetrator_data = {
        "fname": perpetrator.name if perpetrator and perpetrator.name else "",
        "age_t": "0",
        "age": str(perpetrator.age) if perpetrator and perpetrator.age else "",
        "dob": "",  # You may calculate this from age if needed
        "age_group_id": "361955",  # Default value - adjust as needed
        "age_group": "31-45",  # Default or calculate based on age
        "location_id": "",
        "sex_id": gender_mapping.get(perpetrator.gender.lower() if perpetrator and perpetrator.gender else "", ""),
        "sex": f"^{perpetrator.gender.capitalize()}" if perpetrator and perpetrator.gender else "",
        "landmark": "",
        "nationality_id": "",
        "national_id_type_id": "",
        "national_id": "",
        "lang_id": "",
        "tribe_id": "",
        "phone": "",
        "phone2": "",
        "email": "",
        "relationship_id": "",
        "shareshome_id": "",
        "health_id": "",
        "employment_id": "",
        "marital_id": "",
        "guardian_fullname": "",
        "notes": "",
        ".id": ""
    }

    # Construct new payload format
    new_payload = {
        "src": "walkin",
        "src_uid": source_uid,
        "src_address": "",
        "src_uid2": f"{source_uid}-2",
        "src_usr": "100",
        "src_vector": "2",
        "src_callid": source_uid,
        "src_ts": unix_timestamp,
        
        "reporter": client_data,
        
        "clients_case": [
            client_data
        ],
        
        "perpetrators_case": [
            perpetrator_data
        ],
        
        "attachments_case": [],
        
        "services": [],
        
        "knowabout116_id": "",
        
        "case_category_id": "362484",  # Default or map from instance.case_category
        
        "narrative": instance.complaint_text if instance.complaint_text else "---",
        
        "plan": "---",
        
        "justice_id": "",
        
        "assessment_id": "",
        
        "priority": "1",
        
        "status": "1",
        
        "escalated_to_id": "0"
    }

    print(f"Sending new payload: {json.dumps(new_payload, indent=2)}")

    # Create Notification
    message = (
        f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} "
        f"in the category {instance.case_category}."
    )
    Notification.objects.create(complaint=instance, message=message)

    # Send to API
    try:
        response = requests.post(API_URL, headers=HEADERS, json=new_payload)
        print(f"API Response: {response.status_code}, {response.text}")

        if response.status_code == 201:
            response_data = response.json()
            # Update logic to extract message_id based on the new response format
            message_id = response_data.get("id", "")  # Adjust based on actual API response
            if message_id:
                instance.message_id_ref = message_id
                instance.save(update_fields=["message_id_ref"])
                logging.info(f"message_id_ref saved: {message_id}")
            else:
                logging.error("message_id not found in API response.")
        else:
            logging.error(f"API call failed: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send complaint to API: {e}")