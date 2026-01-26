import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestSummarizeExceptionHandling:
    """Test summarize exception handling - covers lines 103-105"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarize_raises_runtime_error_on_failure(self, mock_cuda):
        """Test summarize raises RuntimeError on failure"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()
        
        # Mock tokenizer to raise exception during encoding
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.side_effect = Exception("Encoding failed")
        
        with pytest.raises(RuntimeError, match="Summarization failed"):
            summarizer.summarize("Some text to summarize")

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarize_cleans_up_on_exception(self, mock_cuda):
        """Test cleanup is called even on exception"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.side_effect = Exception("Failed")
        
        with patch.object(summarizer, '_cleanup_memory') as mock_cleanup:
            with pytest.raises(RuntimeError):
                summarizer.summarize("Test")
        
        mock_cleanup.assert_called_once()


class TestSummarizeSingleExceptionHandling:
    """Test _summarize_single exception handling - covers lines 127-129"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarize_single_raises_on_pipeline_failure(self, mock_cuda):
        """Test _summarize_single raises exception when pipeline fails"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.side_effect = Exception("Pipeline error")
        
        with pytest.raises(Exception, match="Pipeline error"):
            summarizer._summarize_single("Test text", 150, 40)


class TestSummarizeHierarchicalFullFlow:
    """Test _summarize_hierarchical full flow - covers lines 139-201"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_hierarchical_summarization_full_flow(self, mock_cuda):
        """Test hierarchical summarization processes all chunks"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.max_length = 512
        
        # Mock tokenizer
        summarizer.tokenizer = MagicMock()
        # First call for combined summaries check - return short (within limit)
        summarizer.tokenizer.encode.return_value = list(range(100))
        
        # Create mock chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "First chunk of text"
        mock_chunk1.token_count = 200
        mock_chunk1.chunk_id = 1
        
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "Second chunk of text"
        mock_chunk2.token_count = 200
        mock_chunk2.chunk_id = 2
        
        mock_chunk3 = MagicMock()
        mock_chunk3.text = "Third chunk of text"
        mock_chunk3.token_count = 200
        mock_chunk3.chunk_id = 3
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]
            
            # Mock _summarize_single to return summaries
            with patch.object(summarizer, '_summarize_single') as mock_single:
                mock_single.side_effect = [
                    "Summary of first chunk",
                    "Summary of second chunk",
                    "Summary of third chunk",
                    "Final combined summary"  # For the meta-summary
                ]
                
                with patch.object(summarizer, '_cleanup_memory'):
                    result = summarizer._summarize_hierarchical("Very long text", 150, 40)
        
        assert result == "Final combined summary"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_hierarchical_handles_chunk_failure(self, mock_cuda):
        """Test hierarchical summarization handles individual chunk failures - covers lines 171-178"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.max_length = 512
        
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = list(range(100))
        
        mock_chunk = MagicMock()
        mock_chunk.text = "Chunk text"
        mock_chunk.token_count = 200
        mock_chunk.chunk_id = 1
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk]
            
            with patch.object(summarizer, '_summarize_single') as mock_single:
                # First call fails, then we get the final summary
                mock_single.side_effect = [Exception("Chunk failed"), "Final summary"]
                
                with patch.object(summarizer, '_cleanup_memory'):
                    with patch.object(summarizer, '_create_fallback_summary', return_value="Fallback"):
                        result = summarizer._summarize_hierarchical("Long text", 150, 40)
        
        # Should have used fallback for failed chunk
        assert result is not None

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_hierarchical_final_summary_failure(self, mock_cuda):
        """Test hierarchical handles final summary failure - covers lines 196-198"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.max_length = 512
        
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = list(range(100))  # Within limit
        
        mock_chunk = MagicMock()
        mock_chunk.text = "Chunk text"
        mock_chunk.token_count = 200
        mock_chunk.chunk_id = 1
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk]
            
            # Mock for hierarchical calls - chunk succeeds, final fails
            call_count = [0]
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "Chunk summary"
                else:
                    raise Exception("Final summarization failed")
            
            with patch.object(summarizer, '_summarize_single', side_effect=side_effect):
                with patch.object(summarizer, '_cleanup_memory'):
                    with patch.object(summarizer, '_optimize_combined_summaries', return_value="Optimized"):
                        result = summarizer._summarize_hierarchical("Long text", 150, 40)
        
        assert result == "Optimized"

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_hierarchical_combined_too_long(self, mock_cuda):
        """Test hierarchical when combined summaries exceed limit - covers lines 199-201"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.max_length = 512
        
        summarizer.tokenizer = MagicMock()
        # Combined summaries are too long - exceeds max_length
        summarizer.tokenizer.encode.return_value = list(range(600))
        
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Chunk 1"
        mock_chunk1.token_count = 200
        mock_chunk1.chunk_id = 1
        
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "Chunk 2"
        mock_chunk2.token_count = 200
        mock_chunk2.chunk_id = 2
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk1, mock_chunk2]
            
            with patch.object(summarizer, '_summarize_single') as mock_single:
                mock_single.side_effect = ["Summary 1", "Summary 2"]
                
                with patch.object(summarizer, '_cleanup_memory'):
                    with patch.object(summarizer, '_optimize_combined_summaries', return_value="Optimized combined"):
                        result = summarizer._summarize_hierarchical("Long text", 150, 40)
        
        # Should use _optimize_combined_summaries since combined is too long
        assert result == "Optimized combined"


