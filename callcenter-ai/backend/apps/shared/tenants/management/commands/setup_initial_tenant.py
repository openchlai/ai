# apps/shared/tenants/management/commands/setup_initial_tenant.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.shared.tenants.models import Tenant, Domain

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial public tenant for development'
    
    def handle(self, *args, **options):
        # Create system user if doesn't exist
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@murima.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            system_user.set_password('admin123')  # Change this!
            system_user.save()
            self.stdout.write('Created system user')
        
        # Create public tenant if doesn't exist
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public',
                'subdomain': 'public',
                'primary_contact_email': 'admin@murima.com',
                'owner': system_user,
            }
        )
        
        if created:
            self.stdout.write('Created public tenant')
        
        # Create localhost domain
        domain, created = Domain.objects.get_or_create(
            domain='localhost',
            defaults={
                'tenant': public_tenant,
                'is_primary': True,
            }
        )
        
        if created:
            self.stdout.write('Created localhost domain')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial tenant')
        )