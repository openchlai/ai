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
    "transcription": "...",
    "translation": "...",
    "language": "sw",
    "audio_info": {...},
    
    // 2. NAMED ENTITIES (NER)
    "entities": [...],
    
    // 3. CASE CLASSIFICATION
    "classification": {...},
    
    // 4. QUALITY ASSURANCE SCORES
    "qa_evaluations": {...},
    
    // 5. CALL SUMMARY
    "summary": "...",
    
    // 6. PROCESSING METADATA
    "processing_time": 45.2,
    "model_info": {...},
    "timestamp": "2026-01-20T10:30:00"
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

## Complete Example Response

```json
{
  "task_id": "abc123def456",
  "status": "completed",
  "progress": 100,
  "result": {
    "transcription": "Habari, hii ni 116 helpline ya watoto...",
    "translation": "Hello, this is 116 children's helpline...",
    "language": "sw",
    "audio_info": {
      "filename": "call_recording.wav",
      "duration_seconds": 120.5,
      "file_size_mb": 2.34
    },
    "entities": [
      {"text": "Central Park", "label": "LANDMARK", "confidence": 0.92},
      {"text": "John Doe", "label": "PERPETRATOR", "confidence": 0.88}
    ],
    "classification": {
      "main_category": "VANE",
      "sub_category": "Physical Abuse",
      "priority": "high",
      "intervention": "Referred",
      "confidence_scores": {
        "main_category": 0.89,
        "priority": 0.90
      }
    },
    "qa_evaluations": {
      "opening": {"score": 8.5},
      "listening": {"score": 7.2},
      "overall_score": 8.0
    },
    "summary": "Caller reported missing child at Central Park...",
    "processing_time": 45.23,
    "model_info": {...},
    "timestamp": "2026-01-20T10:30:45"
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
# Escalation logic
if (classification['priority'] == 'high' and
    classification['confidence_scores']['priority'] > 0.85 and
    any(e['label'] == 'PERPETRATOR' for e in entities)):
    escalate_immediately(call_id)
```

### 3. Human-in-the-Loop
Never fully automate critical decisions:

```python
# Flag for review instead of auto-action
if classification['priority'] == 'urgent':
    if classification['confidence_scores']['priority'] > 0.90:
        flag_for_immediate_review(call_id, auto_escalate=True)
    else:
        flag_for_review(call_id, auto_escalate=False)
```

### 4. Track Model Performance
Monitor how well insights match agent feedback:

```python
# Compare AI predictions with agent feedback
feedback = get_agent_feedback(call_id)
ai_classification = result['classification']['main_category']
agent_classification = feedback['actual_category']

if ai_classification != agent_classification:
    log_mismatch(call_id, ai_classification, agent_classification)
```

---

## Related Documentation

- [Audio Processing API](audio-api-reference.md)
- [Agent Feedback API](agent_feedback.md)
- [Streaming API](streaming.md)

---
