import json
import logging
import uuid
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import logging
import requests
import csv
from django.http import JsonResponse, HttpResponse
from webhook_handler.token_manager import TokenManager
from platform_adapters.adapter_factory import AdapterFactory
from endpoint_integration.message_router import MessageRouter
from shared.models.standard_message import StandardMessage
from webhook_handler.services.conversation_service import ConversationService
from webhook_handler.models import (
    Contact, Person, Complaint, WhatsAppMessage, 
    WhatsAppMedia, Conversation, WebhookMessage,
    Organization, WhatsAppCredential, Notification
)

logger = logging.getLogger(__name__)
router = MessageRouter()

@method_decorator(csrf_exempt, name='dispatch')
class UnifiedWebhookView(View):
    """
    Unified view for handling webhooks from all platforms.
    
    This view processes all communication for all platforms:
    - Incoming messages (from platforms to the system)
    - Outgoing messages (from the system to platforms)
    - Verification challenges
    - Token management
    """
    
    def get(self, request, platform, *args, **kwargs):
        """
        Handle GET requests (typically verification challenges).
        
        Args:
            request: The HTTP request
            platform: Platform identifier from URL
            
        Returns:
            HTTP response
        """
        try:
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Let the adapter handle verification
            response = adapter.handle_verification(request)
            if response:
                return response
                
            # If adapter didn't handle it, return a default response
            return HttpResponse("Verification not required or failed.")
            
        except ValueError as e:
            # Unsupported platform
            logger.error(f"Unsupported platform: {platform}")
            return HttpResponse(f"Unsupported platform: {platform}", status=404)
            
        except Exception as e:
            logger.exception(f"Error handling verification: {str(e)}")
            return HttpResponse("Verification failed", status=500)
    
    def post(self, request, platform, *args, **kwargs):
        """
        Handle POST requests (incoming and outgoing messages).
        
        This method now handles:
        1. Incoming messages from platforms
        2. Outgoing messages to platforms
        3. Token management operations
        
        Args:
            request: The HTTP request
            platform: Platform identifier from URL
            
        Returns:
            HTTP response
        """
        try:
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                # If the body isn't JSON, treat it as form data
                payload = request.POST.dict()
                
            # Determine the direction of the message flow
            direction = payload.get('direction', 'incoming')
            
            # Handle outgoing messages (system to platform)
            if direction == 'outgoing':
                return self._handle_outgoing_message(adapter, platform, payload, request)
                
            # Handle token operations
            elif direction == 'token':
                return self._handle_token_operation(adapter, platform, payload, request)
                
            # Handle incoming messages (platform to system)
            else:
                # For webform, use a special handler
                if platform == 'webform':
                    return self._handle_webform_submission(adapter, payload, request)
                
                # For other platforms, validate the request
                if not adapter.validate_request(request):
                    return HttpResponse("Invalid request", status=400)
                
                # Parse messages from the request
                messages = adapter.parse_messages(request)
                
                # Process each message
                responses = []
                for message_dict in messages:
                    # Convert to StandardMessage object
                    std_message = StandardMessage.from_dict(message_dict)
                    
                    # Route to endpoint
                    response = router.route_to_endpoint(std_message)
                    responses.append(response)
                
                # Format the response according to platform requirements
                return adapter.format_webhook_response(responses)
                
        except ValueError as e:
            # Unsupported platform
            logger.error(f"Unsupported platform: {platform}")
            return HttpResponse(f"Unsupported platform: {platform}", status=404)
            
        except Exception as e:
            logger.exception(f"Error processing webhook: {str(e)}")
            return HttpResponse("Processing failed", status=500)
    
    def _handle_incoming_message(self, adapter, platform, payload, request):
        """
        Process incoming messages from a platform.
        
        Args:
            adapter: Platform adapter instance
            platform: Platform identifier
            payload: Request payload
            request: HTTP request
            
        Returns:
            HTTP response
        """
        # For webform, use the payload data directly
        if platform == 'webform':
            return self._handle_webform_submission(adapter, payload)
            
        # For other platforms, validate the request
        if not adapter.validate_request(request):
            return HttpResponse("Invalid request", status=400)
        
        # Parse messages from the request
        messages = adapter.parse_messages(request)
        
        # Process each message
        responses = []
        for message_dict in messages:
            # Convert to StandardMessage object
            std_message = StandardMessage.from_dict(message_dict)
            
            # Route to endpoint
            response = router.route_to_endpoint(std_message)
            responses.append(response)
        
        # Format the response according to platform requirements
        return adapter.format_webhook_response(responses)
    
    def _handle_outgoing_message(self, adapter, platform, payload, request):
        """
        Process outgoing messages to a platform.
        
        Args:
            adapter: Platform adapter instance
            platform: Platform identifier
            payload: Request payload
            request: HTTP request
            
        Returns:
            HTTP response
        """
        data = payload.get('data', {})
        
        if platform == 'whatsapp':
            # Required fields
            recipient = data.get('recipient')
            message_type = data.get('message_type', 'text')
            content = data.get('content', '')
            
            if not recipient:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Recipient is required'
                }, status=400)
            
            # Prepare message content
            message_content = {
                'message_type': message_type,
                'content': content,
                'caption': data.get('caption'),
                'media_url': data.get('media_url')
            }
            
            # Send the message
            response = adapter.send_message(recipient, message_content)
            
            # Return response
            if response.get('status') == 'success':
                return JsonResponse({
                    'status': 'success',
                    'message_id': response.get('message_id'),
                    'message': 'Message sent successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': response.get('error', 'Failed to send message')
                }, status=400)
        
        # Return error for unsupported platforms
        return JsonResponse({
            'status': 'error',
            'message': f'Sending messages not supported for platform: {platform}'
        }, status=400)
    
    def _handle_token_operation(self, adapter, platform, payload, request):
        """
        Process token operations for a platform.
        
        Args:
            adapter: Platform adapter instance
            platform: Platform identifier
            payload: Request payload
            request: HTTP request
            
        Returns:
            HTTP response
        """
        data = payload.get('data', {})
        
        if platform == 'whatsapp':
            # Required fields
            short_lived_token = data.get('short_lived_token')
            org_id = data.get('org_id')
            
            if not short_lived_token:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Short-lived token is required'
                }, status=400)
            
            # Generate token
            if hasattr(adapter, 'generate_token'):
                response = adapter.generate_token(short_lived_token, org_id)
                
                # Return response
                if response.get('status') == 'success':
                    return JsonResponse({
                        'status': 'success',
                        'token': response.get('token'),
                        'expiry': response.get('expiry'),
                        'organization_id': response.get('organization_id')
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': response.get('error', 'Failed to generate token')
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Token operations not supported for platform: {platform}'
                }, status=400)
        
        # Return error for unsupported platforms
        return JsonResponse({
            'status': 'error',
            'message': f'Token operations not supported for platform: {platform}'
        }, status=400)
    
    def _handle_webform_submission(self, adapter, payload, request=None):
        """
        Process webform submissions.
        
        Args:
            adapter: Platform adapter instance
            payload: Request payload
            request: HTTP request (optional)
                
        Returns:
            HTTP response
        """
        try:
            # Extract data from payload
            data = payload.get('data', payload)  # Allow both nested and flat data
            
            # Add organization ID if available from token authentication
            if request and hasattr(request, 'organization_id'):
                data['organization_id'] = request.organization_id
                data['organization_name'] = request.organization_name
            
            # Import the ComplaintSerializer 
            from platform_adapters.webform.serializers import ComplaintSerializer
            
            # Validate and create using the nested serializer
            complaint_serializer = ComplaintSerializer(data=data)
            if complaint_serializer.is_valid():
                complaint = complaint_serializer.save()
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid complaint data',
                    'errors': complaint_serializer.errors
                }, status=400)
            
            # Convert complaint to StandardMessage
            standard_message = adapter.create_from_complaint(complaint)
            
            # Route to endpoint
            response = router.route_to_endpoint(standard_message)
            
            # Update complaint with message_id_ref if available
            if response.get('status') == 'success' and response.get('message_id'):
                complaint.message_id_ref = response['message_id']
                complaint.save(update_fields=["message_id_ref"])
            
            # Create a notification
            notification = Notification.objects.create(
                complaint=complaint,
                message=f"Your complaint has been submitted successfully. Reference ID: {complaint.complaint_id}"
            )
            
            return JsonResponse({
                'status': 'success',
                'complaint_id': str(complaint.complaint_id),
                'message': 'Complaint submitted successfully',
                'notification_id': str(notification.notification_id),
                'response_from_kim': response
            })
                
        except Exception as e:
            logger.exception(f"Error processing webform: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Processing failed',
                'error': str(e)
            }, status=500)
    
    def _get_categories_from_payload(self, adapter):
        """
        Extract categories from the payload.
        
        Args:
            payload: The request payload
        
        Returns:
            List of categories
        """
        # Assuming the payload contains a 'categories' field
        return payload.get('categories', [])

