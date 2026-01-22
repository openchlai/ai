"""
OpenCHS AI Pipeline - Transcript Chunking Pipeline
Handles chunking for Classification, QA Scoring, Translation, Summarization, and NER models
"""

import re
from typing import List, Dict, Any, Tuple, Union
from transformers import AutoTokenizer
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BaseChunker:
    """Base class for all chunking strategies"""
    
    def __init__(self, tokenizer_name: str = "distilbert-base-uncased", max_tokens: int = 512):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_tokens = max_tokens
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text, add_special_tokens=True))
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle multiple sentence endings and common abbreviations
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Simple sentence splitter (you can use nltk.sent_tokenize for better results)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]


class ClassificationChunker(BaseChunker):
    """
    Chunker for Classification models (Multitask Classifier, QA Scoring)
    - Max 512 tokens per chunk
    - 150 token overlap between chunks for context preservation
    """
    
    def __init__(self, tokenizer_name: str = "distilbert-base-uncased", 
                 max_tokens: int = 512, overlap_tokens: int = 150):
        super().__init__(tokenizer_name, max_tokens)
        self.overlap_tokens = overlap_tokens
    
    def chunk_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Chunk transcript with overlapping context
        Returns list of chunks with metadata
        """
        sentences = self.split_into_sentences(transcript)
        chunks = []
        
        current_chunk = ""
        current_sentences = []
        overlap_buffer = []
        chunk_index = 0
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = self.count_tokens(test_chunk)
            
            if token_count <= self.max_tokens:
                current_chunk = test_chunk
                current_sentences.append(sentence)
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'token_count': self.count_tokens(current_chunk),
                        'sentence_count': len(current_sentences)
                    })
                    chunk_index += 1
                    
                    # Calculate overlap for next chunk
                    overlap_buffer = self._get_overlap_sentences(
                        current_sentences, 
                        self.overlap_tokens
                    )
                
                # Start new chunk with overlap + current sentence
                if overlap_buffer:
                    current_chunk = " ".join(overlap_buffer) + " " + sentence
                    current_sentences = overlap_buffer + [sentence]
                else:
                    current_chunk = sentence
                    current_sentences = [sentence]
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_index': chunk_index,
                'token_count': self.count_tokens(current_chunk),
                'sentence_count': len(current_sentences)
            })
        
        # Add total chunks info to each chunk
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk['total_chunks'] = total_chunks
            chunk['position_ratio'] = chunk['chunk_index'] / max(total_chunks - 1, 1)
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str], target_tokens: int) -> List[str]:
        """Get sentences from the end that fit within target token count"""
        overlap = []
        token_count = 0
        
        # Work backwards from the end
        for sentence in reversed(sentences):
            test_overlap = [sentence] + overlap
            test_text = " ".join(test_overlap)
            test_tokens = self.count_tokens(test_text)
            
            if test_tokens <= target_tokens:
                overlap = test_overlap
                token_count = test_tokens
            else:
                break
        
        return overlap


class TranslationChunker(BaseChunker):
    """
    Chunker for Translation models (Helsinki/opus-mt)
    - Max 512 tokens per chunk
    - No overlap (context not needed)
    - Smart chunking at sentence boundaries
    """
    
    def chunk_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Chunk transcript at sentence boundaries without overlap
        """
        sentences = self.split_into_sentences(transcript)
        chunks = []
        
        current_chunk = ""
        current_sentences = []
        chunk_index = 0
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = self.count_tokens(test_chunk)
            
            if token_count <= self.max_tokens:
                current_chunk = test_chunk
                current_sentences.append(sentence)
            else:
                # Save current chunk
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'token_count': self.count_tokens(current_chunk),
                        'sentence_count': len(current_sentences)
                    })
                    chunk_index += 1
                
                # Start new chunk with current sentence
                current_chunk = sentence
                current_sentences = [sentence]
        
        # Last chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_index': chunk_index,
                'token_count': self.count_tokens(current_chunk),
                'sentence_count': len(current_sentences)
            })
        
        return chunks
    
    def reconstruct_translation(self, translated_chunks: List[str]) -> str:
        """
        Reconstruct full translation from translated chunks
        """
        return " ".join(translated_chunks)


