from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import BaseModel, AuditLog
import uuid

User = get_user_model()

class BaseModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a simple concrete model for testing
        class TestModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        self.test_model = TestModel.objects.create(
            name="Test Object",
            created_by=self.user,
            updated_by=self.user
        )

    def test_uuid_primary_key(self):
        self.assertIsInstance(self.test_model.id, uuid.UUID)

    def test_timestamps(self):
        self.assertIsNotNone(self.test_model.created_at)
        self.assertIsNotNone(self.test_model.updated_at)

    def test_user_tracking(self):
        self.assertEqual(self.test_model.created_by, self.user)
        self.assertEqual(self.test_model.updated_by, self.user)

    def test_soft_delete(self):
        self.assertFalse(self.test_model.is_deleted)
        self.test_model.delete(user=self.user)
        self.test_model.refresh_from_db()
        self.assertTrue(self.test_model.is_deleted)
        self.assertIsNotNone(self.test_model.deleted_at)
        self.assertEqual(self.test_model.deleted_by, self.user)

class AuditLogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='audituser',
            password='auditpass123'
        )
        
    def test_audit_log_creation(self):
        log = AuditLog.objects.create(
            user=self.user,
            action='CREATE',
            object_type='TestModel',
            object_id=str(uuid.uuid4()),
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(log.timestamp)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'CREATE')