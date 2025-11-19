"""
Enhanced callbacks for better training monitoring and error recovery
"""

import os
import json
import torch
import logging
from pathlib import Path
from datetime import datetime
from transformers import TrainerCallback, TrainerState, TrainerControl
from typing import Dict, Any
import mlflow

logger = logging.getLogger(__name__)


class SafetyCallback(TrainerCallback):
    """Monitor for NaN losses and other training anomalies"""
    
    def __init__(self, max_nan_count: int = 3):
        self.max_nan_count = max_nan_count
        self.nan_count = 0
        self.last_checkpoint = None
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        
        loss = logs.get('loss')
        
        if loss is not None:
            # Check for NaN
            if torch.isnan(torch.tensor(loss)) or torch.isinf(torch.tensor(loss)):
                self.nan_count += 1
                logger.error(f"⚠️  NaN/Inf loss detected! Count: {self.nan_count}/{self.max_nan_count}")
                
                if self.nan_count >= self.max_nan_count:
                    logger.error(f"❌ Training stopped: Too many NaN losses")
                    control.should_training_stop = True
                    
                    # Try to recover from last checkpoint
                    if self.last_checkpoint:
                        logger.info(f"💡 Try resuming from: {self.last_checkpoint}")
            else:
                # Reset count on valid loss
                self.nan_count = 0
    
    def on_save(self, args, state, control, **kwargs):
        # Track last good checkpoint
        checkpoint_folder = f"checkpoint-{state.global_step}"
        self.last_checkpoint = os.path.join(args.output_dir, checkpoint_folder)