class SummarizationChunker(BaseChunker):
    """
    Chunker for Summarization models (FLAN)
    - Sentence-boundary aware like translation
    - But includes context overlap for better coherence
    """
    
    def __init__(self, tokenizer_name: str = "openchs/sum-flan-t5-base-synthetic-v1", 
                 max_tokens: int = 512, overlap_tokens: int = 100):
        super().__init__(tokenizer_name, max_tokens)
        self.overlap_tokens = overlap_tokens
    
    def chunk_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Chunk transcript with light overlap for summarization context
        """
        sentences = self.split_into_sentences(transcript)
        chunks = []
        
        current_chunk = ""
        current_sentences = []
        overlap_buffer = []
        chunk_index = 0
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = self.count_tokens(test_chunk)
            
            if token_count <= self.max_tokens:
                current_chunk = test_chunk
                current_sentences.append(sentence)
            else:
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'token_count': self.count_tokens(current_chunk),
                        'sentence_count': len(current_sentences)
                    })
                    chunk_index += 1
                    
                    # Get overlap sentences
                    overlap_buffer = self._get_overlap_sentences(
                        current_sentences, 
                        self.overlap_tokens
                    )
                
                # New chunk with overlap
                if overlap_buffer:
                    current_chunk = " ".join(overlap_buffer) + " " + sentence
                    current_sentences = overlap_buffer + [sentence]
                else:
                    current_chunk = sentence
                    current_sentences = [sentence]
        
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_index': chunk_index,
                'token_count': self.count_tokens(current_chunk),
                'sentence_count': len(current_sentences)
            })
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str], target_tokens: int) -> List[str]:
        """Get sentences from the end that fit within target token count"""
        overlap = []
        for sentence in reversed(sentences):
            test_overlap = [sentence] + overlap
            test_text = " ".join(test_overlap)
            if self.count_tokens(test_text) <= target_tokens:
                overlap = test_overlap
            else:
                break
        return overlap
    
    def reconstruct_summary(self, chunk_summaries: List[str]) -> str:
        """
        Reconstruct full summary from chunk summaries as paragraphs
        """
        # Join summaries with paragraph breaks
        return "\n\n".join(chunk_summaries)

class NERChunker(BaseChunker):
    """
    Chunker for NER models
    - Sentence-boundary aware
    - No overlap needed
    - Tracks character positions for entity reconstruction
    """
    
    def chunk_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Chunk transcript at sentence boundaries for NER
        Maintains character position metadata for reconstruction
        """
        sentences = self.split_into_sentences(transcript)
        chunks = []
        
        current_chunk = ""
        current_sentences = []
        chunk_index = 0
        start_char_idx = 0
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = self.count_tokens(test_chunk)
            
            if token_count <= self.max_tokens:
                current_chunk = test_chunk
                current_sentences.append(sentence)
            else:
                if current_chunk.strip():
                    chunk_text = current_chunk.strip()
                    chunks.append({
                        'text': chunk_text,
                        'chunk_index': chunk_index,
                        'token_count': self.count_tokens(chunk_text),
                        'sentence_count': len(current_sentences),
                        'start_char': start_char_idx,
                        'end_char': start_char_idx + len(chunk_text)
                    })
                    start_char_idx += len(chunk_text) + 1  # +1 for space
                    chunk_index += 1
                
                current_chunk = sentence
                current_sentences = [sentence]
        
        if current_chunk.strip():
            chunk_text = current_chunk.strip()
            chunks.append({
                'text': chunk_text,
                'chunk_index': chunk_index,
                'token_count': self.count_tokens(chunk_text),
                'sentence_count': len(current_sentences),
                'start_char': start_char_idx,
                'end_char': start_char_idx + len(chunk_text)
            })
        
        return chunks
    
    def reconstruct_entities(
        self, 
        chunk_entities: List[List[Dict]], 
        chunks: List[Dict],
        flat: bool = True
    ) -> Union[List[Dict], Dict[str, List[str]]]:
        """
        Reconstruct full entity list from chunked NER results
        Adjusts character positions based on chunk offsets
        
        Args:
            chunk_entities: List of entity lists from each chunk
            chunks: List of chunk metadata from chunk_transcript()
            flat: If True, return flat list; if False, return grouped by label
            
        Returns:
            Either List[Dict] with adjusted positions or Dict[str, List[str]] grouped by label
        """
        if not chunk_entities or not chunks:
            return [] if flat else {}
        
        all_entities = []
        
        # Process each chunk's entities
        for chunk_idx, entities in enumerate(chunk_entities):
            if chunk_idx >= len(chunks):
                logger.warning(f"Chunk index {chunk_idx} out of bounds for chunks")
                continue
            
            chunk_info = chunks[chunk_idx]
            chunk_start = chunk_info['start_char']
            
            for entity in entities:
                # Adjust character positions based on chunk offset
                adjusted_entity = {
                    'text': entity.get('text', ''),
                    'label': entity.get('label', ''),
                    'start': entity.get('start', 0) + chunk_start,
                    'end': entity.get('end', 0) + chunk_start,
                    'confidence': entity.get('confidence', 0.0)
                }
                all_entities.append(adjusted_entity)
        
        # Remove duplicates (entities at same position with same label)
        unique_entities = []
        seen = set()
        
        for entity in sorted(all_entities, key=lambda e: (e['start'], e['end'], e['label'])):
            entity_key = (entity['start'], entity['end'], entity['label'])
            if entity_key not in seen:
                seen.add(entity_key)
                unique_entities.append(entity)
        
        # Return in requested format
        if flat:
            return unique_entities
        else:
            # Group by label
            grouped = {}
            for entity in unique_entities:
                label = entity['label']
                if label not in grouped:
                    grouped[label] = []
                # Avoid duplicate texts for same label
                if entity['text'] not in grouped[label]:
                    grouped[label].append(entity['text'])
            return grouped

