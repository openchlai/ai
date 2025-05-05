# Voice Recognition

This directory contains models and utilities for speech recognition within child protection case management.

## Purpose

The voice recognition module provides capabilities to:
- Transcribe case worker audio recordings to text
- Support multilingual speech recognition for diverse communities
- Enable voice-based entry of case notes in field settings
- Identify key terms and urgency indicators in spoken reports
- Assist in documenting child interviews with minimal disruption

## Structure

- `audio_processing.py`: Audio preprocessing and feature extraction utilities
- `model.py`: Core speech recognition model implementation
- Future additions will include specialized acoustic models and keyword detection

## Setup

```bash
# Install required dependencies
pip install -r requirements.txt

# Download pre-trained acoustic models
python download_acoustic_models.py --languages "en,fr,es,sw"

# Optional: Install GPU acceleration libraries
pip install -r requirements-gpu.txt
```

## Usage

### Basic Transcription

```python
from voice_recognition.model import SpeechRecognizer

# Initialize recognizer
recognizer = SpeechRecognizer(language="en")

# Transcribe audio file
transcript = recognizer.transcribe("case_interview.wav")
print(f"Transcript: {transcript}")
```

### Real-time Recognition

```python
from voice_recognition.model import RealtimeRecognizer
from voice_recognition.audio_processing import AudioStream

# Setup real-time recognition
recognizer = RealtimeRecognizer(language="en")
audio_stream = AudioStream()

# Start recognition session
recognizer.start_session()

# Process audio in chunks (simplified example)
for audio_chunk in audio_stream.capture():
    text_segment = recognizer.process_chunk(audio_chunk)
    if text_segment:
        print(f"Recognized: {text_segment}")

# End session
recognizer.end_session()
```

## Development Guidelines

When working with voice recognition models:

1. Prioritize accuracy for child protection terminology
2. Test with diverse accents and speaking styles
3. Implement privacy safeguards for sensitive audio recordings
4. Consider environmental challenges (background noise, field conditions)
5. Ensure clear indicators of confidence levels in transcriptions

## Evaluation

```bash
# Evaluate recognition accuracy
python evaluate.py --model standard --language en --test-set field_recordings.csv

# Test with background noise
python evaluate_noise.py --model standard --noise-level medium
```

## Special Considerations

Speech recognition in child protection contexts requires:

- Enhanced privacy and security for sensitive audio
- Specialized vocabulary for child protection terms
- Support for hesitant or emotionally affected speech
- Capability to flag potentially urgent situations
- Accommodations for children's speech patterns

