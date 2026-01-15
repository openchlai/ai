"""
Tests for app/utils/text_utils.py
Tests transcript chunking and classification aggregation logic
"""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np


class TestBaseChunker:
    """Test base chunking functionality"""

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_base_chunker_initialization(self, mock_tokenizer_class):
        """Test BaseChunker initialization with custom tokenizer and max_tokens"""
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import BaseChunker

        chunker = BaseChunker(tokenizer_name="bert-base-uncased", max_tokens=256)

        assert chunker.max_tokens == 256
        mock_tokenizer_class.from_pretrained.assert_called_once_with("bert-base-uncased")

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_count_tokens(self, mock_tokenizer_class):
        """Test token counting"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101, 2054, 2003, 1998, 2054, 2003, 102]  # 7 tokens
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import BaseChunker

        chunker = BaseChunker()
        token_count = chunker.count_tokens("This is a test sentence.")

        assert token_count == 7
        mock_tokenizer.encode.assert_called_with("This is a test sentence.", add_special_tokens=True)

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_split_into_sentences(self, mock_tokenizer_class):
        """Test sentence splitting"""
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import BaseChunker

        chunker = BaseChunker()

        # Test text with multiple sentences
        text = "This is first sentence. This is second sentence! What about third? And one more."
        sentences = chunker.split_into_sentences(text)

        assert len(sentences) == 4
        assert sentences[0] == "This is first sentence."
        assert sentences[1] == "This is second sentence!"
        assert sentences[2] == "What about third?"

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_split_into_sentences_with_extra_spaces(self, mock_tokenizer_class):
        """Test sentence splitting normalizes whitespace"""
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import BaseChunker

        chunker = BaseChunker()

        # Text with extra spaces
        text = "This  is   first.   This is  second."
        sentences = chunker.split_into_sentences(text)

        # Should normalize spaces
        assert all("  " not in s for s in sentences)


class TestClassificationChunker:
    """Test classification-specific chunking with overlap"""

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_classification_chunker_initialization(self, mock_tokenizer_class):
        """Test ClassificationChunker with overlap configuration"""
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import ClassificationChunker

        chunker = ClassificationChunker(max_tokens=512, overlap_tokens=150)

        assert chunker.max_tokens == 512
        assert chunker.overlap_tokens == 150

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_chunk_transcript_single_chunk(self, mock_tokenizer_class):
        """Test chunking when transcript fits in single chunk"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 100  # 100 tokens
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import ClassificationChunker

        chunker = ClassificationChunker(max_tokens=512)
        transcript = "This is a short transcript."
        chunks = chunker.chunk_transcript(transcript)

        assert len(chunks) == 1
        assert chunks[0]['chunk_index'] == 0
        assert chunks[0]['total_chunks'] == 1
        assert chunks[0]['text'] == "This is a short transcript."

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_chunk_transcript_multiple_chunks(self, mock_tokenizer_class):
        """Test chunking when transcript requires multiple chunks"""
        mock_tokenizer = MagicMock()
        # Simulate token counting - each sentence is ~50 tokens
        def mock_encode(text, add_special_tokens=True):
            word_count = len(text.split())
            return [101] * (word_count * 5)  # Roughly 5 tokens per word

        mock_tokenizer.encode.side_effect = mock_encode
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import ClassificationChunker

        chunker = ClassificationChunker(max_tokens=100)  # Low limit to force multiple chunks
        transcript = " ".join(["Sentence number {}.".format(i) for i in range(20)])
        chunks = chunker.chunk_transcript(transcript)

        # Should create multiple chunks
        assert len(chunks) > 1
        # Check metadata
        for chunk in chunks:
            assert 'chunk_index' in chunk
            assert 'text' in chunk
            assert 'token_count' in chunk
            assert 'total_chunks' in chunk
            assert 'position_ratio' in chunk

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_chunk_transcript_maintains_chunk_info(self, mock_tokenizer_class):
        """Test that chunks maintain proper indexing and position ratio"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 50

        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import ClassificationChunker

        chunker = ClassificationChunker()
        transcript = "First. Second. Third. Fourth. Fifth."
        chunks = chunker.chunk_transcript(transcript)

        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            assert chunk['chunk_index'] == i
            assert chunk['total_chunks'] == total_chunks
            assert chunk['position_ratio'] == i / max(total_chunks - 1, 1)


class TestTranslationChunker:
    """Test translation-specific chunking without overlap"""

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_translation_chunker_no_overlap(self, mock_tokenizer_class):
        """Test TranslationChunker has no overlap"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 50
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import TranslationChunker

        chunker = TranslationChunker()
        transcript = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk_transcript(transcript)

        # Should be able to concatenate chunks without overlap
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'text' in chunk
            assert 'chunk_index' in chunk


