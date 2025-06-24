import pytest
import json
from unittest.mock import patch, Mock
from core.pipeline.insights import generate_case_insights


class TestInsightsGeneration:
    """Test case insights generation pipeline"""

    @patch('requests.post')
    def test_generate_case_insights_success(self, mock_post):
        """Test successful insights generation"""
        # Mock API response
        mock_response = Mock()
        mock_insights = {
            "case_summary": "Test case involving workplace issues",
            "named_entities": {
                "persons": ["John Doe"],
                "organizations": ["ABC Company"],
                "locations": ["New York"],
                "dates": ["2023-01-15"],
                "contact_information": ["555-1234"]
            },
            "classification": {
                "category": ["Workplace abuse"],
                "interventions_needed": ["Legal aid", "Counseling"],
                "priority_level": "high"
            },
            "case_management": {
                "safety_planning": {
                    "immediate_actions": ["Contact supervisor"],
                    "long_term_measures": ["Document incidents"]
                },
                "psychosocial_support": {
                    "short_term": ["Crisis counseling"],
                    "long_term": ["Therapy sessions"]
                },
                "legal_protocols": {
                    "applicable_laws": ["Labor Protection Act"],
                    "required_documents": ["Employment contract"],
                    "authorities_to_contact": ["Labor Department"]
                },
                "medical_protocols": {
                    "immediate_needs": ["Stress assessment"],
                    "follow_up_care": ["Regular checkups"]
                }
            },
            "risk_assessment": {
                "red_flags": ["Hostile work environment"],
                "potential_barriers": ["Fear of retaliation"],
                "protective_factors": ["Union support"]
            },
            "cultural_considerations": ["Consider local customs"]
        }
        
        mock_response.json.return_value = {
            'response': json.dumps(mock_insights)
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        transcript = "John Doe from ABC Company in New York reported workplace harassment."
        result = generate_case_insights(transcript)
        
        # Verify API call
        mock_post.assert_called_once_with(
            'http://192.168.10.6:11434/api/generate',
            json={
                'model': 'mistral',
                'prompt': pytest.approx(str, abs=100),  # Approximate match for long prompt
                'stream': False
            },
            timeout=30
        )
        
        # Verify result structure
        assert result == mock_insights
        assert result["case_summary"] == "Test case involving workplace issues"
        assert "John Doe" in result["named_entities"]["persons"]
        assert result["classification"]["priority_level"] == "high"

    @patch('requests.post')
    def test_generate_case_insights_api_error(self, mock_post):
        """Test handling of API request errors"""
        mock_post.side_effect = Exception("API connection failed")
        
        transcript = "Test transcript"
        
        with pytest.raises(Exception, match="API connection failed"):
            generate_case_insights(transcript)

    @patch('requests.post')
    def test_generate_case_insights_http_error(self, mock_post):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_post.return_value = mock_response
        
        transcript = "Test transcript"
        
        with pytest.raises(Exception, match="HTTP 500 Error"):
            generate_case_insights(transcript)

    @patch('requests.post')
    def test_generate_case_insights_invalid_json(self, mock_post):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'invalid json format'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        transcript = "Test transcript"
        
        with pytest.raises(json.JSONDecodeError):
            generate_case_insights(transcript)

    @patch('requests.post')
    def test_generate_case_insights_timeout(self, mock_post):
        """Test handling of request timeout"""
        mock_post.side_effect = Exception("Request timeout")
        
        transcript = "Test transcript"
        
        with pytest.raises(Exception, match="Request timeout"):
            generate_case_insights(transcript)

    @patch('requests.post')
    def test_generate_case_insights_prompt_content(self, mock_post):
        """Test that prompt contains expected content"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': '{"case_summary": "test"}'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        transcript = "Worker reported safety violations at construction site."
        generate_case_insights(transcript)
        
        # Get the actual prompt from the mock call
        call_args = mock_post.call_args
        prompt = call_args[1]['json']['prompt']
        
        # Verify prompt contains key elements
        assert "trauma-informed social worker" in prompt
        assert "case_summary" in prompt
        assert "named_entities" in prompt
        assert "classification" in prompt
        assert "risk_assessment" in prompt
        assert transcript in prompt

    @patch('requests.post')
    def test_generate_case_insights_complex_case(self, mock_post):
        """Test insights generation for complex case"""
        complex_insights = {
            "case_summary": "Multi-faceted case involving labor exploitation and housing issues",
            "named_entities": {
                "persons": ["Maria Santos", "John Manager"],
                "organizations": ["Construction Co", "Housing Authority"],
                "locations": ["Downtown District", "Worker Housing"],
                "dates": ["2023-01-01", "2023-06-15"],
                "contact_information": ["maria@email.com", "555-9876"]
            },
            "classification": {
                "category": ["Labor exploitation", "Housing insecurity"],
                "interventions_needed": ["Legal aid", "Housing assistance", "Medical attention"],
                "priority_level": "high"
            },
            "case_management": {
                "safety_planning": {
                    "immediate_actions": ["Secure safe housing", "Document violations"],
                    "long_term_measures": ["Legal proceedings", "Advocacy support"]
                },
                "psychosocial_support": {
                    "short_term": ["Crisis intervention", "Cultural broker"],
                    "long_term": ["Trauma therapy", "Support groups"]
                },
                "legal_protocols": {
                    "applicable_laws": ["Labor Standards Act", "Housing Rights Act"],
                    "required_documents": ["Work contracts", "Pay stubs", "Housing agreements"],
                    "authorities_to_contact": ["Labor Inspector", "Housing Authority", "Police"]
                },
                "medical_protocols": {
                    "immediate_needs": ["Physical examination", "Mental health screening"],
                    "follow_up_care": ["Specialized treatment", "Regular monitoring"]
                }
            },
            "risk_assessment": {
                "red_flags": ["Employer threats", "Unsafe housing", "Language barriers"],
                "potential_barriers": ["Immigration status", "Economic dependence", "Social isolation"],
                "protective_factors": ["Community support", "Documentation available", "Willing to cooperate"]
            },
            "cultural_considerations": ["Language interpretation", "Cultural sensitivity", "Religious considerations"]
        }
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': json.dumps(complex_insights)
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        complex_transcript = """
        Maria Santos reported that her employer, John Manager at Construction Co, 
        has been withholding wages and forcing workers to live in substandard housing 
        in the Downtown District. The situation has been ongoing since January 2023.
        Contact: maria@email.com, 555-9876
        """
        
        result = generate_case_insights(complex_transcript)
        
        assert len(result["named_entities"]["persons"]) == 2
        assert len(result["classification"]["category"]) == 2
        assert result["classification"]["priority_level"] == "high"
        assert len(result["risk_assessment"]["red_flags"]) == 3
        assert len(result["cultural_considerations"]) == 3