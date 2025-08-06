# core/utils.py
from django.utils import timezone
from .models import AuditLog
from django.http import HttpRequest

def log_action(
    action: str,
    request: HttpRequest = None,
    user=None,
    obj=None,
    metadata: dict = None
) -> AuditLog:
    """Centralized logging function"""
    if request and hasattr(request, 'user'):
        user = user or request.user
    
    log = AuditLog(
        user=user,
        action=action,
        ip_address=request.META.get('REMOTE_ADDR') if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT') if request else None,
        object_type=obj.__class__.__name__ if obj else None,
        object_id=str(obj.id) if obj else None,
        metadata=metadata or {}
    )
    log.save()
    return log