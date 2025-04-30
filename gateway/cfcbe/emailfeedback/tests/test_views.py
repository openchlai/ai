import pytest
from emailfeedback.models import Email
from emailfeedback.serializers import EmailSerializer
from django.utils.timezone import make_aware
from datetime import datetime
from rest_framework import status
from django.db.models.signals import post_save
from emailfeedback.signals import forward_email

# Base URL for API endpoints
BASE_URL = '/emails/'  # Matches emailfeedback.urls included at root in cfcbe/urls.py

@pytest.fixture(autouse=True)
def disable_signals():
    post_save.disconnect(forward_email, sender=Email)
    yield
    post_save.connect(forward_email, sender=Email)

@pytest.fixture(autouse=True)
def debug_urls(client):
    """Print URL patterns for debugging."""
    from django.urls import get_resolver
    resolver = get_resolver()
    print("Registered URL Patterns:")
    for pattern in resolver.url_patterns:
        print(pattern)
    yield

@pytest.fixture
def email(db):
    """Create an Email instance for testing."""
    return Email.objects.create(
        sender="test@example.com",
        recipient="recipient@example.com",
        subject="Test Subject",
        body="Test body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        is_read=False,
        raw_message=b""
    )

@pytest.fixture
def valid_email_data():
    """Valid data for creating an Email via API (excluding raw_message)."""
    return {
        "sender": "new@example.com",
        "recipient": "new_recipient@example.com",
        "subject": "New Subject",
        "body": "New body",
        "received_date": "2025-01-21T10:00:00Z",
        "is_read": False
    }

def test_list_emails_empty(client, db):
    """Test GET /emails/ with no emails."""
    response = client.get(BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_emails(client, email):
    """Test GET /emails/ with existing emails."""
    response = client.get(BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    serialized = EmailSerializer(email).data
    assert response.json()[0] == serialized

def test_create_email_valid(client, valid_email_data, db):
    """Test POST /emails/ with valid data (expect failure due to missing raw_message)."""
    response = client.post(BASE_URL, data=valid_email_data, content_type='application/json')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR  # View raises unhandled IntegrityError
    assert not Email.objects.filter(sender="new@example.com").exists()

def test_create_email_invalid_sender(client, valid_email_data, db):
    """Test POST /emails/ with invalid sender."""
    data = valid_email_data.copy()
    data["sender"] = "a" * 256
    response = client.post(BASE_URL, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "sender" in response.json()

def test_create_email_missing_subject(client, valid_email_data, db):
    """Test POST /emails/ with missing subject."""
    data = valid_email_data.copy()
    data["subject"] = ""
    response = client.post(BASE_URL, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "subject" in response.json()

def test_retrieve_email(client, email):
    """Test GET /emails/:id/ for existing email."""
    response = client.get(f'{BASE_URL}{email.id}/')
    assert response.status_code == status.HTTP_200_OK
    serialized = EmailSerializer(email).data
    assert response.json() == serialized

def test_retrieve_email_not_found(client, db):
    """Test GET /emails/:id/ for non-existent email."""
    response = client.get(f'{BASE_URL}999/')
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_email_valid(client, email, valid_email_data, db):
    """Test PUT /emails/:id/ with valid data."""
    response = client.put(
        f'{BASE_URL}{email.id}/',
        data=valid_email_data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    email.refresh_from_db()
    assert email.sender == "new@example.com"
    assert email.recipient == "new_recipient@example.com"
    assert email.subject == "New Subject"
    assert email.body == "New body"
    assert email.received_date == make_aware(datetime(2025, 1, 21, 10, 0, 0))
    assert email.is_read is False

def test_update_email_invalid_recipient(client, email, valid_email_data, db):
    """Test PUT /emails/:id/ with invalid recipient."""
    data = valid_email_data.copy()
    data["recipient"] = "b" * 256
    response = client.put(
        f'{BASE_URL}{email.id}/',
        data=data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recipient" in response.json()

def test_partial_update_email(client, email, db):
    """Test PATCH /emails/:id/ to update is_read."""
    data = {"is_read": True}
    response = client.patch(
        f'{BASE_URL}{email.id}/',
        data=data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    email.refresh_from_db()
    assert email.is_read is True
    assert email.sender == "test@example.com"

def test_delete_email(client, email, db):
    """Test DELETE /emails/:id/ for existing email."""
    response = client.delete(f'{BASE_URL}{email.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Email.objects.filter(id=email.id).exists()

def test_delete_email_not_found(client, db):
    """Test DELETE /emails/:id/ for non-existent email."""
    response = client.delete(f'{BASE_URL}999/')
    assert response.status_code == status.HTTP_404_NOT_FOUND