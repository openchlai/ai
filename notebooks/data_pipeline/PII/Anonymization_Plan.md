# 🛡️ Data Anonymization Plan for AI Model Training

**Scope: Case Management & Helpline AI Training Data**  
**Countries: Kenya, Uganda, Tanzania**  
**Partners: National Child Protection Agencies, UNICEF, BITZ IT Consulting Ltd**  
**Prepared for: AI Model Development (Speech-to-Text, NLP, Case Classification, Prediction)**
## 1. Objectives

To ensure no personally identifiable information (PII) or sensitive personal data (SPD) is retained in the training datasets used for AI/ML development.

To standardize and localize data anonymization across Kenya, Uganda, and Tanzania in accordance with national data protection laws and child protection policies.

To maximize data utility while preserving confidentiality, especially in text and speech datasets.

## 2. Scope of the Data

Data Types for Training Models:

- Structured case records (CSV/JSON)
- Transcribed helpline call logs (TXT/CSV)
- Free-text case notes and narratives
- Caller/Reporter metadata
- Speech data (used only post-transcription)

## 3. Legal & Ethical Framework

- Kenya: Data Protection Act (2019), Children Act (2022)
- Uganda: Data Protection and Privacy Act (2019), Children (Amendment) Act (2016)
- Tanzania: Data Protection Act (2022), Law of the Child Act (2009)
- Cross-Cutting: UNICEF Child Safeguarding Policy, GDPR (if data crosses borders)

## 4. Anonymization Techniques

### A. Structured Data (e.g., CSV/JSON)

| Field | Technique | Example Before | Example After |
|-------|-----------|----------------|---------------|
| child_name, reporter_name | Removal or token replacement | "Amina Nyambura" | {{CHILD_NAME}} |
| date_of_birth | Generalization | "2015-06-14" | "2015" or "10-14 years" |
| location | Regional aggregation | "Kayole, Nairobi" | "Nairobi County" |
| phone, email | Deletion | 0701234567, [email protected] | Removed |
| national_id | Masking or removal | "30872125" | {{ID}} |
| GPS coordinates | Dropped or rounded to district | "-1.2921, 36.8219" | "Nairobi County" |

### B. Unstructured Data (Narratives, Transcripts)

NER + Rule-Based Redaction using spaCy/Presidio + Custom Filters

Detect and replace:

- Names of children, reporters, perpetrators
- Specific location names (villages, schools, landmarks)
- Contact information
- Ethnic group or tribal identifiers (localized filters)
- Institutions (church, school, orphanage names)

Before:
```
Amina reported that her uncle, John Omondi, assaulted her in Mathare. She was taken to Mama Lucy Hospital on 12th Feb.
```

After:
```
{{REPORTER_NAME}} reported that her uncle, {{PERPETRATOR_NAME}}, assaulted her in {{LOCATION}}. She was taken to {{HEALTH_FACILITY}} on {{DATE}}.
```

### C. Speech/Audio Data

- Audio → Text via Whisper/STT model
- Text anonymized using above NER/redaction rules
- Original voice discarded unless:
  - It is obfuscated (voice scrambling, pitch shifting)
  - It's required for model training under a Data Sharing Agreement (DSA)

## 5. Sample Anonymized Dataset

Structured CSV Sample:

| case_id | child_age | location | narrative_snippet |
|---------|-----------|----------|-------------------|
| 00012 | 12 | Nairobi County | {{REPORTER_NAME}} said {{CHILD_NAME}} was beaten by {{PERPETRATOR_NAME}} at {{LOCATION}}. |

Unstructured Text Sample:

Original:
```
"Mary Wanjiku, aged 11, was rescued from a house in Kibera after being locked in by her aunt, Jane. The neighbor Peter called the helpline on 0712345678."
```

Anonymized:
```
"{{CHILD_NAME}}, aged 11, was rescued from a house in {{LOCATION}} after being locked in by her aunt, {{PERPETRATOR_NAME}}. The neighbor {{REPORTER_NAME}} called the helpline."
```

## 6. Validation & Quality Control

- Automated Checks: Regex sweeps, residual NER tagging, dictionary lookups
- Manual Audits: 5–10% spot-checking by designated data protection focal points
- Data Utility Testing: Verify anonymized data supports model accuracy

## 7. Retention & Access Control

- Raw data: Access restricted to authorized personnel only during preprocessing
- Anonymized datasets: Stored securely and versioned (for model reproducibility)
- Data disposal: Raw data destroyed post-anonymization; documented in disposal log

## 8. Tools & Pipelines

- spaCy / Presidio for NER redaction
- Custom Redaction Rules for local names, schools, ethnic identifiers
- Whisper + text pipeline for audio
- Git + encrypted storage for dataset versioning and audits

## 9. Governance & Roles

| Role | Entity | Responsibility |
|------|--------|----------------|
| Data Controller | DCS Kenya, MGLSD Uganda, MoHCDGEC Tanzania | Owns and approves use of raw and anonymized data |
| Data Processor | BITZ IT | Performs anonymization and prepares training datasets |
| Oversight & QA | UNICEF & Country Focal Points | Ensures compliance and validates anonymization quality |

## 10. Final Notes

1. No AI models will be trained on raw or sensitive data.
2. All models and evaluations will reference only anonymized content.
3. No personally identifiable content is to be embedded in vector embeddings, model weights, or documentation.
