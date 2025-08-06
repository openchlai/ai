
import pytest
from unittest.mock import patch
from core.pipeline.ner import extract_entities

@pytest.mark.unit
@patch('core.pipeline.ner.nlp')
def test_extract_entities(mock_nlp):
    """
    Test the extract_entities function.
    """
    # Mock the NLP response
    from unittest.mock import Mock

    from unittest.mock import Mock

    from unittest.mock import Mock

    mock_doc = Mock()
    mock_doc.ents = [type('ent', (object,), {'text': 'test', 'label_': 'PERSON'})]
    mock_nlp.return_value = mock_doc

    # Call the function
    text = "This is a test sentence."
    entities = extract_entities(text)

    # Check the result
    assert entities == {
        "PERSON": ["test"],
        "ORG": [],
        "GPE": [],
        "LOC": [],
        "DATE": [],
        "TIME": [],
        "MONEY": [],
        "EVENT": [],
        "CONTACT_INFO": [],
    }

    # Check that the NLP model was called with the correct text
    mock_nlp.assert_called_once_with(text)
