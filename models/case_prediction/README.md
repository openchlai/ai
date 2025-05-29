# Case Prediction Models

This directory contains models and tools for predicting outcomes and trajectories of child protection cases.

## Purpose

The case prediction module uses machine learning to:
- Predict likely outcomes of child protection cases
- Estimate time-to-resolution based on case characteristics
- Identify factors that may influence case progression
- Assist in resource allocation by forecasting case complexity

## Structure

- `case_model.py`: Core prediction model implementation
- `utils.py`: Utility functions for data processing and model evaluation
- `data_prep.py`: Data preparation pipeline for training and inference
- `train.py`: Training script for the case prediction models

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download pre-trained model weights (when available)
python download_models.py
```

## Usage

```python
from case_prediction.case_model import CasePredictionModel
from case_prediction.utils import preprocess_case_data

# Initialize model
model = CasePredictionModel.load('path/to/model')

# Prepare case data
case_data = preprocess_case_data(raw_case_data)

# Make prediction
prediction = model.predict(case_data)
print(f"Predicted outcome: {prediction['outcome']}")
print(f"Estimated time to resolution: {prediction['time_days']} days")
print(f"Confidence score: {prediction['confidence']}")
```

## Development Guidelines

When contributing to this module:

1. Ensure all models are properly validated using the evaluation framework
2. Document data dependencies and preprocessing steps
3. Follow the defined model API for consistency
4. Run unit tests before submitting changes: `pytest tests/`
5. Include performance metrics when updating models

## Model Evaluation

Periodically evaluate model performance:

```bash
# Run evaluation on test dataset
python evaluate.py --model latest --dataset test_cases.csv
```

