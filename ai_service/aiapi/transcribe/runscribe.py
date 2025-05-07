#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from core import creds
from transformers import WhisperProcessor, WhisperForConditionalGeneration, Wav2Vec2Processor, Wav2Vec2ForCTC
import whisper

# Paths
AUDIO_DIR = os.path.join(creds.DATASETS, "audio")
DONE_DIR = os.path.join(creds.DATASETS, "audio_done")
HF_MEDIUM_FINETUNED_MODEL_PATH = "/home/bitz/voice_recognition/whisper-medium-sw-3"

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
    print(f"Detecting language from {num_segments} segments...")
    
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
        
        print(f"Segment {i+1}/{len(positions)} ({pos/16000:.1f}s): Top lang = {max(probs, key=probs.get)}")
        
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
    print(f"Overall language detection: {detected_language} (Top langs: {lang_info})")
    
    return detected_language, all_probs

# Function to transcribe using the HF whisper medium finetuned model
def transcribe_hf_whisper_medium_finetuned(audio_path, task):
    print(f"Starting hf whisper model finetuned with commonvoices sw for: {audio_path} task {task}")
    
    try:
        # Get the latest checkpoint
        checkpoint_path = get_latest_checkpoint(HF_MEDIUM_FINETUNED_MODEL_PATH)
        if not checkpoint_path:
            print("No checkpoint found, using the base model")
            checkpoint_path = HF_MEDIUM_FINETUNED_MODEL_PATH
        
        print(f"Using model checkpoint: {checkpoint_path}")
        
        # Load processor from base model and model from checkpoint
        processor = WhisperProcessor.from_pretrained(HF_MEDIUM_FINETUNED_MODEL_PATH)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Loading from checkpoint
        model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)

        start_time = int(time())  # Start time for the first chunk
        # Get the length of the audio file
        audio_length = librosa.get_duration(path=audio_path)

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
        language_counts = {"sw": 0, "en": 0}  # Dictionary to track language detection results
        
        # For simplified language detection
        try:
            # For a fine-tuned Swahili model, we can use a simplified approach
            # We'll look at the first few tokens of transcription to determine language
            language_detection_enabled = True
            print("Language detection enabled for fine-tuned model")
            
            # Define common words for language detection
            swahili_words = ["na", "kwa", "ya", "wa", "ni", "za", "kuwa", "kutoka", "sasa", "hivyo", 
                          "lakini", "hata", "kama", "pia", "hii", "wewe", "mimi", "sisi", "wao", 
                          "kwamba", "huo", "hilo", "hapa", "zaidi", "moja", "kubwa", "ndani"]
            
            english_words = ["the", "and", "of", "to", "in", "is", "that", "for", "with", "this", 
                           "you", "are", "have", "not", "be", "they", "from", "one", "all", 
                           "there", "their", "will", "would", "about", "what", "which", "when"]
            
        except Exception as lang_e:
            print(f"Language detection setup failed: {str(lang_e)}")
            language_detection_enabled = False
            language_counts = {"sw": 1}  # Default to Swahili

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
                        print(f"Detected language for chunk {i//chunk_size + 1}: {detected_lang} (SW:{sw_count}/EN:{en_count})")
                    else:
                        print(f"No language markers found in chunk {i//chunk_size + 1}")
                except Exception as lang_e:
                    print(f"Language detection error for chunk {i//chunk_size + 1}: {str(lang_e)}")

            transcriptions.append(transcription)  # Save chunk result
            print(f"📝 Transformer: Transcribed chunk {i//chunk_size + 1}")

        end_time = int(time())  # End time for the last chunk

        # Determine the most common language
        detected_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else "sw"
        
        # Map language code to full name
        language_names = {
            "sw": "swahili",
            "en": "english"
        }
        primary_language = language_names.get(detected_language, detected_language)
        
        print(f"Most frequent detected language: {primary_language}")
        
        processing_time = end_time - start_time
        print(f"Total processing time: {processing_time} seconds")

        full_transcription = " ".join(transcriptions)

        transformer_dict = {
                'transcription.transformer.text': full_transcription,
                'transcription.transformer.length': audio_length,
                'transcription.transformer.init': start_time,
                'transcription.transformer.exit': end_time,
                'transcription.transformer.processing_time': processing_time,
                'transcription.transformer.model': 'whisper-medium-finetuned-commonvoice',
                'transcription.transformer.checkpoint': checkpoint_path,
                'transcription.transformer.language': primary_language,  # Use the most common detected language
                'transcription.transformer.language_distribution': language_counts,  # Add distribution for analysis
                'transcription.transformer.task': task,
                'transcription.transformer.sampling_rate': 16000,
                }
        
        print(transformer_dict)
        
        # Merge all transcriptions
        print("\n🚀 **Transformer Transcription Result (First 100 chars):**")
        print(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
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
        
        return full_transcription
        
    except Exception as e:
        print(f"Error in transformer transcription: {str(e)}")
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return f"ERROR: {str(e)}"

# Function to transcribe using OpenAI Whisper large model
def transcribe_openai_whisper_large(audio_path, task):
    print(f"Starting OpenAI Whisper Large transcription for: {audio_path} task {task}")
    # Check if task is valid
    valid_tasks = ["transcribe", "translate"]
    if task not in valid_tasks:
        raise ValueError(f"Invalid task: {task}. Valid options are: {valid_tasks}")
    
    try:
        # Load the Whisper model
        model_id = "large"
        print(f"Loading Whisper model: {model_id}")
        model = whisper.load_model(model_id)

        detected_language, language_probs = detect_language_from_multiple_segments(audio_path, model, num_segments=40)
        print(f"Detected language: {detected_language}")
        start_time = int(time())
        audio_length = librosa.get_duration(path=audio_path)
        print(f"Audio length: {audio_length:.2f} seconds")


        
        # Use transcribe method to process the entire audio file
        # This automatically handles longer audio files by processing them in chunks
        result = model.transcribe(
            audio_path,
            task= task,
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
        torch_dict = {
            'transcription.torch.text': transcription_text,
            'transcription.torch.length': audio_length,
            'transcription.torch.init': start_time,
            'transcription.torch.exit': end_time,
            'transcription.torch.processing_time': processing_time,
            'transcription.torch.model': model_id,
            'transcription.torch.language': detected_language,
            'transcription.torch.task': task,
            'transcription.torch.sampling_rate': 16000,
        }

        print(torch_dict)
        
        print("\n🚀 **Whisper Transcription Result (First 100 chars):**")
        print(transcription_text[:100] + "..." if len(transcription_text) > 100 else transcription_text)
        
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
            
        return transcription_text
        
    except Exception as e:
        print(f"Error in Whisper transcription: {str(e)}")
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return f"ERROR: {str(e)}"
    
# Function to transcribe using HuggingFace Whisper base model    
def transcribe_hf_whisper_base(audio_path, model_size, task="transcribe"):
    """
    Transcribe or translate audio using a base Whisper model from HuggingFace.
    
    Args:
        audio_path (str): Path to the audio file to process
        model_size (str): Size of Whisper model to use ("tiny", "base", "small", "medium", "large-v2", "large-v3")
        task (str): Either "transcribe" (default) or "translate" to English
        
    Returns:
        str: The full transcription or translation text
    """
    print(f"Starting HF base (not finetuned) Whisper {model_size} {task} for: {audio_path} task {task}")
    # Check if model size is valid
    valid_model_sizes = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
    if model_size not in valid_model_sizes:
        raise ValueError(f"Invalid model size: {model_size}. Valid options are: {valid_model_sizes}")
    print(f"Using model size: {model_size}")
    # Check if task is valid
    valid_tasks = ["transcribe", "translate"]
    if task not in valid_tasks:
        raise ValueError(f"Invalid task: {task}. Valid options are: {valid_tasks}")
    print(f"Using task: {task}")
    
    try:
        # Load model and processor
        model_id = f"openai/whisper-{model_size}"
        print(f"Loading model: {model_id}")
        
        processor = WhisperProcessor.from_pretrained(model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        model = WhisperForConditionalGeneration.from_pretrained(model_id).to(device)

        start_time = int(time())  # Start time for the first chunk
        # Get the length of the audio file
        audio_length = librosa.get_duration(path=audio_path)

        # Set model to evaluation mode
        model.eval()
        
        # Load audio using librosa for better handling of long files
        print(f"Loading audio file: {audio_path}")
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        print(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")

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
        
        print("Performing content-based language detection...")
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
                    print(f"Segment {i+1}: Detected {detected_lang} (SW:{sw_count}/EN:{en_count})")
                else:
                    # If no markers found, default to English
                    language_counts["en"] += 1
                    print(f"Segment {i+1}: No clear markers, defaulting to English")

        # Get most common language
        detected_language = max(language_counts.items(), key=lambda x: x[1])[0]
        print(f"Overall detected language: {detected_language}")

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
            print(f"📝 Whisper {model_size}: Processed chunk {i//chunk_size + 1}")

        end_time = int(time())  # End time for the last chunk
        processing_time = end_time - start_time
        print(f"Total processing time: {processing_time} seconds")

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
        
        whisper_dict = {
            'transcription.whisper.text': full_transcription,
            'transcription.whisper.length': audio_length,
            'transcription.whisper.init': start_time,
            'transcription.whisper.exit': end_time,
            'transcription.whisper.processing_time': processing_time,
            'transcription.whisper.model': f'whisper-{model_size}',
            'transcription.whisper.language': language_name,
            'transcription.whisper.language_distribution': language_counts,
            'transcription.whisper.task': task,
            'transcription.whisper.sampling_rate': 16000,
        }
        
        print(whisper_dict)
        
        # Output preview
        print(f"\n🚀 **Whisper {model_size} Result (First 100 chars):**")
        print(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
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
        
        return full_transcription
        
    except Exception as e:
        print(f"Error in Whisper {model_size} processing: {str(e)}")
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return f"ERROR: {str(e)}"
 
def transcribe_wav2vec2(audio_path, model_id="facebook/wav2vec2-large-960h-lv60-self"):
    """
    Transcribe audio using a Wav2Vec2 model from HuggingFace.
    
    Args:
        audio_path (str): Path to the audio file to process
        model_id (str): HuggingFace model ID for the Wav2Vec2 model
        
    Returns:
        str: The full transcription text
    """
    print(f"Starting Wav2Vec2 transcription for: {audio_path}")
    
    try:
        # Load model and processor
        print(f"Loading model: {model_id}")
        
        processor = Wav2Vec2Processor.from_pretrained(model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        model = Wav2Vec2ForCTC.from_pretrained(model_id).to(device)

        start_time = int(time())
        
        # Get the length of the audio file
        audio_length = librosa.get_duration(path=audio_path)

        # Set model to evaluation mode
        model.eval()
        
        # Load audio using librosa
        print(f"Loading audio file: {audio_path}")
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
        print(f"Audio loaded: {len(speech_array)/sampling_rate:.2f} seconds")

        # Process in chunks due to potential GPU memory limitations
        chunk_size = 30 * 16000  # 30 seconds at 16kHz
        transcriptions = []
        
        # Process in chunks
        for i in range(0, len(speech_array), chunk_size):
            chunk = speech_array[i:i + chunk_size]
            
            # Skip chunks that are too short
            if len(chunk) < 1600:  # Skip if less than 0.1 seconds
                continue
                
            print(f"Processing chunk {i//chunk_size + 1}")
            
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
            print(f"📝 Wav2Vec2: Transcribed chunk {i//chunk_size + 1}")

        end_time = int(time())
        processing_time = end_time - start_time
        print(f"Total processing time: {processing_time} seconds")

        # Join all transcriptions
        full_transcription = " ".join(transcriptions)

        full_transcription = full_transcription.lower()
        
        # For this phonetic model, add a note that it's phonetic output
        if "espeak" in model_id:
            print("Note: This model produces phonetic transcriptions in IPA format")
        
        wav2vec2_dict = {
            'transcription.wav2vec2.text': full_transcription,
            'transcription.wav2vec2.length': audio_length,
            'transcription.wav2vec2.init': start_time,
            'transcription.wav2vec2.exit': end_time,
            'transcription.wav2vec2.processing_time': processing_time,
            'transcription.wav2vec2.model': model_id,
            'transcription.wav2vec2.sampling_rate': 16000,
        }
        
        print(wav2vec2_dict)
        
        # Output preview
        print("\n🚀 **Wav2Vec2 Transcription Result (First 100 chars):**")
        print(full_transcription[:100] + "..." if len(full_transcription) > 100 else full_transcription)
        
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

        return full_transcription
        
    except Exception as e:
        print(f"Error in Wav2Vec2 transcription: {str(e)}")
        traceback.print_exc()  # Print the full traceback for debugging
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return f"ERROR: {str(e)}"
     
# Process a single audio file with both models
def process_audio_file(audio_file):
    base_name = os.path.basename(audio_file)
    print(f"\n==== Processing file: {base_name} ====")
    
    # Run hf transcription
    hf_finetuned_medium_transcribe_result = transcribe_hf_whisper_medium_finetuned(audio_file, "transcribe")

    # Run hf translation
    hf_finetuned_medium_translate_result = transcribe_hf_whisper_medium_finetuned(audio_file, "translate")
    
    # Run whisper transcription
    openai_large_transcribe_result = transcribe_openai_whisper_large(audio_file, "transcribe")

    # Run whisper translation
    openai_large_translate_result = transcribe_openai_whisper_large(audio_file, "translate")

    # Run hf whisper base medium transcription
    hf_base_medium_transcribe_result = transcribe_hf_whisper_base(audio_file, "medium", "transcribe")

    # Run hf whisper base medium translation
    hf_base_medium_translate_result = transcribe_hf_whisper_base(audio_file, "medium", "translate")

    # Run hf whisper base large-v3 transcription
    hf_base_large_transcribe_result = transcribe_hf_whisper_base(audio_file, "large-v3", "transcribe")

    # Run hf whisper base large-v3 translation
    hf_base_large_translate_result = transcribe_hf_whisper_base(audio_file, "large-v3", "translate")

    # Run wav2vec2 transcription
    wav2vec2_transcribe_result = transcribe_wav2vec2(audio_file)
    
    # Save results to text files alongside the audio file in DONE_DIR
    base_name_no_ext = os.path.splitext(base_name)[0]
    
    # Move audio file to done directory
    done_audio_path = os.path.join(DONE_DIR, base_name)
    shutil.move(audio_file, done_audio_path)
    
    # Save transformer result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_transformer.txt"), 'w') as f:
       f.write(hf_finetuned_medium_transcribe_result)

    # Save transformer translation
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_transformer_translation.txt"), 'w') as f:
       f.write(hf_finetuned_medium_translate_result)
    
    # Save whisper result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_whisper.txt"), 'w') as f:
       f.write(openai_large_transcribe_result)
    
    # Save whisper translation
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_whisper_translation.txt"), 'w') as f:
       f.write(openai_large_translate_result)

    # Save hf whisper base medium result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_hf_base_medium.txt"), 'w') as f:
       f.write(hf_base_medium_transcribe_result)
    
    # Save hf whisper base medium translation
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_hf_base_medium_translation.txt"), 'w') as f:
       f.write(hf_base_medium_translate_result)

    # Save hf whisper base large result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_hf_base_large.txt"), 'w') as f:
       f.write(hf_base_large_transcribe_result)

    # Save hf whisper base large translation
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_hf_base_large_translation.txt"), 'w') as f:
       f.write(hf_base_large_translate_result)
    
    # Save wav2vec2 result
    with open(os.path.join(DONE_DIR, f"{base_name_no_ext}_wav2vec2.txt"), 'w') as f:
        f.write(wav2vec2_transcribe_result)
    
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
                # process_audio_file(audio_files[0])
                print("Processed one file. Waiting 30 seconds before checking for more...")
            else:
                print("No audio files found. Waiting...")
            
            # Sleep before checking again
            sleep(30)
            
    except Exception as e:
        print(f"Error in scribe_timer: {str(e)}")
        raise e
