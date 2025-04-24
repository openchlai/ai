from typing import List, Dict, Any, Optional
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
import uuid
import time
import logging
from datetime import datetime
import requests
from datetime import datetime
import logging
import requests
import csv
from django.http import JsonResponse, HttpResponse


from platform_adapters.base_adapter import BaseAdapter
from shared.models.standard_message import StandardMessage


logger = logging.getLogger(__name__)

class WebformAdapter(BaseAdapter):
    """
    Adapter for handling webform submissions as a platform in the gateway.
    
    This adapter processes web form submissions and converts them to
    the standardized message format used by the gateway.
    """
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle platform verification challenges.
        
        Webforms don't typically need verification challenges,
        so this method returns None.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            None as webforms don't use verification challenges
        """
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate the authenticity of the incoming request.
        
        For webforms, we trust the request as it comes through our server.
        Basic validation can be done to ensure required fields are present.
        
        Args:
            request: The request data
            
        Returns:
            True if request is valid, False otherwise
        """
        # For webforms, ensure required fields are present
        if isinstance(request, dict):
            # Check for complaint_text as a required field
            if 'complaint_text' not in request:
                logger.warning("Webform submission missing required field: complaint_text")
                return False
            return True
        return False
    
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Convert form data to a list of standardized messages.
        
        Args:
            request: Form submission data or HTTP request
            
        Returns:
            List containing one standardized message dict
        """
        # If request is a dictionary, it's already parsed form data
        if isinstance(request, dict):
            data = request
        # If request is an HttpRequest, try to parse the body
        elif isinstance(request, HttpRequest):
            try:
                if request.body:
                    data = json.loads(request.body)
                else:
                    data = request.POST.dict()
            except json.JSONDecodeError:
                data = request.POST.dict()
        else:
            # Fallback - try to convert to dict
            data = dict(request)
        
        # Create a StandardMessage from the form data
        standard_message = self._form_data_to_standard_message(data)
        
        # Return as a list of one message dict
        return [standard_message.to_dict()]
    
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a webform user.
        
        For webforms, this might create a notification that
        the user can access when checking their submission status.
        
        Args:
            recipient_id: Typically the session_id
            message_content: Content to send
            
        Returns:
            Status of the notification creation
        """
        try:
            # For webforms, we create a notification
            # Note: This logic can be updated to fit how you want to notify users
            from webhook_handler.models import Notification, Complaint
            
            # Try to find the complaint associated with the session_id
            try:
                complaint = Complaint.objects.get(session_id=recipient_id)
                
                # Create a notification for the complaint
                notification = Notification.objects.create(
                    complaint=complaint,
                    message=message_content.get('content', 'Update on your complaint'),
                    is_read=False
                )
                
                return {
                    'status': 'success',
                    'notification_id': str(notification.notification_id),
                    'message': 'Notification created successfully'
                }
            except Complaint.DoesNotExist:
                return {
                    'status': 'error',
                    'error': f'No complaint found with session_id: {recipient_id}'
                }
            
        except Exception as e:
            logger.error(f"Error sending webform notification: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response for a webform submission.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            JSON response with status information
        """
        return JsonResponse({
            'status': 'success',
            'message': 'Form processed successfully',
            'responses': responses
        })
    
    def _form_data_to_standard_message(self, data: Dict[str, Any]) -> StandardMessage:
        """
        Convert form submission data to a StandardMessage.
        
        Args:
            data: Form submission data
            
        Returns:
            StandardMessage: The form data in standardized format
        """
        # Generate unique IDs if not provided
        message_id = data.get('submission_id', str(uuid.uuid4()))
        sender_id = data.get('session_id', str(uuid.uuid4()))
        
        # Extract content
        content = data.get('complaint_text', '')
        
        # Extract victim and perpetrator data
        victim_data = data.get('victim', {})
        perpetrator_data = data.get('perpetrator', {})
        
        # Build metadata
        metadata = {
            'reporter_nickname': data.get('reporter_nickname'),
            'case_category': data.get('case_category'),
            'case_category_id': data.get('case_category_id', '362484'),  # Default ID if not provided
            'victim': victim_data,
            'perpetrator': perpetrator_data,
            'has_image': bool(data.get('complaint_image')),
            'has_audio': bool(data.get('complaint_audio')),
            'has_video': bool(data.get('complaint_video')),
        }
        
        # Determine message type based on content
        message_type = 'complaint'
        if data.get('complaint_image'):
            message_type = 'complaint_with_image'
        elif data.get('complaint_audio'):
            message_type = 'complaint_with_audio'
        elif data.get('complaint_video'):
            message_type = 'complaint_with_video'
        
        # Get media URL if available
        media_url = None
        if data.get('complaint_image'):
            media_url = data.get('complaint_image')
        elif data.get('complaint_audio'):
            media_url = data.get('complaint_audio')
        elif data.get('complaint_video'):
            media_url = data.get('complaint_video')
        
        # Create StandardMessage
        return StandardMessage(
            message_id=message_id,
            sender_id=sender_id,
            platform='webform',
            content=content,
            timestamp=time.time(),
            message_type=message_type,
            media_url=media_url,
            metadata=metadata
        )


    def create_from_complaint(self, complaint) -> StandardMessage:
        from webhook_handler.models import Complaint
        """
        Create a StandardMessage from a Complaint model instance.
        
        Args:
            complaint: A Complaint model instance
            
        Returns:
            StandardMessage in the gateway's standard format
        """
        # Convert victim to dict if exists
        victim_data = {}
        if complaint.victim:
            victim_data = {
                'name': complaint.victim.name,
                'age': complaint.victim.age,
                'gender': complaint.victim.gender,
                'additional_info': complaint.victim.additional_info
            }
        
        # Convert perpetrator to dict if exists
        perpetrator_data = {}
        if complaint.perpetrator:
            perpetrator_data = {
                'name': complaint.perpetrator.name,
                'age': complaint.perpetrator.age,
                'gender': complaint.perpetrator.gender,
                'additional_info': complaint.perpetrator.additional_info if hasattr(complaint.perpetrator, 'additional_info') else None
            }
        
        # Build metadata with complaint-specific information
        metadata = {
            'complaint_id': str(complaint.complaint_id),
            'reporter_nickname': complaint.reporter_nickname,
            'case_category': complaint.case_category,
            'case_category_id': "362484",  # Default ID or map from category
            'victim': victim_data,
            'perpetrator': perpetrator_data,
            'has_image': bool(complaint.complaint_image),
            'has_audio': bool(complaint.complaint_audio),
            'has_video': bool(complaint.complaint_video),
        }
        
        # Determine MIME type based on content
        content_type = 'application/json'
        
        # Get media URL if available
        media_url = None
        if complaint.complaint_image:
            try:
                media_url = complaint.complaint_image.url
                content_type = 'image/jpeg'  # Adjust as needed based on image type
            except:
                pass
        elif complaint.complaint_audio:
            try:
                media_url = complaint.complaint_audio.url
                content_type = 'audio/mpeg'  # Adjust as needed based on audio type
            except:
                pass
        elif complaint.complaint_video:
            try:
                media_url = complaint.complaint_video.url
                content_type = 'video/mp4'  # Adjust as needed based on video type
            except:
                pass
        
        # Generate a unique session ID if not available
        session_id = str(complaint.session_id or uuid.uuid4())
        
        # Create StandardMessage aligned with endpoint formats
        return StandardMessage(
            source="walkin",                            # Will map to 'src' in cases endpoint
            source_uid=f"walkin-100-{int(time.time())}",  # Will map to 'src_uid'
            source_address=session_id,  # Will map to 'src_address'
            message_id=str(complaint.complaint_id),     # Will map to 'src_callid'
            source_timestamp=complaint.created_at.timestamp(),  # Will map to 'src_ts'
            content=complaint.complaint_text or "",     # Will map to 'narrative'
            content_type=content_type,                 # MIME type for the content
            platform="webform",                        # Internal platform identifier
            media_url=media_url,                       # URL to any media content
            metadata=metadata                          # Platform-specific data
        )
    def __init__(self):
        """Initialize the WebForm Adapter."""
        self.config = self._get_config()

    def _get_config(self):
        """Get configuration from settings."""
        platform_configs = getattr(settings, 'PLATFORM_CONFIGS', {})
        return platform_configs.get('webform', {})
    
    def get_categories(self) -> Dict[str, Any]:
        """
        Fetch categories from the external API and format them for easy use.

        Returns:
            Dictionary containing categories with their IDs, names, and subcategories
        """
        try:
            # Get configuration
            auth_token = self.config.get('api_token')
            
            if not auth_token:
                logger.error("Missing API token")
                return {
                    'status': 'error',
                    'error': 'Missing API configuration'
                }
            
            # Prepare API URL
            url = "https://demo-openchs.bitz-itc.com/helpline/api/categories/362557"
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            logger.info(f"Fetching categories from {url}")
            response = requests.get(url, headers=headers)
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                # Extract main category and its subcategories
                categories = []
                if 'categories' in data:
                    for category in data['categories']:
                        category_info = {
                            'id': category[0],
                            'name': category[6],  # This is the category name
                            'subcategories': []
                        }
                        
                        # Check for subcategories
                        for subcategory in data.get('subcategories', []):
                            if subcategory[8] == category[0]:  # Match subcategory to parent category
                                subcategory_info = {
                                    'id': subcategory[0],
                                    'name': subcategory[5],  # This is the subcategory name
                                }
                                category_info['subcategories'].append(subcategory_info)
                        
                        categories.append(category_info)
                    
                return {
                    'status': 'success',
                    'categories': categories
                }
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {
                    'status': 'error',
                    'error': f"API error: {response.status_code}"
                }
            
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_subcategories(self, category_id: int) -> Dict[str, Any]:
        """
        Fetch subcategories for a specific category from the external API.

        Args:
            category_id (int): The ID of the category for which subcategories are fetched.

        Returns:
            dict: Dictionary containing subcategories with their IDs and names.
        """
        try:
            # Get API token from configuration
            auth_token = self.config.get('api_token')

            if not auth_token:
                logger.error("Missing API token")
                return {
                    'status': 'error',
                    'error': 'Missing API configuration'
                }

            # Construct dynamic API URL
            url = f"https://demo-openchs.bitz-itc.com/helpline/api/categories/{category_id}"

            # Request headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }

            # Fetch data from API
            logger.info(f"Fetching subcategories for category ID {category_id} from {url}")
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                # Extract subcategories
                subcategories = []
                if 'subcategories' in data:
                    for subcategory in data['subcategories']:
                        subcategory_info = {
                            'id': subcategory[0],
                            'name': subcategory[5],  # Subcategory name
                            'parent_id': subcategory[8],  # Parent category ID
                            'parent_name': subcategory[9]  # Parent category name
                        }
                        subcategories.append(subcategory_info)

                return {
                    'status': 'success',
                    'category_id': category_id,
                    'subcategories': subcategories
                }
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {
                    'status': 'error',
                    'error': f"API error: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Error fetching subcategories: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    def export_all_locations(self) -> dict:
        """
        Exports all locations from the system in a hierarchical structure.
        This function traverses the entire location hierarchy, starting from regions,
        and builds a complete tree of all locations with their IDs.
        
        Returns:
            dict: A dictionary containing the full location hierarchy with IDs
        """
        try:
            # Get API token from configuration
            auth_token = self.config.get('api_token')
            
            if not auth_token:
                logger.error("Missing API token")
                return {
                    'status': 'error',
                    'error': 'Missing API configuration'
                }
            
            # Base URL for the external API
            base_url = "https://demo-openchs.bitz-itc.com/helpline/api/categories/"
            
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Start with the top level (Locations)
            logger.info("Starting export of all locations")
            root_id = "88"  # Locations root ID
            
            # Function to recursively fetch all locations in the hierarchy
            def fetch_locations_recursively(location_id, current_path=None, depth=0):
                if current_path is None:
                    current_path = []
                
                # Create indentation for readable logs
                indent = "  " * depth
                
                # Log the start of fetching this location
                path_str = " -> ".join([item.get('name', 'Unknown') for item in current_path]) if current_path else "Root"
                logger.info(f"{indent}Fetching location ID: {location_id} (Path: {path_str})")
                
                # Fetch data for the current location
                url = f"{base_url}{location_id}"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"{indent}API error when fetching location {location_id}: {response.status_code}")
                    return None
                
                data = response.json()
                
                # Get the subcategories
                subcategories = data.get('subcategories', [])
                
                # Log the number of subcategories found
                logger.info(f"{indent}Found {len(subcategories)} subcategories for location ID: {location_id}")
                
                # If no subcategories, return an empty list
                if not subcategories:
                    logger.info(f"{indent}No subcategories found for location ID: {location_id} - this is a leaf node")
                    return []
                
                # Process each subcategory
                results = []
                for i, subcategory in enumerate(subcategories):
                    sub_id = subcategory[0]
                    sub_name = subcategory[5]
                    parent_id = subcategory[8] if len(subcategory) > 8 else None
                    full_path = subcategory[6] if len(subcategory) > 6 else None
                    
                    # Skip if we can't get the ID
                    if not sub_id:
                        logger.warning(f"{indent}Skipping subcategory at index {i} due to missing ID")
                        continue
                    
                    # Log the subcategory being processed
                    logger.info(f"{indent}Processing subcategory: {sub_name} (ID: {sub_id})")
                    if full_path:
                        logger.info(f"{indent}  Full path: {full_path}")
                    
                    # Determine the level based on the path or position
                    level_name = None
                    if full_path:
                        # Count the segments in the path (each level is separated by ^)
                        segments = full_path.split('^')
                        # Remove empty segments
                        segments = [s for s in segments if s]
                        level_pos = len(segments) - 1
                        
                        # Map position to level name
                        level_map = {
                            0: 'region',
                            1: 'district',
                            2: 'county',
                            3: 'subcounty',
                            4: 'parish',
                            5: 'village',
                            6: 'constituency'
                        }
                        level_name = level_map.get(level_pos, 'unknown')
                    
                    # Log the determined level
                    logger.info(f"{indent}  Level determined as: {level_name}")
                    
                    # Create the updated path for this subcategory
                    updated_path = current_path + [{'id': sub_id, 'name': sub_name}]
                    
                    # Log that we're about to recursively fetch children
                    logger.info(f"{indent}Starting recursive fetch for: {sub_name} (ID: {sub_id})")
                    
                    # Create location entry with children from recursive call
                    children = fetch_locations_recursively(sub_id, updated_path, depth + 1)
                    
                    location_entry = {
                        'id': sub_id,
                        'name': sub_name,
                        'level': level_name,
                        'parent_id': parent_id,
                        'full_path': full_path,
                        'children': children
                    }
                    
                    # Log the completion of this subcategory processing
                    child_count = len(children) if children else 0
                    logger.info(f"{indent}Completed processing {sub_name} (ID: {sub_id}) with {child_count} children")
                    
                    results.append(location_entry)
                
                return results
            
            # Log the start of the export process
            logger.info(f"Starting recursive fetch of all locations from root ID: {root_id}")
            start_time = datetime.now()
            
            # Start the recursive fetch from the root
            all_locations = fetch_locations_recursively(root_id)
            
            # Calculate and log the time taken
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Completed export of all locations in {duration:.2f} seconds")
            
            # Count total locations
            def count_locations(locations):
                count = len(locations)
                for location in locations:
                    if 'children' in location and location['children']:
                        count += count_locations(location['children'])
                return count
            
            total_locations = count_locations(all_locations)
            logger.info(f"Total locations exported: {total_locations}")
            
            # Return the complete hierarchy
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': round(duration, 2),
                'total_locations': total_locations,
                'location_hierarchy': all_locations
            }
            
        except Exception as e:
            logger.error(f"Error exporting locations: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }



    # Add this to your urls.py
    # path('webhook/webform/locations-export/', LocationExportView.as_view(), name='locations-export'),




    def export_case_categories(self) -> dict:
        """
        Exports all case categories from the system in a hierarchical structure.
        This function traverses the entire case category hierarchy, starting from the root case category,
        and builds a complete tree of all case categories with their IDs.
        
        Returns:
            dict: A dictionary containing the full case category hierarchy with IDs
        """
        try:
            # Get API token from configuration
            auth_token = self.config.get('api_token')
            
            if not auth_token:
                logger.error("Missing API token")
                return {
                    'status': 'error',
                    'error': 'Missing API configuration'
                }
            
            # Base URL for the external API
            base_url = "https://demo-openchs.bitz-itc.com/helpline/api/categories/"
            
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Start with the top level (Case Category)
            logger.info("Starting export of all case categories")
            root_id = "362557"  # Case Category root ID
            
            # Log the start of the export process
            logger.info(f"Starting recursive fetch of all case categories from root ID: {root_id}")
            start_time = datetime.now()
            
            # Function to recursively fetch all case categories in the hierarchy
            def fetch_categories_recursively(category_id, current_path=None, depth=0):
                if current_path is None:
                    current_path = []
                
                # Create indentation for readable logs
                indent = "  " * depth
                
                # Log the start of fetching this category
                path_str = " -> ".join([item.get('name', 'Unknown') for item in current_path]) if current_path else "Root"
                logger.info(f"{indent}Fetching case category ID: {category_id} (Path: {path_str})")
                
                # Fetch data for the current category
                url = f"{base_url}{category_id}"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"{indent}API error when fetching case category {category_id}: {response.status_code}")
                    return None
                
                data = response.json()
                
                # Get the subcategories
                subcategories = data.get('subcategories', [])
                
                # Log the number of subcategories found
                logger.info(f"{indent}Found {len(subcategories)} subcategories for case category ID: {category_id}")
                
                # If no subcategories, return an empty list
                if not subcategories:
                    logger.info(f"{indent}No subcategories found for case category ID: {category_id} - this is a leaf node")
                    return []
                
                # Process each subcategory
                results = []
                for i, subcategory in enumerate(subcategories):
                    sub_id = subcategory[0]
                    sub_name = subcategory[5]
                    parent_id = subcategory[8] if len(subcategory) > 8 else None
                    full_path = subcategory[6] if len(subcategory) > 6 else None
                    
                    # Skip if we can't get the ID
                    if not sub_id:
                        logger.warning(f"{indent}Skipping subcategory at index {i} due to missing ID")
                        continue
                    
                    # Log the subcategory being processed
                    logger.info(f"{indent}Processing subcategory: {sub_name} (ID: {sub_id})")
                    if full_path:
                        logger.info(f"{indent}  Full path: {full_path}")
                    
                    # Determine the level based on the path or position
                    level_name = None
                    if full_path:
                        # Count the segments in the path (each level is separated by ^)
                        segments = full_path.split('^')
                        # Remove empty segments
                        segments = [s for s in segments if s]
                        level_pos = len(segments) - 1
                        
                        # Map position to level name
                        level_map = {
                            0: 'category',
                            1: 'subcategory',
                            2: 'subsubcategory',
                            3: 'type',
                            4: 'subtype'
                        }
                        level_name = level_map.get(level_pos, 'level_' + str(level_pos))
                    
                    # Log the determined level
                    logger.info(f"{indent}  Level determined as: {level_name}")
                    
                    # Create the updated path for this subcategory
                    updated_path = current_path + [{'id': sub_id, 'name': sub_name}]
                    
                    # Log that we're about to recursively fetch children
                    logger.info(f"{indent}Starting recursive fetch for: {sub_name} (ID: {sub_id})")
                    
                    # Create category entry with children from recursive call
                    children = fetch_categories_recursively(sub_id, updated_path, depth + 1)
                    
                    category_entry = {
                        'id': sub_id,
                        'name': sub_name,
                        'level': level_name,
                        'parent_id': parent_id,
                        'full_path': full_path,
                        'children': children
                    }
                    
                    # Log the completion of this subcategory processing
                    child_count = len(children) if children else 0
                    logger.info(f"{indent}Completed processing {sub_name} (ID: {sub_id}) with {child_count} children")
                    
                    results.append(category_entry)
                
                return results
            
            # Start the recursive fetch from the root
            all_categories = fetch_categories_recursively(root_id)
            
            # Calculate and log the time taken
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Completed export of all case categories in {duration:.2f} seconds")
            
            # Count total categories
            def count_categories(categories):
                count = len(categories)
                for category in categories:
                    if 'children' in category and category['children']:
                        count += count_categories(category['children'])
                return count
            
            total_categories = count_categories(all_categories)
            logger.info(f"Total case categories exported: {total_categories}")
            
            # Return the complete hierarchy
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': round(duration, 2),
                'total_categories': total_categories,
                'category_hierarchy': all_categories
            }
            
        except Exception as e:
            logger.error(f"Error exporting case categories: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }


