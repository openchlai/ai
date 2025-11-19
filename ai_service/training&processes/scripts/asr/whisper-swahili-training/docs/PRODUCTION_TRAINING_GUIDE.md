# Production Training Guide for Whisper Swahili Fine-tuning

## 📋 Pre-Training Checklist

Before running on RunPod, complete these steps in order:

### 1. Environment Setup

```bash
# Install requirements
pip install -r requirements.txt

# Set environment variables
export HF_TOKEN="your_huggingface_token"
export NGROK_TOKEN="your_ngrok_token"  # If using MLflow with ngrok
export WANDB_API_KEY="your_wandb_key"  # If using wandb
```

### 2. Run Pre-Validation

```bash
# Validate your setup before training
python pre_train_validation.py --config configs/runpod_config.yaml
```

This checks:
- ✅ CUDA availability and GPU memory
- ✅ Configuration validity
- ✅ Dataset access
- ✅ Model loading
- ✅ Output directories
- ✅ MLflow connection
- ✅ HuggingFace authentication

**Don't proceed until all checks pass!**

### 3. Get Baseline Metrics

```bash
# Evaluate baseline model performance
python evaluate_baseline.py \
    --config configs/runpod_config.yaml \
    --num-samples 500 \
    --save-predictions

# This will save results to ./evaluation_results/baseline_results_*.json
```

**Expected baseline WER:** ~30-40% for Whisper Large v2 on Swahili CV17

### 4. Test on Colab First

```bash
# Run small test on Colab
python train_improved.py --config configs/colab_config.yaml

# This should:
# ✅ Train for ~500 steps
# ✅ Generate TensorBoard logs
# ✅ Save checkpoints
# ✅ Log to MLflow (if configured)
```

## 🚀 Production Training on RunPod

### Storage Considerations

**Dataset Loading Modes:**

The pipeline automatically chooses between two loading modes:

1. **Streaming Mode** (1-3GB disk usage)
   - Enabled when `train_samples` or `test_samples` is set
   - Downloads samples on-demand
   - Perfect for Colab/limited storage

2. **Regular Mode** (25-30GB disk usage)
   - Enabled when both are `null`
   - Downloads full dataset first
   - Faster for production training

**For RunPod:** Use Regular mode (faster) if you have 100GB+ storage
**For Colab:** Use Streaming mode (required for free tier)

See `DATASET_LOADING_GUIDE.md` for detailed comparison.

### Step 1: Setup RunPod Instance

**Recommended specs:**
- GPU: A100 40GB or A100 80GB
- CPU: 8+ cores
- RAM: 32GB+
- Storage: 100GB+ SSD

**Template:** PyTorch 2.0+

### Step 2: Clone and Setup

```bash
# SSH into RunPod instance
git clone <your-repo>
cd whisper-swahili-training

# Install requirements
pip install -r requirements.txt

# Set tokens
export HF_TOKEN="your_token"
export MLFLOW_TRACKING_URI="http://your-local-ip:5000"  # If using MLflow
```

### Step 3: Create Production Config

Create `configs/runpod_config.yaml`:

```yaml
parent: "base_config.yaml"

dataset:
  name: "mozilla-foundation/common_voice_17_0"
  language: "sw"
  train_samples: null  # null = full dataset (regular loading)
  test_samples: 2000   # Limit test set for faster eval
  num_workers: 8
  
  # NOTE: Dataset Loading Modes
  # - If train_samples OR test_samples is set: STREAMING mode (memory efficient)
  # - If both are null: REGULAR mode (downloads full dataset)
  # - For RunPod with good storage: Use REGULAR (faster)
  # - For Colab/limited storage: Use STREAMING
  # - See DATASET_LOADING_GUIDE.md for details

training:
  per_device_train_batch_size: 16  # A100 can handle this
  gradient_accumulation_steps: 1
  max_steps: 10000
  learning_rate: 0.00001
  warmup_steps: 500
  
  # Checkpointing
  save_steps: 500
  eval_steps: 500
  save_total_limit: 3
  learning_rate: 0.00001
  warmup_steps: 500
  
  # Checkpointing
  save_steps: 500
  eval_steps: 500
  save_total_limit: 3
  
  # Recovery
  load_best_model_at_end: true
  metric_for_best_model: "wer"
  
  # Push to hub
  push_to_hub: true
  hub_model_id: "your-username/whisper-large-v2-sw"
  
  # Optimization
  fp16: true
  gradient_checkpointing: true
  optim: "adamw_torch"
  
  # Early stopping (optional)
  early_stopping_patience: 5

mlflow:
  tracking_uri: "http://your-local-ip:5000"
  experiment_name: "whisper-swahili-production"
  use_ngrok: false

logging:
  use_mlflow: true
  use_tensorboard: true
  use_wandb: false  # Set true if using wandb
  tensorboard_dir: "./logs/tensorboard"
  save_tensorboard_to_hf: true
```

### Step 4: Run Pre-Validation on RunPod

