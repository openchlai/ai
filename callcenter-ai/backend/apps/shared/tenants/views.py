"""
Tenants App Views

Provides comprehensive views for tenant management including:
- Platform admin views (cross-tenant management)
- Tenant self-management views
- Public views (invitation acceptance, etc.)
- Bulk operations and utilities
"""

import re
import uuid
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.db.models import Q, Count, Sum
from django.db import transaction
from django.http import Http404
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import status, permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.conf import settings
from .models import Tenant, Domain, TenantInvitation, TenantSettings
from .serializers import (
    TenantListSerializer, TenantDetailSerializer, TenantCreateSerializer,
    TenantPublicSerializer, DomainSerializer, TenantInvitationSerializer,
    TenantInvitationAcceptSerializer, TenantSettingsSerializer,
    BulkTenantActionSerializer
)

User = get_user_model()


# Custom Permissions (will be moved to accounts app later)
class IsPlatformAdmin(permissions.BasePermission):
    """Permission for platform administrators only."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'is_platform_admin', request.user.is_superuser)
        )


class IsTenantOwnerOrAdmin(permissions.BasePermission):
    """Permission for tenant owners and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For now, allow tenant owners and superusers
        # This will be enhanced when accounts app is available
        if hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.is_superuser
        elif hasattr(obj, 'tenant'):
            return obj.tenant.owner == request.user or request.user.is_superuser
        return request.user.is_superuser


