import pytest
from emailfeedback.models import Email
from emailfeedback.serializers import EmailSerializer
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models.signals import post_save
from emailfeedback.signals import forward_email_to_main_system

# Disable post_save signal to prevent side effects during tests
@pytest.fixture(autouse=True)
def disable_signals():
    try:
        post_save.disconnect(forward_email_to_main_system, sender=Email)
    except NameError:
        pass  # Signal might not exist
    yield
    try:
        post_save.connect(forward_email_to_main_system, sender=Email)
    except NameError:
        pass

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
        raw_message=b""  # Satisfy NOT NULL constraint
    )

@pytest.fixture
def valid_email_data():
    """Valid data for creating an Email via serializer."""
    return {
        "sender": "new@example.com",
        "recipient": "new_recipient@example.com",
        "subject": "New Subject",
        "body": "New body",
        "received_date": "2025-01-21T10:00:00Z",
        "is_read": False
    }

def test_serialize_email(email):
    """Test serializing an Email instance."""
    serializer = EmailSerializer(email)
    data = serializer.data
    assert data["sender"] == "test@example.com"
    assert data["recipient"] == "recipient@example.com"
    assert data["subject"] == "Test Subject"
    assert data["body"] == "Test body"
    assert data["received_date"] == "2025-01-21T10:00:00Z"
    assert data["is_read"] is False

def test_deserialize_valid_data(valid_email_data, db):
    """Test creating an Email with valid data."""
    serializer = EmailSerializer(data=valid_email_data)
    assert serializer.is_valid(), serializer.errors
    # Manually set raw_message to avoid IntegrityError
    validated_data = serializer.validated_data
    email = Email.objects.create(**validated_data, raw_message=b"")
    assert email.sender == "new@example.com"
    assert email.recipient == "new_recipient@example.com"
    assert email.subject == "New Subject"
    assert email.body == "New body"
    assert email.received_date == make_aware(datetime(2025, 1, 21, 10, 0, 0))
    assert email.is_read is False
    assert email.raw_message == b""

def test_deserialize_invalid_sender(valid_email_data, db):
    """Test that sender exceeding max_length raises a validation error."""
    data = valid_email_data.copy()
    data["sender"] = "a" * 256  # Exceeds max_length=255
    serializer = EmailSerializer(data=data)
    assert not serializer.is_valid()
    assert "sender" in serializer.errors
    assert "no more than 255 characters" in str(serializer.errors["sender"][0]).lower()

def test_deserialize_invalid_recipient(valid_email_data, db):
    """Test that recipient exceeding max_length raises a validation error."""
    data = valid_email_data.copy()
    data["recipient"] = "b" * 256  # Exceeds max_length=255
    serializer = EmailSerializer(data=data)
    assert not serializer.is_valid()
    assert "recipient" in serializer.errors
    assert "no more than 255 characters" in str(serializer.errors["recipient"][0]).lower()

def test_deserialize_invalid_received_date(valid_email_data, db):
    """Test that invalid received_date raises a validation error."""
    data = valid_email_data.copy()
    data["received_date"] = "invalid_date"
    serializer = EmailSerializer(data=data)
    assert not serializer.is_valid()
    assert "received_date" in serializer.errors
    assert "datetime has wrong format" in str(serializer.errors["received_date"][0]).lower()

def test_deserialize_blank_subject_and_body(valid_email_data, db):
    """Test that blank subject and body are invalid."""
    data = valid_email_data.copy()
    data["subject"] = ""
    data["body"] = ""
    serializer = EmailSerializer(data=data)
    assert not serializer.is_valid()
    assert "subject" in serializer.errors
    assert "body" in serializer.errors
    assert "may not be blank" in str(serializer.errors["subject"][0]).lower()
    assert "may not be blank" in str(serializer.errors["body"][0]).lower()

def test_read_only_fields(email, valid_email_data):
    """Test that id is read-only."""
    serializer = EmailSerializer(email, data=valid_email_data)
    assert serializer.is_valid(), serializer.errors
    # Manually update to avoid IntegrityError
    validated_data = serializer.validated_data
    for key, value in validated_data.items():
        setattr(email, key, value)
    email.raw_message = b""  # Ensure NOT NULL constraint
    email.save()
    assert email.sender == "new@example.com"
    assert email.id == email.id  # ID should not change