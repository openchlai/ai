import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import AudioFile


@pytest.mark.django_db
class TestAudioFileModel:
    """Test AudioFile model functionality"""

    def test_create_audio_file_basic(self, sample_audio_file):
        """Test creating a basic AudioFile instance"""
        audio_file = AudioFile.objects.create(audio=sample_audio_file)
        
        assert audio_file.id is not None
        assert audio_file.audio is not None
        assert audio_file.created_at is not None
        assert audio_file.updated_at is not None
        assert audio_file.transcript is None
        assert audio_file.translated_text is None
        assert audio_file.annotated_text is None
        assert audio_file.summary is None
        assert audio_file.insights is None

    def test_audio_file_str_representation(self, sample_audio_file):
        """Test string representation of AudioFile"""
        audio_file = AudioFile.objects.create(audio=sample_audio_file)
        expected_str = f"AudioFile {audio_file.id} - {audio_file.created_at}"
        assert str(audio_file) == expected_str

    def test_audio_file_with_all_fields(self, sample_audio_file):
        """Test creating AudioFile with all fields"""
        test_insights = {
            "case_summary": "Test case",
            "classification": {"category": "test", "priority": "high"}
        }
        
        audio_file = AudioFile.objects.create(
            audio=sample_audio_file,
            transcript="Test transcript",
            translated_text="Test translation",
            annotated_text="Test annotation",
            summary="Test summary",
            insights=test_insights
        )
        
        assert audio_file.transcript == "Test transcript"
        assert audio_file.translated_text == "Test translation"
        assert audio_file.annotated_text == "Test annotation"
        assert audio_file.summary == "Test summary"
        assert audio_file.insights == test_insights

    def test_insights_json_field(self, sample_audio_file):
        """Test insights JSONField functionality"""
        complex_insights = {
            "case_summary": "Complex case summary",
            "named_entities": {
                "persons": ["John Doe", "Jane Smith"],
                "organizations": ["Company A"],
                "locations": ["New York", "California"]
            },
            "classification": {
                "category": ["Legal aid needed"],
                "priority_level": "high"
            }
        }
        
        audio_file = AudioFile.objects.create(
            audio=sample_audio_file,
            insights=complex_insights
        )
        
        # Retrieve from database and verify
        saved_audio_file = AudioFile.objects.get(id=audio_file.id)
        assert saved_audio_file.insights == complex_insights
        assert saved_audio_file.insights["case_summary"] == "Complex case summary"
        assert len(saved_audio_file.insights["named_entities"]["persons"]) == 2

    def test_audio_file_update_fields(self, sample_audio_file):
        """Test updating AudioFile fields"""
        audio_file = AudioFile.objects.create(audio=sample_audio_file)
        original_created_at = audio_file.created_at
        original_updated_at = audio_file.updated_at
        
        # Update fields
        audio_file.transcript = "Updated transcript"
        audio_file.summary = "Updated summary"
        audio_file.save()
        
        # Refresh from database
        audio_file.refresh_from_db()
        
        assert audio_file.transcript == "Updated transcript"
        assert audio_file.summary == "Updated summary"
        assert audio_file.created_at == original_created_at  # Should not change
        assert audio_file.updated_at >= original_updated_at  # Should be updated

    @pytest.mark.unit
    def test_audio_file_model_fields(self):
        """Test model field definitions"""
        fields = AudioFile._meta.get_fields()
        field_names = [field.name for field in fields]
        
        expected_fields = [
            'id', 'audio', 'transcript', 'translated_text', 
            'annotated_text', 'summary', 'insights', 
            'created_at', 'updated_at'
        ]
        
        for field_name in expected_fields:
            assert field_name in field_names

    def test_audio_file_cascade_delete(self, sample_audio_file):
        """Test that deleting AudioFile removes it from database"""
        audio_file = AudioFile.objects.create(audio=sample_audio_file)
        audio_file_id = audio_file.id
        
        # Delete the instance
        audio_file.delete()
        
        # Verify it's deleted from database
        assert not AudioFile.objects.filter(id=audio_file_id).exists()