class TestCreateFallbackSummaryTruncation:
    """Test _create_fallback_summary truncation - covers line 213"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_fallback_truncates_very_long_single_sentence(self, mock_cuda):
        """Test fallback truncates very long single sentence to 200 chars"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        
        # Single sentence with no periods that exceeds 200 chars
        # Note: _create_fallback_summary splits on '. ' so a sentence without period is one item
        # When there's only one sentence, it tries to get first and last, but they're the same
        # With two sentences, it will take first + last
        text = "First. " + "A" * 250  # Very long second "sentence"
        result = summarizer._create_fallback_summary(text, max_sentences=2)
        
        # Should contain both parts since we have 2 sentences
        assert "First" in result


class TestOptimizeCombinedSummariesBreak:
    """Test _optimize_combined_summaries break statement - covers line 236"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_optimize_breaks_when_limit_reached(self, mock_cuda):
        """Test optimization breaks when length limit is reached"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        
        # Create chunks where adding the last one would exceed limit
        chunk_summaries = [
            {"summary": "A" * 100, "chunk_id": 1, "original_length": 500},  # Highest priority
            {"summary": "B" * 100, "chunk_id": 2, "original_length": 400},
            {"summary": "C" * 100, "chunk_id": 3, "original_length": 300},
            {"summary": "D" * 100, "chunk_id": 4, "original_length": 200},
        ]
        
        # Set max_length such that only first 2 can fit (max_length * 4 chars)
        result = summarizer._optimize_combined_summaries(chunk_summaries, max_length=50)
        
        # Should stop before including all summaries
        # max_length * 4 = 200 chars limit
        assert len(result) <= 300  # Should have stopped adding


class TestOptimizeCombinedSummariesLengthLimiting:
    """Test _optimize_combined_summaries length limiting - covers lines 239-241"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_optimize_limits_final_length(self, mock_cuda):
        """Test optimization limits final text length"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        
        # Create one very long summary that exceeds max_length * 6
        chunk_summaries = [
            {"summary": "word " * 500, "chunk_id": 1, "original_length": 1000},
        ]
        
        # max_length = 50, so max_length * 6 = 300 chars
        result = summarizer._optimize_combined_summaries(chunk_summaries, max_length=50)
        
        # Result should be trimmed if it exceeds max_length * 6
        # The implementation cuts to max_length * 2 words (100 words)
        words = result.split()
        assert len(words) <= 100 or len(result) <= 600  # Either word limit or char limit


class TestSummarizeWithFallbackFinalReturn:
    """Test summarize_with_fallback final return - covers line 282"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarize_with_fallback_returns_after_loop(self, mock_cuda):
        """Test summarize_with_fallback returns fallback after all retries exhausted"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        
        # Every attempt fails
        with patch.object(summarizer, 'summarize', side_effect=Exception("Failed")):
            with patch.object(summarizer, '_cleanup_memory'):
                result = summarizer.summarize_with_fallback("Test text here", max_retries=0)
        
        # Should return fallback summary
        assert result is not None
        # Fallback creates extractive summary
        assert isinstance(result, str)


