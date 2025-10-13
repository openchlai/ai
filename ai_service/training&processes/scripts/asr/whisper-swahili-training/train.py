import os
import argparse
import torch
import sys
from pathlib import Path
from itertools import islice
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)
from datasets import load_dataset, Audio
import datasets
import evaluate
from src.config_manager import ConfigManager
from src.mlflow_utils import MLflowManager
from src.enhanced_callbacks import (
    SafetyCallback,
    ProgressMonitorCallback,
    CheckpointManagerCallback,
    MetricsLoggerCallback,
    EarlyStoppingCallback,
    TensorBoardVerificationCallback,
    MLflowCallback
)
import logging
import shutil

# Set tokenizers parallelism before any tokenizer usage
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhisperTrainer:
    def __init__(self, config_path: str, resume_from_checkpoint: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.mlflow_manager = MLflowManager(self.config)
        self.resume_from_checkpoint = resume_from_checkpoint
        
        # Setup MLflow if enabled
        if self.config['logging']['use_mlflow']:
            try:
                self.mlflow_manager.setup_tracking()
            except Exception as e:
                logger.warning(f"MLflow setup failed: {e}. Continuing without MLflow.")
                self.config['logging']['use_mlflow'] = False
    
    def find_latest_checkpoint(self):
        """Find the latest checkpoint in output directory"""
        output_dir = Path(self.config['training']['output_dir'])
        
        if not output_dir.exists():
            return None
        
        # Find all checkpoint directories
        checkpoints = list(output_dir.glob('checkpoint-*'))
        
        if not checkpoints:
            return None
        
        # Sort by step number
        checkpoints.sort(key=lambda x: int(x.name.split('-')[1]))
        
        latest = checkpoints[-1]
        logger.info(f"Found latest checkpoint: {latest}")
        return str(latest)
    
    def prepare_dataset(self):
        """Load and prepare Common Voice dataset - with streaming support"""
        dataset_config = self.config['dataset']
        
        # Check if we should use streaming
        use_streaming = (dataset_config.get('train_samples') or 
                        dataset_config.get('test_samples'))
        
        if use_streaming:
            logger.info("Using streaming mode for dataset loading (optimized for limited storage)")
            return self.prepare_dataset_streaming()
        else:
            logger.info("Using regular dataset loading")
            return self.prepare_dataset_regular()
    
    def prepare_dataset_regular(self):
        """Regular dataset loading - downloads full dataset"""
        dataset_config = self.config['dataset']
        
        # Determine splits
        train_split = "train"
        test_split = "validation"
        
        logger.info(f"Loading full dataset splits: {train_split}, {test_split}")
        
        try:
            # Load dataset
            dataset = load_dataset(
                dataset_config['name'],
                dataset_config['language'],
                split={'train': train_split, 'test': test_split},
                trust_remote_code=True
            )
            
            # Remove unnecessary columns
            columns_to_remove = [
                "accent", "age", "client_id", "down_votes", 
                "gender", "locale", "segment", "up_votes", "variant", "path"
            ]
            dataset = dataset.remove_columns(
                [col for col in columns_to_remove if col in dataset['train'].column_names]
            )
            
            # Cast to 16kHz
            dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
            
            logger.info(f"Dataset loaded - Train: {len(dataset['train'])}, Test: {len(dataset['test'])}")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    def prepare_dataset_streaming(self):
        """Streaming dataset loading - memory efficient for limited samples"""
        from itertools import islice
        import datasets
        
        dataset_config = self.config['dataset']
        language_code = dataset_config.get('language', 'sw')
        
        train_samples = dataset_config.get('train_samples')
        test_samples = dataset_config.get('test_samples')

        logger.info("Loading dataset in streaming mode (on-demand loading)")

        try:
            # Load streaming datasets directly
            logger.info("Loading train split in streaming mode...")
            train_dataset = load_dataset(
                dataset_config['name'],
                language_code,
                split='train',
                streaming=True,
                trust_remote_code=True
            )

            logger.info("Loading validation split in streaming mode...")
            test_dataset = load_dataset(
                dataset_config['name'],
                language_code,
                split='validation',
                streaming=True,
                trust_remote_code=True
            )

            # Remove unnecessary columns
            columns_to_remove = [
                "accent", "age", "client_id", "down_votes",
                "gender", "locale", "segment", "up_votes", "variant", "path"
            ]

            # Get actual column names from first sample
            first_sample = next(iter(train_dataset))
            available_columns = list(first_sample.keys())
            columns_to_remove = [col for col in columns_to_remove if col in available_columns]

            if columns_to_remove:
                train_dataset = train_dataset.remove_columns(columns_to_remove)
                test_dataset = test_dataset.remove_columns(columns_to_remove)
                logger.info(f"Removed columns: {columns_to_remove}")

            # Cast audio to 16kHz
            train_dataset = train_dataset.cast_column("audio", Audio(sampling_rate=16000))
            test_dataset = test_dataset.cast_column("audio", Audio(sampling_rate=16000))

            # Apply sample limits if specified
            if train_samples:
                train_dataset = train_dataset.take(train_samples)
                logger.info(f"Limited training to {train_samples} samples")
            else:
                logger.info("Using full training set (~44k samples) in streaming mode")

            if test_samples:
                test_dataset = test_dataset.take(test_samples)
                logger.info(f"Limited validation to {test_samples} samples")
            else:
                logger.info("Using full validation set (~12k samples) in streaming mode")

            # Create dataset dict
            dataset = datasets.DatasetDict({
                'train': train_dataset,
                'test': test_dataset
            })

            logger.info("Streaming dataset ready")
            
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load dataset in streaming mode: {e}")
            raise
    
    def setup_model(self):
        """Initialize Whisper model and processors"""
        model_config = self.config['model']
        
        try:
            # Load processors
            self.processor = WhisperProcessor.from_pretrained(
                model_config['name'],
                language=model_config['language'],
                task=model_config['task']
            )
            
            # Load model
            logger.info(f"Loading model: {model_config['name']}")
            # Always load in float32, let Trainer handle FP16 mixed precision
            model = WhisperForConditionalGeneration.from_pretrained(
                model_config['name'],
                low_cpu_mem_usage=True,
                use_cache=False
            )
            
            # Configure for language
            model.generation_config.language = model_config['language']
            model.generation_config.task = model_config['task']
            model.generation_config.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                language=model_config['language'],
                task=model_config['task']
            )
            
            if self.config['training']['gradient_checkpointing']:
                model.config.use_cache = False
                # Use non-reentrant checkpointing to avoid the backward graph error
                model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            
            # Apply LoRA if configured
            if model_config.get('use_peft', False):
                model = self._apply_peft(model, model_config['peft_config'])
            
            logger.info("Model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _apply_peft(self, model, peft_config):
        """Apply PEFT/LoRA to model"""
        from peft import LoraConfig, get_peft_model, TaskType
        
        lora_config = LoraConfig(
            r=peft_config['r'],
            lora_alpha=peft_config['lora_alpha'],
            target_modules=peft_config['target_modules'],
            lora_dropout=peft_config['lora_dropout'],
            bias="none",
            task_type=TaskType.SEQ_2_SEQ_LM,
        )
        
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        return model
    
    def train(self):
        """Main training function with error recovery"""
        
        try:
            # Start MLflow run
            if self.config['logging']['use_mlflow']:
                self.mlflow_manager.start_run()
            
            # Prepare dataset
            dataset = self.prepare_dataset()
            
            # Setup model
            model = self.setup_model()
            
            # Prepare dataset for training
            def prepare_dataset(batch):
                audio = batch["audio"]
                batch["input_features"] = self.processor.feature_extractor(
                    audio["array"], 
                    sampling_rate=audio["sampling_rate"]
                ).input_features[0]
                batch["labels"] = self.processor.tokenizer(batch["sentence"]).input_ids
                return batch
            
            logger.info("Processing dataset...")

            # Check if using streaming datasets
            from datasets import IterableDataset
            is_streaming = isinstance(dataset['train'], IterableDataset)

            if is_streaming:
                # For streaming datasets, map each split individually
                logger.info("Using streaming dataset - processing on-the-fly")
                columns_to_remove = ['audio', 'sentence']

                train_dataset = dataset['train'].map(
                    prepare_dataset,
                    remove_columns=columns_to_remove
                )
                eval_dataset = dataset['test'].map(
                    prepare_dataset,
                    remove_columns=columns_to_remove
                )
            else:
                # For regular datasets, use multiprocessing
                logger.info("Using regular dataset with multiprocessing")
                dataset = dataset.map(
                    prepare_dataset,
                    remove_columns=dataset.column_names["train"],
                    num_proc=self.config['dataset']['num_workers']
                )
                train_dataset = dataset['train']
                eval_dataset = dataset['test']
            
            # Data collator
            from dataclasses import dataclass
            from typing import Any, Dict, List, Union

            @dataclass
            class DataCollatorSpeechSeq2SeqWithPadding:
                processor: Any

                def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
                    input_features = [{"input_features": feature["input_features"]} for feature in features]
                    batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

                    label_features = [{"input_ids": feature["labels"]} for feature in features]
                    
                    import warnings
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message=".*fast tokenizer.*")
                        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

                    labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

                    if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
                        labels = labels[:, 1:]

                    batch["labels"] = labels
                    return batch

            data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=self.processor)
            
            # Setup training arguments
            training_config = self.config['training']
            
            # Setup reporting
            report_to = []
            if self.config['logging']['use_tensorboard']:
                report_to.append("tensorboard")
                os.makedirs(self.config['logging']['tensorboard_dir'], exist_ok=True)
            if self.config['logging']['use_wandb']:
                report_to.append("wandb")
            
            # Determine checkpoint to resume from
            checkpoint = None
            if self.resume_from_checkpoint:
                if self.resume_from_checkpoint == "latest":
                    checkpoint = self.find_latest_checkpoint()
                else:
                    checkpoint = self.resume_from_checkpoint
                
                if checkpoint:
                    logger.info(f"Resuming training from: {checkpoint}")
                else:
                    logger.warning("No checkpoint found, starting from scratch")
            
            training_args = Seq2SeqTrainingArguments(
                output_dir=training_config['output_dir'],
                per_device_train_batch_size=training_config['per_device_train_batch_size'],
                per_device_eval_batch_size=training_config['per_device_eval_batch_size'],
                gradient_accumulation_steps=training_config['gradient_accumulation_steps'],
                learning_rate=training_config['learning_rate'],
                warmup_steps=training_config['warmup_steps'],
                max_steps=training_config['max_steps'],
                gradient_checkpointing=training_config['gradient_checkpointing'],
                gradient_checkpointing_kwargs={"use_reentrant": False},  # Fix for backward graph bug
                fp16=training_config['fp16'],
                eval_strategy=training_config['evaluation_strategy'],
                eval_steps=training_config['eval_steps'],
                save_steps=training_config['save_steps'],
                logging_steps=training_config['logging_steps'],
                logging_dir=self.config['logging']['tensorboard_dir'],
                load_best_model_at_end=training_config['load_best_model_at_end'],
                metric_for_best_model=training_config['metric_for_best_model'],
                greater_is_better=training_config['greater_is_better'],
                push_to_hub=training_config['push_to_hub'],
                hub_model_id=training_config.get('hub_model_id'),
                hub_token=os.environ.get('HF_TOKEN'),
                report_to=report_to,
                save_total_limit=training_config.get('save_total_limit', 3),
                optim=training_config.get('optim', 'adamw_torch'),
                predict_with_generate=True,
                generation_max_length=225,
                dataloader_num_workers=training_config['dataloader_num_workers'],
                # Recovery options
                save_safetensors=True,
                ignore_data_skip=False,  # Important for resuming
                # Reduce checkpoint size - don't save optimizer/scheduler state
                save_only_model=True,  # Only save model weights, not optimizer state (saves ~11GB per checkpoint)
            )
            
            # Metrics
            wer_metric = evaluate.load("wer")
            
            def compute_metrics(pred):
                pred_ids = pred.predictions
                label_ids = pred.label_ids
                
                label_ids[label_ids == -100] = self.processor.tokenizer.pad_token_id
                
                pred_str = self.processor.tokenizer.batch_decode(
                    pred_ids, skip_special_tokens=True
                )
                label_str = self.processor.tokenizer.batch_decode(
                    label_ids, skip_special_tokens=True
                )
                
                wer = 100 * wer_metric.compute(
                    predictions=pred_str, 
                    references=label_str
                )
                return {"wer": wer}
            
            # Setup callbacks
            callbacks = [
                SafetyCallback(max_nan_count=3),
                ProgressMonitorCallback(),
                CheckpointManagerCallback(max_checkpoints=3),
                MetricsLoggerCallback(),
                TensorBoardVerificationCallback(),
            ]
            
            # Add early stopping if configured
            if training_config.get('early_stopping_patience'):
                callbacks.append(
                    EarlyStoppingCallback(
                        patience=training_config['early_stopping_patience']
                    )
                )
            
            # Add MLflow callback
            if self.config['logging']['use_mlflow']:
                callbacks.append(MLflowCallback(self.mlflow_manager))
            
            # Initialize trainer
            trainer = Seq2SeqTrainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                processing_class=self.processor.feature_extractor,
                callbacks=callbacks,
            )
            
            # Train
            logger.info("="*60)
            logger.info("STARTING TRAINING")
            logger.info("="*60)
            logger.info(f"Output directory: {training_config['output_dir']}")
            logger.info(f"Max steps: {training_config['max_steps']}")
            logger.info(f"Batch size: {training_config['per_device_train_batch_size']}")
            logger.info(f"Gradient accumulation: {training_config['gradient_accumulation_steps']}")
            logger.info(f"Effective batch size: {training_config['per_device_train_batch_size'] * training_config['gradient_accumulation_steps']}")
            logger.info(f"Learning rate: {training_config['learning_rate']}")
            logger.info("="*60)
            
            train_result = trainer.train(resume_from_checkpoint=checkpoint)
            
            # Save final model
            logger.info("Saving final model...")
            trainer.save_model()
            self.processor.save_pretrained(training_config['output_dir'])
            
            # Log training metrics
            logger.info("="*60)
            logger.info("TRAINING COMPLETED")
            logger.info("="*60)
            logger.info(f"Training loss: {train_result.training_loss:.4f}")
            logger.info(f"Training steps: {train_result.global_step}")
            logger.info("="*60)
            
            # Final evaluation
            logger.info("Running final evaluation...")
            eval_results = trainer.evaluate()
            
            logger.info("="*60)
            logger.info("FINAL EVALUATION RESULTS")
            logger.info("="*60)
            for key, value in eval_results.items():
                if isinstance(value, float):
                    logger.info(f"{key}: {value:.4f}")
            logger.info("="*60)
            
            # Log to MLflow
            if self.config['logging']['use_mlflow']:
                self.mlflow_manager.log_model(model, self.processor)
                
                # Log TensorBoard files
                if self.config['logging']['use_tensorboard']:
                    tb_dir = self.config['logging']['tensorboard_dir']
                    self.mlflow_manager.log_artifacts(tb_dir, "tensorboard")
                
                self.mlflow_manager.end_run()
            
            # Upload TensorBoard to HuggingFace
            if (self.config['logging']['save_tensorboard_to_hf'] and 
                self.config['training']['push_to_hub']):
                self._upload_tensorboard_to_hf()
            
            logger.info("✅ Training pipeline completed successfully!")
            
            return train_result, eval_results
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️  Training interrupted by user")
            logger.info("Latest checkpoint saved. You can resume training with --resume latest")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"\n❌ Training failed with error: {e}")
            logger.exception("Full traceback:")
            
            # Try to save emergency checkpoint
            try:
                emergency_dir = Path(training_config['output_dir']) / "emergency_checkpoint"
                emergency_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Attempting to save emergency checkpoint to {emergency_dir}")
                
                if 'model' in locals():
                    model.save_pretrained(emergency_dir)
                if 'self' in locals() and hasattr(self, 'processor'):
                    self.processor.save_pretrained(emergency_dir)
                    
                logger.info("✓ Emergency checkpoint saved")
            except Exception as save_error:
                logger.error(f"Could not save emergency checkpoint: {save_error}")
            
            sys.exit(1)
    
    def _upload_tensorboard_to_hf(self):
        """Upload TensorBoard logs to HuggingFace"""
        from huggingface_hub import HfApi
        
        try:
            api = HfApi()
            tb_dir = self.config['logging']['tensorboard_dir']
            model_id = self.config['training']['hub_model_id']
            
            # Create tar file of tensorboard logs
            shutil.make_archive(
                "tensorboard_logs", 
                "tar", 
                tb_dir
            )
            
            # Upload to HF
            api.upload_file(
                path_or_fileobj="tensorboard_logs.tar",
                path_in_repo="tensorboard_logs.tar",
                repo_id=model_id,
                token=os.environ.get('HF_TOKEN')
            )
            
            logger.info(f"✓ TensorBoard logs uploaded to {model_id}")
        except Exception as e:
            logger.warning(f"Could not upload TensorBoard logs: {e}")


def main():
    parser = argparse.ArgumentParser(description='Train Whisper on Swahili')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to config file')
    parser.add_argument('--resume', type=str, default=None,
                        help='Resume from checkpoint (path or "latest")')
    parser.add_argument('--mlflow-uri', type=str,
                        help='Override MLflow tracking URI')
    args = parser.parse_args()
    
    # Override MLflow URI if provided
    if args.mlflow_uri:
        os.environ['MLFLOW_TRACKING_URI'] = args.mlflow_uri
    
    trainer = WhisperTrainer(args.config, resume_from_checkpoint=args.resume)
    trainer.train()


if __name__ == "__main__":
    main()