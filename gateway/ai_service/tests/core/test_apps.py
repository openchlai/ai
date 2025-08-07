
import pytest
from django.apps import apps
from core.apps import CoreConfig

@pytest.mark.unit
def test_core_app_config():
    """
    Test the CoreConfig app configuration.
    """
    # Check that the app config can be loaded
    app_config = apps.get_app_config('core')
    assert isinstance(app_config, CoreConfig)
    
    # Check the app name
    assert app_config.name == 'core'
    
    # Check the default auto field
    assert app_config.default_auto_field == 'django.db.models.BigAutoField'
