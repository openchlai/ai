import pytest
from core.serializers import AudioFileSerializer
from core.models import AudioFile


@pytest.mark.django_db
class TestAudioFileSerializer:
    """Test AudioFileSerializer functionality"""

    def test_serialize_audio_file(self, audio_file_factory):
        """Test serializing an AudioFile instance"""
        audio_file = audio_file_factory()
        serializer = AudioFileSerializer(audio_file)
        data = serializer.data
        
        # Check that all expected fields are present
        expected_fields = [
            'id', 'audio', 'transcript', 'translated_text', 
            'annotated_text', 'summary', 'insights', 'created_at'
        ]
        
        for field in expected_fields:
            assert field in data
        
        # Check field values
        assert data['id'] == audio_file.id
        assert data['transcript'] == audio_file.transcript
        assert data['translated_text'] == audio_file.translated_text
        assert data['annotated_text'] == audio_file.annotated_text
        assert data['summary'] == audio_file.summary
        assert data['insights'] == audio_file.insights

    def test_deserialize_audio_file(self, sample_audio_file):
        """Test deserializing data to create AudioFile"""
        data = {'audio': sample_audio_file}
        serializer = AudioFileSerializer(data=data)
        
        assert serializer.is_valid()
        audio_file = serializer.save()
        
        assert isinstance(audio_file, AudioFile)
        assert audio_file.audio is not None
        assert audio_file.id is not None

    def test_serializer_validation_with_invalid_data(self):
        """Test serializer validation with invalid data"""
        data = {}  # Missing required 'audio' field
        serializer = AudioFileSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'audio' in serializer.errors

    def test_read_only_fields(self, sample_audio_file):
        """Test that read-only fields cannot be set during creation"""
        data = {
            'audio': sample_audio_file,
            'transcript': 'Should be ignored',
            'translated_text': 'Should be ignored',
            'annotated_text': 'Should be ignored',
            'summary': 'Should be ignored',
            'insights': {'should': 'be ignored'}
        }
        
        serializer = AudioFileSerializer(data=data)
        assert serializer.is_valid()
        audio_file = serializer.save()
        
        # Read-only fields should be None since they're not set in processing
        assert audio_file.transcript is None
        assert audio_file.translated_text is None
        assert audio_file.annotated_text is None
        assert audio_file.summary is None
        assert audio_file.insights is None

    def test_serializer_meta_configuration(self):
        """Test serializer Meta class configuration"""
        serializer = AudioFileSerializer()
        meta = serializer.Meta
        
        # Check model
        assert meta.model == AudioFile
        
        # Check fields
        expected_fields = [
            'id', 'audio', 'transcript', 'translated_text', 
            'annotated_text', 'summary', 'insights', 'created_at'
        ]
        assert set(meta.fields) == set(expected_fields)
        
        # Check read-only fields
        expected_read_only = [
            'transcript', 'translated_text', 'annotated_text', 
            'summary', 'insights', 'created_at'
        ]
        assert set(meta.read_only_fields) == set(expected_read_only)

    def test_insights_field_serialization(self, audio_file_factory):
        """Test that insights JSONField is properly serialized"""
        complex_insights = {
            "case_summary": "Test case summary",
            "named_entities": {
                "persons": ["John Doe"],
                "locations": ["New York"]
            },
            "classification": {
                "category": ["Legal aid needed"],
                "priority_level": "high"
            }
        }
        
        audio_file = audio_file_factory(insights=complex_insights)
        serializer = AudioFileSerializer(audio_file)
        data = serializer.data
        
        assert data['insights'] == complex_insights
        assert data['insights']['case_summary'] == "Test case summary"
        assert data['insights']['classification']['priority_level'] == "high"