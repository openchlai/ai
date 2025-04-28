#!/bin/bash
set -e  # Exit on error

echo "=================================================="
echo "Wav2Vec Fine-Tuning Environment Setup"
echo "=================================================="

# Install setuptools and wheel instead of distutils for Python 3.12
echo "Installing setuptools and wheel for Python 3.12..."
pip install --upgrade pip setuptools wheel

# Check Python version
PYTHON_VERSION=$(python --version | cut -d' ' -f2)
echo "Using Python $PYTHON_VERSION"

# Install basic build dependencies
echo "Installing basic build dependencies..."
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Install PyTorch with CUDA support
install_pytorch() {
    echo "Installing PyTorch and torchaudio..."
    
    # Check CUDA availability and version
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
        echo "CUDA detected: $CUDA_VERSION"
        
        # Install appropriate PyTorch version based on CUDA
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
}

# Install core dependencies
install_dependencies() {
    echo "Installing core dependencies one by one..."

    # Install manually one by one to avoid dependency conflicts
    pip install numpy==1.24.3
    pip install soundfile  # Required by librosa
    pip install matplotlib
    pip install pandas
    pip install jiwer
    pip install huggingface_hub==0.14.1
    pip install transformers==4.28.1
    pip install datasets==2.12.0
    pip install evaluate==0.4.0
    pip install librosa
    pip install tensorboard
}

# Create directories
create_directories() {
    echo "Creating project directories..."
    mkdir -p wav2vec2-swahili-finetuned/logs
    mkdir -p wav2vec2-swahili-finetuned/checkpoints
}

# Verify installation
verify_installation() {
    echo "Verifying installation..."
    
    # Create verification script
    cat > verify_installation.py << 'EOL'
import sys
import platform

# Print system information
print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.platform()}")

# Check each package
packages = [
    "torch", "torchaudio", "transformers", "datasets", 
    "evaluate", "numpy", "pandas", "tensorboard", 
    "librosa", "jiwer", "matplotlib"
]

all_success = True
for package in packages:
    try:
        module = __import__(package)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {package}: {version}")
    except ImportError as e:
        print(f"❌ {package}: Failed to import - {e}")
        all_success = False

# Check CUDA availability
try:
    import torch
    if torch.cuda.is_available():
        print("\nCUDA is available!")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    else:
        print("\nCUDA is not available. Using CPU.")
except Exception as e:
    print(f"Error checking CUDA: {e}")
    all_success = False

print("\nVerification " + ("SUCCESSFUL" if all_success else "FAILED"))
EOL

    python verify_installation.py
}

# Main execution
echo "Starting installation process..."

# Install setuptools and wheel
pip install --upgrade pip setuptools wheel

# Install PyTorch and torchaudio
install_pytorch

# Install other dependencies
install_dependencies

# Create directories
create_directories

# Verify installation
verify_installation

echo "=================================================="
echo "Installation complete!"
echo "You can now run the training script."
echo "=================================================="