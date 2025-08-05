# apps/shared/api/authentication.py

import logging
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions
from .models import APIKey, APIRequestLog

logger = logging.getLogger(__name__)


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for API key-based access.
    
    Supports both platform-level and tenant-scoped API keys.
    Handles rate limiting, origin validation, and automatic logging.
    
    Expected header format:
        Authorization: ApiKey your-api-key-here
        or
        X-API-Key: your-api-key-here
    """
    
    keyword = 'ApiKey'
    header_name = 'HTTP_AUTHORIZATION'
    alt_header_name = 'HTTP_X_API_KEY'
    
    def authenticate(self, request):
        """
        Authenticate the request using API key.
        
        Returns:
            tuple: (user, auth_info) if successful, None if no API key provided
            
        Raises:
            AuthenticationFailed: If API key is invalid or restricted
        """
        api_key_value = self._get_api_key_from_request(request)
        
        if not api_key_value:
            return None  # No API key provided, try next authentication method
        
        api_key = self._validate_api_key(api_key_value, request)
        
        # Set API key in request for later use
        request.api_key = api_key
        request.tenant = api_key.tenant
        
        # Create a user object representing the API key
        # This allows the rest of the system to work with "user" concept
        api_user = self._create_api_user(api_key)
        
        # Return user and API key info for DRF
        return (api_user, {'api_key': api_key, 'tenant': api_key.tenant})
    
    def _get_api_key_from_request(self, request):
        """Extract API key from request headers."""
        # Try Authorization header first: "Authorization: ApiKey abc123"
        auth_header = request.META.get(self.header_name)
        if auth_header:
            try:
                keyword, key = auth_header.split(' ', 1)
                if keyword.lower() == self.keyword.lower():
                    return key.strip()
            except ValueError:
                pass
        
        # Try X-API-Key header: "X-API-Key: abc123"
        api_key_header = request.META.get(self.alt_header_name)
        if api_key_header:
            return api_key_header.strip()
        
        return None
    
    def _validate_api_key(self, api_key_value, request):
        """
        Validate the API key and check all restrictions.
        
        Args:
            api_key_value: The raw API key string
            request: The Django request object
            
        Returns:
            APIKey: The valid API key object
            
        Raises:
            AuthenticationFailed: If validation fails
        """
        # Look up the API key
        api_key = APIKey.objects.get_by_key(api_key_value)
        if not api_key:
            logger.warning(f"Invalid API key attempted from {self._get_client_ip(request)}")
            raise exceptions.AuthenticationFailed(_('Invalid API key'))
        
        # Check if key is active
        if not api_key.is_active:
            logger.warning(f"Inactive API key {api_key.key_prefix}... attempted from {self._get_client_ip(request)}")
            raise exceptions.AuthenticationFailed(_('API key is disabled'))
        
        # Check expiration
        if api_key.is_expired():
            logger.warning(f"Expired API key {api_key.key_prefix}... attempted from {self._get_client_ip(request)}")
            raise exceptions.AuthenticationFailed(_('API key has expired'))
        
        # Check rate limiting
        if api_key.is_rate_limited():
            logger.warning(f"Rate limited API key {api_key.key_prefix}... from {self._get_client_ip(request)}")
            raise exceptions.Throttled(
                detail=_('API key rate limit exceeded'),
                wait=self._get_rate_limit_reset_time(api_key)
            )
        
        # Check allowed origins
        origin = self._get_request_origin(request)
        if not api_key.is_origin_allowed(origin):
            logger.warning(f"Unauthorized origin {origin} for API key {api_key.key_prefix}...")
            raise exceptions.AuthenticationFailed(_('Origin not allowed for this API key'))
        
        # Update usage and last used info
        api_key.increment_usage()
        api_key.last_used_ip = self._get_client_ip(request)
        api_key.save(update_fields=['last_used_ip'])
        
        logger.info(f"API key {api_key.key_prefix}... authenticated successfully")
        return api_key
    
    def _create_api_user(self, api_key):
        """
        Create a pseudo-user object for API key authentication.
        
        This allows the rest of the system to work with user-based permissions
        while using API keys for authentication.
        """
        class APIUser:
            """Pseudo-user class representing an API key."""
            
            def __init__(self, api_key):
                self.api_key = api_key
                self.tenant = api_key.tenant
                self.is_authenticated = True
                self.is_active = api_key.is_active
                self.is_anonymous = False
                self.is_staff = False
                self.is_superuser = False
                
                # For display purposes
                self.username = f"api_key_{api_key.key_prefix}"
                self.email = ""
                self.first_name = ""
                self.last_name = api_key.name
                
                # API-specific attributes
                self.is_api_user = True
                self.pk = None
                self.id = None
            
            def __str__(self):
                return f"APIUser({self.api_key.name})"
            
            def get_full_name(self):
                return self.api_key.name
            
            def get_short_name(self):
                return self.api_key.name
            
            def has_perm(self, permission):
                """Check if API key has a specific permission."""
                return self.api_key.has_permission(permission)
            
            def has_perms(self, permissions):
                """Check if API key has all specified permissions."""
                return all(self.has_perm(perm) for perm in permissions)
            
            def has_module_perms(self, app_label):
                """Check if API key has any permissions for the given app."""
                # Check if any permission starts with the app label
                for permission_key in self.api_key.permissions.keys():
                    if permission_key.startswith(f"{app_label}."):
                        return True
                return False
            
            def save(self, *args, **kwargs):
                """Prevent saving - this is a pseudo-user."""
                raise NotImplementedError("Cannot save API user objects")
        
        return APIUser(api_key)
    
    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _get_request_origin(self, request):
        """Extract origin from request for validation."""
        # Try various headers to determine origin
        origin = (
            request.META.get('HTTP_ORIGIN') or
            request.META.get('HTTP_HOST') or
            request.META.get('HTTP_REFERER', '').split('/')[2] if '/' in request.META.get('HTTP_REFERER', '') else
            self._get_client_ip(request)
        )
        return origin.split(':')[0] if ':' in origin else origin
    
    def _get_rate_limit_reset_time(self, api_key):
        """Calculate seconds until rate limit resets."""
        if api_key.usage_reset_at > timezone.now():
            return (api_key.usage_reset_at - timezone.now()).total_seconds()
        return 0
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return f'{self.keyword} realm="API"'


class TenantAPIKeyAuthentication(APIKeyAuthentication):
    """
    API Key authentication that enforces tenant-scoped access.
    
    Only allows API keys that are specifically scoped to a tenant.
    Platform-wide API keys are rejected.
    """
    
    def _validate_api_key(self, api_key_value, request):
        """Validate API key and ensure it's tenant-scoped."""
        api_key = super()._validate_api_key(api_key_value, request)
        
        # Ensure the API key is tenant-scoped
        if not api_key.tenant:
            logger.warning(f"Platform API key {api_key.key_prefix}... attempted on tenant endpoint")
            raise exceptions.AuthenticationFailed(
                _('This endpoint requires a tenant-scoped API key')
            )
        
        return api_key


