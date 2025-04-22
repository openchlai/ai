#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Transcription Service with Database Integration

This service processes audio files for cases that need transcription.
It queries the database for pending cases, finds the corresponding audio files,
transcribes them using multiple models, and updates the database with the results.

Usage:
    python transcription_service.py

Author: Updated script based on original
"""

from __future__ import (
    unicode_literals,
    print_function
    )

import os
import re
import glob
import traceback
import torch
import shutil
import librosa
from time import sleep, time
import importlib
import sys
from core import creds
from transformers import WhisperProcessor, WhisperForConditionalGeneration, Wav2Vec2Processor, Wav2Vec2ForCTC
import whisper
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('transcription_service')

# Paths
AUDIO_DIR = os.path.join(creds.DATASETS, "audio")
DONE_DIR = os.path.join(creds.DATASETS, "audio_done")
HF_MEDIUM_FINETUNED_MODEL_PATH = "/home/bitz/voice_recognition/whisper-medium-sw-3"

# Function to dynamically locate and import modules
def locate(module_name):
    try:
        logger.info(f"Locating module: {module_name}")
        module = importlib.import_module(f"models.{module_name}")
        logger.info(f"Successfully located module: {module_name}")
        return module
    except ImportError as e:
        logger.error(f"Error importing module {module_name}: {str(e)}")
        raise

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

# Detected language (analyzing multiple segments)
def detect_language_from_multiple_segments(audio_path, model, num_segments=5):
    """Detect language by analyzing multiple segments of the audio file"""
    logger.info(f"Detecting language from {num_segments} segments...")
    
    # Load full audio
    full_audio = whisper.load_audio(audio_path)
    audio_length = len(full_audio)
    
    # Calculate segment positions (evenly distributed)
    segment_length = min(30 * 16000, audio_length)  # Max 30 seconds per segment
    
    # Determine positions to sample
    if audio_length <= segment_length:
        # Audio is shorter than one segment
        positions = [0]
    else:
        # Sample multiple positions
        positions = []
        for i in range(num_segments):
            # Distribute segments evenly across the audio
            pos = int((audio_length - segment_length) * i / (num_segments - 1))
            positions.append(pos)
    
    # Collect language probabilities from each segment
    all_probs = {}
    
    for i, pos in enumerate(positions):
        # Extract segment
        segment = full_audio[pos:pos + segment_length]
        
        # Pad or trim to fit model's expected input
        segment = whisper.pad_or_trim(segment)
        
        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(segment, n_mels=model.dims.n_mels).to(model.device)
        
        # Detect language for this segment
        _, probs = model.detect_language(mel)
        
        logger.info(f"Segment {i+1}/{len(positions)} ({pos/16000:.1f}s): Top lang = {max(probs, key=probs.get)}")
        
        # Aggregate probabilities
        for lang, prob in probs.items():
            if lang in all_probs:
                all_probs[lang] += prob
            else:
                all_probs[lang] = prob
    
    # Normalize the aggregated probabilities
    total = sum(all_probs.values())
    if total > 0:  # Avoid division by zero
        for lang in all_probs:
            all_probs[lang] /= total
    
    # Get the most likely language
    detected_language = max(all_probs, key=all_probs.get)
    
    # Print top 3 languages with probabilities
    top_langs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)[:3]
    lang_info = ", ".join([f"{lang}: {prob:.2f}" for lang, prob in top_langs])
    logger.info(f"Overall language detection: {detected_language} (Top langs: {lang_info})")
    
    return detected_language, all_probs

# Function to transcribe using the HF whisper medium finetuned model
def transcribe_hf_whisper_medium_finetuned(audio_path, task):
    logger.info(f"Starting hf whisper model finetuned with commonvoices sw for: {audio_path} task {task}")
    
    try:
        # Get the latest checkpoint
        checkpoint_path = get_latest_checkpoint(HF_MEDIUM_FINETUNED_MODEL_PATH)
        if not checkpoint_path:
            logger.info("No checkpoint found, using the base model")
            checkpoint_path = HF_MEDIUM_FINETUNED_MODEL_PATH
        
        logger.info(f"Using model checkpoint: {checkpoint_path}")
        
        # Load processor from base model and model from checkpoint
        processor = WhisperProcessor.from_pretrained(HF_MEDIUM_FINETUNED_MODEL_PATH)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Loading from checkpoint
        model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)

        start_time = int(time())  # Start time for the first chunk
        # Get the length of the audio file
        audio_length = librosa.get_duration(path=audio_path)

        # Set model to evaluation mode
        model.eval()
        model.generation_config.forced_decoder_ids = None  # Fix forced_decoder_ids warning

        # Load audio using librosa for better handling of long files
        logger.info(f"Loading audio file: {audio_path}")
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        logger.info(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")

        # Split the audio into 30-second chunks (Whisper's maximum length)
        chunk_size = 30 * 16000  # 30 seconds * 16,000 samples per second
        transcriptions = []  # Store all transcriptions
        language_counts = {"sw": 0, "en": 0}  # Dictionary to track language detection results
        
        # For simplified language detection
        try:
            # For a fine-tuned Swahili model, we can use a simplified approach
            # We'll look at the first few tokens of transcription to determine language
            language_detection_enabled = True
            logger.info("Language detection enabled for fine-tuned model")
            
            # Define common words for language detection
            swahili_words = ["na", "kwa", "ya", "wa", "ni", "za", "kuwa", "kutoka", "sasa", "hivyo", 
                          "lakini", "hata", "kama", "pia", "hii", "wewe", "mimi", "sisi", "wao", 
                          "kwamba", "huo", "hilo", "hapa", "zaidi", "moja", "kubwa", "ndani"]
            
            english_words = ["the", "and", "of", "to", "in", "is", "that", "for", "with", "this", 
                           "you", "are", "have", "not", "be", "they", "from", "one", "all", 
                           "there", "their", "will", "would", "about", "what", "which", "when"]
            
        except Exception as lang_e:
            logger.error(f"Language detection setup failed: {str(lang_e)}")
            language_detection_enabled = False
            language_counts = {"sw": 1}  # Default to Swahili

        # Process in chunks
        for i in range(0, len(speech_array), chunk_size):
            chunk = speech_array[i:i + chunk_size]
            
            # Skip chunks that are too short
            if len(chunk) < 1600:  # Skip if less than 0.1 seconds
                continue
                
            logger.info(f"Processing chunk {i//chunk_size + 1}")

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
                    task=task,
                )

            # Decode and clean up transcription
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            transcription = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", transcription)  # Remove unwanted symbols
            transcription = re.sub(r"\s+", " ", transcription).strip()  # Clean spaces
            
            # Simple language detection based on transcription content
            if language_detection_enabled and transcription:
                try:
                    # Count occurrences of words from each language
                    words = transcription.lower().split()
                    sw_count = sum(1 for word in words if word in swahili_words)
                    en_count = sum(1 for word in words if word in english_words)
                    
                    # Determine language based on higher count
                    if sw_count > 0 or en_count > 0:  # Only if we found language markers
                        detected_lang = "sw" if sw_count >= en_count else "en"
                        language_counts[detected_lang] = language_counts.get(detected_lang, 0) + 1
                        logger.info(f"Detected language for chunk {i//chunk_size + 1}: {detected_lang} (SW:{sw_count}/EN:{en_count})")
                    else:
                        logger.info(f"No language markers found in chunk {i//chunk_size + 1}")
                except Exception as lang_e:
                    logger.error(f"Language detection error for chunk {i//chunk_size + 1}: {str(lang_e)}")

            transcriptions.append(transcription)  # Save chunk result
            logger.info(f"📝 Transformer: Transcribed chunk {i//chunk_size + 1}")

        end_time = int(time())  # End time for the last chunk

        # Determine the most common language
        detected_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else "sw"
        
        # Map language code to full name
        language_names = {
            "sw": "swahili",
            "en": "english"
        }
        primary_language = language_names.get(detected_language, detected_language)
        
        logger.info(f"Most frequent detected language: {primary_language}")
        
        processing_time = end_time - start_time
        logger.info(f"Total processing time: {processing_time} seconds")

        full_transcription = " ".join(transcriptions)

        # But the return value would change:
        model_name = 'whisper_medium_finetuned_commonvoice'  # Use underscores instead of hyphens
        transformer_dict = {
            'text': full_transcription,
            'length': audio_length,
            'init': start_time,
            'exit': end_time,
            'processing_time': processing_time,
            'language': primary_language,
            'language_distribution': language_counts,
            'task': task,
            'sampling_rate': 16000,
        }
        
        logger.info(f"Transformer transcription completed: {model_name}")
        
        # Merge all transcriptions
        logger.info("\n🚀 **Transformer Transcription Result (First 100 chars):**")
        logger.info(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
        # Clean up GPU memory
        del model
        del processor
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Explicitly clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        return {model_name: transformer_dict}
        
    except Exception as e:
        error_msg = f"Error in transformer transcription: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return {"error": error_msg}
    
# Function to transcribe using OpenAI Whisper large model
def transcribe_openai_whisper_large(audio_path, task):
    logger.info(f"Starting OpenAI Whisper Large transcription for: {audio_path} task {task}")
    # Check if task is valid
    valid_tasks = ["transcribe", "translate"]
    if task not in valid_tasks:
        error_msg = f"Invalid task: {task}. Valid options are: {valid_tasks}"
        logger.error(error_msg)
        return {"error": error_msg}
    
    try:
        # Load the Whisper model
        model_id = "large"
        logger.info(f"Loading Whisper model: {model_id}")
        model = whisper.load_model(model_id)

        detected_language, language_probs = detect_language_from_multiple_segments(audio_path, model, num_segments=40)
        logger.info(f"Detected language: {detected_language}")
        start_time = int(time())
        audio_length = librosa.get_duration(path=audio_path)
        logger.info(f"Audio length: {audio_length:.2f} seconds")

        # Use transcribe method to process the entire audio file
        # This automatically handles longer audio files by processing them in chunks
        result = model.transcribe(
            audio_path,
            task=task,
        )
        
        # Get the transcription text - model.transcribe returns a dictionary
        transcription_text = result["text"]
        
        # Clean up the transcription text
        transcription_text = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", transcription_text)  # Remove unwanted symbols
        transcription_text = re.sub(r"\s+", " ", transcription_text).strip()  # Clean spaces
        
        # Get the end time
        end_time = int(time())
        
        # Calculate processing time in seconds
        processing_time = end_time - start_time
        
        # Create result dictionary
        model_name = f'whisper-{model_id}'
        torch_dict = {
            'text': transcription_text,
            'length': audio_length,
            'init': start_time,
            'exit': end_time,
            'processing_time': processing_time,
            'language': detected_language,
            'task': task,
            'sampling_rate': 16000,
        }

        logger.info(f"Whisper transcription completed: {model_name}")
        
        logger.info("\n🚀 **Whisper Transcription Result (First 100 chars):**")
        logger.info(transcription_text[:100] + "..." if len(transcription_text) > 100 else transcription_text)
        
        # Better cleanup to ensure GPU memory is released
        # Clean up model
        del model        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Explicitly clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()  # Wait for all CUDA operations to finish
            
        return {model_name: torch_dict}
        
    except Exception as e:
        error_msg = f"Error in Whisper transcription: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return {"error": error_msg}
    
# Function to transcribe using HuggingFace Whisper base model    
def transcribe_hf_whisper_base(audio_path, model_size, task="transcribe"):
    """
    Transcribe or translate audio using a base Whisper model from HuggingFace.
    
    Args:
        audio_path (str): Path to the audio file to process
        model_size (str): Size of Whisper model to use ("tiny", "base", "small", "medium", "large-v2", "large-v3")
        task (str): Either "transcribe" (default) or "translate" to English
        
    Returns:
        dict: Dictionary containing transcription results
    """
    logger.info(f"Starting HF base (not finetuned) Whisper {model_size} {task} for: {audio_path} task {task}")
    # Check if model size is valid
    valid_model_sizes = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
    if model_size not in valid_model_sizes:
        error_msg = f"Invalid model size: {model_size}. Valid options are: {valid_model_sizes}"
        logger.error(error_msg)
        return {"error": error_msg}
    logger.info(f"Using model size: {model_size}")
    
    # Check if task is valid
    valid_tasks = ["transcribe", "translate"]
    if task not in valid_tasks:
        error_msg = f"Invalid task: {task}. Valid options are: {valid_tasks}"
        logger.error(error_msg)
        return {"error": error_msg}
    logger.info(f"Using task: {task}")
    
    try:
        # Load model and processor
        model_id = f"openai/whisper-{model_size}"
        logger.info(f"Loading model: {model_id}")
        
        processor = WhisperProcessor.from_pretrained(model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)

        start_time = int(time())  # Start time for the first chunk
        # Get the length of the audio file
        audio_length = librosa.get_duration(path=audio_path)

        # Set model to evaluation mode
        model.eval()
        
        # Load audio using librosa for better handling of long files
        logger.info(f"Loading audio file: {audio_path}")
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        logger.info(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")

        # Define common words for language detection
        swahili_words = ["na", "kwa", "ya", "wa", "ni", "za", "kuwa", "kutoka", "sasa", "hivyo", 
                      "lakini", "hata", "kama", "pia", "hii", "wewe", "mimi", "sisi", "wao", 
                      "kwamba", "huo", "hilo", "hapa", "zaidi", "moja", "kubwa", "ndani"]
        
        english_words = ["the", "and", "of", "to", "in", "is", "that", "for", "with", "this", 
                       "you", "are", "have", "not", "be", "they", "from", "one", "all", 
                       "there", "their", "will", "would", "about", "what", "which", "when"]

        # Initialize language counts
        language_counts = {"en": 0, "sw": 0}
        
        # Sample segments and transcribe them for language detection
        num_segments = min(3, int(len(speech_array) / (16000 * 30)) + 1)
        segment_positions = [i * len(speech_array) // num_segments for i in range(num_segments)]
        
        logger.info("Performing content-based language detection...")
        for i, pos in enumerate(segment_positions):
            # Extract segment for language detection
            segment_end = min(pos + 30 * 16000, len(speech_array))
            segment = speech_array[pos:segment_end]
            
            if len(segment) < 8000:  # Skip if too short
                continue
                
            # Process features for this segment
            features = processor.feature_extractor(segment, sampling_rate=16000, return_tensors="pt").input_features.to(device)
            
            # Generate a quick sample transcription
            with torch.no_grad():
                # Use English as default language for this sample to avoid errors
                forced_decoder_ids = processor.get_decoder_prompt_ids(task="transcribe", language="en")
                sample_ids = model.generate(
                    features, 
                    forced_decoder_ids=forced_decoder_ids,
                    max_length=50,  # Short sequence for language detection
                    num_beams=1,    # Fast beam
                    temperature=0.0 # Deterministic
                )
                
                # Decode the transcription
                sample_text = processor.batch_decode(sample_ids, skip_special_tokens=True)[0]
                
                # Count occurrences of words from each language
                words = sample_text.lower().split()
                sw_count = sum(1 for word in words if word in swahili_words)
                en_count = sum(1 for word in words if word in english_words)
                
                # Add to language counts
                if sw_count > 0 or en_count > 0:
                    detected_lang = "sw" if sw_count > en_count else "en"
                    language_counts[detected_lang] += 1
                    logger.info(f"Segment {i+1}: Detected {detected_lang} (SW:{sw_count}/EN:{en_count})")
                else:
                    # If no markers found, default to English
                    language_counts["en"] += 1
                    logger.info(f"Segment {i+1}: No clear markers, defaulting to English")

        # Get most common language
        detected_language = max(language_counts.items(), key=lambda x: x[1])[0]
        logger.info(f"Overall detected language: {detected_language}")

        # Split the audio into 30-second chunks (Whisper's maximum length)
        chunk_size = 30 * 16000  # 30 seconds * 16,000 samples per second
        transcriptions = []  # Store all transcriptions

        # Process in chunks
        for i in range(0, len(speech_array), chunk_size):
            chunk = speech_array[i:i + chunk_size]
            
            # Skip chunks that are too short
            if len(chunk) < 1600:  # Skip if less than 0.1 seconds
                continue
                
            logger.info(f"Processing chunk {i//chunk_size + 1}")

            # Convert chunk to model input format
            inputs = processor.feature_extractor(
                chunk, sampling_rate=16000, return_tensors="pt"
            )

            input_features = inputs.input_features.to(device)
            
            # Run inference with optimized parameters
            with torch.no_grad():
                # Set up forced decoder IDs based on task and detected language
                if task == "translate":
                    # For translation to English
                    forced_decoder_ids = processor.get_decoder_prompt_ids(task="translate", language=None)
                else:
                    # For transcription in detected language
                    forced_decoder_ids = processor.get_decoder_prompt_ids(task="transcribe", language=detected_language)
                
                predicted_ids = model.generate(
                    input_features,
                    max_length=225,
                    num_beams=5,              # Beam search for improved output
                    temperature=0.7,
                    repetition_penalty=1.5,
                    forced_decoder_ids=forced_decoder_ids
                )

            # Decode and clean up transcription
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            
            # Less aggressive cleaning to preserve more of the original text
            transcription = re.sub(r"[\r\n\t]", " ", transcription)  # Replace line breaks with spaces
            transcription = re.sub(r"\s+", " ", transcription).strip()  # Clean extra spaces
            
            transcriptions.append(transcription)  # Save chunk result
            logger.info(f"📝 Whisper {model_size}: Processed chunk {i//chunk_size + 1}")

        end_time = int(time())  # End time for the last chunk
        processing_time = end_time - start_time
        logger.info(f"Total processing time: {processing_time} seconds")

        full_transcription = " ".join(transcriptions)

        # Map language code to full name
        language_names = {
            "en": "english",
            "sw": "swahili",
            "fr": "french",
            "es": "spanish",
            "de": "german",
            "zh": "chinese",
            "ru": "russian",
            "ja": "japanese",
            "ar": "arabic",
            "hi": "hindi",
            "pt": "portuguese",
            "it": "italian"
        }
        
        # Get full language name if available
        language_name = language_names.get(detected_language, detected_language)
        
        model_name = f'whisper-{model_size}'
        whisper_dict = {
            'text': full_transcription,
            'length': audio_length,
            'init': start_time,
            'exit': end_time,
            'processing_time': processing_time,
            'language': language_name,
            'language_distribution': language_counts,
            'task': task,
            'sampling_rate': 16000,
        }
        
        logger.info(f"HF Whisper base transcription completed: {model_name}")
        
        # Output preview
        logger.info(f"\n🚀 **Whisper {model_size} Result (First 100 chars):**")
        logger.info(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
        # Clean up GPU memory
        del model
        del processor
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Explicitly clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        return {model_name: whisper_dict}
        
    except Exception as e:
        error_msg = f"Error in Whisper {model_size} processing: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return {"error": error_msg}
    
# Function to transcribe using Wav2Vec2 model
def transcribe_wav2vec2(audio_path, model_id="facebook/wav2vec2-large-960h-lv60-self"):
    """
    Transcribe audio using a Wav2Vec2 model from HuggingFace.
    
    Args:
        audio_path (str): Path to the audio file to process
        model_id (str): HuggingFace model ID for the Wav2Vec2 model
        
    Returns:
        dict: Dictionary containing transcription results
    """
    logger.info(f"Starting Wav2Vec2 transcription for: {audio_path}")
    
    try:
        # Load model and processor
        logger.info(f"Loading model: {model_id}")
        
        processor = Wav2Vec2Processor.from_pretrained(model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        model = Wav2Vec2ForCTC.from_pretrained(model_id).to(device)

        start_time = int(time())
        
        # Get the length of the audio file
        audio_length = librosa.get_duration(path=audio_path)

        # Set model to evaluation mode
        model.eval()
        
        # Load audio using librosa
        logger.info(f"Loading audio file: {audio_path}")
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        logger.info(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")

        # Process in chunks due to potential GPU memory limitations
        chunk_size = 30 * 16000  # 30 seconds at 16kHz
        transcriptions = []
        
        # Process in chunks
        for i in range(0, len(speech_array), chunk_size):
            chunk = speech_array[i:i + chunk_size]
            
            # Skip chunks that are too short
            if len(chunk) < 1600:  # Skip if less than 0.1 seconds
                continue
                
            logger.info(f"Processing chunk {i//chunk_size + 1}")
            
            # Process audio with the model
            input_values = processor(
                chunk, 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_values.to(device)
            
            # Run inference
            with torch.no_grad():
                logits = model(input_values).logits
                
            # Take argmax and decode
            predicted_ids = torch.argmax(logits, dim=-1)
            chunk_transcription = processor.batch_decode(predicted_ids)[0]
            
            transcriptions.append(chunk_transcription)
            logger.info(f"📝 Wav2Vec2: Transcribed chunk {i//chunk_size + 1}")

        end_time = int(time())
        processing_time = end_time - start_time
        logger.info(f"Total processing time: {processing_time} seconds")

        # Join all transcriptions
        full_transcription = " ".join(transcriptions)

        full_transcription = full_transcription.lower()
        
        # For this phonetic model, add a note that it's phonetic output
        if "espeak" in model_id:
            logger.info("Note: This model produces phonetic transcriptions in IPA format")
        
        # Extract model name from model_id for the key
        model_name = model_id.split('/')[-1] if '/' in model_id else model_id
        
        wav2vec2_dict = {
            'text': full_transcription,
            'length': audio_length,
            'init': start_time,
            'exit': end_time,
            'processing_time': processing_time,
            'sampling_rate': 16000,
        }
        
        logger.info(f"Wav2Vec2 transcription completed: {model_name}")
        
        # Output preview
        logger.info("\n🚀 **Wav2Vec2 Transcription Result (First 100 chars):**")
        logger.info(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
        # Clean up GPU memory
        del model
        del processor
        del input_values
        del logits
        del predicted_ids

        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Explicitly clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            with torch.cuda.device(device):
                # Ensure all CUDA operations are completed
                torch.cuda.ipc_collect()
                torch.cuda.synchronize()

            for obj in gc.get_objects():
                try:
                    if torch.is_tensor(obj):
                        obj.detach().cpu
                except:
                    pass

        return {model_name: wav2vec2_dict}
        
    except Exception as e:
        error_msg = f"Error in Wav2Vec2 transcription: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return {"error": error_msg}
    
def process_audio_file(audio_file, case_id):
    """
    Process an audio file and update the database with transcription results
    
    Args:
        audio_file (str): Path to the audio file to process
        case_id (str): ID of the case in the database
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    base_name = os.path.basename(audio_file)
    logger.info(f"\n==== Processing file: {base_name} for case ID: {case_id} ====")
    
    # Initialize transcription dictionary to store all results
    transcription_data = {}
    translation_data = {}
    
    try:
        # Run hf whisper medium finetuned transcription
        logger.info("Starting HF Whisper medium finetuned transcription")
        hf_finetuned_medium_transcribe_result = transcribe_hf_whisper_medium_finetuned(audio_file, "transcribe")
        if "error" not in hf_finetuned_medium_transcribe_result:
            transcription_data.update(hf_finetuned_medium_transcribe_result)
        else:
            logger.error(f"Error in HF finetuned transcription: {hf_finetuned_medium_transcribe_result['error']}")

        # Run hf whisper medium finetuned translation
        logger.info("Starting HF Whisper medium finetuned translation")
        hf_finetuned_medium_translate_result = transcribe_hf_whisper_medium_finetuned(audio_file, "translate")
        if "error" not in hf_finetuned_medium_translate_result:
            translation_data.update(hf_finetuned_medium_translate_result)
        else:
            logger.error(f"Error in HF finetuned translation: {hf_finetuned_medium_translate_result['error']}")
        
        # Run openai whisper large transcription
        logger.info("Starting OpenAI Whisper large transcription")
        openai_large_transcribe_result = transcribe_openai_whisper_large(audio_file, "transcribe")
        if "error" not in openai_large_transcribe_result:
            transcription_data.update(openai_large_transcribe_result)
        else:
            logger.error(f"Error in OpenAI Whisper large transcription: {openai_large_transcribe_result['error']}")

        # Run openai whisper large translation
        logger.info("Starting OpenAI Whisper large translation")
        openai_large_translate_result = transcribe_openai_whisper_large(audio_file, "translate")
        if "error" not in openai_large_translate_result:
            translation_data.update(openai_large_translate_result)
        else:
            logger.error(f"Error in OpenAI Whisper large translation: {openai_large_translate_result['error']}")

        # Run hf whisper base medium transcription
        logger.info("Starting HF Whisper base medium transcription")
        hf_base_medium_transcribe_result = transcribe_hf_whisper_base(audio_file, "medium", "transcribe")
        if "error" not in hf_base_medium_transcribe_result:
            transcription_data.update(hf_base_medium_transcribe_result)
        else:
            logger.error(f"Error in HF Whisper base medium transcription: {hf_base_medium_transcribe_result['error']}")

        # Run hf whisper base medium translation
        logger.info("Starting HF Whisper base medium translation")
        hf_base_medium_translate_result = transcribe_hf_whisper_base(audio_file, "medium", "translate")
        if "error" not in hf_base_medium_translate_result:
            translation_data.update(hf_base_medium_translate_result)
        else:
            logger.error(f"Error in HF Whisper base medium translation: {hf_base_medium_translate_result['error']}")

        # Run wav2vec2 transcription (English only)
        logger.info("Starting Wav2Vec2 large transcription")
        wav2vec2_transcribe_result = transcribe_wav2vec2(audio_file)
        if "error" not in wav2vec2_transcribe_result:
            transcription_data.update(wav2vec2_transcribe_result)
        else:
            logger.error(f"Error in Wav2Vec2 transcription: {wav2vec2_transcribe_result['error']}")
        
        # Move audio file to done directory
        # done_audio_path = os.path.join(DONE_DIR, base_name)
        # try:
        #     shutil.move(audio_file, done_audio_path)
        #     logger.info(f"Moved audio file to: {done_audio_path}")
        # except Exception as e:
        #     logger.error(f"Error moving audio file: {str(e)}")
        
        # Update database with transcription and translation results
        casedata = locate('casedata')
        
        # Update transcription data
        if transcription_data:
            logger.info(f"Updating transcription data for case ID: {case_id}")
            
            # Combine all text fields into a single field for easier access
            all_transcription_texts = {}
            for key, value in transcription_data.items():
                if key.endswith('.text'):
                    model_name = key.split('.')[1]
                    all_transcription_texts[model_name] = value
            
            # Create combined transcription data with all_texts field
            combined_data = transcription_data.copy()
            combined_data['all_texts'] = all_transcription_texts
            
            transcription_update = {
                "item": "edit",
                "id": case_id,
                "edit": {
                    "transcription": combined_data
                }
            }
            transcription_result = casedata.indexaction(transcription_update)
            if transcription_result.get('error'):
                logger.error(f"Error updating transcription data: {transcription_result['error']}")
            else:
                logger.info("Successfully updated transcription data")
        
        # Update translation data
        if translation_data:
            logger.info(f"Updating translation data for case ID: {case_id}")
            
            # Combine all text fields into a single field for easier access
            all_translation_texts = {}
            for key, value in translation_data.items():
                if key.endswith('.text'):
                    model_name = key.split('.')[1]
                    all_translation_texts[model_name] = value
            
            # Create combined translation data with all_texts field
            combined_translation = translation_data.copy()
            combined_translation['all_texts'] = all_translation_texts
            
            translation_update = {
                "item": "edit",
                "id": case_id,
                "edit": {
                    "translation": combined_translation
                }
            }
            translation_result = casedata.indexaction(translation_update)
            if translation_result.get('error'):
                logger.error(f"Error updating translation data: {translation_result['error']}")
            else:
                logger.info("Successfully updated translation data")
        
        # Add audit entry for transcription completion
        audit_update = {
            "item": "audit",
            "id": case_id,
            "audit": {
                "action": "transcription_completed",
                "details": f"Automated transcription completed with {len(transcription_data)} models"
            }
        }
        audit_result = casedata.indexaction(audit_update)
        if audit_result.get('error'):
            logger.error(f"Error adding audit entry: {audit_result['error']}")
        else:
            logger.info("Successfully added audit entry for transcription completion")
        
        logger.info(f"Completed processing: {base_name}")
        logger.info("==== Processing complete ====\n")
        return True
        
    except Exception as e:
        error_msg = f"Error in process_audio_file: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()
        
        # Try to add audit entry for failed transcription
        try:
            casedata = locate('casedata')
            error_update = {
                "item": "audit",
                "id": case_id,
                "audit": {
                    "action": "transcription_failed",
                    "details": error_msg[:500]  # Limit error message length
                }
            }
            casedata.indexaction(error_update)
        except Exception as audit_e:
            logger.error(f"Error adding audit entry for failure: {str(audit_e)}")
        
        return False
    
