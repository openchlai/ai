#!/bin/bash

# Simple script to install PyTorch with torchaudio

echo "=================================================="
echo "Installing PyTorch and torchaudio"
echo "=================================================="

# First upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Check CUDA availability
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
    echo "CUDA detected: $CUDA_VERSION"
    
    # Install PyTorch based on CUDA version
    if [[ $CUDA_VERSION == 11.* ]]; then
        echo "Installing PyTorch for CUDA 11.x"
        pip install torch==2.0.1+cu117 torchaudio -f https://download.pytorch.org/whl/torch_stable.html
    elif [[ $CUDA_VERSION == 12.* ]]; then
        echo "Installing PyTorch for CUDA 12.x"
        pip install torch==2.2.0 torchaudio==2.2.0
    else
        echo "Unknown CUDA version. Installing latest PyTorch"
        pip install torch torchaudio
    fi
else
    echo "CUDA not detected. Installing CPU version of PyTorch."
    pip install torch torchaudio
fi

# Verify installation
python -c "import torch; import torchaudio; print('PyTorch version:', torch.__version__); print('torchaudio version:', torchaudio.__version__); print('CUDA available:', torch.cuda.is_available())"

echo "=================================================="
echo "PyTorch installation complete"
echo "=================================================="