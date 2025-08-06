
import pytest
from unittest.mock import patch
from core.pipeline.insights import generate_case_insights

@pytest.mark.unit
@patch('core.pipeline.insights.create_fallback_insights')
@patch('core.pipeline.insights.summarizer.summarize')
@patch('core.pipeline.insights.ner.extract_entities')
@patch('core.pipeline.insights.classifier.classify_case')
def test_generate_case_insights(mock_classify_case, mock_extract_entities, mock_summarize, mock_create_fallback_insights):
    """
    Test the generate_case_insights function.
    """
    mock_summarize.return_value = "This is a test summary."
    mock_extract_entities.return_value = {"PERSON": ["test"], "ORG": [], "GPE": [], "LOC": [], "DATE": [], "TIME": [], "MONEY": [], "EVENT": [], "CONTACT_INFO": []}
    mock_classify_case.return_value = {"category": ["test"], "interventions_needed": ["test"], "priority_level": "medium"}
    mock_create_fallback_insights.return_value = {"key": "value"}

    # Call the function
    transcript = "This is a test transcript."
    insights = generate_case_insights(transcript)

    # Check the result
    assert insights == {"key": "value"}

    # Check that the fallback function was called
    mock_create_fallback_insights.assert_called_once()