class ProgressMonitorCallback(TrainerCallback):
    """Enhanced progress monitoring with time estimates"""
    
    def __init__(self):
        self.start_time = None
        self.step_times = []
        
    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = datetime.now()
        logger.info(f"🚀 Training started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None or 'loss' not in logs:
            return
        
        current_step = state.global_step
        max_steps = state.max_steps
        
        # Calculate progress
        progress = (current_step / max_steps) * 100
        
        # Estimate time remaining
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            steps_done = current_step
            
            if steps_done > 0:
                seconds_per_step = elapsed / steps_done
                steps_remaining = max_steps - steps_done
                seconds_remaining = seconds_per_step * steps_remaining
                
                hours = int(seconds_remaining // 3600)
                minutes = int((seconds_remaining % 3600) // 60)
                
                logger.info(
                    f"📊 Progress: {progress:.1f}% | "
                    f"Step {current_step}/{max_steps} | "
                    f"Loss: {logs.get('loss', 'N/A'):.4f} | "
                    f"ETA: {hours}h {minutes}m"
                )
    
    def on_train_end(self, args, state, control, **kwargs):
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            logger.info(f"✅ Training completed in {hours}h {minutes}m")


class CheckpointManagerCallback(TrainerCallback):
    """Manage checkpoints and ensure recovery is possible"""
    
    def __init__(self, max_checkpoints: int = 3, save_optimizer: bool = True):
        self.max_checkpoints = max_checkpoints
        self.save_optimizer = save_optimizer
        self.checkpoint_info = []
        
    def on_save(self, args, state, control, **kwargs):
        checkpoint_folder = f"checkpoint-{state.global_step}"
        checkpoint_path = os.path.join(args.output_dir, checkpoint_folder)
        
        # Save checkpoint metadata
        metadata = {
            'step': state.global_step,
            'timestamp': datetime.now().isoformat(),
            'loss': state.log_history[-1].get('loss') if state.log_history else None,
            'eval_loss': state.log_history[-1].get('eval_loss') if state.log_history else None,
        }
        
        metadata_path = os.path.join(checkpoint_path, 'checkpoint_info.json')
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save checkpoint metadata: {e}")
        
        self.checkpoint_info.append({
            'step': state.global_step,
            'path': checkpoint_path,
            'timestamp': datetime.now()
        })
        
        logger.info(f"💾 Checkpoint saved: {checkpoint_path}")
        
        # Clean up old checkpoints if needed
        self._cleanup_old_checkpoints(args)
    
    def _cleanup_old_checkpoints(self, args):
        """Keep only the most recent N checkpoints"""
        if len(self.checkpoint_info) <= self.max_checkpoints:
            return
        
        # Sort by step
        self.checkpoint_info.sort(key=lambda x: x['step'])
        
        # Remove oldest checkpoints
        to_remove = self.checkpoint_info[:-self.max_checkpoints]
        
        for checkpoint in to_remove:
            try:
                import shutil
                if os.path.exists(checkpoint['path']):
                    shutil.rmtree(checkpoint['path'])
                    logger.info(f"🗑️  Removed old checkpoint: {checkpoint['path']}")
            except Exception as e:
                logger.warning(f"Could not remove checkpoint {checkpoint['path']}: {e}")
        
        # Update list
        self.checkpoint_info = self.checkpoint_info[-self.max_checkpoints:]


class MetricsLoggerCallback(TrainerCallback):
    """Enhanced metrics logging with statistics"""
    
    def __init__(self, log_file: str = "training_metrics.jsonl"):
        self.log_file = log_file
        self.metrics_history = []
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        
        # Add timestamp
        log_entry = {
            'step': state.global_step,
            'timestamp': datetime.now().isoformat(),
            **logs
        }
        
        # Save to file
        log_path = os.path.join(args.output_dir, self.log_file)
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.warning(f"Could not write metrics log: {e}")
        
        self.metrics_history.append(log_entry)
    
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics is None:
            return
        
        # Log evaluation metrics
        logger.info("📈 Evaluation Metrics:")
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                logger.info(f"  {key}: {value:.4f}")
    
    def on_train_end(self, args, state, control, **kwargs):
        # Save final metrics summary
        if self.metrics_history:
            summary_path = os.path.join(args.output_dir, 'metrics_summary.json')
            
            # Calculate statistics
            losses = [m.get('loss') for m in self.metrics_history if m.get('loss') is not None]
            
            if losses:
                summary = {
                    'final_loss': losses[-1],
                    'min_loss': min(losses),
                    'max_loss': max(losses),
                    'avg_loss': sum(losses) / len(losses),
                    'total_steps': state.global_step,
                    'total_metrics_logged': len(self.metrics_history)
                }
                
                try:
                    with open(summary_path, 'w') as f:
                        json.dump(summary, f, indent=2)
                    logger.info(f"📊 Metrics summary saved to {summary_path}")
                except Exception as e:
                    logger.warning(f"Could not save metrics summary: {e}")


class EarlyStoppingCallback(TrainerCallback):
    """Stop training if no improvement for N evaluations"""
    
    def __init__(self, patience: int = 5, threshold: float = 0.0):
        self.patience = patience
        self.threshold = threshold
        self.best_metric = None
        self.wait_count = 0
        
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics is None:
            return
        
        # Get the metric we're tracking (WER - lower is better)
        current_metric = metrics.get('eval_wer')
        
        if current_metric is None:
            return
        
        # Check if this is the best so far
        if self.best_metric is None or current_metric < (self.best_metric - self.threshold):
            self.best_metric = current_metric
            self.wait_count = 0
            logger.info(f"🎯 New best WER: {current_metric:.2f}")
        else:
            self.wait_count += 1
            logger.info(f"⏳ No improvement for {self.wait_count}/{self.patience} evaluations")
            
            if self.wait_count >= self.patience:
                logger.info(f"⛔ Early stopping triggered - no improvement for {self.patience} evaluations")
                control.should_training_stop = True


class TensorBoardVerificationCallback(TrainerCallback):
    """Verify TensorBoard logging is working"""
    
    def __init__(self):
        self.verified = False
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if self.verified:
            return
        
        if args.logging_dir and os.path.exists(args.logging_dir):
            # Check if events files are being created
            event_files = list(Path(args.logging_dir).glob('events.out.tfevents.*'))
            
            if event_files:
                logger.info(f"✅ TensorBoard logging verified: {args.logging_dir}")
                self.verified = True
            else:
                logger.warning(f"⚠️  No TensorBoard events found in {args.logging_dir}")


class MLflowCallback(TrainerCallback):
    """Enhanced MLflow logging callback"""
    
    def __init__(self, mlflow_manager):
        self.mlflow_manager = mlflow_manager
        self.current_step = 0
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        """Log training metrics to MLflow"""
        if logs:
            # Filter and log metrics
            metrics = {k: v for k, v in logs.items() 
                      if isinstance(v, (int, float))}
            
            if metrics and state.global_step > self.current_step:
                try:
                    self.mlflow_manager.log_metrics(metrics, state.global_step)
                    self.current_step = state.global_step
                except Exception as e:
                    logger.warning(f"MLflow logging failed: {e}")
    
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        """Log evaluation metrics to MLflow"""
        if metrics:
            eval_metrics = {f"eval_{k}": v for k, v in metrics.items() 
                           if isinstance(v, (int, float))}
            
            if eval_metrics:
                try:
                    self.mlflow_manager.log_metrics(eval_metrics, state.global_step)
                except Exception as e:
                    logger.warning(f"MLflow evaluation logging failed: {e}")
    
    def on_save(self, args, state, control, **kwargs):
        """Log checkpoint save event to MLflow"""
        try:
            self.mlflow_manager.log_metrics(
                {"checkpoint_saved": 1}, 
                state.global_step
            )
            logger.info(f"📊 Checkpoint logged to MLflow at step {state.global_step}")
        except Exception as e:
            logger.warning(f"MLflow checkpoint logging failed: {e}")
    
    def on_train_begin(self, args, state, control, **kwargs):
        """Log training configuration at start"""
        logger.info("📊 MLflow callback initialized")
    
    def on_train_end(self, args, state, control, **kwargs):
        """Final logging at training end"""
        try:
            final_metrics = {
                "training_completed": 1,
                "total_steps": state.global_step
            }
            self.mlflow_manager.log_metrics(final_metrics, state.global_step)
            logger.info("📊 Training completion logged to MLflow")
        except Exception as e:
            logger.warning(f"MLflow final logging failed: {e}")