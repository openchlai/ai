#!/usr/bin/env python3
"""
Production-ready Whisper Fine-tuning Pipeline
Follows MLOps best practices with proper error handling and resource management.
"""

import os
import json
import logging
import argparse
import sys
import time
import pandas as pd
import numpy as np
import torch
import gc
from pathlib import Path
import soundfile as sf
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import warnings

# ML/DL imports
from transformers import (
    WhisperProcessor, 
    WhisperForConditionalGeneration
)

# Handle different transformers versions for imports
try:
    from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
except ImportError:
    try:
        from transformers.training_args_seq2seq import Seq2SeqTrainingArguments
        from transformers.trainer_seq2seq import Seq2SeqTrainer
    except ImportError:
        # For newer versions, these are in different locations
        from transformers import TrainingArguments as Seq2SeqTrainingArguments
        from transformers import Trainer as Seq2SeqTrainer

# Import callbacks separately with fallbacks
try:
    from transformers import TrainerCallback, EarlyStoppingCallback
except ImportError:
    try:
        from transformers.trainer_callback import TrainerCallback, EarlyStoppingCallback
    except ImportError:
        # Minimal fallback implementations
        class TrainerCallback:
            def on_train_begin(self, args, state, control, **kwargs): pass
            def on_log(self, args, state, control, logs=None, **kwargs): pass
            def on_evaluate(self, args, state, control, metrics=None, **kwargs): pass
            def on_train_end(self, args, state, control, **kwargs): pass
        
        class EarlyStoppingCallback(TrainerCallback):
            def __init__(self, early_stopping_patience=1, early_stopping_threshold=0.0):
                self.early_stopping_patience = early_stopping_patience
                self.early_stopping_threshold = early_stopping_threshold
from datasets import Dataset, DatasetDict
import evaluate

# MLflow imports
import mlflow
import mlflow.pytorch

