from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from core.utils import log_action
from core.models import AuditLog

User = get_user_model()

class LogActionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.factory = RequestFactory()
        
    def test_log_action_with_request(self):
        request = self.factory.get('/test-path')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        log_action('READ', request, metadata={'path': '/test-path'})
        
        log = AuditLog.objects.first()
        self.assertEqual(log.action, 'READ')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.metadata['path'], '/test-path')
        
    def test_log_action_without_request(self):
        log_action('CREATE', user=self.user, object_type='TestModel')
        
        log = AuditLog.objects.first()
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.object_type, 'TestModel')