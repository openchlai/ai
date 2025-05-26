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
import librosa
import shutil
from time import time, sleep
import whisper
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Add the parent directory to the path to import the translation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from translate.translation import translate_file
from . import util_code as utils


# Paths
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets", "audio")
DONE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets", "audio_done4")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets", "case_data")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://backend.bitz-itc.com/api/webhook/webform/")
ALTERNATE_WEBHOOK_URL = os.getenv("ALTERNATE_WEBHOOK_URL", "https://demo-openchs.bitz-itc.com/helpline/api/cases/")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "kg6ja8o3llqnhccb3ngo1e1p4s")

# Ensure necessary directories exist
def ensure_dirs():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_case_data(case_data: Dict[str, Any], audio_filename: str) -> str:
    """Save case data to JSON file with timestamp."""
    print("Saving case data")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(audio_filename))[0]
        output_filename = f"case_{timestamp}_{base_name}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)
        
        print(f"Case data saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Failed to save case data: {str(e)}")
        traceback.print_exc()
        raise RuntimeError(f"Failed to save case data: {str(e)}")

def post_to_webhook(case_data: Dict[str, Any], endpoint_type: str="simple") -> Optional[requests.Response]:
    """Post the case data to the appropriate webhook endpoint."""
    print(f"Posting {endpoint_type} case data to webhook")
    
    if not WEBHOOK_TOKEN:
        print("No webhook token provided. Set WEBHOOK_TOKEN environment variable.")
        return None
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {WEBHOOK_TOKEN}"
        }
        
        url = WEBHOOK_URL if endpoint_type == "simple" else ALTERNATE_WEBHOOK_URL
        data = case_data["simple_case"] if endpoint_type == "simple" else case_data["detailed_case"]
        
        # Try posting once without retries
        try:
            with requests.Session() as session:
                response = session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=30
                )
            
            print(f"Webhook response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"Successfully posted to {url}")
                print(f"Response body: {response.text[:500]}")  # Print first 500 chars of response
                return response
            else:
                print(f"Post failed with status {response.status_code}")
                print(f"Response body: {response.text[:500]}")  # Print first 500 chars of response
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Webhook request failed with exception: {str(e)}")
            return None
        
    except Exception as e:
        print(f"Webhook post failed: {str(e)}")
        traceback.print_exc()
        return None

# def get_segment_confidence(segment):
    """
    Calculate confidence score for a segment based on token probabilities.
    
    Args:
        segment: A segment from Whisper's result containing tokens and their probabilities
        
    Returns:
        float: Average confidence score for the segment
    """
    # if hasattr(segment, 'avg_logprob'):
        # Convert log probability to confidence score (0-1 range)
        # Higher log probability (closer to 0) means higher confidence
       # confidence = np.exp(min(0, segment.avg_logprob))  # Convert log prob to probability
         # return confidence
    # return None

def transcribe_audio(audio_path):
    """
    Transcribe audio using OpenAI's Whisper large model.
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        
    Returns:
        str: The transcription text
    """
    print(f"Starting OpenAI Whisper Large transcription for: {audio_path}")
    
    try:
        # Load the Whisper model
        model_id = "large-v3"
        print(f"Loading Whisper model: {model_id}")
        model = whisper.load_model(model_id)
        
        start_time = int(time())
        audio_length = librosa.get_duration(path=audio_path)
        print(f"Audio length: {audio_length:.2f} seconds")
        
        # Use transcribe method to process the entire audio file
        result = model.transcribe(
            audio_path,
            task="transcribe",
        )
        
        # Get the transcription text
        transcription_text = result["text"]
        
        # Clean up the transcription text
        transcription_text = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", transcription_text)  # Remove unwanted symbols
        transcription_text = re.sub(r"\s+", " ", transcription_text).strip()  # Clean spaces
        
	# Process segments and extract confidence scores
        # segments_with_confidence = []
        # for segment in result["segments"]:
    		# Calculate confidence for this segment
          #      confidence = get_segment_confidence(segment)
    
    		# Add segment with confidence to our list
           #     segments_with_confidence.append({
        #		"id": segment["id"],
        #		"start": segment["start"],
       	#		"end": segment["end"],
        #		"text": segment["text"],
        #		"confidence": confidence
    	#	})

        # Get the end time
        end_time = int(time())
        
        # Calculate processing time in seconds
        processing_time = end_time - start_time
        
        print(f"Processing time: {processing_time} seconds")
        print("\n🚀 **Whisper Transcription Result:**")
        print(transcription_text)
        
        result2 = model.transcribe(
            audio_path,
            task="translate",
        )
        translation_text = result2["text"]
        
        # Clean up the transcription text
        translation_text = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", translation_text)  # Remove unwanted symbols
        translation_text = re.sub(r"\s+", " ", translation_text).strip()  # Clean spaces
        end_time = int(time())
        
        # Calculate processing time in seconds
        processing_time = end_time - start_time
        
        print(f"Processing time: {processing_time} seconds")
        print("\n🚀 **Whisper Translation Result:**")
        print(translation_text)
        
	# Print sample confidence scores
        # print("\n📊 **Sample Confidence Scores:**")
        # for i, segment in enumerate(segments_with_confidence[:3]):  # Show first 3 segments
          #  print(f"Segment {i+1}: {segment['text']} (Confidence: {segment['confidence']:.4f})")
        # Clean up model
        del model
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Explicitly clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return transcription_text
        
    except Exception as e:
        print(f"Error in Whisper transcription: {str(e)}")
        traceback.print_exc()
        
        # Enhanced cleanup in case of error
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        return f"ERROR: {str(e)}", None

def find_audio_file():
    """
    Find the first audio file in the AUDIO_DIR.
    
    Returns:
        str: Path to the audio file or None if no file is found
    """
    audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav")) + \
                  glob.glob(os.path.join(AUDIO_DIR, "*.mp3")) + \
                  glob.glob(os.path.join(AUDIO_DIR, "*.ogg")) + \
                  glob.glob(os.path.join(AUDIO_DIR, "*.flac"))
    
    if audio_files:
        return audio_files[0]
    return None

def process_audio_file(audio_file):
    """
    Process a single audio file: transcribe, save to file, and translate.
    
    Args:
        audio_file (str): Path to the audio file to process
    """
    base_name = os.path.basename(audio_file)
    print(f"\n==== Processing file: {base_name} ====")
    
    # Transcribe the audio
    # Transcribe the audio and get confidence scores
    transcription = transcribe_audio(audio_file)
    print(transcription)
    
    # Save transcription to file
    base_name_no_ext = os.path.splitext(base_name)[0]
    
    # Move audio file to done directory
    done_audio_path = os.path.join(DONE_DIR, base_name)
    shutil.move(audio_file, done_audio_path)
    
    # Save transcription result
    transcription_file = os.path.join(DONE_DIR, f"{base_name_no_ext}_whisper.txt")
    with open(transcription_file, 'w', encoding='utf-8') as f:
        f.write(transcription)
        
    print(f"Transcription saved to: {transcription_file}")
    
    # Translate the transcription
    translation_file = os.path.join(DONE_DIR, f"{base_name_no_ext}_NLLB_translation.txt")
    print(f"Translating transcription to English...")
    translate_file(
        transcription_file,           # Input file path
        translation_file,             # Output file path
        src_lang=None,                # None to enable auto-detection (don't need to specify this parameter)
        tgt_lang="eng_Latn",          # Default target is English
        max_length=512,               # Max output sequence length
        auto_detect=True,             # Enable language auto-detection
        max_chunk_tokens=250,         # Smaller chunk size to prevent repetition issues
        overlap_tokens=50,            # Add overlap between chunks for better coherence
        num_beams=4                   # Use beam search for higher quality translations
    )
        
    # Save detailed result with confidence scores
#    if segments_with_confidence:
 #       confidence_file = os.path.join(DONE_DIR, f"{base_name_no_ext}_whisper_confidence.json")
  #      with open(confidence_file, 'w', encoding='utf-8') as f:
   #         json.dump(segments_with_confidence, f, indent=2)
    #    print(f"Confidence scores saved to: {confidence_file}")
    # Generate case data
    
    # Read the translated text
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translated_text = f.read()
    except Exception as e:
        print(f"Error reading translation file: {e}")
        translated_text = ""
    print(f"NLLB Translated text: {translated_text}")

    case_data = utils.generate_case_data(transcription) 
    print(case_data)
    
    # Save case data to JSON file
    try:
        save_case_data(case_data, base_name)
    except Exception as e:
        print(f"Error saving case data: {str(e)}")
    
    # Post to webhooks
    try:
        # Post simple case data
        simple_response = post_to_webhook(case_data, endpoint_type="simple")
        if simple_response:
            print("Simple case data posted successfully")
        
        # Post detailed case data
        detailed_response = post_to_webhook(case_data, endpoint_type="detailed")
        if detailed_response:
            print("Detailed case data posted successfully")
    except Exception as e:
        print(f"Error posting to webhook: {str(e)}")

    
    # print(f"Translation saved to: {translation_file}")
    print(f"Completed processing: {base_name}")
    print(f"File moved to: {done_audio_path}")
    print("==== Processing complete ====\n")

def scribe_timer(data=False):
    """
    Main timer function that continuously checks for audio files and processes them.
    
    Args:
        data (bool): Whether to return data instead of printing (not used in this implementation)
    """
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
        traceback.print_exc()
        raise e

def main():
    """
    Main function to find an audio file and transcribe it.
    """
    ensure_dirs()
    
    audio_file = find_audio_file()
    if audio_file:
        print(f"Found audio file: {audio_file}")
        process_audio_file(audio_file)
        return True
    else:
        print("No audio files found.")
        return False

if __name__ == "__main__":
    # Check if we should run in timer mode
    if len(sys.argv) > 1 and sys.argv[1] == "--timer":
        scribe_timer()
    else:
        main()
