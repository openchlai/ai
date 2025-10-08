# Translator Model Documentation

## 1. Model Overview

The translator model is a sequence-to-sequence model that is designed to translate text from one language to another. It is based on the **MarianMT architecture** from Hugging Face and has been fine-tuned for **Swahili–English domain-specific translation**.  

The script (`translation.py`) supports training, evaluation, and experiment tracking via MLflow.

## 2. Model Details

*   **Model Architecture:** The model is based on the MarianMT architecture.
*   **Training Data:** The model is fine-tuned on a custom Swahili–English dataset, loaded through the Hugging Face `datasets` library.
*   **Frameworks:** PyTorch, Hugging Face Transformers, Datasets, and Evaluate.
*   **Experiment Tracking:** MLflow is used to log training parameters, metrics, and artifacts.

## 3. Training Pipeline

### 3.1. Configuration

The script requires a JSON configuration file. Example:

```json
{
  "language_pair": "en-sw",
  "train_file": "data/train.json",
  "validation_file": "data/val.json",
  "test_file": "data/test.json",
  "source_lang": "en",
  "target_lang": "sw",
  "num_train_epochs": 5,
  "per_device_train_batch_size": 16,
  "per_device_eval_batch_size": 16,
  "learning_rate": 5e-5
}
```

### 3.2. Running Training

```bash
python translation.py --config config.json
```

This will:

* Load the dataset and tokenizer.
* Fine-tune the MarianMT model.
* Log metrics and hyperparameters in MLflow.
* Save the trained model to `./models/finetuned-<lang-pair>/`.

## 4. Request Format

Since this is a training script, the request format is the **configuration file** passed to the program. Each language being trained has a seperate configuration file.   

Example:  

```json
{
  "language_pair": "en-sw",
  "train_file": "data/train.json"
}
```

## 5. Response Format

The script produces:

```json
{
  "metrics": {
    "train_loss": "...",
    "eval_loss": "...",
    "chrf_scroe": "...",
    "bleu_score": "..."
  },
  "artifacts": {
    "saved_model": "./models/finetuned-en-sw",
    "mlflow_experiment": "translation-en-sw"
  }
}
```

## 6. Example Usage

```python
from transformers import MarianMTModel, MarianTokenizer

model_name = "./models/finetuned-en-sw"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

text = ["Watoto wanahitaji msaada."]
inputs = tokenizer(text, return_tensors="pt", padding=True)
translated = model.generate(**inputs)
print(tokenizer.decode(translated[0], skip_special_tokens=True))
```

Output:

```
"Children need help."
```

## 7. Error Handling

*   If the configuration file is missing, a `FileNotFoundError` will be raised.
*   If the dataset path is invalid, loading will fail with an error.
*   If the model cannot be saved or loaded, an exception will be thrown and logged.
