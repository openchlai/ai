import os
import torch
import logging
import evaluate
from transformers import (
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments
)

from .dataset_loader import DatasetLoader
from .model_loader import ModelLoader
from .callbacks import ProgressCallback

logger = logging.getLogger(__name__)

class WhisperTrainer:
    """
    Trainer for Whisper ASR model fine-tuning
    """
    def __init__(self, session_id, config, backend_client):
        self.session_id = session_id
        self.config = config
        self.backend_client = backend_client
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize model and dataset components
        self.dataset_loader = DatasetLoader(config)
        self.model_loader = ModelLoader(config)
        
        # Create output directory
        self.output_dir = os.path.join("models", f"whisper-{session_id}")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def train(self):
        """
        Execute training process
        """
        logger.info(f"Starting Whisper training on {self.device}")
        
        # Load dataset
        logger.info("Loading dataset...")
        dataset = self.dataset_loader.load_dataset()
        
        # Load model components
        logger.info("Loading model and processors...")
        model = self.model_loader.load_model()
        feature_extractor, tokenizer, processor = self.model_loader.load_processor()
        
        # Prepare dataset
        logger.info("Preparing dataset...")
        processed_dataset = self.dataset_loader.prepare_dataset(
            dataset, feature_extractor, tokenizer
        )
        
        # Data collator
        logger.info("Setting up data collator...")
        data_collator = self.model_loader.create_data_collator(processor, model)
        
        # Load WER metric
        logger.info("Loading evaluation metric...")
        wer_metric = evaluate.load("wer")
        
        # Define compute_metrics function
        def compute_metrics(pred):
            pred_ids = pred.predictions
            label_ids = pred.label_ids
            
            # Replace -100 with pad token id
            label_ids[label_ids == -100] = tokenizer.pad_token_id
            
            # Decode predictions and references
            pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
            label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)
            
            # Compute WER
            wer = 100 * wer_metric.compute(predictions=pred_str, references=label_str)
            
            return {"wer": wer}
        
        # Training arguments
        logger.info("Setting up training arguments...")
        training_args = Seq2SeqTrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=self.config.get('batch_size', 16),
            gradient_accumulation_steps=self.config.get('gradient_accumulation_steps', 1),
            learning_rate=self.config.get('learning_rate', 1e-5),
            warmup_steps=self.config.get('warmup_steps', 500),
            max_steps=self.config.get('max_steps', 4000),
            gradient_checkpointing=True,
            fp16=torch.cuda.is_available(),
            evaluation_strategy="steps",
            per_device_eval_batch_size=self.config.get('eval_batch_size', 8),
            predict_with_generate=True,
            generation_max_length=225,
            save_steps=1000,
            eval_steps=1000,
            logging_steps=25,
            report_to=["tensorboard"],
            load_best_model_at_end=True,
            metric_for_best_model="wer",
            greater_is_better=False,
            push_to_hub=False,
        )
        
        # Custom callback
        progress_callback = ProgressCallback(
            session_id=self.session_id,
            backend_client=self.backend_client
        )
        
        # Initialize trainer
        logger.info("Initializing trainer...")
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=processed_dataset["train"],
            eval_dataset=processed_dataset["test"],
            data_collator=data_collator,
            compute_metrics=compute_metrics,
            tokenizer=processor.feature_extractor,
            callbacks=[progress_callback]
        )
        
        # Start training
        logger.info("Starting training...")
        trainer.train()
        
        # Save model and processor
        logger.info("Saving model and processor...")
        trainer.save_model()
        processor.save_pretrained(self.output_dir)
        
        # Final evaluation
        logger.info("Performing final evaluation...")
        metrics = trainer.evaluate()
        
        logger.info(f"Training completed successfully. Final WER: {metrics.get('eval_wer', 'N/A')}")
        
        return metrics