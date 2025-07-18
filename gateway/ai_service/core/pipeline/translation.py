import logging
import torch
from transformers import MarianMTModel, MarianTokenizer
from core.utils.path_resolver import resolve_model_path
from core.pipeline.model_loader import load_model_config

logger = logging.getLogger(__name__)
config = load_model_config()
translation_cfg = config.get("translation_model")

if not translation_cfg:
    raise RuntimeError("Translation model configuration missing in config file.")

model_path = resolve_model_path(translation_cfg["path"])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device} | Model path: {model_path}")

# === Load tokenizer and model ===
try:
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path).to(device)
    logger.info(f"Loaded MarianMT model from: {model_path}")
except Exception as e:
    logger.error(f"Failed to load MarianMT model: {e}")
    raise RuntimeError(f"Model load error: {e}")

# === Translation function ===
def translate(text: str) -> str:
    logger.info("Running MarianMT translation")
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
            early_stopping=True
        )

        return tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise RuntimeError(f"Translation failed: {str(e)}")
