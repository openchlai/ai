
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from core.models import AudioFile

@pytest.mark.django_db
def test_health_check(client):
    """
    Test the health check endpoint.
    """
    url = reverse('health-check')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'healthy', 'service': 'ai_service'}

@pytest.mark.django_db
def test_task_status_not_found(client):
    """
    Test the task status endpoint with a non-existent task ID.
    """
    url = reverse('task-status', kwargs={'task_id': 'non-existent-task-id'})
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
@patch('core.views.process_audio_pipeline.delay')
def test_audio_upload_view(mock_process_audio, client, sample_audio_file):
    """
    Test the audio upload view.
    """
    # Mock the celery task
    mock_process_audio.return_value.id = 'test-task-id'

    initial_count = AudioFile.objects.count()
    # Make a POST request to the upload view
    url = reverse('audio-upload')
    response = client.post(url, {'audio': sample_audio_file}, format='multipart')

    # Check the response
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert 'task_id' in response.data
    assert response.data['task_id'] == 'test-task-id'

    # Check that the audio file was saved
    assert AudioFile.objects.count() == initial_count + 1
    audio = AudioFile.objects.first()
    assert audio.audio.name.endswith(sample_audio_file.name)

    # Check that the celery task was called
    mock_process_audio.assert_called_once_with(audio.id)