from django.http import JsonResponse
from django.views import View
import logging

logger = logging.getLogger(__name__)

class WebformCategoriesView(View):
    """
    View for retrieving categories and subcategories for the webform.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for categories and subcategories.
        
        Args:
            request: The HTTP request, which may contain a category ID as a query parameter.

        Returns:
            JSON response with categories or subcategories.
        """
        try:
            # Get the webform adapter
            adapter = AdapterFactory.get_adapter('webform')

            # Get category ID from request parameters (if provided)
            category_id = request.GET.get('category_id')

            if category_id:
                try:
                    category_id = int(category_id)  # Ensure it's an integer
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid category_id. It must be an integer.'
                    }, status=400)

                # Fetch subcategories for the given category_id
                response = adapter.get_subcategories(category_id)

                if response.get('status') == 'success':
                    return JsonResponse({
                        'status': 'success',
                        'category_id': category_id,
                        'subcategories': response.get('subcategories', [])
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': response.get('error', 'Failed to fetch subcategories')
                    }, status=400)
            
            # If no category_id is provided, return main categories
            response = adapter.get_categories()

            if response.get('status') == 'success':
                return JsonResponse({
                    'status': 'success',
                    'categories': response.get('categories', [])
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': response.get('error', 'Failed to fetch categories')
                }, status=400)

        except Exception as e:
            logger.error(f"Unexpected error in WebformCategoriesView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Internal Server Error: {str(e)}'
            }, status=500)
