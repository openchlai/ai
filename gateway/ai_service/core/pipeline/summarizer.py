import logging
import torch
from core.pipeline.model_loader import load_hf_model_and_tokenizer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# === Load summarizer model and tokenizer ===
try:
    model, tokenizer, device = load_hf_model_and_tokenizer("summarizer_model")
    logger.info("✅ Summarization model loaded successfully.")
except Exception as e:
    raise RuntimeError(f"Failed to load summarizer model or tokenizer: {e}")

# === Summarization function ===
def summarize(text: str, max_length: int = 128, min_length: int = 30) -> str:
    """
    Summarizes input text using the loaded model.
    
    Args:
        text (str): Input text to summarize.
        max_length (int): Max length of summary.
        min_length (int): Min length of summary.
    
    Returns:
        str: The generated summary or error message.
    """
    if not text.strip():
        return ""

    try:
        inputs = tokenizer(
            "summarize: " + text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
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

    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return "[Error generating summary]"
