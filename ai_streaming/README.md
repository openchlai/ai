# AI Streaming - Real-time Audio Transcription Server

This project implements a real-time audio transcription server using OpenAI's Whisper model. It provides streaming speech-to-text capabilities with server-client architecture for processing continuous audio streams.

## Architecture Overview

The system consists of several key components that work together to provide real-time audio transcription:

1. **Audio Processing Pipeline**: Converts raw audio to mel spectrograms
2. **Whisper Model Implementation**: PyTorch-based Whisper model for speech recognition
3. **Streaming Server**: TCP server handling multiple concurrent clients
4. **Tokenization & Decoding**: Text processing and output generation

## File Descriptions

### Core Files

#### `aii_server.py` - TCP Streaming Server
**Purpose**: Main server application that handles real-time audio streaming and transcription.

**Key Features**:
- TCP server listening on port 8300 (127.0.0.1)
- Multi-threaded client handling using Python threading
- Processes 20ms audio chunks (640 bytes of SLIN format)
- Implements sliding window processing (5-second chunks)
- Automatic buffer management and overflow handling
- Single shared model instance across all clients

**How it works**:
- Accepts raw audio data from clients
- Buffers audio in 5-second windows (160,000 bytes)
- Triggers transcription when buffer threshold is reached
- Clears buffer when it reaches 30 seconds (960,000 bytes)
- Prints transcription results with timing information

#### `aii.py` - Core Transcription Engine
**Purpose**: Main transcription logic and model loading functionality.

**Key Components**:
- `load_model()`: Loads Whisper model from disk (currently uses tiny.pt)
- `transcribe()`: Main transcription function handling audio-to-text conversion
- `decode_with_fallback()`: Implements temperature-based fallback decoding
- `segments()`: Splits transcription into time-segmented chunks
- `new_segment()`: Creates individual transcript segments with timestamps

**Configuration**:
- Model: `/usr/src/pt/tiny.pt` (Whisper tiny model)
- Device: Auto-detects CUDA/CPU
- Temperature fallback: 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
- Language: English (but supports multilingual detection)

#### `model.py` - Whisper Model Implementation
**Purpose**: Complete PyTorch implementation of the Whisper architecture.

**Key Classes**:
- `Whisper`: Main model class combining encoder and decoder
- `AudioEncoder`: Processes mel spectrograms into audio features
- `TextDecoder`: Generates text tokens from audio features
- `MultiHeadAttention`: Attention mechanism with optional SDPA support
- `ResidualAttentionBlock`: Transformer blocks for both encoder and decoder
- `ModelDimensions`: Dataclass defining model architecture parameters

**Features**:
- Supports both CPU and GPU inference
- Key-value caching for efficient autoregressive decoding
- Configurable attention mechanisms (SDPA when available)
- Multilingual support detection
- Custom layer implementations (LayerNorm, Linear, Conv1d)

#### `decoding.py` - Decoding Algorithms
**Purpose**: Implements various decoding strategies and token generation methods.

**Key Classes**:
- `DecodingTask`: Main orchestrator for the decoding process
- `GreedyDecoder`: Implements greedy search decoding
- `BeamSearchDecoder`: Implements beam search with patience
- `PyTorchInference`: Handles forward passes and KV-cache management
- `LogitFilter`: Various filters for token suppression and timestamp rules

**Features**:
- Multiple decoding strategies (greedy, beam search)
- Temperature-based sampling
- Token suppression for non-speech elements
- Timestamp token handling and validation
- Language detection capabilities

#### `tokenizer.py` - Text Tokenization
**Purpose**: Handles text encoding/decoding using tiktoken with Whisper-specific tokens.

**Key Features**:
- Supports 111 languages with language-specific tokens
- Special tokens for timestamps, tasks, and control
- Multilingual vs. English-only tokenizer modes
- Word-level tokenization with Unicode support
- Non-speech token filtering

**Special Tokens**:
- `<|startoftranscript|>`, `<|endoftext|>`
- `<|transcribe|>`, `<|translate|>`
- `<|nospeech|>`, `<|notimestamps|>`
- Time tokens: `<|0.00|>` to `<|30.00|>` (0.02s intervals)
- Language tokens: `<|en|>`, `<|es|>`, etc.

#### `mel.py` - Audio Preprocessing
**Purpose**: Converts raw audio to mel spectrograms for model input.

**Key Function**:
- `log_mel_spectrogram()`: Converts 16-bit signed linear audio to mel spectrogram
- `mel_filters()`: Loads mel filterbank matrices (80 or 128 mel channels)

**Audio Parameters**:
- Sample rate: 16 kHz
- Window size: 400 samples (N_FFT)
- Hop length: 160 samples (10ms frames)
- Chunk length: 30 seconds (480,000 samples)
- Mel channels: 80 (default)

**Process**:
1. Converts bytearray to float32 numpy array
2. Normalizes from int16 range to [-1, 1]
3. Applies STFT with Hann window
4. Converts to mel scale using precomputed filters
5. Applies logarithm and normalization

#### `utils.py` - Utility Functions
**Purpose**: General utility functions for text processing and file I/O.

**Key Functions**:
- `compression_ratio()`: Calculates text repetition ratio
- `format_timestamp()`: Formats seconds to HH:MM:SS.mmm
- `exact_div()`: Integer division with assertion
- Various result writers (TXT, VTT, SRT, TSV, JSON)
- Unicode safety functions for different encodings

### Asset Files

#### `assets/mel_filters.npz`
Pre-computed mel filterbank matrices for 80 and 128 mel channels, avoiding runtime dependency on librosa.

#### `assets/gpt2.tiktoken` & `assets/multilingual.tiktoken`
Tokenizer vocabulary files containing base64-encoded token mappings for English-only and multilingual models respectively.

### Configuration Files

#### `__init__.py`
Empty Python package initialization file.

#### `README`
Basic placeholder readme file.

## Usage

### Starting the Server
```bash
python aii_server.py
```

### Client Integration
Connect to `127.0.0.1:8300` and send:
1. Audio data in 20ms chunks (640 bytes SLIN format)
2. Use byte value 13 (carriage return) as delimiter
3. Receive transcription results printed to server console

### Audio Format Requirements
- **Format**: 16-bit signed linear (SLIN)
- **Sample Rate**: 16 kHz
- **Channels**: Mono
- **Chunk Size**: 640 bytes (20ms at 16kHz)

## Model Configuration

The system currently uses Whisper tiny model but can be configured for other sizes:
- **Current**: `tiny.pt` (39 MB, fastest)
- **Alternative**: `large-v3.pt` (1550 MB, most accurate)

## Performance Characteristics

- **Latency**: ~5 seconds (processing window size)
- **Throughput**: Real-time (1x speed or better)
- **Memory**: ~500 MB for tiny model, ~6 GB for large
- **Concurrent Clients**: Limited by available RAM and CPU

## Dependencies

- PyTorch
- NumPy  
- tiktoken
- Standard Python libraries (socket, threading, time, etc.)

## Future Enhancements

The codebase includes infrastructure for:
- Word-level timestamps
- Multiple language support
- Configurable chunk sizes
- Different output formats
- Attention visualization hooks

This implementation provides a solid foundation for real-time speech recognition applications with customizable parameters and extensible architecture.