class PlatformAPIKeyAuthentication(APIKeyAuthentication):
    """
    API Key authentication for platform-level operations.
    
    Only allows platform-wide API keys (not tenant-scoped).
    Used for platform administration and cross-tenant operations.
    """
    
    def _validate_api_key(self, api_key_value, request):
        """Validate API key and ensure it's platform-scoped."""
        api_key = super()._validate_api_key(api_key_value, request)
        
        # Ensure the API key is platform-scoped (no tenant)
        if api_key.tenant:
            logger.warning(f"Tenant API key {api_key.key_prefix}... attempted on platform endpoint")
            raise exceptions.AuthenticationFailed(
                _('This endpoint requires a platform-level API key')
            )
        
        return api_key


class APIRequestLoggingMixin:
    """
    Mixin to add automatic API request logging to views.
    
    Can be used with any DRF view to automatically log API requests
    with detailed timing and response information.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add request logging."""
        start_time = timezone.now()
        
        # Call the parent dispatch method
        response = super().dispatch(request, *args, **kwargs)
        
        # Log the request
        self._log_api_request(request, response, start_time)
        
        return response
    
    def _log_api_request(self, request, response, start_time):
        """Log the API request with detailed information."""
        try:
            # Calculate response time
            response_time = timezone.now() - start_time
            
            # Get API key if available
            api_key = getattr(request, 'api_key', None)
            
            # Prepare response data (metadata only, not full response)
            response_data = {
                'content_type': getattr(response, 'content_type', ''),
                'has_content': bool(getattr(response, 'content', '')),
            }
            
            # Add error information if it's an error response
            if hasattr(response, 'status_code') and response.status_code >= 400:
                response_data['error'] = True
                if hasattr(response, 'data') and isinstance(response.data, dict):
                    # Include error message but not sensitive data
                    response_data['error_type'] = response.data.get('error', 'unknown')
                    response_data['detail'] = str(response.data.get('detail', ''))[:200]  # Limit length
            
            # Create log entry
            log_entry = APIRequestLog.objects.log_request(
                api_key=api_key,
                request=request,
                response_data=response_data
            )
            
            # Update with response information
            log_entry.status_code = getattr(response, 'status_code', None)
            log_entry.response_time = response_time
            
            # Calculate response size
            if hasattr(response, 'content'):
                log_entry.response_size = len(response.content)
            
            log_entry.save(update_fields=['status_code', 'response_time', 'response_size'])
            
        except Exception as e:
            # Don't let logging errors break the API response
            logger.error(f"Error logging API request: {e}")
    
    def handle_exception(self, exc):
        """Override to log exceptions in API requests."""
        try:
            # Log the exception
            api_key = getattr(self.request, 'api_key', None)
            if api_key:
                log_entry = APIRequestLog.objects.log_request(
                    api_key=api_key,
                    request=self.request,
                    response_data={'error': True, 'exception': str(exc)}
                )
                log_entry.error_message = str(exc)
                log_entry.exception_type = type(exc).__name__
                log_entry.status_code = getattr(exc, 'status_code', 500)
                log_entry.save(update_fields=['error_message', 'exception_type', 'status_code'])
        except Exception as log_error:
            logger.error(f"Error logging API exception: {log_error}")
        
        # Call parent exception handler
        return super().handle_exception(exc)


