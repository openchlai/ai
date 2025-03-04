import logging
from datasets import Audio, DatasetDict, load_dataset

logger = logging.getLogger(__name__)

class DatasetLoader:
    """
    Handles dataset loading and preprocessing for ASR
    """
    def __init__(self, config):
        self.config = config
    
    def load_dataset(self):
        """
        Load dataset based on configuration
        """
        dataset_name = self.config.get('dataset_name', 'mozilla-foundation/common_voice_11_0')
        language_code = self.config.get('language_code', 'sw')
        
        logger.info(f"Loading dataset: {dataset_name}, language: {language_code}")
        
        # Load dataset
        common_voice = DatasetDict()
        common_voice["train"] = load_dataset(
            dataset_name,
            language_code,
            split="train+validation", trust_remote_code=True
        )
        common_voice["test"] = load_dataset(
            dataset_name,
            language_code,
            split="test", trust_remote_code=True
        )
        
        # Remove unwanted columns
        remove_cols = self.config.get('remove_columns', [
            "accent", "age", "client_id", "down_votes", 
            "gender", "locale", "path", "segment", "up_votes"
        ])
        
        if remove_cols:
            common_voice = common_voice.remove_columns(remove_cols)
        
        # Resample to 16kHz
        logger.info("Resampling audio to 16kHz...")
        common_voice = common_voice.cast_column("audio", Audio(sampling_rate=16000))
        
        return common_voice
    
    def prepare_dataset(self, dataset, feature_extractor, tokenizer):
        """
        Preprocess dataset for training
        """
        logger.info("Preparing dataset for training...")
        
        def preprocess_function(batch):
            # Extract audio
            audio = batch["audio"]
            
            # Extract input features
            batch["input_features"] = feature_extractor(
                audio["array"], 
                sampling_rate=audio["sampling_rate"]
            ).input_features[0]
            
            # Generate labels
            batch["labels"] = tokenizer(batch["sentence"]).input_ids
            
            return batch
        
        # Apply preprocessing
        processed_dataset = dataset.map(
            preprocess_function,
            remove_columns=dataset.column_names["train"],
            num_proc=self.config.get('preprocessing_workers', 1)
        )
        
        return processed_dataset