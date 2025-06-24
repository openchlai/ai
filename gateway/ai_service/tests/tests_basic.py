import pytest
from django.test import TestCase
from core.models import AudioFile
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_django_setup():
    """Test that Django is set up correctly"""
    # This should work if Django is configured properly
    assert AudioFile.objects.count() == 0


@pytest.mark.django_db  
def test_audio_file_creation():
    """Test basic AudioFile creation"""
    # Create a simple audio file
    audio_content = b'fake audio content'
    audio_file = SimpleUploadedFile("test.wav", audio_content, content_type="audio/wav")
    
    # Create AudioFile instance
    instance = AudioFile.objects.create(audio=audio_file)
    
    # Test basic properties
    assert instance.id is not None
    assert instance.audio is not None
    assert instance.created_at is not None
    assert instance.updated_at is not None
    assert instance.transcript is None
    assert instance.summary is None
    
    # Test string representation
    expected_str = f"AudioFile {instance.id} - {instance.created_at}"
    assert str(instance) == expected_str


@pytest.mark.django_db
def test_audio_file_json_field():
    """Test AudioFile with JSON insights field"""
    audio_content = b'test audio'
    audio_file = SimpleUploadedFile("test.wav", audio_content, content_type="audio/wav")
    
    insights_data = {
        "case_summary": "Test case",
        "priority": "high"
    }
    
    instance = AudioFile.objects.create(
        audio=audio_file,
        transcript="Test transcript",
        insights=insights_data
    )
    
    # Verify data was saved correctly
    saved_instance = AudioFile.objects.get(id=instance.id)
    assert saved_instance.transcript == "Test transcript"
    assert saved_instance.insights == insights_data
    assert saved_instance.insights["case_summary"] == "Test case"