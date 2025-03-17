# audio_data_preparation/utils/speaker_diarization.py

import os
import json
import numpy as np
import librosa
import soundfile as sf
import torch
import uuid
import logging
from django.conf import settings

# Configure logging
logger = logging.getLogger('audio_data_preparation')

# Global pipeline instance (singleton)
_PIPELINE = None

def get_diarization_pipeline():
    """
    Get or initialize the speaker diarization pipeline.
    Uses a singleton pattern to ensure the model is loaded only once.
    
    Returns:
    --------
    Pipeline
        The initialized diarization pipeline, or None if initialization failed
    """
    global _PIPELINE
    
    if _PIPELINE is not None:
        return _PIPELINE
    
    # Get token from settings or environment
    token = getattr(settings, 'HUGGINGFACE_TOKEN', os.environ.get('HUGGINGFACE_TOKEN'))
    if not token:
        logger.error("No Hugging Face token configured. Set HUGGINGFACE_TOKEN in settings or environment.")
        return None
    
    # Set environment variables
    os.environ["HUGGINGFACE_TOKEN"] = token
    os.environ["HF_TOKEN"] = token
    
    try:
        # Suppress specific warnings about version mismatches
        import warnings
        warnings.filterwarnings("ignore", message="Model was trained with")
        
        # Choose device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading diarization model on {device}...")
        
        # Import here to ensure environment is set
        from pyannote.audio import Pipeline
        
        # Load the pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=token
        )
        
        # Move to device
        pipeline = pipeline.to(device)
        
        # Store in global variable
        _PIPELINE = pipeline
        logger.info("Diarization model loaded successfully!")
        return pipeline
    
    except Exception as e:
        logger.error(f"Error loading diarization model: {e}")
        logger.error("\nTroubleshooting steps:")
        logger.error("1. Make sure your token has proper permissions")
        logger.error("2. Ensure you've accepted the model terms at: https://huggingface.co/pyannote/speaker-diarization")
        logger.error("3. Check your internet connection")
        return None