# Add flush=True to all print statements for immediate output
def progress_print(message, level="INFO"):
    """Print with immediate flush for real-time progress"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", flush=True)
    logger.info(message)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('training_progress.log')
    ]
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


class WhisperTrainingConfig:
    """Configuration class for Whisper training pipeline - fully config-driven"""
    
    # Define required parameters with no defaults
    REQUIRED_PARAMS = {
        # Data paths
        'labelstudio_export_path': str,
        'audio_base_path': str,
        
        # Model configuration
        'model_name': str,
        'target_language': str,
        'task': str,
        
        # Training configuration
        'learning_rate': float,
        'per_device_train_batch_size': int,
        'per_device_eval_batch_size': int,
        'gradient_accumulation_steps': int,
        'max_steps': int,
        'warmup_steps': int,
        'eval_steps': int,
        'save_steps': int,
        'logging_steps': int,
        
        # Memory optimization
        'fp16': bool,
        'bf16': bool,
        'gradient_checkpointing': bool,
        'dataloader_pin_memory': bool,
        'dataloader_num_workers': int,
        
        # Evaluation
        'test_size': float,
        'max_eval_samples': int,
        
        # MLflow
        'mlflow_tracking_uri': str,
        'mlflow_experiment_name': str,
        
        # Output
        'output_dir': str,
        'registered_model_name': str,
    }
    
    # Optional parameters with validation
    OPTIONAL_PARAMS = {
        'gradient_checkpointing_kwargs': dict,
        'max_grad_norm': float,
        'optim': str,
        'num_train_epochs': int,  # Alternative to max_steps
        'early_stopping_patience': int,
        'early_stopping_threshold': float,
        'generation_max_length': int,
        'target_sample_rate': int,
        'max_audio_duration': float,
        'min_audio_duration': float,
        'max_transcription_length': int,
        'min_transcription_length': int,
    }
    
    def __init__(self, config_path: str):
        """Initialize configuration from JSON file - no defaults allowed for required params"""
        if not config_path:
            raise ValueError("Config path is required")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Load configuration
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        # Validate and set required parameters
        self._validate_and_set_required_params(config_dict)
        
        # Set optional parameters with validation
        self._validate_and_set_optional_params(config_dict)
        
        # Validate configuration consistency
        self._validate_configuration()
        
        logger.info(f"Configuration loaded successfully from {config_path}")
        self._log_configuration_summary()
    
    def _validate_and_set_required_params(self, config_dict: dict):
        """Validate and set all required parameters"""
        missing_params = []
        
        for param_name, param_type in self.REQUIRED_PARAMS.items():
            if param_name not in config_dict:
                missing_params.append(param_name)
            else:
                value = config_dict[param_name]
                
                # Type validation
                if not isinstance(value, param_type):
                    raise TypeError(f"Parameter '{param_name}' must be of type {param_type.__name__}, got {type(value).__name__}")
                
                setattr(self, param_name, value)
        
        if missing_params:
            raise ValueError(f"Missing required configuration parameters: {missing_params}")
    
    def _validate_and_set_optional_params(self, config_dict: dict):
        """Validate and set optional parameters"""
        # Set defaults for optional parameters
        optional_defaults = {
            'gradient_checkpointing_kwargs': {"use_reentrant": False},
            'max_grad_norm': 1.0,
            'optim': "adamw_torch",
            'num_train_epochs': None,  # Use max_steps by default
            'early_stopping_patience': 3,
            'early_stopping_threshold': 0.01,
            'generation_max_length': 225,
            'target_sample_rate': 16000,
            'max_audio_duration': 60.0,
            'min_audio_duration': 0.1,
            'max_transcription_length': 1000,
            'min_transcription_length': 3,
        }
        
        for param_name, default_value in optional_defaults.items():
            if param_name in config_dict:
                value = config_dict[param_name]
                expected_type = self.OPTIONAL_PARAMS[param_name]
                
                # Type validation for optional params
                if not isinstance(value, expected_type):
                    raise TypeError(f"Optional parameter '{param_name}' must be of type {expected_type.__name__}, got {type(value).__name__}")
                
                setattr(self, param_name, value)
            else:
                setattr(self, param_name, default_value)
    
    def _validate_configuration(self):
        """Validate configuration consistency and constraints"""
        errors = []
        
        # Validate ranges and constraints
        if not (0 < self.learning_rate < 1):
            errors.append(f"learning_rate must be between 0 and 1, got {self.learning_rate}")
        
        if not (0 < self.test_size < 1):
            errors.append(f"test_size must be between 0 and 1, got {self.test_size}")
        
        if self.per_device_train_batch_size <= 0:
            errors.append(f"per_device_train_batch_size must be positive, got {self.per_device_train_batch_size}")
        
        if self.gradient_accumulation_steps <= 0:
            errors.append(f"gradient_accumulation_steps must be positive, got {self.gradient_accumulation_steps}")
        
        if self.max_steps <= 0 and (not hasattr(self, 'num_train_epochs') or self.num_train_epochs is None):
            errors.append("Either max_steps must be positive or num_train_epochs must be specified")
        
        if self.warmup_steps < 0:
            errors.append(f"warmup_steps must be non-negative, got {self.warmup_steps}")
        
        # Validate task and language
        valid_tasks = ["transcribe", "translate"]
        if self.task not in valid_tasks:
            errors.append(f"task must be one of {valid_tasks}, got '{self.task}'")
        
        # Validate model name format
        if "/" not in self.model_name:
            errors.append(f"model_name should be in format 'organization/model', got '{self.model_name}'")
        
        # Validate paths exist
        if not os.path.exists(self.labelstudio_export_path):
            errors.append(f"labelstudio_export_path does not exist: {self.labelstudio_export_path}")
        
        if not os.path.exists(self.audio_base_path):
            errors.append(f"audio_base_path does not exist: {self.audio_base_path}")
        
        # Validate MLflow URI format
        if not self.mlflow_tracking_uri.startswith(("http://", "https://", "file://", "sqlite:///")):
            errors.append(f"mlflow_tracking_uri must be a valid URI, got '{self.mlflow_tracking_uri}'")
        
        # Validate precision settings
        if self.fp16 and self.bf16:
            errors.append("Cannot enable both fp16 and bf16 simultaneously")
        
        # Validate audio duration constraints
        if self.min_audio_duration >= self.max_audio_duration:
            errors.append(f"min_audio_duration ({self.min_audio_duration}) must be less than max_audio_duration ({self.max_audio_duration})")
        
        # Validate transcription length constraints
        if self.min_transcription_length >= self.max_transcription_length:
            errors.append(f"min_transcription_length ({self.min_transcription_length}) must be less than max_transcription_length ({self.max_transcription_length})")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors))
    
    def _log_configuration_summary(self):
        """Log a summary of the configuration"""
        logger.info("Configuration Summary:")
        logger.info(f"  Model: {self.model_name}")
        logger.info(f"  Language: {self.target_language} | Task: {self.task}")
        logger.info(f"  Training: {self.max_steps} steps, LR: {self.learning_rate}")
        logger.info(f"  Batch: {self.per_device_train_batch_size} x {self.gradient_accumulation_steps} accumulation")
        logger.info(f"  Precision: FP16={self.fp16}, BF16={self.bf16}")
        logger.info(f"  Data: {self.labelstudio_export_path}")
        logger.info(f"  Output: {self.output_dir}")
        logger.info(f"  MLflow: {self.mlflow_tracking_uri} | Experiment: {self.mlflow_experiment_name}")
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary for MLflow logging"""
        config_dict = {}
        
        # Add all required parameters
        for param_name in self.REQUIRED_PARAMS.keys():
            config_dict[param_name] = getattr(self, param_name)
        
        # Add all optional parameters that were set
        for param_name in self.OPTIONAL_PARAMS.keys():
            if hasattr(self, param_name):
                config_dict[param_name] = getattr(self, param_name)
        
        return config_dict
    
    def get_effective_batch_size(self) -> int:
        """Calculate effective batch size"""
        return self.per_device_train_batch_size * self.gradient_accumulation_steps
    
    def validate_data_paths(self):
        """Validate that all data paths are accessible"""
        # Check Label Studio export
        if not os.path.exists(self.labelstudio_export_path):
            raise FileNotFoundError(f"Label Studio export not found: {self.labelstudio_export_path}")
        
        # Check audio base path
        if not os.path.exists(self.audio_base_path):
            raise FileNotFoundError(f"Audio base path not found: {self.audio_base_path}")
        
        # Check if audio directory exists within base path
        audio_dir = os.path.join(self.audio_base_path, 'audio')
        if not os.path.exists(audio_dir):
            logger.warning(f"Audio subdirectory not found: {audio_dir}")
            # Don't raise error here as audio files might be in base path directly
        
        return True

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    """Fixed data collator with proper attention mask handling"""
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        # Split inputs and labels
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # Get tokenized label sequences
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # Create proper attention mask for labels
        labels = labels_batch["input_ids"]
        attention_mask = labels_batch.get("attention_mask")
        
        if attention_mask is not None:
            # Use the attention mask from tokenizer and replace padding with -100
            labels = labels.masked_fill(attention_mask.ne(1), -100)
        else:
            # Fallback: create attention mask manually
            pad_token_id = self.processor.tokenizer.pad_token_id
            if pad_token_id is None:
                pad_token_id = self.processor.tokenizer.eos_token_id
            labels = labels.masked_fill(labels == pad_token_id, -100)

        # Handle decoder start token
        if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]
            if attention_mask is not None:
                attention_mask = attention_mask[:, 1:]

        batch["labels"] = labels
        
        # Add attention mask to batch
        if attention_mask is not None:
            batch["decoder_attention_mask"] = attention_mask
            
        return batch