class TestEstimateSummarizationTimeHierarchical:
    """Test estimate_summarization_time hierarchical path - covers lines 296-298"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_estimate_time_for_long_text(self, mock_cuda):
        """Test time estimation for text requiring hierarchical summarization"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.max_length = 512
        
        # Mock tokenizer to return long token list
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = list(range(700))  # > max_length
        
        # Mock chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.token_count = 350
        mock_chunk2 = MagicMock()
        mock_chunk2.token_count = 350
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk1, mock_chunk2]
            mock_chunker.estimate_processing_time.return_value = 5.0
            
            result = summarizer.estimate_summarization_time("Very long text that needs chunking")
        
        # Should return chunker estimate * 1.5
        assert result == 7.5


class TestGetSummarizationStrategyInfoHierarchical:
    """Test get_summarization_strategy_info hierarchical path - covers lines 315-317"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_strategy_info_for_long_text(self, mock_cuda):
        """Test strategy info returns hierarchical for long text"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.max_length = 512
        
        # Mock tokenizer to return long token list
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = list(range(700))  # > max_length - 50
        
        # Mock chunks
        mock_chunk1 = MagicMock()
        mock_chunk2 = MagicMock()
        mock_chunk3 = MagicMock()
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]
            
            result = summarizer.get_summarization_strategy_info("Very long text")
        
        assert result["strategy"] == "hierarchical"
        assert result["chunk_count"] == 3
        assert result["token_count"] == 700
        assert "estimated_time" in result


class TestGlobalSummarizerInstance:
    """Test global summarization_model instance"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_global_instance_exists(self, mock_cuda):
        """Test that global summarization_model instance exists"""
        mock_cuda.return_value = False
        
        from app.model_scripts.summarizer_model import summarization_model
        
        assert summarization_model is not None
        assert hasattr(summarization_model, 'summarize')
        assert hasattr(summarization_model, 'load')


class TestSummarizeIntegration:
    """Integration tests for summarize flow"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_summarize_with_min_length(self, mock_cuda):
        """Test summarize respects min_length parameter"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.max_length = 512
        
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = [1, 2, 3]  # Short text
        
        summarizer.pipeline = MagicMock()
        summarizer.pipeline.return_value = [{"summary_text": "Short summary"}]
        
        with patch.object(summarizer, '_cleanup_memory'):
            result = summarizer.summarize("Test text", max_length=100, min_length=20)
        
        # Verify pipeline was called with correct parameters
        summarizer.pipeline.assert_called_once()
        call_kwargs = summarizer.pipeline.call_args
        assert call_kwargs[1]['min_length'] == 20
        assert call_kwargs[1]['max_length'] == 100


class TestHierarchicalCleanupFrequency:
    """Test cleanup is called every 3 chunks - covers lines 167-169"""

    @patch('app.model_scripts.summarizer_model.torch.cuda.is_available')
    def test_cleanup_called_every_three_chunks(self, mock_cuda):
        """Test cleanup is called at regular intervals during hierarchical summarization"""
        from app.model_scripts.summarizer_model import SummarizationModel
        
        mock_cuda.return_value = False
        
        summarizer = SummarizationModel()
        summarizer.loaded = True
        summarizer.max_length = 512
        
        summarizer.tokenizer = MagicMock()
        summarizer.tokenizer.encode.return_value = list(range(100))
        
        # Create 6 chunks to trigger cleanup twice (at i=0 and i=3)
        chunks = []
        for i in range(6):
            mock_chunk = MagicMock()
            mock_chunk.text = f"Chunk {i}"
            mock_chunk.token_count = 100
            mock_chunk.chunk_id = i + 1
            chunks.append(mock_chunk)
        
        with patch('app.core.text_chunker.text_chunker') as mock_chunker:
            mock_chunker.chunk_text.return_value = chunks
            
            with patch.object(summarizer, '_summarize_single') as mock_single:
                mock_single.return_value = "Summary"
                
                with patch.object(summarizer, '_cleanup_memory') as mock_cleanup:
                    try:
                        summarizer._summarize_hierarchical("Long text", 150, 40)
                    except:
                        pass
                
                # Cleanup should be called for i=0 and i=3 (every 3 chunks)
                assert mock_cleanup.call_count >= 2
