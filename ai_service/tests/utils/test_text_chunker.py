# tests/test_text_chunker.py
import pytest
import sys
import os
from typing import List

# Add the app directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.text_chunker import IntelligentTextChunker, TextChunk, ChunkConfig


class TestIntelligentTextChunker:
    """Test suite for the intelligent text chunker"""
    
    @pytest.fixture
    def chunker(self):
        """Create a text chunker instance for testing"""
        return IntelligentTextChunker()
    
    @pytest.fixture
    def short_text(self):
        """Short text that doesn't need chunking"""
        return "This is a short text that should not require chunking."
    
    @pytest.fixture
    def medium_text(self):
        """Medium text that may need chunking"""
        return """
        This is a medium-length text that might require chunking depending on the model requirements.
        It contains multiple sentences that can be used to test the sentence-based chunking strategy.
        The text should be long enough to trigger chunking for models with lower token limits.
        Each sentence provides meaningful content that should be preserved during the chunking process.
        """
    
    @pytest.fixture
    def long_text(self):
        """Long text that definitely needs chunking"""
        sentences = [
            "This is a comprehensive test case for the intelligent text chunking system.",
            "The system should be able to handle very long texts by breaking them into manageable chunks.",
            "Each chunk should preserve sentence boundaries when possible to maintain semantic coherence.",
            "The chunking strategy should adapt based on the specific model requirements and token limits.",
            "For translation models, we need to be more careful about context preservation.",
            "Classification models can work with shorter chunks since they focus on overall meaning.",
            "Summarization models benefit from larger chunks to maintain narrative flow.",
            "Named Entity Recognition can work with smaller chunks as entities are often local.",
            "The overlap between chunks helps maintain context across chunk boundaries.",
            "This approach ensures that no important information is lost during processing.",
        ] * 10  # Repeat to make it very long
        
        return " ".join(sentences)
    
    @pytest.fixture
    def very_long_sentence(self):
        """Single sentence that's too long and needs forced splitting"""
        words = ["word"] * 500  # Create a 500-word sentence (>400 tokens to force splitting)
        return " ".join(words) + "."
    
    # Basic functionality tests
    
    def test_chunker_initialization(self, chunker):
        """Test that the chunker initializes correctly"""
        assert chunker is not None
        assert len(chunker.chunk_configs) > 0
        assert "translation" in chunker.chunk_configs
        assert "classification" in chunker.chunk_configs
        assert "summarization" in chunker.chunk_configs
        assert "ner" in chunker.chunk_configs
    
    def test_token_counting(self, chunker):
        """Test token counting functionality"""
        text = "This is a test sentence."
        token_count = chunker.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, int)
    
    def test_sentence_splitting(self, chunker):
        """Test sentence splitting functionality"""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = chunker.split_into_sentences(text)
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
        assert "Third sentence" in sentences[2]
    
    # Chunking strategy tests
    
    def test_short_text_no_chunking(self, chunker, short_text):
        """Test that short text doesn't get chunked"""
        chunks = chunker.chunk_text(short_text, "classification")
        assert len(chunks) == 1
        assert chunks[0].text == short_text.strip()
        assert chunks[0].chunk_id == 0
        assert not chunks[0].overlap_with_previous
        assert not chunks[0].overlap_with_next
    
    def test_empty_text_handling(self, chunker):
        """Test handling of empty or None text"""
        assert chunker.chunk_text("", "classification") == []
        assert chunker.chunk_text("   ", "classification") == []
        assert chunker.chunk_text(None, "classification") == []
    
    def test_long_text_chunking(self, chunker, long_text):
        """Test that long text gets properly chunked"""
        chunks = chunker.chunk_text(long_text, "classification")
        assert len(chunks) > 1
        
        # Verify chunk properties
        for chunk in chunks:
            assert isinstance(chunk, TextChunk)
            assert chunk.token_count > 0
            assert chunk.sentence_count > 0
            assert len(chunk.text.strip()) > 0
        
        # Verify chunk IDs are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == i
    
    def test_different_strategies(self, chunker, long_text):
        """Test different chunking strategies produce different results"""
        translation_chunks = chunker.chunk_text(long_text, "translation")
        classification_chunks = chunker.chunk_text(long_text, "classification")
        summarization_chunks = chunker.chunk_text(long_text, "summarization")
        ner_chunks = chunker.chunk_text(long_text, "ner")
        
        # Summarization should have fewer, larger chunks
        assert len(summarization_chunks) <= len(translation_chunks)
        assert len(summarization_chunks) <= len(classification_chunks)
        
        # Each strategy should produce valid chunks
        for chunks in [translation_chunks, classification_chunks, summarization_chunks, ner_chunks]:
            assert len(chunks) > 0
            assert all(chunk.token_count > 0 for chunk in chunks)
    
    def test_very_long_sentence_handling(self, chunker, very_long_sentence):
        """Test handling of sentences that exceed token limits"""
        chunks = chunker.chunk_text(very_long_sentence, "classification")
        assert len(chunks) > 1  # Should be split despite being one sentence
        
        # Verify all chunks are valid
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0
            assert chunk.token_count > 0
    
    # Overlap and context preservation tests
    
    def test_overlap_marking(self, chunker, long_text):
        """Test that overlap between chunks is properly marked"""
        chunks = chunker.chunk_text(long_text, "translation")
        
        if len(chunks) > 1:
            # Check overlap markings
            for i in range(len(chunks) - 1):
                if chunks[i].overlap_with_next:
                    assert chunks[i + 1].overlap_with_previous
    
    def test_overlap_content(self, chunker):
        """Test that overlapping chunks actually share content"""
        # Create text with clear sentence boundaries
        sentences = [f"This is sentence number {i}." for i in range(1, 21)]
        text = " ".join(sentences)
        
        chunks = chunker.chunk_text(text, "translation")
        
        if len(chunks) > 1:
            # Look for overlapping chunks
            for i in range(len(chunks) - 1):
                if chunks[i].overlap_with_next and chunks[i + 1].overlap_with_previous:
                    # There should be some common content
                    chunk1_words = set(chunks[i].text.split())
                    chunk2_words = set(chunks[i + 1].text.split())
                    overlap = chunk1_words.intersection(chunk2_words)
                    assert len(overlap) > 0  # Should have some overlapping words
    
    # Configuration and limits tests
    
    def test_token_limits_respected(self, chunker, long_text):
        """Test that chunks respect token limits for each strategy"""
        strategies = ["translation", "classification", "summarization", "ner"]
        
        for strategy in strategies:
            chunks = chunker.chunk_text(long_text, strategy)
            config = chunker.chunk_configs[strategy]
            
            for chunk in chunks:
                # Allow some tolerance for special tokens and edge cases
                assert chunk.token_count <= config.max_tokens + 50, f"Chunk exceeded limit for {strategy}"
    
    def test_minimum_chunk_size(self, chunker):
        """Test that very small chunks are handled appropriately"""
        # Create text with very short sentences
        text = "Hi. No. Yes. Maybe. OK."
        chunks = chunker.chunk_text(text, "classification")
        
        # Should create at least one chunk
        assert len(chunks) >= 1
        
        # All chunks should have content
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0
    
    # Edge cases and error handling
    
    def test_special_characters(self, chunker):
        """Test handling of text with special characters"""
        text = "Text with émojis 😊, symbols @#$%, and unicode characters: ñáéíóú."
        chunks = chunker.chunk_text(text, "classification")
        
        assert len(chunks) >= 1
        assert chunks[0].text.strip() != ""
    
    def test_mixed_languages(self, chunker):
        """Test handling of mixed language text"""
        text = "English text. Texto en español. Texte en français. Back to English."
        chunks = chunker.chunk_text(text, "translation")
        
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0
    
    def test_repeated_punctuation(self, chunker):
        """Test handling of repeated punctuation marks"""
        text = "What?? Really!!! Yes... No??? Maybe!!!"
        chunks = chunker.chunk_text(text, "classification")
        
        assert len(chunks) >= 1
        assert chunks[0].text.strip() != ""
    
    # Utility method tests
    
    def test_strategy_mapping(self, chunker):
        """Test model type to strategy mapping"""
        assert chunker.get_chunking_strategy_for_model("translator") == "translation"
        assert chunker.get_chunking_strategy_for_model("classifier_model") == "classification"
        assert chunker.get_chunking_strategy_for_model("summarizer") == "summarization"
        assert chunker.get_chunking_strategy_for_model("ner") == "ner"
        assert chunker.get_chunking_strategy_for_model("unknown") == "classification"  # Default
    
    def test_processing_time_estimation(self, chunker, long_text):
        """Test processing time estimation"""
        chunks = chunker.chunk_text(long_text, "translation")
        estimated_time = chunker.estimate_processing_time(chunks, "translation")
        
        assert estimated_time > 0
        assert isinstance(estimated_time, float)
        
        # Larger chunks should take more time
        more_chunks = chunker.chunk_text(long_text + " " + long_text, "translation")
        longer_time = chunker.estimate_processing_time(more_chunks, "translation")
        assert longer_time >= estimated_time
    
    # Integration tests
    
    def test_chunking_preserves_information(self, chunker):
        """Test that chunking doesn't lose important information"""
        original_text = "John Doe works at Microsoft in Seattle. He started on January 1, 2020."
        chunks = chunker.chunk_text(original_text, "ner")
        
        # Reconstruct text from chunks (without overlap handling for simplicity)
        reconstructed = " ".join(chunk.text for chunk in chunks)
        
        # Important entities should be preserved
        assert "John Doe" in reconstructed
        assert "Microsoft" in reconstructed
        assert "Seattle" in reconstructed
        assert "January 1, 2020" in reconstructed
    
    def test_performance_with_large_text(self, chunker):
        """Test performance with very large texts"""
        # Create a very large text
        large_text = "This is a performance test sentence. " * 1000
        
        import time
        start_time = time.time()
        chunks = chunker.chunk_text(large_text, "classification")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 10.0  # 10 seconds max
        assert len(chunks) > 0
        
        # Verify chunks are reasonable
        for chunk in chunks:
            assert chunk.token_count > 0
            assert len(chunk.text.strip()) > 0


