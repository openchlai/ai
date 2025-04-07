#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import io
import os
import re
import glob
import torch
import shutil
import numpy as np
import librosa
from threading import Thread
from time import sleep, time
from core import creds
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Paths
AUDIO_DIR = os.path.join(creds.DATASETS, "audio")
DONE_DIR = os.path.join(creds.DATASETS, "audio_done")
TRANSFORMER_MODEL_PATH = "/home/bitz/voice_recognition/whisper-medium-sw-3"

# Ensure necessary directories exist
def ensure_dirs():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)

# Get the latest checkpoint from the model directory
def get_latest_checkpoint(model_dir):
    checkpoints = [d for d in os.listdir(model_dir) if d.startswith('checkpoint-')]
    if not checkpoints:
        return None  # No checkpoints found
    
    # Extract checkpoint numbers and find the highest
    checkpoint_nums = [int(cp.split('-')[1]) for cp in checkpoints]
    latest_num = max(checkpoint_nums)
    latest_checkpoint = f"checkpoint-{latest_num}"
    
    return os.path.join(model_dir, latest_checkpoint)

# Function to transcribe using the Transformer model
def transcribe_using_transformer(audio_path):
    print(f"Starting transformer-based transcription for: {audio_path}")
    
    try:
        # Get the latest checkpoint
        checkpoint_path = get_latest_checkpoint(TRANSFORMER_MODEL_PATH)
        if not checkpoint_path:
            print("No checkpoint found, using the base model")
            checkpoint_path = TRANSFORMER_MODEL_PATH
        
        print(f"Using model checkpoint: {checkpoint_path}")
        
        # Load processor from base model and model from checkpoint
        processor = WhisperProcessor.from_pretrained(TRANSFORMER_MODEL_PATH)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Loading from checkpoint
        model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)

        # Set model to evaluation mode
        model.eval()
        model.generation_config.forced_decoder_ids = None  # Fix forced_decoder_ids warning

        # Load audio using librosa for better handling of long files
        print(f"Loading audio file: {audio_path}")
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        print(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")

        # Split the audio into 30-second chunks (Whisper's maximum length)
        chunk_size = 30 * 16000  # 30 seconds * 16,000 samples per second
        transcriptions = []  # Store all transcriptions

        # Process in chunks
        for i in range(0, len(speech_array), chunk_size):
            chunk = speech_array[i:i + chunk_size]
            
            # Skip chunks that are too short
            if len(chunk) < 1600:  # Skip if less than 0.1 seconds
                continue
                
            print(f"Processing chunk {i//chunk_size + 1}")

            # Convert chunk to model input format
            inputs = processor.feature_extractor(
                chunk, sampling_rate=16000, return_tensors="pt"
            )

            input_features = inputs.input_features.to(device)
            attention_mask = inputs.attention_mask.to(device) if "attention_mask" in inputs else None

            # Run inference with optimized parameters
            with torch.no_grad():
                predicted_ids = model.generate(
                    input_features,
                    attention_mask=attention_mask,
                    max_length=225,
                    num_beams=5,  # Beam search to improve output
                    temperature=0.7,
                    repetition_penalty=1.5,
                )

            # Decode and clean up transcription
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            transcription = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", transcription)  # Remove unwanted symbols
            transcription = re.sub(r"\s+", " ", transcription).strip()  # Clean spaces

            transcriptions.append(transcription)  # Save chunk result
            print(f"📝 Transformer: Transcribed chunk {i//chunk_size + 1}")

        # Merge all transcriptions
        full_transcription = " ".join(transcriptions)
        print("\n🚀 **Transformer Transcription Result (First 100 chars):**")
        print(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
        # Clean up GPU memory
        del model
        del processor
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        return full_transcription
        
    except Exception as e:
        print(f"Error in transformer transcription: {str(e)}")
        # Clean up GPU memory in case of error
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        return f"ERROR: {str(e)}"

# Function to transcribe using Whisper - Processing full audio file
def transcribe_using_whisper(audio_path):
    print(f"Starting Whisper transcription for: {audio_path}")
    
    try:
        # Note: Using Whisper via transformers instead of OpenAI's whisper package
        # Load the model from Hugging Face
        model_id = "openai/whisper-large-v3"
        print(f"Loading Whisper model: {model_id}")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        processor = WhisperProcessor.from_pretrained(model_id)
        model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)
        
        # Process audio - We will use librosa to handle longer files properly
        print(f"Loading audio file: {audio_path}")
        # Use librosa to load the audio file - this handles longer files better
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        print(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")
        
        # Process in chunks of 30 seconds to avoid memory issues
        # Whisper can handle up to 30 seconds of audio at once
        chunk_length = 30 * 16000  # 30 seconds at 16kHz
        transcriptions = []
        
        # Process full audio in chunks
        for i in range(0, len(speech_array), chunk_length):
            print(f"Processing chunk {i//chunk_length + 1}")
            chunk = speech_array[i:i + chunk_length]
            
            # Skip chunks that are too short
            if len(chunk) < 1600:  # Skip if less than 0.1 seconds
                continue
                
            # Convert to features
            input_features = processor.feature_extractor(
                chunk, 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_features.to(device)
            
            # Generate token ids
            with torch.no_grad():
                predicted_ids = model.generate(
                    input_features,
                    language="swahili",
                    task="transcribe"
                )
            
            # Decode token ids to text
            chunk_text = processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0].strip()
            
            transcriptions.append(chunk_text)
        
        # Join all chunks with a space
        full_transcription = " ".join(transcriptions)
        
        print("\n🚀 **Whisper Transcription Result (First 100 chars):**")
        print(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
        # Clean up
        del model
        del processor
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        return full_transcription
        
    except Exception as e:
        print(f"Error in Whisper transcription: {str(e)}")
        # Clean up GPU memory in case of error
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        return f"ERROR: {str(e)}"

# Process a single audio file with both models
def process_audio_file(audio_file):
    base_name = os.path.basename(audio_file)
    print(f"\n==== Processing file: {base_name} ====")
    
    # Run transformer transcription
    transformer_result = transcribe_using_transformer(audio_file)
    
    # Run whisper transcription
    whisper_result = transcribe_using_whisper(audio_file)
    
    # Save results to text files alongside the audio file in DONE_DIR
    base_name_no_ext = os.path.splitext(base_name)[0]
    
    # Move audio file to done directory
    done_audio_path = os.path.join(DONE_DIR, base_name)
    shutil.move(audio_file, done_audio_path)
    
    # Save transformer result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_transformer.txt"), 'w') as f:
        f.write(transformer_result)
    
    # Save whisper result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_whisper.txt"), 'w') as f:
        f.write(whisper_result)
    
    print(f"Completed processing: {base_name}")
    print(f"File moved to: {done_audio_path}")
    print("==== Processing complete ====\n")

# Main timer function that checks for audio files
def scribe_timer(data=False):
    print("Starting transcription service...")
    ensure_dirs()
    
    try:
        while True:
            # Look for audio files
            audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav")) + \
                          glob.glob(os.path.join(AUDIO_DIR, "*.mp3")) + \
                          glob.glob(os.path.join(AUDIO_DIR, "*.ogg")) + \
                          glob.glob(os.path.join(AUDIO_DIR, "*.flac"))
            
            if audio_files:
                print(f"Found {len(audio_files)} audio file(s) to process")
                # Process only the first file, then wait
                process_audio_file(audio_files[0])
                print("Processed one file. Waiting 30 seconds before checking for more...")
            else:
                print("No audio files found. Waiting...")
            
            # Sleep before checking again
            sleep(30)
            
    except Exception as e:
        print(f"Error in scribe_timer: {str(e)}")
        raise e