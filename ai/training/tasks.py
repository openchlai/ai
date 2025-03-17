import logging
from celery import shared_task
from .trainer.whisper_trainer import WhisperTrainer
from .utils.backend_client import BackendClient

logger = logging.getLogger('training')

@shared_task(bind=True)
def start_whisper_training(self, session_id, config):
    """
    Celery task to execute Whisper model training
    
    Args:
        session_id (str): Unique identifier for the training session
        config (dict): Training configuration
    """
    logger.info(f"Starting Whisper training session {session_id}")
    
    # Initialize backend client
    backend_client = BackendClient()
    
    try:
        # Update session status to 'running'
        backend_client.update_session_status(session_id, 'running')
        
        # Initialize and run trainer
        trainer = WhisperTrainer(
            session_id=session_id,
            config=config,
            backend_client=backend_client
        )
        
        # Execute training
        result = trainer.train()
        
        # Update session status to 'completed'
        backend_client.update_session_status(session_id, 'completed')
        
        return {
            'status': 'completed',
            'session_id': session_id,
            'metrics': result
        }
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        
        # Update session status to 'failed'
        backend_client.update_session_status(
            session_id, 
            'failed', 
            error_details=str(e)
        )
        
        # Re-raise the exception for Celery
        raise