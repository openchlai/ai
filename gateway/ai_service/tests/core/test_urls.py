
from django.urls import path, reverse
from core import views
import pytest

@pytest.mark.unit
def test_urls():
    """
    Test the urls for the core app.
    """
    assert reverse('health') == '/api/core/health/'
    assert reverse('audio-upload') == '/api/core/upload/'
    assert reverse('task-status', kwargs={'task_id': '123'}) == '/api/core/task_status/123/'
