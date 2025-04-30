import pytest
from emailfeedback.models import Email
from django.utils.timezone import make_aware
from datetime import datetime
from django.db import IntegrityError
from django.core.exceptions import ValidationError

@pytest.fixture
def email(db):  # 'db' fixture ensures database access
    return Email.objects.create(
        sender="test@example.com",
        recipient="recipient@example.com",
        subject="Test Subject",
        body="Test body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        is_read=False,
        raw_message=b"test raw message"
    )

def test_field_values(email):
    """Test that all fields are saved correctly."""
    assert email.sender == "test@example.com"
    assert email.recipient == "recipient@example.com"
    assert email.subject == "Test Subject"
    assert email.body == "Test body"
    assert email.received_date == make_aware(datetime(2025, 1, 21, 10, 0, 0))
    assert email.is_read is False
    assert email.raw_message == b"test raw message"

def test_str_method(email):
    """Test the __str__ method."""
    expected_str = "Email from test@example.com to recipient@example.com: Test Subject"
    assert str(email) == expected_str

def test_default_is_read(db):
    """Test that is_read defaults to False."""
    email = Email.objects.create(
        sender="default@example.com",
        recipient="recipient@example.com",
        subject="Default Subject",
        body="Default body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b"test raw message"
    )
    assert email.is_read is False

def test_sender_max_length(db):
    """Test that sender respects max_length=255."""
    max_length = Email._meta.get_field("sender").max_length
    valid_sender = "a" * 255
    email = Email.objects.create(
        sender=valid_sender,
        recipient="recipient@example.com",
        subject="Test Subject",
        body="Test body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b"test raw message"
    )
    assert email.sender == valid_sender

    with pytest.raises(ValidationError):
        Email.objects.create(
            sender="a" * 256,  # Exceeds max_length
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test body",
            received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
            raw_message=b"test raw message"
        ).full_clean()

def test_recipient_max_length(db):
    """Test that recipient respects max_length=255."""
    max_length = Email._meta.get_field("recipient").max_length
    valid_recipient = "b" * 255
    email = Email.objects.create(
        sender="test@example.com",
        recipient=valid_recipient,
        subject="Test Subject",
        body="Test body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b"test raw message"
    )
    assert email.recipient == valid_recipient

    with pytest.raises(ValidationError):
        Email.objects.create(
            sender="test@example.com",
            recipient="b" * 256,  # Exceeds max_length
            subject="Test Subject",
            body="Test body",
            received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
            raw_message=b"test raw message"
        ).full_clean()

def test_empty_subject_and_body(db):
    """Test that subject and body can be empty."""
    email = Email.objects.create(
        sender="test@example.com",
        recipient="recipient@example.com",
        subject="",
        body="",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b"test raw message"
    )
    assert email.subject == ""
    assert email.body == ""

def test_large_subject_and_body(db):
    """Test that subject and body can handle large text."""
    large_text = "x" * 10000  # 10,000 characters
    email = Email.objects.create(
        sender="test@example.com",
        recipient="recipient@example.com",
        subject=large_text,
        body=large_text,
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b"test raw message"
    )
    assert email.subject == large_text
    assert email.body == large_text

def test_received_date_valid(db):
    """Test that received_date accepts valid datetimes."""
    email = Email.objects.create(
        sender="test@example.com",
        recipient="recipient@example.com",
        subject="Test Subject",
        body="Test body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b"test raw message"
    )
    assert email.received_date == make_aware(datetime(2025, 1, 21, 10, 0, 0))

def test_received_date_invalid(db):
    """Test that invalid received_date raises an error."""
    with pytest.raises(ValidationError):
        Email.objects.create(
            sender="test@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test body",
            received_date="invalid_date",  # Invalid format
            raw_message=b"test raw message"
        )

def test_raw_message_not_null(db):
    """Test that raw_message cannot be null."""
    with pytest.raises(IntegrityError):
        Email.objects.create(
            sender="test@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test body",
            received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
            is_read=False
        )

def test_raw_message_empty(db):
    """Test that raw_message can be an empty binary."""
    email = Email.objects.create(
        sender="test@example.com",
        recipient="recipient@example.com",
        subject="Test Subject",
        body="Test body",
        received_date=make_aware(datetime(2025, 1, 21, 10, 0, 0)),
        raw_message=b""
    )
    assert email.raw_message == b""