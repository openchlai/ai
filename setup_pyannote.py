# setup_pyannote.py
"""
Script to set up Django settings for pyannote diarization.
Run this script to add the necessary settings to your Django settings file.
"""
import os
import sys
import argparse
from pathlib import Path

def find_settings_file():
    """Find Django settings.py file"""
    # Try to find settings.py in common locations
    potential_paths = [
        Path.cwd() / "settings.py",
        Path.cwd() / "config" / "settings.py",
        Path.cwd() / "project" / "settings.py",
        Path.cwd() / "app" / "settings.py"
    ]
    
    # If this is run from a Django project, use Django's mechanisms
    try:
        from django.conf import settings
        return Path(settings.BASE_DIR) / "settings.py"
    except:
        pass
    
    # Look for settings files manually
    for path in potential_paths:
        if path.exists():
            return path
    
    return None

def add_huggingface_token(settings_path, token):
    """Add Hugging Face token to settings file"""
    if not settings_path.exists():
        print(f"Error: Settings file not found at {settings_path}")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Check if token already exists
    if f"HUGGINGFACE_TOKEN = " in content:
        print("HUGGINGFACE_TOKEN already exists in settings")
        # Update the token value
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("HUGGINGFACE_TOKEN = "):
                lines[i] = f'HUGGINGFACE_TOKEN = "{token}"'
                with open(settings_path, 'w') as f:
                    f.write('\n'.join(lines))
                print(f"Updated HUGGINGFACE_TOKEN in {settings_path}")
                return True
    
    # Add token to the end of the file
    with open(settings_path, 'a') as f:
        f.write(f'\n\n# Hugging Face settings\nHUGGINGFACE_TOKEN = "{token}"\n')
    
    print(f"Added HUGGINGFACE_TOKEN to {settings_path}")
    return True

def configure_environment_variable(token):
    """Configure token as environment variable"""
    # Determine the appropriate shell rc file
    home = Path.home()
    shell_rc_files = [
        home / ".bashrc",
        home / ".zshrc",
        home / ".profile"
    ]
    
    # Find the first existing rc file
    rc_file = None
    for f in shell_rc_files:
        if f.exists():
            rc_file = f
            break
    
    if not rc_file:
        print("Could not find a shell RC file. Will not add environment variable.")
        return False
    
    # Check if the token is already in the file
    with open(rc_file, 'r') as f:
        content = f.read()
    
    if f"HUGGINGFACE_TOKEN={token}" in content:
        print(f"Environment variable already set in {rc_file}")
        return True
    
    # Add token to rc file
    with open(rc_file, 'a') as f:
        f.write(f'\n# Hugging Face token for pyannote\nexport HUGGINGFACE_TOKEN="{token}"\n')
    
    print(f"Added HUGGINGFACE_TOKEN to {rc_file}")
    print("You'll need to restart your shell or run 'source ~/.bashrc' for the environment variable to take effect")
    return True

def test_token_works():
    """Test if the token works with pyannote"""
    print("\nTesting token with pyannote...")
    
    try:
        import torch
        from huggingface_hub import login
        
        login(token=os.environ.get("HUGGINGFACE_TOKEN"))
        
        # Try to access the model
        from pyannote.audio import Pipeline
        
        Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=os.environ.get("HUGGINGFACE_TOKEN")
        )
        
        print("✅ Token is working correctly with pyannote!")
        return True
    except Exception as e:
        print(f"❌ Error testing token: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Set up Django settings for pyannote diarization")
    parser.add_argument("--token", type=str, required=True, help="Hugging Face token")
    parser.add_argument("--settings", type=str, help="Path to Django settings.py (optional)")
    parser.add_argument("--env-only", action="store_true", help="Only set environment variable, don't modify settings.py")
    parser.add_argument("--skip-test", action="store_true", help="Skip testing if the token works")
    args = parser.parse_args()
    
    print("=== Setting up pyannote for Django ===\n")
    
    # Temporarily set environment variable for testing
    os.environ["HUGGINGFACE_TOKEN"] = args.token
    
    # Set up environment variable
    configure_environment_variable(args.token)
    
    # Set up Django settings
    if not args.env_only:
        settings_path = args.settings
        if not settings_path:
            settings_path = find_settings_file()
            if not settings_path:
                print("Could not find Django settings.py file. Please specify with --settings")
                return 1
        
        add_huggingface_token(Path(settings_path), args.token)
    
    # Test token
    if not args.skip_test:
        test_token_works()
    
    print("\nSetup complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())