class MLflowIntegrationCallback(TrainerCallback):
    """Enhanced MLflow integration with proper error handling"""
    
    def __init__(self, config: WhisperTrainingConfig, baseline_wer: Optional[float] = None):
        self.config = config
        self.baseline_wer = baseline_wer
        self.run_id = None
        self.logged_params = set()
    
    def on_train_begin(self, args, state, control, **kwargs):
        """Initialize MLflow run"""
        try:
            # End any existing runs
            if mlflow.active_run():
                logger.info("Ending existing MLflow run to start a new one")
                mlflow.end_run()
            
            # Start new run
            run = mlflow.start_run(run_name=f"whisper-training-{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}")
            self.run_id = run.info.run_id
            
            # Log configuration parameters (avoid conflicts)
            config_params = self.config.to_dict()
            for key, value in config_params.items():
                try:
                    if key not in self.logged_params:
                        mlflow.log_param(key, value)
                        self.logged_params.add(key)
                except Exception as e:
                    logger.warning(f"Failed to log param {key}: {e}")
            

            
            # Log training arguments
            training_params = {
                "effective_batch_size": args.per_device_train_batch_size * args.gradient_accumulation_steps,
                "total_train_batch_size": args.per_device_train_batch_size * args.gradient_accumulation_steps * max(1, args.world_size),
                "num_train_epochs": args.num_train_epochs,
                "max_steps": args.max_steps,
            }
            # Only log parameters that haven't been logged yet
            for key, value in training_params.items():
                try:
                    if key not in self.logged_params:
                        mlflow.log_param(key, value)
                        self.logged_params.add(key)
                except Exception as e:
                    logger.warning(f"Failed to log training param {key}: {e}")
            
            if self.baseline_wer is not None:
                mlflow.log_metric("baseline_wer", self.baseline_wer * 100)
            
            logger.info(f"MLflow run started: {self.run_id}")
            
        except Exception as e:
            logger.error(f"Failed to start MLflow run: {e}")
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        """Log training metrics"""
        if logs and mlflow.active_run():
            try:
                step = state.global_step
                for key, value in logs.items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        mlflow.log_metric(key, value, step=step)
                
                # Log epoch
                mlflow.log_metric("epoch", state.epoch, step=step)
                
            except Exception as e:
                logger.warning(f"Failed to log metrics: {e}")
    
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        """Log evaluation metrics"""
        if metrics and mlflow.active_run():
            try:
                step = state.global_step
                for key, value in metrics.items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        mlflow.log_metric(key, value, step=step)
                        
                logger.info(f"Evaluation at step {step}: {metrics}")
                
            except Exception as e:
                logger.warning(f"Failed to log evaluation metrics: {e}")
    
    def on_train_end(self, args, state, control, **kwargs):
        """Finalize MLflow run"""
        logger.info("Training completed. MLflow run ready for model registration.")


