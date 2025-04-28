#!/bin/bash

echo "=================================================="
echo "Python 3.12 Compatible Installation"
echo "=================================================="

# Upgrade pip and essential tools
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install numpy from binary (no build required)
echo "Installing numpy (binary version)..."
pip install --only-binary=numpy numpy>=1.26.0

# Install PyTorch with CUDA support
echo "Installing PyTorch and torchaudio..."
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
    echo "CUDA detected: $CUDA_VERSION"
    
    # Install PyTorch based on CUDA version
    if [[ $CUDA_VERSION == 11.* ]]; then
        echo "Installing PyTorch for CUDA 11.x"
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    elif [[ $CUDA_VERSION == 12.* ]]; then
        echo "Installing PyTorch for CUDA 12.x"
        pip install torch torchvision torchaudio
    else
        echo "Unknown CUDA version. Installing latest PyTorch"
        pip install torch torchvision torchaudio
    fi
else
    echo "CUDA not detected. Installing CPU version of PyTorch."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install modern versions of libraries compatible with Python 3.12
echo "Installing Python 3.12 compatible dependencies..."
pip install soundfile
pip install matplotlib
pip install pandas
pip install jiwer
pip install huggingface_hub
pip install transformers
pip install datasets
pip install evaluate
pip install librosa
pip install tensorboard

# Create directories
echo "Creating project directories..."
mkdir -p wav2vec2-swahili-finetuned/logs
mkdir -p wav2vec2-swahili-finetuned/checkpoints

# Verify installation
echo "Verifying installation..."
python -c "
import platform
print(f'Python {platform.python_version()}')

packages = ['numpy', 'torch', 'torchaudio', 'transformers', 'datasets', 
            'evaluate', 'librosa', 'jiwer', 'tensorboard']

for pkg in packages:
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        print(f'✅ {pkg}: {version}')
    except ImportError as e:
        print(f'❌ {pkg}: Failed - {e}')

import torch
if torch.cuda.is_available():
    print(f'CUDA available: {torch.cuda.get_device_name(0)}')
else:
    print('CUDA not available, using CPU')
"

echo "=================================================="
echo "Installation complete!"
echo "=================================================="