# Audio Processing Insights

> **Note:** Response structures may vary slightly based on API version and configuration.
> This documentation reflects API version 0.1.0 running in production mode.

## Overview

The `/audio/process` endpoint returns comprehensive AI-generated insights about call transcripts. This guide explains every field in the response and how to interpret them.

---

## Quick Reference

```bash
# Process audio and get insights
curl -X POST "http://localhost:8125/audio/process" \
  -F "audio=@call_recording.wav" \
  -F "language=sw" \
  -F "include_translation=true" \
  -F "include_insights=true"

# Poll for results
curl -X GET "http://localhost:8125/audio/task/{task_id}"
```

---

## Complete Response Structure

```json
{
  "task_id": "abc123...",
  "status": "completed",
  "progress": 100,
  "result": {
    // 1. TRANSCRIPTION DATA
    "transcript": "...",
    "translation": "...",
    "audio_info": {...},
    "nlp_processing_info": {...},

    // 2. NAMED ENTITIES (NER)
    "entities": {...},

    // 3. CASE CLASSIFICATION
    "classification": {...},

    // 4. QUALITY ASSURANCE SCORES
    "qa_scores": {...},

    // 5. CALL SUMMARY
    "summary": "...",

    // 6. PROCESSING METADATA
    "processing_steps": {...},
    "pipeline_info": {...},

    // 7. AI-GENERATED INSIGHTS (VAC Survivor-Centred)
    "insights": {
      "reporting_metadata": {...},
      "ai_decision_panel": {...},
      "case_overview": {...},
      "classification": {...},
      "vac_incident_profile": {...},
      "safeguarding_flags": {...},
      "persons_involved": {...},
      "location_and_context": {...},
      "service_and_referral_plan": {...},
      "chi_unicef_reporting_indicators": {...},
      "extracted_entities": {...},
      "case_tags_and_keywords": {...},
      "data_quality": {...},
      "processing_metadata": {...},
      // Backward-compatible fields
      "risk_level": "...",
      "suggested_disposition": "...",
      "category_suggestions": {...}
    }
  }
}
```

---

## 1. Transcription Data

### 1.1 Transcription (Swahili)

**Field:** `result.transcription`
**Type:** String
**Description:** Full Swahili transcription of the audio file.

**Example:**
```json
{
  "transcription": "Habari, hii ni 116 helpline ya watoto. Unaweza kunisaidia vipi leo? Mtoto wangu amepotea pale Central Park..."
}
```

**Model Used:** `openchs/asr-whisper-helpline-sw-v1` (Whisper large-v2 fine-tuned for Swahili child helpline conversations)

**Use Cases:**
- Archive original language conversation
- Verify transcription accuracy
- Feed into downstream Swahili text analysis tools

---

### 1.2 Translation (English)

**Field:** `result.translation`
**Type:** String
**Description:** English translation of the Swahili transcript.

**Example:**
```json
{
  "translation": "Hello, this is 116 children's helpline. How can I help you today? My child is missing at Central Park..."
}
```

**Model Used:** `openchs/sw-en-opus-mt-mul-en-v1` (MarianMT fine-tuned for Swahili→English translation)

**Use Cases:**
- Enable non-Swahili speakers to understand calls
- Feed English text to downstream models (NER, Classification, QA)
- Generate English documentation

---

### 1.3 Language

**Field:** `result.language`
**Type:** String
**Description:** Detected/specified language code.

**Example:**
```json
{
  "language": "sw"
}
```

**Possible Values:**
- `sw` - Swahili
- `en` - English
- `auto` - Auto-detected
- Other ISO 639-1 codes for 99+ supported languages

---

### 1.4 Audio Info

**Field:** `result.audio_info`
**Type:** Object
**Description:** Metadata about the processed audio file.

**Example:**
```json
{
  "audio_info": {
    "filename": "call_recording.wav",
    "duration_seconds": 120.5,
    "file_size_mb": 2.34,
    "format": "wav",
    "sample_rate": 16000,
    "channels": 1
  }
}
```

**Fields:**
- `filename`: Original file name
- `duration_seconds`: Audio duration
- `file_size_mb`: File size
- `format`: Audio format (wav, mp3, etc.)
- `sample_rate`: Sample rate in Hz
- `channels`: Number of audio channels (1=mono, 2=stereo)

---

## 2. Named Entity Recognition (NER)

### 2.1 Entities Array

**Field:** `result.entities`
**Type:** Array of Entity objects
**Description:** Extracted entities from the translated text with labels and confidence scores.

**Example:**
```json
{
  "entities": [
    {
      "text": "Central Park",
      "label": "LANDMARK",
      "start": 67,
      "end": 79,
      "confidence": 0.9234
    },
    {
      "text": "John Doe",
      "label": "PERPETRATOR",
      "start": 145,
      "end": 153,
      "confidence": 0.8876
    },
    {
      "text": "116",
      "label": "PHONE_NUMBER",
      "start": 8,
      "end": 11,
      "confidence": 0.9901
    },
    {
      "text": "5 years",
      "label": "AGE",
      "start": 102,
      "end": 109,
      "confidence": 0.9123
    }
  ]
}
```

