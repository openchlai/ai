#!/bin/bash

# Whisper Fine-tuning Training Script
# Production-ready training with proper error handling

set -e  # Exit on any error

echo "========================================"
echo "Whisper Fine-tuning Training Pipeline"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment should be used
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Using virtual environment: $VIRTUAL_ENV"
else
    print_warning "No virtual environment detected. Consider using one for isolation."
fi

# Setup environment
print_status "Setting up training environment..."
python3 setup_training.py

if [ $? -ne 0 ]; then
    print_error "Environment setup failed"
    exit 1
fi

print_success "Environment setup completed"

# Run training with different configurations based on arguments
CONFIG_FILE="config/training_config.json"
LOG_FILE="logs/training_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory if it doesn't exist
mkdir -p logs

print_status "Starting training pipeline..."
print_status "Config file: $CONFIG_FILE"
print_status "Log file: $LOG_FILE"

# Run training with logging
python3 whisper_training_pipeline.py \
    --config "$CONFIG_FILE" \
    2>&1 | tee "$LOG_FILE"

# Check if training was successful
if [ $? -eq 0 ]; then
    print_success "Training completed successfully!"
    print_status "Check results at: http://localhost:5000"
    print_status "Model saved in: ./whisper-finetuned-production"
    print_status "Training log: $LOG_FILE"
else
    print_error "Training failed. Check log file: $LOG_FILE"
    exit 1
fi

echo "========================================"
echo "Training pipeline completed"
echo "========================================"