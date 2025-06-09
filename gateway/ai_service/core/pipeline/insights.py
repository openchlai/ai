import json
import logging
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..pipeline import summarizer, ner, classifier

logger = logging.getLogger(__name__)

def generate_case_insights(transcript: str) -> Dict[str, Any]:
    """
    Generate trauma-informed case insights from transcript using summarization and Mistral model.
    """
    # Step 1: Summarize transcript
    try:
        summary = summarizer.summarize(transcript)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        summary = transcript[:1000]  # fallback: truncate raw transcript

    # Step 2: NER
    try:
        entities = ner.extract_entities(transcript)
    except Exception as e:
        logger.error(f"NER failed: {e}")
        entities = {}


    # Step 3: Classification
    try:
        case_classification = classifier.classify_case(transcript)
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        #  sensible defaults so the rest of the code doesn't break
        case_classification = {
            "main_category": "Unknown",
            "sub_category": "Unknown",
            "intervention": "None",
            "priority": "Low"
        }

    case_classification_dict = (
        case_classification.to_dict()
        if hasattr(case_classification, "to_dict")
        else case_classification  
    )
    category = case_classification_dict["main_category"]
    sub_category = case_classification_dict["sub_category"]
    intervention = case_classification_dict["intervention"]
    priority = case_classification_dict["priority"]

    case_classification = {
        "category": [category, sub_category],
        "interventions_needed": [intervention],
        "priority_level": priority
    }


    prompt = f"""You are a trauma-informed social worker conducting an expert case analysis. Analyze the following case summary and entities to generate a comprehensive JSON response with the following structure:

{{
  "case_summary": "Brief 2-3 sentence overview of the case",
  "named_entities": {{
    "persons": [],
    "organizations": [],
    "locations": [],
    "dates": [],
    "contact_information": []
  }},
  "classification": {{
    "category": {category, sub_category},
    "interventions_needed": {intervention},
    "priority_level": "{priority}"
  }},
  "case_management": {{
    "safety_planning": {{
      "immediate_actions": [],
      "long_term_measures": []
    }},
    "psychosocial_support": {{
      "short_term": [],
      "long_term": []
    }},
    "legal_protocols": {{
      "applicable_laws": [],
      "required_documents": [],
      "authorities_to_contact": []
    }},
    "medical_protocols": {{
      "immediate_needs": [],
      "follow_up_care": []
    }}
  }},
  "risk_assessment": {{
    "red_flags": [],
    "potential_barriers": [],
    "protective_factors": []
  }},
  "cultural_considerations": []
}}

Case Summary:
{summary}

Named Entities:
{json.dumps(entities, indent=2)}

Classification:
{json.dumps(case_classification, indent=2)}

Context: Respond with JSON only. Avoid additional explanations.
"""

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=5, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        response = session.post(
            'http://192.168.10.6:11434/api/generate',
            json={
                'model': 'mistral',
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()

        if 'response' not in data:
            logger.error(f"Invalid response format: {data}")
            raise ValueError("Missing 'response' key in model output")

        # Clean and validate JSON
        try:
            insights = json.loads(data['response'])
        except json.JSONDecodeError:
            logger.warning("Trying to sanitize invalid JSON from model...")
            fixed_response = data['response'].strip().split("```json")[-1].split("```")[0].strip()
            insights = json.loads(fixed_response)

        return insights

    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while calling insight service: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while calling insight service: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}", exc_info=True)
        raise