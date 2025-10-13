#!/bin/bash
#
# Production Preparation Script
# Run this before starting production training on RunPod
#

set -e  # Exit on error

echo "========================================="
echo "Whisper Swahili Production Preparation"
echo "========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if config file provided
CONFIG_FILE=${1:-"configs/runpod_config.yaml"}

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Config file not found: $CONFIG_FILE${NC}"
    echo "Usage: ./prepare_for_production.sh [config_file]"
    exit 1
fi

echo -e "${GREEN}Using config: $CONFIG_FILE${NC}"
echo

# Check environment variables
echo "Step 1: Checking Environment Variables"
echo "----------------------------------------"

check_env() {
    if [ -z "${!1}" ]; then
        echo -e "${YELLOW}⚠️  $1 not set${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 is set${NC}"
        return 0
    fi
}

ENV_OK=true
check_env "HF_TOKEN" || ENV_OK=false

echo

# Optional environment variables
if check_env "MLFLOW_TRACKING_URI"; then
    echo -e "${GREEN}  MLflow tracking enabled${NC}"
fi

if check_env "WANDB_API_KEY"; then
    echo -e "${GREEN}  W&B tracking enabled${NC}"
fi

echo

if [ "$ENV_OK" = false ]; then
    echo -e "${RED}❌ Required environment variables missing!${NC}"
    echo "Please set: export HF_TOKEN=your_token"
    exit 1
fi

# Run pre-validation
echo "Step 2: Running Pre-Validation Checks"
echo "----------------------------------------"
python pre_train_validation.py --config "$CONFIG_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Pre-validation failed!${NC}"
    echo "Please fix the issues above before continuing."
    exit 1
fi

echo

# Get baseline metrics
echo "Step 3: Evaluating Baseline Model"
echo "----------------------------------------"
echo "This will take a few minutes..."
echo

python evaluate_baseline.py \
    --config "$CONFIG_FILE" \
    --num-samples 500 \
    --save-predictions

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Baseline evaluation failed, but continuing...${NC}"
else
    echo -e "${GREEN}✓ Baseline metrics saved${NC}"
fi

echo

# Create directories
echo "Step 4: Setting Up Directories"
echo "----------------------------------------"

mkdir -p logs/tensorboard
mkdir -p evaluation_results
mkdir -p checkpoints

echo -e "${GREEN}✓ Directories created${NC}"
echo

# Summary
echo "========================================="
echo "PREPARATION COMPLETE!"
echo "========================================="
echo
echo "You are ready to start training:"
echo
echo -e "${GREEN}python train.py --config $CONFIG_FILE${NC}"
echo
echo "To monitor training:"
echo "  - TensorBoard: tensorboard --logdir=./logs/tensorboard"
echo "  - Logs: tail -f training_metrics.jsonl"
echo "  - MLflow: Check http://localhost:5000 (if configured)"
echo
echo "To resume if interrupted:"
echo -e "${GREEN}python train.py --config $CONFIG_FILE --resume latest${NC}"
echo
echo "========================================="
echo "Good luck! 🚀"
echo "========================================="