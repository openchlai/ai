#!/usr/bin/env python3
"""
Standalone evaluation script for fine-tuned Whisper models
Can evaluate both local models and HuggingFace Hub models
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
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperEvaluator:
    """Evaluate fine-tuned Whisper model"""
    
    def __init__(
        self,
        model_path: str,
        dataset_name: str,
        dataset_lang: str,
        language: str = "sw",
        task: str = "transcribe",
        device: str = None
    ):
        self.model_path = model_path
        self.dataset_name = dataset_name
        self.dataset_lang = dataset_lang
        self.language = language
        self.task = task
        
        # Setup device
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Using device: {self.device}")
        
    def load_model_and_processor(self):
        """Load model and processor"""
        logger.info(f"Loading model from: {self.model_path}")

        try:
            self.processor = WhisperProcessor.from_pretrained(
                self.model_path,
                language=self.language,
                task=self.task
            )

            # Use float32 for compatibility (fp16 can cause dtype mismatches)
            self.dtype = torch.float32
            self.model = WhisperForConditionalGeneration.from_pretrained(
                self.model_path,
                torch_dtype=self.dtype,
            ).to(self.device)

            self.model.generation_config.language = self.language
            self.model.generation_config.task = self.task

            self.model.eval()

            # Count parameters
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

            logger.info(f"✓ Model loaded successfully (dtype: {self.dtype})")
            logger.info(f"  Total parameters: {total_params:,}")
            logger.info(f"  Trainable parameters: {trainable_params:,}")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def load_test_dataset(self, split: str = "validation", num_samples: int = None):
        """Load test dataset using streaming to avoid cache issues"""

        logger.info(f"Loading dataset: {self.dataset_name}")
        logger.info(f"Split: {split}, Samples: {num_samples or 'all'}")

        try:
            # Use streaming mode to avoid corrupted cache issues
            dataset = load_dataset(
                self.dataset_name,
                self.dataset_lang,
                split=split,
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

            # Take limited samples if specified
            if num_samples:
                dataset = dataset.take(num_samples)
                logger.info(f"✓ Taking {num_samples} samples from {split} split")
            else:
                logger.info(f"✓ Loaded {split} split (streaming mode)")

            return dataset

        except Exception as e:
            raise RuntimeError(f"Failed to load dataset: {str(e)}")
    
    def evaluate(
        self,
        split: str = "validation",
        num_samples: int = None,
        batch_size: int = 8,
        save_predictions: bool = True,
        output_dir: str = "./evaluation_results"
    ) -> Dict:
        """Run evaluation"""
        
        # Load model and data
        self.load_model_and_processor()
        dataset = self.load_test_dataset(split, num_samples)
        
        # Initialize metrics
        wer_metric = evaluate.load("wer")
        
        predictions = []
        references = []
        sample_ids = []
        
        logger.info(f"Starting evaluation...")

        # Evaluate sample by sample for streaming compatibility
        for sample in tqdm(dataset, desc="Evaluating"):
            # Process audio
            audio_array = sample["audio"]["array"]
            inputs = self.processor(
                audio_array,
                sampling_rate=16000,
                return_tensors="pt"
            ).to(self.device)

            # Generate predictions
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    inputs.input_features,
                    language=self.language,
                    task=self.task,
                    max_length=225
                )

            # Decode predictions
            transcription = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]

            predictions.append(transcription)
            references.append(sample["sentence"])

            # Store ID if available
            if 'id' in sample:
                sample_ids.append(sample['id'])
        
        # Compute WER
        wer = 100 * wer_metric.compute(
            predictions=predictions,
            references=references
        )
        
        # Create detailed results
        results = {
            "model_path": self.model_path,
            "dataset": self.dataset_name,
            "language": self.language,
            "split": split,
            "num_samples": len(predictions),
            "wer": round(wer, 2),
            "timestamp": datetime.now().isoformat(),
            "device": str(self.device)
        }
        
        # Calculate per-sample WER for analysis
        per_sample_wers = []
        for pred, ref in zip(predictions, references):
            sample_wer = 100 * wer_metric.compute(predictions=[pred], references=[ref])
            per_sample_wers.append(sample_wer)
        
        results["wer_stats"] = {
            "mean": round(sum(per_sample_wers) / len(per_sample_wers), 2),
            "min": round(min(per_sample_wers), 2),
            "max": round(max(per_sample_wers), 2),
            "median": round(sorted(per_sample_wers)[len(per_sample_wers)//2], 2)
        }
        
        # Print results
        logger.info(f"\n{'='*60}")
        logger.info(f"EVALUATION RESULTS")
        logger.info(f"{'='*60}")
        logger.info(f"Model: {results['model_path']}")
        logger.info(f"Dataset: {results['dataset']}")
        logger.info(f"Samples: {results['num_samples']}")
        logger.info(f"WER: {results['wer']}%")
        logger.info(f"WER Stats:")
        logger.info(f"  Mean: {results['wer_stats']['mean']}%")
        logger.info(f"  Min: {results['wer_stats']['min']}%")
        logger.info(f"  Max: {results['wer_stats']['max']}%")
        logger.info(f"  Median: {results['wer_stats']['median']}%")
        logger.info(f"{'='*60}\n")
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = output_path / f"eval_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"✓ Results saved to: {results_file}")
        
        # Save predictions if requested
        if save_predictions:
            predictions_file = output_path / f"predictions_{timestamp}.json"
            
            # Save detailed predictions (limit to first 500)
            detailed_predictions = []
            for i in range(min(500, len(predictions))):
                item = {
                    "reference": references[i],
                    "prediction": predictions[i],
                    "wer": per_sample_wers[i]
                }
                if sample_ids:
                    item["id"] = sample_ids[i]
                detailed_predictions.append(item)
            
            with open(predictions_file, 'w') as f:
                json.dump(detailed_predictions, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Predictions saved to: {predictions_file}")
            
            # Find worst examples
            worst_indices = sorted(
                range(len(per_sample_wers)), 
                key=lambda i: per_sample_wers[i], 
                reverse=True
            )[:10]
            
            logger.info("\n🔍 Worst 10 Examples:")
            for idx in worst_indices:
                logger.info(f"\n  WER: {per_sample_wers[idx]:.1f}%")
                logger.info(f"  REF: {references[idx][:100]}...")
                logger.info(f"  HYP: {predictions[idx][:100]}...")
        
        return results
    
    def compare_with_baseline(self, baseline_results_path: str):
        """Compare current results with baseline"""
        try:
            with open(baseline_results_path, 'r') as f:
                baseline = json.load(f)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"COMPARISON WITH BASELINE")
            logger.info(f"{'='*60}")
            logger.info(f"Baseline WER: {baseline['wer']}%")
            
            # This will be populated after running evaluate()
            # You would call this after evaluate() completes
            
        except FileNotFoundError:
            logger.warning(f"Baseline results not found: {baseline_results_path}")
        except Exception as e:
            logger.error(f"Error comparing with baseline: {e}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate fine-tuned Whisper model')
    parser.add_argument('--model-path', type=str, required=True,
                        help='Path to model (local directory or HuggingFace model ID)')
    parser.add_argument('--dataset-name', type=str,
                        default='mozilla-foundation/common_voice_17_0',
                        help='Dataset name')
    parser.add_argument('--dataset-lang', type=str, default='sw',
                        help='Dataset language code')
    parser.add_argument('--language', type=str, default='sw',
                        help='Model language')
    parser.add_argument('--task', type=str, default='transcribe',
                        choices=['transcribe', 'translate'],
                        help='Task type')
    parser.add_argument('--split', type=str, default='validation',
                        help='Dataset split to evaluate')
    parser.add_argument('--num-samples', type=int, default=None,
                        help='Number of samples to evaluate (default: all)')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='Batch size for evaluation')
    parser.add_argument('--output-dir', type=str, default='./evaluation_results',
                        help='Output directory for results')
    parser.add_argument('--save-predictions', action='store_true',
                        help='Save predictions to file')
    parser.add_argument('--baseline-results', type=str,
                        help='Path to baseline results for comparison')
    
    args = parser.parse_args()
    
    evaluator = WhisperEvaluator(
        model_path=args.model_path,
        dataset_name=args.dataset_name,
        dataset_lang=args.dataset_lang,
        language=args.language,
        task=args.task
    )
    
    results = evaluator.evaluate(
        split=args.split,
        num_samples=args.num_samples,
        batch_size=args.batch_size,
        save_predictions=args.save_predictions,
        output_dir=args.output_dir
    )
    
    # Compare with baseline if provided
    if args.baseline_results:
        evaluator.compare_with_baseline(args.baseline_results)


if __name__ == "__main__":
    main()