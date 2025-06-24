import pytest
from unittest.mock import patch, Mock
from core.pipeline.summarizer import summarize


class TestSummarizer:
    """Test text summarization pipeline"""

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_success(self, mock_summarizer_pipeline):
        """Test successful text summarization"""
        # Mock summarizer pipeline output
        mock_summarizer_pipeline.return_value = [
            {"summary_text": "This is a concise summary of the input text."}
        ]
        
        input_text = """
        This is a long text that needs to be summarized. It contains multiple sentences
        and paragraphs that describe various events and situations. The text discusses
        workplace issues, employee concerns, and potential solutions. There are many
        details that need to be condensed into a shorter, more manageable format.
        The summarization should capture the key points while reducing the overall length.
        """
        
        result = summarize(input_text)
        
        # Verify summarizer was called with correct parameters
        mock_summarizer_pipeline.assert_called_once_with(
            input_text, 
            max_length=150, 
            min_length=30, 
            do_sample=False
        )
        
        assert result == "This is a concise summary of the input text."
        assert isinstance(result, str)
        assert len(result) < len(input_text)

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_custom_parameters(self, mock_summarizer_pipeline):
        """Test summarization with custom parameters"""
        mock_summarizer_pipeline.return_value = [
            {"summary_text": "Custom summary with different parameters."}
        ]
        
        input_text = "Long text to be summarized with custom settings."
        
        # Test that we can't easily pass custom parameters with current implementation
        # But we can verify the default parameters are used
        result = summarize(input_text)
        
        mock_summarizer_pipeline.assert_called_once_with(
            input_text,
            max_length=150,
            min_length=30,
            do_sample=False
        )
        
        assert result == "Custom summary with different parameters."

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_short_text(self, mock_summarizer_pipeline):
        """Test summarization of short text"""
        mock_summarizer_pipeline.return_value = [
            {"summary_text": "Short text summary."}
        ]
        
        short_text = "This is a short text."
        result = summarize(short_text)
        
        mock_summarizer_pipeline.assert_called_once_with(
            short_text,
            max_length=150,
            min_length=30,
            do_sample=False
        )
        
        assert result == "Short text summary."

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_empty_text(self, mock_summarizer_pipeline):
        """Test summarization of empty text"""
        mock_summarizer_pipeline.return_value = [
            {"summary_text": ""}
        ]
        
        empty_text = ""
        result = summarize(empty_text)
        
        mock_summarizer_pipeline.assert_called_once_with(
            empty_text,
            max_length=150,
            min_length=30,
            do_sample=False
        )
        
        assert result == ""

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_pipeline_error(self, mock_summarizer_pipeline):
        """Test handling of summarization pipeline errors"""
        mock_summarizer_pipeline.side_effect = Exception("Summarization model failed")
        
        input_text = "Text that will cause an error during summarization."
        
        with pytest.raises(RuntimeError, match="Summarization failed"):
            summarize(input_text)

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_malformed_output(self, mock_summarizer_pipeline):
        """Test handling of malformed pipeline output"""
        # Pipeline returns unexpected format
        mock_summarizer_pipeline.return_value = [
            {"unexpected_key": "No summary_text key"}
        ]
        
        input_text = "Text that will cause malformed output."
        
        with pytest.raises(KeyError):
            summarize(input_text)

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_multiple_summaries(self, mock_summarizer_pipeline):
        """Test handling when pipeline returns multiple summaries"""
        # Pipeline returns multiple summaries (should use first one)
        mock_summarizer_pipeline.return_value = [
            {"summary_text": "First summary option."},
            {"summary_text": "Second summary option."}
        ]
        
        input_text = "Text that generates multiple summary options."
        result = summarize(input_text)
        
        # Should return the first summary
        assert result == "First summary option."

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_long_input_text(self, mock_summarizer_pipeline):
        """Test summarization of very long input text"""
        mock_summarizer_pipeline.return_value = [
            {"summary_text": "Summary of very long text with key points extracted."}
        ]
        
        # Create a very long text
        long_text = " ".join([
            "This is sentence number {}.".format(i) 
            for i in range(1, 101)
        ])  # 100 sentences
        
        result = summarize(long_text)
        
        mock_summarizer_pipeline.assert_called_once_with(
            long_text,
            max_length=150,
            min_length=30,
            do_sample=False
        )
        
        assert result == "Summary of very long text with key points extracted."
        assert len(result) < len(long_text)

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_special_characters(self, mock_summarizer_pipeline):
        """Test summarization with special characters and formatting"""
        mock_summarizer_pipeline.return_value = [
            {"summary_text": "Summary preserving important information."}
        ]
        
        text_with_special_chars = """
        Client reported: "I haven't been paid $500 for 2 weeks!"
        Employer's response: "Pay will come next month."
        Issues include:
        - Wage theft
        - Poor working conditions  
        - No safety equipment
        Contact: john.doe@email.com, (555) 123-4567
        """
        
        result = summarize(text_with_special_chars)
        
        mock_summarizer_pipeline.assert_called_once_with(
            text_with_special_chars,
            max_length=150,
            min_length=30,
            do_sample=False
        )
        
        assert result == "Summary preserving important information."

    @patch('core.pipeline.summarizer.summarizer')
    def test_summarize_return_type(self, mock_summarizer_pipeline):
        """Test that summarize always returns a string"""
        test_cases = [
            [{"summary_text": "String summary"}],
            [{"summary_text": ""}],
            [{"summary_text": "Summary with numbers 123 and symbols @#$"}]
        ]
        
        for mock_output in test_cases:
            mock_summarizer_pipeline.return_value = mock_output
            
            result = summarize("Test input")
            
            assert isinstance(result, str)
            assert result == mock_output[0]["summary_text"]

    def test_summarizer_pipeline_initialization(self):
        """Test that summarizer pipeline is properly initialized"""
        # This test verifies the module-level summarizer is configured correctly
        from core.pipeline.summarizer import summarizer
        
        # We can't easily test the actual pipeline without mocking,
        # but we can verify it exists
        assert summarizer is not None