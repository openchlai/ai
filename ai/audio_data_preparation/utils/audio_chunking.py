# audio_data_preparation/utils/audio_chunking.py

import os
import json
import numpy as np
import librosa
import soundfile as sf
import uuid
from tqdm import tqdm
from django.conf import settings

def create_speech_only_chunks(audio_path, segments, output_dir, 
                             max_length=10.0, overlap=2.0, min_chunk=1.0):
    """
    Create audio chunks containing only speech, no silence, with specified overlap.
    
    Parameters:
    -----------
    audio_path : str
        Path to the speaker audio file (with silence)
    segments : list
        List of segment dictionaries with start/end times of speech
    output_dir : str
        Directory to save the chunks
    max_length : float
        Maximum chunk duration in seconds (default: 10 seconds)
    overlap : float
        Overlap duration in seconds between chunks when splitting long segments (default: 2 seconds)
    min_chunk : float
        Minimum chunk duration in seconds (default: 1 second)
        
    Returns:
    --------
    list
        Information about created chunks
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load audio
    print(f"Loading audio file {audio_path}...")
    audio, sr = librosa.load(audio_path, sr=None)
    
    # Get base filename without extension
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    
    # Sort segments by start time
    sorted_segments = sorted(segments, key=lambda x: x['start'])
    
    # Create speech-only chunks
    chunks = []
    chunk_audio_list = []
    
    print("Creating speech-only chunks...")
    for segment in tqdm(sorted_segments):
        # Skip segments shorter than min_chunk
        segment_duration = segment['end'] - segment['start']
        if segment_duration < min_chunk:
            continue
            
        # Extract segment audio
        start_sample = segment['start_sample']
        end_sample = segment['end_sample']
        
        # Ensure we don't go out of bounds
        if end_sample > len(audio):
            end_sample = len(audio)
            
        if start_sample >= end_sample or start_sample >= len(audio):
            continue
            
        segment_audio = audio[start_sample:end_sample]
        
        # Remove silence from segment
        # Use librosa's non_silent intervals to find actual speech parts
        non_silent = librosa.effects.split(
            segment_audio, 
            top_db=30,  # Adjust as needed
            frame_length=1024,
            hop_length=512
        )
        
        if len(non_silent) == 0:
            continue  # Skip if no speech detected
        
        # Process each non-silent interval in this segment
        for ns_start, ns_end in non_silent:
            # Skip very short speech parts
            ns_duration = (ns_end - ns_start) / sr
            if ns_duration < min_chunk:
                continue
                
            # Get actual speech audio
            speech_audio = segment_audio[ns_start:ns_end]
            speech_duration = len(speech_audio) / sr
            
            # If speech part is longer than max_length, split with overlap
            if speech_duration > max_length:
                # Calculate number of chunks needed
                overlap_samples = int(overlap * sr)
                stride = int(max_length * sr) - overlap_samples
                total_samples = len(speech_audio)
                
                # Create overlapping chunks
                for i in range(0, total_samples, stride):
                    end_idx = min(i + int(max_length * sr), total_samples)
                    
                    # Skip the last chunk if it's too short
                    if (end_idx - i) / sr < min_chunk:
                        continue
                        
                    # Extract chunk
                    chunk_audio = speech_audio[i:end_idx]
                    
                    # Calculate absolute timestamps
                    abs_start = segment['start'] + (ns_start + i) / sr
                    abs_end = segment['start'] + (ns_start + end_idx) / sr
                    
                    # Save info
                    chunks.append({
                        'start': abs_start,
                        'end': abs_end,
                        'duration': (end_idx - i) / sr
                    })
                    
                    # Store audio for saving later
                    chunk_audio_list.append((chunk_audio, abs_start, abs_end))
            else:
                # Use as is
                abs_start = segment['start'] + ns_start / sr
                abs_end = segment['start'] + ns_end / sr
                
                chunks.append({
                    'start': abs_start,
                    'end': abs_end,
                    'duration': speech_duration
                })
                
                # Store audio for saving later
                chunk_audio_list.append((speech_audio, abs_start, abs_end))
    
    # Save chunks
    chunk_info = []
    
    for i, (chunk_audio, start_time, end_time) in enumerate(chunk_audio_list):
        # Create unique identifier
        chunk_id = uuid.uuid4().hex[:8]
        
        # Create output filename
        chunk_filename = f"{base_filename}_chunk_{i:03d}_{start_time:.2f}-{end_time:.2f}_{chunk_id}.wav"
        chunk_path = os.path.join(output_dir, chunk_filename)
        
        # Save chunk
        sf.write(chunk_path, chunk_audio, sr)
        
        chunk_info.append({
            'path': chunk_path,
            'start': start_time,
            'end': end_time,
            'duration': end_time - start_time,
            'chunk_id': f"{i:03d}_{chunk_id}"
        })
    
    return chunk_info

def chunk_audio_files(audio_path, diarization_json=None, output_dir=None, 
                    max_length=10.0, overlap=2.0, min_chunk=1.0):
    """
    Wrapper function to chunk audio files based on diarization results.
    
    Parameters:
    -----------
    audio_path : str
        Path to the audio file to chunk (can be original or speaker-specific)
    diarization_json : str or None
        Path to diarization result JSON file (if None, will perform diarization first)
    output_dir : str
        Directory to save the chunks (default: settings.CHUNKED_AUDIO_PATH)
    max_length : float
        Maximum chunk duration in seconds (default: 10.0)
    overlap : float
        Overlap duration in seconds (default: 2.0)
    min_chunk : float
        Minimum chunk duration in seconds (default: 1.0)
        
    Returns:
    --------
    dict
        Information about the chunking process and created chunks
    """
    # Use default output directory if not specified
    if output_dir is None:
        output_dir = settings.CHUNKED_AUDIO_PATH
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a unique subdirectory for this chunking task
    task_id = uuid.uuid4().hex[:8]
    base_filename = os.path.splitext(os.path.basename(audio_path))[0]
    chunk_dir = os.path.join(output_dir, f"{base_filename}_chunks_{task_id}")
    os.makedirs(chunk_dir, exist_ok=True)
    
    # Check if diarization result is provided
    if diarization_json and os.path.exists(diarization_json):
        print(f"Using existing diarization results from {diarization_json}")
        with open(diarization_json, 'r') as f:
            diarization_result = json.load(f)
        
        # Determine if this is a speaker-specific audio or original audio
        if '_SPEAKER_' in audio_path or '_timeline_' in audio_path:
            # This is likely a speaker-specific audio from diarization
            # Find the speaker based on filename
            speaker = None
            for spk in diarization_result['speaker_stats'].keys():
                if spk in audio_path:
                    speaker = spk
                    break
            
            if speaker:
                print(f"Detected speaker {speaker} in audio path")
                segments = []
                for segment in diarization_result['segments']:
                    if segment['speaker'] == speaker:
                        # Calculate sample positions based on the audio's sample rate
                        _, sr = librosa.load(audio_path, sr=None)
                        segments.append({
                            'start': segment['start'],
                            'end': segment['end'],
                            'start_sample': int(segment['start'] * sr),
                            'end_sample': int(segment['end'] * sr),
                            'speaker': segment['speaker']
                        })
                
                # Create chunks for this speaker
                chunks = create_speech_only_chunks(
                    audio_path,
                    segments,
                    chunk_dir,
                    max_length=max_length,
                    overlap=overlap,
                    min_chunk=min_chunk
                )
                
                # Save chunk info
                info = {
                    'output_path': chunk_dir,
                    'original_audio': audio_path,
                    'speaker': speaker,
                    'chunks': chunks,
                    'total_chunks': len(chunks),
                    'parameters': {
                        'max_length': max_length,
                        'overlap': overlap,
                        'min_chunk': min_chunk
                    }
                }
                
                # Save to JSON
                info_path = os.path.join(chunk_dir, "chunk_info.json")
                with open(info_path, 'w') as f:
                    json.dump(info, f, indent=2)
                
                print(f"Created {len(chunks)} speech-only chunks for speaker {speaker}")
                
                return info
            
        # If not speaker-specific or speaker not found, process all speakers
        all_chunks = []
        for speaker, stats in diarization_result['speaker_stats'].items():
            print(f"Processing chunks for speaker {speaker}...")
            
            # Create speaker-specific directory
            speaker_dir = os.path.join(chunk_dir, f"speaker_{speaker}")
            os.makedirs(speaker_dir, exist_ok=True)
            
            # Filter segments for this speaker
            segments = []
            for segment in diarization_result['segments']:
                if segment['speaker'] == speaker:
                    # Calculate sample positions based on the audio's sample rate
                    _, sr = librosa.load(audio_path, sr=None)
                    segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'start_sample': int(segment['start'] * sr),
                        'end_sample': int(segment['end'] * sr),
                        'speaker': segment['speaker']
                    })
            
            # Create chunks for this speaker
            speaker_chunks = create_speech_only_chunks(
                audio_path,
                segments,
                speaker_dir,
                max_length=max_length,
                overlap=overlap,
                min_chunk=min_chunk
            )
            
            # Add speaker info to chunks
            for chunk in speaker_chunks:
                chunk['speaker'] = speaker
            
            all_chunks.extend(speaker_chunks)
        
        # Save combined chunk info
        info = {
            'output_path': chunk_dir,
            'original_audio': audio_path,
            'diarization_json': diarization_json,
            'chunks': all_chunks,
            'total_chunks': len(all_chunks),
            'parameters': {
                'max_length': max_length,
                'overlap': overlap,
                'min_chunk': min_chunk
            }
        }
        
        # Save to JSON
        info_path = os.path.join(chunk_dir, "chunk_info.json")
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"Created {len(all_chunks)} speech-only chunks across all speakers")
        
        return info
    else:
        # No diarization result provided, we'll need to perform diarization first
        from .speaker_diarization import perform_diarization
        
        print("No diarization result provided. Performing diarization first...")
        diarization_output = perform_diarization(audio_path)
        
        # Now process each speaker file
        all_chunks = []
        
        # Load diarization result
        with open(diarization_output['diarization_json'], 'r') as f:
            diarization_result = json.load(f)
        
        # Process each speaker
        for speaker, speaker_path in diarization_output['speaker_paths'].items():
            print(f"Processing chunks for speaker {speaker}...")
            
            # Create speaker-specific directory
            speaker_dir = os.path.join(chunk_dir, f"speaker_{speaker}")
            os.makedirs(speaker_dir, exist_ok=True)
            
            # Filter segments for this speaker
            segments = []
            for segment in diarization_result['segments']:
                if segment['speaker'] == speaker:
                    # Calculate sample positions based on the speaker audio's sample rate
                    _, sr = librosa.load(speaker_path, sr=None)
                    segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'start_sample': int(segment['start'] * sr),
                        'end_sample': int(segment['end'] * sr),
                        'speaker': segment['speaker']
                    })
            
            # Create chunks for this speaker
            speaker_chunks = create_speech_only_chunks(
                speaker_path,
                segments,
                speaker_dir,
                max_length=max_length,
                overlap=overlap,
                min_chunk=min_chunk
            )
            
            # Add speaker info to chunks
            for chunk in speaker_chunks:
                chunk['speaker'] = speaker
            
            all_chunks.extend(speaker_chunks)
        
        # Save combined chunk info
        info = {
            'output_path': chunk_dir,
            'original_audio': audio_path,
            'diarization_output': diarization_output['output_path'],
            'diarization_json': diarization_output['diarization_json'],
            'chunks': all_chunks,
            'total_chunks': len(all_chunks),
            'parameters': {
                'max_length': max_length,
                'overlap': overlap,
                'min_chunk': min_chunk
            }
        }
        
        # Save to JSON
        info_path = os.path.join(chunk_dir, "chunk_info.json")
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"Created {len(all_chunks)} speech-only chunks across all speakers")
        
        return info