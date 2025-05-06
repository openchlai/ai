#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Install git-lfs for model management
if ! command -v git-lfs &> /dev/null; then
    echo "Installing git-lfs..."
    apt-get update && apt-get install -y git-lfs || {
        echo "Cannot install git-lfs with apt. Please install manually."
    }
fi

# Create directories for models and logs
mkdir -p wav2vec2-swahili-finetuned/logs
mkdir -p wav2vec2-swahili-finetuned/checkpoints

# Download a small test file to verify audio processing works
wget -O test_audio.wav https://github.com/mozilla/DeepSpeech/raw/master/data/smoke_test/speech_recognition.wav || echo "Could not download test file, but training can still proceed."

echo "Setup complete! You can now run the training script."
