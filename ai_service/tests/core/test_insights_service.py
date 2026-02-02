import json
import pytest
from unittest.mock import patch, MagicMock
import requests


class TestSanitizeJsonResponse:
    """Test JSON sanitization from LLM responses"""

    def test_sanitize_removes_markdown_code_blocks(self):
        """Test removal of markdown code blocks"""
        from app.core.insights_service import sanitize_json_response

        response = '```json\n{"case_summary": "test"}\n```'
        result = sanitize_json_response(response)

        assert '```' not in result
        assert '{"case_summary": "test"}' in result

    def test_sanitize_extracts_case_summary_json(self):
        """Test extraction of JSON with case_summary"""
        from app.core.insights_service import sanitize_json_response

        response = 'Some text {"case_summary": "important", "other": "data"} more text'
        result = sanitize_json_response(response)

        assert 'case_summary' in result
        assert 'Some text' not in result

    def test_sanitize_extracts_generic_json(self):
        """Test extraction of generic JSON when no case_summary"""
        from app.core.insights_service import sanitize_json_response

        response = 'Text before {"risk_level": "High", "data": "value"} text after'
        result = sanitize_json_response(response)

        assert '{' in result
        assert '}' in result

    def test_sanitize_returns_cleaned_text_when_no_json(self):
        """Test handling of non-JSON responses"""
        from app.core.insights_service import sanitize_json_response

        response = '```This is just plain text```'
        result = sanitize_json_response(response)

        assert '```' not in result
        assert 'This is just plain text' in result

    def test_sanitize_handles_nested_json(self):
        """Test handling of nested JSON structures"""
        from app.core.insights_service import sanitize_json_response

        response = '''```json
        {
            "case_summary": "test",
            "nested": {"key": "value"}
        }
        ```'''
        result = sanitize_json_response(response)

        assert 'case_summary' in result
        assert '```' not in result


class TestCallOllama:
    """Test Ollama API calls"""

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_success(self, mock_session_class):
        """Test successful Ollama API call"""
        from app.core.insights_service import call_ollama

        # Setup mock
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'Generated insights'}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        result = call_ollama( 'Test prompt')

        assert result == 'Generated insights'
        mock_session.post.assert_called_once()

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_with_custom_endpoint(self, mock_session_class):
        """Test Ollama call with custom endpoint"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'Result'}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        custom_endpoint = "http://custom:11434/api/generate"
        result = call_ollama( 'Test', endpoint=custom_endpoint)

        assert result == 'Result'
        call_args = mock_session.post.call_args
        assert call_args[0][0] == custom_endpoint

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_strips_whitespace(self, mock_session_class):
        """Test that response is stripped of whitespace"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': '  Result with spaces  '}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        result = call_ollama('Test')

        assert result == 'Result with spaces'

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_handles_http_error(self, mock_session_class):
        """Test handling of HTTP errors"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.HTTPError("Server error")
        mock_session_class.return_value = mock_session

        result = call_ollama( 'Test')

        assert result is None

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_handles_timeout(self, mock_session_class):
        """Test handling of request timeout"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.Timeout("Timeout")
        mock_session_class.return_value = mock_session

        result = call_ollama('Test')

        assert result is None

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_handles_connection_error(self, mock_session_class):
        """Test handling of connection errors"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_session.post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_session_class.return_value = mock_session

        result = call_ollama('Test')

        assert result is None

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_uses_retry_logic(self, mock_session_class):
        """Test that retry logic is configured"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'Success'}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        call_ollama( 'Test')

        # Verify session mount was called (retry adapter setup)
        assert mock_session.mount.called

    @patch('app.core.insights_service.requests.Session')
    def test_call_ollama_sends_correct_payload(self, mock_session_class):
        """Test that correct payload is sent"""
        from app.core.insights_service import call_ollama

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'Result'}
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        call_ollama('Test prompt')

        call_args = mock_session.post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == 'mistral'
        assert payload['prompt'] == 'Test prompt'
        assert payload['stream'] is False