class SpeakerDiarizer:
    def __init__(self, device=None):
        """
        Initialize the speaker diarization pipeline.
        
        Parameters:
        -----------
        device : str
            Device to run the model on ('cuda' or 'cpu'), if None, will use CUDA if available
        """
        # Get the pipeline
        self.pipeline = get_diarization_pipeline()
        
        if self.pipeline is None:
            raise RuntimeError("Failed to initialize diarization pipeline")

    def diarize(self, audio_file, min_speakers=2, max_speakers=2):
        """
        Perform speaker diarization on an audio file.
        
        Parameters:
        -----------
        audio_file : str
            Path to the audio file
        min_speakers : int
            Minimum number of speakers to expect
        max_speakers : int
            Maximum number of speakers to expect
            
        Returns:
        --------
        dict
            Diarization results containing segments with speaker labels
        """
        logger.info(f"Diarizing {audio_file}...")
        
        # Apply diarization
        diarization = self.pipeline(
            audio_file,
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )
        
        # Extract segments with speaker labels
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'start': float(turn.start),
                'end': float(turn.end),
                'speaker': speaker,
                'duration': float(turn.end - turn.start)
            })
        
        # Sort segments by start time
        segments = sorted(segments, key=lambda x: x['start'])
        
        # Calculate speaker statistics
        speaker_stats = {}
        for segment in segments:
            speaker = segment['speaker']
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    'total_duration': 0,
                    'segment_count': 0,
                    'first_appearance': segment['start']
                }
            
            speaker_stats[speaker]['total_duration'] += segment['duration']
            speaker_stats[speaker]['segment_count'] += 1
        
        return {
            'segments': segments,
            'speaker_stats': speaker_stats,
            'num_speakers': len(speaker_stats)
        }
    
    def create_timeline_preserved_audio(self, audio_file, diarization_result, output_dir):
        """
        Create audio files for each speaker that preserve the original timeline with silence.
        
        Parameters:
        -----------
        audio_file : str
            Path to the audio file
        diarization_result : dict
            The diarization results
        output_dir : str
            Directory to save the timeline-preserved audio files
            
        Returns:
        --------
        dict
            Information about the generated audio files
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load the audio file
        logger.info(f"Loading audio file {audio_file}...")
        audio, sr = librosa.load(audio_file, sr=None)
        audio_duration = len(audio) / sr
        
        # Get base filename without extension
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]
        
        segments = diarization_result['segments']
        speakers = list(diarization_result['speaker_stats'].keys())
        
        # Group segments by speaker
        speaker_segments = {}
        for speaker in speakers:
            speaker_segments[speaker] = []
        
        for segment in segments:
            speaker = segment['speaker']
            speaker_segments[speaker].append({
                'start': segment['start'],
                'end': segment['end'],
                'start_sample': int(segment['start'] * sr),
                'end_sample': int(segment['end'] * sr)
            })
        
        # Create timeline-preserved audio for each speaker
        output_info = {}
        
        logger.info("Creating timeline-preserved audio files for each speaker...")
        for speaker in speakers:
            # Create a silent audio array of the same length as the original
            speaker_audio = np.zeros_like(audio)
            
            # Fill in only the segments for this speaker
            for segment in speaker_segments[speaker]:
                start_sample = segment['start_sample']
                end_sample = segment['end_sample']
                
                # Ensure we don't go out of bounds
                if end_sample > len(audio):
                    end_sample = len(audio)
                
                if start_sample >= end_sample or start_sample >= len(audio):
                    continue
                
                # Copy this speaker's segment to the right position
                speaker_audio[start_sample:end_sample] = audio[start_sample:end_sample]
            
            # Create output filename with unique ID
            unique_id = uuid.uuid4().hex[:8]
            output_filename = f"{base_filename}_{speaker}_timeline_{unique_id}.wav"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the timeline-preserved audio
            sf.write(output_path, speaker_audio, sr)
            
            output_info[speaker] = {
                'path': output_path,
                'duration': audio_duration,
                'segments': speaker_segments[speaker]
            }
            
            logger.info(f"Created {output_path} ({audio_duration:.2f} seconds)")
        
        return output_info

def perform_diarization(audio_path, output_dir=None, min_speakers=2, max_speakers=2):
    """
    Wrapper function to perform speaker diarization on an audio file.
    
    Parameters:
    -----------
    audio_path : str
        Path to the audio file
    output_dir : str
        Directory to save the diarized audio files (default: settings.DIARIZED_AUDIO_PATH)
    min_speakers : int
        Minimum number of speakers to expect
    max_speakers : int
        Maximum number of speakers to expect
        
    Returns:
    --------
    dict
        Information about the diarization results and speaker audio files
    """
    # Use default output directory if not specified
    if output_dir is None:
        output_dir = settings.DIARIZED_AUDIO_PATH
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a unique subdirectory for this audio file
    file_id = uuid.uuid4().hex[:8]
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    result_dir = os.path.join(output_dir, f"{base_filename}_{file_id}")
    os.makedirs(result_dir, exist_ok=True)
    
    try:
        # Initialize diarizer
        diarizer = SpeakerDiarizer()
        
        # Perform diarization
        diarization_result = diarizer.diarize(
            audio_path,
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )
        
        # Save diarization results
        json_output = os.path.join(result_dir, "diarization_result.json")
        with open(json_output, 'w') as f:
            json.dump(diarization_result, f, indent=2)
        
        # Create timeline-preserved audio files for each speaker
        speaker_files = diarizer.create_timeline_preserved_audio(
            audio_path, 
            diarization_result,
            result_dir
        )
        
        # Prepare output details
        speaker_paths = {}
        for speaker, info in speaker_files.items():
            speaker_paths[speaker] = info['path']
        
        output_details = {
            'output_path': result_dir,
            'diarization_json': json_output,
            'speaker_count': len(speaker_paths),
            'speaker_paths': speaker_paths,
            'original_audio': audio_path,
            'status': 'success'
        }
        
        return output_details
    
    except Exception as e:
        logger.error(f"Error in diarization process: {str(e)}")
        return {
            'output_path': result_dir,
            'error': str(e),
            'status': 'error',
            'original_audio': audio_path
        }