from django.http import JsonResponse
from django.views import View
import logging

# Assuming you have a logger set up
logger = logging.getLogger(__name__)

class LocationExportView(View):
    """
    View to export all locations in a hierarchical structure.
    This endpoint provides a complete export of all locations in the system,
    organized in their hierarchical structure.
    
    Options:
    - ?format=json (default) - Returns hierarchical JSON data
    - ?format=csv - Returns flattened CSV data
    - ?log_level=INFO (default) - Sets logging verbosity (DEBUG, INFO, WARNING, ERROR)
    """

    def get(self, request, *args, **kwargs):
        try:
            # Set logging level based on request parameter
            log_level = request.GET.get('log_level', 'INFO').upper()
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
            
            if log_level in valid_levels:
                numeric_level = getattr(logging, log_level)
                logger.setLevel(numeric_level)
                logger.info(f"Log level set to {log_level}")
            else:
                logger.setLevel(logging.INFO)
                logger.warning(f"Invalid log level: {log_level}. Using INFO.")
            
            # Get the adapter from the factory
            adapter = AdapterFactory.get_adapter('webform')
            
            # Get the format parameter (default to 'json')
            export_format = request.GET.get('format', 'json').lower()
            
            # Log request details
            logger.info(f"Location export requested with format: {export_format}")
            
            # Export all locations
            response_data = adapter.export_all_locations()
            
            # Check if export was successful
            if response_data.get('status') != 'success':
                return JsonResponse({
                    'status': 'error',
                    'message': response_data.get('error', 'Failed to export locations')
                }, status=400)
            
            # Handle different output formats
            if export_format == 'csv':
                # Convert hierarchical data to flat structure for CSV
                flat_locations = self._flatten_location_hierarchy(response_data['location_hierarchy'])
                
                # Create CSV response
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="locations_export.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['id', 'name', 'level', 'parent_id', 'full_path'])
                
                for location in flat_locations:
                    writer.writerow([
                        location['id'],
                        location['name'],
                        location['level'],
                        location['parent_id'],
                        location['full_path']
                    ])
                
                return response
            else:
                # Default to JSON response
                return JsonResponse(response_data)
                
        except Exception as e:
            logger.error(f"Error in LocationExportView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Internal server error: {str(e)}"
            }, status=500)
    
    def _flatten_location_hierarchy(self, locations, flat_list=None):
        """
        Convert the hierarchical location structure to a flat list.
        
        Args:
            locations: List of location dictionaries with nested children
            flat_list: List to accumulate flattened locations
            
        Returns:
            list: Flat list of all locations
        """
        if flat_list is None:
            flat_list = []
        
        for location in locations:
            # Create a copy without the children field
            flat_location = {
                'id': location['id'],
                'name': location['name'],
                'level': location['level'],
                'parent_id': location['parent_id'],
                'full_path': location['full_path']
            }
            
            flat_list.append(flat_location)
            
            # Process children recursively
            if 'children' in location and location['children']:
                self._flatten_location_hierarchy(location['children'], flat_list)
        
        return flat_list
    
