import pytest
from django.conf import settings
from django.apps import apps
from io import BytesIO
from PIL import Image

# Debug INSTALLED_APPS and app registry
print(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
print(f"Feedback app registered: {'feedback' in [app_config.name for app_config in apps.get_app_configs()]}")

from feedback.models import Person, Complaint, CaseNote, ComplaintStatus, Voicenotes
from feedback.serializers import PersonSerializer, ComplaintSerializer, CaseNoteSerializer, ComplaintStatusSerializer, VoicenotesSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def person_data():
    """Valid Person data."""
    return {
        "name": "Jane Doe",
        "age": 25,
        "gender": "Female",
        "additional_info": "Test info"
    }

@pytest.fixture
def complaint_data(person_data):
    """Valid Complaint data."""
    return {
        "reporter_nickname": "Anonymous",
        "case_category": "Harassment",
        "complaint_text": "Test complaint",
        "victim": person_data,
        "perpetrator": person_data
    }

@pytest.fixture
def case_note_data():
    """Valid CaseNote data."""
    return {
        "note_text": "Test note",
        "created_by": "Agent Smith"
    }

@pytest.fixture
def complaint_status_data():
    """Valid ComplaintStatus data."""
    return {
        "status": "Open",
        "updated_by": "Agent Smith"
    }

@pytest.fixture
def voicenote_data():
    """Valid Voicenotes data."""
    return {
        "voicenote": b"Test audio data"
    }

@pytest.fixture
def create_image_file():
    """Create a valid PNG image for testing."""
    image = Image.new('RGB', (100, 100), color='red')
    image_file = BytesIO()
    image.save(image_file, format='PNG')
    image_file.seek(0)
    return SimpleUploadedFile("test.png", image_file.read(), content_type="image/png")

@pytest.mark.django_db
def test_person_serializer_valid(person_data):
    """Test PersonSerializer with valid data."""
    serializer = PersonSerializer(data=person_data)
    assert serializer.is_valid(), serializer.errors
    person = serializer.save()
    assert person.name == "Jane Doe"
    assert person.age == 25
    assert person.gender == "Female"
    assert person.additional_info == "Test info"

@pytest.mark.django_db
def test_person_serializer_nullable_fields():
    """Test PersonSerializer with nullable fields."""
    data = {"name": "John Doe"}
    serializer = PersonSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    person = serializer.save()
    assert person.name == "John Doe"
    assert person.age is None
    assert person.gender is None
    assert person.additional_info is None

def test_person_serializer_invalid_data():
    """Test PersonSerializer with invalid data."""
    data = {"name": ""}  # Empty name
    serializer = PersonSerializer(data=data)
    assert not serializer.is_valid()
    assert "name" in serializer.errors

@pytest.mark.django_db
def test_complaint_serializer_valid(complaint_data):
    """Test ComplaintSerializer with valid data."""
    serializer = ComplaintSerializer(data=complaint_data)
    assert serializer.is_valid(), serializer.errors
    complaint = serializer.save()
    assert complaint.reporter_nickname == "Anonymous"
    assert complaint.case_category == "Harassment"
    assert complaint.complaint_text == "Test complaint"
    assert complaint.victim.name == "Jane Doe"
    assert complaint.perpetrator.name == "Jane Doe"
    assert complaint.complaint_id is not None

@pytest.mark.django_db
def test_complaint_serializer_file_fields(create_image_file):
    """Test ComplaintSerializer with file fields."""
    data = {
        "reporter_nickname": "Anonymous",
        "case_category": "Abuse",
        "complaint_text": "Test complaint",
        "complaint_image": create_image_file,
        "complaint_audio": SimpleUploadedFile("test.mp3", b"audio data", content_type="audio/mpeg"),
        "complaint_video": SimpleUploadedFile("test.mp4", b"video data", content_type="video/mp4")
    }
    serializer = ComplaintSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    complaint = serializer.save()
    assert complaint.complaint_image
    assert complaint.complaint_audio
    assert complaint.complaint_video

@pytest.mark.django_db
def test_complaint_serializer_nullable_fields():
    """Test ComplaintSerializer with nullable fields."""
    data = {
        "reporter_nickname": "Anonymous",
        "complaint_text": "Minimal complaint"
    }
    serializer = ComplaintSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    complaint = serializer.save()
    assert complaint.reporter_nickname == "Anonymous"
    assert complaint.complaint_text == "Minimal complaint"
    assert complaint.case_category == "Not Specified"
    assert complaint.victim is None
    assert complaint.perpetrator is None

def test_complaint_serializer_invalid_data():
    """Test ComplaintSerializer with oversized data."""
    data = {"complaint_text": "x" * 1001}  # Exceeds typical TextField length
    serializer = ComplaintSerializer(data=data)
    assert not serializer.is_valid()
    assert "complaint_text" in serializer.errors

@pytest.mark.django_db
def test_case_note_serializer_valid(case_note_data, complaint):
    """Test CaseNoteSerializer with valid data."""
    # Create CaseNote directly since complaint is read-only
    case_note = CaseNote.objects.create(
        complaint=complaint,
        note_text=case_note_data["note_text"],
        created_by=case_note_data["created_by"]
    )
    serializer = CaseNoteSerializer(case_note)
    assert serializer.data["note_text"] == "Test note"
    assert serializer.data["created_by"] == "Agent Smith"
    assert serializer.data["complaint"] == str(complaint.complaint_id)

def test_case_note_serializer_missing_note_text():
    """Test CaseNoteSerializer with missing note_text."""
    data = {"created_by": "Agent Smith"}
    serializer = CaseNoteSerializer(data=data)
    assert not serializer.is_valid()
    assert "note_text" in serializer.errors

@pytest.mark.django_db
def test_complaint_status_serializer_valid(complaint_status_data, complaint):
    """Test ComplaintStatusSerializer with valid data."""
    # Create ComplaintStatus directly since complaint is read-only
    status_obj = ComplaintStatus.objects.create(
        complaint=complaint,
        status=complaint_status_data["status"],
        updated_by=complaint_status_data["updated_by"]
    )
    serializer = ComplaintStatusSerializer(status_obj)
    assert serializer.data["status"] == "Open"
    assert serializer.data["updated_by"] == "Agent Smith"
    assert serializer.data["complaint"] == str(complaint.complaint_id)

def test_complaint_status_serializer_missing_status():
    """Test ComplaintStatusSerializer with missing status."""
    data = {"updated_by": "Agent Smith"}
    serializer = ComplaintStatusSerializer(data=data)
    assert not serializer.is_valid()
    assert "status" in serializer.errors

@pytest.mark.django_db
def test_voicenote_serializer_valid():
    """Test VoicenotesSerializer with existing instance."""
    # Create Voicenote directly since voicenote is read-only
    voicenote = Voicenotes.objects.create(voicenote=b"Test audio data")
    serializer = VoicenotesSerializer(voicenote)
    assert serializer.data["created_at"] is not None

def test_voicenote_serializer_invalid_data():
    """Test VoicenotesSerializer with invalid data."""
    data = {}  # No fields provided
    serializer = VoicenotesSerializer(data=data)
    assert not serializer.is_valid()