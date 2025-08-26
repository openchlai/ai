# tests/test_qa_model.py
import pytest
import sys
import os
import torch
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_qa_model():
    """Create a mocked QA model for testing"""
    with patch("app.model_scripts.qa_model.DistilBertTokenizer.from_pretrained") as mock_tokenizer, \
         patch("app.model_scripts.qa_model.torch.load") as mock_load, \
         patch("os.path.exists", return_value=True):
        
        # Mock tokenizer
        mock_tok = MagicMock()
        mock_tok.encode_plus.return_value = {
            'input_ids': torch.tensor([[1, 2, 3, 4, 5]]),
            'attention_mask': torch.tensor([[1, 1, 1, 1, 1]])
        }
        mock_tok.convert_tokens_to_string.return_value = "test text"
        mock_tokenizer.from_pretrained.return_value = mock_tok
        
        # Mock model state dict
        mock_state = {
            'bert.embeddings.word_embeddings.weight': torch.randn(100, 768),
            'qa_heads.opening.0.weight': torch.randn(1, 768),
            'qa_heads.opening.0.bias': torch.randn(1)
        }
        mock_load.return_value = mock_state
        
        from app.model_scripts.qa_model import QAModel
        model = QAModel()
        model.tokenizer = mock_tok
        model.model = MagicMock()
        model.loaded = True
        model.load_time = datetime.now()
        return model

def test_qa_model_initialization():
    """Test QAModel initialization"""
    with patch("app.config.settings.Settings.get_model_path", return_value="/fake/path"):
        from app.model_scripts.qa_model import QAModel
        model = QAModel()
        assert model.model_path == "/fake/path"
        assert not model.loaded
        assert model.max_sequence_length == 512

def test_qa_model_load_success():
    """Test successful QA model loading"""
    with patch("app.model_scripts.qa_model.DistilBertTokenizer.from_pretrained") as mock_tokenizer, \
         patch("app.model_scripts.qa_model.torch.load") as mock_load, \
         patch("os.path.exists", return_value=True):
        
        # Mock tokenizer and model loading
        mock_tokenizer.return_value = MagicMock()
        mock_load.return_value = {"test": "state"}
        
        from app.model_scripts.qa_model import QAModel
        model = QAModel()
        
        # Mock the model creation
        with patch.object(model, '_create_model') as mock_create:
            mock_model = MagicMock()
            mock_create.return_value = mock_model
            
            result = model.load()
            
            assert result is True
            assert model.loaded is True

def test_qa_model_load_failure():
    """Test QA model loading failure"""
    with patch("os.path.exists", return_value=False):
        from app.model_scripts.qa_model import QAModel
        model = QAModel()
        result = model.load()
        
        assert result is False
        assert model.loaded is False
        assert model.error is not None

def test_evaluate_transcript(mock_qa_model):
    """Test transcript evaluation"""
    transcript = "Hello, thank you for calling. How can I help you today?"
    
    # Mock model output
    mock_qa_model.model.return_value = {
        'opening': torch.tensor([[0.8]]),
        'listening': torch.tensor([[0.7, 0.8, 0.6, 0.9, 0.5]]),
        'proactiveness': torch.tensor([[0.6, 0.7, 0.8]]),
        'resolution': torch.tensor([[0.8, 0.9, 0.7, 0.6, 0.8]]),
        'hold': torch.tensor([[0.5, 0.6]]),
        'closing': torch.tensor([[0.4]])
    }
    
    result = mock_qa_model.evaluate_transcript(transcript)
    
    assert isinstance(result, dict)
    assert "scores" in result
    assert "overall_score" in result
    assert "breakdown" in result

def test_evaluate_empty_transcript(mock_qa_model):
    """Test evaluating empty transcript"""
    result = mock_qa_model.evaluate_transcript("")
    
    # Should return default/low scores
    assert isinstance(result, dict)
    assert "scores" in result

def test_evaluate_transcript_not_loaded():
    """Test evaluating transcript when model is not loaded"""
    from app.model_scripts.qa_model import QAModel
    model = QAModel()
    
    with pytest.raises(RuntimeError, match="QA model is not loaded"):
        model.evaluate_transcript("Hello world")

def test_get_qa_metrics(mock_qa_model):
    """Test getting available QA metrics"""
    metrics = mock_qa_model.get_qa_metrics()
    
    assert isinstance(metrics, dict)
    assert "opening" in metrics
    assert "listening" in metrics
    assert "resolution" in metrics