**Model Used:** `openchs/ner_distillbert_v1` (DistilBERT fine-tuned for helpline entity extraction)

---

### 2.2 Entity Labels

| Label | Description | Examples |
|-------|-------------|----------|
| **PERPETRATOR** | Person causing harm | "John Doe", "The teacher", "My uncle" |
| **VICTIM** | Person being harmed | "The child", "My daughter", "8-year-old boy" |
| **NAME** | General person names | "Mary", "Ahmed", "Sarah" |
| **LOCATION** | General locations | "Dar es Salaam", "Mwanza", "Tanzania" |
| **LANDMARK** | Specific places | "Central Park", "St. Joseph Hospital", "Main Market" |
| **PHONE_NUMBER** | Phone numbers | "116", "+255 123 456 789", "0712345678" |
| **AGE** | Ages mentioned | "5 years old", "15 years", "infant" |
| **GENDER** | Gender references | "male", "female", "girl", "boy" |

---

### 2.3 Entity Confidence Scores

**Range:** 0.0 - 1.0
**Interpretation:**

| Confidence | Interpretation | Action |
|------------|----------------|--------|
| **> 0.90** | Very High - Highly reliable | Use as-is |
| **0.75 - 0.90** | High - Reliable | Use with minimal review |
| **0.60 - 0.75** | Medium - Moderately reliable | Review recommended |
| **< 0.60** | Low - Uncertain | Manual verification required |

---

### 2.4 Entity Use Cases

**Automatic Alerts:**
```python
# Alert on specific locations
for entity in entities:
    if entity['label'] == 'LANDMARK' and entity['confidence'] > 0.85:
        alert_nearby_services(entity['text'])
```

**Victim/Perpetrator Tracking:**
```python
# Extract key parties
victims = [e for e in entities if e['label'] == 'VICTIM']
perpetrators = [e for e in entities if e['label'] == 'PERPETRATOR']
```

**Phone Number Extraction:**
```python
# Get all phone numbers for follow-up
phones = [e['text'] for e in entities if e['label'] == 'PHONE_NUMBER']
```

---

## 3. Case Classification

### 3.1 Classification Object

**Field:** `result.classification`
**Type:** Object
**Description:** Multi-task classification with main category, sub-categories, intervention, and priority.

**Example:**
```json
{
  "classification": {
    "main_category": "VANE",
    "sub_category": "Physical Abuse",
    "sub_category_2": "Neglect",
    "intervention": "Referred",
    "priority": "high",
    "confidence_scores": {
      "main_category": 0.8923,
      "sub_category": 0.8456,
      "sub_category_2": 0.7234,
      "intervention": 0.8123,
      "priority": 0.9012
    }
  }
}
```

**Model Used:** `openchs/cls-gbv-distilbert-v1` (Multi-task DistilBERT for GBV case classification)

---

### 3.2 Main Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **VANE** | Violence Against Children | Physical abuse, sexual abuse, emotional abuse |
| **GBV** | Gender-Based Violence | Domestic violence, sexual harassment |
| **Child Maintenance & Custody** | Legal/financial support issues | Unpaid child support, custody disputes |
| **Disability** | Disability-related concerns | Access to services, discrimination |
| **Nutrition** | Nutrition and health | Malnutrition, feeding problems |
| **Advice and Counselling** | General advice requests | Parenting tips, education advice |
| **Information** | Information requests | Service locations, contact info |

---

### 3.3 Priority Levels

| Priority | Description | Response Time | Action Required |
|----------|-------------|---------------|-----------------|
| **urgent** | Immediate danger | < 5 minutes | Immediate escalation, emergency services |
| **high** | Serious situation | < 1 hour | Supervisor notification, priority handling |
| **medium** | Important but not critical | < 24 hours | Standard follow-up procedures |
| **low** | General inquiry | < 72 hours | Normal processing |

---

### 3.4 Interventions

| Intervention | Description | Example Actions |
|--------------|-------------|-----------------|
| **Referred** | Case referred to external service | Police, hospital, social services |
| **Counselling** | Counselling provided | Emotional support, crisis intervention |
| **Signposting** | Directed to appropriate resources | Contact numbers, service locations |
| **Awareness/Information Provided** | General information given | Educational content, resource lists |

---

### 3.5 Classification Use Cases

**Priority-Based Routing:**
```python
classification = result['classification']

if classification['priority'] in ['urgent', 'high']:
    escalate_to_supervisor(call_id)
    send_sms_alert(supervisor_phone)
```

**Automatic Referrals:**
```python
if classification['main_category'] == 'VANE':
    if classification['sub_category'] in ['Sexual Abuse', 'Physical Abuse']:
        auto_refer_to_police(call_details)
```

**Performance Metrics:**
```python
# Track intervention effectiveness
interventions_by_category = {}
for call in calls:
    category = call['classification']['main_category']
    intervention = call['classification']['intervention']
    track_outcome(category, intervention)
```

---

## 4. Quality Assurance (QA) Scores

### 4.1 QA Evaluations Object