# Find and process pending transcription cases
def process_pending_transcriptions():
    """
    Query the database for one case needing transcription, find its audio file,
    process it, or mark as "no audio found" if the audio doesn't exist
    """
    logger.info("Looking for a pending transcription case...")
    
    try:
        # Import casedata module
        casedata = locate('casedata')
        
        # Query for one case that needs transcription
        query = {
            "task": "transcribe",
            "transcription_only": True,
            "docs": 1  # Get just one case
        }
        
        result = casedata.indexdata(query)
        
        if not result.get('data'):
            logger.error(f"Error querying database: {result.get('error', 'Unknown error')}")
            return 0
        
        if not result.get('unique_ids') or len(result.get('unique_ids', [])) == 0:
            logger.info("No pending transcription cases found")
            return 0
        
        # Get the unique_id for the single case
        unique_id = result.get('unique_ids')[0]
        logger.info(f"Found case with unique_id: {unique_id}")
        
        # Get the case details
        case_query = {
            "task": "transcribe",
            "uniqueid": unique_id
        }
        
        case_result = casedata.indexdata(case_query)
        
        if not case_result.get('data') or not case_result.get('meta'):
            logger.error(f"Could not find case details for unique_id: {unique_id}")
            return 0
        
        case_data = case_result['meta'][0]
        case_id = case_data.get('id')
        
        if not case_id:
            logger.error(f"No case ID found for unique_id: {unique_id}")
            return 0
        
        logger.info(f"Processing case ID: {case_id}, unique_id: {unique_id}")
        
        # Look for audio file with matching unique_id
        audio_files = []
        for ext in ['wav', 'mp3', 'ogg', 'flac']:
            pattern = os.path.join(AUDIO_DIR, f"{unique_id}*.{ext}")
            audio_files.extend(glob.glob(pattern))
        
        if not audio_files:
            logger.warning(f"No audio file found for unique_id: {unique_id}")
            
            # Update the case with "no audio found" status
            # Important: Must set a non-empty transcription object
            transcription_update = {
                "item": "edit",
                "id": case_id,
                "edit": {
                    "transcription": {
                        "status": "no_audio_found",
                        "processed_time": int(time()),
                        "no_audio": True  # Add a clear flag
                    }
                }
            }
            
            update_result = casedata.indexaction(transcription_update)
            if update_result.get('error'):
                logger.error(f"Failed to update transcription with no_audio_found status: {update_result.get('error')}")
            else:
                logger.info(f"Successfully marked case {case_id} as no_audio_found")
            
            # Add audit entry
            audit_update = {
                "item": "audit",
                "id": case_id,
                "audit": {
                    "action": "transcription_skipped",
                    "details": "No matching audio file found"
                }
            }
            audit_result = casedata.indexaction(audit_update)
            if audit_result.get('error'):
                logger.error(f"Failed to add audit entry: {audit_result.get('error')}")
            
            # Return 1 to indicate we processed one case (even though no transcription was done)
            return 1
        
        # Use the first matching audio file
        audio_file = audio_files[0]
        logger.info(f"Found audio file: {audio_file}")
        
        # Process the audio file
        success = process_audio_file(audio_file, case_id)
        
        return 1 if success else 0
        
    except Exception as e:
        logger.error(f"Error in process_pending_transcriptions: {str(e)}")
        traceback.print_exc()
        return 0

# Main timer function that checks for pending transcription cases
def scribe_timer(data=False):
    """
    Main service loop that looks for cases needing transcription
    """
    logger.info("Starting transcription service...")
    ensure_dirs()
    
    try:
        while True:
            # Process pending transcription cases
            processed_count = process_pending_transcriptions()
            
            if processed_count > 0:
                logger.info(f"Processed {processed_count} file(s). Waiting 30 seconds before checking for more...")
            else:
                logger.info("No cases processed. Waiting...")
            
            # Sleep before checking again
            sleep(30)
            
    except Exception as e:
        logger.error(f"Error in scribe_timer: {str(e)}")
        traceback.print_exc()
        raise e