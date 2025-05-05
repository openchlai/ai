# Model Fine-Tuning

This directory contains scripts and utilities for fine-tuning pre-trained language models for specific child protection tasks.

## Purpose

The fine-tuning module provides tools to:
- Adapt pre-trained language models to domain-specific tasks
- Optimize model performance for child protection use cases
- Create specialized versions of models for different regional contexts
- Track and manage different versions of fine-tuned models

## Structure

- `bert_tuning.py`: Scripts for fine-tuning BERT-based models
- `gpt_tuning.py`: Scripts for fine-tuning GPT-based models
- Future additions will include specialized tuning for other model architectures

## Setup

```bash
# Install required dependencies
pip install -r requirements.txt

# Download base models
python download_base_models.py
```

## Usage

### Fine-tuning a BERT model

```python
from fine_tuning.bert_tuning import fine_tune_bert

# Prepare configuration
config = {
    'base_model': 'bert-base-uncased',
    'output_dir': './tuned_models/bert_child_protection',
    'train_file': 'data/train.csv',
    'validation_file': 'data/val.csv',
    'learning_rate': 2e-5,
    'num_train_epochs': 3,
    'batch_size': 16
}

# Run fine-tuning
fine_tune_bert(config)
```

### Fine-tuning a GPT model

```python
from fine_tuning.gpt_tuning import fine_tune_gpt

# Prepare configuration
config = {
    'base_model': 'gpt2',
    'output_dir': './tuned_models/gpt_case_summarization',
    'train_file': 'data/summaries_train.jsonl',
    'validation_file': 'data/summaries_val.jsonl',
    'learning_rate': 5e-5,
    'num_train_epochs': 2,
    'batch_size': 4
}

# Run fine-tuning
fine_tune_gpt(config)
```

## Development Guidelines

When working on fine-tuning scripts:

1. Document all hyperparameters and their recommended ranges
2. Include evaluation metrics in training output
3. Save model checkpoints periodically
4. Log training progress and key metrics
5. Ensure reproducibility by setting random seeds

## Model Management

Keep track of fine-tuned models:

```bash
# List available fine-tuned models
python list_models.py

# Compare performance of different fine-tuned versions
python compare_models.py --models model1 model2 --dataset test_data.csv
```

