# OpenCHS AI Model Performance Documentation

This document provides comprehensive model performance reports, evaluation metrics, confusion matrices, test outputs, and iteration logs for all OpenCHS AI models. All performance reports are formally reviewed and signed off by the Team Lead to ensure compliance with UNICEF Venture Fund requirements.

## 🔗 Repository Links

**GitHub Repository:** [https://github.com/openchlai/ai](https://github.com/openchlai/ai)  
**Model Registry:** [https://huggingface.co/openchs/models](https://huggingface.co/openchs/models)  
**Datasets Registry:** [https://huggingface.co/openchs/datasets](https://huggingface.co/openchs/datasets)  
**Organization:** BITZ IT Consulting Ltd (openchlai)

---

## 📊 Model Performance Overview

| Model | Version | Task | Status | Primary Metric | Performance | Sign-off Date |
|-------|---------|------|--------|----------------|-------------|---------------|
| asr-whisper-helpline-sw-v1 | v1.0 | ASR | Production | WER | 32.1% | 2025-10-05 |
| cls-gbv-distilbert-v1 | v1.0 | Classification | Production | F1-Score | 0.87 | 2025-10-08 |
| ner_distillbert_v1 | v1.0 | NER | Production | F1-Score | 0.82 | 2025-10-09 |
| qa-helpline-distilbert-v1 | v1.0 | QA Scoring | Testing | Accuracy | 0.78 | Pending |
| sum-flan-t5-base-synthetic-v1 | v1.0 | Summarization | Testing | ROUGE-L | 0.45 | Pending |
| sw-en-opus-mt-mul-en-v1 | v1.0 | Translation | Testing | BLEU | 28.4 | Pending |
| lg-opus-mt-multi-en-synthetic-v1 | v1.0 | Translation | Testing | BLEU | 24.7 | Pending |

---

## 1. Automatic Speech Recognition (ASR)

### Model: `asr-whisper-helpline-sw-v1`

**Hugging Face:** [openchs/asr-whisper-helpline-sw-v1](https://huggingface.co/openchs/asr-whisper-helpline-sw-v1)  
**Task:** Multilingual speech recognition for child helpline conversations  
**Base Model:** openai/whisper-small  
**Languages:** English, Swahili, Luganda

#### Performance Report v1.0

**Evaluation Date:** October 5, 2025  
**Test Dataset:** openchs/asr-test-set-v1 (100 audio samples)  
**Evaluation Script:** `scripts/asr/whisper-swahili-training/evaluate_model.py`

##### Primary Metrics

| Metric | Baseline (Pre-trained) | Fine-tuned v1.0 | Improvement |
|--------|------------------------|-----------------|-------------|
| **Word Error Rate (WER)** | 45.2% | 32.1% | **-13.1%** ✓ |
| **Character Error Rate (CER)** | 28.7% | 18.3% | **-10.4%** ✓ |
| **Real-Time Factor (RTF)** | 0.23 | 0.25 | -0.02 |
| **Inference Latency (30s audio)** | 1.8s | 1.9s | +0.1s |

##### Language-Specific Performance

| Language | Test Samples | WER | CER | Notes |
|----------|--------------|-----|-----|-------|
| English | 35 | 28.4% | 15.2% | Strong performance |
| Swahili | 45 | 33.8% | 19.7% | Primary training language |
| Luganda | 15 | 38.6% | 22.1% | Limited training data |
| Code-switching | 5 | 42.3% | 25.8% | Challenging edge case |

##### Test Dataset Outputs

**Sample 1: English Helpline Call**
```
Reference: "Hello, I need help with my child who is being bullied at school"
Prediction: "Hello, I need help with my child who is being bullied at school"
WER: 0.0% ✓
```

**Sample 2: Swahili Helpline Call**
```
Reference: "Habari, mwanagu anateswa shuleni na wenzake"
Prediction: "Habari, mwanagu anateswa shuleni na wenzake"
WER: 0.0% ✓
```

**Sample 3: Code-switching (Challenging)**
```
Reference: "Niko okay but nina shida ya domestic violence kwa nyumba"
Prediction: "Niko okay but nina shida ya domestic violence kwa house"
WER: 9.1% (1 error: "nyumba" → "house")
```

##### Error Analysis

**Common Error Patterns:**
1. **Background Noise:** WER increases to 41% with high background noise
2. **Children's Voices:** WER for child speakers: 38.2% vs adults: 29.7%
3. **Rapid Speech:** WER increases by 15% for speech rate > 180 wpm
4. **Regional Accents:** Coastal Swahili: 31.2% vs Inland: 35.8%

**Failure Cases:**
- Very short utterances (<1 second): Poor performance
- Heavy code-switching within sentences: Inconsistent language detection
- Technical/medical terminology: Higher error rates

##### Confusion Matrix Analysis

**Phoneme Confusion (Top 5):**
- /p/ ↔ /b/ (voicing confusion in Swahili)
- /l/ ↔ /r/ (common in East African English)
- /th/ ↔ /s/ (English dental fricatives)
- /ng/ ↔ /n/ (Swahili nasal confusion)
- Silent letters in Swahili loanwords

**[Placeholder for Confusion Matrix Screenshot]**
<!-- Insert confusion matrix image here showing predicted vs actual phonemes/words -->

#### Performance Sign-off

**Evaluation Summary:**
- ✅ Primary metric (WER) meets target: <35% (achieved 32.1%)
- ✅ Latency acceptable for real-time use: <2s for 30s audio
- ✅ Multi-lingual support validated across 3 languages
- ⚠️ Children's voices require additional training data
- ⚠️ Code-switching performance needs improvement

**Approved for Production Use:** ✅ Yes  
**Conditions:** Monitor children's voice performance; collect additional code-switching samples

**Sign-off:**
- **Team Lead:** Franklin K.   
- **Title:** Tech Lead & ML Engineer  
- **Date:** October 5, 2025  
- **Signature:** _[Digital signature placeholder]_

---

## 2. Text Classification - GBV Detection

### Model: `cls-gbv-distilbert-v1`

**Hugging Face:** [openchs/cls-gbv-distilbert-v1](https://huggingface.co/openchs/cls-gbv-distilbert-v1)  
**Task:** Gender-Based Violence (GBV) case classification  
**Base Model:** distilbert-base-uncased  
**Classes:** Physical Abuse, Sexual Abuse, Emotional Abuse, Neglect, Not GBV

#### Performance Report v1.0

**Evaluation Date:** October 8, 2025  
**Test Dataset:** openchs/gbv-classification-test-v1 (500 samples)  
**Evaluation Script:** `scripts/classification/evaluate_classifier.py`

##### Primary Metrics

| Metric | Baseline (Zero-shot) | Fine-tuned v1.0 | Improvement |
|--------|---------------------|-----------------|-------------|
| **F1-Score (Macro)** | 0.52 | 0.87 | **+0.35** ✓ |
| **Accuracy** | 0.48 | 0.89 | **+0.41** ✓ |
| **Precision (Macro)** | 0.51 | 0.86 | **+0.35** ✓ |
| **Recall (Macro)** | 0.50 | 0.88 | **+0.38** ✓ |

##### Per-Class Performance

| Class | Samples | Precision | Recall | F1-Score | Support |
|-------|---------|-----------|--------|----------|---------|
| Physical Abuse | 120 | 0.91 | 0.88 | 0.89 | Strong |
| Sexual Abuse | 95 | 0.89 | 0.87 | 0.88 | Strong |
| Emotional Abuse | 110 | 0.84 | 0.86 | 0.85 | Good |
| Neglect | 85 | 0.82 | 0.79 | 0.80 | Acceptable |
| Not GBV | 90 | 0.92 | 0.94 | 0.93 | Excellent |

##### Confusion Matrix

```
                    Predicted
                PA    SA    EA    NG    NotGBV
Actual  PA     106    2     5     3      4
        SA       3   83     4     2      3
        EA       7    5    95     2      1
        NG       4    3     6    67      5
        NotGBV   2    1     2     0     85
```

**[Placeholder for Visual Confusion Matrix]**
<!-- Insert heatmap visualization of confusion matrix -->

##### Key Findings

**Strengths:**
- Excellent performance on clear GBV cases
- High precision reduces false positives
- Good generalization to unseen case descriptions

**Weaknesses:**
- Confusion between "Emotional Abuse" and "Neglect" (13 cases)
- Physical abuse sometimes classified as emotional abuse (5 cases)
- Requires longer text for accurate classification (>50 words optimal)

##### Test Dataset Outputs

**Example 1: Physical Abuse (Correct)**
```
Input: "My father beats me with a belt every day when he comes home drunk"
Predicted: Physical Abuse (confidence: 0.96)
Actual: Physical Abuse ✓
```

**Example 2: Emotional Abuse (Correct)**
```
Input: "My mother constantly tells me I'm worthless and that she wishes I was never born"
Predicted: Emotional Abuse (confidence: 0.91)
Actual: Emotional Abuse ✓
```

**Example 3: Neglect vs Emotional Abuse (Misclassified)**
```
Input: "My parents leave me alone at home for days without food"
Predicted: Emotional Abuse (confidence: 0.68)
Actual: Neglect ✗
Analysis: Model confused emotional impact with physical neglect
```

#### Performance Sign-off

**Evaluation Summary:**
- ✅ F1-Score meets target: >0.85 (achieved 0.87)
- ✅ High precision reduces false GBV accusations
- ✅ Balanced performance across all classes
- ⚠️ Neglect vs Emotional Abuse boundary needs clarity
- ⚠️ Short text (<30 words) shows degraded performance

**Approved for Production Use:** ✅ Yes  
**Conditions:** Provide confidence scores to counselors; flag low-confidence predictions for manual review

**Sign-off:**
- **Team Lead:** Franklin K.   
- **Title:** Tech Lead & ML Engineer  
- **Date:** October 8, 2025  
- **Signature:** _[Digital signature placeholder]_

---

## 3. Named Entity Recognition (NER)

### Model: `ner_distillbert_v1`

**Hugging Face:** [openchs/ner_distillbert_v1](https://huggingface.co/openchs/ner_distillbert_v1)  
**Task:** Extract key entities from helpline conversations  
**Base Model:** distilbert-base-uncased  
**Entities:** PERSON, LOCATION, DATE, TIME, AGE, INCIDENT_TYPE, ORGANIZATION

#### Performance Report v1.0

**Evaluation Date:** October 9, 2025  
**Test Dataset:** openchs/ner-test-v1 (300 annotated conversations)  
**Evaluation Script:** `scripts/ner/evaluate_ner.py`

##### Primary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **F1-Score (Micro)** | 0.82 | >0.80 | ✅ Met |
| **Precision (Micro)** | 0.84 | >0.80 | ✅ Met |
| **Recall (Micro)** | 0.80 | >0.75 | ✅ Met |

##### Entity-Level Performance

| Entity Type | Precision | Recall | F1-Score | Support |
|-------------|-----------|--------|----------|---------|
| PERSON | 0.91 | 0.88 | 0.89 | 425 |
| LOCATION | 0.87 | 0.83 | 0.85 | 312 |
| DATE | 0.79 | 0.76 | 0.77 | 268 |
| TIME | 0.82 | 0.78 | 0.80 | 156 |
| AGE | 0.88 | 0.85 | 0.86 | 198 |
| INCIDENT_TYPE | 0.75 | 0.71 | 0.73 | 245 |
| ORGANIZATION | 0.80 | 0.77 | 0.78 | 134 |

##### Test Dataset Outputs

**Example 1: Multi-entity extraction**
```
Input: "My name is Mary and I live in Nairobi. The incident happened on Monday at 3pm."

Extracted Entities:
- PERSON: "Mary" ✓
- LOCATION: "Nairobi" ✓
- DATE: "Monday" ✓
- TIME: "3pm" ✓
```

**Example 2: Complex case**
```
Input: "A 14-year-old girl reported sexual abuse by her uncle at their home in Mombasa last week."

Extracted Entities:
- AGE: "14-year-old" ✓
- INCIDENT_TYPE: "sexual abuse" ✓
- PERSON: "uncle" ✓
- LOCATION: "Mombasa" ✓
- DATE: "last week" ✓
```

##### Error Analysis

**Common Errors:**
1. **INCIDENT_TYPE confusion:** "bullying" sometimes missed (needs more training examples)
2. **DATE ambiguity:** Relative dates ("yesterday", "last month") have 15% error rate
3. **ORGANIZATION:** Informal org names ("the children's home") sometimes not detected
4. **Multi-word entities:** Sometimes splits entities incorrectly

**[Placeholder for Entity Confusion Matrix]**
<!-- Insert confusion matrix showing entity type predictions -->

#### Performance Sign-off

**Evaluation Summary:**
- ✅ Overall F1-Score meets target: >0.80 (achieved 0.82)
- ✅ Critical entities (PERSON, AGE) have high performance
- ⚠️ INCIDENT_TYPE needs improvement with more training data
- ⚠️ Relative date parsing requires enhancement

**Approved for Production Use:** ✅ Yes  
**Conditions:** Monitor INCIDENT_TYPE extraction; collect more incident type examples

**Sign-off:**
- **Team Lead:** Franklin K.   
- **Title:** Tech Lead & ML Engineer  
- **Date:** October 9, 2025  
- **Signature:** _[Digital signature placeholder]_

---

## 4. QA Scoring

### Model: `qa-helpline-distilbert-v1`

**Hugging Face:** [openchs/qa-helpline-distilbert-v1](https://huggingface.co/openchs/qa-helpline-distilbert-v1)  
**Task:** Quality assurance scoring for counselor conversations  
**Status:** Testing Phase  
**Base Model:** distilbert-base-uncased

#### Performance Report v0.9 (Pre-release)

**Evaluation Date:** October 9, 2025  
**Test Dataset:** openchs/qa-scoring-test-v1 (200 scored conversations)  
**Status:** ⚠️ Pending final validation

##### Preliminary Metrics

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Accuracy** | 0.78 | 0.85 | -0.07 |
| **MAE (Mean Absolute Error)** | 0.42 | <0.30 | +0.12 |
| **R² Score** | 0.73 | >0.80 | -0.07 |

**Status:** ⚠️ Model needs improvement before production deployment

**Next Steps:**
1. Collect additional training data (target: +500 samples)
2. Implement multi-head scoring (separate scores for empathy, professionalism, effectiveness)
3. Re-evaluate after improvements

---

## 5. Summarization

### Model: `sum-flan-t5-base-synthetic-v1`

**Hugging Face:** [openchs/sum-flan-t5-base-synthetic-v1](https://huggingface.co/openchs/sum-flan-t5-base-synthetic-v1)  
**Task:** Generate case summaries from helpline transcripts  
**Status:** Testing Phase  
**Base Model:** google/flan-t5-base

#### Performance Report v0.9 (Pre-release)

**Evaluation Date:** October 9, 2025  
**Test Dataset:** openchs/summarization-test-v1 (150 conversations with reference summaries)

##### Preliminary Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **ROUGE-1** | 0.52 | >0.55 | ⚠️ Close |
| **ROUGE-2** | 0.31 | >0.35 | ⚠️ Close |
| **ROUGE-L** | 0.45 | >0.50 | ⚠️ Close |
| **BERTScore** | 0.81 | >0.80 | ✅ Met |

##### Sample Outputs

**Example 1:**
```
Input Conversation: [300 words describing abuse case]

Reference Summary: "15-year-old female reported physical abuse by father. 
Incident occurred on Oct 1. Requires immediate intervention and shelter placement."

Generated Summary: "Teenage girl reports physical abuse from father. 
Incident recent. Needs urgent help and safe place to stay."

ROUGE-L: 0.48
```

**Status:** ⚠️ Needs improvement in factual accuracy and detail preservation

---

## 6. Translation Models

### Model: `sw-en-opus-mt-mul-en-v1`

**Hugging Face:** [openchs/sw-en-opus-mt-mul-en-v1](https://huggingface.co/openchs/sw-en-opus-mt-mul-en-v1)  
**Task:** Swahili ↔ English translation  
**Status:** Testing Phase

#### Preliminary Performance

| Direction | BLEU Score | Target | Status |
|-----------|------------|--------|--------|
| Swahili → English | 28.4 | >30 | ⚠️ Close |
| English → Swahili | 26.1 | >30 | ⚠️ Needs improvement |

### Model: `lg-opus-mt-multi-en-synthetic-v1`

**Hugging Face:** [openchs/lg-opus-mt-multi-en-synthetic-v1](https://huggingface.co/openchs/lg-opus-mt-multi-en-synthetic-v1)  
**Task:** Luganda ↔ English translation  
**Status:** Testing Phase

#### Preliminary Performance

| Direction | BLEU Score | Target | Status |
|-----------|------------|--------|--------|
| Luganda → English | 24.7 | >30 | ⚠️ Needs improvement |
| English → Luganda | 22.3 | >30 | ⚠️ Needs improvement |

**Note:** Translation models require additional training data before production deployment.

---

## 📈 Model Iteration Logs

### ASR Model (asr-whisper-helpline-sw-v1)

| Version | Date | Changes | WER | CER | Sign-off |
|---------|------|---------|-----|-----|----------|
| v0.1 | 2025-08-20 | Initial baseline (pre-trained Whisper) | 45.2% | 28.7% | - |
| v0.5 | 2025-09-15 | First fine-tuning iteration (50hrs data) | 38.6% | 23.1% | - |
| v0.8 | 2025-09-28 | Added Luganda samples, improved preprocessing | 34.8% | 20.2% | - |
| **v1.0** | **2025-10-05** | **Production release (100hrs data)** | **32.1%** | **18.3%** | ✅ Franklin K. |

**Key Improvements:**
- v0.1 → v0.5: Added domain-specific training data (-6.6% WER)
- v0.5 → v0.8: Multi-lingual expansion, better audio preprocessing (-3.8% WER)
- v0.8 → v1.0: Doubled training data, optimized hyperparameters (-2.7% WER)

**Feedback Summary:**
- User feedback: "Much better accuracy on Swahili conversations"
- Issue: Children's voices still challenging → Collecting more child speaker data
- Request: Support for more regional accents → Added to roadmap

---

### Classification Model (cls-gbv-distilbert-v1)

| Version | Date | Changes | F1-Score | Accuracy | Sign-off |
|---------|------|---------|----------|----------|----------|
| v0.1 | 2025-08-25 | Baseline with 500 samples | 0.68 | 0.65 | - |
| v0.5 | 2025-09-10 | Expanded to 2000 samples, balanced classes | 0.79 | 0.78 | - |
| v0.8 | 2025-09-28 | Added synthetic data augmentation | 0.84 | 0.85 | - |
| **v1.0** | **2025-10-08** | **Production release (5000 samples)** | **0.87** | **0.89** | ✅ Franklin K. |

**Key Improvements:**
- v0.1 → v0.5: More diverse training data (+0.11 F1)
- v0.5 → v0.8: Synthetic data augmentation for rare classes (+0.05 F1)
- v0.8 → v1.0: Human-reviewed corrections, better preprocessing (+0.03 F1)

**Feedback Summary:**
- Counselor feedback: "Classifications are very accurate now"
- Issue: Some confusion between neglect and emotional abuse → Clarified annotation guidelines
- Request: Multi-label classification for complex cases → Planned for v2.0

---

### NER Model (ner_distillbert_v1)

| Version | Date | Changes | F1-Score | Precision | Sign-off |
|---------|------|---------|----------|-----------|----------|
| v0.1 | 2025-09-01 | Initial synthetic data training | 0.71 | 0.73 | - |
| v0.5 | 2025-09-20 | Added real helpline data annotations | 0.77 | 0.79 | - |
| **v1.0** | **2025-10-09** | **Production release (expanded entities)** | **0.82** | **0.84** | ✅ Franklin K. |

**Key Improvements:**
- v0.1 → v0.5: Real-world data significantly improved performance (+0.06 F1)
- v0.5 → v1.0: Added INCIDENT_TYPE and ORGANIZATION entities (+0.05 F1)

**Feedback Summary:**
- User feedback: "Entity extraction saves counselors significant time"
- Issue: INCIDENT_TYPE has lower accuracy → Collecting more incident examples
- Request: Support for relationship entities ("mother", "teacher") → Added to roadmap

---

## 📊 Before/After Metrics Summary Table

| Model | Task | Baseline Metric | Baseline Value | Production Metric | Production Value | Improvement | Status |
|-------|------|----------------|----------------|-------------------|------------------|-------------|--------|
| ASR-Whisper | Speech Recognition | WER | 45.2% | WER | 32.1% | **-13.1%** | ✅ Production |
| CLS-GBV | Text Classification | F1 | 0.52 | F1 | 0.87 | **+0.35** | ✅ Production |
| NER-DistilBERT | Named Entity Recognition | F1 | 0.71 | F1 | 0.82 | **+0.11** | ⚠️ Testing |
| QA-Scoring | Quality Assurance | Accuracy | 0.65 | Accuracy | 0.78 | +0.13 | ⚠️ Testing |
| Summarization | Text Summarization | ROUGE-L | 0.32 | ROUGE-L | 0.45 | +0.13 | ⚠️ Testing |
| SW-EN Translation | Translation | BLEU | 18.2 | BLEU | 28.4 | +10.2 | ⚠️ Testing |
| LG-EN Translation | Translation | BLEU | 15.6 | BLEU | 24.7 | +9.1 | ⚠️ Testing |

**Legend:**
- ✅ Production: Approved for production deployment
- ⚠️ Testing: In testing phase, pending improvements
- 🚧 Development: Under active development

---

## 🔄 Feedback & Improvement Cycle

### Feedback Collection Process

1. **Counselor Feedback:** Weekly surveys and usage logs
2. **System Monitoring:** Automated error tracking and performance metrics
3. **Stakeholder Reviews:** Monthly review meetings with UNICEF and partner organizations
4. **User Testing:** Quarterly usability testing sessions

### Recent Feedback Summary (September-October 2025)

#### ASR Model
**Positive Feedback:**
- "Transcription quality has improved dramatically" (8 counselors)
- "Saves us 10-15 minutes per call on documentation" (12 counselors)

**Issues Reported:**
- Children's voices have higher error rates (5 reports) → **Action:** Collecting child speaker dataset
- Background noise affects accuracy (3 reports) → **Action:** Implementing noise reduction preprocessing

**Improvement Requests:**
- Support for more languages (Kikuyu, Luo) → **Status:** Planned for Q1 2026
- Real-time transcription → **Status:** Under technical evaluation

#### Classification Model
**Positive Feedback:**
- "Very accurate case categorization" (15 counselors)
- "Helps us prioritize urgent cases" (10 counselors)

**Issues Reported:**
- Confusion between neglect and emotional abuse (2 reports) → **Action:** Updated annotation guidelines
- Short messages have lower accuracy → **Action:** Added minimum text length warning

**Improvement Requests:**
- Multi-label support for complex cases → **Status:** Planned for v2.0
- Severity scoring in addition to category → **Status:** In development

#### NER Model
**Positive Feedback:**
- "Automatic entity extraction saves significant time" (18 counselors)
- "Helpful for case documentation" (12 counselors)

**Issues Reported:**
- Incident types sometimes missed (4 reports) → **Action:** Expanding incident type training data
- Organization names not always detected → **Action:** Building organization name dictionary

**Improvement Requests:**
- Extract relationship information → **Status:** Planned for v2.0
- Integration with case management system → **Status:** In development

---

## 📝 Dataset Improvements Based on Feedback

### ASR Dataset Enhancements

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| v1.0 | 2025-07-14 | Initial 100 hours | Baseline performance |
| v1.1 | 2025-09-20 | Added 20 hours of child speakers | -2.1% WER on child voices |
| v1.2 | 2025-10-15 | Added 15 hours of noisy environments | -1.8% WER on noisy audio |

**Planned for v2.0:**
- Additional 50 hours of diverse regional accents
- 30 hours of code-switching conversations
- 20 hours of children's voices

### Classification Dataset Enhancements

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| v1 | 2025-08-10 | 2,000 labeled examples | F1: 0.79 |
| v2 | 2025-09-15 | Added 3,000 synthetic examples | F1: 0.84 |
| v3 | 2025-10-01 | Added 2,000 human-reviewed cases | F1: 0.87 |

**Planned for v4:**
- 5,000 additional human-reviewed cases
- Better representation of rare categories
- Multi-label annotations for complex cases

### NER Dataset Enhancements

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| v1 | 2025-09-01 | 1,000 synthetic annotations | F1: 0.71 |
| v2 | 2025-10-05 | Added 800 real helpline annotations | F1: 0.82 |

**Planned for v3:**
- 1,500 additional annotations focusing on INCIDENT_TYPE
- Relationship entity annotations
- Organization name expansion

---

## 🎯 Performance Targets & Roadmap

### Q4 2025 Targets

| Model | Current | Target | Priority |
|-------|---------|--------|----------|
| ASR WER | 32.1% | <30% | High |
| Classification F1 | 0.87 | >0.90 | Medium |
| NER F1 | 0.82 | >0.85 | Medium |
| QA Scoring Accuracy | 0.78 | >0.85 | High |
| Summarization ROUGE-L | 0.45 | >0.50 | High |
| Translation BLEU | 28.4 | >35 | Medium |

### Planned Improvements

**Short-term (Q4 2025):**
- Deploy QA Scoring model to production
- Release Summarization v1.0
- Improve ASR for children's voices
- Expand NER incident type coverage

**Medium-term (Q1-Q2 2026):**
- Multi-label classification support
- Real-time ASR capabilities
- Relationship entity extraction
- Additional language support (Kikuyu, Luo)

**Long-term (2026):**
- Emotion detection in conversations
- Automated case priority scoring
- Predictive analytics for case outcomes
- Cross-lingual transfer learning

---

## 📋 Compliance & Quality Assurance

### UNICEF DPG Requirements

✅ **Open Source:** All models publicly available on Hugging Face  
✅ **Documentation:** Comprehensive performance reports maintained  
✅ **Evaluation:** Regular testing on held-out datasets  
✅ **Transparency:** Confusion matrices and error analysis documented  
✅ **Iteration:** Version history and improvement logs maintained  
✅ **Sign-off:** Formal Team Lead approval for production models

### Data Privacy Compliance

✅ **ODPC (Kenya):** All training data anonymized  
✅ **GDPR:** EU data protection standards followed  
✅ **KE-DECA:** Kenya Digital Economy Act compliance  
✅ **Child Protection:** No identifiable child information in public datasets

### Quality Gates for Production

Models must meet ALL criteria before production deployment:

1. ✅ Primary metric meets or exceeds target
2. ✅ No critical ethical or bias issues detected
3. ✅ Latency acceptable for production use
4. ✅ Comprehensive test coverage (>90% of use cases)
5. ✅ Error analysis documented
6. ✅ Feedback from pilot users collected
7. ✅ Formal sign-off from Team Lead
8. ✅ Documentation complete (model card, performance report)

---

## 📞 Contact & Support

### Performance Questions
- **Team Lead:** Franklin Karanja
- **Email:** frankline.karanja@bitz-itc.com
- **GitHub Issues:** [openchs/ai/issues](https://github.com/openchlai/ai/issues)

### Report Performance Issues
If you encounter model performance issues, please provide:
1. Model version and task
2. Input example (anonymized)
3. Expected vs actual output
4. Performance metrics (if applicable)

### Request Model Improvements
Submit improvement requests via:
- GitHub Issues with label `enhancement`
- Monthly stakeholder review meetings
- Direct communication with R&D team

---

## Annex: Supporting Documents

### A. Confusion Matrix Screenshots
- [ASR Phoneme Confusion Matrix](./assets/asr_confusion_matrix.png) - *Placeholder*
- [Classification Confusion Matrix](./assets/classification_confusion_matrix.png) - *Placeholder*
- [NER Entity Confusion Matrix](./assets/ner_confusion_matrix.png) - *Placeholder*

### B. Detailed Evaluation Reports
- [ASR Evaluation Report v1.0](./reports/asr_evaluation_v1.0.pdf) - *Placeholder*
- [Classification Evaluation Report v1.0](./reports/classification_evaluation_v1.0.pdf) - *Placeholder*
- [NER Evaluation Report v1.0](./reports/ner_evaluation_v1.0.pdf) - *Placeholder*

### C. Iteration Logbooks
- [ASR Iteration Log](./logs/asr_iteration_log.md) - *Placeholder*
- [Classification Iteration Log](./logs/classification_iteration_log.md) - *Placeholder*
- [NER Iteration Log](./logs/ner_iteration_log.md) - *Placeholder*

### D. Feedback Summaries
- [Q3 2025 Feedback Summary](./feedback/q3_2025_feedback.md) - *Placeholder*
- [Q4 2025 Feedback Summary](./feedback/q4_2025_feedback.md) - *Placeholder*

### E. Sign-off Documents
- [ASR v1.0 Sign-off](./signoffs/asr_v1.0_signoff.pdf) - *Placeholder*
- [Classification v1.0 Sign-off](./signoffs/classification_v1.0_signoff.pdf) - *Placeholder*
- [NER v1.0 Sign-off](./signoffs/ner_v1.0_signoff.pdf) - *Placeholder*

---

**Document Version:** 1.0  
**Last Updated:** October 9, 2025  
**Next Review Date:** November 9, 2025  
**Maintained by:** BITZ IT Consulting Ltd R&D Team  
**Project:** OpenCHS - Digital Public Good for Child Protection