class TestChunkConfig:
    """Test the ChunkConfig dataclass"""
    
    def test_config_creation(self):
        """Test creating a chunk configuration"""
        config = ChunkConfig(
            max_tokens=512,
            overlap_tokens=50,
            min_chunk_tokens=10
        )
        
        assert config.max_tokens == 512
        assert config.overlap_tokens == 50
        assert config.min_chunk_tokens == 10
        assert config.preserve_sentences == True  # Default
        assert config.preserve_paragraphs == True  # Default
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = ChunkConfig(max_tokens=100, overlap_tokens=10, min_chunk_tokens=5)
        assert config.overlap_tokens < config.max_tokens
        assert config.min_chunk_tokens < config.max_tokens


class TestTextChunk:
    """Test the TextChunk dataclass"""
    
    def test_chunk_creation(self):
        """Test creating a text chunk"""
        chunk = TextChunk(
            text="This is a test chunk.",
            start_pos=0,
            end_pos=21,
            chunk_id=0,
            token_count=5,
            sentence_count=1
        )
        
        assert chunk.text == "This is a test chunk."
        assert chunk.start_pos == 0
        assert chunk.end_pos == 21
        assert chunk.chunk_id == 0
        assert chunk.token_count == 5
        assert chunk.sentence_count == 1
        assert chunk.overlap_with_previous == False  # Default
        assert chunk.overlap_with_next == False     # Default


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmarks for the text chunker"""

    @pytest.fixture
    def chunker(self):
        """Create a text chunker instance for benchmarking"""
        return IntelligentTextChunker()

    @pytest.mark.benchmark
    def test_chunking_speed_small_text(self, chunker):
        """Benchmark chunking speed for small texts"""
        text = "Short text. " * 50  # ~100 words
        
        import time
        start = time.time()
        for _ in range(100):  # Run 100 times
            chunks = chunker.chunk_text(text, "classification")
        end = time.time()
        
        avg_time = (end - start) / 100
        assert avg_time < 0.1  # Should be under 100ms per call
    
    @pytest.mark.benchmark  
    def test_chunking_speed_large_text(self, chunker):
        """Benchmark chunking speed for large texts"""
        text = "Large text sentence. " * 1000  # ~3000 words
        
        import time
        start = time.time()
        chunks = chunker.chunk_text(text, "summarization")
        end = time.time()
        
        processing_time = end - start
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert len(chunks) > 1  # Should create multiple chunks


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])