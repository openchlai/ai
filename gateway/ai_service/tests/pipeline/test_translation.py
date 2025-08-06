
import torch
import pytest
from unittest.mock import patch
from core.pipeline.translation import translate as translate_text

@pytest.mark.unit
@patch('core.pipeline.translation.model')
@patch('core.pipeline.translation.tokenizer')
def test_translate_text(mock_tokenizer, mock_model):
    """
    Test the translate_text function.
    """
    mock_model.generate.return_value = torch.tensor([[0, 1, 2]])
    mock_tokenizer.decode.return_value = "This is a test translation."

    # Call the function
    text = "This is a test sentence."
    translation = translate_text(text)

    # Check the result
    assert translation == "This is a test translation."

    # Check that the translator was called with the correct text
    mock_tokenizer.assert_called_once_with(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
