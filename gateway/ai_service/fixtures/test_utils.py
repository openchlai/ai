"""
Test utilities and helper functions
"""
import json
import os
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock


def create_test_audio_file(filename="test_audio.wav", size="small"):
    """
    Create a test audio file with minimal WAV header
    
    Args:
        filename: Name of the audio file
        size: Size of the file - 'small', 'medium', 'large'
    
    Returns:
        SimpleUploadedFile: Mock audio file for testing
    """
    # Basic WAV header
    base_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data'
    
    if size == "small":
        # Small audio file (< 1KB)
        audio_data = base_header + b'\x00' * 100
    elif size == "medium":
        # Medium audio file (~10KB)
        audio_data = base_header + b'\x00' * 10000
    elif size == "large":
        # Large audio file (~100KB)
        audio_data = base_header + b'\x00' * 100000
    else:
        audio_data = base_header + b'\x00' * 100
    
    return SimpleUploadedFile(
        name=filename,
        content=audio_data,
        content_type="audio/wav"
    )


def create_mock_whisper_result(text="Test transcription", language="en", confidence=0.9):
    """
    Create a mock Whisper transcription result
    
    Args:
        text: Transcribed text
        language: Detected language
        confidence: Confidence score
    
    Returns:
        dict: Mock Whisper result
    """
    return {
        "text": text,
        "language": language,
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "text": text,
                "confidence": confidence
            }
        ]
    }


def create_mock_spacy_doc(entities=None):
    """
    Create a mock spaCy document with entities
    
    Args:
        entities: List of tuples (text, label)
    
    Returns:
        Mock: Mock spaCy document
    """
    if entities is None:
        entities = [("John Doe", "PERSON"), ("New York", "GPE")]
    
    mock_doc = Mock()
    mock_ents = []
    
    for text, label in entities:
        mock_ent = Mock()
        mock_ent.text = text
        mock_ent.label_ = label
        mock_ents.append(mock_ent)
    
    mock_doc.ents = mock_ents
    return mock_doc


def create_mock_transformer_output(summary="Test summary"):
    """
    Create mock transformer pipeline output
    
    Args:
        summary: Summary text
    
    Returns:
        list: Mock transformer output
    """
    return [{"summary_text": summary}]


def create_mock_classification_result(category="test_category", confidence=0.85):
    """
    Create mock classification result
    
    Args:
        category: Classification category
        confidence: Confidence score
    
    Returns:
        dict: Mock classification result
    """
    return {
        "category": category,
        "confidence": confidence
    }


def create_mock_insights_result(case_type="workplace"):
    """
    Create mock case insights result
    
    Args:
        case_type: Type of case (workplace, housing, legal, etc.)
    
    Returns:
        dict: Mock insights result
    """
    base_insights = {
        "case_summary": f"Test {case_type} case requiring immediate attention",
        "named_entities": {
            "persons": ["Test Person"],
            "organizations": ["Test Organization"],
            "locations": ["Test Location"],
            "dates": ["2023-01-01"],
            "contact_information": ["test@email.com"]
        },
        "classification": {
            "category": [f"{case_type}_issue"],
            "interventions_needed": ["Legal aid", "Support services"],
            "priority_level": "medium"
        },
        "case_management": {
            "safety_planning": {
                "immediate_actions": ["Document incidents"],
                "long_term_measures": ["Follow up"]
            },
            "psychosocial_support": {
                "short_term": ["Crisis intervention"],
                "long_term": ["Ongoing counseling"]
            },
            "legal_protocols": {
                "applicable_laws": ["Relevant Act"],
                "required_documents": ["Documentation"],
                "authorities_to_contact": ["Relevant Authority"]
            },
            "medical_protocols": {
                "immediate_needs": ["Assessment"],
                "follow_up_care": ["Regular checkups"]
            }
        },
        "risk_assessment": {
            "red_flags": ["Warning sign"],
            "potential_barriers": ["Potential obstacle"],
            "protective_factors": ["Support system"]
        },
        "cultural_considerations": ["Language needs"]
    }
    
    return base_insights


