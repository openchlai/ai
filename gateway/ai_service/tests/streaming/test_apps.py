
import pytest
from django.apps import apps
from streaming.apps import StreamingConfig

@pytest.mark.unit
def test_streaming_app_config():
    """
    Test the StreamingConfig app configuration.
    """
    # Check that the app config can be loaded
    app_config = apps.get_app_config('streaming')
    assert isinstance(app_config, StreamingConfig)
    
    # Check the app name
    assert app_config.name == 'streaming'
    
    # Check the default auto field
    assert app_config.default_auto_field == 'django.db.models.BigAutoField'
