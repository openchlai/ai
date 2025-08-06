from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import AuditLog

User = get_user_model()

class BaseViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
class AuditLogViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.log = AuditLog.objects.create(
            user=self.user,
            action='CREATE',
            object_type='TestModel',
            object_id='550e8400-e29b-41d4-a716-446655440000'
        )
        
    def test_list_audit_logs_unauthorized(self):
        url = reverse('audit-log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_list_audit_logs_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('audit-log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_filter_audit_logs(self):
        self.client.force_authenticate(user=self.admin)
        url = f"{reverse('audit-log-list')}?action=CREATE"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_audit_log(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('audit-log-detail', args=[str(self.log.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.log.id))

class HealthCheckViewTests(TestCase):
    def test_health_check(self):
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')