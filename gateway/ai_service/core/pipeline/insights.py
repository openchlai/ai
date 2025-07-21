import json
import logging
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..pipeline import summarizer, ner, classifier

logger = logging.getLogger(__name__)

def create_fallback_insights(summary: str, entities: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create fallback insights when external LLM service is unavailable.
    Uses available summary, entities, and classification data to generate basic insights.
    """
    logger.info("📋 Generating fallback insights from available data")
    
    # Extract entities by type
    persons = []
    organizations = []
    locations = []
    dates = []
    contact_info = []
    
    if isinstance(entities, dict):
        for entity_type, entity_list in entities.items():
            if entity_type.lower() in ['person', 'persons', 'people']:
                persons.extend(entity_list if isinstance(entity_list, list) else [entity_list])
            elif entity_type.lower() in ['org', 'organization', 'organizations']:
                organizations.extend(entity_list if isinstance(entity_list, list) else [entity_list])
            elif entity_type.lower() in ['loc', 'location', 'locations', 'gpe']:
                locations.extend(entity_list if isinstance(entity_list, list) else [entity_list])
            elif entity_type.lower() in ['date', 'dates', 'time']:
                dates.extend(entity_list if isinstance(entity_list, list) else [entity_list])
    elif isinstance(entities, list):
        # Handle flat list of entities
        for entity in entities:
            if isinstance(entity, dict) and 'label' in entity:
                if entity['label'] in ['PERSON', 'PER']:
                    persons.append(entity.get('text', ''))
                elif entity['label'] in ['ORG']:
                    organizations.append(entity.get('text', ''))
                elif entity['label'] in ['LOC', 'GPE']:
                    locations.append(entity.get('text', ''))
                elif entity['label'] in ['DATE', 'TIME']:
                    dates.append(entity.get('text', ''))
    
    # Determine priority level
    priority = classification.get('priority', classification.get('priority_level', 'medium'))
    if isinstance(priority, (int, float)):
        priority = 'high' if priority > 2 else 'medium' if priority > 1 else 'low'
    
    # Generate basic case summary
    case_summary = summary[:200] + "..." if len(summary) > 200 else summary
    if not case_summary.strip():
        case_summary = "Case requires further analysis based on available transcription data."
    
    # Basic risk assessment based on classification
    red_flags = []
    protective_factors = ["Case documented and flagged for review"]
    
    main_category = classification.get('main_category', classification.get('category', 'General'))
    if isinstance(main_category, list):
        main_category = main_category[0] if main_category else 'General'
    
    # Add category-specific insights
    if 'abuse' in main_category.lower():
        red_flags.extend(["Potential abuse indicators present", "Safety concerns identified"])
        protective_factors.append("Professional documentation initiated")
    elif 'legal' in main_category.lower():
        red_flags.append("Legal intervention may be required")
        protective_factors.append("Legal documentation in progress")
    
    return {
        "case_summary": case_summary,
        "named_entities": {
            "persons": persons[:10],  # Limit to avoid overwhelming output
            "organizations": organizations[:10],
            "locations": locations[:10], 
            "dates": dates[:10],
            "contact_information": contact_info[:5]
        },
        "classification": {
            "category": [main_category] if main_category else ["General Support"],
            "interventions_needed": classification.get('intervention', classification.get('interventions_needed', ['Assessment required'])),
            "priority_level": priority
        },
        "case_management": {
            "safety_planning": {
                "immediate_actions": ["Document case details", "Assess immediate safety needs"],
                "long_term_measures": ["Follow-up assessment", "Develop comprehensive support plan"]
            },
            "psychosocial_support": {
                "short_term": ["Active listening and validation", "Crisis intervention if needed"],
                "long_term": ["Ongoing counseling assessment", "Community resource connection"]
            },
            "legal_protocols": {
                "applicable_laws": ["Review relevant legal frameworks"],
                "required_documents": ["Case documentation", "Incident report if applicable"],
                "authorities_to_contact": ["Determine appropriate authorities based on case type"]
            },
            "medical_protocols": {
                "immediate_needs": ["Assess for urgent medical attention"],
                "follow_up_care": ["Coordinate with healthcare providers if needed"]
            }
        },
        "risk_assessment": {
            "red_flags": red_flags,
            "potential_barriers": ["Limited information available", "Need for comprehensive assessment"],
            "protective_factors": protective_factors
        },
        "cultural_considerations": ["Consider cultural context and sensitivity in all interventions"],
        "fallback_mode": True,  # Indicate this was generated using fallback
        "note": "Insights generated using available data. Consider manual review for comprehensive analysis."
    }

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
        case_classification = {
            "category": [],
            "interventions_needed": [],
            "priority_level": "medium"
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
    "category": ["Select applicable categories"],
    "interventions_needed": ["List required interventions"],
    "priority_level": "high/medium/low"
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
            'http://127.0.0.1:11434/api/generate',
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

    except requests.exceptions.ConnectionError as e:
        logger.warning(f"🔄 Ollama service unavailable, using fallback insights: {e}")
        return create_fallback_insights(summary, entities, case_classification)
    except requests.exceptions.Timeout as e:
        logger.warning(f"⏰ Ollama service timeout, using fallback insights: {e}")
        return create_fallback_insights(summary, entities, case_classification)
    except requests.exceptions.RequestException as e:
        logger.warning(f"🌐 HTTP error with Ollama service, using fallback insights: {e}")
        return create_fallback_insights(summary, entities, case_classification)
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate insights with Ollama, using fallback: {str(e)}")
        return create_fallback_insights(summary, entities, case_classification)
