
import pytest
from django.contrib import admin
from core.models import AudioFile

# Since there is no AudioFileAdmin, we will just check if the model is registered
@pytest.mark.unit
def test_audio_file_admin_registration():
    """
    Test that the AudioFile model is registered with the admin site.
    """
    # Check if the AudioFile model is registered
    # Ensure admin is auto-discovered for tests
    from django.contrib import admin
    admin.autodiscover()
    assert admin.site.is_registered(AudioFile)
