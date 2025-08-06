# System Core App

The **foundational backbone** of the platform providing consistent data patterns, automatic audit trails, and unified system behavior across all tenant applications.

## 🎯 Purpose

The core app ensures **every component** of the platform follows the same patterns for:
- **Data modeling** with automatic timestamps, user tracking, and soft deletes
- **Audit logging** with complete transparency and compliance
- **API consistency** with standardized serializers and responses
- **System management** with runtime configuration and error monitoring
- **Security patterns** with built-in permission frameworks

---

## 📦 What's Included

### **Abstract Base Models**
- `BaseModel` - Complete model with UUID, timestamps, user tracking, soft delete
- `TimestampedModel` - Just created_at/updated_at for reference data
- `UUIDModel` - UUID primary keys for security
- `UserTrackingModel` - created_by/updated_by fields
- `SoftDeleteModel` - Soft delete with restore capability

### **System Models**
- `AuditLog` - Comprehensive audit trail for all system actions
- `SystemConfiguration` - Runtime settings without code deployments
- `ErrorLog` - System error tracking with resolution management

### **Base Serializers**
- `BaseModelSerializer` - Automatic user tracking and consistent API responses
- `TimestampedModelSerializer` - For reference data
- `ReadOnlyBaseSerializer` - Read-only endpoints

### **Managers & QuerySets**
- `BaseModelManager` - Common queries (recent, created_by_user, etc.)
- `ActiveManager` - Automatically filters soft-deleted records
- `SystemConfigurationManager` - get_value()/set_value() helpers

### **Automatic Features**
- **Audit logging** via Django signals (no manual intervention)
- **System configuration** initialization on startup
- **Error logging** with request context
- **Django admin** interfaces for system management

---

## 🚀 Quick Start

### 1. **Model Inheritance** (Most Common)

```python
# apps/tenant/your_app/models.py
from apps.shared.core.models import BaseModel

class YourModel(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=50, default='active')
    
    class Meta:
        verbose_name = "Your Model"
        ordering = ['-created_at']

# You automatically get:
# - UUID primary key (id)
# - Timestamps (created_at, updated_at)
# - User tracking (created_by, updated_by)
# - Soft delete (is_deleted, deleted_at, deleted_by)
# - Automatic audit logging
```

### 2. **Serializer Inheritance**

```python
# apps/tenant/your_app/serializers.py
from apps.shared.core.serializers import BaseModelSerializer

class YourModelSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = YourModel
        fields = BaseModelSerializer.Meta.fields + [
            'title', 'description', 'status'
        ]

# You automatically get:
# - User tracking from request.user
# - Read-only timestamp fields
# - Consistent API response format
# - Soft delete field handling
```

### 3. **Manager Usage**

```python
# Query patterns
active_records = YourModel.objects.all()  # Excludes soft-deleted
all_records = YourModel.objects.with_deleted()  # Includes soft-deleted
deleted_only = YourModel.objects.deleted_only()  # Only soft-deleted

# Built-in methods
recent = YourModel.objects.recent(days=7)
by_user = YourModel.objects.created_by_user(user)
```

---

## 🏗️ Architecture & Design Principles

### **1. Consistency Above All**
Every app follows identical patterns ensuring the platform feels unified.

### **2. Audit Everything** 
Complete transparency with automatic logging of all actions without developer intervention.

### **3. Fail Gracefully**
System operations never break due to audit/logging failures - they log errors and continue.

### **4. Security First**
Built-in user tracking, permission patterns, and sensitive data protection.

### **5. Performance Aware**
Optimized queries, efficient patterns, and scalable designs.

---

## 🔧 Advanced Usage

### **Soft Delete Operations**

```python
# Soft delete with reason
instance.soft_delete(user=request.user)

# Restore deleted record
instance.restore()

# Query deleted records
deleted_items = YourModel.objects.deleted_only()

# Include deleted in queries
all_items = YourModel.objects.with_deleted()
```

### **Manual Audit Logging**

```python
from apps.shared.core.models import AuditLog
from django.contrib.contenttypes.models import ContentType

# For special business events
AuditLog.objects.create(
    user=request.user,
    tenant=request.tenant,
    action='TRANSFER',
    object_type=ContentType.objects.get_for_model(YourModel),
    object_id=str(instance.id),
    object_repr=str(instance),
    description="Custom business action performed",
    changes={'field': {'old': 'value1', 'new': 'value2'}},
    ip_address=get_client_ip(request),
    metadata={'custom_data': 'value'}
)
```

