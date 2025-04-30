import pytest
from feedback.models import Complaint, Person, CaseNote, ComplaintStatus, Voicenotes, Notification
from feedback.serializers import ComplaintSerializer, CaseNoteSerializer, ComplaintStatusSerializer, VoicenotesSerializer
from rest_framework import status
from django.db.models.signals import post_save
from feedback.signals import create_notification
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid

# Disable post_save signal to prevent side effects during tests
@pytest.fixture(autouse=True)
def disable_signals():
    post_save.disconnect(create_notification, sender=Complaint)
    yield
    post_save.connect(create_notification, sender=Complaint)

@pytest.fixture
def person(db):
    """Create a Person instance for testing."""
    return Person.objects.create(
        name="John Doe",
        age=30,
        gender="Male",
        additional_info="Test info"
    )

@pytest.fixture
def complaint(db, person):
    """Create a Complaint instance for testing."""
    return Complaint.objects.create(
        reporter_nickname="Reporter",
        case_category="Abuse",
        complaint_text="Test complaint",
        victim=person,
        perpetrator=person
    )

@pytest.fixture
def case_note(db, complaint):
    """Create a CaseNote instance for testing."""
    return CaseNote.objects.create(
        complaint=complaint,
        note_text="Test note",
        created_by="Agent"
    )

@pytest.fixture
def complaint_status(db, complaint):
    """Create a ComplaintStatus instance for testing."""
    return ComplaintStatus.objects.create(
        complaint=complaint,
        status="Open",
        updated_by="Agent"
    )

@pytest.fixture
def voicenote(db):
    """Create a Voicenote instance for testing."""
    return Voicenotes.objects.create(
        voicenote=b"test audio data"
    )

@pytest.fixture
def valid_complaint_data(person):
    """Valid data for creating a Complaint via API."""
    return {
        "reporter_nickname": "New Reporter",
        "case_category": "Harassment",
        "complaint_text": "New complaint",
        "victim": {
            "name": "Jane Doe",
            "age": 25,
            "gender": "Female",
            "additional_info": "Victim info"
        },
        "perpetrator": {
            "name": "Bob Smith",
            "age": 40,
            "gender": "Male",
            "additional_info": "Perpetrator info"
        }
    }

@pytest.fixture
def valid_case_note_data(complaint):
    """Valid data for creating a CaseNote via API."""
    return {
        "complaint": str(complaint.complaint_id),
        "note_text": "New note",
        "created_by": "Agent2"
    }

@pytest.fixture
def valid_status_data():
    """Valid data for updating ComplaintStatus via API."""
    return {
        "status": "Resolved",
        "updated_by": "Agent3"
    }

@pytest.fixture
def valid_voicenote_data():
    """Valid data for creating a Voicenote via API."""
    return {
        "voicenote": SimpleUploadedFile("test.mp3", b"new audio data", content_type="audio/mpeg")
    }

