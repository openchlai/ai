import json
import logging
import re
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def sanitize_json_response(response_text: str) -> str:
    """Extract and clean JSON from LLM response."""
    cleaned = re.sub(r'```json?\s*|\s*```', '', response_text, flags=re.DOTALL).strip()
    json_match = re.search(r'\{[^{}]*"case_summary"[^{}]*\}', cleaned, re.DOTALL)
    if json_match:
        return json_match.group(0)
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    return json_match.group(0) if json_match else cleaned

def call_ollama( prompt: str, endpoint: str = "http://localhost:11434/api/generate", timeout: int = 120) -> Optional[str]:
    """Call Ollama API with retries."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[502, 503, 504, 429])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    model = "mistral"
    payload = {'model': model, 'prompt': prompt, 'stream': False}
    
    try:
        response = session.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return None

def generate_case_insights(
    transcript: str,
    classification_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    VAC Survivor-Centred Case Intelligence Generator

    Pipeline:
        Transcript (ASR/Translation)
            + DistilBERT Classification (Authoritative Categories)
            → ai-service (Structured Decision Support + Reporting JSON)
            → Analytics + AI Decision Panel Output

    Produces JSON compatible with:
        - AI Decision Support Panel
        - CHI reporting
        - UNICEF VAC reporting
        - CPIMS/CPIMS+
        - Government + Donor safeguarding reporting
    """

    # -----------------------------
    # 1. Defaults (Safe Fallbacks)
    # -----------------------------
    main_cat = "Unknown"
    sub_cat = "Unknown"
    intervention = "Unknown"
    priority = "Unknown"
    clf_conf = 0.0

    if classification_results:
        main_cat = classification_results.get("main_category", main_cat)
        sub_cat = classification_results.get("sub_category", sub_cat)
        intervention = classification_results.get("intervention", intervention)
        priority = classification_results.get("priority", priority)
        clf_conf = classification_results.get("confidence", clf_conf)

    # -----------------------------
    # 2. Master Survivor-Centred Prompt
    # -----------------------------
    prompt = f"""
You are a Survivor-Centred Child Protection Decision Support and Reporting System.

This system supports Violence Against Children (VAC) case management.

Your job is to convert a helpline narrative into ONE structured JSON record that supports:

A) AI Decision Support Panel (real-time counsellor guidance)
B) Survivor-centred safeguarding response planning
C) CHI standard helpline reporting
D) UNICEF VAC programme reporting
E) CPIMS / CPIMS+ case management reporting
F) Government and donor accountability reporting

============================================================
SURVIVOR-CENTRED PRINCIPLES (MANDATORY)
- Use neutral, non-blaming language
- Prioritize child safety and confidentiality
- Recommend supportive, rights-based interventions
- Do not include personal opinions or judgment
============================================================

NON-NEGOTIABLE RULES
1. Output MUST be valid JSON only. No markdown, no extra text.
2. ONLY use facts explicitly stated in the transcript. Do NOT infer or speculate.
3. Categories below are authoritative and MUST be copied exactly.
4. Missing information must be represented as null, [] or clearly stated.
5. Boolean flags must be true/false only.
6. If not mentioned, default safeguarding flags to false.
7. Do NOT invent names, places, dates, or details.

------------------------------------------------------------
AUTHORITATIVE CLASSIFICATION (DO NOT CHANGE)

primary_category: "{main_cat}"
sub_category: "{sub_cat}"
intervention: "{intervention}"
priority: "{priority}"
classifier_confidence: {clf_conf:.3f}

------------------------------------------------------------

CASE NARRATIVE
------------------------------------------------------------
{transcript}
------------------------------------------------------------

Return ONE JSON object with EXACTLY this schema:

{{
  "reporting_metadata": {{
    "schema_version": "4.0",
    "generated_by_model": "ai-service",
    "pipeline_stage": "vac_case_intelligence",
    "reporting_compatibility": [
      "CHI",
      "UNICEF_VAC",
      "CPIMS",
      "GOV_STATUTORY",
      "DONOR_NGO"
    ]
  }},

  "ai_decision_panel": {{
    "case_headline": "",
    "immediate_safety_alert": false,
    "safety_alert_reason": null,
    "recommended_next_step": "",
    "recommended_timeframe": "Immediate|<24h|<72h|Routine",
    "survivor_centred_guidance": [
      "Use supportive, non-blaming language",
      "Prioritize the child’s immediate safety",
      "Explain available referral and protection options"
    ]
  }},

  "case_overview": {{
    "risk_level": "Critical|High|Medium|Low",
    "risk_score": 0.0,
    "urgency_window_hours": 0,
    "suggested_disposition": "",
    "rationale_summary": ""
  }},

  "classification": {{
    "primary_category": "{main_cat}",
    "sub_category": "{sub_cat}",
    "intervention": "{intervention}",
    "priority": "{priority}",
    "classifier_confidence": {clf_conf:.3f}
  }},

  "vac_incident_profile": {{
    "violence_type": null,
    "incident_setting": null,
    "perpetrator_relationship": null,
    "incident_reported_as_ongoing": false,
    "child_in_immediate_danger": false
  }},

  "safeguarding_flags": {{
    "physical_violence_flag": false,
    "sexual_violence_flag": false,
    "emotional_psychological_flag": false,
    "neglect_flag": false,
    "exploitation_flag": false,
    "trafficking_flag": false,
    "harmful_practice_flag": false,
    "self_harm_suicide_flag": false
  }},

  "persons_involved": {{
    "survivors": [],
    "alleged_perpetrators": [],
    "callers": [],
    "other_named_persons": []
  }},

  "location_and_context": {{
    "locations_mentioned": [],
    "setting_type": null,
    "school_related": false,
    "household_related": false,
    "community_related": false
  }},

  "service_and_referral_plan": {{
    "immediate_referral_needed": false,
    "mandatory_reporting_required": false,
    "recommended_referrals": [],
    "recommended_services": [],
    "follow_up_required": true,
    "follow_up_timeframe_hours": 0
  }},

  "chi_unicef_reporting_indicators": {{
    "referral_made_or_needed": false,
    "service_provided": null,
    "case_priority_level": "{priority}",
    "vac_category_alignment": "{sub_cat}"
  }},

  "extracted_entities": {{
    "names": [],
    "locations": [],
    "organizations": [],
    "dates": []
  }},

  "case_tags_and_keywords": {{
    "context_tags": [],
    "vulnerability_tags": [],
    "service_tags": [],
    "keywords": []
  }},

  "data_quality": {{
    "insight_confidence_score": 0.0,
    "information_completeness": "Complete|Partial|Minimal",
    "missing_information": [],
    "contradictions_detected": false
  }}
}}

Return ONLY the JSON object.
"""

    # -----------------------------
    # 3. Call ai-service for insights
    # -----------------------------
    logger.info("Calling ai-service for VAC case insights...")
    response_text = call_ollama( prompt)

    if not response_text:
        return {"error": "ai-service unavailable"}

    # -----------------------------
    # 4. Parse + Sanitize JSON
    # -----------------------------
    try:
        insights = json.loads(response_text)

    except json.JSONDecodeError:
        sanitized = sanitize_json_response(response_text)
        insights = json.loads(sanitized)

    # -----------------------------
    # 5. Hard-Enforce Categories (with safe access)
    # -----------------------------
    if "classification" not in insights:
        insights["classification"] = {}
    insights["classification"]["primary_category"] = main_cat
    insights["classification"]["sub_category"] = sub_cat
    insights["classification"]["intervention"] = intervention
    insights["classification"]["priority"] = priority
    insights["classification"]["classifier_confidence"] = clf_conf

    if "chi_unicef_reporting_indicators" not in insights:
        insights["chi_unicef_reporting_indicators"] = {}
    insights["chi_unicef_reporting_indicators"]["case_priority_level"] = priority
    insights["chi_unicef_reporting_indicators"]["vac_category_alignment"] = sub_cat

    # -----------------------------
    # 6. Backward-Compatible Top-Level Fields
    # Required by audio_tasks.py and notification service
    # -----------------------------
    case_overview = insights.get("case_overview", {})
    insights["risk_level"] = case_overview.get("risk_level", "Low")
    insights["suggested_disposition"] = case_overview.get("suggested_disposition", "")
    insights["rationale_summary"] = case_overview.get("rationale_summary", "")
    insights["confidence_score"] = insights.get("data_quality", {}).get("insight_confidence_score", 0.0)

    # Map 'classification' to 'category_suggestions' for backward compatibility
    insights["category_suggestions"] = {
        "primary_category": main_cat,
        "sub_category": sub_cat,
        "intervention": intervention,
        "priority": priority,
        "tags": insights.get("case_tags_and_keywords", {}).get("keywords", [])
    }

    logger.info("Generated VAC survivor-centred insights successfully.")
    return insights