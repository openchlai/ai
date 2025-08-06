# core/ner.py

import spacy
import logging
import subprocess
from typing import Dict, List, Union

logger = logging.getLogger(__name__)

# === Load spaCy model with fallback ===
def load_spacy_model(model_name: str = "en_core_web_md") -> spacy.Language:
    try:
        logger.info(f"🔄 Attempting to load spaCy model: {model_name}")
        return spacy.load(model_name)
    except OSError:
        logger.warning(f"⚠️ spaCy model '{model_name}' not found. Attempting download...")
        try:
            subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)
            logger.info(f"✅ Successfully downloaded spaCy model: {model_name}")
            return spacy.load(model_name)
        except Exception as e:
            logger.error(f"❌ Failed to download or load spaCy model: {model_name}")
            raise RuntimeError(
                f"spaCy model '{model_name}' could not be loaded. "
                f"Run `python -m spacy download {model_name}` manually."
            ) from e

# Load the model once on import
nlp = load_spacy_model()

# === Named Entity Extraction ===
def extract_entities(text: str, flat: bool = False) -> Union[Dict[str, List[str]], List[Dict[str, str]]]:
    """
    Extract named entities from a text.

    Args:
        text (str): Input text.
        flat (bool): If True, return a flat list of entity dictionaries.

    Returns:
        Dict[str, List[str]] or List[Dict[str, str]]
    """
    if not nlp:
        raise RuntimeError("spaCy NLP model is not initialized.")

    try:
        doc = nlp(text)
        entity_dict: Dict[str, List[str]] = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],
            "LOC": [],
            "DATE": [],
            "TIME": [],
            "MONEY": [],
            "EVENT": [],
            "CONTACT_INFO": [],  # reserved for custom models
        }

        for ent in doc.ents:
            if ent.label_ in entity_dict:
                entity_dict[ent.label_].append(ent.text)

        logger.info(f"🔍 Extracted {sum(len(v) for v in entity_dict.values())} entities.")

        if flat:
            return [{"text": ent_text, "label": label} for label, texts in entity_dict.items() for ent_text in texts]

        return entity_dict

    except Exception as e:
        logger.exception("❌ Entity extraction failed")
        raise RuntimeError(f"NER failed: {e}")
