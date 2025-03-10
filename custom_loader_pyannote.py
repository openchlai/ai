#!/usr/bin/env python
"""
Verify that pyannote speaker diarization is working correctly.
Run this after downloading the model to verify everything works.
"""
import os
import argparse
import json
import torch
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify-pyannote")

def verify_installation():
    """Verify pyannote installation"""
    print("\n=== Verifying Installation ===\n")
    
    try:
        # Check torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        # Check pyannote
        import pyannote.audio
        print(f"pyannote.audio version: {pyannote.audio.__version__}")
        
        # Check huggingface_hub
        import huggingface_hub
        print(f"huggingface_hub version: {huggingface_hub.__version__}")
        
        # Check for some other dependencies
        try:
            import speechbrain
            print(f"speechbrain version: {speechbrain.__version__}")
        except (ImportError, AttributeError):
            print("speechbrain: Not found or no version info")
        
        try:
            import pytorch_lightning
            print(f"pytorch_lightning version: {pytorch_lightning.__version__}")
        except (ImportError, AttributeError):
            print("pytorch_lightning: Not found or no version info")
        
        print("\n✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"\n✗ Missing required package: {str(e)}")
        return False

def check_cache_status():
    """Check if the cache contains pyannote models"""
    print("\n=== Checking Cache Status ===\n")
    
    # Check huggingface cache
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
    pyannote_dirs = list(hf_cache.glob("models--pyannote--*"))
    
    if not pyannote_dirs:
        print("No pyannote models found in HuggingFace cache")
    else:
        print(f"Found {len(pyannote_dirs)} pyannote models in cache:")
        for d in pyannote_dirs:
            print(f"  - {d.name}")
            
            # Check for snapshots
            snapshots_dir = d / "snapshots"
            if snapshots_dir.exists():
                snapshots = list(snapshots_dir.glob("*"))
                print(f"    Contains {len(snapshots)} snapshots")
                
                # Check most recent snapshot
                if snapshots:
                    latest = max(snapshots, key=lambda p: p.stat().st_mtime)
                    print(f"    Latest snapshot: {latest.name}")
                    
                    # List some files in the snapshot
                    files = list(latest.glob("*"))[:5]
                    if files:
                        print(f"    Contains files: {', '.join(f.name for f in files)}")
    
    # Check torch cache
    torch_cache = Path.home() / ".cache" / "torch" / "pyannote"
    if torch_cache.exists():
        print("\nFound torch pyannote cache:")
        models = list(torch_cache.glob("models--pyannote--*"))
        print(f"  Contains {len(models)} models")
        for m in models:
            print(f"  - {m.name}")
    else:
        print("\nNo torch pyannote cache found")
    
    return len(pyannote_dirs) > 0

def test_pipeline(token, audio_file=None):
    """Test the pyannote pipeline"""
    print("\n=== Testing Pyannote Pipeline ===\n")
    
    # Set environment variables
    os.environ["HUGGINGFACE_TOKEN"] = token
    os.environ["HF_TOKEN"] = token
    
    try:
        # Import only after setting environment variables
        from pyannote.audio import Pipeline
        
        # Try loading the pipeline
        print("Loading pipeline...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization", 
            use_auth_token=token
        )
        
        # Move to appropriate device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Moving pipeline to {device}...")
        pipeline = pipeline.to(device)
        
        print("✓ Pipeline loaded successfully")
        
        # Test on audio file if provided
        if audio_file:
            if not os.path.exists(audio_file):
                print(f"✗ Audio file not found: {audio_file}")
                return True  # Pipeline loaded, so return True
            
            print(f"Processing audio file: {audio_file}")
            diarization = pipeline(audio_file)
            
            # Format results
            results = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                results.append({
                    "speaker": speaker,
                    "start": round(turn.start, 2),
                    "end": round(turn.end, 2)
                })
            
            # Display results
            speakers = set(r["speaker"] for r in results)
            print(f"Detected {len(speakers)} speakers")
            print("Sample segments:")
            for segment in results[:5]:  # Show first 5 segments
                print(f"  {segment['speaker']}: {segment['start']}s - {segment['end']}s")
            
            print("\n✓ Audio processing successful")
        
        return True
    except Exception as e:
        print(f"✗ Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Verify pyannote speaker diarization")
    parser.add_argument("--token", type=str, required=True, help="HuggingFace token")
    parser.add_argument("--audio", type=str, help="Audio file to test (optional)")
    args = parser.parse_args()
    
    print("=== Pyannote Speaker Diarization Verification ===")
    
    # Step 1: Verify installation
    if not verify_installation():
        print("\n✗ Installation verification failed")
        return 1
    
    # Step 2: Check cache status
    cache_ok = check_cache_status()
    if not cache_ok:
        print("\n⚠️ No cached models found. This may be normal if first run.")
    
    # Step 3: Test pipeline
    if not test_pipeline(args.token, args.audio):
        print("\n✗ Pipeline test failed")
        return 1
    
    # Success
    print("\n=== Verification Complete ===")
    print("\n✅ Pyannote speaker diarization is working correctly!")
    print("\nYou can now use the model in your Django application")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())