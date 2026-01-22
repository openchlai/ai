#!/usr/bin/env python3
"""
Pre-training validation script
Run this to verify your setup before starting training
"""

import os
import sys
import torch
import argparse
from pathlib import Path
from src.config_manager import ConfigManager
from datasets import load_dataset, Audio
import logging
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import mlflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PreTrainValidator:
    """Validate setup before training"""
    
    def __init__(self, config_path: str):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.errors = []
        self.warnings = []
        
    def validate_all(self) -> bool:
        """Run all validation checks"""
        logger.info("="*60)
        logger.info("PRE-TRAINING VALIDATION")
        logger.info("="*60)
        
        checks = [
            ("Environment", self.validate_environment),
            ("Config", self.validate_config),
            ("Dataset Access", self.validate_dataset_access),
            ("Model Access", self.validate_model_access),
            ("Output Directories", self.validate_output_dirs),
            ("MLflow Setup", self.validate_mlflow),
            ("HuggingFace Auth", self.validate_huggingface),
        ]
        
        for check_name, check_func in checks:
            logger.info(f"\n{'='*60}")
            logger.info(f"Checking: {check_name}")
            logger.info(f"{'='*60}")
            try:
                check_func()
                logger.info(f"✅ {check_name}: PASSED")
            except Exception as e:
                self.errors.append(f"{check_name}: {str(e)}")
                logger.error(f"❌ {check_name}: FAILED - {str(e)}")
        
        # Print summary
        self.print_summary()
        
        return len(self.errors) == 0
    
    def validate_environment(self):
        """Check CUDA, memory, disk space"""
        # Check CUDA
        if torch.cuda.is_available():
            logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"✓ CUDA version: {torch.version.cuda}")
            
            # Check memory
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"✓ GPU memory: {total_memory:.2f} GB")
            
            if total_memory < 16:
                self.warnings.append(f"GPU memory ({total_memory:.2f} GB) may be insufficient for large batch sizes")
        else:
            logger.warning("⚠️  CUDA not available - training will be slow on CPU")
            self.warnings.append("CUDA not available")
        
        # Check disk space
        import shutil
        output_dir = self.config['training']['output_dir']
        try:
            stat = shutil.disk_usage(output_dir)
            free_gb = stat.free / 1e9
            logger.info(f"✓ Free disk space: {free_gb:.2f} GB")
            
            if free_gb < 50:
                self.warnings.append(f"Low disk space ({free_gb:.2f} GB). Training may require 20-50 GB.")
        except:
            logger.warning("⚠️  Could not check disk space")
    
    def validate_config(self):
        """Validate configuration values"""
        # Check required keys
        required_sections = ['model', 'dataset', 'training', 'logging']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        logger.info(f"✓ All required config sections present")
        
        # Validate model config
        model_cfg = self.config['model']
        if not model_cfg.get('name'):
            raise ValueError("model.name not specified")
        logger.info(f"✓ Model: {model_cfg['name']}")
        logger.info(f"✓ Language: {model_cfg['language']}")
        logger.info(f"✓ Task: {model_cfg['task']}")
        
        # Validate training config
        training_cfg = self.config['training']
        
        # Check batch size and gradient accumulation
        batch_size = training_cfg['per_device_train_batch_size']
        grad_accum = training_cfg['gradient_accumulation_steps']
        effective_batch = batch_size * grad_accum
        
        logger.info(f"✓ Per-device batch size: {batch_size}")
        logger.info(f"✓ Gradient accumulation: {grad_accum}")
        logger.info(f"✓ Effective batch size: {effective_batch}")
        
        if effective_batch < 8:
            self.warnings.append(f"Effective batch size ({effective_batch}) is small. Consider increasing for better training.")
        
        # Check max_steps
        max_steps = training_cfg['max_steps']
        logger.info(f"✓ Max steps: {max_steps}")
        
        if max_steps < 500:
            self.warnings.append(f"max_steps ({max_steps}) is very low. May not converge properly.")
        
        # Check learning rate
        lr = training_cfg['learning_rate']
        logger.info(f"✓ Learning rate: {lr}")
        
        if lr > 1e-3:
            self.warnings.append(f"Learning rate ({lr}) seems high for fine-tuning")
        
        # Check FP16
        if training_cfg['fp16'] and not torch.cuda.is_available():
            raise ValueError("fp16 enabled but CUDA not available")
        
        logger.info(f"✓ FP16 training: {training_cfg['fp16']}")
        logger.info(f"✓ Gradient checkpointing: {training_cfg['gradient_checkpointing']}")
    
    def validate_dataset_access(self):
        """Test dataset loading"""
        dataset_cfg = self.config['dataset']

        logger.info(f"Testing dataset access: {dataset_cfg['name']}")
        logger.info(f"Language: {dataset_cfg['language']}")

        # Try loading in streaming mode to avoid downloading full dataset
        try:
            test_dataset = load_dataset(
                dataset_cfg['name'],
                dataset_cfg['language'],
                split='validation',
                streaming=True,
                trust_remote_code=True
            )
            logger.info(f"✓ Successfully accessed dataset in streaming mode")

            # Take one sample to check structure
            sample = next(iter(test_dataset))
            columns = list(sample.keys())
            logger.info(f"✓ Sample columns: {columns}")

            # Check for required columns
            if 'audio' not in columns:
                raise ValueError("'audio' column not found in dataset")
            if 'sentence' not in columns:
                raise ValueError("'sentence' column not found in dataset")

            # Try casting audio on the streaming dataset
            test_dataset = test_dataset.cast_column("audio", Audio(sampling_rate=16000))
            sample_with_audio = next(iter(test_dataset))
            logger.info(f"✓ Audio casting successful")

        except Exception as e:
            raise RuntimeError(f"Dataset loading failed: {str(e)}")
    
    def validate_model_access(self):
        """Test model loading"""
        model_cfg = self.config['model']
        
        logger.info(f"Testing model access: {model_cfg['name']}")
        
        try:
            # Try loading processor
            processor = WhisperProcessor.from_pretrained(
                model_cfg['name'],
                language=model_cfg['language'],
                task=model_cfg['task']
            )
            logger.info(f"✓ Processor loaded successfully")
            
            # Try loading model (on CPU to save memory)
            model = WhisperForConditionalGeneration.from_pretrained(
                model_cfg['name'],
                dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            logger.info(f"✓ Model loaded successfully")
            
            # Check model size
            num_params = sum(p.numel() for p in model.parameters())
            logger.info(f"✓ Model parameters: {num_params:,}")
            
            del model  # Free memory
            
        except Exception as e:
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def validate_output_dirs(self):
        """Check output directories"""
        training_cfg = self.config['training']
        logging_cfg = self.config['logging']
        
        # Create output directories
        output_dir = Path(training_cfg['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Output directory: {output_dir}")
        
        if logging_cfg['use_tensorboard']:
            tb_dir = Path(logging_cfg['tensorboard_dir'])
            tb_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ TensorBoard directory: {tb_dir}")
        
        # Check write permissions
        test_file = output_dir / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            logger.info(f"✓ Write permissions OK")
        except Exception as e:
            raise RuntimeError(f"Cannot write to output directory: {str(e)}")
    
    def validate_mlflow(self):
        """Check MLflow setup"""
        if not self.config['logging']['use_mlflow']:
            logger.info("⊘ MLflow disabled in config")
            return
        
        mlflow_cfg = self.config['mlflow']
        tracking_uri = mlflow_cfg.get('tracking_uri', 'http://localhost:5000')
        
        logger.info(f"Testing MLflow connection: {tracking_uri}")
        
        try:
            mlflow.set_tracking_uri(tracking_uri)
            
            # Try to get or create experiment
            experiment_name = mlflow_cfg.get('experiment_name', 'whisper-training')
            
            try:
                experiment = mlflow.create_experiment(experiment_name)
                logger.info(f"✓ Created MLflow experiment: {experiment_name}")
            except:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                logger.info(f"✓ Found existing MLflow experiment: {experiment_name}")
            
            # Test logging
            with mlflow.start_run(run_name="validation_test") as run:
                mlflow.log_param("test", "validation")
                mlflow.log_metric("test_metric", 1.0)
                logger.info(f"✓ MLflow logging test successful")
            
        except Exception as e:
            self.warnings.append(f"MLflow connection issue: {str(e)}. Training will continue without MLflow logging.")
            logger.warning(f"⚠️  MLflow issue: {str(e)}")
    
    def validate_huggingface(self):
        """Check HuggingFace authentication"""
        hf_token = os.environ.get('HF_TOKEN')
        
        if not hf_token:
            self.warnings.append("HF_TOKEN not set. Push to hub will fail.")
            logger.warning("⚠️  HF_TOKEN not set in environment")
            return
        
        logger.info(f"✓ HF_TOKEN found")
        
        # Check if push_to_hub is enabled
        if self.config['training']['push_to_hub']:
            hub_model_id = self.config['training'].get('hub_model_id')
            if not hub_model_id:
                self.warnings.append("push_to_hub enabled but hub_model_id not specified")
            else:
                logger.info(f"✓ Hub model ID: {hub_model_id}")
    
    def print_summary(self):
        """Print validation summary"""
        logger.info("\n" + "="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)
        
        if self.errors:
            logger.error(f"\n❌ FAILED: {len(self.errors)} error(s) found:")
            for error in self.errors:
                logger.error(f"  - {error}")
            logger.error("\nPlease fix these errors before training.")
        else:
            logger.info("\n✅ ALL CHECKS PASSED!")
        
        if self.warnings:
            logger.warning(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
            logger.warning("\nTraining can proceed, but review warnings.")
        
        logger.info("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Pre-training validation')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to config file')
    args = parser.parse_args()
    
    validator = PreTrainValidator(args.config)
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()  