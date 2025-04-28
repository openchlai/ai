import torch
import torchaudio
import transformers
import datasets
import evaluate
import numpy as np
import pandas as pd
import matplotlib
import tensorboard
import jiwer
import librosa

# Print versions to verify installation
print("PyTorch version:", torch.__version__)
print("Torchaudio version:", torchaudio.__version__)
print("Transformers version:", transformers.__version__)
print("Datasets version:", datasets.__version__)
print("Evaluate version:", evaluate.__version__)
print("NumPy version:", np.__version__)
print("Pandas version:", pd.__version__)
print("Matplotlib version:", matplotlib.__version__)
print("Librosa version:", librosa.__version__)
print("Jiwer version:", jiwer.__version__)

# Check CUDA availability
if torch.cuda.is_available():
    print("\nCUDA is available!")
    print("CUDA version:", torch.version.cuda)
    print("GPU device:", torch.cuda.get_device_name(0))
    print("GPU memory:", torch.cuda.get_device_properties(0).total_memory / (1024**3), "GB")
else:
    print("\nCUDA is not available. Using CPU.")

print("\nInstallation test complete. All libraries imported successfully!")
