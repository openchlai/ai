# apps/shared/accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shared.accounts'
    label = 'accounts'
    verbose_name = 'User Accounts'
    
    def ready(self):
        import apps.shared.accounts.signals