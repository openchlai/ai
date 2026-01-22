# Quick Start Guide - Whisper Swahili Training

## 🚀 RunPod Setup

### 1. Launch RunPod Instance
- GPU: A100 40GB or 80GB
- Disk: 100GB+ recommended
- Template: PyTorch 2.0+ with CUDA 11.8+

### 2. Setup Environment
```bash
# Clone repo and navigate to project
cd tasks/asr/whisper-swahili-training

# Install dependencies
pip install -r requirements.txt

# Set HuggingFace token
export HF_TOKEN="your_huggingface_token"
```

### 3. Configure MLflow Tracking (Local Machine)
```bash
# On your local machine, start ngrok
ngrok http 5000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
```

### 4. Update RunPod Config
Edit `configs/runpod_config.yaml`:
```yaml
mlflow:
  tracking_uri: "https://abc123.ngrok.io"  # Paste your ngrok URL

training:
  hub_model_id: "your-hf-username/whisper-large-v2-sw"  # Your HF username
```

### 5. Start Training
```bash
# Run preparation checks (optional but recommended)
./prepare_for_production.sh configs/runpod_config.yaml

# Start training
python train.py --config configs/runpod_config.yaml

# Or resume from checkpoint if interrupted
python train.py --config configs/runpod_config.yaml --resume latest
```

---

## 🔬 Google Colab Setup

### 1. Upload Project to Colab
```python
# In Colab notebook
!git clone https://github.com/your-repo.git
%cd tasks/asr/whisper-swahili-training
!pip install -r requirements.txt
```

### 2. Set Tokens
```python
import os
os.environ['HF_TOKEN'] = 'your_huggingface_token'
```

### 3. Configure MLflow (Local Machine)
```bash
# On your local machine
ngrok http 5000
# Copy the URL
```

### 4. Update Colab Config
Edit `configs/colab_config.yaml`:
```yaml
mlflow:
  tracking_uri: "https://abc123.ngrok.io"  # Your ngrok URL

training:
  hub_model_id: "your-hf-username/whisper-large-v2-sw-colab"
```

### 5. Train in Colab
```python
!python train.py --config configs/colab_config.yaml
```

---

## 📊 Monitoring Training

### MLflow (on your local machine)
```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# Start ngrok tunnel
ngrok http 5000

# View at: http://localhost:5000
```

### Training Logs
```bash
# Watch metrics in real-time
tail -f training_metrics.jsonl

# View TensorBoard (if running locally on RunPod)
tensorboard --logdir=./logs/tensorboard --port=6006
```

### Check Progress
- MLflow UI: See loss curves, WER metrics
- Training logs: Step-by-step progress
- Checkpoints: Saved every 500 steps in `./whisper-large-v2-sw/checkpoint-*/`

---

## 🎯 After Training

### 1. Evaluate Final Model
```bash
# Evaluate on test split (do this ONCE at the end)
python evaluate_model.py \
    --model-path ./whisper-large-v2-sw \
    --dataset-name mozilla-foundation/common_voice_17_0 \
    --dataset-lang sw \
    --split test \
    --num-samples 2000

# Or evaluate from HuggingFace Hub
python evaluate_model.py \
    --model-path your-username/whisper-large-v2-sw \
    --dataset-name mozilla-foundation/common_voice_17_0 \
    --dataset-lang sw \
    --split test \
    --num-samples 2000
```

### 2. Check Results
- WER should be < 20% (baseline ~30-40%)
- Results saved in `evaluation_results/`

### 3. Download Model
```bash
# Model automatically pushed to HuggingFace Hub (if push_to_hub=true)
# Access at: https://huggingface.co/your-username/whisper-large-v2-sw
```

---

## ⚙️ Configuration Presets

### RunPod (Production)
- Config: `configs/runpod_config.yaml`
- Dataset: Full (44k train, 12k validation)
- Duration: ~8-12 hours (10k steps)
- GPU: A100 40GB/80GB
- Batch size: 16 (effective 16)

### Google Colab (Testing)
- Config: `configs/colab_config.yaml`
- Dataset: Subset (5k train, 500 validation)
- Duration: ~3-4 hours (2k steps)
- GPU: T4 15GB
- Batch size: 4 (effective 16 with grad accumulation)

### Local Test (Debugging)
- Config: `configs/local_test_config.yaml`
- Dataset: Tiny (50 train, 10 test)
- Duration: ~5 minutes (10 steps)
- Just for testing pipeline

---

## 🔧 Troubleshooting

### OOM (Out of Memory)
```yaml
# Reduce batch size or increase gradient accumulation
per_device_train_batch_size: 8  # was 16
gradient_accumulation_steps: 2  # was 1
```

### Slow Training
- Check `num_workers` (should be 8 on RunPod, 2 on Colab)
- Verify fp16 is enabled
- Monitor GPU utilization: `watch -n 1 nvidia-smi`

### MLflow Connection Failed
- Training continues with local logging
- Check ngrok tunnel is active
- Verify MLflow server is running locally

### Colab Disconnected
- Model checkpoints auto-saved every 200 steps
- Resume with: `--resume latest`
- Final model pushed to HuggingFace Hub (if push_to_hub=true)

---

## 📝 Expected Performance

| Metric | Baseline | After Training |
|--------|----------|----------------|
| WER    | 30-40%   | <20% (target)  |
| Training Time | - | 8-12 hours (RunPod) |
| GPU Memory | - | ~38GB (A100 40GB) |
| Disk Space | - | ~50-100GB |

---

## 🎓 Next Steps

1. **Evaluate on test split** (once, at the end)
2. **Compare with baseline** from `evaluation_results/`
3. **Push to HuggingFace Hub** (automatic if configured)
4. **Document results** in experiment notes
5. **Use model** for inference/production

---

## 📚 Key Files

- `train.py` - Main training script
- `evaluate_model.py` - Model evaluation
- `evaluate_baseline.py` - Baseline metrics
- `configs/runpod_config.yaml` - Production config
- `configs/colab_config.yaml` - Colab config
- `prepare_for_production.sh` - Pre-flight checks
