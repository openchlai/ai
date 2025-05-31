# insights.py
import json
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)

def generate_case_insights(transcript: str) -> Dict[str, Any]:
    """
    Generate trauma-informed case insights from transcript using Mistral model
    """
    prompt = f"""You are a trauma-informed social worker conducting an expert case analysis. Analyze the following case details and return a comprehensive JSON response with the following structure:

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

Available categories for classification:
- Labor exploitation
- Wage theft
- Workplace abuse
- Human trafficking
- Psychological distress
- Housing insecurity
- Legal aid needed
- Medical attention needed

Instructions:
1. Extract ALL named entities (people, organizations, locations, dates, contact info)
2. Classify the case by category, required interventions, and priority level
3. Provide detailed safety planning measures
4. Specify psychosocial support needs with timeframes
5. List all applicable legal protocols and required documents
6. Outline medical protocols based on survivor needs
7. Conduct thorough risk assessment including protective factors
8. Highlight cultural considerations for service delivery

Case Details:
{transcript}

Response Requirements:
- Be specific, culturally sensitive, and trauma-informed
- Focus on survivor autonomy and empowerment
- Reference Tanzanian context where applicable
- Provide actionable recommendations
- Use clear, concise language
- Return ONLY valid JSON (no commentary)"""

    try:
        response = requests.post(
            'http://192.168.10.6:11434/api/generate',
            json={
                'model': 'mistral',
                'prompt': prompt,
                'stream': False
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        # Parse the JSON response
        insights = json.loads(data['response'])
        return insights
        
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}")
        raise