# ComplaintViewSet Tests
def test_list_complaints_empty(client, db):
    """Test GET /complaints/ with no complaints."""
    response = client.get('/complaints/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_complaints(client, complaint):
    """Test GET /complaints/ with existing complaints."""
    response = client.get('/complaints/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    serialized = ComplaintSerializer(complaint).data
    assert response.json()[0]['complaint_id'] == str(complaint.complaint_id)

def test_create_complaint_valid(client, valid_complaint_data, db):
    """Test POST /complaints/ with valid data."""
    response = client.post('/complaints/', data=valid_complaint_data, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['status'] == 'Complaint submitted successfully'
    complaint = Complaint.objects.get(reporter_nickname="New Reporter")
    assert complaint.case_category == "Harassment"
    assert complaint.victim.name == "Jane Doe"
    assert complaint.perpetrator.name == "Bob Smith"

def test_create_complaint_with_files(client, valid_complaint_data, db):
    """Test POST /complaints/ with image and audio files."""
    data = valid_complaint_data.copy()
    image = SimpleUploadedFile("test.jpg", b"image data", content_type="image/jpeg")
    audio = SimpleUploadedFile("test.mp3", b"audio data", content_type="audio/mpeg")
    data['complaint_image'] = image
    data['complaint_audio'] = audio
    response = client.post('/complaints/', data=data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    complaint = Complaint.objects.get(reporter_nickname="New Reporter")
    assert complaint.complaint_image
    assert complaint.complaint_audio

def test_create_complaint_invalid(client, valid_complaint_data, db):
    """Test POST /complaints/ with invalid victim data."""
    data = valid_complaint_data.copy()
    data['victim']['age'] = -1  # Invalid age
    response = client.post('/complaints/', data=data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "victim" in response.json()
    assert "age" in response.json()["victim"]

def test_retrieve_complaint(client, complaint):
    """Test GET /complaints/:id/ for existing complaint."""
    response = client.get(f'/complaints/{str(complaint.complaint_id)}/')
    assert response.status_code == status.HTTP_200_OK
    serialized = ComplaintSerializer(complaint).data
    assert response.json()['complaint_id'] == str(complaint.complaint_id)

def test_update_complaint(client, complaint, valid_complaint_data):
    """Test PUT /complaints/:id/ with valid data."""
    response = client.put(
        f'/complaints/{str(complaint.complaint_id)}/',
        data=valid_complaint_data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    complaint.refresh_from_db()
    assert complaint.reporter_nickname == "New Reporter"
    assert complaint.victim.name == "Jane Doe"

def test_delete_complaint(client, complaint):
    """Test DELETE /complaints/:id/ for existing complaint."""
    response = client.delete(f'/complaints/{str(complaint.complaint_id)}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Complaint.objects.filter(complaint_id=complaint.complaint_id).exists()

# CaseNoteViewSet Tests
def test_list_case_notes_empty(client, db):
    """Test GET /case-notes/ with no case notes."""
    response = client.get('/case-notes/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_case_notes(client, case_note):
    """Test GET /case-notes/ with existing case notes."""
    response = client.get('/case-notes/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    serialized = CaseNoteSerializer(case_note).data
    assert response.json()[0]['note_text'] == "Test note"

def test_create_case_note_valid(client, valid_case_note_data):
    """Test POST /case-notes/ with valid data."""
    response = client.post('/case-notes/', data=valid_case_note_data, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['message'] == 'Case note added successfully'
    case_note = CaseNote.objects.get(note_text="New note")
    assert case_note.created_by == "Agent2"

def test_create_case_note_invalid(client, valid_case_note_data):
    """Test POST /case-notes/ with missing note_text."""
    data = valid_case_note_data.copy()
    data['note_text'] = ""
    response = client.post('/case-notes/', data=data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "note_text" in response.json()

def test_retrieve_case_note(client, case_note):
    """Test GET /case-notes/:id/ for existing case note."""
    response = client.get(f'/case-notes/{case_note.id}/')
    assert response.status_code == status.HTTP_200_OK
    serialized = CaseNoteSerializer(case_note).data
    assert response.json()['note_text'] == "Test note"

def test_update_case_note(client, case_note, valid_case_note_data):
    """Test PUT /case-notes/:id/ with valid data."""
    response = client.put(
        f'/case-notes/{case_note.id}/',
        data=valid_case_note_data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    case_note.refresh_from_db()
    assert case_note.note_text == "New note"

def test_delete_case_note(client, case_note):
    """Test DELETE /case-notes/:id/ for existing case note."""
    response = client.delete(f'/case-notes/{case_note.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not CaseNote.objects.filter(id=case_note.id).exists()

# ComplaintStatusUpdateView Tests
def test_update_complaint_status(client, complaint, valid_status_data):
    """Test PUT /complaints/<complaint_id>/status/update/ with valid data."""
    response = client.put(
        f'/complaints/{str(complaint.complaint_id)}/status/update/',
        data=valid_status_data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    status_obj = ComplaintStatus.objects.get(complaint=complaint)
    assert status_obj.status == "Resolved"
    assert status_obj.updated_by == "Agent3"

@pytest.mark.django_db
def test_update_complaint_status_not_found(client, valid_status_data):
    """Test PUT /complaints/<complaint_id>/status/update/ with non-existent complaint."""
    response = client.put(
        f'/complaints/{str(uuid.uuid4())}/status/update/',
        data=valid_status_data,
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['error'] == 'Complaint not found'

# get_complaint_status Tests
def test_get_complaint_status(client, complaint, complaint_status):
    """Test GET /complaints/<complaint_id>/status/get/ for existing status."""
    response = client.get(f'/complaints/{str(complaint.complaint_id)}/status/get/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == "Open"
    assert response.json()['case_id'] == str(complaint.complaint_id)

def test_get_complaint_status_no_status(client, complaint):
    """Test GET /complaints/<complaint_id>/status/get/ with no status."""
    response = client.get(f'/complaints/{str(complaint.complaint_id)}/status/get/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['error'] == 'Status not found'

# submit_feedback Tests
def test_submit_feedback_valid(client):
    """Test POST /submit-feedback/ with valid data."""
    data = {"feedback": "Great service"}
    response = client.post('/submit-feedback/', data=data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['message'] == 'Feedback submitted successfully'

def test_submit_feedback_invalid(client):
    """Test POST /submit-feedback/ with empty feedback."""
    data = {"feedback": ""}
    response = client.post('/submit-feedback/', data=data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['error'] == 'Feedback cannot be empty'

# VoicenotesListCreateView Tests
def test_list_voicenotes_empty(client, db):
    """Test GET /voicenotes/ with no voicenotes."""
    response = client.get('/voicenotes/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_voicenotes(client, voicenote):
    """Test GET /voicenotes/ with existing voicenotes."""
    response = client.get('/voicenotes/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    serialized = VoicenotesSerializer(voicenote).data
    assert response.json()[0]['id'] == voicenote.id

@pytest.mark.django_db
def test_create_voicenote_valid(client, valid_voicenote_data):
    """Test POST /voicenotes/ with valid data."""
    response = client.post('/voicenotes/', data=valid_voicenote_data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    voicenote = Voicenotes.objects.get(id=response.json()['id'])
    assert voicenote.voicenote.read() == b"new audio data"

# VoicenotesRetrieveUpdateDestroyView Tests
def test_retrieve_voicenote(client, voicenote):
    """Test GET /voicenotes/:id/ for existing voicenote."""
    response = client.get(f'/voicenotes/{voicenote.id}/')
    assert response.status_code == status.HTTP_200_OK
    serialized = VoicenotesSerializer(voicenote).data
    assert response.json()['id'] == voicenote.id

def test_update_voicenote(client, voicenote, valid_voicenote_data):
    """Test PUT /voicenotes/:id/ with valid data."""
    response = client.put(
        f'/voicenotes/{voicenote.id}/',
        data=valid_voicenote_data,
        format='multipart'
    )
    assert response.status_code == status.HTTP_200_OK
    voicenote.refresh_from_db()
    assert voicenote.voicenote.read() == b"new audio data"

def test_delete_voicenote(client, voicenote):
    """Test DELETE /voicenotes/:id/ for existing voicenote."""
    response = client.delete(f'/voicenotes/{voicenote.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Voicenotes.objects.filter(id=voicenote.id).exists()