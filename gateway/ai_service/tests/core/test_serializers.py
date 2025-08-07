
import pytest
from rest_framework.test import APIRequestFactory
from core.serializers import AudioFileSerializer
from core.models import AudioFile

@pytest.mark.django_db
def test_audio_file_serializer(sample_audio_file):
    """
    Test the AudioFileSerializer.
    """
    audio_file = AudioFile.objects.create(audio=sample_audio_file)
    serializer = AudioFileSerializer(audio_file)

    # Check that the serializer returns the expected fields
    expected_fields = [
        'id',
        'audio',
        'transcript',
        'translated_text',
        'annotated_text',
        'summary',
        'insights',
        'created_at',
        'updated_at',
    ]
    for field in expected_fields:
        assert field in serializer.data

    # Check that the audio URL is correct
    request = APIRequestFactory().get('/')
    serializer = AudioFileSerializer(audio_file, context={'request': request})
    assert serializer.data['audio'].startswith('http://testserver/audio_files/')