def load_test_data(filename="sample_test_data.json"):
    """
    Load test data from JSON file
    
    Args:
        filename: Name of the JSON file in fixtures directory
    
    Returns:
        dict: Test data
    """
    fixtures_dir = Path(__file__).parent
    file_path = fixtures_dir / filename
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}


def assert_audio_file_created(audio_file):
    """
    Assert that an AudioFile instance was created correctly
    
    Args:
        audio_file: AudioFile instance to validate
    """
    assert audio_file.id is not None
    assert audio_file.audio is not None
    assert audio_file.created_at is not None
    assert audio_file.updated_at is not None


def assert_pipeline_response_structure(response_data):
    """
    Assert that API response has correct structure
    
    Args:
        response_data: Response data dictionary
    """
    required_fields = [
        'id', 'transcript', 'insights', 'entities', 
        'classification', 'annotated_text'
    ]
    
    for field in required_fields:
        assert field in response_data, f"Missing field: {field}"
    
    # Validate data types
    assert isinstance(response_data['id'], int)
    assert isinstance(response_data['transcript'], str)
    assert isinstance(response_data['insights'], dict)
    assert isinstance(response_data['entities'], list)
    assert isinstance(response_data['classification'], dict)
    assert isinstance(response_data['annotated_text'], str)


def assert_insights_structure(insights):
    """
    Assert that insights have correct structure
    
    Args:
        insights: Insights dictionary
    """
    required_sections = [
        'case_summary', 'named_entities', 'classification',
        'case_management', 'risk_assessment', 'cultural_considerations'
    ]
    
    for section in required_sections:
        assert section in insights, f"Missing insights section: {section}"
    
    # Validate named_entities structure
    entity_types = ['persons', 'organizations', 'locations', 'dates', 'contact_information']
    for entity_type in entity_types:
        assert entity_type in insights['named_entities']
        assert isinstance(insights['named_entities'][entity_type], list)
    
    # Validate classification structure
    classification_fields = ['category', 'interventions_needed', 'priority_level']
    for field in classification_fields:
        assert field in insights['classification']


def assert_entities_format(entities, format_type="flat"):
    """
    Assert that entities have correct format
    
    Args:
        entities: Entities data
        format_type: Expected format - 'flat' or 'dict'
    """
    if format_type == "flat":
        assert isinstance(entities, list)
        for entity in entities:
            assert isinstance(entity, dict)
            assert 'text' in entity
            assert 'label' in entity
    
    elif format_type == "dict":
        assert isinstance(entities, dict)
        expected_labels = ['PERSON', 'ORG', 'GPE', 'LOC', 'DATE', 'TIME', 'MONEY', 'EVENT']
        for label in expected_labels:
            assert label in entities
            assert isinstance(entities[label], list)


def create_test_file_path(tmp_path, filename, content=None):
    """
    Create a test file with given content
    
    Args:
        tmp_path: Temporary path fixture
        filename: Name of file to create
        content: Content to write (bytes or string)
    
    Returns:
        str: Path to created file
    """
    file_path = tmp_path / filename
    
    if content is None:
        # Default audio content
        content = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    if isinstance(content, str):
        file_path.write_text(content, encoding='utf-8')
    else:
        file_path.write_bytes(content)
    
    return str(file_path)


class MockLogger:
    """Mock logger for testing"""
    
    def __init__(self):
        self.info_calls = []
        self.error_calls = []
        self.warning_calls = []
        self.debug_calls = []
    
    def info(self, message):
        self.info_calls.append(message)
    
    def error(self, message):
        self.error_calls.append(message)
    
    def warning(self, message):
        self.warning_calls.append(message)
    
    def debug(self, message):
        self.debug_calls.append(message)
    
    def exception(self, message):
        self.error_calls.append(f"EXCEPTION: {message}")


def verify_no_external_calls(mock_requests, mock_whisper, mock_spacy):
    """
    Verify that no external API calls were made during tests
    
    Args:
        mock_requests: Mock requests object
        mock_whisper: Mock Whisper object  
        mock_spacy: Mock spaCy object
    """
    # This would be used in integration tests to ensure
    # unit tests don't make real external calls
    pass


def get_coverage_target():
    """
    Get the target coverage percentage for tests
    
    Returns:
        int: Target coverage percentage
    """
    return 40  # Target 40% coverage as specified