### **System Configuration**

```python
from apps.shared.core.models import SystemConfiguration

# Get configuration value
max_size = SystemConfiguration.objects.get_value(
    'max_file_upload_size', 
    default=5242880
)

# Set configuration value
SystemConfiguration.objects.set_value(
    'new_feature_enabled', 
    True, 
    user=request.user
)

# Get all configs for a category
email_configs = SystemConfiguration.objects.get_category_configs('email')
```

### **Error Logging**

```python
from apps.shared.core.models import ErrorLog

# Log errors with context
try:
    risky_operation()
except Exception as e:
    ErrorLog.objects.log_error(
        level='ERROR',
        message=str(e),
        exception_type=type(e).__name__,
        user=request.user,
        tenant=request.tenant,
        request=request,
        context={'operation': 'risky_operation', 'params': params}
    )
    raise
```

---

## 🎨 ViewSet Integration

### **Standard CRUD Pattern**

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from apps.shared.core.serializers import SoftDeleteActionSerializer

class YourModelViewSet(ModelViewSet):
    serializer_class = YourModelSerializer
    
    def get_queryset(self):
        # Automatically excludes soft-deleted records
        return YourModel.objects.select_related('created_by')
    
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Soft delete with optional reason."""
        instance = self.get_object()
        serializer = SoftDeleteActionSerializer(data=request.data)
        
        if serializer.is_valid():
            reason = serializer.validated_data.get('reason', '')
            instance.soft_delete(user=request.user)
            return Response({'status': 'deleted', 'reason': reason})
        
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted record."""
        instance = self.get_object()
        instance.restore()
        return Response({'status': 'restored'})