class APIKeyPermissionMixin:
    """
    Mixin to add API key permission checking to views.
    
    Provides methods to check if the current API key has specific permissions.
    """
    
    def check_api_permission(self, permission_key, raise_exception=True):
        """
        Check if the current API key has a specific permission.
        
        Args:
            permission_key: Dot-notation permission (e.g., 'cases.create')
            raise_exception: Whether to raise PermissionDenied if check fails
            
        Returns:
            bool: True if permission is granted
            
        Raises:
            PermissionDenied: If permission check fails and raise_exception=True
        """
        api_key = getattr(self.request, 'api_key', None)
        
        if not api_key:
            if raise_exception:
                raise exceptions.PermissionDenied(_('API key required'))
            return False
        
        has_permission = api_key.has_permission(permission_key)
        
        if not has_permission and raise_exception:
            logger.warning(
                f"API key {api_key.key_prefix}... denied permission '{permission_key}'"
            )
            raise exceptions.PermissionDenied(
                _(f'API key does not have permission: {permission_key}')
            )
        
        return has_permission
    
    def get_api_key(self):
        """Get the current API key from the request."""
        return getattr(self.request, 'api_key', None)
    
    def get_api_tenant(self):
        """Get the tenant associated with the current API key."""
        api_key = self.get_api_key()
        return api_key.tenant if api_key else None


# Convenience function for manual API key validation
def validate_api_key(key_value, require_tenant=None, require_permission=None):
    """
    Validate an API key manually (outside of DRF authentication).
    
    Args:
        key_value: The raw API key string
        require_tenant: If True, requires tenant-scoped key. If False, requires platform key.
        require_permission: Permission key that must be granted
        
    Returns:
        APIKey: Valid API key object
        
    Raises:
        ValueError: If validation fails
    """
    api_key = APIKey.objects.get_by_key(key_value)
    
    if not api_key:
        raise ValueError("Invalid API key")
    
    if not api_key.is_active:
        raise ValueError("API key is disabled")
    
    if api_key.is_expired():
        raise ValueError("API key has expired")
    
    if api_key.is_rate_limited():
        raise ValueError("API key rate limit exceeded")
    
    if require_tenant is not None:
        if require_tenant and not api_key.tenant:
            raise ValueError("Tenant-scoped API key required")
        if not require_tenant and api_key.tenant:
            raise ValueError("Platform-level API key required")
    
    if require_permission and not api_key.has_permission(require_permission):
        raise ValueError(f"API key missing required permission: {require_permission}")
    
    return api_key