**Field:** `result.qa_evaluations`
**Type:** Object
**Description:** Detailed QA scores evaluating agent performance across 17 sub-metrics grouped into 6 main criteria.

**Example:**
```json
{
  "qa_evaluations": {
    "opening": {
      "score": 8.5,
      "sub_scores": {
        "greeting": 9.0,
        "identification": 8.0,
        "offer_assistance": 8.5
      },
      "feedback": "Good opening overall. Agent identified themselves and offered help promptly."
    },
    "listening": {
      "score": 7.2,
      "sub_scores": {
        "empathy": 8.0,
        "active_listening": 7.5,
        "clarification": 6.0
      },
      "feedback": "Agent showed empathy but could ask more clarifying questions."
    },
    "proactiveness": {
      "score": 6.8,
      "sub_scores": {
        "anticipation": 7.0,
        "suggestion": 6.5
      },
      "feedback": "Agent addressed immediate concerns but could suggest preventive measures."
    },
    "resolution": {
      "score": 8.0,
      "sub_scores": {
        "problem_solving": 8.5,
        "follow_up": 7.5
      },
      "feedback": "Effective problem-solving. Follow-up plan provided."
    },
    "hold": {
      "score": 9.0,
      "sub_scores": {
        "permission": 9.0,
        "explanation": 9.0,
        "duration": 9.0
      },
      "feedback": "Excellent hold procedure compliance."
    },
    "closing": {
      "score": 8.7,
      "sub_scores": {
        "summary": 9.0,
        "next_steps": 8.5,
        "farewell": 8.5
      },
      "feedback": "Call closed professionally with clear next steps."
    },
    "overall_score": 8.0,
    "overall_feedback": "Good call handling overall. Agent demonstrated empathy and resolved the issue effectively."
  }
}
```

**Model Used:** `openchs/qa-helpline-distilbert-v1` (DistilBERT fine-tuned for helpline QA evaluation)

---

### 4.2 QA Criteria Breakdown

#### Opening (3 sub-metrics)
- **greeting**: Proper greeting (0-10)
- **identification**: Agent identified themselves (0-10)
- **offer_assistance**: Offered help promptly (0-10)

#### Listening (3 sub-metrics)
- **empathy**: Demonstrated empathy (0-10)
- **active_listening**: Engaged actively (0-10)
- **clarification**: Asked clarifying questions (0-10)

#### Proactiveness (2 sub-metrics)
- **anticipation**: Anticipated caller needs (0-10)
- **suggestion**: Made helpful suggestions (0-10)

#### Resolution (2 sub-metrics)
- **problem_solving**: Resolved the issue (0-10)
- **follow_up**: Provided follow-up plan (0-10)

#### Hold (3 sub-metrics)
- **permission**: Asked permission before hold (0-10)
- **explanation**: Explained reason for hold (0-10)
- **duration**: Kept hold time reasonable (0-10)

#### Closing (3 sub-metrics)
- **summary**: Summarized the call (0-10)
- **next_steps**: Clarified next steps (0-10)
- **farewell**: Professional farewell (0-10)

---

### 4.3 Score Interpretation

| Score Range | Performance Level | Action Required |
|-------------|-------------------|-----------------|
| **9.0 - 10.0** | Excellent | None - exemplary performance |
| **7.0 - 8.9** | Good | Continue current practices |
| **5.0 - 6.9** | Acceptable | Minor improvements needed |
| **3.0 - 4.9** | Poor | Training recommended |
| **0.0 - 2.9** | Very Poor | Immediate intervention required |

---

### 4.4 QA Use Cases

**Agent Performance Tracking:**
```python
qa_scores = result['qa_evaluations']

# Identify weak areas
weak_areas = {
    criteria: scores['score']
    for criteria, scores in qa_scores.items()
    if scores['score'] < 7.0 and criteria != 'overall_score'
}

if weak_areas:
    schedule_training(agent_id, list(weak_areas.keys()))
```

**Quality Assurance Reports:**
```python
# Generate monthly QA report
monthly_scores = {
    'opening': [],
    'listening': [],
    'resolution': [],
    ...
}

for call in monthly_calls:
    qa = call['qa_evaluations']
    for criterion in monthly_scores:
        monthly_scores[criterion].append(qa[criterion]['score'])

# Calculate averages
average_scores = {
    criterion: sum(scores) / len(scores)
    for criterion, scores in monthly_scores.items()
}
```

**Real-Time Agent Feedback:**
```python
# Send real-time feedback to agents
if qa_scores['overall_score'] < 5.0:
    send_supervisor_alert(call_id, "Low QA score detected")

if qa_scores['empathy']['score'] < 6.0:
    send_agent_tip(agent_id, "Remember to acknowledge caller's feelings")
```

---

## 5. Call Summary

### 5.1 Summary Field

**Field:** `result.summary`
**Type:** String
**Description:** Concise AI-generated summary of the call conversation.

**Example:**
```json
{
  "summary": "Caller reported a missing child at Central Park. Child is 5 years old, wearing a red shirt. Police were contacted. Caller was advised to stay at the location and was provided with follow-up contact information."
}
```

