import pytest
from django.conf import settings

# Monkeypatch INSTALLED_APPS before importing models
def pytest_configure():
    original_installed_apps = list(settings.INSTALLED_APPS)
    if 'feedback' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS = original_installed_apps + ['feedback']
        print(f"Monkeypatched INSTALLED_APPS: {settings.INSTALLED_APPS}")

pytest_configure()

from django.utils.timezone import now
from feedback.models import Person, Complaint, CaseNote, ComplaintStatus, Notification, Voicenotes
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture(autouse=True)
def restore_installed_apps(monkeypatch):
    """Restore original INSTALLED_APPS after tests."""
    original_installed_apps = list(settings.INSTALLED_APPS)
    yield
    monkeypatch.setattr(settings, 'INSTALLED_APPS', original_installed_apps)
    print(f"Restored INSTALLED_APPS: {settings.INSTALLED_APPS}")

@pytest.fixture
def person(db):
    """Create a Person instance."""
    return Person.objects.create(
        name="John Doe",
        age=30,
        gender="Male",
        additional_info="Test info"
    )

@pytest.fixture
def complaint(db, person):
    """Create a Complaint instance with victim and perpetrator."""
    return Complaint.objects.create(
        reporter_nickname="Anonymous",
        case_category="Abuse",
        complaint_text="Test complaint",
        victim=person,
        perpetrator=person
    )

@pytest.fixture
def case_note(db, complaint):
    """Create a CaseNote instance."""
    return CaseNote.objects.create(
        complaint=complaint,
        note_text="Test note",
        created_by="Agent Smith"
    )

@pytest.fixture
def complaint_status(db, complaint):
    """Create a ComplaintStatus instance."""
    return ComplaintStatus.objects.create(
        complaint=complaint,
        status="Open",
        updated_by="Agent Smith"
    )

@pytest.fixture
def notification(db, complaint):
    """Create a Notification instance."""
    return Notification.objects.create(
        complaint=complaint,
        message="Test notification"
    )

@pytest.fixture
def voicenote(db):
    """Create a Voicenote instance."""
    return Voicenotes.objects.create(
        voicenote=b"Test audio data"
    )

def test_person_str(person):
    """Test Person __str__ method."""
    assert str(person) == "John Doe"

def test_complaint_str(complaint):
    """Test Complaint __str__ method."""
    assert str(complaint) == f"Complaint {complaint.complaint_id} by Anonymous"

def test_complaint_fields(complaint, person):
    """Test Complaint field values and relationships."""
    assert complaint.reporter_nickname == "Anonymous"
    assert complaint.case_category == "Abuse"
    assert complaint.complaint_text == "Test complaint"
    assert complaint.victim == person
    assert complaint.perpetrator == person
    assert isinstance(complaint.complaint_id, uuid.UUID)
    assert complaint.created_at is not None

def test_complaint_file_fields(complaint, db):
    """Test Complaint file fields."""
    complaint.complaint_image = SimpleUploadedFile("test.jpg", b"image data", content_type="image/jpeg")
    complaint.complaint_audio = SimpleUploadedFile("test.mp3", b"audio data", content_type="audio/mpeg")
    complaint.complaint_video = SimpleUploadedFile("test.mp4", b"video data", content_type="video/mp4")
    complaint.save()
    assert complaint.complaint_image
    assert complaint.complaint_audio
    assert complaint.complaint_video

def test_case_note_str(case_note, complaint):
    """Test CaseNote __str__ method."""
    assert str(case_note) == f"CaseNote for {complaint.complaint_id} on {case_note.created_at}"

def test_complaint_status_str(complaint_status, complaint):
    """Test ComplaintStatus __str__ method."""
    assert str(complaint_status) == f"Status for Complaint {complaint.complaint_id}: Open"

def test_notification_str(notification, complaint):
    """Test Notification __str__ method."""
    assert str(notification) == f"Notification for Complaint {complaint.complaint_id}"

def test_voicenote_str(voicenote):
    """Test Voicenote __str__ method (assuming no complaint relation)."""
    with pytest.raises(AttributeError):  # complaint field is commented out
        str(voicenote)
    assert voicenote.voicenote == b"Test audio data"
    assert voicenote.created_at is not None