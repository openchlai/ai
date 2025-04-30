import pytest
from django.conf import settings

def pytest_configure(config):
    """Modify INSTALLED_APPS before test collection."""
    if 'feedback' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS) + ['feedback']