from transformers import NllbTokenizer, AutoModelForSeq2SeqLM
import logging

logger = logging.getLogger(__name__)

def translate(text, target_lang="eng_Latn"):
    """Translate text using larger NLLB model (1.3B)."""
    logger.info(f"Starting translation to {target_lang}")
    try:
        # Using the larger 1.3B parameter model instead of distilled 600M
        tokenizer = NllbTokenizer.from_pretrained("facebook/nllb-200-1.3B")
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-1.3B")

        # Better handling of long texts
        max_length = 1024  # Increased from default
        inputs = tokenizer(
            text, 
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=max_length
        )

        translated = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[target_lang],
            max_length=max_length,
            num_beams=4  # Better quality translation
        )
        result = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        logger.info("Translation completed successfully")
        return result
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise RuntimeError(f"Translation failed: {str(e)}")
