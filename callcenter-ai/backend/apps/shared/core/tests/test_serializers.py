from django.test import TestCase
from rest_framework.exceptions import ValidationError
from core.serializers import AuditLogSerializer, AuditLogFilterSerializer
from core.models import AuditLog
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class AuditLogSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='serializeruser',
            password='serializerpass123'
        )
        
        self.log_data = {
            'user': self.user.id,
            'action': 'CREATE',
            'object_type': 'TestModel',
            'object_id': '550e8400-e29b-41d4-a716-446655440000',
            'ip_address': '192.168.1.1',
            'metadata': {'key': 'value'}
        }
        
    def test_valid_audit_log_serializer(self):
        serializer = AuditLogSerializer(data=self.log_data)
        self.assertTrue(serializer.is_valid())
        
    def test_audit_log_serializer_output(self):
        log = AuditLog.objects.create(**self.log_data)
        serializer = AuditLogSerializer(instance=log)
        self.assertEqual(serializer.data['action'], 'CREATE')
        self.assertEqual(serializer.data['object_type'], 'TestModel')

class AuditLogFilterSerializerTestCase(TestCase):
    def test_valid_filter_serializer(self):
        data = {
            'action': 'CREATE',
            'date_from': '2023-01-01',
            'date_to': '2023-12-31'
        }
        serializer = AuditLogFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_invalid_date_range(self):
        data = {
            'date_from': '2023-12-31',
            'date_to': '2023-01-01'
        }
        serializer = AuditLogFilterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)