class TestSummarizationChunker:
    """Test summarization-specific chunking with light overlap"""

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_summarization_chunker_with_overlap(self, mock_tokenizer_class):
        """Test SummarizationChunker uses overlap"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 50
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import SummarizationChunker

        chunker = SummarizationChunker(overlap_tokens=100)

        assert chunker.overlap_tokens == 100

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_reconstruct_summary(self, mock_tokenizer_class):
        """Test summary reconstruction from chunks"""
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import SummarizationChunker

        chunker = SummarizationChunker()
        chunk_summaries = [
            "First part of summary",
            "Second part of summary",
            "Third part of summary"
        ]

        reconstructed = chunker.reconstruct_summary(chunk_summaries)

        # Should join with paragraph breaks
        assert "\n\n" in reconstructed
        assert "First part" in reconstructed
        assert "Second part" in reconstructed


class TestNERChunker:
    """Test NER-specific chunking with character position tracking"""

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_ner_chunker_char_positions(self, mock_tokenizer_class):
        """Test NER chunker tracks character positions"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 50
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import NERChunker

        chunker = NERChunker()
        transcript = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk_transcript(transcript)

        # Check character positions
        for chunk in chunks:
            assert 'start_char' in chunk
            assert 'end_char' in chunk
            assert chunk['start_char'] >= 0
            assert chunk['end_char'] > chunk['start_char']

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_reconstruct_entities_flat(self, mock_tokenizer_class):
        """Test entity reconstruction in flat format"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 50
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import NERChunker

        chunker = NERChunker()

        # Create mock chunk data
        chunks = [
            {'start_char': 0, 'end_char': 15},
            {'start_char': 16, 'end_char': 31}
        ]

        # Create mock entity data
        chunk_entities = [
            [
                {'text': 'John', 'label': 'PERSON', 'start': 0, 'end': 4, 'confidence': 0.95},
                {'text': 'Smith', 'label': 'PERSON', 'start': 5, 'end': 10, 'confidence': 0.92}
            ],
            [
                {'text': 'Company', 'label': 'ORG', 'start': 0, 'end': 7, 'confidence': 0.88}
            ]
        ]

        # Reconstruct
        entities = chunker.reconstruct_entities(chunk_entities, chunks, flat=True)

        assert isinstance(entities, list)
        # Second chunk should have adjusted positions
        assert any(e['start'] > 15 for e in entities)

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_reconstruct_entities_grouped(self, mock_tokenizer_class):
        """Test entity reconstruction grouped by label"""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101] * 50
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import NERChunker

        chunker = NERChunker()

        chunks = [
            {'start_char': 0, 'end_char': 15}
        ]

        chunk_entities = [
            [
                {'text': 'John', 'label': 'PERSON', 'start': 0, 'end': 4, 'confidence': 0.95},
                {'text': 'Company', 'label': 'ORG', 'start': 5, 'end': 12, 'confidence': 0.88}
            ]
        ]

        entities = chunker.reconstruct_entities(chunk_entities, chunks, flat=False)

        assert isinstance(entities, dict)
        assert 'PERSON' in entities
        assert 'ORG' in entities
        assert 'John' in entities['PERSON']
        assert 'Company' in entities['ORG']

    @patch('app.utils.text_utils.AutoTokenizer')
    def test_reconstruct_entities_empty(self, mock_tokenizer_class):
        """Test entity reconstruction with empty data"""
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        from app.utils.text_utils import NERChunker

        chunker = NERChunker()

        # Empty entities
        entities = chunker.reconstruct_entities([], [], flat=True)
        assert entities == []

        entities = chunker.reconstruct_entities([], [], flat=False)
        assert entities == {}


class TestClassificationAggregator:
    """Test classification prediction aggregation"""

    def test_aggregate_case_classification_single_chunk(self):
        """Test aggregation for single chunk prediction"""
        from app.utils.text_utils import ClassificationAggregator

        chunk_predictions = [
            {
                'main_category': 'abuse',
                'sub_category': 'physical',
                'sub_category_2': 'neglect',
                'intervention': 'immediate',
                'priority': 'high',
                'confidence_scores': {
                    'main_category': 0.95,
                    'sub_category': 0.89,
                    'sub_category_2': 0.75,
                    'intervention': 0.92,
                    'priority': 0.87
                }
            }
        ]

        result = ClassificationAggregator.aggregate_case_classification(chunk_predictions)

        assert result['main_category'] == 'abuse'
        assert result['sub_category'] == 'physical'
        assert result['intervention'] == 'immediate'
        assert result['num_chunks'] == 1

    def test_aggregate_case_classification_multiple_chunks_consensus(self):
        """Test aggregation with consensus across chunks"""
        from app.utils.text_utils import ClassificationAggregator

        chunk_predictions = [
            {
                'main_category': 'abuse',
                'sub_category': 'physical',
                'sub_category_2': 'neglect',
                'intervention': 'immediate',
                'priority': 'high',
                'confidence_scores': {
                    'main_category': 0.95,
                    'sub_category': 0.89,
                    'sub_category_2': 0.75,
                    'intervention': 0.92,
                    'priority': 0.87
                }
            },
            {
                'main_category': 'abuse',
                'sub_category': 'physical',
                'sub_category_2': 'emotional',
                'intervention': 'immediate',
                'priority': 'high',
                'confidence_scores': {
                    'main_category': 0.93,
                    'sub_category': 0.91,
                    'sub_category_2': 0.82,
                    'intervention': 0.90,
                    'priority': 0.88
                }
            }
        ]

        result = ClassificationAggregator.aggregate_case_classification(chunk_predictions)

        # Consensus on main findings
        assert result['main_category'] == 'abuse'
        assert result['intervention'] == 'immediate'
        assert result['num_chunks'] == 2

    def test_aggregate_case_classification_empty(self):
        """Test aggregation with empty predictions"""
        from app.utils.text_utils import ClassificationAggregator

        result = ClassificationAggregator.aggregate_case_classification([])

        assert result is None

    def test_aggregate_qa_scoring_single_chunk(self):
        """Test QA scoring aggregation for single chunk"""
        from app.utils.text_utils import ClassificationAggregator

        chunk_predictions = [
            {
                'opening': [
                    {'submetric': 'greeting', 'prediction': True, 'probability': 0.95},
                    {'submetric': 'rapport', 'prediction': True, 'probability': 0.88}
                ],
                'listening': [
                    {'submetric': 'active_listening', 'prediction': True, 'probability': 0.92}
                ]
            }
        ]

        result = ClassificationAggregator.aggregate_qa_scoring(chunk_predictions)

        assert result['success'] is True
        assert result['num_chunks'] == 1
        assert 'opening' in result['predictions']
        assert 'listening' in result['predictions']

    def test_aggregate_qa_scoring_multiple_chunks(self):
        """Test QA scoring aggregation with probability-weighted voting"""
        from app.utils.text_utils import ClassificationAggregator

        chunk_predictions = [
            {
                'opening': [
                    {'submetric': 'greeting', 'prediction': True, 'probability': 0.95}
                ]
            },
            {
                'opening': [
                    {'submetric': 'greeting', 'prediction': False, 'probability': 0.60}
                ]
            }
        ]

        result = ClassificationAggregator.aggregate_qa_scoring(chunk_predictions)

        assert result['success'] is True
        assert result['num_chunks'] == 2
        # True prediction has higher weight (0.95 vs 0.60)
        assert result['predictions']['opening'][0]['prediction'] is True

    def test_aggregate_qa_scoring_empty(self):
        """Test QA scoring aggregation with empty predictions"""
        from app.utils.text_utils import ClassificationAggregator

        result = ClassificationAggregator.aggregate_qa_scoring([])

        assert result is None

    def test_get_top_2_subcategories_multi(self):
        """Test getting top 2 subcategories from multiple chunks"""
        from app.utils.text_utils import ClassificationAggregator

        chunk_predictions = [
            {
                'sub_category': 'physical',
                'sub_category_2': 'emotional',
                'confidence_scores': {
                    'sub_category': 0.90,
                    'sub_category_2': 0.75
                }
            },
            {
                'sub_category': 'physical',
                'sub_category_2': 'neglect',
                'confidence_scores': {
                    'sub_category': 0.88,
                    'sub_category_2': 0.82
                }
            }
        ]

        result = ClassificationAggregator._get_top_2_subcategories_multi(chunk_predictions)

        assert 'sub_category' in result
        assert 'sub_category_2' in result
        assert result['sub_category'] == 'physical'  # Has highest combined score

    def test_get_top_2_subcategories_single_option(self):
        """Test getting top 2 when only one subcategory exists"""
        from app.utils.text_utils import ClassificationAggregator

        chunk_predictions = [
            {
                'sub_category': 'physical',
                'sub_category_2': None,
                'confidence_scores': {
                    'sub_category': 0.95,
                    'sub_category_2': 0.0
                }
            }
        ]

        result = ClassificationAggregator._get_top_2_subcategories_multi(chunk_predictions)

        assert result['sub_category'] == 'physical'
        assert result['sub_category_2'] is None
        assert result['sub_category_2_confidence'] == 0.0
