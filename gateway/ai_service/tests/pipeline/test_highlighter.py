import pytest
from core.utils.highlighter import highlight_text


class TestHighlighter:
    """Test text highlighting utility"""

    def test_highlight_text_with_dict_entities(self):
        """Test highlighting with dictionary format entities"""
        text = "Alice went to Wonderland with Bob."
        entities = {
            "PERSON": ["Alice", "Bob"],
            "LOC": ["Wonderland"]
        }
        
        result = highlight_text(text, entities)
        
        assert "[Alice|PERSON]" in result
        assert "[Bob|PERSON]" in result
        assert "[Wonderland|LOC]" in result

    def test_highlight_text_with_list_entities(self):
        """Test highlighting with list format entities"""
        text = "Alice went to Wonderland."
        entities = [
            {"text": "Alice", "label": "PERSON"},
            {"text": "Wonderland", "label": "LOC"}
        ]
        
        result = highlight_text(text, entities)
        
        assert "[Alice|PERSON]" in result
        assert "[Wonderland|LOC]" in result

    def test_highlight_text_no_entities(self):
        """Test highlighting with no entities"""
        text = "This is a simple text."
        entities_dict = {"PERSON": [], "LOC": []}
        entities_list = []
        
        result_dict = highlight_text(text, entities_dict)
        result_list = highlight_text(text, entities_list)
        
        assert result_dict == text
        assert result_list == text

    def test_highlight_text_overlapping_entities(self):
        """Test highlighting with overlapping entity text"""
        text = "New York and New York City are different."
        entities = [
            {"text": "New York", "label": "GPE"},
            {"text": "New York City", "label": "GPE"}
        ]
        
        result = highlight_text(text, entities)
        
        # Should highlight both entities
        assert "[New York|GPE]" in result
        assert "[New York City|GPE]" in result

    def test_highlight_text_case_sensitive(self):
        """Test that highlighting is case sensitive"""
        text = "alice went to Alice's house."
        entities = [{"text": "Alice", "label": "PERSON"}]
        
        result = highlight_text(text, entities)
        
        # Should only highlight exact match "Alice", not "alice"
        assert "[Alice|PERSON]" in result
        assert "[alice|PERSON]" not in result

    def test_highlight_text_multiple_occurrences(self):
        """Test highlighting multiple occurrences of same entity"""
        text = "Alice met Alice at Alice's house."
        entities = [{"text": "Alice", "label": "PERSON"}]
        
        result = highlight_text(text, entities)
        
        # All occurrences should be highlighted
        alice_count = result.count("[Alice|PERSON]")
        assert alice_count == 3

    def test_highlight_text_invalid_entity_format(self):
        """Test error handling for invalid entity format"""
        text = "Some text"
        invalid_entities = "invalid format"
        
        with pytest.raises(ValueError, match="Unexpected entities type"):
            highlight_text(text, invalid_entities)

    def test_highlight_text_missing_keys_in_list(self):
        """Test handling of entities with missing keys"""
        text = "Alice went to Wonderland."
        entities = [
            {"text": "Alice"},  # Missing label
            {"label": "LOC"},   # Missing text
            {"text": "Wonderland", "label": "LOC"}  # Complete
        ]
        
        result = highlight_text(text, entities)
        
        # Should only highlight the complete entity
        assert "[Wonderland|LOC]" in result
        assert "[Alice|" not in result  # Should not highlight incomplete entity

    def test_highlight_text_empty_string(self):
        """Test highlighting empty text"""
        text = ""
        entities = [{"text": "Alice", "label": "PERSON"}]
        
        result = highlight_text(text, entities)
        
        assert result == ""

    def test_highlight_text_special_characters(self):
        """Test highlighting entities with special characters"""
        text = "Contact john.doe@email.com or call (555) 123-4567."
        entities = [
            {"text": "john.doe@email.com", "label": "EMAIL"},
            {"text": "(555) 123-4567", "label": "PHONE"}
        ]
        
        result = highlight_text(text, entities)
        
        assert "[john.doe@email.com|EMAIL]" in result
        assert "[(555) 123-4567|PHONE]" in result