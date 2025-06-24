import pytest
from unittest.mock import patch, Mock
from core.pipeline.ner import extract_entities


class TestNERPipeline:
    """Test Named Entity Recognition pipeline"""

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_dict_format(self, mock_nlp):
        """Test entity extraction returning dictionary format"""
        # Mock spaCy entities
        mock_ent1 = Mock()
        mock_ent1.text = "Barack Obama"
        mock_ent1.label_ = "PERSON"
        
        mock_ent2 = Mock()
        mock_ent2.text = "United States"
        mock_ent2.label_ = "GPE"
        
        mock_doc = Mock()
        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp.return_value = mock_doc
        
        text = "John Doe and Jane Smith are here."
        result = extract_entities(text, flat=False)
        
        assert len(result["PERSON"]) == 2
        assert "John Doe" in result["PERSON"]
        assert "Jane Smith" in result["PERSON"]

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_all_supported_types(self, mock_nlp):
        """Test extraction of all supported entity types"""
        # Create entities for all supported types
        entities = [
            ("John Doe", "PERSON"),
            ("Microsoft", "ORG"),
            ("United States", "GPE"),
            ("New York", "LOC"),
            ("January 15, 2023", "DATE"),
            ("3:00 PM", "TIME"),
            ("$100", "MONEY"),
            ("Olympics", "EVENT")
        ]
        
        mock_ents = []
        for text, label in entities:
            mock_ent = Mock()
            mock_ent.text = text
            mock_ent.label_ = label
            mock_ents.append(mock_ent)
        
        mock_doc = Mock()
        mock_doc.ents = mock_ents
        mock_nlp.return_value = mock_doc
        
        text = "John Doe from Microsoft visited United States..."
        result = extract_entities(text, flat=False)
        
        # Check that all entity types have been populated
        assert len(result["PERSON"]) == 1
        assert len(result["ORG"]) == 1
        assert len(result["GPE"]) == 1
        assert len(result["LOC"]) == 1
        assert len(result["DATE"]) == 1
        assert len(result["TIME"]) == 1
        assert len(result["MONEY"]) == 1
        assert len(result["EVENT"]) == 1
        
        text = "Barack Obama was the President of the United States."
        result = extract_entities(text, flat=False)
        
        assert isinstance(result, dict)
        assert "Barack Obama" in result["PERSON"]
        assert "United States" in result["GPE"]
        assert len(result["PERSON"]) == 1
        assert len(result["GPE"]) == 1

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_flat_format(self, mock_nlp):
        """Test entity extraction returning flat list format"""
        # Mock spaCy entities
        mock_ent1 = Mock()
        mock_ent1.text = "Barack Obama"
        mock_ent1.label_ = "PERSON"
        
        mock_ent2 = Mock()
        mock_ent2.text = "New York"
        mock_ent2.label_ = "GPE"
        
        mock_doc = Mock()
        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp.return_value = mock_doc
        
        text = "Barack Obama visited New York."
        result = extract_entities(text, flat=True)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert {"text": "Barack Obama", "label": "PERSON"} in result
        assert {"text": "New York", "label": "GPE"} in result

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_no_entities(self, mock_nlp):
        """Test text with no recognizable entities"""
        mock_doc = Mock()
        mock_doc.ents = []
        mock_nlp.return_value = mock_doc
        
        text = "This is a simple text without entities."
        result = extract_entities(text, flat=False)
        
        assert isinstance(result, dict)
        for entity_list in result.values():
            assert len(entity_list) == 0

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_unsupported_labels(self, mock_nlp):
        """Test entities with unsupported labels are ignored"""
        # Mock entity with unsupported label
        mock_ent = Mock()
        mock_ent.text = "Something"
        mock_ent.label_ = "UNSUPPORTED_LABEL"
        
        mock_doc = Mock()
        mock_doc.ents = [mock_ent]
        mock_nlp.return_value = mock_doc
        
        text = "Some text with unsupported entity."
        result = extract_entities(text, flat=False)
        
        # Should return empty lists for all supported categories
        for entity_list in result.values():
            assert len(entity_list) == 0

    def test_extract_entities_nlp_not_loaded(self):
        """Test error handling when spaCy model is not loaded"""
        with patch('core.pipeline.ner.nlp', None):
            with pytest.raises(RuntimeError, match="spaCy model not initialized"):
                extract_entities("Test text")

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_spacy_exception(self, mock_nlp):
        """Test handling of spaCy processing exceptions"""
        mock_nlp.side_effect = Exception("spaCy processing failed")
        
        with pytest.raises(RuntimeError, match="NER failed"):
            extract_entities("Test text")

    @patch('core.pipeline.ner.nlp')
    def test_extract_entities_multiple_same_type(self, mock_nlp):
        """Test multiple entities of the same type"""
        # Create multiple PERSON entities
        mock_ent1 = Mock()
        mock_ent1.text = "John Doe"
        mock_ent1.label_ = "PERSON"
        
        mock_ent2 = Mock()
        mock_ent2.text = "Jane Smith"
        mock_ent2.label_ = "PERSON"
        
        mock_doc = Mock()
        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp.return_value = mock_doc