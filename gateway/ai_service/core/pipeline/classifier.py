from transformers import AutoTokenizer, AutoModelForSequenceClassification
from joblib import load
import torch
import re
import os
import yaml
from importlib.resources import files

# Load config
try:
    config_path = os.getenv("MODEL_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config_file = files("ai_service").joinpath("config/model_config.yaml")
        with config_file.open("r") as f:
            config = yaml.safe_load(f)
except Exception as e:
    raise RuntimeError(f"Could not load model config: {e}")

model_config = config.get("classifier_model", {})
model_path = model_config.get("path", "/app/models/classifier_model")

# Ensure the path is a valid local directory
if not os.path.exists(os.path.join(model_path, "config.json")):
    raise FileNotFoundError(f"Expected model config.json not found in: {model_path}")

# Load model, tokenizer, label encoder
model = AutoModelForSequenceClassification.from_pretrained(
    pretrained_model_name_or_path=model_path,
    local_files_only=True
)
tokenizer = AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path=model_path,
    local_files_only=True
)
label_encoder = load(os.path.join(model_path, "label_encoder.joblib"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def classify_case(narrative: str):
    text = re.sub(r'[^a-z0-9\s]', '', narrative.lower().strip())
    inputs = tokenizer(text, truncation=True, padding='max_length', max_length=256, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    top_prob, top_label = torch.max(probs, dim=1)
    category = label_encoder.inverse_transform([top_label.cpu().item()])[0]

    return {
        "category": category,
        "confidence": round(top_prob.item(), 4)
    }
