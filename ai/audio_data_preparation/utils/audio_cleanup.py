# audio_data_preparation/utils/audio_cleanup.py

import os
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from scipy import signal
import uuid
import json
from django.conf import settings

def preprocess_audio(audio_path, output_dir=None, noise_reduction=0.3, normalize=True):
    """
    Clean up an audio file by applying various preprocessing techniques.
    
    Parameters:
    -----------
    audio_path : str
        Path to the input audio file
    output_dir : str
        Directory to save the processed audio file (default: settings.PROCESSED_AUDIO_PATH)
    noise_reduction : float
        Strength of noise reduction (0.0 to 1.0, default: 0.3)
    normalize : bool
        Whether to normalize the audio (default: True)
    
    Returns:
    --------
    dict
        Dictionary containing information about the processed audio
    """
    print(f"Processing {audio_path}...")
    
    # Use default output directory if not specified
    if output_dir is None:
        output_dir = settings.PROCESSED_AUDIO_PATH
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    
    # Step 1: Load the audio file
    audio, sr = librosa.load(audio_path, sr=16000)  # Standardize to 16kHz
    duration = len(audio) / sr
    print(f"Original audio: {duration:.2f} seconds, {sr}Hz sample rate")
    
    # Step 2: Apply noise reduction if enabled
    if noise_reduction > 0:
        print(f"Applying noise reduction (strength: {noise_reduction})...")
        reduced_noise = nr.reduce_noise(
            y=audio, 
            sr=sr,
            stationary=True,
            prop_decrease=noise_reduction
        )
    else:
        reduced_noise = audio
    
    # Step 3: Normalize the audio if enabled
    if normalize:
        print("Normalizing audio...")
        processed_audio = librosa.util.normalize(reduced_noise)
    else:
        processed_audio = reduced_noise
    
    # Step 4: Apply bandpass filter (focus on speech frequencies: 150-5000 Hz)
    print("Applying bandpass filter...")
    nyquist = 0.5 * sr
    low = 150 / nyquist
    high = 5000 / nyquist
    b, a = signal.butter(3, [low, high], btype='band')  # Reduced order from 4 to 3
    filtered = signal.filtfilt(b, a, processed_audio)
    
    # Final processing
    processed_audio = filtered
    
    # Create unique output filename
    output_filename = f"{base_filename}_processed_{uuid.uuid4().hex[:8]}.wav"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the processed audio
    sf.write(output_path, processed_audio, sr)
    
    # Calculate audio metrics
    rms = librosa.feature.rms(y=processed_audio)[0].mean()
    spectral_centroid = librosa.feature.spectral_centroid(y=processed_audio, sr=sr)[0].mean()
    spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=processed_audio, sr=sr))
    
    # Prepare output details
    audio_details = {
        'original_path': audio_path,
        'processed_path': output_path,
        'duration': duration,
        'sample_rate': sr,
        'channels': 1,  # Mono
        'metrics': {
            'rms': float(rms),
            'spectral_centroid': float(spectral_centroid),
            'spectral_contrast': float(spectral_contrast)
        },
        'processing_params': {
            'noise_reduction': noise_reduction,
            'normalize': normalize
        }
    }
    
    print(f"Saved processed audio to {output_path}")
    
    return {
        'output_path': output_path,
        'audio_details': audio_details
    }