def test_calculate_overall_score(mock_qa_model):
    """Test overall score calculation"""
    scores = {
        "opening": 0.8,
        "listening": 0.7,
        "proactiveness": 0.6,
        "resolution": 0.8,
        "hold": 0.5,
        "closing": 0.4
    }
    
    overall_score = mock_qa_model._calculate_overall_score(scores)
    
    assert isinstance(overall_score, float)
    assert 0 <= overall_score <= 1

def test_get_score_interpretation(mock_qa_model):
    """Test score interpretation"""
    interpretation = mock_qa_model.get_score_interpretation(0.8)
    assert isinstance(interpretation, str)
    
    interpretation = mock_qa_model.get_score_interpretation(0.5)
    assert isinstance(interpretation, str)
    
    interpretation = mock_qa_model.get_score_interpretation(0.2)
    assert isinstance(interpretation, str)

def test_get_recommendations(mock_qa_model):
    """Test getting recommendations based on scores"""
    scores = {
        "opening": 0.3,  # Low score
        "listening": 0.9,  # High score
        "resolution": 0.5  # Medium score
    }
    
    recommendations = mock_qa_model.get_recommendations(scores)
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

def test_batch_evaluate(mock_qa_model):
    """Test batch transcript evaluation"""
    transcripts = [
        "Hello, how can I help?",
        "Thank you for calling our service.",
        "Let me check that for you."
    ]
    
    # Mock model outputs for batch
    mock_qa_model.model.return_value = {
        'opening': torch.tensor([[0.8], [0.9], [0.7]]),
        'listening': torch.tensor([[0.7, 0.8, 0.6, 0.9, 0.5]] * 3),
        'proactiveness': torch.tensor([[0.6, 0.7, 0.8]] * 3),
        'resolution': torch.tensor([[0.8, 0.9, 0.7, 0.6, 0.8]] * 3),
        'hold': torch.tensor([[0.5, 0.6]] * 3),
        'closing': torch.tensor([[0.4]] * 3)
    }
    
    results = mock_qa_model.batch_evaluate(transcripts)
    
    assert isinstance(results, list)
    assert len(results) == len(transcripts)

def test_is_ready(mock_qa_model):
    """Test model readiness check"""
    assert mock_qa_model.is_ready() is True
    
    mock_qa_model.loaded = False
    assert mock_qa_model.is_ready() is False

def test_get_model_info(mock_qa_model):
    """Test getting model information"""
    info = mock_qa_model.get_model_info()
    
    assert isinstance(info, dict)
    assert "loaded" in info
    assert "model_path" in info
    assert "qa_metrics" in info

def test_preprocess_transcript(mock_qa_model):
    """Test transcript preprocessing"""
    raw_transcript = "  Hello,   world!  \n  How are you?  "
    processed = mock_qa_model._preprocess_transcript(raw_transcript)
    
    assert isinstance(processed, str)
    assert processed.strip() == processed  # No leading/trailing whitespace
    assert "\n" not in processed  # Newlines removed

def test_extract_features(mock_qa_model):
    """Test feature extraction from transcript"""
    transcript = "Thank you for calling. Please hold while I check."
    
    features = mock_qa_model._extract_features(transcript)
    
    assert isinstance(features, dict)
    # Should extract various linguistic features
    assert "word_count" in features or "politeness_indicators" in features

def test_validate_scores(mock_qa_model):
    """Test score validation"""
    valid_scores = {"opening": 0.8, "listening": 0.7}
    invalid_scores = {"opening": 1.5, "listening": -0.2}
    
    validated_valid = mock_qa_model._validate_scores(valid_scores)
    validated_invalid = mock_qa_model._validate_scores(invalid_scores)
    
    # Valid scores should pass through unchanged
    assert validated_valid == valid_scores
    
    # Invalid scores should be clamped to [0, 1]
    assert 0 <= validated_invalid["opening"] <= 1
    assert 0 <= validated_invalid["listening"] <= 1

def test_estimate_evaluation_time(mock_qa_model):
    """Test evaluation time estimation"""
    transcript = "This is a sample transcript for testing."
    estimated_time = mock_qa_model.estimate_evaluation_time(transcript)
    
    assert isinstance(estimated_time, float)
    assert estimated_time > 0