#!/usr/bin/env python3
"""
Setup script for Whisper training environment
Handles MLflow server setup and environment validation
"""

import os
import sys
import subprocess
import logging
import time
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_gpu_availability():
    """Check if GPU is available and get info"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU available: {gpu_name} ({gpu_memory:.1f}GB)")
            return True
        else:
            logger.warning("No GPU available - training will be slow on CPU")
            return False
    except ImportError:
        logger.error("PyTorch not installed")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'torch', 'transformers', 'datasets', 'evaluate', 
        'mlflow', 'soundfile', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} is missing")
    
    if missing_packages:
        logger.error(f"Please install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True


def setup_mlflow_server(port=5000):
    """Setup MLflow tracking server"""
    logger.info("Setting up MLflow tracking server...")
    
    # Check if MLflow server is already running
    try:
        response = requests.get(f"http://localhost:{port}/health")
        if response.status_code == 200:
            logger.info(f"MLflow server already running on port {port}")
            return True
    except requests.exceptions.ConnectionError:
        pass
    
    # Create mlruns directory
    mlruns_dir = Path("mlruns")
    mlruns_dir.mkdir(exist_ok=True)
    
    # Start MLflow server
    try:
        logger.info(f"Starting MLflow server on port {port}...")
        process = subprocess.Popen([
            sys.executable, "-m", "mlflow", "server",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--backend-store-uri", f"sqlite:///mlflow.db",
            "--default-artifact-root", "./mlruns"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"http://localhost:{port}/health")
                if response.status_code == 200:
                    logger.info("MLflow server started successfully!")
                    logger.info(f"MLflow UI available at: http://localhost:{port}")
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        
        logger.error("MLflow server failed to start")
        return False
        
    except Exception as e:
        logger.error(f"Failed to start MLflow server: {e}")
        return False


def validate_data_paths(config_path="config/training_config.json"):
    """Validate that data paths exist"""
    import json
    
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check Label Studio export
    labelstudio_path = config.get('labelstudio_export_path')
    if not os.path.exists(labelstudio_path):
        logger.error(f"Label Studio export not found: {labelstudio_path}")
        logger.info("Please ensure your Label Studio export is in the correct location")
        return False
    
    # Check audio base path
    audio_base_path = config.get('audio_base_path')
    if not os.path.exists(audio_base_path):
        logger.error(f"Audio base path not found: {audio_base_path}")
        return False
    
    # Check if audio directory exists
    audio_dir = os.path.join(audio_base_path, 'audio')
    if not os.path.exists(audio_dir):
        logger.error(f"Audio directory not found: {audio_dir}")
        return False
    
    # Count audio files
    audio_files = list(Path(audio_dir).glob('*.wav'))
    logger.info(f"Found {len(audio_files)} audio files in {audio_dir}")
    
    if len(audio_files) == 0:
        logger.error("No audio files found!")
        return False
    
    logger.info("✓ Data paths validated successfully")
    return True


def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "config",
        "logs",
        "models",
        "mlruns",
        "whisper-finetuned-production"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")


def main():
    """Main setup function"""
    logger.info("Setting up Whisper training environment...")
    
    # Create directory structure
    create_directory_structure()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed. Please install missing packages.")
        return False
    
    # Check GPU
    check_gpu_availability()
    
    # Setup MLflow server
    if not setup_mlflow_server():
        logger.error("MLflow setup failed")
        return False
    
    # Validate data paths
    if not validate_data_paths():
        logger.error("Data validation failed")
        return False
    
    logger.info("="*60)
    logger.info("SETUP COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    logger.info("Next steps:")
    logger.info("1. Verify your Label Studio export is correct")
    logger.info("2. Run: python whisper_training_pipeline.py")
    logger.info("3. Monitor training at: http://localhost:5000")
    logger.info("="*60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)