```

---

## 📊 Model Examples by Use Case

### **Business Entities** (Use BaseModel)

```python
# Cases, Contacts, Calls, Communications, etc.
class Case(BaseModel):
    case_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default='open')
    priority = models.CharField(max_length=20, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

### **Reference/Lookup Data** (Use TimestampedModel)

```python
# Categories, Priorities, Status choices, etc.
class CaseCategory(TimestampedModel):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#0066CC')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
```

### **Logging/Temporary Data** (Use UUIDModel or direct inheritance)

```python
# API logs, temporary tokens, etc.
class APIRequestLog(UUIDModel):
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.DurationField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

## 🔍 Automatic Audit Trail

The core app **automatically logs**:

### **Model Operations**
- ✅ CREATE - New record creation with all field values
- ✅ UPDATE - Field changes with old vs new values  
- ✅ DELETE - Both soft deletes and hard deletes
- ✅ User context - Who performed the action
- ✅ Request context - IP address, user agent, timestamp

### **Authentication Events**
- ✅ LOGIN - Successful user logins
- ✅ LOGOUT - User logouts
- ✅ LOGIN_FAILED - Failed login attempts for security

### **What Gets Logged**
- User who performed the action
- Tenant where action occurred
- Exact field changes (old value → new value)
- IP address and user agent
- Timestamp with timezone
- Custom metadata for business events

### **Example Audit Log Entry**
```json
{
    "id": "uuid-here",
    "created_at": "2025-01-15T10:30:00Z",
    "user": "john.doe",
    "tenant": "acme-corp",
    "action": "UPDATE",
    "object_type": "cases.Case",
    "object_id": "case-uuid",
    "object_repr": "Case #2025-001: Customer complaint",
    "changes": {
        "status": {"old": "open", "new": "in_progress"},
        "assigned_to": {"old": null, "new": "jane.smith"}
    },
    "description": "Update Case",
    "ip_address": "192.168.1.100",
    "metadata": {
        "model": "tenant_cases.Case",
        "timestamp": "2025-01-15T10:30:00Z"
    }
}
```

---

## ⚡ Performance Best Practices

### **QuerySet Optimizations**

```python
# ✅ GOOD - Optimized queries
cases = Case.objects.select_related(
    'assigned_to', 'category', 'created_by'
).prefetch_related(
    'comments', 'documents'
).filter(status='open')[:50]

# ❌ BAD - N+1 queries
cases = Case.objects.filter(status='open')
for case in cases:
    print(case.assigned_to.name)  # Database hit per case
```

### **Bulk Operations**

```python
from apps.shared.core.signals import DisableAuditing

# For bulk operations, temporarily disable auditing
with DisableAuditing():
    Case.objects.bulk_create(case_instances)
    Case.objects.bulk_update(cases, ['status'])
```

### **Manager Patterns**

```python
# Build on BaseModelManager for custom behavior
class CaseManager(BaseModelManager):
    def open(self):
        return self.filter(status='open')
    
    def urgent(self):
        return self.filter(priority='high')
    
    def by_status(self, status):
        return self.filter(status=status)

class Case(BaseModel):
    objects = CaseManager()
    
    # Usage:
    urgent_cases = Case.objects.urgent()
    open_cases = Case.objects.open()
```

---

## 🛡️ Security Features

### **Automatic User Tracking**
Every record automatically tracks who created and last modified it.

### **Soft Delete Protection**
Business data is never permanently deleted - only marked as deleted with timestamp and user.

### **Audit Trail Integrity**
Audit logs are read-only and cannot be modified through the application.

### **Sensitive Data Handling**
System configurations can be marked as sensitive and are hidden in API responses.

### **IP and User Agent Logging**
All actions are logged with request context for security monitoring.

---

## 🚫 Common Mistakes & Solutions

### **❌ Forgetting User Context**
```python
# BAD - No user tracking
instance = YourModel.objects.create(title="Test")

# GOOD - Use serializer or set manually  
serializer = YourModelSerializer(data=data, context={'request': request})
instance = serializer.save()  # Automatic user tracking
```

### **❌ Hard Deletes**
```python
# BAD - Permanent deletion, no audit trail
instance.delete()

# GOOD - Soft delete with audit trail
instance.soft_delete(user=request.user)
```

### **❌ Inconsistent Inheritance**
```python
# BAD - Mixing patterns
class ModelA(models.Model):  # No audit trail
    pass

class ModelB(BaseModel):     # Has audit trail
    pass

# GOOD - Consistent patterns
class ModelA(BaseModel):     # Audit trail
    pass

class ModelB(BaseModel):     # Audit trail  
    pass
```

### **❌ Ignoring Soft Delete**
```python
# BAD - Doesn't handle soft-deleted records
instances = YourModel.objects.all()  # Excludes soft-deleted (correct)
instance = YourModel.objects.get(id=uuid)  # May raise DoesNotExist for soft-deleted

# GOOD - Handle soft delete appropriately
instances = YourModel.objects.with_deleted()  # Include if needed
try:
    instance = YourModel.objects.get(id=uuid)
except YourModel.DoesNotExist:
    # Check if soft-deleted
    instance = YourModel.objects.with_deleted().get(id=uuid)
    if instance.is_deleted:
        # Handle soft-deleted case
        pass
```

---

## 🧪 Testing

### **Model Tests**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tenant.your_app.models import YourModel

User = get_user_model()

class YourModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_model_creation_with_audit(self):
        """Test BaseModel functionality."""
        instance = YourModel.objects.create(
            title="Test",
            created_by=self.user,
            updated_by=self.user
        )
        
        # Test BaseModel fields
        self.assertIsNotNone(instance.id)  # UUID
        self.assertIsNotNone(instance.created_at)
        self.assertEqual(instance.created_by, self.user)
        self.assertFalse(instance.is_deleted)
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        instance = YourModel.objects.create(
            title="Test",
            created_by=self.user,
            updated_by=self.user
        )
        
        instance.soft_delete(user=self.user)
        
        # Verify soft delete
        self.assertTrue(instance.is_deleted)
        self.assertIsNotNone(instance.deleted_at)
        self.assertEqual(instance.deleted_by, self.user)
        
        # Verify queryset behavior
        self.assertNotIn(instance, YourModel.objects.all())
        self.assertIn(instance, YourModel.objects.with_deleted())
```

### **Serializer Tests**

```python
from rest_framework.test import APITestCase
from apps.tenant.your_app.serializers import YourModelSerializer

class YourModelSerializerTest(APITestCase):
    def test_user_tracking_automatic(self):
        """Test automatic user tracking in serializer."""
        self.client.force_authenticate(user=self.user)
        
        data = {'title': 'Test', 'description': 'Test description'}
        serializer = YourModelSerializer(
            data=data, 
            context={'request': self.factory.post('/', data)}
        )
        
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        
        self.assertEqual(instance.created_by, self.user)
        self.assertEqual(instance.updated_by, self.user)
```

---

## 📋 System Configuration

### **Default Configurations**

The core app automatically creates these default configurations:

| Key | Description | Default Value |
|-----|-------------|---------------|
| `system_name` | Platform display name | "Murima Platform" |
| `max_file_upload_size` | File upload limit (bytes) | 10485760 (10MB) |
| `session_timeout_minutes` | User session timeout | 480 (8 hours) |
| `audit_retention_days` | Audit log retention | 2555 (7 years) |
| `error_log_retention_days` | Error log retention | 90 (3 months) |
| `enable_audit_logging` | Audit logging toggle | true |
| `maintenance_mode` | Maintenance mode flag | false |
| `api_rate_limit_per_minute` | API rate limiting | 1000 |

### **Using Configurations**

```python
# In your code
from apps.shared.core.models import SystemConfiguration

# Get value with default
timeout = SystemConfiguration.objects.get_value(
    'session_timeout_minutes', 
    default=480
)

# Set value
SystemConfiguration.objects.set_value(
    'new_feature_enabled', 
    True, 
    user=admin_user
)
```

---

## 🛠️ Django Admin

Access the Django admin interface to manage:

- **System Configurations** - Runtime settings
- **Audit Logs** - Read-only audit trail viewing  
- **Error Logs** - Error monitoring and resolution

Navigate to `/admin/` and look for the "Core" section.

---

## 🔧 Installation & Setup

### **1. Add to Django Settings**

```python
# settings.py
SHARED_APPS = [
    # ... other apps
    'apps.shared.core',
]

# If using django-tenants
TENANT_APPS = [
    # Your tenant apps that will use core models
]
```

### **2. Run Migrations**

```bash
python manage.py makemigrations core
python manage.py migrate
```

### **3. Create Superuser**

```bash
python manage.py createsuperuser
```

### **4. Verify Installation**

```python
# In Django shell
from apps.shared.core.models import SystemConfiguration
configs = SystemConfiguration.objects.all()
print(f"Found {configs.count()} default configurations")
```

---

## 📚 File Structure

```
apps/shared/core/
├── __init__.py
├── admin.py              # Django admin interfaces
├── apps.py              # App configuration
├── managers.py          # Custom managers and querysets
├── models.py            # Base models and system models
├── serializers.py       # Base serializers  
├── signals.py           # Automatic audit logging
├── migrations/          # Database migrations
└── README.md           # This file
```

---

## 🤝 Contributing

### **When Adding New Features**

1. **Follow existing patterns** - Consistency is key
2. **Add comprehensive tests** - Test all functionality
3. **Update documentation** - Keep README current
4. **Consider backward compatibility** - Don't break existing apps
5. **Performance impact** - Profile changes with large datasets

### **Code Standards**

- **Docstrings** - Document all public methods
- **Type hints** - Use where helpful
- **Error handling** - Graceful failure modes
- **Logging** - Use appropriate log levels
- **Security** - Always consider security implications

---

## 🆘 Troubleshooting

### **Common Issues**

#### **Audit logs not appearing**
- Check that signals are registered in `apps.py`
- Verify request context is available (middleware)
- Ensure tenant context is set

#### **Soft delete not working**
- Confirm model inherits from `BaseModel`
- Use `.all()` not `.filter()` for default active records
- Check manager configuration

#### **User tracking fields are None**
- Use serializers with request context
- Set user fields manually if not using serializers
- Verify request.user is authenticated

#### **Configuration values not found**
- Check migrations have run
- Verify default configurations were created
- Use `get_value()` with defaults

### **Debug Mode**

```python
import logging
logging.getLogger('murima.core').setLevel(logging.DEBUG)
```

---

## 📈 Roadmap

### **Completed** ✅
- Base models with audit trails
- Automatic signal-based logging
- System configuration management
- Django admin interfaces
- Base serializers and managers

### **In Progress** 🚧
- Permission framework (`permissions.py`)
- Utility functions (`utils.py`)
- Custom exceptions (`exceptions.py`)

### **Planned** 📅
- Middleware for request context
- API rate limiting
- Advanced audit analytics
- Configuration validation
- Health check endpoints

---

## 📞 Support

For questions or issues:

1. **Check this README** - Most common patterns are covered
2. **Review integration guide** - Detailed usage examples
3. **Check existing tests** - See how features are tested
4. **Team documentation** - Platform-specific guides
5. **Create issue** - For bugs or feature requests

---

## 📄 License

Part of the Murima Platform - Internal Use Only

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Maintainer**: Murima Development Team