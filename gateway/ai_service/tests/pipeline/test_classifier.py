import pytest
from unittest.mock import patch, Mock
import torch
from core.pipeline.classifier import classify_case, CaseClassifier


class TestClassifier:
    """Test case classification pipeline"""

    @patch('core.pipeline.classifier.get_classifier')
    def test_classify_case_with_mocked_classifier(self, mock_get_classifier):
        """Test classification with a mocked classifier"""
        # Mock the classifier's classify method
        mock_classifier_instance = Mock()
        mock_classifier_instance.classify.return_value = {
            "main_category": "legal_aid_needed",
            "sub_category": "immigration",
            "intervention": "legal_advice",
            "priority": "high"
        }
        mock_get_classifier.return_value = mock_classifier_instance

        narrative = "Client needs help with immigration paperwork and legal documentation."
        result = classify_case(narrative)

        assert result["main_category"] == "legal_aid_needed"
        mock_classifier_instance.classify.assert_called_once_with(narrative)
