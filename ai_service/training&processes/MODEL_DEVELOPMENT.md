# OpenCHS AI Model Development Documentation

This document provides comprehensive information about model development processes, source code organization, training configurations, performance testing, and version control practices for the OpenCHS AI platform.

## 🔗 Repository Information

**GitHub Repository:** [https://github.com/openchlai/ai](https://github.com/openchlai/ai)  
**Development Directory:** `ai_service/training&processes/`  
**MLflow Tracking:** [Internal MLflow Server]  
**Model Registry:** [https://huggingface.co/openchs/models](https://huggingface.co/openchs/models)

---

## 📊 Overview

| Task | Scripts | Notebooks | Training Status | Model Checkpoints | Performance Tests |
|------|---------|-----------|----------------|-------------------|-------------------|
| ASR | ✓ | ✓ | Production | ✓ | ✓ |
| Classification | ✓ | ✓ | Production | ✓ | Pending |
| NER | Planned | Planned | Development | - | - |
| QA Scoring | Planned | Planned | Development | - | - |
| Summarization | ✓ | Planned | Development | ✓ | ✓ |
| Translation | Planned | Planned | Development | - | - |

---

## 📂 Repository Structure

```
ai_service/training&processes/
├── notebooks/           # Jupyter notebooks for experimentation
│   ├── asr/
│   ├── classification/
│   ├── ner/
│   ├── qa-scoring/
│   ├── summarization/
│   └── translation/
└── scripts/            # Production training scripts
    ├── asr/
    ├── classification/
    ├── ner/
    ├── qa-scoring/
    ├── summarization/
    └── translation/
```

---

## 1. Automatic Speech Recognition (ASR)

### 📁 Directory: `scripts/asr/whisper-swahili-training/`

Complete training pipeline for fine-tuning Whisper models on Swahili, English, and Luganda child helpline audio.

#### Source Code Structure

```
whisper-swahili-training/
├── configs/                     # Training configuration files
│   ├── base_config.yaml        # Base configuration template
│   ├── colab_config.yaml       # Google Colab specific settings
│   ├── lambda_config.yaml      # AWS Lambda deployment config
│   ├── local_test_config.yaml  # Local development config
│   └── runpod_config.yaml      # RunPod GPU training config
├── src/                        # Core training modules
│   ├── config_manager.py       # Configuration management
│   ├── enhanced_callbacks.py   # Custom training callbacks
│   └── mlflow_utils.py         # MLflow integration utilities
├── logs/                       # Training logs
│   └── tensorboard/            # TensorBoard event files
├── evaluation_results/         # Model evaluation outputs
├── whisper-trained/            # Model checkpoints directory
├── train.py                    # Main training script
├── evaluate_model.py           # Model evaluation script
├── evaluate_baseline.py        # Baseline model evaluation
├── pre_train_validation.py     # Pre-training data validation
└── requirements.txt            # Python dependencies
```

#### Configuration Files

**Purpose:** Define training hyperparameters, data paths, model settings, and infrastructure requirements.

| Config File | Use Case | Key Parameters |
|-------------|----------|----------------|
| `base_config.yaml` | Template for all configs | Model architecture, training defaults |
| `colab_config.yaml` | Google Colab training | Free GPU optimization, reduced batch size |
| `lambda_config.yaml` | AWS Lambda inference | Serverless deployment settings |
| `local_test_config.yaml` | Local development | Small dataset, fast iteration |
| `runpod_config.yaml` | Production training | High-end GPU, full dataset, optimized batch size |

**Sample Configuration Structure:**
```yaml
model:
  name: "openai/whisper-small"
  language: "swahili"
  task: "transcribe"

training:
  num_epochs: 10
  batch_size: 16
  learning_rate: 1e-5
  warmup_steps: 500
  gradient_accumulation_steps: 2

data:
  train_dataset: "openchs/asr-dataset-v1"
  eval_dataset: "openchs/asr-eval-v1"
  max_duration: 30.0

mlflow:
  experiment_name: "whisper-swahili-finetuning"
  tracking_uri: "http://mlflow-server:5000"
```

#### Training Scripts

**`train.py`** - Main training orchestrator
- Loads configuration from YAML files
- Initializes Whisper model and tokenizer
- Sets up data loaders with augmentation
- Configures MLflow experiment tracking
- Implements training loop with callbacks
- Saves model checkpoints

**`evaluate_model.py`** - Model performance evaluation
- Loads trained model checkpoint
- Runs inference on test dataset
- Calculates WER (Word Error Rate), CER (Character Error Rate)
- Generates detailed evaluation reports
- Logs metrics to MLflow

**`evaluate_baseline.py`** - Baseline comparison
- Evaluates pre-trained Whisper model (no fine-tuning)
- Establishes baseline metrics for comparison
- Documents performance improvements from fine-tuning

**`pre_train_validation.py`** - Data quality checks
- Validates dataset format and structure
- Checks audio file integrity
- Verifies transcription quality
- Reports data statistics and issues

#### Model Development Logs

**TensorBoard Logs:** `logs/tensorboard/`
- Real-time training metrics visualization
- Loss curves, learning rate schedules
- Gradient norms and weight distributions

**Access TensorBoard:**
```bash
tensorboard --logdir=./logs/tensorboard --host=0.0.0.0 --port=6006
```

**MLflow Tracking:**
- Experiment runs with hyperparameters
- Training/validation metrics over time
- Model artifacts and checkpoints
- Comparison across different configurations

#### Evaluation Results

**Directory:** `evaluation_results/`

| File | Description | Metrics |
|------|-------------|---------|
| `baseline_results_20251004_092253.json` | Pre-trained Whisper baseline | WER: 45.2%, CER: 28.7% |
| `baseline_predictions_20251004_092253.json` | Baseline model predictions | Full prediction outputs |
| `eval_results_20251005_185014.json` | Fine-tuned model evaluation | WER: 32.1%, CER: 18.3% |

**Evaluation Metrics Tracked:**
- Word Error Rate (WER)
- Character Error Rate (CER)
- Real-Time Factor (RTF)
- Language-specific accuracy (English, Swahili, Luganda)
- Code-switching detection accuracy

#### Model Checkpoints

**Directory:** `whisper-trained/`

Trained model checkpoints are stored with version control:
- Model weights (`pytorch_model.bin`)
- Tokenizer configuration
- Training configuration snapshot
- Evaluation metrics summary

**Checkpoint Naming Convention:**
```
whisper-swahili-{model_size}-{version}-{date}
Example: whisper-swahili-small-v1.0.1-20251004
```

**Model Registry:**
- Hugging Face Models: [https://huggingface.co/openchs/models](https://huggingface.co/openchs/models)
- Hugging Face Datasets: [https://huggingface.co/openchs/datasets](https://huggingface.co/openchs/datasets)
- Git Tags: Version-tagged in repository
- MLflow Model Registry: Production/staging models

#### Performance Tests

**Test Categories:**

1. **Accuracy Tests**
   - WER/CER on test dataset
   - Per-language performance breakdown
   - Code-switching accuracy

2. **Latency Tests**
   - Inference time per audio second
   - Real-time factor (RTF)
   - Batch processing throughput

3. **Robustness Tests**
   - Background noise handling
   - Audio quality variations
   - Accent and dialect coverage

4. **Edge Case Tests**
   - Very short utterances (< 1 second)
   - Long recordings (> 30 seconds)
   - Multilingual conversations

#### Documentation

**`QUICK_START.md`** - Getting started guide for developers
- Environment setup
- Running first training job
- Basic troubleshooting

**`docs/PRODUCTION_TRAINING_GUIDE.md`** - Production deployment guide
- Infrastructure requirements
- Distributed training setup
- Monitoring and alerting
- Checkpoint management

#### Git Commit History

Key commits tracked for reproducibility:
```bash
# View training-related commits
git log --oneline --grep="whisper" -- scripts/asr/

# Example commits:
abc1234 - Add Whisper fine-tuning pipeline
def5678 - Implement MLflow tracking integration
ghi9012 - Add evaluation scripts and metrics
jkl3456 - Optimize for RunPod GPU training
```

#### Notebooks

**`notebooks/asr/dvc_dataset_loading_tutorial.ipynb`**
- Tutorial for loading DVC-tracked datasets
- Data preprocessing examples
- Audio feature extraction demonstrations
- Integration with training pipeline

---

## 2. Call Classification

### 📁 Directory: `scripts/classification/`

Multi-task classification system for categorizing helpline calls and extracting key attributes.

#### Source Code

**`multitask_classifier_trainer.py`** - Multi-task learning trainer
- Handles multiple classification heads (case type, urgency, sentiment)
- Implements custom loss weighting strategies
- Supports BERT, RoBERTa, and XLM-RoBERTa backbones
- Integrated with MLflow for experiment tracking

**Training Configuration:**
```python
config = {
    "model_name": "xlm-roberta-base",
    "tasks": ["case_type", "urgency", "sentiment"],
    "num_epochs": 20,
    "batch_size": 32,
    "learning_rate": 2e-5,
    "task_weights": {"case_type": 1.0, "urgency": 0.8, "sentiment": 0.5}
}
```

**Performance Metrics Tracked:**
- Per-task accuracy, F1-score, precision, recall
- Confusion matrices for each classification head
- Cross-task performance correlations
- Training time and resource utilization

#### Model Checkpoints

Stored in MLflow Model Registry with tags:
- `classification-multitask-v1`
- Best performing epoch checkpoint
- Full model configuration

#### Notebooks

**`notebooks/classification/multitask_classifier_pipeline.ipynb`**
- Data exploration and analysis
- Model architecture experimentation
- Hyperparameter tuning experiments
- Error analysis and visualization

#### Git Commits

```bash
# Classification development history
git log --oneline -- scripts/classification/

# Example commits:
mno7890 - Initial multitask classifier implementation
pqr1234 - Add task-specific loss weighting
stu5678 - Integrate with MLflow tracking
```

---

## 3. Summarization

### 📁 Directory: `scripts/summarization/`

Conversation summarization models for generating case notes from helpline transcripts.

#### Source Code

**`trainerV1.py`** - Summarization model trainer
- Fine-tunes T5/BART models for abstractive summarization
- Implements custom evaluation metrics (ROUGE, BERTScore)
- Supports multi-lingual summarization (English, Swahili)

**`validate.py`** - Model validation script
- Validates summary quality and coherence
- Checks for hallucinations and factual accuracy
- Generates human-readable evaluation reports

**Training Configuration:**
```python
config = {
    "model_name": "google/mt5-base",
    "max_source_length": 512,
    "max_target_length": 150,
    "num_epochs": 15,
    "beam_search_size": 4,
    "length_penalty": 0.6
}
```

**Performance Metrics:**
- ROUGE-1, ROUGE-2, ROUGE-L scores
- BERTScore for semantic similarity
- Human evaluation scores (relevance, coherence, conciseness)
- Hallucination rate

#### Model Checkpoints

Location: MLflow Model Registry
- Version-tagged checkpoints
- Associated configuration files
- Evaluation metrics for each version

#### Git Commits

```bash
# Summarization development history
git log --oneline -- scripts/summarization/

# Example commits:
vwx9012 - Add mT5-based summarization trainer
yza3456 - Implement ROUGE evaluation metrics
bcd7890 - Add validation script for quality checks
```

---

## 4. In-Development Models

The following models are currently in early development stages:

### NER (Named Entity Recognition)
- **Status:** Planning phase
- **Planned Features:** Person names, locations, dates, incident types
- **Target Models:** spaCy, BERT-based NER

### QA Scoring (Quality Assurance)
- **Status:** Research phase
- **Planned Features:** Conversation quality metrics, counselor performance scoring
- **Target Models:** Custom scoring model based on conversation analysis

### Translation
- **Status:** Planning phase
- **Planned Features:** English ↔ Swahili ↔ Luganda translation
- **Target Models:** MarianMT, mBART, NLLB

---

## 🔧 Development Workflow

### 1. Experimentation Phase
- Use Jupyter notebooks in `notebooks/` directory
- Rapid prototyping and hypothesis testing
- Data exploration and visualization
- Architecture experimentation

### 2. Script Development Phase
- Convert proven notebook code to production scripts
- Add proper error handling and logging
- Implement configuration management
- Add comprehensive documentation

### 3. Training Phase
- Use configuration files for reproducibility
- Log all experiments to MLflow
- Save checkpoints at regular intervals
- Monitor training with TensorBoard

### 4. Evaluation Phase
- Run evaluation scripts on held-out test data
- Compare against baseline models
- Document performance improvements
- Conduct error analysis

### 5. Version Control
- Commit code changes with descriptive messages
- Tag releases with semantic versioning
- Link commits to MLflow experiments
- Document breaking changes

---

## 📋 MLflow Experiment Tracking

All training runs are logged to MLflow with the following information:

### Logged Parameters
- Model architecture and size
- Training hyperparameters
- Dataset versions (via DVC)
- Hardware configuration
- Random seeds for reproducibility

### Logged Metrics
- Training/validation loss
- Task-specific performance metrics
- Learning rate over time
- Gradient norms
- Inference latency

### Logged Artifacts
- Model checkpoints
- Training configuration files
- Evaluation results (JSON)
- Visualizations (plots, confusion matrices)
- TensorBoard logs

### Experiment Organization

```
Experiments:
├── whisper-swahili-finetuning/
│   ├── run-001-baseline
│   ├── run-002-small-model
│   ├── run-003-medium-model
│   └── run-004-optimized
├── classification-multitask/
│   ├── run-001-bert-base
│   ├── run-002-xlm-roberta
│   └── run-003-weighted-loss
└── summarization-mt5/
    ├── run-001-baseline
    ├── run-002-beam-search
    └── run-003-length-penalty
```

---

## 🧪 Performance Testing Framework

### Test Categories

#### 1. Accuracy Tests
- **Location:** `evaluation_results/`
- **Frequency:** After each training run
- **Metrics:** Task-specific (WER, F1, ROUGE, etc.)

#### 2. Latency Tests
- **Method:** Benchmark inference time on various input sizes
- **Target:** < 2 seconds per request for 30-second audio
- **Logged to:** MLflow metrics

#### 3. Resource Usage Tests
- **Monitored:** GPU/CPU utilization, memory consumption
- **Tools:** nvidia-smi, psutil
- **Logged to:** Training logs

#### 4. Stress Tests
- **Scenarios:** Concurrent requests, long-running sessions
- **Purpose:** Verify production readiness
- **Results:** Documented in deployment guides

### Test Automation

Automated testing pipeline (planned):
```bash
# Run all tests for a model
./scripts/test_pipeline.sh --model whisper-swahili --checkpoint latest

# Generates:
# - Accuracy report
# - Latency benchmark
# - Resource usage profile
# - Comparison with baseline
```

---

## 🔐 Version Control & Reproducibility

### Git Workflow

**Branch Strategy:**
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature development
- `experiment/*` - Experimental work

**Commit Message Format:**
```
<type>(<scope>): <subject>

[optional body]
[optional footer]

Types: feat, fix, docs, test, refactor
Scopes: asr, classification, ner, qa, summarization, translation

Example:
feat(asr): Add Whisper fine-tuning pipeline with MLflow integration

- Implemented training script with custom callbacks
- Added configuration management for different environments
- Integrated MLflow tracking for experiments
- Added baseline evaluation script

Closes #123
```

### Tagging Strategy

Models are tagged when:
- Training completes successfully
- Evaluation metrics meet thresholds
- Model ready for production deployment

**Tag Format:** `{task}-{model}-v{major}.{minor}.{patch}-{date}`

**Examples:**
- `asr-whisper-v1.0.1-20251004`
- `classification-multitask-v1.0.0-20250827`
- `summarization-mt5-v1.0.0-20250826`

### Configuration Management

All training configurations are version-controlled:
- YAML files in `configs/` directories
- Committed alongside code changes
- Referenced in MLflow experiments
- Documented in training logs

---

## 📚 Documentation Standards

### Code Documentation
- Docstrings for all functions and classes
- Type hints for better IDE support
- Inline comments for complex logic
- README files in each subdirectory

### Training Documentation
- Configuration file explanations
- Hyperparameter tuning notes
- Performance improvement strategies
- Known issues and workarounds

### Experiment Documentation
- MLflow run descriptions
- Hypothesis and results
- Comparison with previous runs
- Next steps and recommendations

---

## 🔄 Model Lifecycle

### 1. Development
- Experiment in notebooks
- Validate approach with small dataset
- Document findings

### 2. Training
- Use production scripts with configuration files
- Log all experiments to MLflow
- Save checkpoints regularly

### 3. Evaluation
- Run comprehensive performance tests
- Compare against baselines
- Document results in `evaluation_results/`

### 4. Deployment
- Tag model version in Git
- Register in MLflow Model Registry
- Update deployment configuration
- Monitor production performance

### 5. Iteration
- Analyze production feedback
- Plan improvements
- Repeat cycle

---

## 📞 Support & Contribution

### Getting Started
1. Clone repository
2. Review `QUICK_START.md` for specific task
3. Set up development environment
4. Run example notebooks

### Reporting Issues
- Use GitHub Issues with appropriate labels
- Include reproducible examples
- Reference specific commits/tags

### Contributing
- Follow git workflow
- Write comprehensive tests
- Document all changes
- Update relevant documentation

---

## 🔗 Related Resources

- **Main Repository:** [openchs/ai](https://github.com/openchlai/ai)
- **Datasets Documentation:** [DATASETS.md](./DATASETS.md)
- **Model Registry:** [https://huggingface.co/openchs/models](https://huggingface.co/openchs/models)
- **Datasets Registry:** [https://huggingface.co/openchs/datasets](https://huggingface.co/openchs/datasets)
- **MLflow Server:** [Internal URL]
- **Production Guide:** [docs/PRODUCTION_TRAINING_GUIDE.md](./scripts/asr/whisper-swahili-training/docs/PRODUCTION_TRAINING_GUIDE.md)

---

**Last Updated:** October 2025  
**Maintained by:** BITZ IT Consulting Ltd R&D Team  
**Project:** OpenCHS - Digital Public Good for Child Protection  
**Git Repository:** https://github.com/openchlai/ai