class WhisperDataLoader:
    """Handles data loading and preprocessing - fully config-driven"""
    
    def __init__(self, config: WhisperTrainingConfig):
        self.config = config
        
    def load_labelstudio_export(self) -> List[Dict]:
        """Load and validate Label Studio export"""
        logger.info(f"Loading Label Studio export from {self.config.labelstudio_export_path}")
        
        processed_data = []
        with open(self.config.labelstudio_export_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    item = json.loads(line.strip())
                    
                    audio_path = item.get('audio_filepath')
                    transcription = item.get('text')
                    duration = item.get('duration')
                    
                    if audio_path and transcription:
                        transcription = transcription.strip()
                        
                        # Use config values instead of hardcoded values
                        if (self.config.min_transcription_length <= len(transcription) <= self.config.max_transcription_length):
                            processed_data.append({
                                'audio_path': audio_path,
                                'transcription': transcription,
                                'duration': duration
                            })
                            
                except (json.JSONDecodeError, Exception) as e:
                    logger.warning(f"Skipping line {line_num}: {e}")
                    continue
        
        logger.info(f"Loaded {len(processed_data)} valid samples")
        return processed_data
    
    def load_and_validate_audio(self, audio_path: str) -> Tuple[Optional[np.ndarray], Optional[int], str]:
        """Load and validate audio file using config parameters"""
        try:
            if not os.path.isabs(audio_path):
                audio_path = os.path.join(self.config.audio_base_path, audio_path)
            
            if not os.path.exists(audio_path):
                return None, None, f"File not found: {audio_path}"
            
            if os.path.getsize(audio_path) == 0:
                return None, None, f"Empty file: {audio_path}"
            
            audio, sr = sf.read(audio_path)
            
            # Convert to mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Use config target sample rate instead of hardcoded 16000
            if sr != self.config.target_sample_rate:
                return None, None, f"Unexpected sample rate {sr}Hz (expected {self.config.target_sample_rate}Hz)"
            
            if audio is None or len(audio) == 0:
                return None, None, f"Empty audio data"
            
            duration = len(audio) / sr
            # Use config duration constraints instead of hardcoded values
            if duration < self.config.min_audio_duration or duration > self.config.max_audio_duration:
                return None, None, f"Duration {duration:.2f}s outside range [{self.config.min_audio_duration}, {self.config.max_audio_duration}]"
            
            return audio, sr, "OK"
            
        except Exception as e:
            return None, None, f"Error loading {audio_path}: {str(e)}"
    
    def process_audio_samples(self, labelstudio_data: List[Dict]) -> List[Dict]:
        """Process and filter audio samples"""
        logger.info("Processing audio samples...")
        
        processed_samples = []
        failed_count = 0
        
        for i, sample in enumerate(labelstudio_data):
            audio, sr, status = self.load_and_validate_audio(sample['audio_path'])
            
            if audio is not None:
                processed_samples.append({
                    'audio': audio,
                    'transcription': sample['transcription'],
                    'audio_path': sample['audio_path'],
                    'duration': len(audio) / sr
                })
            else:
                failed_count += 1
                if i < 5:  # Log first few failures
                    logger.warning(f"Failed to load {sample['audio_path']}: {status}")
            
            if (i + 1) % 50 == 0:
                logger.info(f"Processed {i + 1}/{len(labelstudio_data)} samples, {len(processed_samples)} valid")
        
        logger.info(f"Final dataset: {len(processed_samples)} valid samples, {failed_count} failed")
        
        if processed_samples:
            durations = [s['duration'] for s in processed_samples]
            logger.info(f"Audio stats - Mean: {np.mean(durations):.2f}s, "
                       f"Min: {np.min(durations):.2f}s, Max: {np.max(durations):.2f}s, "
                       f"Total: {np.sum(durations)/60:.1f} minutes")
        
        return processed_samples


class WhisperTrainingPipeline:
    """Main training pipeline - fully config-driven"""
    
    def __init__(self, config: WhisperTrainingConfig):
        self.config = config
        self.processor = None
        self.model = None
        self.trainer = None
        self.wer_metric = evaluate.load("wer")
        
        # Validate configuration and data paths
        self.config.validate_data_paths()
        
        # Setup MLflow
        self._setup_mlflow()
        
        # Clear GPU memory
        self._clear_gpu_memory()
    
    def _setup_mlflow(self):
        """Setup MLflow tracking"""
        mlflow.set_tracking_uri(self.config.mlflow_tracking_uri)
        try:
            mlflow.set_experiment(self.config.mlflow_experiment_name)
            logger.info(f"MLflow experiment set: {self.config.mlflow_experiment_name}")
        except Exception as e:
            logger.warning(f"MLflow setup issue: {e}")
    
    def _clear_gpu_memory(self):
        """Clear GPU memory and clean up"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        logger.info("GPU memory cleared")
    
    def load_model_and_processor(self):
        """Load Whisper model and processor using config model_name"""
        logger.info(f"Loading model: {self.config.model_name}")
        
        try:
            # Load processor with explicit pad token configuration
            progress_print("🔄 Loading Whisper processor...")
            self.processor = WhisperProcessor.from_pretrained(self.config.model_name)
            
            # Fix tokenizer pad token issue
            if self.processor.tokenizer.pad_token is None:
                self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
                progress_print("🔧 Set pad_token = eos_token for tokenizer")
            
            # Load model
            progress_print("🔄 Loading Whisper model weights...")
            
            # Load model with appropriate dtype
            model_kwargs = {}
            if torch.cuda.is_available():
                # Use config precision settings instead of hardcoded
                if self.config.fp16:
                    model_kwargs['torch_dtype'] = torch.float16
                elif self.config.bf16:
                    model_kwargs['torch_dtype'] = torch.bfloat16
                else:
                    model_kwargs['torch_dtype'] = torch.float32
            
            self.model = WhisperForConditionalGeneration.from_pretrained(
                self.config.model_name,  # Use config model name
                **model_kwargs
            )
            
            # Configure model for training
            self.model.config.forced_decoder_ids = None
            self.model.config.suppress_tokens = []
            self.model.config.use_cache = False
            
            # Move to GPU
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(device)
            
            logger.info(f"Model {self.config.model_name} loaded successfully on {device}")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.config.model_name}: {e}")
            raise
    
    def prepare_dataset(self, samples: List[Dict]) -> DatasetDict:
        """Convert samples to HuggingFace dataset format using config parameters"""
        logger.info("Preparing dataset...")
        
        def process_sample(sample):
            # Process audio to log-mel spectrogram using config sample rate
            input_features = self.processor.feature_extractor(
                sample['audio'], 
                sampling_rate=self.config.target_sample_rate,  # Use config value
                return_tensors="pt"
            ).input_features[0]
            
            # Tokenize transcription using config max length
            labels = self.processor.tokenizer(
                sample['transcription'], 
                return_tensors="pt", 
                padding=True, 
                truncation=True,
                max_length=self.config.generation_max_length * 2  # Use config-based length
            ).input_ids[0]
            
            return {
                "input_features": input_features,
                "labels": labels
            }
        
        # Process all samples
        processed = []
        for sample in samples:
            try:
                processed_sample = process_sample(sample)
                processed.append(processed_sample)
            except Exception as e:
                logger.warning(f"Failed to process sample: {e}")
                continue
        
        if not processed:
            raise ValueError("No samples could be processed successfully")
        
        # Create dataset
        dataset = Dataset.from_list(processed)
        
        # Train/test split
        dataset = dataset.train_test_split(test_size=self.config.test_size, seed=42)
        
        logger.info(f"Dataset prepared - Train: {len(dataset['train'])}, Val: {len(dataset['test'])}")
        return dataset
    
    def compute_metrics(self, eval_pred):
        """Compute WER metric during training"""
        pred_ids = eval_pred.predictions
        label_ids = eval_pred.label_ids

        # Handle nested predictions (common in Seq2Seq models)
        if isinstance(pred_ids, tuple):
            pred_ids = pred_ids[0]  # Take the first element if it's a tuple
        
        # Ensure pred_ids is 2D (batch_size, sequence_length)
        if len(pred_ids.shape) > 2:
            pred_ids = pred_ids.reshape(-1, pred_ids.shape[-1])
        
        # Replace -100 with pad token id in labels
        label_ids[label_ids == -100] = self.processor.tokenizer.pad_token_id

        try:
            # Decode predictions and labels with error handling
            pred_str = []
            label_str = []
            
            for i in range(len(pred_ids)):
                try:
                    # Handle individual prediction
                    pred_tokens = pred_ids[i]
                    if isinstance(pred_tokens, list):
                        pred_tokens = pred_tokens[0] if len(pred_tokens) > 0 and isinstance(pred_tokens[0], list) else pred_tokens
                    
                    # Ensure pred_tokens is a 1D array/list of integers
                    if hasattr(pred_tokens, 'flatten'):
                        pred_tokens = pred_tokens.flatten()
                    
                    # Convert to list and filter out non-integer values
                    pred_tokens = [int(token) for token in pred_tokens if isinstance(token, (int, float)) and not isinstance(token, bool)]
                    
                    # Decode
                    pred_text = self.processor.tokenizer.decode(pred_tokens, skip_special_tokens=True)
                    pred_str.append(pred_text)
                    
                except Exception as e:
                    logger.warning(f"Failed to decode prediction {i}: {e}")
                    pred_str.append("")  # Empty string as fallback
                
                try:
                    # Handle labels
                    label_tokens = label_ids[i]
                    label_text = self.processor.tokenizer.decode(label_tokens, skip_special_tokens=True)
                    label_str.append(label_text)
                    
                except Exception as e:
                    logger.warning(f"Failed to decode label {i}: {e}")
                    label_str.append("")  # Empty string as fallback

            # Compute WER with error handling
            if pred_str and label_str:
                wer = self.wer_metric.compute(predictions=pred_str, references=label_str)
            else:
                logger.warning("No valid predictions/labels for WER computation")
                wer = 1.0  # Return high WER if computation fails

        except Exception as e:
            logger.warning(f"WER computation failed: {e}")
            wer = 1.0  # Return high WER if computation fails

        return {"wer": wer}
    def evaluate_baseline(self, test_samples: List[Dict]) -> Optional[float]:
        """Evaluate baseline model performance using config parameters"""
        logger.info("Evaluating baseline model...")
        
        # Use config max_eval_samples instead of hardcoded value
        max_samples = min(len(test_samples), self.config.max_eval_samples)
        
        predictions = []
        references = []
        
        self.model.eval()
        device = next(self.model.parameters()).device
        
        with torch.no_grad():
            for i, sample in enumerate(test_samples[:max_samples]):
                try:
                    # Process audio using config sample rate
                    input_features = self.processor(
                        sample['audio'], 
                        sampling_rate=self.config.target_sample_rate,  # Use config value
                        return_tensors="pt"
                    ).input_features.to(device)
                    
                    # Generate transcription with config parameters
                    try:
                        generation_kwargs = {
                            "max_length": self.config.generation_max_length,
                            "num_beams": 1,
                            "do_sample": False,
                            "language": self.config.target_language,  # Use these instead
                            "task": self.config.task                  # of forced_decoder_ids
                        }
                    except Exception:
                        generation_kwargs = None
                    
                    predicted_ids = self.model.generate(
                        input_features,
                        **generation_kwargs
                    )[0]
                    
                    prediction = self.processor.decode(predicted_ids, skip_special_tokens=True)
                    
                    predictions.append(prediction)
                    references.append(sample['transcription'])
                    
                except Exception as e:
                    logger.warning(f"Baseline evaluation failed for sample {i}: {e}")
                    continue
        
        if predictions:
            try:
                baseline_wer = self.wer_metric.compute(predictions=predictions, references=references)
                logger.info(f"Baseline WER: {baseline_wer:.4f}")
                
                # Log sample predictions (limit based on config)
                sample_count = min(3, len(predictions))
                for i in range(sample_count):
                    logger.info(f"Sample {i+1}:")
                    logger.info(f"  Reference: {references[i][:100]}...")
                    logger.info(f"  Prediction: {predictions[i][:100]}...")
                
                return baseline_wer
            except Exception as e:
                logger.warning(f"WER computation failed: {e}")
                return None
        else:
            logger.warning("No successful baseline predictions")
            return None
    
    def setup_trainer(self, dataset: DatasetDict, baseline_wer: Optional[float] = None):
        """Setup the Seq2SeqTrainer using all config parameters"""
        logger.info("Setting up trainer...")
        
        # Data collator
        data_collator = DataCollatorSpeechSeq2SeqWithPadding(
            processor=self.processor,
            decoder_start_token_id=self.model.config.decoder_start_token_id,
        )
        
        # Training arguments - ALL from config
        training_args_dict = {
            "output_dir": self.config.output_dir,
            
            # Batch configuration from config
            "per_device_train_batch_size": self.config.per_device_train_batch_size,
            "per_device_eval_batch_size": self.config.per_device_eval_batch_size,
            "gradient_accumulation_steps": self.config.gradient_accumulation_steps,
            
            # Training configuration from config
            "learning_rate": self.config.learning_rate,
            "warmup_steps": self.config.warmup_steps,
            "max_steps": self.config.max_steps,
            
            # Memory optimization from config
            "gradient_checkpointing": self.config.gradient_checkpointing,
            "fp16": self.config.fp16,
            "bf16": self.config.bf16,
            
            # Evaluation from config
            "eval_strategy": "steps",
            "eval_steps": self.config.eval_steps,
            "generation_max_length": self.config.generation_max_length,
            
            # Saving and logging from config
            "save_steps": self.config.save_steps,
            "logging_steps": self.config.logging_steps,
            "save_total_limit": 3,
            "load_best_model_at_end": True,
            "metric_for_best_model": "wer",
            "greater_is_better": False,
            
            # Disable automatic MLflow reporting
            "report_to": [],
            
            # Memory optimization from config
            "dataloader_pin_memory": self.config.dataloader_pin_memory,
            "dataloader_num_workers": self.config.dataloader_num_workers,
            
            "remove_unused_columns": False,
            
            # Additional settings from config
            "max_grad_norm": self.config.max_grad_norm,
            "optim": self.config.optim,
        }
        
        # Add num_train_epochs if specified in config (alternative to max_steps)
        if hasattr(self.config, 'num_train_epochs') and self.config.num_train_epochs is not None:
            training_args_dict["num_train_epochs"] = self.config.num_train_epochs
            del training_args_dict["max_steps"]  # Remove max_steps if using epochs
        
        training_args = Seq2SeqTrainingArguments(**training_args_dict)
        
        # Add gradient checkpointing kwargs from config if supported
        if hasattr(self.config, 'gradient_checkpointing_kwargs') and hasattr(training_args, 'gradient_checkpointing_kwargs'):
            training_args.gradient_checkpointing_kwargs = self.config.gradient_checkpointing_kwargs
        
        # Auto-detect precision if not explicitly set
        if torch.cuda.is_available() and not (self.config.fp16 or self.config.bf16):
            if torch.cuda.get_device_capability()[0] >= 8:
                training_args.bf16 = True
                logger.info("Auto-enabled BF16 precision (Ampere GPU detected)")
            else:
                logger.info("Using FP32 precision (older GPU detected)")
        
        # Initialize trainer
        trainer_kwargs = {
            "model": self.model,
            "args": training_args,
            "train_dataset": dataset["train"],
            "eval_dataset": dataset["test"],
            "data_collator": data_collator,
            "compute_metrics": self.compute_metrics,
        }
        
        # Add processing_class/tokenizer with version compatibility
        try:
            trainer_kwargs["processing_class"] = self.processor
        except Exception:
            try:
                trainer_kwargs["tokenizer"] = self.processor.tokenizer
            except Exception:
                pass
        
        self.trainer = Seq2SeqTrainer(**trainer_kwargs)
        
        # Add callbacks
        mlflow_callback = MLflowIntegrationCallback(self.config, baseline_wer)
        self.trainer.add_callback(mlflow_callback)
        
        # Add early stopping using config parameters
        try:
            early_stopping = EarlyStoppingCallback(
                early_stopping_patience=self.config.early_stopping_patience,
                early_stopping_threshold=self.config.early_stopping_threshold
            )
            self.trainer.add_callback(early_stopping)
            logger.info(f"Early stopping enabled: patience={self.config.early_stopping_patience}, threshold={self.config.early_stopping_threshold}")
        except Exception:
            logger.info("Early stopping callback not available in this version")
        
        logger.info("Trainer setup complete")
    
    def train(self):
        """Execute training with proper error handling"""
        logger.info("Starting training...")
        
        try:
            # Clear memory before training
            self._clear_gpu_memory()
            
            # Train
            train_result = self.trainer.train()
            
            logger.info("Training completed successfully")
            return train_result
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
        finally:
            # Clean up
            self._clear_gpu_memory()

    def evaluate_and_save_model(self) -> Dict:
        """Enhanced model saving with proper accelerator unwrapping"""
        progress_print("📊 Starting final evaluation...")
        
        try:
            # Evaluate
            eval_results = self.trainer.evaluate()
            final_wer = eval_results.get('eval_wer', None)
            
            progress_print(f"📊 Final evaluation results: {eval_results}")
            
            # Save model locally first
            progress_print("💾 Saving model locally...")
            self.trainer.save_model()
            progress_print(f"✅ Model saved locally to {self.config.output_dir}")
            
            # Save processor
            self.processor.save_pretrained(self.config.output_dir)
            progress_print("✅ Processor saved locally")
            
            # MLflow logging with proper accelerator handling
            if mlflow.active_run():
                try:
                    # Log final metrics
                    progress_print("📊 Logging final metrics to MLflow...")
                    for key, value in eval_results.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(f"final_{key}", value)
                    
                    # Properly unwrap model for MLflow
                    progress_print("🔄 Attempting MLflow model upload...")
                    model_logged = False
                    
                    # Method 1: Proper accelerator unwrapping
                    try:
                        # Get the base model without accelerator wrapper
                        if hasattr(self.trainer, 'accelerator') and hasattr(self.trainer.accelerator, 'unwrap_model'):
                            model_to_save = self.trainer.accelerator.unwrap_model(self.trainer.model)
                            progress_print("🔧 Model unwrapped from accelerator")
                        else:
                            # Fallback: try to get the base model
                            model_to_save = getattr(self.trainer.model, 'module', self.trainer.model)
                            progress_print("🔧 Using base model")
                        
                        # Ensure model is in eval mode and on CPU for serialization
                        model_to_save.eval()
                        if torch.cuda.is_available():
                            model_to_save = model_to_save.cpu()
                            progress_print("📱 Model moved to CPU for serialization")
                        
                        # Log with updated MLflow API
                        mlflow.pytorch.log_model(
                            pytorch_model=model_to_save,
                            artifact_path="model",
                            registered_model_name=self.config.registered_model_name,
                            await_registration_for=300,
                            pip_requirements=[
                                "torch>=2.0.0",
                                "transformers>=4.30.0", 
                                "datasets>=2.0.0",
                                "soundfile>=0.12.0"
                            ]
                        )
                        progress_print("✅ Model uploaded to MLflow successfully (Method 1)")
                        model_logged = True
                        
                    except Exception as e:
                        progress_print(f"⚠️  Method 1 failed: {e}", "WARNING")
                    
                    # Method 2: Artifact upload fallback (your current working method)
                    if not model_logged:
                        try:
                            progress_print("🔄 Using artifact upload method...")
                            mlflow.log_artifacts(self.config.output_dir, artifact_path="model")
                            
                            # Add comprehensive model info
                            model_info = {
                                "model_name": self.config.model_name,
                                "model_path": self.config.output_dir,
                                "final_wer": final_wer,
                                "model_type": "whisper_finetuned",
                                "training_completed": True,
                                "early_stopped": True,
                                "loading_instructions": f"Use: WhisperForConditionalGeneration.from_pretrained('{self.config.output_dir}')",
                                "processor_instructions": f"Use: WhisperProcessor.from_pretrained('{self.config.output_dir}')"
                            }
                            
                            mlflow.log_dict(model_info, "model_info.json")
                            progress_print("✅ Model files uploaded as artifacts (Method 2)")
                            model_logged = True
                            
                        except Exception as e2:
                            progress_print(f"⚠️  Method 2 also failed: {e2}", "WARNING")
                    
                    if model_logged:
                        progress_print("📈 MLflow logging completed successfully")
                    else:
                        progress_print("⚠️  MLflow upload failed, but model saved locally", "WARNING")
                    
                except Exception as e:
                    progress_print(f"⚠️  MLflow logging failed: {e}", "WARNING")
                    progress_print("💡 Model is still saved locally and can be used")
            
            return eval_results
            
        except Exception as e:
            progress_print(f"❌ Final evaluation failed: {e}", "ERROR")
            raise
        finally:
            try:
                if mlflow.active_run():
                    mlflow.end_run()
            except:
                pass

    def run_complete_pipeline(self):
        """Run the complete training pipeline"""
        logger.info("Starting complete Whisper training pipeline...")
        
        try:
            # 1. Load data
            data_loader = WhisperDataLoader(self.config)
            labelstudio_data = data_loader.load_labelstudio_export()
            processed_samples = data_loader.process_audio_samples(labelstudio_data)
            
            if len(processed_samples) == 0:
                raise ValueError("No valid audio samples found")
            
            # 2. Load model
            self.load_model_and_processor()
            
            # 3. Prepare dataset
            dataset = self.prepare_dataset(processed_samples)
            
            # 4. Evaluate baseline
            baseline_wer = self.evaluate_baseline(processed_samples[-20:])
            
            # 5. Setup trainer
            self.setup_trainer(dataset, baseline_wer)
            
            # 6. Train
            train_result = self.train()
            
            # 7. Final evaluation
            eval_results = self.evaluate_and_save_model()
            
            # 8. Summary
            logger.info("="*60)
            logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("="*60)
            if baseline_wer:
                logger.info(f"Baseline WER: {baseline_wer*100:.2f}%")
            if 'eval_wer' in eval_results:
                final_wer = eval_results['eval_wer']
                logger.info(f"Final WER: {final_wer:.2f}%")
                if baseline_wer:
                    improvement = ((baseline_wer*100 - final_wer) / (baseline_wer*100)) * 100
                    logger.info(f"Improvement: {improvement:.2f}%")
            
            logger.info(f"Model saved to: {self.config.output_dir}")
            logger.info(f"MLflow tracking: {self.config.mlflow_tracking_uri}")
            
            return {
                'train_result': train_result,
                'eval_results': eval_results,
                'baseline_wer': baseline_wer
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        finally:
            self._clear_gpu_memory()


def main():
    """Main entry point - enforces config-only usage for robust experimentation"""
    parser = argparse.ArgumentParser(
        description="Whisper Fine-tuning Pipeline - Configuration-Driven",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration-Only Mode:
This pipeline requires ALL parameters to be specified in a JSON configuration file.
Command-line overrides are no longer supported to ensure reproducible experiments.

Example usage:
    python whisper_training_pipeline.py --config config/training_config.json
    
Configuration file must contain all required parameters. See training_config.json template.
        """
    )
    
    # Only accept config file - no individual parameter overrides
    parser.add_argument(
        "--config", 
        type=str, 
        required=True,
        help="Path to configuration JSON file (required)"
    )
    
    parser.add_argument(
        "--validate-only", 
        action="store_true",
        help="Only validate configuration without running training"
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Perform dry run: validate config, load data, but skip training"
    )
    
    args = parser.parse_args()
    
    # Validate config file exists
    if not args.config:
        logger.error("Configuration file is required. Use --config path/to/config.json")
        sys.exit(1)
    
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    try:
        # Load configuration (will validate all required parameters)
        logger.info(f"Loading configuration from: {args.config}")
        config = WhisperTrainingConfig(args.config)
        
        # If validation-only mode, exit after successful config validation
        if args.validate_only:
            logger.info("✅ Configuration validation successful!")
            logger.info("All required parameters are present and valid.")
            return {"status": "validation_passed", "config": config.to_dict()}
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        logger.info(f"Output directory: {config.output_dir}")
        
        # Initialize pipeline
        pipeline = WhisperTrainingPipeline(config)
        
        # If dry-run mode, validate data loading but don't train
        if args.dry_run:
            logger.info("🔄 Performing dry run...")
            
            # Load and validate data
            data_loader = WhisperDataLoader(config)
            labelstudio_data = data_loader.load_labelstudio_export()
            processed_samples = data_loader.process_audio_samples(labelstudio_data)
            
            if len(processed_samples) == 0:
                logger.error("❌ No valid audio samples found in dry run")
                sys.exit(1)
            
            # Load model
            pipeline.load_model_and_processor()
            
            # Prepare dataset
            dataset = pipeline.prepare_dataset(processed_samples)
            
            logger.info("✅ Dry run successful!")
            logger.info(f"Found {len(processed_samples)} valid samples")
            logger.info(f"Dataset split - Train: {len(dataset['train'])}, Val: {len(dataset['test'])}")
            logger.info("Configuration and data pipeline are ready for training.")
            
            return {
                "status": "dry_run_passed", 
                "samples_found": len(processed_samples),
                "train_samples": len(dataset['train']),
                "val_samples": len(dataset['test'])
            }
        
        # Run full training pipeline
        logger.info("🚀 Starting full training pipeline...")
        results = pipeline.run_complete_pipeline()
        
        logger.info("✅ Training pipeline completed successfully!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        
        # Log configuration details for debugging
        if 'config' in locals():
            logger.error("Configuration summary:")
            logger.error(f"  Model: {config.model_name}")
            logger.error(f"  Data: {config.labelstudio_export_path}")
            logger.error(f"  Output: {config.output_dir}")
        
        raise


def validate_config_file(config_path: str) -> bool:
    """Standalone function to validate configuration file"""
    try:
        config = WhisperTrainingConfig(config_path)
        logger.info("✅ Configuration file is valid")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False


def create_sample_config(output_path: str = "sample_training_config.json"):
    """Create a sample configuration file with all required parameters"""
    sample_config = {
        # Required parameters
        "labelstudio_export_path": "label-studio-export/data-v1/manifest.jsonl",
        "audio_base_path": "label-studio-export/data-v1",
        "model_name": "openai/whisper-small",
        "target_language": "sw",
        "task": "transcribe",
        "learning_rate": 1e-5,
        "per_device_train_batch_size": 2,
        "per_device_eval_batch_size": 2,
        "gradient_accumulation_steps": 2,
        "max_steps": 1000,
        "warmup_steps": 500,
        "eval_steps": 100,
        "save_steps": 100,
        "logging_steps": 25,
        "fp16": False,
        "bf16": True,
        "gradient_checkpointing": True,
        "dataloader_pin_memory": False,
        "dataloader_num_workers": 0,
        "test_size": 0.2,
        "max_eval_samples": 10,
        "mlflow_tracking_uri": "http://localhost:5000",
        "mlflow_experiment_name": "whisper-production-training",
        "output_dir": "./whisper-finetuned-production",
        "registered_model_name": "whisper-finetuned-swahili",
        
        # Optional parameters with defaults
        "gradient_checkpointing_kwargs": {"use_reentrant": False},
        "max_grad_norm": 1.0,
        "optim": "adamw_torch",
        "early_stopping_patience": 3,
        "early_stopping_threshold": 0.01,
        "generation_max_length": 225,
        "target_sample_rate": 16000,
        "min_audio_duration": 0.1,
        "max_audio_duration": 60.0,
        "min_transcription_length": 3,
        "max_transcription_length": 1000
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)
    
    logger.info(f"Sample configuration created: {output_path}")
    return output_path


if __name__ == "__main__":
    # Add option to create sample config
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample-config":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "sample_training_config.json"
        create_sample_config(output_file)
        sys.exit(0)
    
    # Add option to validate config only
    if len(sys.argv) > 2 and sys.argv[1] == "--validate-config":
        config_file = sys.argv[2]
        is_valid = validate_config_file(config_file)
        sys.exit(0 if is_valid else 1)
    
    # Run the main training pipeline
    try:
        main()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)
# if __name__ == "__main__":
#     main()