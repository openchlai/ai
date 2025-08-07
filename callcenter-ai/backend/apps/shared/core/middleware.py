import threading
from django.utils.deprecation import MiddlewareMixin

_user = threading.local()

def get_current_user():
    return getattr(_user, 'value', None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = getattr(request, 'user', None)
        response = self.get_response(request)
        _user.value = None
        return response

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            from apps.shared.core.utils import log_action
            log_action('REQUEST', request, metadata={
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code
            })
        return response

def get_audit_log_serializer():
    from apps.shared.core.serializers_auditlog import AuditLogSerializer
    return AuditLogSerializer
