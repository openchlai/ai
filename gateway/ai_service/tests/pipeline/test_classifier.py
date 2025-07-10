import pytest
from unittest.mock import patch, Mock
import torch
from core.pipeline.classifier import classify_case


class TestClassifier:
    """Test case classification pipeline"""

    @patch('core.pipeline.classifier.model')
    @patch('core.pipeline.classifier.tokenizer')
    @patch('core.pipeline.classifier.label_encoder')
    @patch('torch.cuda.is_available')
    def test_classify_case_cpu_device(self, mock_cuda, mock_label_encoder, mock_tokenizer, mock_model):
        """Test classification on CPU device"""
        # Mock CPU-only environment
        mock_cuda.return_value = False
        
        # Mock tokenizer
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        
        # Mock model output
        mock_outputs = Mock()
        mock_logits = torch.tensor([[1.8, 2.2, 0.5]])
        mock_outputs.logits = mock_logits
        mock_model.return_value = mock_outputs
        
        # Mock label encoder
        mock_label_encoder.inverse_transform.return_value = ["legal_aid_needed"]
        
        narrative = "Client needs help with immigration paperwork and legal documentation."
        
        with patch('torch.nn.functional.softmax') as mock_softmax, \
             patch('torch.max') as mock_max:
            
            mock_probs = torch.tensor([[0.2, 0.7, 0.1]])
            mock_softmax.return_value = mock_probs
            mock_max.return_value = (torch.tensor([0.7]), torch.tensor([1]))
            
            result = classify_case(narrative)
            
            assert result["category"] == "legal_aid_needed"
            assert isinstance(result["confidence"], float)

    @patch('core.pipeline.classifier.model')
    @patch('core.pipeline.classifier.tokenizer')
    def test_classify_case_preprocessing(self, mock_tokenizer, mock_model):
        """Test text preprocessing in classification"""
        # Mock tokenizer to capture preprocessed text
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[1.0, 2.0, 0.5]])
        mock_model.return_value = mock_outputs
        
        # Test with text containing special characters and mixed case
        narrative = "Client reported WAGE THEFT!!! They haven't been paid $500 for 2 weeks."
        
        with patch('core.pipeline.classifier.label_encoder') as mock_label_encoder, \
             patch('torch.nn.functional.softmax') as mock_softmax, \
             patch('torch.max') as mock_max:
            
            mock_label_encoder.inverse_transform.return_value = ["wage_theft"]
            mock_softmax.return_value = torch.tensor([[0.1, 0.8, 0.1]])
            mock_max.return_value = (torch.tensor([0.8]), torch.tensor([1]))
            
            result = classify_case(narrative)
            
            # Verify tokenizer was called with preprocessed text
            args, kwargs = mock_tokenizer.call_args
            processed_text = args[0]
            
            # Should be lowercase and alphanumeric only
            assert processed_text.islower()
            assert "client reported wage theft they havent been paid 500 for 2 weeks" in processed_text

    @patch('core.pipeline.classifier.model')
    @patch('core.pipeline.classifier.tokenizer')
    @patch('core.pipeline.classifier.label_encoder')
    def test_classify_case_multiple_categories(self, mock_label_encoder, mock_tokenizer, mock_model):
        """Test classification with different case categories"""
        test_cases = [
            ("Worker injured on construction site without safety equipment", "workplace_abuse"),
            ("Domestic worker not receiving promised wages", "wage_theft"),
            ("Individual seeking help with asylum application", "legal_aid_needed"),
            ("Person experiencing anxiety and depression", "psychological_distress"),
            ("Family evicted from apartment without notice", "housing_insecurity"),
            ("Patient denied medical treatment due to status", "medical_attention_needed")
        ]
        
        for narrative, expected_category in test_cases:
            # Reset mocks for each test
            mock_tokenizer.reset_mock()
            mock_model.reset_mock()
            mock_label_encoder.reset_mock()
            
            # Configure mocks
            mock_tokenizer.return_value = Mock()
            mock_tokenizer.return_value.to.return_value = {
                'input_ids': torch.tensor([[1, 2, 3]]),
                'attention_mask': torch.tensor([[1, 1, 1]])
            }
            
            mock_outputs = Mock()
            mock_outputs.logits = torch.tensor([[1.0, 2.5, 0.8]])
            mock_model.return_value = mock_outputs
            
            mock_label_encoder.inverse_transform.return_value = [expected_category]
            
            with patch('torch.nn.functional.softmax') as mock_softmax, \
                 patch('torch.max') as mock_max:
                
                mock_softmax.return_value = torch.tensor([[0.1, 0.8, 0.1]])
                mock_max.return_value = (torch.tensor([0.8]), torch.tensor([1]))
                
                result = classify_case(narrative)
                
                assert result["category"] == expected_category
                assert 0.0 <= result["confidence"] <= 1.0

    @patch('core.pipeline.classifier.model')
    def test_classify_case_model_error(self, mock_model):
        """Test handling of model prediction errors"""
        mock_model.side_effect = Exception("Model prediction failed")
        
        narrative = "Test case for error handling"
        
        with pytest.raises(Exception, match="Model prediction failed"):
            classify_case(narrative)

    @patch('core.pipeline.classifier.tokenizer')
    def test_classify_case_tokenizer_error(self, mock_tokenizer):
        """Test handling of tokenizer errors"""
        mock_tokenizer.side_effect = Exception("Tokenization failed")
        
        narrative = "Test case for tokenizer error"
        
        with pytest.raises(Exception, match="Tokenization failed"):
            classify_case(narrative)

    @patch('core.pipeline.classifier.model')
    @patch('core.pipeline.classifier.tokenizer')
    @patch('core.pipeline.classifier.label_encoder')
    def test_classify_case_confidence_scores(self, mock_label_encoder, mock_tokenizer, mock_model):
        """Test confidence score calculation"""
        # Mock tokenizer
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output with different confidence levels
        test_cases = [
            (torch.tensor([[5.0, 1.0, 0.5]]), 0.9),  # High confidence
            (torch.tensor([[2.0, 1.8, 1.5]]), 0.4),  # Low confidence
            (torch.tensor([[3.0, 2.5, 2.0]]), 0.5),  # Medium confidence
        ]
        
        for logits, expected_confidence_range in test_cases:
            mock_outputs = Mock()
            mock_outputs.logits = logits
            mock_model.return_value = mock_outputs
            mock_label_encoder.inverse_transform.return_value = ["test_category"]
            
            with patch('torch.nn.functional.softmax') as mock_softmax, \
                 patch('torch.max') as mock_max:
                
                # Calculate actual softmax for realistic confidence
                actual_probs = torch.nn.functional.softmax(logits, dim=-1)
                mock_softmax.return_value = actual_probs
                top_prob, top_idx = torch.max(actual_probs, dim=1)
                mock_max.return_value = (top_prob, top_idx)
                
                result = classify_case("Test narrative")
                
                # Confidence should be reasonable and rounded to 4 decimal places
                assert isinstance(result["confidence"], float)
                assert 0.0 <= result["confidence"] <= 1.0
                assert len(str(result["confidence"]).split('.')[-1]) <= 4

    def test_classify_case_empty_narrative(self):
        """Test classification with empty narrative"""
        with patch('core.pipeline.classifier.model') as mock_model, \
             patch('core.pipeline.classifier.tokenizer') as mock_tokenizer, \
             patch('core.pipeline.classifier.label_encoder') as mock_label_encoder:
            
            mock_tokenizer.return_value = Mock()
            mock_tokenizer.return_value.to.return_value = {
                'input_ids': torch.tensor([[1]]),  # Empty input representation
                'attention_mask': torch.tensor([[1]])
            }
            
            mock_outputs = Mock()
            mock_outputs.logits = torch.tensor([[1.0, 0.5, 0.3]])
            mock_model.return_value = mock_outputs
            mock_label_encoder.inverse_transform.return_value = ["unknown"]
            
            with patch('torch.nn.functional.softmax') as mock_softmax, \
                 patch('torch.max') as mock_max:
                
                mock_softmax.return_value = torch.tensor([[0.6, 0.3, 0.1]])
                mock_max.return_value = (torch.tensor([0.6]), torch.tensor([0]))
                
                result = classify_case("")
                
                assert "category" in result
                assert "confidence" in result

    @patch('torch.cuda.is_available')
    def test_classify_case_success(self, mock_cuda, mock_label_encoder, mock_tokenizer, mock_model):
        """Test successful case classification"""
        # Mock CUDA availability
        mock_cuda.return_value = True
        
        # Mock tokenizer
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        
        # Mock model output
        mock_outputs = Mock()
        mock_logits = torch.tensor([[2.1, 1.5, 0.8]])
        mock_outputs.logits = mock_logits
        mock_model.return_value = mock_outputs
        
        # Mock label encoder
        mock_label_encoder.inverse_transform.return_value = ["workplace_abuse"]
        
        narrative = "Employee reported harassment and unsafe working conditions at the factory."
        
        with patch('torch.nn.functional.softmax') as mock_softmax, \
             patch('torch.max') as mock_max:
            
            # Mock softmax and max operations
            mock_probs = torch.tensor([[0.6, 0.3, 0.1]])
            mock_softmax.return_value = mock_probs
            mock_max.return_value = (torch.tensor([0.6]), torch.tensor([0]))
            
            result = classify_case(narrative)
            
            assert isinstance(result, dict)
            assert "category" in result
            assert "confidence" in result
            assert result["category"] == "workplace_abuse"
            assert isinstance(result["confidence"], float)
