# Whisper Medium Swahili Fine-tuned Model

A fine-tuned OpenAI Whisper Medium model specialized for Swahili speech recognition, trained on CommonVoice Swahili dataset.

## Model Overview

- **Base Model**: OpenAI Whisper Medium
- **Fine-tuned For**: Swahili (sw) speech recognition
- **Training Dataset**: CommonVoice Swahili
- **Model Type**: Speech-to-Text (ASR)
- **Supported Languages**: Swahili (primary), English (secondary)

## Directory Structure

```
whisper-medium-sw-3/
├── checkpoint-1000/          # Training checkpoint at step 1000
├── checkpoint-2000/          # Training checkpoint at step 2000
├── checkpoint-3000/          # Training checkpoint at step 3000
├── checkpoint-4000/          # Training checkpoint at step 4000
├── checkpoint-5000/          # Training checkpoint at step 5000
├── checkpoint-6000/          # Training checkpoint at step 6000 (latest)
├── added_tokens.json         # Additional tokens added during fine-tuning
├── merges.txt               # BPE merges file
├── normalizer.json          # Text normalization configuration
├── preprocessor_config.json # Audio preprocessing configuration
├── special_tokens_map.json  # Special tokens mapping
├── tokenizer_config.json    # Tokenizer configuration
├── vocab.json              # Vocabulary file
└── runs/                   # TensorBoard training logs
```

Each checkpoint contains:
- `config.json` - Model configuration
- `generation_config.json` - Generation parameters
- `model.safetensors` - Model weights
- `preprocessor_config.json` - Audio preprocessing config
- Training state files (optimizer, scheduler, etc.)

## Requirements

### Python Dependencies

```bash
pip install torch transformers librosa soundfile accelerate
```

### Required Libraries

```python
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
import time
import re
import gc
```

## Usage

### Basic Usage

```python
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
import os

def get_latest_checkpoint(model_path):
    """Get the latest checkpoint from the model directory"""
    checkpoints = [d for d in os.listdir(model_path) if d.startswith('checkpoint-')]
    if not checkpoints:
        return None
    latest = max(checkpoints, key=lambda x: int(x.split('-')[1]))
    return os.path.join(model_path, latest)

def transcribe_audio(audio_path, model_path, task="transcribe"):
    """
    Transcribe audio using the fine-tuned Whisper model
    
    Args:
        audio_path (str): Path to audio file
        model_path (str): Path to model directory
        task (str): "transcribe" or "translate"
    
    Returns:
        str: Transcribed text
    """
    # Get latest checkpoint
    checkpoint_path = get_latest_checkpoint(model_path)
    if not checkpoint_path:
        checkpoint_path = model_path
    
    print(f"Using checkpoint: {checkpoint_path}")
    
    # Load processor and model
    processor = WhisperProcessor.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)
    
    # Load and preprocess audio
    speech_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)
    
    # Process audio in 30-second chunks
    chunk_size = 30 * 16000  # 30 seconds at 16kHz
    transcriptions = []
    
    model.eval()
    model.generation_config.forced_decoder_ids = None
    
    for i in range(0, len(speech_array), chunk_size):
        chunk = speech_array[i:i + chunk_size]
        
        if len(chunk) < 1600:  # Skip very short chunks
            continue
            
        # Process chunk
        inputs = processor.feature_extractor(
            chunk, sampling_rate=16000, return_tensors="pt"
        )
        input_features = inputs.input_features.to(device)
        
        # Generate transcription
        with torch.no_grad():
            predicted_ids = model.generate(
                input_features,
                max_length=225,
                num_beams=5,
                temperature=0.7,
                repetition_penalty=1.5,
                task=task,
            )
        
        # Decode transcription
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        transcription = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", transcription)
        transcription = re.sub(r"\s+", " ", transcription).strip()
        
        transcriptions.append(transcription)
    
    # Cleanup
    del model, processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return " ".join(transcriptions)

# Example usage
model_path = "./whisper-medium-sw-3"
audio_file = "path/to/your/audio.wav"
result = transcribe_audio(audio_file, model_path)
print(result)
```

### Advanced Usage with Language Detection

