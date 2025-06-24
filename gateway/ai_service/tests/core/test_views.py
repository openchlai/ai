import pytest
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework import status
from core.models import AudioFile


@pytest.mark.django_db
class TestAudioUploadView:
    """Test AudioUploadView API endpoint"""

    def test_successful_audio_upload_and_processing(self, api_client, sample_audio_file):
        """Test successful audio upload with full processing pipeline"""
        url = reverse('audio-upload')
        
        # Mock all pipeline components
        with patch('core.pipeline.transcription.transcribe') as mock_transcribe, \
             patch('core.pipeline.insights.generate_case_insights') as mock_insights, \
             patch('core.pipeline.ner.extract_entities') as mock_ner, \
             patch('core.pipeline.classifier.classify_case') as mock_classify, \
             patch('core.utils.highlighter.highlight_text') as mock_highlight:
            
            # Configure mocks
            mock_transcribe.return_value = "This is a test transcription"
            mock_insights.return_value = {
                "case_summary": "Test case summary",
                "classification": {"category": "test", "priority_level": "medium"}
            }
            mock_ner.return_value = [
                {"text": "test", "label": "MISC"}
            ]
            mock_classify.return_value = {
                "category": "test_category",
                "confidence": 0.95
            }
            mock_highlight.return_value = "This is a [test|MISC] transcription"
            
            # Make request
            response = api_client.post(url, {'audio': sample_audio_file}, format='multipart')
            
            # Assertions
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            
            # Check response structure
            assert 'id' in data
            assert 'transcript' in data
            assert 'insights' in data
            assert 'entities' in data
            assert 'classification' in data
            assert 'annotated_text' in data
            
            # Check response values
            assert data['transcript'] == "This is a test transcription"
            assert data['insights']['case_summary'] == "Test case summary"
            assert len(data['entities']) == 1
            assert data['entities'][0]['text'] == "test"
            assert data['classification']['category'] == "test_category"
            assert data['annotated_text'] == "This is a [test|MISC] transcription"
            
            # Verify database record was created
            audio_file = AudioFile.objects.get(id=data['id'])
            assert audio_file.transcript == "This is a test transcription"
            assert audio_file.annotated_text == "This is a [test|MISC] transcription"

    def test_upload_without_audio_file(self, api_client):
        """Test upload request without audio file"""
        url = reverse('audio-upload')
        response = api_client.post(url, {}, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'audio' in data  # Should have validation error for missing audio field

    def test_transcription_failure_handling(self, api_client, sample_audio_file):
        """Test handling of transcription pipeline failure"""
        url = reverse('audio-upload')
        
        with patch('core.pipeline.transcription.transcribe') as mock_transcribe:
            mock_transcribe.side_effect = Exception("Transcription failed")
            
            response = api_client.post(url, {'audio': sample_audio_file}, format='multipart')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert 'error' in data
            assert data['error'] == "Processing failed"
            assert 'details' in data
            
            # Verify no AudioFile was created in database
            assert AudioFile.objects.count() == 0

    def test_insights_generation_failure_handling(self, api_client, sample_audio_file):
        """Test handling of insights generation failure"""
        url = reverse('audio-upload')
        
        with patch('core.pipeline.transcription.transcribe') as mock_transcribe, \
             patch('core.pipeline.insights.generate_case_insights') as mock_insights:
            
            mock_transcribe.return_value = "Test transcription"
            mock_insights.side_effect = Exception("Insights generation failed")
            
            response = api_client.post(url, {'audio': sample_audio_file}, format='multipart')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert 'error' in data
            assert "Insights generation failed" in data['details']

    def test_ner_failure_handling(self, api_client, sample_audio_file):
        """Test handling of NER pipeline failure"""
        url = reverse('audio-upload')
        
        with patch('core.pipeline.transcription.transcribe') as mock_transcribe, \
             patch('core.pipeline.insights.generate_case_insights') as mock_insights, \
             patch('core.pipeline.ner.extract_entities') as mock_ner:
            
            mock_transcribe.return_value = "Test transcription"
            mock_insights.return_value = {"test": "insights"}
            mock_ner.side_effect = Exception("NER failed")
            
            response = api_client.post(url, {'audio': sample_audio_file}, format='multipart')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_file_cleanup_on_processing_failure(self, api_client, sample_audio_file):
        """Test that audio file is cleaned up when processing fails"""
        url = reverse('audio-upload')
        
        with patch('core.pipeline.transcription.transcribe') as mock_transcribe:
            mock_transcribe.side_effect = Exception("Processing failed")
            
            # Verify no files exist before test
            initial_count = AudioFile.objects.count()
            
            response = api_client.post(url, {'audio': sample_audio_file}, format='multipart')
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            
            # Verify no AudioFile was left in database
            assert AudioFile.objects.count() == initial_count

    @pytest.mark.api
    def test_response_format_structure(self, api_client, sample_audio_file):
        """Test that response has correct structure and data types"""
        url = reverse('audio-upload')
        
        with patch('core.pipeline.transcription.transcribe') as mock_transcribe, \
             patch('core.pipeline.insights.generate_case_insights') as mock_insights, \
             patch('core.pipeline.ner.extract_entities') as mock_ner, \
             patch('core.pipeline.classifier.classify_case') as mock_classify, \
             patch('core.utils.highlighter.highlight_text') as mock_highlight:
            
            # Configure mocks with specific return types
            mock_transcribe.return_value = "Test transcript"
            mock_insights.return_value = {"key": "value"}
            mock_ner.return_value = [{"text": "entity", "label": "LABEL"}]
            mock_classify.return_value = {"category": "test", "confidence": 0.9}
            mock_highlight.return_value = "Highlighted text"
            
            response = api_client.post(url, {'audio': sample_audio_file}, format='multipart')
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            
            # Check data types
            assert isinstance(data['id'], int)
            assert isinstance(data['transcript'], str)
            assert isinstance(data['insights'], dict)
            assert isinstance(data['entities'], list)
            assert isinstance(data['classification'], dict)
            assert isinstance(data['annotated_text'], str)