class TenantPagination(PageNumberPagination):
    """Custom pagination for tenant lists."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Platform Admin Views (Cross-tenant management)

class PlatformTenantViewSet(ModelViewSet):
    """
    Platform admin viewset for managing all tenants.
    Simplified to handle ONLY tenant creation - user management is handled by accounts app.
    """
    
    queryset = Tenant.objects.all().select_related('owner').annotate(
        user_count=Count('memberships', distinct=True),
        domain_count=Count('domains', distinct=True)
    )
    permission_classes = [IsPlatformAdmin]
    pagination_class = TenantPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sector', 'subscription_plan', 'is_active', 'require_2fa']
    search_fields = ['name', 'subdomain', 'primary_contact_email', 'owner__email']
    ordering_fields = ['name', 'created_at', 'subscription_expires_at', 'user_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TenantListSerializer
        elif self.action == 'create':
            return TenantCreateSerializer
        else:
            return TenantDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create tenant for an existing user.
        User must already exist - no user creation here.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract owner information from the validated data
        owner_email = serializer.validated_data.get('owner_email')
        if not owner_email:
            return Response(
                {'error': 'owner_email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Step 1: Find the existing owner user
                try:
                    owner_user = User.objects.get(email=owner_email)
                except User.DoesNotExist:
                    return Response(
                        {
                            'error': f'User with email {owner_email} not found',
                            'suggestion': 'Create the user account first using the accounts API, then create the tenant',
                            'accounts_endpoint': '/api/v1/auth/signup/ or /api/platform/users/'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Step 2: Add owner to the validated data
                serializer.validated_data['owner'] = owner_user
                
                # Step 3: Create the tenant
                tenant = self.perform_create(serializer)
                
                # Step 4: Create default domain
                domain = self._create_default_domain(tenant)
                
                # Step 5: Set up tenant membership and roles
                self._setup_tenant_membership(tenant, owner_user)
                
                # Step 6: Send notification email
                self._send_tenant_ready_email(owner_user, tenant)
                
                # Step 7: Prepare response data
                response_data = {
                    'tenant': TenantDetailSerializer(tenant).data,
                    'owner': {
                        'id': str(owner_user.id),
                        'email': owner_user.email,
                        'name': owner_user.get_full_name()
                    },
                    'domain': {
                        'domain': domain.domain,
                        'is_primary': domain.is_primary,
                        'tenant_url': f"https://{domain.domain}"
                    },
                    'message': f'Tenant successfully created for existing user {owner_email}',
                    'next_steps': self._get_next_steps(tenant)
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {
                    'error': 'Failed to create tenant',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _create_default_domain(self, tenant):
        """Create the default domain for the tenant."""
        domain_name = f"{tenant.subdomain}.localhost"  # Replace with your domain
        
        domain, created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={
                'tenant': tenant,
                'is_primary': True,
                'is_custom': False,
                'is_verified': True  # Auto-verify subdomains
            }
        )
        
        return domain
    
    def _setup_tenant_membership(self, tenant, owner_user):
        """
        Set up tenant membership and roles for the owner.
        This will be enhanced when the accounts app is integrated.
        """
        # TODO: This will be implemented when TenantMembership model is available
        # TenantMembership.objects.create(
        #     user=owner_user,
        #     tenant=tenant,
        #     role='owner',
        #     is_active=True
        # )
        pass
    
    def _send_tenant_ready_email(self, user, tenant):
        from django.core.mail import send_mail
        """
        Send tenant ready notification to user.
        This will be enhanced when email service is available.
        """
        # TODO: Implement actual email sending
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@bitz-itc.com')
            subject = f"Your new tenant '{tenant.name}' is ready!"
            message = f"""
            Hi {user.get_full_name()},
            Your new tenant '{tenant.name}' has been successfully created.
            You can access it at: https://{tenant.subdomain}.localhost
            Please configure your tenant settings and invite team members.
            If you have any questions, feel free to contact support.
            Best regards,
            The Bitz ITC Team
            """
            send_mail(subject, message, from_email, [user.email])  
            print(f"Tenant ready email sent to {user.email} for tenant {tenant.name}")
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Failed to send tenant ready email: {str(e)}")
            raise
    
    def _get_next_steps(self, tenant):
        """Return next steps for the created tenant."""
        return [
            f"Tenant '{tenant.name}' is ready at https://{tenant.subdomain}.localhost",
            "Owner can now access their tenant dashboard",
            "Configure tenant settings and invite team members",
            "Set up communication channels and workflows"
        ]
    
    def perform_create(self, serializer):
        """Create tenant with audit logging."""
        tenant = serializer.save()
        
        # Create audit log entry when core.models is available
        # TODO: Add audit logging when AuditLog model is available
        
        return tenant
    
    @action(detail=False, methods=['get'])
    def user_lookup(self, request):
        """
        Helper endpoint to look up users for tenant creation.
        Helps admins find existing users before creating tenants.
        """
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'email parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            return Response({
                'found': True,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.get_full_name(),
                    'is_active': user.is_active,
                    'date_joined': user.date_joined
                },
                'existing_tenants': [
                    {
                        'id': str(tenant.id),
                        'name': tenant.name,
                        'subdomain': tenant.subdomain,
                        'role': 'owner' if tenant.owner == user else 'member'
                    }
                    for tenant in user.owned_tenants.all()  # Add related tenants when membership model exists
                ]
            })
        except User.DoesNotExist:
            return Response({
                'found': False,
                'message': f'No user found with email {email}',
                'suggestion': 'Create user first using /api/platform/users/ or /api/v1/auth/signup/'
            })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on multiple tenants."""
        serializer = BulkTenantActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tenant_ids = serializer.validated_data['tenant_ids']
        action_type = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        tenants = Tenant.objects.filter(schema_name__in=tenant_ids)
        results = {'success': [], 'errors': []}
        
        with transaction.atomic():
            for tenant in tenants:
                try:
                    if action_type == 'activate':
                        tenant.is_active = True
                        tenant.save()
                        results['success'].append(f"Activated {tenant.name}")
                    
                    elif action_type == 'deactivate':
                        tenant.is_active = False
                        tenant.save()
                        results['success'].append(f"Deactivated {tenant.name}")
                    
                    elif action_type == 'extend_trial':
                        days = serializer.validated_data.get('trial_extension_days', 7)
                        if tenant.trial_ends_at:
                            tenant.trial_ends_at += timedelta(days=days)
                            tenant.save()
                            results['success'].append(f"Extended trial for {tenant.name} by {days} days")
                        else:
                            results['errors'].append(f"{tenant.name} is not on trial")
                    
                    elif action_type == 'change_plan':
                        new_plan = serializer.validated_data['subscription_plan']
                        old_plan = tenant.subscription_plan
                        tenant.subscription_plan = new_plan
                        tenant.save()
                        results['success'].append(f"Changed {tenant.name} from {old_plan} to {new_plan}")
                
                except Exception as e:
                    results['errors'].append(f"Error with {tenant.name}: {str(e)}")
        
        return Response({
            'message': f"Bulk action '{action_type}' completed",
            'results': results,
            'reason': reason
        })
    
    @action(detail=True, methods=['post'])
    def verify_domains(self, request, pk=None):
        """Verify all domains for a tenant."""
        tenant = self.get_object()
        domains = tenant.domains.filter(verified_at__isnull=True)
        
        verified_count = 0
        for domain in domains:
            domain.mark_as_verified()
            verified_count += 1
        
        return Response({
            'message': f"Verified {verified_count} domain(s) for {tenant.name}",
            'verified_domains': [d.domain for d in domains]
        })
    
    @action(detail=True, methods=['get'])
    def usage_report(self, request, pk=None):
        """Get detailed usage report for a tenant."""
        tenant = self.get_object()
        
        usage_data = {
            'tenant': TenantListSerializer(tenant).data,
            'usage_stats': tenant.get_usage_stats(),
            'subscription_info': {
                'plan': tenant.subscription_plan,
                'is_trial': tenant.is_trial,
                'trial_days_remaining': tenant.trial_days_remaining,
                'subscription_expires_at': tenant.subscription_expires_at,
                'is_expired': tenant.is_subscription_expired
            },
            'limits': {
                'max_users': tenant.max_users,
                'max_storage_mb': tenant.max_storage_mb,
                'max_monthly_calls': tenant.max_monthly_calls,
                'max_monthly_sms': tenant.max_monthly_sms
            },
            'domains': [
                {
                    'domain': d.domain,
                    'is_primary': d.is_primary,
                    'is_verified': d.is_verified,
                    'is_custom': d.is_custom
                }
                for d in tenant.domains.all()
            ]
        }
        
        return Response(usage_data)
    
    @action(detail=False, methods=['get'])
    def platform_statistics(self, request):
        """Get platform-wide statistics."""
        stats = {
            'total_tenants': Tenant.objects.count(),
            'active_tenants': Tenant.objects.filter(is_active=True).count(),
            'trial_tenants': Tenant.objects.filter(subscription_plan='trial').count(),
            'expired_trials': Tenant.objects.filter(
                subscription_plan='trial',
                trial_ends_at__lt=timezone.now()
            ).count(),
            'tenants_by_sector': dict(
                Tenant.objects.values_list('sector').annotate(
                    count=Count('id')
                )
            ),
            'tenants_by_plan': dict(
                Tenant.objects.values_list('subscription_plan').annotate(
                    count=Count('id')
                )
            ),
            'recent_signups': Tenant.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }
        
        return Response(stats)


