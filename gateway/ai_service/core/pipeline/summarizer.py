from importlib.resources import files
import os
import torch
import yaml
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# === Force CPU inference ===
device = torch.device("cpu")

# === Load model path from config ===
# === Load model config ===
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

# === Get summarization model path ===
summ_config = config.get("summarization_model", {})
model_path = os.path.abspath(summ_config.get("path", "/app/models/summarizer_model"))

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Summarizer model not found at: {model_path}")

# === Load model and tokenizer ===
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
model = model.to(device)

# === Summarization function ===
def summarize(text: str, max_length: int = 128, min_length: int = 30) -> str:
    if not text.strip():
        return ""

    inputs = tokenizer("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