class TestGenerateCaseInsights:
    """Test case insights generation"""

    @patch('app.core.insights_service.call_ollama')
    def test_generate_case_insights_success(self, mock_call_ollama):
        """Test successful insights generation"""
        from app.core.insights_service import generate_case_insights

        mock_response = json.dumps({
            "case_overview": {
                "risk_level": "High",
                "suggested_disposition": "Immediate action",
                "rationale_summary": "Case requires attention"
            },
            "data_quality": {
                "insight_confidence_score": 0.85
            },
            "extracted_entities": {
                "names": ["John Doe"],
                "locations": ["Nairobi"],
                "organizations": ["UNICEF"],
                "dates": ["2024-01-15"]
            },
            "classification": {
                "primary_category": "Abuse",
                "sub_category": "Physical",
                "intervention": "Referral",
                "priority": "High"
            },
            "case_tags_and_keywords": {
                "keywords": ["urgent", "child_protection"]
            }
        })
        mock_call_ollama.return_value = mock_response

        result = generate_case_insights("Test transcript", None)

        assert result['risk_level'] == 'High'
        assert result['confidence_score'] == 0.85
        assert 'John Doe' in result['extracted_entities']['names']

    @patch('app.core.insights_service.call_ollama')
    def test_generate_case_insights_with_classification(self, mock_call_ollama):
        """Test insights generation with classification results"""
        from app.core.insights_service import generate_case_insights

        classification_results = {
            'main_category': 'Abuse',
            'sub_category': 'Physical',
            'intervention': 'Police Referral',
            'priority': 'Critical',
            'confidence': 0.92
        }

        mock_response = json.dumps({
            "risk_level": "Critical",
            "suggested_disposition": "Police referral",
            "rationale_summary": "Serious abuse case",
            "confidence_score": 0.9,
            "extracted_entities": {
                "names": [],
                "locations": [],
                "organizations": [],
                "dates": []
            },
            "category_suggestions": {
                "primary_category": "Abuse",
                "sub_category": "Physical",
                "intervention": "Police Referral",
                "priority": "Critical",
                "tags": ["abuse", "critical"]
            },
            "priority": "Critical"
        })
        mock_call_ollama.return_value = mock_response

        result = generate_case_insights("Test transcript", classification_results)

        assert result['category_suggestions']['primary_category'] == 'Abuse'
        assert result['category_suggestions']['priority'] == 'Critical'

    @patch('app.core.insights_service.call_ollama')
    def test_generate_case_insights_ollama_unavailable(self, mock_call_ollama):
        """Test handling when Ollama is unavailable"""
        from app.core.insights_service import generate_case_insights

        mock_call_ollama.return_value = None

        result = generate_case_insights("Test transcript", None)

        assert result == {"error": "ai-service unavailable"}

    @patch('app.core.insights_service.call_ollama')
    @patch('app.core.insights_service.sanitize_json_response')
    def test_generate_case_insights_handles_invalid_json(self, mock_sanitize, mock_call_ollama):
        """Test handling of invalid JSON responses"""
        from app.core.insights_service import generate_case_insights

        # First call returns invalid JSON, sanitizer fixes it
        mock_call_ollama.return_value = "```json\nInvalid JSON\n```"
        mock_sanitize.return_value = json.dumps({"risk_level": "Low", "error": "Sanitized"})

        result = generate_case_insights("Test", None)

        # Should have called sanitizer
        mock_sanitize.assert_called_once()
        assert result['risk_level'] == 'Low'

    @patch('app.core.insights_service.call_ollama')
    def test_generate_case_insights_defaults_for_missing_classification(self, mock_call_ollama):
        """Test default values when classification is None"""
        from app.core.insights_service import generate_case_insights

        mock_response = json.dumps({
            "case_overview": {
                "risk_level": "Medium",
                "suggested_disposition": "Monitor",
                "rationale_summary": "Standard case"
            },
            "data_quality": {
                "insight_confidence_score": 0.7
            },
            "extracted_entities": {
                "names": [],
                "locations": [],
                "organizations": [],
                "dates": []
            },
            "classification": {
                "primary_category": "Unknown",
                "sub_category": "Unknown",
                "intervention": "Unknown",
                "priority": "Unknown"
            },
            "case_tags_and_keywords": {
                "keywords": []
            }
        })
        mock_call_ollama.return_value = mock_response

        result = generate_case_insights("Test transcript", None)

        # Should have Unknown values when no classification provided
        assert result['category_suggestions']['primary_category'] == 'Unknown'

    @patch('app.core.insights_service.call_ollama')
    def test_generate_case_insights_builds_prompt_correctly(self, mock_call_ollama):
        """Test that prompt is built with correct structure"""
        from app.core.insights_service import generate_case_insights

        mock_response = json.dumps({
            "case_overview": {"risk_level": "Low"},
            "classification": {}
        })
        mock_call_ollama.return_value = mock_response

        test_transcript = "Test case narrative"
        classification = {
            'main_category': 'Neglect',
            'sub_category': 'Supervision',
            'intervention': 'Home Visit',
            'priority': 'Medium',
            'confidence': 0.8
        }

        generate_case_insights(test_transcript, classification)

        # Verify call_ollama was called with prompt as first argument
        call_args = mock_call_ollama.call_args
        prompt = call_args[0][0]

        # Verify prompt contains transcript and classification
        assert test_transcript in prompt
        assert 'Neglect' in prompt
        assert 'Supervision' in prompt

    @patch('app.core.insights_service.call_ollama')
    def test_generate_case_insights_without_classification_no_section(self, mock_call_ollama):
        """Test prompt without classification section"""
        from app.core.insights_service import generate_case_insights

        mock_response = json.dumps({
            "case_overview": {"risk_level": "Low"},
            "classification": {}
        })
        mock_call_ollama.return_value = mock_response

        generate_case_insights("Transcript", None)

        # Verify prompt was built - prompt is now the first argument
        call_args = mock_call_ollama.call_args
        prompt = call_args[0][0]

        # Should have Unknown defaults when no classification provided
        assert 'Unknown' in prompt
