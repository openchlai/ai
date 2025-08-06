
import pytest
from core.utils.highlighter import highlight_text

@pytest.mark.unit
def test_highlight_text():
    """
    Test the highlight_text function.
    """
    text = "This is a test sentence."
    entities = [{"text": "test", "label": "test"}]
    highlighted_text = highlight_text(text, entities)
    assert highlighted_text == 'This is a [test|test] sentence.'