```bash
python pre_train_validation.py --config configs/runpod_config.yaml
```

### Step 5: Start Training

```bash
# Start training with all monitoring
python train_improved.py --config configs/runpod_config.yaml

# Training will:
# ✅ Log to TensorBoard (view at logs/tensorboard)
# ✅ Log to MLflow (if configured)
# ✅ Save checkpoints every 500 steps
# ✅ Evaluate every 500 steps
# ✅ Push to HuggingFace Hub
# ✅ Monitor for NaN losses
# ✅ Show progress and ETA
```

### Step 6: Monitor Training

**TensorBoard (Local):**
```bash
tensorboard --logdir=./logs/tensorboard --port=6006
```

**Check Logs:**
```bash
tail -f training_metrics.jsonl
```

**MLflow (if configured):**
Access at `http://localhost:5000`

## 🔄 Resuming Training

If training is interrupted:

```bash
# Resume from latest checkpoint
python train_improved.py \
    --config configs/runpod_config.yaml \
    --resume latest

# Or resume from specific checkpoint
python train_improved.py \
    --config configs/runpod_config.yaml \
    --resume ./whisper-large-v2-sw/checkpoint-5000
```

## 📊 Post-Training Evaluation

### 1. Evaluate Final Model

```bash
python evaluate_model.py \
    --model-path ./whisper-large-v2-sw \
    --dataset-name mozilla-foundation/common_voice_17_0 \
    --dataset-lang sw \
    --num-samples 2000 \
    --save-predictions \
    --baseline-results ./evaluation_results/baseline_results_*.json
```

### 2. Evaluate HuggingFace Model

```bash
python evaluate_model.py \
    --model-path your-username/whisper-large-v2-sw \
    --dataset-name mozilla-foundation/common_voice_17_0 \
    --dataset-lang sw \
    --save-predictions
```

## 📈 Expected Results

### Training Metrics
- **Baseline WER:** ~30-40%
- **Target WER:** <20%
- **Training time:** ~8-12 hours on A100 for 10K steps
- **Checkpoints:** Every 500 steps (~30-45 min intervals)

### Monitoring
- Loss should decrease smoothly
- WER should improve progressively
- No NaN losses
- GPU memory usage: ~35-40GB on A100

## 🛠️ Troubleshooting

### OOM (Out of Memory)
```yaml
# Reduce batch size in config
training:
  per_device_train_batch_size: 8  # Down from 16
  gradient_accumulation_steps: 2  # Keep effective batch same
```

### Slow Training
- Check dataloader workers: `num_workers: 8`
- Verify fp16 is enabled
- Check GPU utilization: `nvidia-smi -l 1`

### NaN Losses
- Training will auto-stop after 3 NaN occurrences
- Resume from last checkpoint
- Consider reducing learning rate

### MLflow Connection Issues
- Verify MLflow server is running
- Check firewall/network settings
- Fall back to local logging if needed

## 📁 Output Structure

After successful training:

```
whisper-large-v2-sw/
├── config.json
├── preprocessor_config.json
├── tokenizer_config.json
├── model.safetensors
├── training_args.bin
├── checkpoint-500/
├── checkpoint-1000/
├── checkpoint-*/ (last 3 checkpoints)
├── training_metrics.jsonl
├── metrics_summary.json
└── checkpoint_info.json (in each checkpoint)

logs/
└── tensorboard/
    └── events.out.tfevents.*

evaluation_results/
├── baseline_results_*.json
├── eval_results_*.json
└── predictions_*.json
```

## ✅ Success Criteria

Before considering training complete:

1. ✅ Training completed without crashes
2. ✅ Final WER < 20%
3. ✅ Model pushed to HuggingFace Hub
4. ✅ TensorBoard logs saved
5. ✅ Evaluation results saved
6. ✅ Checkpoints preserved
7. ✅ Improvement over baseline documented

## 🚦 Next Steps After Training

1. Run comprehensive evaluation on test set
2. Test model on real Swahili audio samples
3. Compare with baseline metrics
4. Document results and improvements
5. Share model card on HuggingFace
6. Consider additional fine-tuning if needed

## 📝 Notes

- **Checkpoint every 500 steps** = Every ~30-45 minutes on A100
- **Total training time** = 8-12 hours for 10K steps
- **Disk space needed** = 50-100GB (model + checkpoints + logs)
- **Network** = Required for HuggingFace push and dataset loading

## 🆘 Emergency Recovery

If training crashes:

1. Check latest checkpoint: `ls -lt whisper-large-v2-sw/checkpoint-*`
2. Resume: `python train_improved.py --config configs/runpod_config.yaml --resume latest`
3. If checkpoint corrupt, check `emergency_checkpoint/`
4. If all fails, restart from baseline with reduced LR

## 📞 Support Resources

- HuggingFace Forums: https://discuss.huggingface.co/
- Whisper Documentation: https://huggingface.co/docs/transformers/model_doc/whisper
- Common Voice Dataset: https://commonvoice.mozilla.org/

---

**Good luck with your training! 🎉**