class PlatformDomainViewSet(ModelViewSet):
    """
    Platform admin viewset for managing all domains.
    Clean domain management without user creation complexity.
    """
    
    queryset = Domain.objects.all().select_related('tenant')
    serializer_class = DomainSerializer
    permission_classes = [IsPlatformAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_primary', 'is_custom', 'tenant']
    search_fields = ['domain', 'tenant__name']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def bulk_verify(self, request):
        """Bulk verify domains."""
        domain_ids = request.data.get('domain_ids', [])
        if not domain_ids:
            return Response(
                {'error': 'No domain IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        domains = Domain.objects.filter(id__in=domain_ids, verified_at__isnull=True)
        verified_count = 0
        
        for domain in domains:
            domain.mark_as_verified()
            verified_count += 1
        
        return Response({
            'message': f"Verified {verified_count} domain(s)",
            'verified_domains': [d.domain for d in domains]
        })
    
    @action(detail=True, methods=['post'])
    def verify_dns(self, request, pk=None):
        """Verify DNS configuration for a custom domain."""
        domain = self.get_object()
        
        if not domain.is_custom:
            return Response(
                {'error': 'DNS verification only applies to custom domains'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement actual DNS verification logic
        # This would check CNAME records, etc.
        
        # For now, just mark as verified
        domain.mark_as_verified()
        
        return Response({
            'message': f'Domain {domain.domain} verified successfully',
            'domain': DomainSerializer(domain).data
        })
# Tenant Self-Management Views

class TenantSelfManagementViewSet(ModelViewSet):
    """
    Viewset for tenant owners/admins to manage their own tenant.
    """
    
    serializer_class = TenantDetailSerializer
    permission_classes = [IsTenantOwnerOrAdmin]
    
    def get_queryset(self):
        """Return only the user's own tenants."""
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.filter(owner=self.request.user)
    
    def get_object(self):
        """Get tenant object with permission check."""
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
    
    @action(detail=True, methods=['get'])
    def settings(self, request, pk=None):
        """Get all settings for this tenant."""
        tenant = self.get_object()
        settings = TenantSettings.objects.filter(tenant=tenant)
        serializer = TenantSettingsSerializer(settings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_branding(self, request, pk=None):
        """Update tenant branding settings."""
        tenant = self.get_object()
        branding_data = request.data.get('branding_settings', {})
        
        # Validate branding data structure
        allowed_keys = ['logo_url', 'primary_color', 'secondary_color', 'font_family', 'custom_css']
        filtered_branding = {k: v for k, v in branding_data.items() if k in allowed_keys}
        
        tenant.branding_settings.update(filtered_branding)
        tenant.save(update_fields=['branding_settings'])
        
        return Response({
            'message': 'Branding updated successfully',
            'branding_settings': tenant.branding_settings
        })
    
    @action(detail=True, methods=['post'])
    def toggle_feature(self, request, pk=None):
        """Enable or disable a feature for this tenant."""
        tenant = self.get_object()
        feature_name = request.data.get('feature_name')
        enabled = request.data.get('enabled', True)
        
        if not feature_name:
            return Response(
                {'error': 'feature_name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if enabled:
            tenant.enable_feature(feature_name)
        else:
            tenant.disable_feature(feature_name)
        
        return Response({
            'message': f"Feature '{feature_name}' {'enabled' if enabled else 'disabled'}",
            'feature_flags': tenant.feature_flags
        })


class TenantInvitationViewSet(ModelViewSet):
    """
    Viewset for managing tenant invitations.
    """
    
    serializer_class = TenantInvitationSerializer
    permission_classes = [IsTenantOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'role_name']
    search_fields = ['email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return invitations for user's tenants only."""
        if self.request.user.is_superuser:
            return TenantInvitation.objects.all().select_related(
                'tenant', 'invited_by', 'accepted_by', 'revoked_by'
            )
        
        user_tenants = Tenant.objects.filter(owner=self.request.user)
        return TenantInvitation.objects.filter(
            tenant__in=user_tenants
        ).select_related('tenant', 'invited_by', 'accepted_by', 'revoked_by')
    
    def perform_create(self, serializer):
        """Create invitation with proper user context."""
        serializer.save(invited_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send reminder email for this invitation."""
        invitation = self.get_object()
        
        if not invitation.is_pending:
            return Response(
                {'error': 'Can only send reminders for pending invitations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = invitation.send_reminder()
        
        if success:
            return Response({'message': 'Reminder sent successfully'})
        else:
            return Response(
                {'error': 'Failed to send reminder'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke this invitation."""
        invitation = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            invitation.revoke(user=request.user, reason=reason)
            return Response({'message': 'Invitation revoked successfully'})
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_send_reminders(self, request):
        """Send reminders for multiple invitations."""
        invitation_ids = request.data.get('invitation_ids', [])
        invitations = self.get_queryset().filter(
            id__in=invitation_ids,
            status='pending'
        )
        
        sent_count = 0
        for invitation in invitations:
            if invitation.send_reminder():
                sent_count += 1
        
        return Response({
            'message': f"Sent {sent_count} reminder(s)",
            'total_requested': len(invitation_ids)
        })


class TenantSettingsViewSet(ModelViewSet):
    """
    Viewset for managing tenant settings.
    """
    
    serializer_class = TenantSettingsSerializer
    permission_classes = [IsTenantOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'setting_type', 'is_sensitive', 'is_system']
    search_fields = ['key', 'name', 'description']
    
    def get_queryset(self):
        """Return settings for user's tenants only."""
        if self.request.user.is_superuser:
            return TenantSettings.objects.all().select_related('tenant')
        
        user_tenants = Tenant.objects.filter(owner=self.request.user)
        return TenantSettings.objects.filter(
            tenant__in=user_tenants
        ).select_related('tenant')
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get settings grouped by category."""
        queryset = self.get_queryset()
        tenant_id = request.query_params.get('tenant')
        
        if tenant_id:
            queryset = queryset.filter(tenant__schema_name=tenant_id)
        
        # Group by category
        categories = {}
        for setting in queryset:
            if setting.category not in categories:
                categories[setting.category] = []
            categories[setting.category].append(
                TenantSettingsSerializer(setting).data
            )
        
        return Response(categories)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Update multiple settings at once."""
        settings_data = request.data.get('settings', [])
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for setting_data in settings_data:
                try:
                    setting_id = setting_data.get('id')
                    if not setting_id:
                        continue
                    
                    setting = self.get_queryset().get(id=setting_id)
                    serializer = TenantSettingsSerializer(
                        setting, 
                        data=setting_data, 
                        partial=True
                    )
                    
                    if serializer.is_valid():
                        serializer.save(updated_by=request.user)
                        updated_count += 1
                    else:
                        errors.append({
                            'setting_id': setting_id,
                            'errors': serializer.errors
                        })
                
                except TenantSettings.DoesNotExist:
                    errors.append({
                        'setting_id': setting_data.get('id'),
                        'errors': 'Setting not found'
                    })
        
        return Response({
            'message': f"Updated {updated_count} setting(s)",
            'errors': errors
        })


# Tenant Creation Endpoint

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tenant(request):
    """
    Authenticated user creates a new tenant.
    User becomes the owner of the created tenant.
    
    Endpoint: POST /api/v1/tenants/
    
    Expected payload:
    {
        "name": "My New Company",
        "subdomain": "mynewcompany",
        "sector": "healthcare",
        "description": "Optional description"
    }
    """
    
    try:
        # Step 1: Validate input data
        validation_result = _validate_tenant_data(request.data)
        if not validation_result['valid']:
            return Response(
                {'error': 'Validation failed', 'details': validation_result['errors']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = validation_result['data']
        user = request.user
        
        with transaction.atomic():
            # Step 2: Check if subdomain is available
            if Tenant.objects.filter(subdomain=data['subdomain']).exists():
                return Response(
                    {'error': f'Subdomain "{data["subdomain"]}" is already taken'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 3: Check user's tenant limits (if any)
            user_tenant_count = Tenant.objects.filter(owner=user).count()
            max_tenants_per_user = 5  # Configure this based on your business rules
            
            if user_tenant_count >= max_tenants_per_user:
                return Response(
                    {
                        'error': f'Maximum tenant limit reached ({max_tenants_per_user})',
                        'current_tenants': user_tenant_count,
                        'suggestion': 'Contact support to increase your limit'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Step 4: Create the tenant
            tenant = _create_tenant_for_user(data, user)
            
            # Step 5: Create the default domain
            domain = _create_default_domain(tenant)
            
            # Step 6: Set up tenant membership and roles
            _setup_tenant_ownership(tenant, user)
            
            # Step 7: Send confirmation email
            _send_tenant_created_email(user, tenant)
            
            # Step 8: Prepare success response
            response_data = {
                'message': f'Tenant "{tenant.name}" created successfully!',
                'tenant': {
                    'id': str(tenant.id),
                    'name': tenant.name,
                    'subdomain': tenant.subdomain,
                    'sector': tenant.sector,
                    'description': tenant.description,
                    'is_trial': tenant.is_trial,
                    'trial_days_remaining': tenant.trial_days_remaining,
                    'subscription_plan': tenant.subscription_plan,
                    'created_at': tenant.created_at
                },
                'domain': {
                    'domain': domain.domain,
                    'is_primary': domain.is_primary,
                    'tenant_url': f"https://{domain.domain}"
                },
                'owner': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.get_full_name()
                },
                'next_steps': [
                    f'Visit your new tenant at https://{domain.domain}',
                    'Complete your tenant setup and configuration',
                    'Invite team members to join your organization',
                    'Configure communication channels and workflows',
                    'Set up your first case categories and workflows'
                ]
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {
                'error': 'Failed to create tenant',
                'message': 'An unexpected error occurred. Please try again.',
                'details': str(e) if settings.DEBUG else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_tenants(request):
    """
    List all tenants owned or accessible by the authenticated user.
    
    Endpoint: GET /api/v1/tenants/
    """
    
    user = request.user
    
    # Get tenants owned by user
    owned_tenants = Tenant.objects.filter(owner=user).select_related('owner')
    
    # TODO: Get tenants where user is a member (when TenantMembership model is available)
    # member_tenants = Tenant.objects.filter(memberships__user=user, memberships__is_active=True)
    
    # For now, just return owned tenants
    tenants_data = []
    
    for tenant in owned_tenants:
        tenant_data = {
            'id': str(tenant.id),
            'name': tenant.name,
            'subdomain': tenant.subdomain,
            'sector': tenant.sector,
            'description': tenant.description,
            'role': 'owner',  # User's role in this tenant
            'is_active': tenant.is_active,
            'subscription_plan': tenant.subscription_plan,
            'is_trial': tenant.is_trial,
            'trial_days_remaining': tenant.trial_days_remaining,
            'created_at': tenant.created_at,
            'tenant_url': f"https://{tenant.subdomain}.localhost",
            'primary_domain': tenant.domains.filter(is_primary=True).first().domain if tenant.domains.filter(is_primary=True).exists() else None
        }
        tenants_data.append(tenant_data)
    
    return Response({
        'count': len(tenants_data),
        'tenants': tenants_data,
        'limits': {
            'max_tenants': 5,  # Configure based on user's plan
            'current_count': len(tenants_data),
            'can_create_more': len(tenants_data) < 5
        }
    })


def _validate_tenant_data(data):
    """
    Validate tenant creation data.
    
    Returns:
        dict: {'valid': bool, 'data': dict, 'errors': list}
    """
    errors = []
    validated_data = {}
    
    # Required fields
    required_fields = ['name', 'subdomain']
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} is required')
        else:
            validated_data[field] = data[field].strip()
    
    if errors:
        return {'valid': False, 'errors': errors, 'data': None}
    
    # Validate organization name
    if len(validated_data['name']) < 2:
        errors.append('Organization name must be at least 2 characters')
    
    if len(validated_data['name']) > 100:
        errors.append('Organization name cannot exceed 100 characters')
    
    # Validate subdomain format
    subdomain = validated_data['subdomain'].lower()
    if not re.match(r'^[a-z0-9-]{3,30}$', subdomain):
        errors.append('Subdomain must be 3-30 characters, lowercase letters, numbers, and hyphens only')
    
    if subdomain.startswith('-') or subdomain.endswith('-'):
        errors.append('Subdomain cannot start or end with a hyphen')
    
    # Reserved subdomains
    reserved_subdomains = [
        'www', 'api', 'admin', 'support', 'help', 'docs', 'blog', 'mail',
        'app', 'dashboard', 'portal', 'console', 'platform', 'system'
    ]
    if subdomain in reserved_subdomains:
        errors.append(f'Subdomain "{subdomain}" is reserved')
    
    validated_data['subdomain'] = subdomain
    
    # Optional fields with validation
    validated_data['sector'] = data.get('sector', 'general')
    validated_data['description'] = data.get('description', '').strip()[:500]  # Limit description length
    
    # Validate sector if provided
    valid_sectors = [
        'general', 'healthcare', 'education', 'government', 'nonprofit',
        'customer_service', 'helpline', 'support_center', 'call_center'
    ]
    if validated_data['sector'] not in valid_sectors:
        errors.append(f'Invalid sector. Must be one of: {", ".join(valid_sectors)}')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'data': validated_data if len(errors) == 0 else None
    }


def _create_tenant_for_user(data, user):
    """Create the tenant with the authenticated user as owner."""
    from datetime import timedelta
    from django.utils import timezone
    
    tenant = Tenant.objects.create(
        name=data['name'],
        subdomain=data['subdomain'],
        schema_name=data['subdomain'],  # Use subdomain as schema name
        owner=user,
        sector=data['sector'],
        description=data['description'],
        subscription_plan='trial',  # Start with trial by default
        is_active=True,
        primary_contact_email=user.email,
        # Set trial period (e.g., 14 days)
        trial_ends_at=timezone.now() + timedelta(days=14)
    )
    return tenant


def _create_default_domain(tenant):
    """Create the default domain for the tenant."""
    domain_name = f"{tenant.subdomain}.localhost"  # Replace with your actual domain
    
    domain = Domain.objects.create(
        domain=domain_name,
        tenant=tenant,
        is_primary=True,
        is_custom=False,
        # is_verified=True  # Auto-verify subdomains
    )
    return domain


def _setup_tenant_ownership(tenant, user):
    """
    Set up tenant ownership and default roles.
    This will be enhanced when the accounts app is integrated.
    """
    # TODO: Create TenantMembership and default roles when accounts app is available
    # TenantMembership.objects.create(
    #     user=user,
    #     tenant=tenant,
    #     role='owner',
    #     is_active=True
    # )
    pass


def _send_tenant_created_email(user, tenant):
    """
    Send tenant created confirmation email.
    This will be implemented when email service is available.
    """
    from django.core.mail import send_mail

    """
    Send tenant created confirmation email to the user.
    This is a placeholder function to be implemented when email service is available.
    """
    try:

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@bitz-itc.com')
        subject = f"Your new tenant '{tenant.name}' is ready!"
        message = f"""
        Hi {user.get_full_name()},
        Your new tenant '{tenant.name}' has been successfully created.
        You can access it at: https://{tenant.subdomain}.localhost
        Please configure your tenant settings and invite team members.
        If you have any questions, feel free to contact support.
        Best regards,
        The Bitz ITC Team
        """
        send_mail(subject, message, from_email, [user.email])
        print(f"Tenant created email sent to {user.email} for tenant {tenant.name}")
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Failed to send tenant created email: {str(e)}")
        raise
 


# Additional utility endpoint for subdomain validation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_subdomain_availability(request):
    """
    Check if a subdomain is available for the authenticated user.
    
    Endpoint: POST /api/v1/tenants/check-subdomain/
    
    Expected payload:
    {
        "subdomain": "mynewcompany"
    }
    """
    subdomain = request.data.get('subdomain', '').strip().lower()
    
    if not subdomain:
        return Response(
            {'error': 'Subdomain is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Format validation
    if not re.match(r'^[a-z0-9-]{3,30}$', subdomain):
        return Response({
            'available': False,
            'error': 'Subdomain must be 3-30 characters, lowercase letters, numbers, and hyphens only'
        })
    
    if subdomain.startswith('-') or subdomain.endswith('-'):
        return Response({
            'available': False,
            'error': 'Subdomain cannot start or end with a hyphen'
        })
    
    # Reserved subdomains
    reserved_subdomains = [
        'www', 'api', 'admin', 'support', 'help', 'docs', 'blog', 'mail',
        'app', 'dashboard', 'portal', 'console', 'platform', 'system'
    ]
    if subdomain in reserved_subdomains:
        return Response({
            'available': False,
            'error': f'Subdomain "{subdomain}" is reserved'
        })
    
    # Check availability
    is_available = not Tenant.objects.filter(subdomain=subdomain).exists()
    
    return Response({
        'available': is_available,
        'subdomain': subdomain,
        'message': 'Subdomain is available' if is_available else 'Subdomain is already taken',
        'suggestion': f'https://{subdomain}.localhost' if is_available else None
    })

# Public Views (No authentication required)

@api_view(['GET'])
@permission_classes([AllowAny])
def tenant_public_info(request, subdomain):
    """
    Get public information about a tenant by subdomain.
    Used for branding and public-facing information.
    """
    try:
        tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
        serializer = TenantPublicSerializer(tenant)
        return Response(serializer.data)
    except Tenant.DoesNotExist:
        return Response(
            {'error': 'Tenant not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def invitation_details(request, token):
    """
    Get invitation details by token (for invitation acceptance page).
    """
    try:
        invitation = TenantInvitation.objects.select_related('tenant').get(token=token)
        
        if not invitation.is_pending:
            return Response(
                {'error': 'Invitation is no longer valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invitation.is_expired:
            return Response(
                {'error': 'Invitation has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'tenant_name': invitation.tenant.name,
            'email': invitation.email,
            'role_name': invitation.role_name,
            'invited_by': invitation.invited_by.get_full_name() or invitation.invited_by.email,
            'message': invitation.message,
            'expires_at': invitation.expires_at,
            'days_until_expiry': invitation.days_until_expiry
        })
    
    except TenantInvitation.DoesNotExist:
        return Response(
            {'error': 'Invalid invitation token'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invitation(request):
    """
    Accept a tenant invitation.
    """
    serializer = TenantInvitationAcceptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    
    try:
        invitation = TenantInvitation.objects.select_related('tenant').get(token=token)
        
        # Accept the invitation
        invitation.accept(user=request.user)
        
        # Note: Creating TenantMembership would happen here
        # when accounts app is available
        
        return Response({
            'message': 'Invitation accepted successfully',
            'tenant': {
                'name': invitation.tenant.name,
                'subdomain': invitation.tenant.subdomain,
                'url': invitation.tenant.get_absolute_url()
            },
            'role': invitation.role_name
        })
    
    except TenantInvitation.DoesNotExist:
        return Response(
            {'error': 'Invalid invitation token'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except DjangoValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# Health Check and Utility Views

@api_view(['GET'])
@permission_classes([AllowAny])
@method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
def health_check(request):
    """
    Basic health check endpoint.
    """
    try:
        # Simple database connectivity check
        tenant_count = Tenant.objects.count()
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'tenant_count': tenant_count,
            'database': 'connected'
        })
    
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'error': str(e),
            'database': 'error'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([IsPlatformAdmin])
def system_status(request):
    """
    Detailed system status for platform administrators.
    """
    try:
        now = timezone.now()
        
        # Basic statistics
        total_tenants = Tenant.objects.count()
        active_tenants = Tenant.objects.filter(is_active=True).count()
        trial_tenants = Tenant.objects.filter(subscription_plan='trial').count()
        
        # Expiring trials (next 7 days)
        expiring_trials = Tenant.objects.filter(
            subscription_plan='trial',
            trial_ends_at__lte=now + timedelta(days=7),
            trial_ends_at__gt=now
        ).count()
        
        # Expired trials
        expired_trials = Tenant.objects.filter(
            subscription_plan='trial',
            trial_ends_at__lte=now
        ).count()
        
        # Pending invitations
        pending_invitations = TenantInvitation.objects.filter(
            status='pending',
            expires_at__gt=now
        ).count()
        
        # Recent signups (last 24 hours)
        recent_signups = Tenant.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        
        return Response({
            'status': 'healthy',
            'timestamp': now.isoformat(),
            'statistics': {
                'total_tenants': total_tenants,
                'active_tenants': active_tenants,
                'trial_tenants': trial_tenants,
                'expiring_trials': expiring_trials,
                'expired_trials': expired_trials,
                'pending_invitations': pending_invitations,
                'recent_signups_24h': recent_signups
            },
            'alerts': {
                'expired_trials': expired_trials > 0,
                'expiring_trials_soon': expiring_trials > 0
            }
        })
    
    except Exception as e:
        return Response({
            'status': 'error',
            'timestamp': now.isoformat(),
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# Subdomain validation utility

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_subdomain(request):
    """
    Validate subdomain availability and format.
    Public endpoint for tenant creation forms.
    """
    subdomain = request.data.get('subdomain', '').lower().strip()
    
    if not subdomain:
        return Response({
            'valid': False,
            'error': 'Subdomain is required'
        })
    
    # Use the same validation as in serializers
    try:
        from .serializers import TenantDetailSerializer
        serializer = TenantDetailSerializer()
        validated_subdomain = serializer.validate_subdomain(subdomain)
        
        # Check if already exists
        if Tenant.objects.filter(subdomain=validated_subdomain).exists():
            return Response({
                'valid': False,
                'error': 'Subdomain is already taken'
            })
        
        return Response({
            'valid': True,
            'subdomain': validated_subdomain,
            'url': f"https://{validated_subdomain}.murima.com"
        })
    
    except ValidationError as e:
        return Response({
            'valid': False,
            'error': str(e.detail[0]) if e.detail else 'Invalid subdomain'
        })