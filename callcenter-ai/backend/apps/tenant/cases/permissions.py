from rest_framework.permissions import BasePermission

class CaseAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if obj.assigned_to == request.user:
            return True
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.has_perm('cases.view_case')
        return request.user.has_perm('cases.change_case')

class ProtectionCasePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.case_type.category in ['vac', 'gbv']:
            return request.user.has_perm('cases.handle_protection_cases')
        return True

class DocumentAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_confidential:
            return request.user.has_perm('cases.view_confidential_docs')
        return True