```python
def transcribe_with_language_detection(audio_path, model_path, task="transcribe"):
    """Enhanced transcription with language detection"""
    
    # Swahili and English word lists for detection
    swahili_words = ["na", "kwa", "ya", "wa", "ni", "za", "kuwa", "kutoka", "sasa", "hivyo"]
    english_words = ["the", "and", "of", "to", "in", "is", "that", "for", "with", "this"]
    
    checkpoint_path = get_latest_checkpoint(model_path)
    processor = WhisperProcessor.from_pretrained(model_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = WhisperForConditionalGeneration.from_pretrained(checkpoint_path).to(device)
    
    speech_array, _ = librosa.load(audio_path, sr=16000, mono=True)
    chunk_size = 30 * 16000
    
    transcriptions = []
    language_counts = {"sw": 0, "en": 0}
    
    model.eval()
    
    for i in range(0, len(speech_array), chunk_size):
        chunk = speech_array[i:i + chunk_size]
        if len(chunk) < 1600:
            continue
            
        inputs = processor.feature_extractor(chunk, sampling_rate=16000, return_tensors="pt")
        
        with torch.no_grad():
            predicted_ids = model.generate(
                inputs.input_features.to(device),
                max_length=225,
                num_beams=5,
                temperature=0.7,
                repetition_penalty=1.5,
                task=task,
            )
        
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        transcription = re.sub(r"[^a-zA-Z0-9\s.,?!]", "", transcription)
        transcription = re.sub(r"\s+", " ", transcription).strip()
        
        # Language detection
        words = transcription.lower().split()
        sw_count = sum(1 for word in words if word in swahili_words)
        en_count = sum(1 for word in words if word in english_words)
        
        if sw_count >= en_count:
            language_counts["sw"] += 1
        else:
            language_counts["en"] += 1
            
        transcriptions.append(transcription)
    
    # Determine primary language
    primary_language = "swahili" if language_counts["sw"] >= language_counts["en"] else "english"
    
    result = {
        "transcription": " ".join(transcriptions),
        "primary_language": primary_language,
        "language_distribution": language_counts,
        "audio_duration": len(speech_array) / 16000
    }
    
    # Cleanup
    del model, processor
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return result
```

## Supported Audio Formats

- WAV, MP3, FLAC, M4A, and other common audio formats
- Recommended: 16kHz sampling rate, mono channel
- Maximum chunk length: 30 seconds (automatically handled)

## Model Parameters

- **Max Length**: 225 tokens
- **Beam Search**: 5 beams
- **Temperature**: 0.7
- **Repetition Penalty**: 1.5
- **Sampling Rate**: 16kHz

## Performance Considerations

### GPU Usage
- CUDA support for faster inference
- Automatic memory cleanup after processing
- Suitable for RTX 3060+ or equivalent

### CPU Usage
- Falls back to CPU if CUDA unavailable
- Slower processing but functional
- Recommended: 8GB+ RAM

## Tasks Supported

1. **transcribe**: Convert speech to text in the same language
2. **translate**: Convert speech to English text

## Language Detection

The model includes built-in language detection between Swahili and English based on common word occurrence patterns.

## Training Information

- **Training Steps**: 6000+ steps
- **Checkpoints**: Saved every 1000 steps
- **Base Model**: `openai/whisper-medium`
- **Dataset**: CommonVoice Swahili

## Latest Checkpoint

The model automatically uses the latest checkpoint (currently `checkpoint-6000`). To use a specific checkpoint:

```python
checkpoint_path = "./whisper-medium-sw-3/checkpoint-5000"  # Use step 5000
```

## Troubleshooting

### Memory Issues
- Ensure sufficient GPU/RAM memory
- Process shorter audio files
- Reduce batch size if customizing

### Audio Loading Issues
- Ensure audio file is accessible
- Check supported formats
- Verify librosa installation

### Model Loading Issues
- Verify checkpoint integrity
- Check file permissions
- Ensure transformers library is up-to-date

## License

Please refer to the original Whisper model license and CommonVoice dataset terms for usage rights and restrictions.

## Citation

If you use this model, please cite:
- OpenAI Whisper: [Whisper Paper](https://arxiv.org/abs/2212.04356)
- CommonVoice Dataset: [Mozilla CommonVoice](https://commonvoice.mozilla.org/)
