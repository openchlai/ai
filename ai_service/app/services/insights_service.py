# app/services/insights_service.py

from datetime import datetime
import json
import logging
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from ..model_scripts.summarizer_model import summarization_model
from ..model_scripts.ner_model import ner_model
from ..model_scripts.classifier_model import classifier_model

logger = logging.getLogger(__name__)

def _assess_transcript_quality(transcript: str) -> Dict[str, Any]:
    """
    Intelligently assess transcript quality to detect Whisper hallucinations
    and other issues that would make content unsuitable for analysis.
    
    Returns:
        Dict with quality assessment including score (0-100) and recommendations
    """
    if not transcript or not transcript.strip():
        return {
            "quality": "unusable",
            "score": 0,
            "reason": "Empty or whitespace-only transcript",
            "issues": ["empty_content"]
        }
    
    transcript = transcript.strip()
    issues = []
    score = 100  # Start with perfect score, deduct points for issues
    
    # Check for common Whisper hallucination patterns
    hallucination_patterns = [
        (r'\b(\w{1,3})\1{3,}\b', "Repetitive short sequences (e.g., KUKUKUKU...)"),  # KUKUKUKU, lalala, etc.
        (r'\b(\w+)\b(?:\s+\1){4,}', "Same word repeated 5+ times"),  # word word word word word
        (r'^(.{1,50})\1{3,}', "Long pattern repetition"),  # entire phrases repeated
        (r'[^\w\s\.,!?;:\'\"-]{10,}', "Excessive special characters"),  # garbage characters
        (r'\b([A-Z]{2,})\1+\b', "Repeated uppercase sequences")  # ABCABC, XYZXYZ
    ]
    
    for pattern, description in hallucination_patterns:
        if re.search(pattern, transcript, re.IGNORECASE):
            issues.append(f"hallucination_pattern: {description}")
            score -= 25  # Heavy penalty for hallucinations
    
    # Check transcript length and content diversity
    length = len(transcript)
    if length < 20:
        issues.append("very_short_content")
        score -= 30
    elif length < 50:
        issues.append("short_content") 
        score -= 15
    
    # Check character diversity (low diversity = likely repetitive)
    unique_chars = len(set(transcript.lower()))
    char_diversity_ratio = unique_chars / length if length > 0 else 0
    
    if char_diversity_ratio < 0.1:  # Less than 10% unique characters
        issues.append("low_character_diversity")
        score -= 20
    elif char_diversity_ratio < 0.2:
        issues.append("moderate_character_diversity")
        score -= 10
    
    # Check word diversity 
    words = transcript.lower().split()
    if words:
        unique_words = len(set(words))
        word_diversity_ratio = unique_words / len(words)
        
        if word_diversity_ratio < 0.3:  # Less than 30% unique words
            issues.append("low_word_diversity")
            score -= 15
        elif word_diversity_ratio < 0.5:
            issues.append("moderate_word_diversity") 
            score -= 5
    
    # Check for meaningful content indicators
    meaningful_patterns = [
        r'\b(hello|hi|good\s+(morning|afternoon|evening))\b',  # Greetings
        r'\b(thank\s+you|please|excuse\s+me)\b',  # Politeness
        r'\b(problem|issue|help|support|question)\b',  # Service context
        r'\b(name|address|phone|number|email)\b',  # Contact info
        r'\?',  # Questions
    ]
    
    meaningful_indicators = sum(1 for pattern in meaningful_patterns 
                              if re.search(pattern, transcript, re.IGNORECASE))
    
    if meaningful_indicators == 0 and len(words) > 10:
        issues.append("no_meaningful_content_indicators")
        score -= 15
    
    # Final quality determination
    if score >= 70:
        quality = "good"
    elif score >= 40:
        quality = "fair" 
    else:
        quality = "unusable"
    
    # Override: If major hallucination patterns detected, mark as unusable
    major_hallucination_issues = [issue for issue in issues if "hallucination_pattern" in issue]
    if major_hallucination_issues and score < 60:
        quality = "unusable"
        score = min(score, 30)  # Cap at 30 for hallucinated content
    
    return {
        "quality": quality,
        "score": max(0, score),  # Ensure score doesn't go negative
        "issues": issues,
        "reason": f"Quality assessment: {quality} ({score}/100)" + 
                 (f" - Issues: {', '.join(issues)}" if issues else ""),
        "transcript_stats": {
            "length": length,
            "word_count": len(words) if words else 0,
            "unique_words": len(set(words)) if words else 0,
            "char_diversity": round(char_diversity_ratio, 3),
            "word_diversity": round(unique_words / len(words) if words else 0, 3),
            "meaningful_indicators": meaningful_indicators
        }
    }

