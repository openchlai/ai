from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import logging

logger = logging.getLogger(__name__)

def translate(text, target_lang="eng_Latn"):
    """Translate text using the NLLB-200 1.3B model with GPU if available, otherwise CPU."""
    logger.info(f"Starting translation to {target_lang}")

    # Detect device: prefer GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    try:
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B")
        tokenizer.src_lang = "eng_Latn"
        model = AutoModelForSeq2SeqLM.from_pretrained(
            "facebook/nllb-200-1.3B",
            torch_dtype=torch.float16 if device.type == "cuda" else torch.float32
        ).to(device)

        # Tokenize input and move tensors to selected device
        max_length = 1024
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=max_length
        ).to(device)

        # Generate translation
        translated = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[target_lang],
            max_length=max_length,
            num_beams=4
        )

        # Decode and return
        result = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        logger.info("Translation completed successfully")
        return result

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise RuntimeError(f"Translation failed: {str(e)}")