**Model Used:** `openchs/sum-flan-t5-base-synthetic-v1` (FLAN-T5-base fine-tuned for helpline call summarization)

---

### 5.2 Summary Characteristics

- **Length:** Typically 2-5 sentences
- **Content:** Caller's issue, key details, actions taken, next steps
- **Style:** Objective, factual, concise
- **Language:** English

---

### 5.3 Summary Use Cases

**Quick Reference:**
```python
# Display summary on dashboard
dashboard_entry = {
    'call_id': call_id,
    'summary': result['summary'],
    'priority': result['classification']['priority'],
    'timestamp': result['timestamp']
}
```

**Case Documentation:**
```python
# Auto-populate case notes
case_notes = f"""
Call ID: {call_id}
Date: {timestamp}
Summary: {result['summary']}
Classification: {classification['main_category']} - {classification['sub_category']}
Priority: {classification['priority']}
Intervention: {classification['intervention']}
"""
save_case_notes(case_notes)
```

**Search and Retrieval:**
```python
# Index summaries for full-text search
index_document(
    doc_id=call_id,
    content=result['summary'],
    metadata={
        'category': classification['main_category'],
        'priority': classification['priority']
    }
)
```

---

## 6. Processing Metadata

### 6.1 Processing Time

**Field:** `result.processing_time`
**Type:** Float (seconds)
**Description:** Total time taken to process the audio file.

**Example:**
```json
{
  "processing_time": 45.23
}
```

**Typical Times:**
- **Short calls (< 30s)**: 10-20 seconds
- **Medium calls (30s-2min)**: 20-45 seconds
- **Long calls (> 2min)**: 45-120 seconds

---

### 6.2 Model Info

**Field:** `result.model_info`
**Type:** Object
**Description:** Information about all models used in processing.

**Example:**
```json
{
  "model_info": {
    "whisper": {
      "model_id": "openchs/asr-whisper-helpline-sw-v1",
      "version": "large-v2",
      "device": "cuda"
    },
    "translator": {
      "model_id": "openchs/sw-en-opus-mt-mul-en-v1",
      "version": "v1"
    },
    "ner": {
      "model_id": "openchs/ner_distillbert_v1",
      "version": "v1"
    },
    "classifier": {
      "model_id": "openchs/cls-gbv-distilbert-v1",
      "version": "v1"
    },
    "qa": {
      "model_id": "openchs/qa-helpline-distilbert-v1",
      "version": "v1"
    },
    "summarizer": {
      "model_id": "openchs/sum-flan-t5-base-synthetic-v1",
      "version": "v1"
    }
  }
}
```

---

### 6.3 Timestamp

**Field:** `result.timestamp`
**Type:** ISO-8601 timestamp string
**Description:** When the processing was completed.

**Example:**
```json
{
  "timestamp": "2026-01-20T10:30:45.123456"
}
```

---

## 7. AI-Generated Insights (VAC Survivor-Centred)

The `insights` object provides comprehensive AI-powered analysis of the call using a **VAC (Violence Against Children) Survivor-Centred** approach. This is generated when `include_insights=true` is passed to the `/audio/process` endpoint.

**Model Used:** AI-Service Models for advanced reasoning and analysis

### 7.1 Complete Insights Structure

```json
{
  "insights": {
    "reporting_metadata": {...},
    "ai_decision_panel": {...},
    "case_overview": {...},
    "classification": {...},
    "vac_incident_profile": {...},
    "safeguarding_flags": {...},
    "persons_involved": {...},
    "location_and_context": {...},
    "service_and_referral_plan": {...},
    "chi_unicef_reporting_indicators": {...},
    "extracted_entities": {...},
    "case_tags_and_keywords": {...},
    "data_quality": {...},
    "processing_metadata": {...},
    // Backward-compatible fields
    "risk_level": "Critical|High|Medium|Low",
    "suggested_disposition": "...",
    "rationale_summary": "...",
    "confidence_score": 0.0,
    "category_suggestions": {...}
  }
}
```

---

### 7.2 Reporting Metadata

**Field:** `insights.reporting_metadata`
**Type:** Object
**Description:** Schema versioning and compatibility information for reporting systems.

**Example:**
```json
{
  "reporting_metadata": {
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
  }
}
```

| Field | Description |
|-------|-------------|
| `schema_version` | Version of the insights schema |
| `generated_by_model` | AI model that generated the insights |
| `pipeline_stage` | Processing pipeline stage identifier |
| `reporting_compatibility` | List of compatible reporting frameworks |

---

### 7.3 AI Decision Panel

**Field:** `insights.ai_decision_panel`
**Type:** Object
**Description:** Real-time decision support for counsellors handling the call.

