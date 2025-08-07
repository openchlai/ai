# app/core/text_chunker.py
import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from transformers import AutoTokenizer
import spacy

logger = logging.getLogger(__name__)

@dataclass
class ChunkConfig:
    """Configuration for text chunking strategies"""
    max_tokens: int
    overlap_tokens: int
    min_chunk_tokens: int
    preserve_sentences: bool = True
    preserve_paragraphs: bool = True

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    text: str
    start_pos: int
    end_pos: int
    chunk_id: int
    token_count: int
    sentence_count: int
    overlap_with_previous: bool = False
    overlap_with_next: bool = False

class IntelligentTextChunker:
    """
    Intelligent text chunking with sliding window strategy
    Supports semantic chunking using sentence boundaries
    """
    
    def __init__(self):
        # Model-specific chunking configurations
        self.chunk_configs = {
            "translation": ChunkConfig(
                max_tokens=450,  # Leave buffer for special tokens
                overlap_tokens=50,
                min_chunk_tokens=10,
                preserve_sentences=True
            ),
            "classification": ChunkConfig(
                max_tokens=400,
                overlap_tokens=30,
                min_chunk_tokens=5,
                preserve_sentences=True
            ),
            "summarization": ChunkConfig(
                max_tokens=900,  # Larger chunks for better context
                overlap_tokens=100,
                min_chunk_tokens=50,
                preserve_sentences=True
            ),
            "ner": ChunkConfig(
                max_tokens=400,
                overlap_tokens=30,
                min_chunk_tokens=10,
                preserve_sentences=False  # NER can work with partial sentences
            )
        }
        
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        except Exception as e:
            logger.warning(f"Could not load tokenizer: {e}. Using approximate counting.")
            self.tokenizer = None
        
        # Initialize spaCy for sentence segmentation
        try:
            self.nlp = spacy.load("en_core_web_md", disable=["ner", "parser", "tagger"])
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}. Using regex fallback.")
            self.nlp = None
    
    def count_tokens(self, text: str) -> int:
        """Accurately count tokens in text"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text, add_special_tokens=True))
            except Exception:
                pass
        
        # Fallback: approximate token count (1 token ≈ 4 characters for English)
        return max(1, len(text) // 4)
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using spaCy or regex fallback"""
        if self.nlp:
            try:
                doc = self.nlp(text)
                sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
                return sentences if sentences else [text]
            except Exception:
                pass
        
        # Fallback: regex-based sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences if sentences else [text]
    
    def chunk_text(self, text: str, strategy: str = "classification") -> List[TextChunk]:
        """
        Chunk text using intelligent sliding window strategy
        
        Args:
            text: Input text to chunk
            strategy: Chunking strategy (translation, classification, summarization, ner)
            
        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []
        
        text = text.strip()
        config = self.chunk_configs.get(strategy, self.chunk_configs["classification"])
        
        # Quick check: if text is already short enough, return as single chunk
        token_count = self.count_tokens(text)
        if token_count <= config.max_tokens:
            return [TextChunk(
                text=text,
                start_pos=0,
                end_pos=len(text),
                chunk_id=0,
                token_count=token_count,
                sentence_count=len(self.split_into_sentences(text))
            )]
        
        logger.info(f"Chunking {token_count} tokens using {strategy} strategy (max: {config.max_tokens})")
        
        if config.preserve_sentences:
            return self._chunk_by_sentences(text, config)
        else:
            return self._chunk_by_tokens(text, config)
    
    def _chunk_by_sentences(self, text: str, config: ChunkConfig) -> List[TextChunk]:
        """Chunk text preserving sentence boundaries"""
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk_sentences = []
        current_chunk_tokens = 0
        chunk_id = 0
        text_position = 0
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = self.count_tokens(sentence)
            
            # If single sentence exceeds max tokens, force split it
            if sentence_tokens > config.max_tokens:
                # Process accumulated sentences first
                if current_chunk_sentences:
                    chunk_text = ' '.join(current_chunk_sentences)
                    chunk_start = text_position - len(chunk_text)
                    
                    chunks.append(TextChunk(
                        text=chunk_text,
                        start_pos=max(0, chunk_start),
                        end_pos=text_position,
                        chunk_id=chunk_id,
                        token_count=current_chunk_tokens,
                        sentence_count=len(current_chunk_sentences)
                    ))
                    chunk_id += 1
                    current_chunk_sentences = []
                    current_chunk_tokens = 0
                
                # Split the long sentence by tokens
                long_sentence_chunks = self._chunk_by_tokens(sentence, config, start_chunk_id=chunk_id)
                for chunk in long_sentence_chunks:
                    chunk.start_pos += text_position
                    chunk.end_pos += text_position
                chunks.extend(long_sentence_chunks)
                chunk_id += len(long_sentence_chunks)
                text_position += len(sentence) + 1
                continue
            
            # Check if adding this sentence would exceed limit
            potential_tokens = current_chunk_tokens + sentence_tokens
            
            if potential_tokens > config.max_tokens and current_chunk_sentences:
                # Create chunk from accumulated sentences
                chunk_text = ' '.join(current_chunk_sentences)
                chunk_start = text_position - len(chunk_text)
                
                chunks.append(TextChunk(
                    text=chunk_text,
                    start_pos=max(0, chunk_start),
                    end_pos=text_position,
                    chunk_id=chunk_id,
                    token_count=current_chunk_tokens,
                    sentence_count=len(current_chunk_sentences),
                    overlap_with_next=True if config.overlap_tokens > 0 else False
                ))
                
                # Handle overlap: keep last few sentences for next chunk
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk_sentences, config.overlap_tokens
                )
                
                current_chunk_sentences = overlap_sentences + [sentence]
                current_chunk_tokens = sum(self.count_tokens(s) for s in current_chunk_sentences)
                chunk_id += 1
            else:
                # Add sentence to current chunk
                current_chunk_sentences.append(sentence)
                current_chunk_tokens = potential_tokens
            
            text_position += len(sentence) + 1
        
        # Handle remaining sentences
        if current_chunk_sentences:
            chunk_text = ' '.join(current_chunk_sentences)
            chunk_start = text_position - len(chunk_text)
            
            chunks.append(TextChunk(
                text=chunk_text,
                start_pos=max(0, chunk_start),
                end_pos=text_position,
                chunk_id=chunk_id,
                token_count=current_chunk_tokens,
                sentence_count=len(current_chunk_sentences)
            ))
        
        # Mark overlaps
        for i in range(len(chunks) - 1):
            if chunks[i].overlap_with_next:
                chunks[i + 1].overlap_with_previous = True
        
        logger.info(f"Created {len(chunks)} sentence-based chunks")
        return chunks
    
    def _chunk_by_tokens(self, text: str, config: ChunkConfig, start_chunk_id: int = 0) -> List[TextChunk]:
        """Chunk text by token count (fallback for very long sentences)"""
        words = text.split()
        chunks = []
        chunk_id = start_chunk_id
        
        current_words = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self.count_tokens(word)
            
            if current_tokens + word_tokens > config.max_tokens and current_words:
                # Create chunk
                chunk_text = ' '.join(current_words)
                chunks.append(TextChunk(
                    text=chunk_text,
                    start_pos=0,  # Approximation for token-based chunking
                    end_pos=len(chunk_text),
                    chunk_id=chunk_id,
                    token_count=current_tokens,
                    sentence_count=1  # Approximation
                ))
                
                # Handle overlap
                overlap_words = current_words[-max(1, config.overlap_tokens // 10):]
                current_words = overlap_words + [word]
                current_tokens = sum(self.count_tokens(w) for w in current_words)
                chunk_id += 1
            else:
                current_words.append(word)
                current_tokens += word_tokens
        
        # Handle remaining words
        if current_words:
            chunk_text = ' '.join(current_words)
            chunks.append(TextChunk(
                text=chunk_text,
                start_pos=0,
                end_pos=len(chunk_text),
                chunk_id=chunk_id,
                token_count=current_tokens,
                sentence_count=1
            ))
        
        logger.info(f"Created {len(chunks)} token-based chunks")
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_tokens: int) -> List[str]:
        """Get sentences for overlap based on token budget"""
        if overlap_tokens <= 0:
            return []
        
        overlap_sentences = []
        tokens_used = 0
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            sentence_tokens = self.count_tokens(sentence)
            if tokens_used + sentence_tokens <= overlap_tokens:
                overlap_sentences.insert(0, sentence)
                tokens_used += sentence_tokens
            else:
                break
        
        return overlap_sentences
    
    def get_chunking_strategy_for_model(self, model_type: str) -> str:
        """Get the appropriate chunking strategy for a model type"""
        strategy_mapping = {
            "translator": "translation",
            "translator_model": "translation",
            "classifier": "classification", 
            "classifier_model": "classification",
            "summarizer": "summarization",
            "summarizer_model": "summarization",
            "ner": "ner",
            "ner_model": "ner"
        }
        return strategy_mapping.get(model_type, "classification")
    
    def estimate_processing_time(self, chunks: List[TextChunk], model_type: str) -> float:
        """Estimate processing time based on chunk count and model type"""
        base_times = {
            "translation": 2.0,      # seconds per chunk
            "classification": 0.5,   # seconds per chunk
            "summarization": 3.0,    # seconds per chunk
            "ner": 0.3              # seconds per chunk
        }
        
        strategy = self.get_chunking_strategy_for_model(model_type)
        base_time = base_times.get(strategy, 1.0)
        
        return len(chunks) * base_time

# Global chunker instance
text_chunker = IntelligentTextChunker()