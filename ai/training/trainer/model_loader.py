import torch
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Union
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    WhisperFeatureExtractor,
    WhisperTokenizer
)

logger = logging.getLogger('training')

class ModelLoader:
    """
    Handles loading and configuration of Whisper model components
    """
    def __init__(self, config):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_model(self):
        """
        Load and configure Whisper model
        """
        model_name = self.config.get('model_name', 'openai/whisper-small')
        logger.info(f"Loading model: {model_name}")
        
        # Load model
        model = WhisperForConditionalGeneration.from_pretrained(model_name).to(self.device)
        
        # Configure generation settings
        language = self.config.get('language', 'Swahili')
        task = self.config.get('task', 'transcribe')
        
        model.generation_config.language = language.lower()
        model.generation_config.task = task
        model.generation_config.forced_decoder_ids = None
        
        return model
    
    def load_processor(self):
        """
        Load feature extractor, tokenizer and processor
        """
        model_name = self.config.get('model_name', 'openai/whisper-small')
        language = self.config.get('language', 'Swahili')
        task = self.config.get('task', 'transcribe')
        
        logger.info(f"Loading processors for {model_name}")
        
        # Load feature extractor
        feature_extractor = WhisperFeatureExtractor.from_pretrained(model_name)
        
        # Load tokenizer
        tokenizer = WhisperTokenizer.from_pretrained(
            model_name,
            language=language,
            task=task
        )
        
        # Load processor
        processor = WhisperProcessor.from_pretrained(
            model_name,
            language=language,
            task=task
        )
        
        return feature_extractor, tokenizer, processor
    
    def create_data_collator(self, processor, model):
        """
        Create a data collator for the Whisper model
        """
        @dataclass
        class DataCollatorSpeechSeq2SeqWithPadding:
            processor: Any
            decoder_start_token_id: int
        
            def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
                # Extract features
                input_features = [{"input_features": feature["input_features"]} for feature in features]
                batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
                
                # Process labels
                label_features = [{"input_ids": feature["labels"]} for feature in features]
                labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
                
                # Replace padding with -100 to ignore these values during loss calculation
                labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
                
                # If first token is decoder_start_token_id, remove it
                if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
                    labels = labels[:, 1:]
                
                batch["labels"] = labels
                return batch
        
        return DataCollatorSpeechSeq2SeqWithPadding(
            processor=processor,
            decoder_start_token_id=model.config.decoder_start_token_id
        )