# app/services/insights_service.py

import json
import logging
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..models.summarizer_model import summarization_model
from ..models.ner_model import ner_model
from ..models.classifier_model import classifier_model

logger = logging.getLogger(__name__)

def generate_case_insights(transcript: str) -> Dict[str, Any]:
    """
    Generate trauma-informed case insights from transcript using summarization and Mistral model.
    """
    # Step 1: Summarize transcript
    try:
        summary = summarization_model.summarize(transcript)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        summary = transcript[:1000]  # fallback: truncate raw transcript

    # Step 2: NER
    try:
        entities = ner_model.extract_entities(transcript)
    except Exception as e:
        logger.error(f"NER failed: {e}")
        entities = {}

    # Step 3: Classification
    try:
        case_classification = classifier_model.classify(transcript)
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

    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while calling insight service: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while calling insight service: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}", exc_info=True)
        raise


def generate_enhanced_audio_insights(
    original_transcript: str, 
    enhanced_transcript: str, 
    translation: str,
    entities: Dict,
    classification: Dict,
    qa_scores: Dict,
    summary: str,
    audio_quality_info: Dict
) -> Dict[str, Any]:
    """
    Generate enhanced insights from downloaded high-quality audio file using Mistral.
    This provides more comprehensive analysis than streaming-based insights.
    """
    
    # Calculate improvement metrics
    transcript_quality_improvement = len(enhanced_transcript) - len(original_transcript)
    quality_ratio = len(enhanced_transcript) / len(original_transcript) if len(original_transcript) > 0 else 1.0
    
    prompt = f"""You are an expert trauma-informed social worker conducting a COMPREHENSIVE case analysis using high-quality audio data. This analysis supersedes previous streaming-based insights with enhanced accuracy from complete call recording.

AUDIO QUALITY ANALYSIS:
- Original streaming transcript: {len(original_transcript)} characters
- Enhanced audio transcript: {len(enhanced_transcript)} characters  
- Quality improvement: {transcript_quality_improvement} characters ({quality_ratio:.2f}x)
- Audio file size: {audio_quality_info.get('file_size_mb', 'unknown')}MB
- Both parties clearly captured in mixed-mono format

Generate a comprehensive JSON response with enhanced insights:

{{
  "analysis_metadata": {{
    "analysis_type": "enhanced_audio_based",
    "transcript_quality_improvement": "{quality_ratio:.2f}x",
    "additional_content_captured": "{transcript_quality_improvement} characters",
    "confidence_level": "high"
  }},
  "enhanced_case_summary": "Detailed 3-4 sentence overview based on complete audio",
  "comprehensive_entities": {{
    "persons": ["All individuals mentioned with roles/relationships"],
    "organizations": ["All organizations, services, institutions mentioned"],
    "locations": ["All locations with context"],
    "dates_timeline": ["Chronological events and dates"],
    "contact_information": ["Phone numbers, addresses, references"],
    "medical_information": ["Health conditions, medications, treatments"],
    "legal_references": ["Case numbers, court dates, legal proceedings"]
  }},
  "advanced_classification": {{
    "primary_categories": ["Main case categories"],
    "secondary_concerns": ["Additional issues identified"],
    "complexity_level": "simple/moderate/complex/highly_complex",
    "intervention_urgency": "immediate/within_24h/within_week/routine",
    "multi_agency_required": true/false
  }},
  "quality_assurance_insights": {{
    "agent_performance_highlights": ["Strengths observed"],
    "communication_quality": "excellent/good/needs_improvement/poor",
    "adherence_to_protocols": ["Protocol compliance observations"],
    "missed_opportunities": ["Areas for improvement"],
    "caller_satisfaction_indicators": ["Signs of satisfaction/dissatisfaction"]
  }},
  "comprehensive_risk_assessment": {{
    "immediate_safety_risks": ["Urgent safety concerns"],
    "medium_term_risks": ["Developing concerns to monitor"],
    "protective_factors": ["Strengths and supports"],
    "vulnerability_indicators": ["Risk factors identified"],
    "suicide_risk_level": "none/low/moderate/high/imminent",
    "violence_risk_level": "none/low/moderate/high/imminent"
  }},
  "detailed_action_plan": {{
    "immediate_actions_24h": ["Actions needed within 24 hours"],
    "short_term_goals_1week": ["Goals for next week"],
    "medium_term_objectives_1month": ["Monthly objectives"],
    "long_term_support_plan": ["Ongoing support needs"],
    "follow_up_schedule": ["When to check in again"]
  }},
  "service_coordination": {{
    "internal_referrals": ["Within organization referrals needed"],
    "external_referrals": ["Outside organization referrals"],
    "documentation_requirements": ["Documents to complete"],
    "reporting_obligations": ["Mandatory reporting needed"],
    "resource_allocation": ["Resources/funding needed"]
  }},
  "cultural_linguistic_insights": {{
    "language_barriers": ["Communication challenges observed"],
    "cultural_considerations": ["Cultural factors affecting case"],
    "interpreter_needs": ["Language support requirements"],
    "culturally_appropriate_interventions": ["Culturally sensitive approaches"]
  }},
  "case_complexity_analysis": {{
    "complexity_factors": ["What makes this case complex"],
    "stakeholders_involved": ["All parties involved in case"],
    "systems_navigation_needed": ["Which systems client must navigate"],
    "coordination_challenges": ["Inter-agency coordination needs"]
  }},
  "outcome_predictions": {{
    "likely_outcomes_with_intervention": ["Expected positive outcomes"],
    "risks_without_intervention": ["Potential negative outcomes"],
    "success_indicators": ["How to measure success"],
    "timeline_expectations": ["Expected timeframe for progress"]
  }}
}}

ENHANCED TRANSCRIPT (Complete Audio):
{enhanced_transcript}

TRANSLATION:
{translation}

NAMED ENTITIES:
{json.dumps(entities, indent=2)}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

QA SCORES:
{json.dumps(qa_scores, indent=2)}

SUMMARY:
{summary}

Context: This analysis is based on complete high-quality audio recording with both parties clearly captured. Provide comprehensive JSON response only."""

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
            timeout=120  # Longer timeout for comprehensive analysis
        )
        response.raise_for_status()

        data = response.json()

        if 'response' not in data:
            logger.error(f"Invalid response format: {data}")
            raise ValueError("Missing 'response' key in model output")

        # Clean and validate JSON
        try:
            enhanced_insights = json.loads(data['response'])
        except json.JSONDecodeError:
            logger.warning("Trying to sanitize invalid JSON from model...")
            fixed_response = data['response'].strip().split("```json")[-1].split("```")[0].strip()
            enhanced_insights = json.loads(fixed_response)

        logger.info(f"✅ Generated enhanced insights from {audio_quality_info.get('file_size_mb', 'unknown')}MB audio file")
        return enhanced_insights

    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while calling enhanced insight service: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while calling enhanced insight service: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to generate enhanced insights: {str(e)}", exc_info=True)
        raise