# AGGREGATION STRATEGIES FOR CLASSIFICATION MODELS

class ClassificationAggregator:
    """
    Aggregates predictions from multiple chunks for classification tasks
    """
    
    @staticmethod
    def aggregate_case_classification(chunk_predictions: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate case category classification results
        Uses confidence-weighted voting
        Returns top 2 subcategories instead of just 1
        """
        if not chunk_predictions:
            return None
        
        if len(chunk_predictions) == 1:
            # Single chunk - get top 2 subcategories
            pred = chunk_predictions[0]
            subcategories = ClassificationAggregator._get_top_2_subcategories_single(pred)
            
            return {
                'main_category': pred['main_category'],
                'sub_category': subcategories['sub_category'],
                'sub_category_2': subcategories['sub_category_2'],
                'intervention': pred['intervention'],
                'priority': pred['priority'],
                'confidence_scores': {
                    'main_category': pred['confidence_scores']['main_category'],
                    'sub_category': subcategories['sub_category_confidence'],
                    'sub_category_2': subcategories['sub_category_2_confidence'],
                    'intervention': pred['confidence_scores']['intervention'],
                    'priority': pred['confidence_scores']['priority']
                },
                'num_chunks': 1
            }
        
        # Multiple chunks - aggregate with weighted voting
        fields = ['main_category', 'intervention', 'priority']
        aggregated = {}
        aggregated_confidences = {}
        
        # Standard aggregation for main_category, intervention, priority
        for field in fields:
            votes = {}
            
            for pred in chunk_predictions:
                value = pred[field]
                confidence = pred['confidence_scores'][field]
                
                if value not in votes:
                    votes[value] = []
                votes[value].append(confidence)
            
            # Weighted voting: sum of confidence scores
            vote_scores = {k: sum(v) for k, v in votes.items()}
            best_prediction = max(vote_scores, key=vote_scores.get)
            
            # Average confidence for the winning prediction
            avg_confidence = np.mean(votes[best_prediction])
            
            aggregated[field] = best_prediction
            aggregated_confidences[field] = float(avg_confidence)
        
        # Special handling for subcategories - get top 2
        subcategories = ClassificationAggregator._get_top_2_subcategories_multi(chunk_predictions)
        
        aggregated['sub_category'] = subcategories['sub_category']
        aggregated['sub_category_2'] = subcategories['sub_category_2']
        aggregated_confidences['sub_category'] = subcategories['sub_category_confidence']
        aggregated_confidences['sub_category_2'] = subcategories['sub_category_2_confidence']
        
        aggregated['confidence_scores'] = aggregated_confidences
        aggregated['num_chunks'] = len(chunk_predictions)
        
        return aggregated
    
    @staticmethod
    def _get_top_2_subcategories_single(prediction: Dict) -> Dict[str, Any]:
        """
        Extract top 2 subcategories from a single prediction
        Assumes the model returns raw scores/logits for all subcategory classes
        
        If your model only returns the top class, you'll need to modify your model
        to return scores for all classes or at least top-k classes
        """
        # This assumes you have access to all subcategory scores
        # You may need to modify your model's predict method to return this
        
        sub_category = prediction['sub_category']
        sub_category_confidence = prediction['confidence_scores']['sub_category']
        
        # Placeholder for second subcategory
        # You'll need to get this from your model's raw output
        # For now, returning None as we don't have access to the second-best prediction
        
        return {
            'sub_category': sub_category,
            'sub_category_confidence': sub_category_confidence,
            'sub_category_2': None,  # Will need model modification
            'sub_category_2_confidence': 0.0
        }
    
    @staticmethod
    def _get_top_2_subcategories_multi(chunk_predictions: List[Dict]) -> Dict[str, Any]:
        """
        Get top 2 subcategories from multiple chunk predictions
        Uses weighted voting across all chunks
        NOW COLLECTS BOTH sub_category AND sub_category_2 from each chunk
        """
        # Collect all subcategory votes with their confidence scores
        subcategory_votes = {}
        
        for pred in chunk_predictions:
            # Get top-1 subcategory
            sub_cat_1 = pred.get('sub_category')
            confidence_1 = pred['confidence_scores'].get('sub_category', 0.0)
            
            if sub_cat_1:
                if sub_cat_1 not in subcategory_votes:
                    subcategory_votes[sub_cat_1] = []
                subcategory_votes[sub_cat_1].append(confidence_1)
            
            # Get top-2 subcategory (NEW!)
            sub_cat_2 = pred.get('sub_category_2')
            confidence_2 = pred['confidence_scores'].get('sub_category_2', 0.0)
            
            if sub_cat_2:  # Only add if not None
                if sub_cat_2 not in subcategory_votes:
                    subcategory_votes[sub_cat_2] = []
                subcategory_votes[sub_cat_2].append(confidence_2)
        
        # Calculate weighted scores (sum of confidences)
        vote_scores = {k: sum(v) for k, v in subcategory_votes.items()}
        
        # Sort by score to get top 2
        sorted_subcategories = sorted(vote_scores.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_subcategories) >= 2:
            top_1 = sorted_subcategories[0]
            top_2 = sorted_subcategories[1]
            
            return {
                'sub_category': top_1[0],
                'sub_category_confidence': float(np.mean(subcategory_votes[top_1[0]])),
                'sub_category_2': top_2[0],
                'sub_category_2_confidence': float(np.mean(subcategory_votes[top_2[0]]))
            }
        elif len(sorted_subcategories) == 1:
            # Only one subcategory found across all chunks
            top_1 = sorted_subcategories[0]
            
            return {
                'sub_category': top_1[0],
                'sub_category_confidence': float(np.mean(subcategory_votes[top_1[0]])),
                'sub_category_2': None,
                'sub_category_2_confidence': 0.0
            }
        else:
            # No subcategories (shouldn't happen)
            return {
                'sub_category': None,
                'sub_category_confidence': 0.0,
                'sub_category_2': None,
                'sub_category_2_confidence': 0.0
            }
    
            
    @staticmethod
    def aggregate_qa_scoring(chunk_predictions: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate QA scoring results across chunks
        Uses probability-weighted voting for each submetric
        """
        if not chunk_predictions:
            return None
        
        if len(chunk_predictions) == 1:
            return {
                'success': True,
                'predictions': chunk_predictions[0],
                'num_chunks': 1
            }
        
        # Get all categories and submetrics
        # chunk_predictions structure: [{'opening': [...], 'listening': [...]}, ...]
        categories = chunk_predictions[0].keys()  # FIXED: Direct access
        aggregated_predictions = {}
        
        for category in categories:
            aggregated_predictions[category] = []
            
            # Get all submetrics in this category
            submetrics = chunk_predictions[0][category]  # FIXED: Direct access
            
            for submetric_idx, submetric_info in enumerate(submetrics):
                submetric_name = submetric_info['submetric']
                
                # Collect predictions and probabilities for this submetric
                predictions = []
                probabilities = []
                
                for chunk_pred in chunk_predictions:
                    sub_pred = chunk_pred[category][submetric_idx]  # FIXED: Direct access
                    predictions.append(sub_pred['prediction'])
                    probabilities.append(sub_pred['probability'])
                
                # Aggregate using weighted voting
                # Weight True predictions by their probability
                true_score = sum(p for pred, p in zip(predictions, probabilities) if pred)
                false_score = sum(p for pred, p in zip(predictions, probabilities) if not pred)
                
                final_prediction = true_score > false_score
                avg_probability = np.mean(probabilities)
                
                aggregated_predictions[category].append({
                    'submetric': submetric_name,
                    'prediction': final_prediction,
                    'score': '✓' if final_prediction else '✗',
                    'probability': float(avg_probability)
                })
        
        return {
            'success': True,
            'predictions': aggregated_predictions,
            'num_chunks': len(chunk_predictions)
        }
