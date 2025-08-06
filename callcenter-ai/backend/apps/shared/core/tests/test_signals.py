from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import AuditLog
from core.signals import log_save, log_delete

User = get_user_model()

class SignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a simple model for testing signals
        class TestModel(models.Model):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        self.test_model = TestModel.objects.create(name="Test Object")
        
    def test_save_signal(self):
        log_save(sender=self.test_model.__class__, instance=self.test_model, created=True)
        
        log = AuditLog.objects.first()
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.object_type, 'TestModel')
        
    def test_delete_signal(self):
        log_delete(sender=self.test_model.__class__, instance=self.test_model)
        
        log = AuditLog.objects.first()
        self.assertEqual(log.action, 'DELETE')
        self.assertEqual(log.object_type, 'TestModel')