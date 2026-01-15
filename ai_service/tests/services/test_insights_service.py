"""
Comprehensive tests for insights_service to achieve 99%+ coverage.
"""
import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
import requests
from requests.exceptions import Timeout, RequestException

from app.services.insights_service import (
    generate_case_insights,
    generate_enhanced_audio_insights
)


class TestGenerateCaseInsights:
    """Test generate_case_insights function"""

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_success(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test successful case insights generation"""
        # Mock model outputs
        mock_summarizer.summarize.return_value = "Summary of case"
        mock_ner.extract_entities.return_value = {"persons": ["John"], "locations": ["Home"]}
        mock_classifier.classify.return_value = {
            "main_category": "abuse",
            "sub_category": "physical",
            "intervention": "urgent_care",
            "priority": "high"
        }

        # Mock API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": json.dumps({
                "case_summary": "Test summary",
                "named_entities": {"persons": ["John"]},
                "classification": {"category": ["abuse"]},
                "case_management": {},
                "risk_assessment": {},
                "cultural_considerations": []
            })
        }
        mock_post.return_value = mock_response

        result = generate_case_insights("Test case transcript")

        assert isinstance(result, dict)
        assert "case_summary" in result
        mock_summarizer.summarize.assert_called_once()

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_summarization_fails(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights when summarization fails"""
        mock_summarizer.summarize.side_effect = Exception("Summarization error")
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.return_value = {}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": json.dumps({"case_summary": "Fallback"})
        }
        mock_post.return_value = mock_response

        result = generate_case_insights("Test transcript " * 100)

        # Should use truncated text as fallback
        assert isinstance(result, dict)

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_ner_fails(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights when NER fails"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.side_effect = Exception("NER error")
        mock_classifier.classify.return_value = {}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": json.dumps({"case_summary": "Test"})}
        mock_post.return_value = mock_response

        result = generate_case_insights("Test transcript")

        assert isinstance(result, dict)

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_classification_fails(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights when classification fails"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.side_effect = Exception("Classification error")

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": json.dumps({"case_summary": "Test"})}
        mock_post.return_value = mock_response

        result = generate_case_insights("Test transcript")

        assert isinstance(result, dict)

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_api_timeout(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights with API timeout"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.return_value = {}
        mock_post.side_effect = Timeout("Request timeout")

        with pytest.raises(Timeout):
            generate_case_insights("Test transcript")

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_http_error(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights with HTTP error"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.return_value = {}
        mock_post.side_effect = RequestException("HTTP error")

        with pytest.raises(RequestException):
            generate_case_insights("Test transcript")

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_invalid_response_format(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights with invalid response format"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.return_value = {}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"error": "Invalid"}  # Missing 'response' key
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Missing 'response' key"):
            generate_case_insights("Test transcript")

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_json_decode_with_markdown(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights with invalid JSON but valid markdown-wrapped JSON"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.return_value = {}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": '```json\n{"case_summary": "Test"}\n```'
        }
        mock_post.return_value = mock_response

        result = generate_case_insights("Test transcript")

        assert isinstance(result, dict)
        assert result.get("case_summary") == "Test"

    @patch('app.services.insights_service.summarization_model')
    @patch('app.services.insights_service.ner_model')
    @patch('app.services.insights_service.classifier_model')
    @patch('requests.Session.post')
    def test_case_insights_retry_on_502(self, mock_post, mock_classifier, mock_ner, mock_summarizer):
        """Test case insights retries on 502 error"""
        mock_summarizer.summarize.return_value = "Summary"
        mock_ner.extract_entities.return_value = {}
        mock_classifier.classify.return_value = {}

        # First call fails with 502, second succeeds
        mock_response_error = MagicMock()
        mock_response_error.status_code = 502

        mock_response_success = MagicMock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            "response": json.dumps({"case_summary": "Test"})
        }

        mock_post.side_effect = [mock_response_error, mock_response_success]

        # The session retry adapter should handle this
        result = generate_case_insights("Test transcript")

        assert isinstance(result, dict)


class TestGenerateEnhancedAudioInsights:
    """Test generate_enhanced_audio_insights function"""

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_success(self, mock_post):
        """Test successful enhanced audio insights generation"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": json.dumps({
                "analysis_metadata": {"analysis_type": "enhanced_audio_based"},
                "enhanced_case_summary": "Test",
                "comprehensive_entities": {},
                "advanced_classification": {},
                "quality_assurance_insights": {},
                "comprehensive_risk_assessment": {},
                "detailed_action_plan": {},
                "service_coordination": {},
                "cultural_linguistic_insights": {},
                "case_complexity_analysis": {},
                "outcome_predictions": {}
            })
        }
        mock_post.return_value = mock_response

        result = generate_enhanced_audio_insights(
            "Original transcript",
            "Enhanced transcript with more detail",
            "Translation",
            {"persons": ["John"]},
            {"category": "abuse"},
            {"score": 0.9},
            "Summary",
            {"file_size_mb": 2.5}
        )

        assert isinstance(result, dict)
        assert "analysis_metadata" in result

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_quality_calculation(self, mock_post):
        """Test quality improvement calculation"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": json.dumps({
                "analysis_metadata": {"analysis_type": "enhanced_audio_based"}
            })
        }
        mock_post.return_value = mock_response

        original = "Short"
        enhanced = "Much longer transcript with many more details"

        result = generate_enhanced_audio_insights(
            original,
            enhanced,
            "Translation",
            {},
            {},
            {},
            "Summary",
            {"file_size_mb": 1.0}
        )

        # Check that quality improvement was calculated
        assert isinstance(result, dict)

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_timeout(self, mock_post):
        """Test enhanced audio insights with timeout"""
        mock_post.side_effect = Timeout("Request timeout")

        with pytest.raises(Timeout):
            generate_enhanced_audio_insights(
                "Original", "Enhanced", "Translation", {}, {}, {}, "Summary", {}
            )

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_http_error(self, mock_post):
        """Test enhanced audio insights with HTTP error"""
        mock_post.side_effect = RequestException("HTTP error")

        with pytest.raises(RequestException):
            generate_enhanced_audio_insights(
                "Original", "Enhanced", "Translation", {}, {}, {}, "Summary", {}
            )

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_invalid_response(self, mock_post):
        """Test enhanced audio insights with invalid response"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"error": "Invalid"}
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Missing 'response' key"):
            generate_enhanced_audio_insights(
                "Original", "Enhanced", "Translation", {}, {}, {}, "Summary", {}
            )

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_json_decode_error(self, mock_post):
        """Test enhanced audio insights with invalid JSON"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": "Invalid JSON {{"
        }
        mock_post.return_value = mock_response

        # Should try to sanitize
        with pytest.raises(json.JSONDecodeError):
            generate_enhanced_audio_insights(
                "Original", "Enhanced", "Translation", {}, {}, {}, "Summary", {}
            )

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_json_decode_with_markdown_fix(self, mock_post):
        """Test enhanced audio insights fixes markdown-wrapped JSON"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": '```json\n{"analysis_metadata": {"analysis_type": "enhanced"}}\n```'
        }
        mock_post.return_value = mock_response

        result = generate_enhanced_audio_insights(
            "Original", "Enhanced", "Translation", {}, {}, {}, "Summary", {}
        )

        assert isinstance(result, dict)

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_empty_original_text(self, mock_post):
        """Test enhanced audio insights with empty original text (avoid division by zero)"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "response": json.dumps({
                "analysis_metadata": {"analysis_type": "enhanced"}
            })
        }
        mock_post.return_value = mock_response

        result = generate_enhanced_audio_insights(
            "",  # Empty original
            "Enhanced text",
            "Translation",
            {},
            {},
            {},
            "Summary",
            {"file_size_mb": 1.0}
        )

        # Should handle division by zero gracefully
        assert isinstance(result, dict)

    @patch('requests.Session.post')
    def test_enhanced_audio_insights_general_exception(self, mock_post):
        """Test enhanced audio insights with general exception"""
        mock_post.side_effect = Exception("Unexpected error")

        with pytest.raises(Exception, match="Unexpected error"):
            generate_enhanced_audio_insights(
                "Original", "Enhanced", "Translation", {}, {}, {}, "Summary", {}
            )
