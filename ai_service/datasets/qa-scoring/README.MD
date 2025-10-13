---
dataset_info:
  features:
  - name: text
    dtype: string
  - name: labels
    struct:
    - name: closing
      sequence: int64
    - name: hold
      sequence: int64
    - name: listening
      sequence: int64
    - name: opening
      sequence: int64
    - name: proactiveness
      sequence: int64
    - name: resolution
      sequence: int64
  splits:
  - name: train
    num_bytes: 86897
    num_examples: 102
  download_size: 27916
  dataset_size: 86897
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
task_categories:
- text-classification
- multiple-choice
tags:
- helpline
- openchs
- distilbert
size_categories:
- n<1K
license: apache-2.0
language:
- en
---

# Dataset Card for OpenCHS Child Helpline QA Scoring Dataset

## Dataset Details

### Dataset Description

This dataset contains simulated, annotated child helpline conversation transcripts for automated quality assurance (QA) scoring. Each conversation is evaluated across six key performance dimensions using binary labels to assess counselor effectiveness and call quality. The dataset is designed for training multi-head DistilBERT classification models that can automatically evaluate helpline conversations in real-time, supporting child protection services across East Africa.

The dataset addresses the critical need for standardized quality assessment in child helplines, where manual QA review is time-consuming and inconsistent. By automating QA scoring, helpline organizations can provide immediate feedback to counselors, identify training needs, and ensure high-quality support for vulnerable children.

**Key Features:**
- 102 simulated, annotated helpline conversations
- 6 independent QA scoring dimensions with 1,734 total annotations
- Multi-head classification structure supporting DistilBERT
- Binary scoring (0/1) for objective evaluation
- Token-optimized for transformer models (avg 162.5 tokens)
- Comprehensive QC validation (QC Score: 67/100)

- **Curated by:** BITZ IT Consulting - OpenCHS Project Team (Rogendo, Shemmiriam, Franklin Nelsonadagi)
- **Funded by:** UNICEF
- **Shared by:** OpenCHS (Open Child Helpline System) Project
- **Language(s) (NLP):** English (en), with planned expansion to Swahili (sw)
- **License:** 

### Trained Model

A multi-head DistilBERT model has been trained on this dataset and is available on the Hugging Face Hub:

