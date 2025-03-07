# audio_data_preparation/utils/speaker_diarization.py

import os
import json
import numpy as np
import librosa
import soundfile as sf
from pyannote.audio import Pipeline
import torch
import uuid
from django.conf import settings

class SpeakerDiarizer:
    def __init__(self, model_name="pyannote/speaker-diarization@2.1", device=None):
        """
        Initialize the speaker diarization pipeline.
        
        Parameters:
        -----------
        model_name : str
            The name of the pretrained diarization model to use
        device : str
            Device to run the model on ('cuda' or 'cpu'), if None, will use CUDA if available
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading diarization model on {device}...")
        try:
            self.pipeline = Pipeline.from_pretrained(model_name, use_auth_token=False)
            self.pipeline = self.pipeline.to(torch.device(device))
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("\nNote: You may need to obtain an access token from HuggingFace:")
            print("1. Create an account at https://huggingface.co/")
            print("2. Create an access token at https://huggingface.co/settings/tokens")
            print("3. Run 'huggingface-cli login' and enter your token")
            print("4. Or set environment variable 'export HUGGINGFACE_TOKEN=your_token'")
            raise

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
        print(f"Diarizing {audio_file}...")
        
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
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker,
                'duration': turn.end - turn.start
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
        print(f"Loading audio file {audio_file}...")
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
        
        print("Creating timeline-preserved audio files for each speaker...")
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
            
            print(f"Created {output_path} ({audio_duration:.2f} seconds)")
        
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
        'original_audio': audio_path
    }
    
    return output_details