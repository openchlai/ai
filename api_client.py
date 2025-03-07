#!/usr/bin/env python
# api_client.py - Example client for using the Audio Processing API

import requests
import json
import time
import argparse
import os

class AudioProcessingClient:
    """
    Client for interacting with the Audio Processing API.
    """
    def __init__(self, base_url="http://localhost:8000/api/audio"):
        self.base_url = base_url
    
    def preprocess_audio(self, audio_path, noise_reduction=0.3, normalize=True):
        """
        Submit an audio file for preprocessing.
        
        Parameters:
        -----------
        audio_path : str
            Path to the audio file
        noise_reduction : float
            Strength of noise reduction (0.0 to 1.0)
        normalize : bool
            Whether to normalize the audio
            
        Returns:
        --------
        dict
            Response from the API
        """
        endpoint = f"{self.base_url}/preprocess/"
        
        payload = {
            "audio_path": audio_path,
            "noise_reduction": noise_reduction,
            "normalize": normalize
        }
        
        response = requests.post(endpoint, json=payload)
        return response.json()
    
    def diarize_speakers(self, audio_path, min_speakers=2, max_speakers=2):
        """
        Submit an audio file for speaker diarization.
        
        Parameters:
        -----------
        audio_path : str
            Path to the audio file
        min_speakers : int
            Minimum number of speakers to expect
        max_speakers : int
            Maximum number of speakers to expect
            
        Returns:
        --------
        dict
            Response from the API
        """
        endpoint = f"{self.base_url}/diarize/"
        
        payload = {
            "audio_path": audio_path,
            "min_speakers": min_speakers,
            "max_speakers": max_speakers
        }
        
        response = requests.post(endpoint, json=payload)
        return response.json()
    
    def chunk_audio(self, audio_path, diarization_result=None, max_length=10.0, 
                   overlap=2.0, min_chunk=1.0):
        """
        Submit an audio file for chunking.
        
        Parameters:
        -----------
        audio_path : str
            Path to the audio file
        diarization_result : str
            Path to diarization result JSON file (optional)
        max_length : float
            Maximum chunk duration in seconds
        overlap : float
            Overlap duration in seconds
        min_chunk : float
            Minimum chunk duration in seconds
            
        Returns:
        --------
        dict
            Response from the API
        """
        endpoint = f"{self.base_url}/chunk/"
        
        payload = {
            "audio_path": audio_path,
            "max_length": max_length,
            "overlap": overlap,
            "min_chunk": min_chunk
        }
        
        if diarization_result:
            payload["diarization_result"] = diarization_result
        
        response = requests.post(endpoint, json=payload)
        return response.json()
    
    def get_task_status(self, task_id):
        """
        Get the status of a task.
        
        Parameters:
        -----------
        task_id : str
            ID of the task
            
        Returns:
        --------
        dict
            Task status details
        """
        endpoint = f"{self.base_url}/status/{task_id}/"
        
        response = requests.get(endpoint)
        return response.json()
    
    def wait_for_completion(self, task_id, check_interval=5, timeout=None):
        """
        Wait for a task to complete.
        
        Parameters:
        -----------
        task_id : str
            ID of the task
        check_interval : int
            Interval in seconds between status checks
        timeout : int or None
            Maximum time to wait in seconds (None for no timeout)
            
        Returns:
        --------
        dict
            Task result
        """
        start_time = time.time()
        while True:
            result = self.get_task_status(task_id)
            
            if result.get('status') in ['completed', 'failed']:
                return result
            
            # Check if timeout reached
            if timeout and (time.time() - start_time > timeout):
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            # Wait before checking again
            time.sleep(check_interval)
    
    def process_audio_pipeline(self, audio_path, output_prefix=None):
        """
        Process an audio file through the entire pipeline:
        1. Preprocess
        2. Diarize
        3. Chunk
        
        Parameters:
        -----------
        audio_path : str
            Path to the audio file
        output_prefix : str or None
            Prefix for output directory names
            
        Returns:
        --------
        dict
            Results from each processing step
        """
        results = {}
        
        # 1. Preprocess
        print("Starting audio preprocessing...")
        preprocess_response = self.preprocess_audio(audio_path)
        task_id = preprocess_response.get('task_id')
        
        if not task_id:
            raise ValueError(f"Failed to start preprocessing: {preprocess_response}")
        
        print(f"Preprocessing task started (ID: {task_id})")
        preprocess_result = self.wait_for_completion(task_id)
        
        if preprocess_result.get('status') != 'completed':
            raise ValueError(f"Preprocessing failed: {preprocess_result}")
        
        processed_audio_path = preprocess_result.get('output_path')
        print(f"Preprocessing completed: {processed_audio_path}")
        results['preprocessing'] = preprocess_result
        
        # 2. Diarize
        print("Starting speaker diarization...")
        diarize_response = self.diarize_speakers(processed_audio_path)
        task_id = diarize_response.get('task_id')
        
        if not task_id:
            raise ValueError(f"Failed to start diarization: {diarize_response}")
        
        print(f"Diarization task started (ID: {task_id})")
        diarize_result = self.wait_for_completion(task_id)
        
        if diarize_result.get('status') != 'completed':
            raise ValueError(f"Diarization failed: {diarize_result}")
        
        diarization_json = diarize_result.get('diarization_json')
        print(f"Diarization completed: {diarization_json}")
        results['diarization'] = diarize_result
        
        # 3. Chunk
        print("Starting audio chunking...")
        chunk_response = self.chunk_audio(processed_audio_path, diarization_json)
        task_id = chunk_response.get('task_id')
        
        if not task_id:
            raise ValueError(f"Failed to start chunking: {chunk_response}")
        
        print(f"Chunking task started (ID: {task_id})")
        chunk_result = self.wait_for_completion(task_id)
        
        if chunk_result.get('status') != 'completed':
            raise ValueError(f"Chunking failed: {chunk_result}")
        
        chunks_dir = chunk_result.get('output_dir')
        chunk_count = chunk_result.get('chunk_count', 0)
        print(f"Chunking completed: {chunk_count} chunks created in {chunks_dir}")
        results['chunking'] = chunk_result
        
        return results