**Example:**
```json
{
  "ai_decision_panel": {
    "case_headline": "Child nutrition concerns reported",
    "immediate_safety_alert": false,
    "safety_alert_reason": null,
    "recommended_next_step": "Provide referral information",
    "recommended_timeframe": "Immediate|<24h|<72h|Routine",
    "survivor_centred_guidance": [
      "Use supportive, non-blaming language",
      "Prioritize the child's immediate safety",
      "Explain available referral and protection options"
    ]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `case_headline` | String | Brief headline summarizing the case |
| `immediate_safety_alert` | Boolean | Whether immediate safety action is needed |
| `safety_alert_reason` | String/null | Reason for safety alert if applicable |
| `recommended_next_step` | String | AI-recommended immediate action |
| `recommended_timeframe` | String | Urgency timeframe for response |
| `survivor_centred_guidance` | Array | Guidance for survivor-centred approach |

---

### 7.4 Case Overview

**Field:** `insights.case_overview`
**Type:** Object
**Description:** High-level risk assessment and disposition recommendations.

**Example:**
```json
{
  "case_overview": {
    "risk_level": "High",
    "risk_score": 0.75,
    "urgency_window_hours": 24,
    "suggested_disposition": "Immediate police referral and child protection services involvement",
    "rationale_summary": "The caller expresses concerns about a child's safety with indicators of ongoing abuse."
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `risk_level` | String | Critical, High, Medium, or Low |
| `risk_score` | Float | Numeric risk score (0.0 - 1.0) |
| `urgency_window_hours` | Integer | Recommended response window in hours |
| `suggested_disposition` | String | Recommended action/next steps |
| `rationale_summary` | String | Explanation for the assessment |

#### Risk Level Interpretation

| Risk Level | Description | Recommended Response Time |
|------------|-------------|---------------------------|
| **Critical** | Immediate danger to child | < 5 minutes, emergency services |
| **High** | Serious situation requiring urgent attention | < 1 hour |
| **Medium** | Important but not immediately dangerous | < 24 hours |
| **Low** | General inquiry or low-risk situation | < 72 hours |

---

### 7.5 Classification (AI-Enhanced)

**Field:** `insights.classification`
**Type:** Object
**Description:** Classification results from the DistilBERT model, preserved in insights for consistency.

**Example:**
```json
{
  "classification": {
    "primary_category": "VANE",
    "sub_category": "Physical Abuse",
    "intervention": "Referred",
    "priority": "1",
    "classifier_confidence": 0.89
  }
}
```

---

### 7.6 VAC Incident Profile

**Field:** `insights.vac_incident_profile`
**Type:** Object
**Description:** Detailed Violence Against Children incident characteristics.

**Example:**
```json
{
  "vac_incident_profile": {
    "violence_type": "physical",
    "incident_setting": "home",
    "perpetrator_relationship": "parent",
    "incident_reported_as_ongoing": true,
    "child_in_immediate_danger": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `violence_type` | String/null | Type of violence (physical, sexual, emotional, neglect) |
| `incident_setting` | String/null | Where the incident occurred |
| `perpetrator_relationship` | String/null | Relationship to the child |
| `incident_reported_as_ongoing` | Boolean | Whether abuse is ongoing |
| `child_in_immediate_danger` | Boolean | Whether child is currently in danger |

---

### 7.7 Safeguarding Flags

**Field:** `insights.safeguarding_flags`
**Type:** Object
**Description:** Boolean flags indicating presence of specific safeguarding concerns.

**Example:**
```json
{
  "safeguarding_flags": {
    "physical_violence_flag": true,
    "sexual_violence_flag": false,
    "emotional_psychological_flag": true,
    "neglect_flag": false,
    "exploitation_flag": false,
    "trafficking_flag": false,
    "harmful_practice_flag": false,
    "self_harm_suicide_flag": false
  }
}
```

| Flag | Description |
|------|-------------|
| `physical_violence_flag` | Physical abuse or violence detected |
| `sexual_violence_flag` | Sexual abuse or violence detected |
| `emotional_psychological_flag` | Emotional or psychological abuse detected |
| `neglect_flag` | Child neglect detected |
| `exploitation_flag` | Child exploitation detected |
| `trafficking_flag` | Human trafficking indicators detected |
| `harmful_practice_flag` | Harmful traditional practices detected |
| `self_harm_suicide_flag` | Self-harm or suicide risk detected |

---

### 7.8 Persons Involved

**Field:** `insights.persons_involved`
**Type:** Object
**Description:** Categorized list of persons mentioned in the call.

**Example:**
```json
{
  "persons_involved": {
    "survivors": ["Mary", "8-year-old girl"],
    "alleged_perpetrators": ["Uncle John"],
    "callers": ["Mother"],
    "other_named_persons": ["Teacher Mrs. Smith"]
  }
}
```

| Field | Description |
|-------|-------------|
| `survivors` | Children or persons who experienced harm |
| `alleged_perpetrators` | Persons alleged to have caused harm |
| `callers` | Persons who made the call |
| `other_named_persons` | Other relevant persons mentioned |

---

### 7.9 Location and Context

**Field:** `insights.location_and_context`
**Type:** Object
**Description:** Geographic and contextual information about the case.

**Example:**
```json
{
  "location_and_context": {
    "locations_mentioned": ["Kibera", "Nairobi"],
    "setting_type": "home",
    "school_related": false,
    "household_related": true,
    "community_related": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `locations_mentioned` | Array | Places mentioned in the call |
| `setting_type` | String/null | Primary setting (home, school, community) |
| `school_related` | Boolean | Whether case involves school setting |
| `household_related` | Boolean | Whether case involves home setting |
| `community_related` | Boolean | Whether case involves community setting |

---

### 7.10 Service and Referral Plan

**Field:** `insights.service_and_referral_plan`
**Type:** Object
**Description:** AI-recommended services and referral pathway.

**Example:**
```json
{
  "service_and_referral_plan": {
    "immediate_referral_needed": true,
    "mandatory_reporting_required": true,
    "recommended_referrals": ["Police", "Child Protection Services"],
    "recommended_services": ["Counselling", "Medical examination"],
    "follow_up_required": true,
    "follow_up_timeframe_hours": 24
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `immediate_referral_needed` | Boolean | Whether immediate referral is required |
| `mandatory_reporting_required` | Boolean | Whether mandatory reporting applies |
| `recommended_referrals` | Array | List of recommended referral agencies |
| `recommended_services` | Array | List of recommended services |
| `follow_up_required` | Boolean | Whether follow-up is needed |
| `follow_up_timeframe_hours` | Integer | Recommended follow-up timeframe |

---

### 7.11 CHI/UNICEF Reporting Indicators

**Field:** `insights.chi_unicef_reporting_indicators`
**Type:** Object
**Description:** Standardized indicators for Child Helpline International and UNICEF reporting.

**Example:**
```json
{
  "chi_unicef_reporting_indicators": {
    "referral_made_or_needed": true,
    "service_provided": "Counselling",
    "case_priority_level": "1",
    "vac_category_alignment": "Physical Abuse"
  }
}
```

| Field | Description |
|-------|-------------|
| `referral_made_or_needed` | Whether referral was made or is needed |
| `service_provided` | Primary service provided during call |
| `case_priority_level` | Priority level for reporting |
| `vac_category_alignment` | VAC category for UNICEF alignment |

---

### 7.12 Extracted Entities

**Field:** `insights.extracted_entities`
**Type:** Object
**Description:** Key entities extracted by AI analysis.

**Example:**
```json
{
  "extracted_entities": {
    "names": ["John Doe", "Mary Smith"],
    "locations": ["Kibera", "Nairobi Hospital"],
    "organizations": ["Police Department", "Social Services"],
    "dates": ["2026-01-15", "last week"]
  }
}
```

---

### 7.13 Case Tags and Keywords

**Field:** `insights.case_tags_and_keywords`
**Type:** Object
**Description:** Categorized tags for case indexing and search.

**Example:**
```json
{
  "case_tags_and_keywords": {
    "context_tags": ["domestic", "family"],
    "vulnerability_tags": ["young_child", "single_parent"],
    "service_tags": ["counselling", "referral"],
    "keywords": ["abuse", "safety", "protection"]
  }
}
```

| Field | Description |
|-------|-------------|
| `context_tags` | Tags describing case context |
| `vulnerability_tags` | Tags identifying vulnerabilities |
| `service_tags` | Tags for service categorization |
| `keywords` | General keywords for search |

---

### 7.14 Data Quality

**Field:** `insights.data_quality`
**Type:** Object
**Description:** Quality assessment of the AI analysis.

**Example:**
```json
{
  "data_quality": {
    "insight_confidence_score": 0.85,
    "information_completeness": "Complete",
    "missing_information": [],
    "contradictions_detected": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `insight_confidence_score` | Float | Overall confidence in the analysis (0.0-1.0) |
| `information_completeness` | String | Complete, Partial, or Minimal |
| `missing_information` | Array | List of missing key information |
| `contradictions_detected` | Boolean | Whether contradictions were found |

---

### 7.15 Processing Metadata

**Field:** `insights.processing_metadata`
**Type:** Object
**Description:** Technical metadata about insights generation.

**Example:**
```json
{
  "processing_metadata": {
    "processing_time_ms": 27524,
    "timestamp": "2026-01-29T08:34:00.929832+00:00",
    "text_analyzed": "translation",
    "text_length": 136
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `processing_time_ms` | Integer | Time to generate insights in milliseconds |
| `timestamp` | String | ISO-8601 timestamp of generation |
| `text_analyzed` | String | Source text used ("translation" or "transcript") |
| `text_length` | Integer | Character count of analyzed text |

---

### 7.16 Backward-Compatible Fields

For compatibility with existing integrations, the following top-level fields are also available:

| Field | Type | Description |
|-------|------|-------------|
| `risk_level` | String | Same as `case_overview.risk_level` |
| `suggested_disposition` | String | Same as `case_overview.suggested_disposition` |
| `rationale_summary` | String | Same as `case_overview.rationale_summary` |
| `confidence_score` | Float | Same as `data_quality.insight_confidence_score` |
| `category_suggestions` | Object | Classification with tags |

**Example:**
```json
{
  "risk_level": "High",
  "suggested_disposition": "Immediate police referral",
  "rationale_summary": "Child safety concerns identified",
  "confidence_score": 0.85,
  "category_suggestions": {
    "primary_category": "VANE",
    "sub_category": "Physical Abuse",
    "intervention": "Referred",
    "priority": "1",
    "tags": ["abuse", "urgent", "referral"]
  }
}
```

---

### 7.17 Insights Use Cases

**Risk-Based Routing:**
```python
insights = result['insights']

# Use backward-compatible field
if insights['risk_level'] == 'Critical':
    escalate_to_emergency(call_id)
    notify_supervisor_immediately(call_details)
elif insights['risk_level'] == 'High':
    escalate_to_supervisor(call_id)

# Or use nested structure
if insights['case_overview']['risk_level'] == 'Critical':
    escalate_to_emergency(call_id)
```

**Safety Alert Handling:**
```python
if insights['ai_decision_panel']['immediate_safety_alert']:
    reason = insights['ai_decision_panel']['safety_alert_reason']
    trigger_emergency_protocol(call_id, reason)
```

**Safeguarding Flag Processing:**
```python
flags = insights['safeguarding_flags']

if flags['sexual_violence_flag'] or flags['physical_violence_flag']:
    mandatory_report_required = True
    notify_child_protection_services(call_id)

if flags['self_harm_suicide_flag']:
    escalate_to_crisis_team(call_id)
```

**Referral Automation:**
```python
plan = insights['service_and_referral_plan']

if plan['immediate_referral_needed']:
    for referral in plan['recommended_referrals']:
        create_referral_ticket(call_id, referral)

if plan['mandatory_reporting_required']:
    initiate_mandatory_report(call_id)
```

**UNICEF/CHI Reporting:**
```python
indicators = insights['chi_unicef_reporting_indicators']

report_data = {
    'case_id': call_id,
    'priority': indicators['case_priority_level'],
    'vac_category': indicators['vac_category_alignment'],
    'referral_made': indicators['referral_made_or_needed'],
    'service': indicators['service_provided']
}
submit_to_chi_database(report_data)
```

**Entity-Based Follow-up:**
```python
# Extract locations for local service referral
locations = insights['extracted_entities']['locations']
for location in locations:
    nearby_services = find_services_near(location)
    suggest_referral(nearby_services)
```

---

## Complete Example Response

```json
{
  "task_id": "3dea3688-b245-4d74-8e0c-a31ea4b46185",
  "status": "completed",
  "progress": 100,
  "result": {
    "status": "completed",
    "filename": "call_recording.wav",
    "result": {
      "audio_info": {
        "filename": "call_recording.wav",
        "file_size_mb": 1.55,
        "language_specified": "sw",
        "processing_time": 37.78
      },
      "transcript": "karibu huduma ya simu kwa mtoto unaongea na mshauri joseph...",
      "translation": "welcome to the child helpline you are speaking with counselor Joseph...",
      "nlp_processing_info": {
        "text_used_for_nlp": "translated_text",
        "nlp_text_length": 136
      },
      "entities": {},
      "classification": {
        "main_category": "Child Maintenance & Custody",
        "sub_category": "Info on Helpline",
        "sub_category_2": "Maintenance",
        "intervention": "Referral",
        "priority": "2",
        "confidence": 0.354,
        "confidence_breakdown": {
          "main_category": 0.216,
          "sub_category": 0.07,
          "intervention": 0.641,
          "priority": 0.488
        }
      },
      "qa_scores": {
        "opening": [{"submetric": "Use of call opening phrase", "prediction": false, "score": "✗", "probability": 0.93}],
        "listening": [{"submetric": "Caller was not interrupted", "prediction": false, "score": "✗", "probability": 0.90}],
        "proactiveness": [{"submetric": "Willing to solve extra issues", "prediction": false, "score": "✗", "probability": 0.83}],
        "resolution": [{"submetric": "Gives accurate information", "prediction": false, "score": "✗", "probability": 0.80}],
        "hold": [{"submetric": "Explains before placing on hold", "prediction": false, "score": "✗", "probability": 0.22}],
        "closing": [{"submetric": "Proper call closing phrase used", "prediction": false, "score": "✗", "probability": 0.76}]
      },
      "summary": "Joseph welcome to the child helpline you are speaking with counselor Joseph...",
      "insights": {
        "reporting_metadata": {
          "schema_version": "4.0",
          "generated_by_model": "ai-service",
          "pipeline_stage": "vac_case_intelligence",
          "reporting_compatibility": ["CHI", "UNICEF_VAC", "CPIMS", "GOV_STATUTORY", "DONOR_NGO"]
        },
        "ai_decision_panel": {
          "case_headline": "",
          "immediate_safety_alert": false,
          "safety_alert_reason": null,
          "recommended_next_step": "Provide referral information",
          "recommended_timeframe": "Immediate|<24h",
          "survivor_centred_guidance": [
            "Use supportive, non-blaming language",
            "Prioritize the child's immediate safety",
            "Explain available referral and protection options"
          ]
        },
        "case_overview": {
          "risk_level": null,
          "risk_score": 0.0,
          "urgency_window_hours": 0,
          "suggested_disposition": "",
          "rationale_summary": ""
        },
        "classification": {
          "primary_category": "Child Maintenance & Custody",
          "sub_category": "Info on Helpline",
          "intervention": "Referral",
          "priority": "2",
          "classifier_confidence": 0.354
        },
        "vac_incident_profile": {
          "violence_type": null,
          "incident_setting": null,
          "perpetrator_relationship": null,
          "incident_reported_as_ongoing": false,
          "child_in_immediate_danger": false
        },
        "safeguarding_flags": {
          "physical_violence_flag": false,
          "sexual_violence_flag": false,
          "emotional_psychological_flag": false,
          "neglect_flag": false,
          "exploitation_flag": false,
          "trafficking_flag": false,
          "harmful_practice_flag": false,
          "self_harm_suicide_flag": false
        },
        "persons_involved": {
          "survivors": [],
          "alleged_perpetrators": [],
          "callers": [],
          "other_named_persons": []
        },
        "location_and_context": {
          "locations_mentioned": [],
          "setting_type": null,
          "school_related": false,
          "household_related": false,
          "community_related": false
        },
        "service_and_referral_plan": {
          "immediate_referral_needed": false,
          "mandatory_reporting_required": false,
          "recommended_referrals": [],
          "recommended_services": [],
          "follow_up_required": true,
          "follow_up_timeframe_hours": 0
        },
        "chi_unicef_reporting_indicators": {
          "referral_made_or_needed": false,
          "service_provided": null,
          "case_priority_level": "2",
          "vac_category_alignment": "Info on Helpline"
        },
        "extracted_entities": {
          "names": [],
          "locations": [],
          "organizations": [],
          "dates": []
        },
        "case_tags_and_keywords": {
          "context_tags": [],
          "vulnerability_tags": [],
          "service_tags": [],
          "keywords": []
        },
        "data_quality": {
          "insight_confidence_score": 0.0,
          "information_completeness": "Complete",
          "missing_information": [],
          "contradictions_detected": false
        },
        "risk_level": null,
        "suggested_disposition": "",
        "rationale_summary": "",
        "confidence_score": 0.0,
        "category_suggestions": {
          "primary_category": "Child Maintenance & Custody",
          "sub_category": "Info on Helpline",
          "intervention": "Referral",
          "priority": "2",
          "tags": []
        },
        "processing_metadata": {
          "processing_time_ms": 27524,
          "timestamp": "2026-01-29T08:34:00.929832+00:00",
          "text_analyzed": "translation",
          "text_length": 136
        }
      },
      "processing_steps": {
        "transcription": {"duration": 9.49, "status": "completed", "output_length": 108},
        "translation": {"duration": 0.25, "status": "completed", "method": "custom_model", "output_length": 136},
        "ner": {"duration": 0.01, "status": "completed", "entities_found": 0},
        "classification": {"duration": 0.14, "status": "completed", "confidence": 0.354},
        "qa_scoring": {"duration": 0.01, "status": "completed", "evaluations_count": 6},
        "summarization": {"duration": 0.36, "status": "completed", "summary_length": 193},
        "insights_generation": {"duration": 27.52, "status": "completed", "source": "ai_service", "risk_level": null}
      },
      "pipeline_info": {
        "total_time": 37.78,
        "models_used": ["whisper", "translator", "ner", "classifier", "summarizer", "all_qa_distilbert_v1", "ai-service"],
        "text_flow": "transcript → translated_text → nlp_models",
        "timestamp": "2026-01-29T08:34:00.930521",
        "processed_by": "celery_worker"
      }
    }
  }
}
```

---

## Best Practices

### 1. Confidence Thresholds
Set appropriate thresholds for your use case:

```python
# Conservative approach (higher precision)
HIGH_CONFIDENCE_THRESHOLD = 0.85
MEDIUM_CONFIDENCE_THRESHOLD = 0.70

# Liberal approach (higher recall)
HIGH_CONFIDENCE_THRESHOLD = 0.75
MEDIUM_CONFIDENCE_THRESHOLD = 0.60
```

### 2. Combine Multiple Insights
Make decisions based on multiple signals:

```python
# Escalation logic combining classification and insights
if (classification['priority'] == 'high' and
    insights['safeguarding_flags']['physical_violence_flag'] and
    insights['case_overview']['risk_level'] in ['Critical', 'High']):
    escalate_immediately(call_id)
```

### 3. Human-in-the-Loop
Never fully automate critical decisions:

```python
# Flag for review instead of auto-action
if insights['ai_decision_panel']['immediate_safety_alert']:
    if insights['data_quality']['insight_confidence_score'] > 0.90:
        flag_for_immediate_review(call_id, auto_escalate=True)
    else:
        flag_for_review(call_id, auto_escalate=False)
```

### 4. Track Model Performance
Monitor how well insights match agent feedback:

```python
# Compare AI predictions with agent feedback
feedback = get_agent_feedback(call_id)
ai_risk = insights['case_overview']['risk_level']
agent_risk = feedback['actual_risk_level']

if ai_risk != agent_risk:
    log_mismatch(call_id, ai_risk, agent_risk)
```

---

## Related Documentation

- [Audio Processing API](audio-api-reference.md)
- [Agent Feedback API](agent_feedback.md)
- [Streaming API](streaming.md)

---
