#!/usr/bin/env python3
"""
Evaluate baseline Whisper model performance on test dataset
Run this BEFORE training to establish baseline metrics
"""

import os
import argparse
import torch
from pathlib import Path
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
)
from datasets import load_dataset, Audio
import evaluate
from tqdm import tqdm
import json
import logging
from src.config_manager import ConfigManager
from src.mlflow_utils import MLflowManager
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaselineEvaluator:
    """Evaluate baseline (untrained) Whisper model performance"""

    def __init__(self, config_path: str, num_samples: int = None, batch_size: int = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.num_samples = num_samples
        self.batch_size = batch_size or 16  # Default to 16 for faster evaluation

        # Setup device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        logger.info(f"Batch size: {self.batch_size}")
        
    def load_model_and_processor(self):
        """Load baseline Whisper model"""
        model_config = self.config['model']

        logger.info(f"Loading baseline model: {model_config['name']}")

        self.processor = WhisperProcessor.from_pretrained(
            model_config['name'],
            language=model_config['language'],
            task=model_config['task']
        )

        # Use fp16 only if enabled in config and CUDA is available
        use_fp16 = self.config['training'].get('fp16', False) and torch.cuda.is_available()
        self.dtype = torch.float16 if use_fp16 else torch.float32

        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_config['name'],
            dtype=self.dtype,
        ).to(self.device)

        self.model.generation_config.language = model_config['language']
        self.model.generation_config.task = model_config['task']

        self.model.eval()
        logger.info(f"Model loaded successfully (dtype: {self.dtype})")
        
    def load_test_dataset(self):
        """Load test split of dataset"""
        dataset_config = self.config['dataset']

        # Determine number of samples
        if self.num_samples:
            num_samples = self.num_samples
        else:
            num_samples = dataset_config.get('test_samples')

        logger.info(f"Loading test dataset in streaming mode")

        # Use streaming mode to avoid cache issues
        dataset = load_dataset(
            dataset_config['name'],
            dataset_config['language'],
            split="validation",
            streaming=True,
            trust_remote_code=True
        )

        # Remove unnecessary columns
        columns_to_remove = [
            "accent", "age", "client_id", "down_votes",
            "gender", "locale", "segment", "up_votes", "variant", "path"
        ]
        dataset = dataset.remove_columns(
            [col for col in columns_to_remove if col in dataset.column_names]
        )

        # Cast to 16kHz
        dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))

        # Take only the required number of samples
        if num_samples:
            dataset = dataset.take(num_samples)
            logger.info(f"Taking {num_samples} test samples")

        return dataset

    def _process_batch(self, batch_audios, batch_sentences, predictions, references):
        """Process a batch of audio samples"""
        # Process batch of audios
        inputs = self.processor(
            batch_audios,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        )

        # Move to device and convert to same dtype as model
        inputs = {k: v.to(self.device).to(self.dtype) for k, v in inputs.items()}

        # Generate predictions
        with torch.no_grad():
            predicted_ids = self.model.generate(
                inputs["input_features"],
                language=self.config['model']['language'],
                task=self.config['model']['task'],
                max_length=225
            )

        # Decode predictions
        transcriptions = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True
        )

        predictions.extend(transcriptions)
        references.extend(batch_sentences)

    def evaluate(self, save_predictions: bool = True):
        """Run evaluation on test set"""

        # Load model and data
        self.load_model_and_processor()
        dataset = self.load_test_dataset()

        # Initialize metrics
        wer_metric = evaluate.load("wer")

        predictions = []
        references = []

        logger.info("Starting evaluation...")

        # Collect samples into batches
        batch_audios = []
        batch_sentences = []

        for sample in tqdm(dataset, desc="Evaluating"):
            batch_audios.append(sample["audio"]["array"])
            batch_sentences.append(sample["sentence"])

            # Process when batch is full
            if len(batch_audios) >= self.batch_size:
                self._process_batch(batch_audios, batch_sentences, predictions, references)
                batch_audios = []
                batch_sentences = []

        # Process remaining samples
        if batch_audios:
            self._process_batch(batch_audios, batch_sentences, predictions, references)
        
        # Compute metrics
        wer = 100 * wer_metric.compute(
            predictions=predictions,
            references=references
        )

        # Create results
        results = {
            "model": self.config['model']['name'],
            "language": self.config['model']['language'],
            "dataset": self.config['dataset']['name'],
            "num_samples": len(predictions),
            "wer": round(wer, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"\n{'='*50}")
        logger.info(f"BASELINE EVALUATION RESULTS")
        logger.info(f"{'='*50}")
        logger.info(f"Model: {results['model']}")
        logger.info(f"Language: {results['language']}")
        logger.info(f"Test samples: {results['num_samples']}")
        logger.info(f"Baseline WER: {results['wer']}%")
        logger.info(f"{'='*50}\n")
        
        # Save results
        output_dir = Path("./evaluation_results")
        output_dir.mkdir(exist_ok=True)
        
        results_file = output_dir / f"baseline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to: {results_file}")
        
        # Save predictions if requested
        if save_predictions:
            predictions_file = output_dir / f"baseline_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(predictions_file, 'w') as f:
                json.dump({
                    "predictions": predictions[:100],  # Save first 100 for review
                    "references": references[:100]
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Sample predictions saved to: {predictions_file}")
        
        # Log to MLflow if enabled
        if self.config['logging']['use_mlflow']:
            self.log_to_mlflow(results)
        
        return results
    
    def log_to_mlflow(self, results):
        """Log baseline results to MLflow"""
        mlflow_manager = MLflowManager(self.config)
        mlflow_manager.setup_tracking()
        
        # Start a baseline run
        run = mlflow_manager.start_run(run_name=f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Log metrics
        import mlflow
        mlflow.log_metric("baseline_wer", results['wer'])
        mlflow.log_param("evaluation_type", "baseline")
        mlflow.log_param("num_test_samples", results['num_samples'])
        
        mlflow_manager.end_run()
        logger.info("Baseline results logged to MLflow")


def main():
    parser = argparse.ArgumentParser(description='Evaluate baseline Whisper performance')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to config file')
    parser.add_argument('--num-samples', type=int, default=None,
                        help='Number of test samples to evaluate (default: all)')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Batch size for evaluation (default: 16)')
    parser.add_argument('--save-predictions', action='store_true',
                        help='Save sample predictions')
    args = parser.parse_args()

    evaluator = BaselineEvaluator(args.config, args.num_samples, args.batch_size)
    results = evaluator.evaluate(save_predictions=args.save_predictions)

    return results


if __name__ == "__main__":
    main()