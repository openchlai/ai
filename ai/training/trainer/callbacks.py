import logging
from transformers import TrainerCallback

logger = logging.getLogger('training')

class ProgressCallback(TrainerCallback):
    """
    Custom callback to send progress updates to main backend
    """
    def __init__(self, session_id, backend_client):
        self.session_id = session_id
        self.backend_client = backend_client
        self.last_update_step = 0
        self.update_frequency = 25  # Send updates every 25 steps
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        """Log training metrics at each logging step"""
        if not logs:
            return
            
        step = state.global_step
        
        # Only send updates at specified frequency to avoid API spam
        if step - self.last_update_step >= self.update_frequency:
            progress_data = {
                'step': step,
                'epoch': getattr(state, 'epoch', 0)
            }
            
            # Add relevant metrics
            for key in ['loss', 'learning_rate', 'grad_norm']:
                if key in logs:
                    progress_data[key] = logs[key]
            
            try:
                self.backend_client.send_progress_update(
                    self.session_id, 
                    progress_data
                )
                self.last_update_step = step
            except Exception as e:
                logger.error(f"Failed to send progress update: {str(e)}")
    
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        """Send evaluation metrics to backend"""
        if not metrics:
            return
            
        evaluation_data = {
            'step': state.global_step,
            'epoch': getattr(state, 'epoch', 0)
        }
        
        # Add all evaluation metrics
        for key, value in metrics.items():
            if key.startswith('eval_'):
                # Remove 'eval_' prefix for cleaner backend storage
                cleaned_key = key[5:] if key.startswith('eval_') else key
                evaluation_data[cleaned_key] = value
        
        try:
            self.backend_client.send_evaluation_metrics(
                self.session_id, 
                evaluation_data
            )
        except Exception as e:
            logger.error(f"Failed to send evaluation metrics: {str(e)}")