class TokenGenerationView(View):
    """
    View for generating authentication tokens for organizations.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for token generation.
        
        Args:
            request: The HTTP request
            
        Returns:
            JSON response with token
        """
        try:
            # Parse request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON in request body.'
                }, status=400)
                
            # Extract organization name
            organization_name = data.get('organization_name')
            organization_email = data.get('organization_email')
            
            if not organization_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Organization name is required.'
                }, status=400)
                
            # Generate token
            token_data = TokenManager.generate_token(organization_name, organization_email)
            
            # Return token
            return JsonResponse({
                'status': 'success',
                'message': 'Authentication token generated successfully.',
                'token': token_data['token'],
                'organization_id': token_data['organization_id'],
                'expires': token_data['expires']
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error generating token: {str(e)}'
            }, status=500)
        

# POST {{base_url}}/api/webhook/webform/auth/token/
# Content-Type: application/json

# {
#   "organization_name": "CPMIS System",
#   "organization_email": "admin@cpmis.org"
# }

# {
#   "status": "success",
#   "message": "Authentication token generated successfully.",
#   "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "organization_id": "12345",
#   "expires": "2026-04-03T11:09:50.554Z"
# }

# POST {{base_url}}/api/webhook/webform/
# Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
# Content-Type: application/json

# {
#   "reporter_nickname": "Anonymous",
#   "case_category": "HARASSMENT",
#   "complaint_text": "I would like to report a case of harassment...",
#   ...
# }

class CaseCategoryExportView(View):
    """
    View to export all case categories in a hierarchical structure.
    This endpoint provides a complete export of all case categories in the system,
    organized in their hierarchical structure.
    
    Options:
    - ?format=json (default) - Returns hierarchical JSON data
    - ?format=csv - Returns flattened CSV data
    - ?log_level=INFO (default) - Sets logging verbosity (DEBUG, INFO, WARNING, ERROR)
    """

    def get(self, request, *args, **kwargs):
        try:
            # Set logging level based on request parameter
            log_level = request.GET.get('log_level', 'INFO').upper()
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
            
            if log_level in valid_levels:
                numeric_level = getattr(logging, log_level)
                logger.setLevel(numeric_level)
                logger.info(f"Log level set to {log_level}")
            else:
                logger.setLevel(logging.INFO)
                logger.warning(f"Invalid log level: {log_level}. Using INFO.")
            
            # Get the adapter from the factory
            adapter = AdapterFactory.get_adapter('webform')
            
            # Get the format parameter (default to 'json')
            export_format = request.GET.get('format', 'json').lower()
            
            # Log request details
            logger.info(f"Case category export requested with format: {export_format}")
            
            # Export all case categories
            response_data = adapter.export_case_categories()
            
            # Check if export was successful
            if response_data.get('status') != 'success':
                return JsonResponse({
                    'status': 'error',
                    'message': response_data.get('error', 'Failed to export case categories')
                }, status=400)
            
            # Handle different output formats
            if export_format == 'csv':
                # Convert hierarchical data to flat structure for CSV
                flat_categories = self._flatten_category_hierarchy(response_data['category_hierarchy'])
                
                # Create CSV response
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="case_categories_export.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['id', 'name', 'level', 'parent_id', 'full_path'])
                
                for category in flat_categories:
                    writer.writerow([
                        category['id'],
                        category['name'],
                        category['level'],
                        category['parent_id'],
                        category['full_path']
                    ])
                
                return response
            else:
                # Default to JSON response
                return JsonResponse(response_data)
                
        except Exception as e:
            logger.error(f"Error in CaseCategoryExportView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Internal server error: {str(e)}"
            }, status=500)
    
    def _flatten_category_hierarchy(self, categories, flat_list=None):
        """
        Convert the hierarchical category structure to a flat list.
        
        Args:
            categories: List of category dictionaries with nested children
            flat_list: List to accumulate flattened categories
            
        Returns:
            list: Flat list of all categories
        """
        if flat_list is None:
            flat_list = []
        
        for category in categories:
            # Create a copy without the children field
            flat_category = {
                'id': category['id'],
                'name': category['name'],
                'level': category['level'],
                'parent_id': category['parent_id'],
                'full_path': category['full_path']
            }
            
            flat_list.append(flat_category)
            
            # Process children recursively
            if 'children' in category and category['children']:
                self._flatten_category_hierarchy(category['children'], flat_list)
        
        return flat_list

# Add this to your urls.py