**Model:** [`openchs/qa-helpline-distilbert-v1`](https://huggingface.co/openchs/qa-helpline-distilbert-v1)

**Model Performance:**
- Overall Accuracy: ~87.5%
- Average F1 Score: ~91.2%
- Best Performing Heads: Closing (100% F1), Resolution (98.5% F1)
- Challenging Heads: Listening (71.4% accuracy, 95.7% F1), Hold (80% F1)

See the model card for complete performance metrics, usage examples, and deployment instructions.

### Dataset Sources

- **Repository:** [GitHub/GitLab Repository URL]
- **Demo:** [Link to model demo if available]
- **Project Page:** OpenCHS AI Pipeline - https://github.com/openchlai/ai
- **Trained Model:** [openchs/qa-helpline-distilbert-v1](https://huggingface.co/openchs/qa-helpline-distilbert-v1)

## Uses

### Direct Use

This dataset is intended for:

1. **Training Multi-Head QA Classification Models**
   - Primary: Multi-head DistilBERT for 6-dimensional QA scoring (17 sub-metrics)
   - Trained model available: [`openchs/qa-helpline-distilbert-v1`](https://huggingface.co/openchs/qa-helpline-distilbert-v1)
   - Secondary: Other transformer-based architectures (BERT, RoBERTa, XLM-R)

2. **Helpline Quality Assurance Automation**
   - Real-time evaluation of counselor performance
   - Automated feedback generation for training
   - Quality monitoring dashboards for supervisors

3. **Research Applications**
   - Conversation analysis in crisis support contexts
   - Multi-task learning for QA assessment
   - Cross-lingual transfer learning (English → Swahili)
   - Class imbalance handling in multi-label classification

4. **Benchmarking**
   - Comparing QA scoring model architectures
   - Evaluating multilingual model performance
   - Testing data augmentation strategies

### Out-of-Scope Use

This dataset should **NOT** be used for:

- **Clinical diagnosis or medical decision-making** - The dataset evaluates counselor performance, not client mental health
- **Automated decision-making without human oversight** - QA scores should inform, not replace, human supervision
- **Training models on unrelated domains** - Conversation patterns are specific to helpline contexts
- **Demographic profiling or surveillance** - Contains sensitive child protection data
- **Commercial applications without proper ethical review** - Involves vulnerable populations
- **Direct client assessment** - Scores evaluate counselors, not callers

**Important:** Models trained on this dataset require human-in-the-loop validation and should not autonomously determine counselor employment decisions.

## Dataset Structure

### Data Format

Each record contains:

```json
{
  "id": "record_0",
  "text": "Hello, thank you for calling Child Helpline...",
  "labels": {
    "opening": [1],
    "listening": [1, 1, 0, 1, 1],
    "proactiveness": [1, 1, 0],
    "resolution": [1, 1, 0, 1, 1],
    "hold": [0, 0],
    "closing": [1]
  }
}
```

### Data Fields

- **id** (`string`): Unique identifier (format: `record_{index}`)
- **text** (`string`): Full conversation transcript between counselor and caller
- **labels** (`dict`): Six scoring dimensions, each containing:
  - Binary values (0 or 1) representing competency assessments
  - Multiple evaluations per conversation (except opening/closing)

### Label Categories

The dataset evaluates conversations across **6 main QA dimensions** comprising **17 specific sub-metrics**:

| Category | Sub-Metrics | Count | Description |
|----------|-------------|-------|-------------|
| **opening** | Use of call opening phrase | 1 | Evaluates proper call initiation protocols |
| **listening** | Non-interruption, empathy, paraphrasing, politeness, confidence | 5 | Assesses active listening and communication skills:<br>• Caller was not interrupted<br>• Empathizes with the caller<br>• Paraphrases or rephrases the issue<br>• Uses 'please' and 'thank you'<br>• Does not hesitate or sound unsure |
| **proactiveness** | Extra issue solving, satisfaction confirmation, follow-up | 3 | Measures proactive service approach:<br>• Willing to solve extra issues<br>• Confirms satisfaction with action points<br>• Follows up on case updates |
| **resolution** | Information accuracy, language use, consultation, process adherence, clarity | 5 | Evaluates problem-solving effectiveness:<br>• Gives accurate information<br>• Correct language use<br>• Consults if unsure<br>• Follows correct steps<br>• Explains solution process clearly |
| **hold** | Hold explanation, gratitude for waiting | 2 | Assesses proper hold procedures:<br>• Explains before placing on hold<br>• Thanks caller for holding |
| **closing** | Proper closing phrase | 1 | Evaluates professional call conclusion |

**Total Sub-Metrics:** 17 across 6 main QA dimensions

**Scoring System:**
- **1 (Positive):** Competency clearly demonstrated, criterion met
- **0 (Negative):** Competency absent, criterion not met

**Note:** Each label category can contain multiple binary annotations representing evaluations at different points in the conversation.

### Label Statistics

| Category | Total Annotations | Avg Score | Positive % | Std Dev | Sub-Metrics | Class Balance |
|----------|------------------|-----------|-----------|---------|-------------|---------------|
| **listening** | 510 | 0.671 | 67.1% | 0.470 | 5 | Balanced ✓ |
| **resolution** | 510 | 0.624 | 62.4% | 0.485 | 5 | Balanced ✓ |
| **opening** | 102 | 0.549 | 54.9% | 0.498 | 1 | Balanced ✓ |
| **closing** | 102 | 0.549 | 54.9% | 0.498 | 1 | Balanced ✓ |
| **proactiveness** | 306 | 0.389 | 38.9% | 0.487 | 3 | **Imbalanced ⚠️** |
| **hold** | 204 | 0.196 | 19.6% | 0.397 | 2 | **Severely Imbalanced ⚠️** |

**Total Annotations:** 1,734 across 102 conversations (17 sub-metrics per conversation)

### Text Statistics

| Metric | Mean | Median | Min | Max | Notes |
|--------|------|--------|-----|-----|-------|
| Character Length | 687.81 | 665 | 40 | 2,780 | 3 records < 100 chars |
| Word Count | 125.29 | 117 | 7 | 542 | Appropriate for helpline calls |
| Token Count (approx) | 162.5 | 152 | 9 | 704 | 3 records exceed 512 limit |

**Token Calculation:** `word_count × 1.3` (accounts for DistilBERT subword tokenization)

### Data Splits

**Current Configuration:**
- **Train:** 102 examples (100%)

**Recommended Splits for Model Training:**

```python
from sklearn.model_selection import train_test_split

# Stratified split to maintain label distribution
train_val, test = train_test_split(dataset, test_size=0.15, 
                                     stratify=dataset['labels']['hold'],
                                     random_state=42)
train, val = train_test_split(train_val, test_size=0.176,  # ~15% of total
                               stratify=train_val['labels']['hold'],
                               random_state=42)

# Results: Train=71, Val=15, Test=16
```

**Important:** Use stratified splitting to preserve minority class distribution (especially `hold` at 19.6% positive).

## Dataset Creation

### Curation Rationale

Child helplines provide critical support to vulnerable children, but maintaining consistent quality across counselors is challenging. Manual QA review is:
- **Time-intensive:** Supervisors can only review 5-10% of calls
- **Inconsistent:** Subjective evaluation varies between reviewers
- **Delayed:** Feedback often comes days after calls
- **Unscalable:** Cannot keep pace with call volume

This dataset enables automated QA scoring to:
1. Provide **immediate feedback** to counselors during/after calls
2. **Standardize evaluation** across all conversations
3. **Identify training needs** through systematic performance tracking
4. **Scale quality assurance** to 100% of calls
5. **Support multilingual operations** (expanding to Swahili)

The six scoring dimensions were selected based on:
- Child helpline best practices (Child Helpline International guidelines)
- Counselor training frameworks used in East Africa
- Supervisor feedback on critical performance indicators
- Alignment with DistilBERT's token limits and multi-head architecture

### Source Data

#### Data Collection and Processing

**Source:** Synthetic and anonymized child helpline conversation transcripts from East African helpline services.

**Collection Process:**
1. Real helpline calls were transcribed (with consent where applicable)
2. No PII present in the dataset
3. Conversations were synthesized and shuffled for randomization
4. Transcripts span diverse case types:
   - Crisis intervention (suicide, abuse)
   - Counseling (emotional support, grief)
   - Information/referral services
   - Child protection reporting

**Processing Pipeline:**
1. **Text normalization:** Standardized punctuation, whitespace
2. **PII detection:** No PII
3. **Quality filtering:** Removed incomplete/corrupted transcripts
4. **Token validation:** Identified conversations exceeding 512 tokens
5. **Format standardization:** JSONL structure with consistent schema

**Quality Control:** 
- QC Score: **67/100**
- Processed: 102/102 records (100% success rate)
- Issues identified: 6 records requiring attention (see Bias & Limitations)

## Bias, Risks, and Limitations

### Known Limitations

**1. Data Quality Issues (QC Score: 67/100)**

| Issue | Count | Impact | Mitigation |
|-------|-------|--------|-----------|
| Short conversations | 3 | May lack context for full QA assessment | Filter or augment with context |
| Token overflow (>512) | 3 | Truncation loses conversation context | Apply sliding window or chunking |
| Label distribution warnings | 326 | All-0 or all-1 scores may indicate annotation inconsistencies | Review annotation guidelines |

**2. Class Imbalance**

- **Severe:** `hold` (19.6% positive) - Minority class underrepresented
- **Moderate:** `proactiveness` (38.9% positive) - Below balanced threshold
- **Impact:** Models may struggle to predict minority classes accurately
- **Mitigation:** 
  - Apply class weights: `weight = n_samples / (n_classes × bincount(y))`
  - Use focal loss for hard examples
  - Oversample minority class or undersample majority

**3. Language & Cultural Bias**

- **English-centric:** Dataset primarily in English, limiting generalizability
- **Cultural context:** Counseling norms vary across East African communities
- **Linguistic diversity:** Does not capture regional dialects, code-switching
- **Future work:** Expanding to Swahili, considering cultural adaptation

**4. Synthetic Data Limitations**

- May not capture full complexity of real-time helpline dynamics
- Potential gaps in conversational flow, emotional intensity
- Annotation may reflect idealized responses vs. realistic scenarios

**5. Model Performance Challenges**

Based on label distribution and trained model results:
- **Listening head:** Achieved 71.4% accuracy but 95.7% F1 - model correctly identifies positive cases but has some false negatives
- **Resolution head:** Excellent performance (90.5% accuracy, 98.5% F1)
- **Proactiveness head:** Good performance (85.7% accuracy, 93.6% F1) despite class imbalance (38.9% positive)
- **Hold head:** Challenging but functional (90.5% accuracy, 80% F1) with severe imbalance (19.6% positive)
- **Opening/Closing heads:** Good to perfect performance (85.7% - 100% F1)

### Risks

**1. Model Misuse**
- **Risk:** Automated QA scores used punitively without context
- **Mitigation:** Emphasize scores as training tools, not disciplinary measures

**2. Over-reliance on Automation**
- **Risk:** Human supervisors defer to model judgments uncritically
- **Mitigation:** Require human review for low-scoring calls; use scores as flags, not verdicts

**3. Bias Amplification**
- **Risk:** Models learn and amplify annotation biases
- **Mitigation:** Regular audits of model predictions, diverse annotator pool, fairness metrics

**4. Privacy Breach**
- **Risk:** PII leakage from unmasked conversations
- **Mitigation:** Mandatory PII removal before training; secure data storage

**5. Cultural Mismatch**
- **Risk:** Models trained on one cultural context misapply to another
- **Mitigation:** Test on diverse populations, adapt for regional contexts

### Recommendations

**For Model Developers:**

1. **Preprocessing:**
   - **MANDATORY:**  Consider to apply text truncation or chunking for  longer conversations (>512 tokens)
   - Consider sliding window approach for context preservation

2. **Training Strategy:**
   - Use stratified train/val/test splits to preserve minority classes
   - Apply class weights for `hold` and `proactiveness` heads
   - Monitor per-head learning curves separately
   - Implement early stopping per head (not global)

3. **Evaluation:**
   - Report per-head F1, precision, recall (not just accuracy)
   - Use macro-averaged metrics to account for imbalance
   - Analyze confusion matrices for each head
   - Test on conversations from different helpline regions

4. **Deployment:**
   - Implement human-in-the-loop validation
   - Set confidence thresholds for flagging uncertain predictions
   - Provide explanations (attention visualization) for scores
   - Monitor for performance drift over time

**For Data Users:**

1. **Ethical Use:**
   - Do not use for automated counselor termination decisions
   - Treat QA scores as feedback, not absolute judgments
   - Maintain counselor privacy; aggregate scores for training insights

2. **Context Awareness:**
   - Recognize dataset's East African context
   - Adapt for different helpline protocols/languages
   - Consider cultural norms in counseling practices

3. **Continuous Improvement:**
   - Collect real-world performance data
   - Update annotations based on supervisor feedback
   - Expand to multilingual datasets

**For Supervisors/Helpline Managers:**

1. Use QA scores to identify training opportunities, not punish counselors
2. Combine automated scores with periodic manual reviews
3. Provide constructive feedback based on specific score dimensions
4. Track score trends over time to measure training effectiveness

## Citation

**Dataset BibTeX:**

```bibtex
@dataset{openchs_qa_scoring_2025,
  title={OpenCHS Child Helpline QA Scoring Dataset},
  author={Rogendo and Shemmiriam and Nelsonadagi and openchlai},
  organization={BITZ IT Consulting},
  year={2025},
  publisher={Hugging Face},
  version={1.0},
  url={https://huggingface.co/datasets/openchs/synthetic_helpline_qa_scoring_v1},
  note={Multi-head classification dataset with 17 sub-metrics for automated helpline quality assurance}
}
```

**Trained Model BibTeX:**

```bibtex
@model{qa_helpline_distilbert_2025,
  title={QA Multi-Head DistilBERT for Helpline Quality Assessment},
  author={BITZ IT Consulting Team},
  year={2025},
  publisher={Hugging Face},
  journal={Hugging Face Model Hub},
  howpublished={\url{https://huggingface.co/openchs/qa-helpline-distilbert-v1}},
  note={AI for Social Impact: Child Helplines and Crisis Support in East Africa}
}
```

**APA:**

Rogendo, Shemmiriam, Franklin. (2025). *OpenCHS Child Helpline QA Scoring Dataset* (Version 1.0) [Data set]. Hugging Face. https://huggingface.co/datasets/openchs/synthetic_helpline_qa_scoring_v1

For the trained model, see: BITZ IT Consulting Team. (2025). *QA Multi-Head DistilBERT for Helpline Quality Assessment*. Hugging Face Model Hub. https://huggingface.co/openchs/qa-helpline-distilbert-v1

## Glossary

**QA Scoring:** Quality Assurance evaluation of helpline conversations across standardized dimensions

**Multi-Head Classification:** Neural network architecture with multiple independent output heads, each predicting a different label category

**DistilBERT:** Lightweight transformer model (66M parameters), 40% smaller than BERT with 97% of performance

**Binary Scoring:** Classification into two classes (0 or 1), representing absence or presence of a competency

**Class Imbalance:** Unequal distribution of labels (e.g., 19.6% vs 80.4%), challenging for model training

**Token:** Subword unit in transformer models; DistilBERT has 512-token max input length

**PII (Personal Identifiable Information):** Data that can identify individuals (names, phone numbers, IDs)

**Stratified Splitting:** Data split method that preserves label distribution across train/val/test sets

**Focal Loss:** Loss function that focuses on hard-to-classify examples, useful for imbalanced datasets

**Inter-Annotator Agreement (κ):** Measure of consistency between annotators; κ > 0.7 indicates good agreement

## More Information

**Project Background:**

The OpenCHS (Open Child Helpline System) project aims to leverage AI for improving child protection services in East Africa. This dataset is part of a broader pipeline that includes:
- ASR (Automatic Speech Recognition) for Swahili transcription
- NER (Named Entity Recognition) for case information extraction
- Multilingual translation (Helsinki/opus-mt models)
- Text summarization (FLAN-based)
- This QA scoring component

**Related Datasets:**
- OpenCHS NER Dataset: Entity recognition for helpline conversations
- OpenCHS CLS Dataset: Multi-Case-Classification Dataset [https://huggingface.co/datasets/openchs/synthetic_helpine_classification_v1]

**Trained Models:**
- [`openchs/qa-helpline-distilbert-v1`](https://huggingface.co/openchs/qa-helpline-distilbert-v1) - Multi-head DistilBERT for QA scoring

**Model Performance:**

The trained multi-head DistilBERT model achieves strong performance on this dataset:

| Head | Accuracy | Precision | Recall | F1 Score | Performance Level |
|------|----------|-----------|--------|----------|-------------------|
| **Closing** | 100.0% | 100.0% | 100.0% | 100.0% | Perfect ✓ |
| **Resolution** | 90.5% | 98.5% | 98.5% | 98.5% | Excellent ✓ |
| **Hold** | 90.5% | 66.7% | 100.0% | 80.0% | Good |
| **Proactiveness** | 85.7% | 91.7% | 95.7% | 93.6% | Good |
| **Opening** | 85.7% | 85.7% | 85.7% | 85.7% | Good |
| **Listening** | 71.4% | 98.5% | 93.1% | 95.7% | Mixed ⚠️ |

**Overall Model Performance:**
- Overall Accuracy: ~87.5%
- Average F1 Score: ~91.2%

**Key Insights:**
- Strongest performance on **Closing** and **Resolution** heads (near-perfect scores)
- **Listening head** shows lower accuracy (71.4%) but excellent F1 (95.7%), indicating the model correctly identifies listening behaviors when present
- **Hold head** achieves high recall (100%) but lower precision (66.7%), suggesting conservative predictions
- Class imbalance in training data (proactiveness: 38.9% positive, hold: 19.6% positive) impacts performance on minority classes

**Future Work:**
- Exploring multilingual models (XLM-RoBERTa) for cross-lingual transfer


**Version:** 1.0  
**Last Updated:** July 2025