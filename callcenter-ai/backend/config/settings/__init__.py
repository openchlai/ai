"""
Django settings module selector

This module automatically loads the appropriate settings file based on the
DJANGO_SETTINGS_MODULE environment variable or defaults to development.
"""

import os

# Default to development settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if settings_module == 'config.settings.development':
    from .development import *
elif settings_module == 'config.settings.production':
    from .production import *
else:
    # Fallback to development
    from .development import *