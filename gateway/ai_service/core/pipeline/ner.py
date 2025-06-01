import spacy
import logging
from typing import Dict, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load the English spaCy model
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Loaded spaCy model: en_core_web_sm")
except Exception as e:
    logger.error("Failed to load spaCy model: en_core_web_md")
    logger.exception(e)
    raise RuntimeError("spaCy model not initialized. Please ensure 'en_core_web_md' is installed.") from e

def extract_entities(text: str, flat: bool = False) -> Union[Dict[str, List[str]], List[Dict[str, str]]]:
    """
    Extract named entities from a text.

    Args:
        text (str): Input text.
        flat (bool): If True, return flat list of dicts (e.g., for highlight API).

    Returns:
        Dict[str, List[str]] or List[Dict[str, str]]
    """
    if nlp is None:
        raise RuntimeError("spaCy model not initialized")
        
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
        }

        for ent in doc.ents:
            if ent.label_ in entity_dict:
                entity_dict[ent.label_].append(ent.text)

        logger.info(f"Extracted {sum(len(v) for v in entity_dict.values())} entities.")

        if flat:
            flat_entities = [{"text": text, "label": label} for label, texts in entity_dict.items() for text in texts]
            return flat_entities

        return entity_dict

    except Exception as e:
        logger.exception(f"Entity extraction failed: {e}")
        raise RuntimeError(f"NER failed: {e}")
