from importlib.resources import files
import os
import yaml
import torch
import logging
from transformers import MarianTokenizer, MarianMTModel

logger = logging.getLogger(__name__)

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

translation_cfg = config["translation_model"]
model_path = translation_cfg["path"]
logger.info(f"Loaded translation model config: {translation_cfg}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

try:
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path)
    model = model.to(device)
    logger.info(f"MarianMT model loaded from: {model_path}")
except Exception as e:
    logger.error(f"Failed to load MarianMT model from {model_path}: {e}")
    raise RuntimeError(f"Model load error: {e}")

def translate(text):
    logger.info("Starting translation with MarianMT")

    try:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256
        ).to(device)

        output_tokens = model.generate(
            **inputs,
            max_length=256,
            num_beams=4,
            early_stopping=True,
            num_return_sequences=1
        )

        translated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        return translated_text

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise RuntimeError(f"Translation failed: {str(e)}")
