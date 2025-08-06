
from unittest.mock import patch, Mock
from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
import torch
import pytest
from core.pipeline.summarizer import summarize as summarize_text

@pytest.mark.unit
@patch('core.pipeline.summarizer.model')
@patch('core.pipeline.summarizer.tokenizer')
def test_summarize_text(mock_tokenizer, mock_model):
    """
    Test the summarize_text function.
    """
    from unittest.mock import MagicMock
    from unittest.mock import MagicMock
    mock_model.generate.return_value = MagicMock(return_value=torch.tensor([[1, 2, 3]]))
    mock_tokenizer.decode.return_value = "This is a test summary."
    mock_tokenizer.return_value = Mock(input_ids=Mock(), attention_mask=Mock())
    mock_tokenizer.return_value.to.return_value = Mock(input_ids=Mock(), attention_mask=Mock())

    # Call the function
    text = "This is a test sentence."
    summary = summarize_text(text)

    # Check the result
    assert summary == "This is a test summary."

    # Check that the summarizer was called with the correct text
    mock_tokenizer.assert_called_once_with("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
