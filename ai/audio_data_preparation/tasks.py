# audio_data_preparation/tasks.py

import os
import uuid
import threading
import traceback
import logging
from django.utils import timezone
from django.db import transaction
from .models import AudioProcessingTask
from .utils.audio_cleanup import preprocess_audio
from .utils.speaker_diarization import perform_diarization
from .utils.audio_chunking import chunk_audio_files

# Configure logging
logger = logging.getLogger(__name__)

def generate_task_id():
    """Generate a unique task ID"""
    return str(uuid.uuid4())

def create_task(task_type, project_id, input_path, **params):
    """
    Create a new audio processing task.
    
    Parameters:
    -----------
    task_type : str
        Type of task ('preprocessing', 'diarization', or 'chunking')
    project_id : str
        ID of the project associated with the task
    input_path : str
        Path to the input audio file
    **params : dict
        Additional parameters for the task
        
    Returns:
    --------
    AudioProcessingTask
        The created task
    """
    task_id = generate_task_id()
    
    with transaction.atomic():
        task = AudioProcessingTask.objects.create(
            task_id=task_id,
            project_id=project_id,
            task_type=task_type,
            input_path=input_path,
            status='pending',
            metadata={'params': params}
        )
    
    return task

def run_task_async(task_id):
    """
    Run a task asynchronously in a separate thread.
    
    Parameters:
    -----------
    task_id : str
        The ID of the task to run
    """
    thread = threading.Thread(target=process_task, args=(task_id,))
    thread.daemon = True
    thread.start()
    return thread

def process_task(task_id):
    """
    Process an audio task based on its type.
    
    Parameters:
    -----------
    task_id : str
        The ID of the task to process
    """
    try:
        task = AudioProcessingTask.objects.get(task_id=task_id)
    except AudioProcessingTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return
    
    # Mark as processing
    task.update_status('processing')
    
    try:
        # Process based on task type
        if task.task_type == 'preprocessing':
            result = process_preprocessing_task(task)
        elif task.task_type == 'diarization':
            result = process_diarization_task(task)
        elif task.task_type == 'chunking':
            result = process_chunking_task(task)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
        
        # Check if the result indicates an error
        if result.get('status') == 'error':
            task.update_status('failed', error_message=result.get('error', 'Unknown error'), 
                                metadata={'error_details': result})
        else:
            # Mark as completed with results
            task.update_status('completed', output_path=result['output_path'], metadata=result)
        
    except Exception as e:
        # Get full traceback for better debugging
        error_message = str(e)
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing task {task_id}: {error_message}")
        logger.error(f"Traceback: {error_traceback}")
        
        # Mark as failed with error message
        task.update_status('failed', error_message=error_message, 
                         metadata={'error_traceback': error_traceback})

def process_preprocessing_task(task):
    """
    Process an audio preprocessing task.
    
    Parameters:
    -----------
    task : AudioProcessingTask
        The task to process
        
    Returns:
    --------
    dict
        The preprocessing result
    """
    params = task.metadata.get('params', {})
    
    # Extract parameters
    noise_reduction = params.get('noise_reduction', 0.3)
    normalize = params.get('normalize', True)
    
    logger.info(f"Running preprocessing on {task.input_path}")
    
    # Run preprocessing
    result = preprocess_audio(
        task.input_path,
        noise_reduction=noise_reduction,
        normalize=normalize
    )
    
    # Ensure result has status field
    if 'status' not in result:
        result['status'] = 'success'
    
    return result

def process_diarization_task(task):
    """
    Process a speaker diarization task.
    
    Parameters:
    -----------
    task : AudioProcessingTask
        The task to process
        
    Returns:
    --------
    dict
        The diarization result
    """
    params = task.metadata.get('params', {})
    
    # Extract parameters
    min_speakers = params.get('min_speakers', 2)
    max_speakers = params.get('max_speakers', 2)
    
    logger.info(f"Running diarization on {task.input_path} with min_speakers={min_speakers}, max_speakers={max_speakers}")
    
    # Run diarization
    result = perform_diarization(
        task.input_path,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )
    
    return result

def process_chunking_task(task):
    """
    Process an audio chunking task.
    
    Parameters:
    -----------
    task : AudioProcessingTask
        The task to process
        
    Returns:
    --------
    dict
        The chunking result
    """
    params = task.metadata.get('params', {})
    
    # Extract parameters
    diarization_result = params.get('diarization_result')
    max_length = params.get('max_length', 10.0)
    overlap = params.get('overlap', 2.0)
    min_chunk = params.get('min_chunk', 1.0)
    
    logger.info(f"Running chunking on {task.input_path}")
    
    # Run chunking
    result = chunk_audio_files(
        task.input_path,
        diarization_json=diarization_result,
        max_length=max_length,
        overlap=overlap,
        min_chunk=min_chunk
    )
    
    # Ensure result has status field
    if 'status' not in result:
        result['status'] = 'success'
    
    return result