def generate_case_insights(
    transcript: str, 
    summary: str = None, 
    entities: Dict = None, 
    classification: Dict = None,
    qa_scores: Dict = None
) -> Dict[str, Any]:
    """
    Generate trauma-informed case insights from transcript using pre-computed results when available.
    Intelligently handles poor quality transcripts (e.g., Whisper hallucinations like 'KUKUKUKU...').
    
    Args:
        transcript: The call transcript text
        summary: Pre-computed summary (optional, will compute if not provided)
        entities: Pre-computed NER results (optional, will compute if not provided)
        classification: Pre-computed classification (optional, will compute if not provided)
        qa_scores: Pre-computed QA scores (optional)
    
    Returns:
        Dictionary with case insights or unusable content response
    """
    
    # Step 0: Intelligent content quality assessment
    content_quality = _assess_transcript_quality(transcript)
    
    if content_quality["quality"] == "unusable":
        logger.warning(f"Audio quality unusable for insights generation")
        return {
            "status": "unusable_content",
            "reason": "Poor audio quality",
            "case_summary": "Unable to generate insights due to poor audio quality",
            "analysis_metadata": {
                "transcript_length": len(transcript),
                "quality_score": content_quality["score"],
                "processing_attempted": False,
                "audio_issue": True
            }
        }
    
    # Use pre-computed results when available, otherwise compute them
    if summary is None:
        try:
            summary = summarization_model.summarize(transcript)
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            summary = transcript[:1000]  # fallback: truncate raw transcript

    if entities is None:
        try:
            entities = ner_model.extract_entities(transcript)
        except Exception as e:
            logger.error(f"NER failed: {e}")
            entities = {}

    if classification is None:
        try:
            case_classification = classifier_model.classify(transcript)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            case_classification = {
                "category": [],
                "interventions_needed": [],
                "priority_level": "medium"
            }
    else:
        case_classification = classification

    # Build enhanced prompt with quality assessment and pre-computed data
    quality_context = f"""TRANSCRIPT QUALITY ASSESSMENT:
- Quality Level: {content_quality['quality']} 
- Quality Score: {content_quality['score']}/100
- Length: {len(transcript)} characters
- Issues Detected: {', '.join(content_quality.get('issues', [])) or 'None'}
- Confidence in Analysis: {'High' if content_quality['score'] >= 80 else 'Medium' if content_quality['score'] >= 60 else 'Low'}
"""

    qa_context = ""
    if qa_scores:
        qa_context = f"""\nQUALITY ASSURANCE METRICS:
{json.dumps(qa_scores, indent=2)}
"""

    prompt = f"""You are a trauma-informed social worker conducting an expert case analysis. The transcript quality has been assessed and pre-processed. Generate a comprehensive JSON response adapting your analysis confidence level based on transcript quality.

{quality_context}{qa_context}

Generate a comprehensive JSON response with the following structure:

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
        
        # Add quality metadata to insights
        insights["analysis_metadata"] = {
            "transcript_quality_score": content_quality["score"],
            "quality_level": content_quality["quality"],
            "quality_issues": content_quality.get("issues", []),
            "used_precomputed_data": {
                "summary": summary is not None,
                "entities": entities is not None, 
                "classification": classification is not None,
                "qa_scores": qa_scores is not None
            },
            "processing_timestamp": datetime.now().isoformat()
        }

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