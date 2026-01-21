
import pytest
from unittest.mock import patch, MagicMock
from app.core.text_chunker import IntelligentTextChunker, ChunkConfig, TextChunk

class TestIntelligentTextChunker:
    
    @pytest.fixture
    def chunker(self):
        # We mock tokenizer and spacy to avoid dependency initialization issues during test
        with patch('app.core.text_chunker.AutoTokenizer.from_pretrained') as mock_tok, \
             patch('app.core.text_chunker.spacy.load') as mock_spacy:
            
            mock_tok_instance = MagicMock()
            # Simple token counting mock: each "word" is 1 token approximately
            mock_tok_instance.encode.side_effect = lambda t, **kwargs: [1] * len(t.split())
            mock_tok.return_value = mock_tok_instance
            
            mock_nlp = MagicMock()
            # Simple sentence split mock
            mock_doc = MagicMock()
            mock_doc.sents = []
            mock_nlp.return_value = mock_doc
            mock_spacy.return_value = mock_nlp
            
            chunker = IntelligentTextChunker()
            chunker.tokenizer = mock_tok_instance
            # Override split logic for predictable testing
            chunker.nlp = None # Force regex fallback for simple testing or use spacy mock if needed
            
            return chunker

    def test_count_tokens_exact(self, chunker):
        """Test exact token counting via tokenizer mock"""
        # Mock behavior set in fixture: split by space = tokens
        cnt = chunker.count_tokens("hello world")
        assert cnt == 2

    def test_count_tokens_fallback(self, chunker):
        """Test fallback token counting"""
        chunker.tokenizer = None
        # Fallback: len/4
        # "12345678" -> 8 chars -> 2 tokens
        cnt = chunker.count_tokens("12345678")
        assert cnt == 2
        
        # "1" -> 0 tokens -> max(1)
        cnt = chunker.count_tokens("1")
        assert cnt == 1

    def test_split_into_sentences_regex(self, chunker):
        """Test regex fallback for sentence splitting"""
        # Force fallback
        chunker.nlp = None
        text = "Hello world. This is test! Another one?"
        sents = chunker.split_into_sentences(text)
        assert len(sents) == 3
        assert sents[0] == "Hello world"
        assert sents[1] == "This is test"
        
    def test_chunk_text_empty(self, chunker):
        assert chunker.chunk_text("") == []
        assert chunker.chunk_text(None) == []
    
    def test_chunk_text_small(self, chunker):
        # Small text fits in one chunk
        text = "short text"
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0].text == "short text"

    def test_chunk_by_tokens_strategy(self, chunker):
        # Use simple config
        text = "w1 w2 w3 w4 w5 w6"
        # Strategy config mock: max 3 tokens, overlap 1
        config = ChunkConfig(max_tokens=3, overlap_tokens=1, min_chunk_tokens=1, preserve_sentences=False)
        
        # Override config
        chunker.chunk_configs["custom"] = config
        
        chunks = chunker.chunk_text(text, strategy="custom")
        
        # Expected:
        # 1: w1 w2 w3
        # 2: w3 w4 w5 (w3 overlap)
        # 3: w5 w6 (w5 overlap)
        assert len(chunks) >= 2
        assert chunks[0].token_count <= 3


    def test_chunk_by_sentences_strategy(self, chunker):
        # Force regex splitting
        chunker.nlp = None
        
        # Sentences: "s1.", "s2.", "s3."
        # Assume each sentence is 1 token ("s1.")
        text = "s1. s2. s3." 
        
        # Config: max 1 token. So each sentence (1 token) fills a chunk.
        # Next sentence would exceed capacity locally or accumulatively.
        config = ChunkConfig(max_tokens=1, overlap_tokens=0, min_chunk_tokens=1, preserve_sentences=True)
        chunker.chunk_configs["custom_sent"] = config
        
        chunks = chunker.chunk_text(text, strategy="custom_sent")
        
        # Should be 3 chunks
        assert len(chunks) == 3
        assert chunks[0].text.strip(".") == "s1"
        assert chunks[1].text.strip(".") == "s2"

    def test_chunk_single_long_sentence(self, chunker):
        chunker.nlp = None
        # One long sentence "w1 w2 ... w10"
        # max tokens 5
        text = "w1 w2 w3 w4 w5 w6 w7 w8 w9 w10."
        
        config = ChunkConfig(max_tokens=5, overlap_tokens=0, min_chunk_tokens=1, preserve_sentences=True)
        chunker.chunk_configs["long_sent"] = config
        
        # Should fall back to token splitting for this sentence
        chunks = chunker.chunk_text(text, strategy="long_sent")
        
        assert len(chunks) >= 2
        assert "w1" in chunks[0].text

    def test_get_chunking_strategy_for_model(self, chunker):
        assert chunker.get_chunking_strategy_for_model("translator") == "translation"
        assert chunker.get_chunking_strategy_for_model("unknown") == "classification"

    def test_estimate_processing_time(self, chunker):
        chunks = [TextChunk("",0,0,0,0,0) for _ in range(5)]
        
        # Translation: 2.0s * 5 = 10s
        time = chunker.estimate_processing_time(chunks, "translator")
        assert time == 10.0