def main():
    """Main function for the command-line client."""
    parser = argparse.ArgumentParser(description="Audio Processing API Client")
    parser.add_argument("--server", default="http://localhost:8000/api/audio", 
                      help="API server URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Preprocess command
    preprocess_parser = subparsers.add_parser("preprocess", help="Preprocess audio")
    preprocess_parser.add_argument("audio_path", help="Path to the audio file")
    preprocess_parser.add_argument("--noise-reduction", type=float, default=0.3,
                                help="Noise reduction strength (0.0-1.0)")
    
    # Diarize command
    diarize_parser = subparsers.add_parser("diarize", help="Perform speaker diarization")
    diarize_parser.add_argument("audio_path", help="Path to the audio file")
    diarize_parser.add_argument("--min-speakers", type=int, default=2,
                               help="Minimum number of speakers")
    diarize_parser.add_argument("--max-speakers", type=int, default=2,
                               help="Maximum number of speakers")
    
    # Chunk command
    chunk_parser = subparsers.add_parser("chunk", help="Chunk audio")
    chunk_parser.add_argument("audio_path", help="Path to the audio file")
    chunk_parser.add_argument("--diarization-result", help="Path to diarization JSON")
    chunk_parser.add_argument("--max-length", type=float, default=10.0,
                            help="Maximum chunk length in seconds")
    chunk_parser.add_argument("--overlap", type=float, default=2.0,
                            help="Overlap between chunks in seconds")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check task status")
    status_parser.add_argument("task_id", help="Task ID")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", 
                                          help="Run full preprocessing pipeline")
    pipeline_parser.add_argument("audio_path", help="Path to the audio file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create client
    client = AudioProcessingClient(args.server)
    
    # Handle commands
    if args.command == "preprocess":
        response = client.preprocess_audio(
            args.audio_path,
            noise_reduction=args.noise_reduction
        )
        task_id = response.get('task_id')
        print(f"Preprocessing task started (ID: {task_id})")
        result = client.wait_for_completion(task_id)
        print(json.dumps(result, indent=2))
        
    elif args.command == "diarize":
        response = client.diarize_speakers(
            args.audio_path,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers
        )
        task_id = response.get('task_id')
        print(f"Diarization task started (ID: {task_id})")
        result = client.wait_for_completion(task_id)
        print(json.dumps(result, indent=2))
        
    elif args.command == "chunk":
        response = client.chunk_audio(
            args.audio_path,
            diarization_result=args.diarization_result,
            max_length=args.max_length,
            overlap=args.overlap
        )
        task_id = response.get('task_id')
        print(f"Chunking task started (ID: {task_id})")
        result = client.wait_for_completion(task_id)
        print(json.dumps(result, indent=2))
        
    elif args.command == "status":
        result = client.get_task_status(args.task_id)
        print(json.dumps(result, indent=2))
        
    elif args.command == "pipeline":
        results = client.process_audio_pipeline(args.audio_path)
        print("\nPipeline completed successfully!")
        print(f"Chunks directory: {results['chunking'].get('output_dir')}")
        print(f"Total chunks: {results['chunking'].get('chunk_count', 0)}")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()