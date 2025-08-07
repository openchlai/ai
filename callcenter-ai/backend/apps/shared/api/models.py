# apps/shared/api/models.py

import secrets
import hashlib
from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.shared.core.models import BaseModel, TimestampedModel

User = get_user_model()


class APIKeyManager(models.Manager):
    """Manager for APIKey model with utility methods."""
    
    def create_api_key(self, name, tenant=None, user=None, permissions=None, rate_limit=1000):
        """Create a new API key with auto-generated key value."""
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = self.create(
            name=name,
            key_hash=key_hash,
            tenant=tenant,
            permissions=permissions or {},
            rate_limit=rate_limit,
            created_by=user,
            updated_by=user
        )
        
        # Return both the object and the raw key (only time raw key is available)
        return api_key, raw_key
    
    def get_by_key(self, raw_key):
        """Get API key by raw key value."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            return self.get(key_hash=key_hash, is_active=True, is_deleted=False)
        except self.model.DoesNotExist:
            return None
    
    def active(self):
        """Get only active, non-deleted API keys."""
        return self.filter(is_active=True, is_deleted=False)


class APIKey(BaseModel):
    """
    API Key model for external API access.
    
    Supports both platform-level and tenant-specific API keys.
    Platform admins can create platform-wide keys, tenant users create tenant-scoped keys.
    """
    
    # Basic information
    name = models.CharField(
        max_length=100,
        help_text="Human-readable name for this API key"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of API key purpose"
    )
    
    # Key management
    key_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="SHA256 hash of the actual API key"
    )
    key_prefix = models.CharField(
        max_length=10,
        editable=False,
        help_text="First few characters of key for identification"
    )
    
    # Scope and permissions
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="If set, key is scoped to this tenant only. If null, platform-wide key."
    )
    permissions = models.JSONField(
        default=dict,
        help_text="JSON object defining what this API key can access"
    )
    
    # Rate limiting and usage
    rate_limit = models.IntegerField(
        default=1000,
        help_text="Maximum requests per hour"
    )
    current_usage = models.IntegerField(
        default=0,
        help_text="Current hour's request count"
    )
    usage_reset_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the current usage counter resets"
    )
    
    # Status and lifecycle
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this API key is currently active"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional expiration date for the API key"
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this API key was used"
    )
    last_used_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last usage"
    )
    
    # Allowed origins (for CORS-like restrictions)
    allowed_origins = models.JSONField(
        default=list,
        blank=True,
        help_text="List of allowed origin domains/IPs. Empty list means no restrictions."
    )
    
    objects = APIKeyManager()
    
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key_hash']),
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['is_active', 'expires_at']),
            models.Index(fields=['usage_reset_at']),
        ]
    
    def __str__(self):
        scope = f"({self.tenant.name})" if self.tenant else "(Platform)"
        return f"{self.name} {scope}"
    
    def save(self, *args, **kwargs):
        # Set key prefix for identification (first 8 chars of hash)
        if self.key_hash and not self.key_prefix:
            self.key_prefix = self.key_hash[:8]
        
        # Initialize usage reset time
        if not self.usage_reset_at:
            self.usage_reset_at = timezone.now() + timedelta(hours=1)
            
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate API key configuration."""
        super().clean()
        
        # Validate permissions structure
        if self.permissions and not isinstance(self.permissions, dict):
            raise ValidationError("Permissions must be a valid JSON object")
        
        # Validate allowed origins
        if self.allowed_origins and not isinstance(self.allowed_origins, list):
            raise ValidationError("Allowed origins must be a list")
    
    def is_expired(self):
        """Check if the API key has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def is_rate_limited(self):
        """Check if the API key has exceeded its rate limit."""
        if timezone.now() > self.usage_reset_at:
            # Reset usage counter if hour has passed
            self.current_usage = 0
            self.usage_reset_at = timezone.now() + timedelta(hours=1)
            self.save(update_fields=['current_usage', 'usage_reset_at'])
        
        return self.current_usage >= self.rate_limit
    
    def increment_usage(self, save=True):
        """Increment the usage counter and update last used info."""
        self.current_usage += 1
        self.last_used_at = timezone.now()
        
        if save:
            self.save(update_fields=['current_usage', 'last_used_at'])
    
    def has_permission(self, permission_key):
        """
        Check if this API key has a specific permission.
        
        Args:
            permission_key: Dot-notation permission like 'cases.create' or 'admin.users'
        
        Returns:
            bool: True if permission is granted
        """
        if not self.permissions:
            return False
        
        # Split permission key into parts (e.g., 'cases.create' -> ['cases', 'create'])
        parts = permission_key.split('.')
        current_level = self.permissions
        
        for part in parts:
            if isinstance(current_level, dict) and part in current_level:
                current_level = current_level[part]
            else:
                return False
        
        # Final value should be True to grant permission
        return current_level is True
    
    def is_origin_allowed(self, origin):
        """Check if the given origin is allowed for this API key."""
        if not self.allowed_origins:
            return True  # No restrictions
        
        return origin in self.allowed_origins
    
    def get_usage_percentage(self):
        """Get current usage as percentage of rate limit."""
        if self.rate_limit == 0:
            return 100
        return (self.current_usage / self.rate_limit) * 100


class APIRequestLogManager(models.Manager):
    """Manager for APIRequestLog with utility methods."""
    
    def log_request(self, api_key, request, response_data=None):
        """Create an API request log entry."""
        return self.create(
            api_key=api_key,
            tenant=api_key.tenant if api_key else None,
            user=getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
            endpoint=request.path,
            method=request.method,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            query_params=dict(request.GET),
            request_size=len(request.body) if hasattr(request, 'body') else 0,
            response_data=response_data or {}
        )
    
    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def recent(self, hours=24):
        """Get recent API requests within specified hours."""
        since = timezone.now() - timedelta(hours=hours)
        return self.filter(timestamp__gte=since)
    
    def by_tenant(self, tenant):
        """Get API requests for a specific tenant."""
        return self.filter(tenant=tenant)
    
    def by_endpoint(self, endpoint_pattern):
        """Get API requests matching endpoint pattern."""
        return self.filter(endpoint__icontains=endpoint_pattern)


class APIRequestLog(TimestampedModel):
    """
    Log of all API requests for monitoring, analytics, and debugging.
    
    Captures detailed information about each API request including timing,
    authentication details, and response information.
    """
    
    # Authentication context
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="API key used for this request (if any)"
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Tenant context for this request"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User making the request (if authenticated)"
    )
    
    # Request details
    endpoint = models.CharField(
        max_length=255,
        help_text="API endpoint path"
    )
    method = models.CharField(
        max_length=10,
        help_text="HTTP method (GET, POST, etc.)"
    )
    query_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Query parameters as JSON"
    )
    request_size = models.IntegerField(
        default=0,
        help_text="Size of request body in bytes"
    )
    
    # Client information
    ip_address = models.GenericIPAddressField(
        help_text="Client IP address"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Client user agent string"
    )
    
    # Response details
    status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="HTTP response status code"
    )
    response_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Time taken to process the request"
    )
    response_size = models.IntegerField(
        default=0,
        help_text="Size of response body in bytes"
    )
    response_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Response metadata (not full response body)"
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error message if request failed"
    )
    exception_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Exception class name if error occurred"
    )
    
    # Analytics metadata
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was made"
    )
    
    objects = APIRequestLogManager()
    
    class Meta:
        verbose_name = "API Request Log"
        verbose_name_plural = "API Request Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant', '-timestamp']),
            models.Index(fields=['api_key', '-timestamp']),
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-timestamp']),  # Most common query
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code or 'Pending'}"
    
    def is_successful(self):
        """Check if the request was successful (2xx status code)."""
        return self.status_code and 200 <= self.status_code < 300
    
    def is_client_error(self):
        """Check if the request had a client error (4xx status code)."""
        return self.status_code and 400 <= self.status_code < 500
    
    def is_server_error(self):
        """Check if the request had a server error (5xx status code)."""
        return self.status_code and 500 <= self.status_code < 600
    
    def get_response_time_ms(self):
        """Get response time in milliseconds."""
        if self.response_time:
            return self.response_time.total_seconds() * 1000
        return None


class APIKeyUsageStats(TimestampedModel):
    """
    Aggregated usage statistics for API keys.
    
    Provides daily/hourly rollups for analytics and billing purposes.
    """
    
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        related_name='usage_stats'
    )
    date = models.DateField(
        help_text="Date for this usage summary"
    )
    hour = models.IntegerField(
        null=True,
        blank=True,
        help_text="Hour of day (0-23) for hourly stats, null for daily stats"
    )
    
    # Usage metrics
    total_requests = models.IntegerField(
        default=0,
        help_text="Total number of requests"
    )
    successful_requests = models.IntegerField(
        default=0,
        help_text="Number of successful requests (2xx)"
    )
    failed_requests = models.IntegerField(
        default=0,
        help_text="Number of failed requests (4xx, 5xx)"
    )
    total_bytes_transferred = models.BigIntegerField(
        default=0,
        help_text="Total bytes in requests and responses"
    )
    
    # Performance metrics
    avg_response_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Average response time"
    )
    max_response_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Maximum response time"
    )
    
    class Meta:
        verbose_name = "API Key Usage Stats"
        verbose_name_plural = "API Key Usage Stats"
        unique_together = [['api_key', 'date', 'hour']]
        ordering = ['-date', '-hour']
        indexes = [
            models.Index(fields=['api_key', '-date']),
            models.Index(fields=['date', 'hour']),
        ]
    
    def __str__(self):
        period = f"{self.date}"
        if self.hour is not None:
            period += f" {self.hour:02d}:00"
        return f"{self.api_key.name} - {period}"