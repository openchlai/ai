# Child Protection Helpline Case Summarization Dataset V1

## Overview

This dataset (`train_data1.jsonl`) contains 1,000 synthetic training examples designed for fine-tuning the FLAN-T5 base model for automatic case summarization in child protection helpline scenarios. The dataset simulates real-world helpline calls reporting various forms of child abuse and exploitation cases across East Africa.

## Dataset Structure

Each record in the JSONL file contains the following fields:

- **transcript**: Full conversation between caller and helpline operator
- **summary**: Concise summary of the case details and key information
- **name**: Caller's name
- **location**: Geographic location where the incident is occurring
- **issue**: Primary type of child protection concern
- **victim**: Description of the child victim (age, relationship to caller)
- **perpetrator**: Identified or suspected perpetrator information
- **referral**: Recommended agencies/authorities for follow-up action
- **category**: Classification of the abuse/exploitation type
- **priority**: Urgency level for intervention
- **intervention**: Specific recommended actions

## Dataset Characteristics

### Size and Format
- **Total Records**: 1,000 examples
- **Format**: JSONL (JSON Lines)
- **Language**: English
- **Geographic Focus**: East African countries (Kenya, Tanzania, Uganda)

### Issue Distribution
The dataset covers the following child protection issues:
- **Child Labor** (576 cases): Forced work in factories, workshops, and other environments
- **Child Marriage** (195 cases): Forced or early marriages of minors
- **Emotional Abuse** (112 cases): Psychological harm and emotional trauma
- **Neglect** (19 cases): Failure to provide basic care and protection
- **Other specialized cases**: Including various forms of exploitation

### Geographic Distribution
Primary locations represented:
- **Mombasa**: 237 cases
- **Mwanza**: 233 cases  
- **Kisumu**: 132 cases
- **Other locations**: 398 cases across 70+ cities and regions

### Priority Levels
- **High Priority**: 803 cases (80.3%)
- **Urgent**: 105 cases (10.5%)
- **Other Priority Levels**: 92 cases (9.2%)

## Data Generation Template

The dataset follows a consistent conversational template:

1. **Initial Contact**: Caller identifies themselves and states the problem
2. **Issue Details**: Description of the child protection concern
3. **Validation**: Helpline operator acknowledges the severity
4. **Context Gathering**: Additional details about witnesses, evidence, etc.
5. **Guidance**: Referral to appropriate authorities and follow-up commitments

## Use Case

This dataset is specifically designed for:

- **Model**: FLAN-T5 Base fine-tuning
- **Task**: Automatic summarization of child protection helpline calls
- **Purpose**: Enable rapid case documentation and triage for child welfare organizations
- **Application**: Supporting helpline operators in generating consistent, accurate case summaries

## Ethical Considerations

- All data is **synthetic** and does not represent real cases or individuals
- Content focuses on **defensive child protection** scenarios
- Designed to improve response capabilities for legitimate child welfare organizations
- No actual personal information or real case details are included

## Data Quality Notes

- Some inconsistencies in field formatting (e.g., "Child labor" vs "Child Labor")
- Priority descriptions vary in verbosity and format
- Geographic data includes both city names and country specifications
- All conversations follow similar linguistic patterns due to template-based generation

## Recommended Preprocessing

Before fine-tuning, consider:

1. **Standardizing** issue categories and priority levels
2. **Normalizing** location formats
3. **Validating** JSON structure consistency
4. **Balancing** dataset if needed for specific issue types

## Citation

This dataset was created for research and development of child protection helpline automation systems. When using this dataset, please ensure compliance with ethical AI guidelines and child protection standards.

---

