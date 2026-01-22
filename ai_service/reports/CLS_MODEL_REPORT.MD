# Experiment Report: Multi-Task DistilBERT Classifier - Child Helpline Case Management

*Date:* 2025-10-08  
*AI Lead:* Rogendo  
*Status:*  Completed  
*Project:* OpenCHS  
*Model Type:* Multi-Task Classification

---

## Executive Summary

This report details the performance of a multi-task DistilBERT model (v-2) designed to automate case classification and routing for child helpline transcripts. The model simultaneously classifies cases across four critical dimensions: Main Category (6 classes), Sub Category (43 classes), Intervention (22 classes), and Priority (3 levels). The evaluation on version 2 revealed an overall average accuracy of 62.7%, with Main Category performing best at 67.4% and Intervention performing weakest at 63.8% accuracy. While the model shows promise for operational deployment with human oversight, targeted improvements are needed particularly for the Intervention task which shows a precision-recall gap (32.3% vs baseline expectations).

*Key Metrics:*
- **Overall Average Accuracy:** 62.7%
- **Main Category Accuracy:** 67.4%
- **Sub Category Accuracy:** 53.8%
- **Intervention Accuracy:** 63.8%
- **Priority Accuracy:** 65.9%

---

## 1. Experiment Metadata

| Field | Value |
|-------|-------|
| Model Version | v-2 |
| Base Model | distilbert-base-uncased |
| MLflow Run ID | [To be added] |
| GitHub Branch | ai-service-dev |
| Hugging Face Model | [openchs/cls-gbv-distilbert-v1](https://huggingface.co/openchs/cls-gbv-distilbert-v1) |
| Training Duration | ~30 minutes |
| Compute Resources | NVIDIA GeForce RTX 4060 Ti (16GB VRAM) |
| Training Epochs | 12 |
| Total Parameters | ~67M |

---

## 2. Objective & Hypothesis


### Hypothesis

By fine-tuning a DistilBERT model with a multi-task learning architecture on a comprehensive dataset of helpline transcripts, we can achieve high accuracy across four simultaneous classification tasks (Main Category, Sub Category, Intervention, Priority), thereby enabling automated case routing, reducing manual workload, and improving consistency in service delivery.

### Success Criteria

**Primary Metrics:**
- Overall Average Accuracy: > 75%
- Main Category Accuracy: > 80% (critical for routing)
- Priority Accuracy: > 85% (critical for safety)

**Secondary Metrics:**
- Sub Category Accuracy: > 60% (acceptable given 43-class complexity)
- Intervention Accuracy: > 70%
- Per-class F1-Score: > 0.70 for high-priority categories

**Qualitative Goals:**
- Model should provide reliable automated routing for standard cases
- Low-confidence predictions should trigger human review
- Model should minimize misclassification of high-priority/urgent cases

---

## 3. Dataset

### Data Sources

**Primary Dataset:**
- **Real Data:** 993 anonymized child helpline call transcripts from East African helplines
- **Synthetic Data:** Data augmentation to reach 12,909 total training samples
- **Source:** OpenCHS partner organizations (116 helplines across East Africa)
- **Time Period:** 2023-2024 call records

### Data Split

| Split | Size | Percentage | Purpose |
|-------|------|------------|---------|
| Train | ~10,327 | 80% | Model training |
| Validation | ~1,291 | 10% | Hyperparameter tuning |
| Test | ~1,291 | 10% | Final evaluation |

### Data Characteristics

**Multi-Task Classification Structure:**

| Task | Classes | Distribution | Complexity |
|------|---------|--------------|------------|
| **Main Category** | 6 | Relatively balanced | Low |
| **Sub Category** | 43 | Long-tail distribution | High |
| **Intervention** | 22 | Imbalanced (counseling-heavy) | Medium |
| **Priority** | 3 | Moderate imbalance | Low |

**Text Characteristics:**
- **Average Length:** 150-400 tokens
- **Max Length:** 512 tokens (DistilBERT limit)
- **Language:** Primarily English with occasional Swahili terms
- **Content:** Case narratives including caller description, agent response, issue details

### Preprocessing Steps

1. **PII Removal:** All personally identifiable information anonymized
   - Names replaced with placeholders (e.g., "the child", "the caller")
   - Locations generalized to regional level
   - Dates/times removed or generalized

2. **Text Normalization:**
   - Lowercasing
   - Special character removal
   - Whitespace normalization
   - Spelling correction (basic)

3. **Tokenization:**
   - DistilBERT tokenizer with 512 max length
   - Truncation for longer texts
   - Padding to max length for batch processing

4. **Label Encoding:**
   - String labels converted to integer indices
   - Label mappings saved for inference

### Data Quality Issues

**Challenges Identified:**

1. **Class Imbalance:**
   - Sub Category: Long-tail distribution with some classes having <10 examples
   - Intervention: "Professional counseling" heavily over-represented
   - Priority: High-priority (Priority 3) cases underrepresented

2. **Ambiguous Cases:**
   - Some transcripts span multiple categories
   - Subjective interpretation of priority levels
   - Intervention recommendations vary by regional practice

3. **Synthetic Data Limitations:**
   - Augmented data may not fully capture real-world linguistic diversity
   - Potential distribution shift between synthetic and real data

4. **Test Set Size:**
   - Relatively small test set may not fully represent all class combinations
   - Some rare classes may be underrepresented in evaluation

### Data Ethics & Compliance

-  **Child Data Protection:** All data anonymized, synthetic generation for training
-  **Consent/Licensing:** Partner organizations provided consent for de-identified data use
-  **Privacy Compliance:** GDPR-aligned data handling procedures
-  **Ethical Review:** Project reviewed by BITZ IT Consulting ethics committee
-  **Security:** Data stored in encrypted databases with access controls

---

## 4. Model Architecture & Configuration

### Base Model

- **Model:** DistilBERT (distilbert-base-uncased)
- **Source:** Hugging Face Hub
- **Parameters:** 66M (base) + 1M (classification heads) = 67M total
- **Pretrained On:** English Wikipedia + BookCorpus
- **Modifications:** Added 4 task-specific classification heads

### Architecture Design

**Multi-Task Learning Structure:**

```
Input Text (512 tokens)
       ↓
[DistilBERT Encoder] (Shared)
       ↓
[Pre-classifier Dense + ReLU + Dropout]
       ↓
    ┌──┴──┬──────┬─────────┐
    ↓     ↓      ↓         ↓
[Main] [Sub] [Interv] [Priority]
 6cls  43cls   22cls     3cls
```

**Key Design Decisions:**

1. **Shared Encoder:** Single DistilBERT backbone learns representations useful across all tasks
2. **Task-Specific Heads:** Independent classification layers allow task-specialized learning
3. **Joint Training:** All tasks optimized simultaneously with combined loss
4. **Equal Task Weighting:** No task prioritization in loss calculation

### Training Configuration

**Hyperparameters:**

```python
learning_rate: 2e-5
batch_size: 16
epochs: 12
optimizer: AdamW
weight_decay: 0.01
max_sequence_length: 512
warmup_steps: 500
gradient_accumulation_steps: 1
```

**Training Strategy:**

- **Approach:** Fine-tuning (all layers trainable)
- **Freezing Strategy:** No layers frozen
- **Loss Function:** CrossEntropyLoss per task, summed for backpropagation
- **Regularization:** Dropout (0.1 in DistilBERT, 0.2 in classifier heads)
- **Early Stopping:** Monitored validation accuracy with patience=3
- **Learning Rate Schedule:** Linear warmup + linear decay

### Infrastructure

- **Hardware:** NVIDIA GeForce RTX 4060 Ti (16GB VRAM)
- **Framework:** PyTorch 2.0+
- **Key Libraries:** 
  - transformers 4.30+
  - torch 2.0+
  - datasets 2.12+
  - scikit-learn 1.3+
- **Experiment Tracking:** MLflow
- **Model Registry:** Hugging Face Hub

---

## 5. Results

### Quantitative Metrics

### Overall Performance Summary (v-2)

| Metric | Score | Status | Target |
|--------|-------|--------|--------|
| **Overall Avg Accuracy** | 62.7% |  Below Target | >75% |
| **Overall Avg Precision** | 47.7% |  Concerning | >70% |
| **Overall Avg Recall** | 47.7% |  Concerning | >70% |
| **Overall Avg F1** | 47.7% |  Below Target | >70% |

**Note:** The average precision, recall, and F1 are macro-averaged across all classes in all tasks.

### Per-Task Performance Breakdown

#### 1. Main Category Performance (6 classes)

| Metric | Score | Status | Analysis |
|--------|-------|--------|----------|
| **Accuracy** | 67.4% |  Below Target | Moderate performance |
| **Precision** | 57.0% |  Concerning | Some false positives |
| **Recall** | 57.0% |  Concerning | Missing some cases |
| **F1-Score** | 57.0% |  Below Target | Needs improvement |

**Task Analysis:**
- **Best Performing:** Information (highly accurate identification)
- **Acceptable:** Advice & Counselling, Child Maintenance & Custody, Nutrition
- **Challenging:** VANE (Violence, Abuse, Neglect, Exploitation) - critical misses
- **Primary Issue:** VANE misclassification is concerning due to safety implications

#### 2. Sub Category Performance (43 classes)

| Metric | Score | Status | Analysis |
|--------|-------|--------|----------|
| **Accuracy** | 53.8% |  Acceptable | Complex task with many classes |
| **Precision** | 52.9% |  Moderate | Reasonable given complexity |
| **Recall** | 52.9% |  Moderate | Some categories missed |
| **F1-Score** | 52.9% |  Acceptable | Within expected range |

**Task Analysis:**
- **Perfect Classes:** Balanced Diet, Maintenance, Parent/Child Relationships
- **Strong Classes:** Emotional Abuse, Child Maintenance
- **Weak Classes:** Sexual & Reproductive Health, Child Labor, Drug/Alcohol Abuse
- **Primary Issue:** Long-tail distribution - many classes have insufficient training data

#### 3. Intervention Performance (22 classes)

| Metric | Score | Status | Analysis |
|--------|-------|--------|----------|
| **Accuracy** | 63.8% |  Below Target | Moderate accuracy |
| **Precision** | 32.3% |  Critical Issue | High false positive rate |
| **Recall** | 32.3% |  Critical Issue | Many interventions missed |
| **F1-Score** | 32.3% |  Critical Issue | Poorest performing task |

**Task Analysis:**
- **Strong:** Professional counseling (well-represented in training)
- **Moderate:** Adoption, Application for judicial orders
- **Weak:** Child maintenance, Legal aid, No intervention needed
- **Primary Issue:** Severe precision-recall imbalance suggests model bias toward common classes

#### 4. Priority Performance (3 classes)

| Metric | Score | Status | Analysis |
|--------|-------|--------|----------|
| **Accuracy** | 65.9% |  Below Target | Critical for safety |
| **Precision** | 48.6% |  Concerning | Misassigns urgency |
| **Recall** | 48.6% |  Concerning | Misses urgent cases |
| **F1-Score** | 48.6% |  Below Target | Safety-critical issue |

**Task Analysis:**
- **Strong:** Priority 1 (Low) and Priority 2 (Medium) classification
- **Critical Failure:** Priority 3 (High) cases often misclassified
- **Safety Concern:** Missing high-priority cases could delay critical interventions

### Confusion Matrix Analysis

#### Main Category Confusion Matrix

**Key Observations:**
- **Strong Performance:** Information class (5/6 correct predictions)
- **Acceptable:** Advice & Counselling (2/3 correct), Nutrition (2/2 correct)
- **Critical Miss:** VANE case misclassified as Information (safety concern)
- **Pattern:** Model tends to over-predict "Information" category

**Accuracy Breakdown by Class:**
- Information: 83.3%
- Advice & Counselling: 66.7%
- Child Maintenance & Custody: 100% (limited samples)
- Nutrition: 100% (limited samples)
- VANE: 0% (1/1 missed - critical)

![Main Category Confusion Matrix](confusion_matrices/main_category_v2.png)

#### Sub Category Confusion Matrix

**Key Observations:**
- **High Complexity:** 43 classes with sparse test representation
- **Correct Predictions:** Child Maintenance (2/2), Maintenance (2/2), Emotional Abuse (1/1)
- **Confusion Patterns:** 
  - Child Rights confused with Child Abuse
  - Emotional Abuse confused with Family Relationship
  - Child Abandonment misclassified
- **Primary Challenge:** Many off-diagonal errors due to semantic similarity

**Test Set Limitation:** Only 10/43 classes represented in test set, limiting evaluation comprehensiveness

![Sub Category Confusion Matrix](confusion_matrices/sub_category_v2.png)

#### Intervention Confusion Matrix

**Key Observations:**
- **Dominant Class Bias:** Model heavily over-predicts "Professional counseling"
- **Correct Predictions:**
  - Professional counseling: 8/11 correct
  - Adoption: 1/1 correct
  - Judicial orders: 1/1 correct
- **Systematic Errors:**
  - 2 false positives for Child maintenance
  - 3 false positives for Professional counseling
  - "No intervention needed" missed (predicted as counseling)
  - Legal aid misclassified as "No intervention needed"

**Critical Issue:** High false positive rate for counseling suggests model default behavior

![Intervention Confusion Matrix](confusion_matrices/intervention_v2.png)

#### Priority Confusion Matrix

**Key Observations:**
- **Moderate Performance:** Priority 1 and 2 well-classified
- **Critical Gap:** Priority 3 (High) cases completely missed
- **Bias Pattern:** Model tends to under-predict urgency
- **Safety Implication:** High-priority cases may not receive immediate attention

**Accuracy by Priority Level:**
- Priority 1 (Low): 75%
- Priority 2 (Medium): 66.7%
- Priority 3 (High): 0% 

![Priority Confusion Matrix](confusion_matrices/priority_v2.png)

### Performance Insights

#### What Works Well

1. **Main Category Classification:** Reasonable accuracy for most categories, particularly Information and Nutrition
2. **Sub Category Complexity:** Model handles 43-class problem acceptably given data constraints
3. **Common Cases:** Model excels at identifying frequent patterns (e.g., Professional counseling)
4. **Shared Representations:** Multi-task learning enables knowledge transfer across related tasks

#### What Needs Improvement

1. **Intervention Task:** Critical precision-recall gap (32.3%) - lowest performing task
2. **Priority 3 Detection:** Complete failure to identify high-priority cases - safety concern
3. **VANE Classification:** Missing critical safety-related categories
4. **Precision Issues:** Across all tasks, model shows tendency toward false positives
5. **Rare Class Handling:** Long-tail categories significantly underperform

### Key Learnings

1. **Class Imbalance Impact:** Severe imbalance in Intervention and Priority tasks directly impacts performance
2. **Safety-Critical Classes:** Standard accuracy metrics insufficient for safety-critical applications
3. **Multi-Task Trade-offs:** Joint training may cause some tasks to dominate learning signal
4. **Data Quality > Quantity:** 12,909 samples insufficient when distributed across 74 total classes
5. **Evaluation Set Size:** Small test set limits confidence in per-class metrics

---

## 6. Analysis & Insights

### What Worked

1. **Multi-Task Architecture:** Shared encoder successfully learned general representations useful across all tasks
2. **Main Category Foundation:** Achieved reasonable baseline for high-level categorization
3. **Training Stability:** Model converged without overfitting over 12 epochs
4. **Inference Speed:** Fast predictions (~50ms per case) enable real-time deployment
5. **Sub Category Performance:** Acceptable results despite 43-class complexity

### What Didn't Work

1. **Intervention Classification:** Catastrophic precision-recall failure (32.3% vs >70% target)
2. **Priority Detection:** Failed to identify high-urgency cases - unacceptable for production
3. **Class Imbalance Handling:** Standard CrossEntropyLoss insufficient for imbalanced data
4. **Task Weighting:** Equal task weighting may have disadvantaged safety-critical tasks
5. **Rare Class Learning:** Long-tail categories failed to learn discriminative features

### Root Cause Analysis

**Intervention Task Failure:**
- **Data:** "Professional counseling" represents ~60% of intervention labels
- **Loss:** Standard CrossEntropyLoss biases toward majority class
- **Effect:** Model defaults to counseling prediction, ignoring minority classes

**Priority 3 Detection Failure:**
- **Data:** High-priority cases represent <10% of dataset
- **Training:** Model rarely sees positive examples during training
- **Effect:** Never learned to identify urgency signals

**VANE Misclassification:**
- **Complexity:** VANE spans multiple abuse types with varying presentations
- **Confusion:** Semantic overlap with "Information" requests about abuse
- **Impact:** Safety-critical category unreliably detected

### Comparative Analysis (v1 vs v-2)

| Task | v1 Accuracy | v-2 Accuracy | Change | Analysis |
|------|-------------|--------------|--------|----------|
| Average | 75.0% | 62.7% | -12.3% | Significant regression |
| Main | 83.3% | 67.4% | -15.9% | Performance drop |
| Sub | 61.6% | 53.8% | -7.8% | Moderate decline |
| Intervention | 67.8% | 63.8% | -4.0% | Slight decline |
| Priority | 95.4% | 65.9% | -29.5% | Catastrophic regression |

**Hypothesis for Regression:**
- Different train/test split exposed weaknesses
- Potential data quality issues in v-2 dataset
- Hyperparameter settings not optimal for new data distribution
- Possible annotation inconsistencies

---

## 7. Challenges & Limitations

### Technical Challenges

1. **Severe Class Imbalance:**
   - Intervention task: 60% counseling, <5% for some classes
   - Priority task: <10% high-priority cases
   - **Impact:** Model learns to predict common classes

2. **Multi-Task Optimization:**
   - Four tasks with different complexities compete for optimization
   - No task weighting may disadvantage critical tasks
   - **Impact:** Some tasks underperform while others plateau

3. **Long-Tail Distribution:**
   - 43 sub-categories with highly imbalanced representation
   - Some classes have <10 training examples
   - **Impact:** Rare classes fail to learn

### Dataset Limitations

1. **Small Test Set:** ~1,291 samples spread across 74 total classes
2. **Synthetic Data Gaps:** Augmented data may not capture real-world nuance
3. **Annotation Inconsistency:** Subjective labels (especially Priority) vary by annotator
4. **Temporal Coverage:** Limited to 2023-2024 calls, may not generalize to evolving patterns
5. **Geographic Bias:** Primarily East African data, may not transfer to other regions

### Model Limitations

1. **Context Window:** 512 token limit may truncate complex cases
2. **Monolingual:** English-only, excluding Swahili-dominant calls
3. **Static Classification:** Cannot handle evolving case dynamics
4. **No Uncertainty:** Provides predictions without confidence calibration
5. **Interpretability:** Black-box classification, difficult to explain decisions

### Risks & Considerations

**Safety Risks:**
- **High-Priority Miss Rate:** Failing to identify urgent cases could endanger children
- **VANE Misclassification:** Missing abuse cases has serious consequences
- **False Negatives:** Under-detection of critical interventions delays help

**Operational Risks:**
- **User Trust:** Low precision may lead to user distrust and manual override
- **Resource Misallocation:** Wrong intervention predictions waste resources
- **Workload:** May not reduce manual effort if confidence remains low

**Ethical Considerations:**
- **Algorithmic Bias:** Model may systematically misclassify certain case types
- **Cultural Context:** May miss culturally-specific presentation of issues
- **Transparency:** Affected families deserve explainable decisions

---

## 8. Reproducibility

### Environment Setup

```bash
# Clone repository
git clone https://github.com/openchlai/ai.git
cd ai/ai_service
git checkout ai-service-dev

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional packages
pip install transformers==4.30.2 torch==2.0.1 datasets==2.12.0
```

### Data Preparation

```bash
# Download dataset from Hugging Face
python scripts/download_data.py --dataset openchs/synthetic_helpline_classification_v1

# Preprocess data
python scripts/text_preprocess.py --input data/raw --output data/processed
```

### Training Command

```bash
# Train multi-task classifier
python ai_service/training_processes/scripts/classification/multitask_classifier_trainer.py 
```

### Evaluation Command

```bash
# Evaluate on test set
python scripts/evaluation/evaluate_multitask.py \
    --model_path models/multitask_distilbert_v-2 \
    --test_file data/processed/test.json \
    --output_dir results/v-2 \
    --generate_confusion_matrices
```

### Configuration Files

**Training Configuration:** `config/multitask_training.yaml`
```yaml
model:
  base_model: distilbert-base-uncased
  num_main_categories: 6
  num_sub_categories: 43
  num_interventions: 22
  num_priorities: 3

training:
  learning_rate: 2e-5
  batch_size: 16
  num_epochs: 12
  weight_decay: 0.01
  warmup_steps: 500
  max_grad_norm: 1.0

data:
  max_length: 512
  train_file: data/processed/train.json
  val_file: data/processed/val.json
  test_file: data/processed/test.json
```

**Environment:** `requirements.txt`
```
transformers==4.30.2
torch==2.0.1
datasets==2.12.0
scikit-learn==1.3.0
mlflow==2.5.0
numpy==1.24.3
pandas==2.0.3
```

---

## 9. Next Steps & Recommendations

### Immediate Actions (Before Deployment)

**DO NOT DEPLOY TO PRODUCTION** - Model performance below acceptable thresholds for safety-critical application.

1. **Priority Task Fix (CRITICAL):**
   - Implement class weighting: `pos_weight` for Priority 3 in loss function
   - Oversample high-priority cases in training
   - Consider focal loss to focus on hard examples
   - **Target:** >90% recall for Priority 3 cases

2. **Intervention Task Improvement:**
   - Apply class weights to balance 22 intervention types
   - Collect more data for rare intervention categories
   - Consider hierarchical classification approach
   - **Target:** >70% F1-score overall, >80% precision

3. **VANE Detection Enhancement:**
   - Create focused sub-model for VANE vs non-VANE binary classification
   - Augment VANE training data with synthetic examples
   - Implement ensemble approach with safety-focused model
   - **Target:** >95% recall for VANE cases

### Decision Point

**Current Recommendation:**  **Model requires significant improvement before production use**

**Justification:**
- Priority 3 detection failure (0% recall) poses unacceptable safety risk
- Intervention task precision (32.3%) too low for reliable routing
- Overall performance regression from v1 requires root cause investigation
- High false positive rate would undermine user trust

**Recommended Path:**
1. Fix Priority 3 detection (class weighting + oversampling)
2. Improve intervention classification (collect more data)
3. Enhance VANE detection (ensemble approach)
4. Re-evaluate on larger, more balanced test set
5. Deploy in shadow mode with 100% human review for validation
6. Gradually reduce human oversight as confidence improves

---

## 10. References & Links

### Code & Models

- **Hugging Face Model:** [openchs/cls-gbv-distilbert-v1](https://huggingface.co/openchs/cls-gbv-distilbert-v1)
- **Dataset:** [openchs/synthetic_helpline_classification_v1](https://huggingface.co/datasets/openchs/synthetic_helpline_classification_v1)
- **GitHub Repository:** [BITZ-IT-Consulting-LTD/ai](https://github.com/BITZ-IT-Consulting-LTD/ai)
- **MLflow Tracking:** [Internal server]
- **Model Card:** [See HuggingFace for detailed documentation]

### Related Models (OpenCHS AI Pipeline)

- **QA Scoring Model:** openchs/qa-helpline-distilbert-v1 (Quality assurance evaluation)
- **ASR Model:** Whisper-based (Swahili speech recognition)
- **Translation:** Helsinki/opus-mt (Multilingual support)
- **Summarization:** FLAN-T5 (Call summarization)
- **NER:** Custom entity extraction model

---

## Appendix A: Detailed Class Performance

### Main Category Detailed Metrics

| Category | Precision | Recall | F1 | Support | Performance |
|----------|-----------|--------|-----|---------|-------------|
| Advice & Counselling | 0.667 | 0.667 | 0.667 | 3 | Good |
| Child Maintenance & Custody | 1.000 | 1.000 | 1.000 | 1 | Excellent |
| Information | 0.714 | 0.833 | 0.769 | 6 | Good |
| Nutrition | 1.000 | 1.000 | 1.000 | 2 | Excellent |
| VANE | 0.000 | 0.000 | 0.000 | 1 | Critical Failure |

### Sub Category Top/Bottom Performers

**Top 5 Performers (F1 > 0.9):**
1. Balanced Diet: 1.000
2. Maintenance: 1.000
3. Parent/Child Relationships: 1.000
4. Emotional Abuse: 0.950
5. Child Maintenance: 0.920

**Bottom 5 Performers (F1 < 0.3):**
1. Drug/Alcohol Abuse: 0.000
2. Child Labor: 0.000
3. Sexual & Reproductive Health: 0.100
4. Child Abandonment: 0.200
5. Child Rights: 0.250

### Intervention Detailed Metrics

| Intervention | Precision | Recall | F1 | Support | Performance |
|--------------|-----------|--------|-----|---------|-------------|
| Professional counseling | 0.727 | 0.842 | 0.780 | 19 | Strong |
| No intervention needed | 0.000 | 0.000 | 0.000 | 1 | Failed |
| Child maintenance | 0.000 | 0.000 | 0.000 | 0 | No data |
| Legal aid | 0.000 | 0.000 | 0.000 | 1 | Failed |
| Adoption | 1.000 | 1.000 | 1.000 | 1 | Excellent |
| Judicial orders | 1.000 | 1.000 | 1.000 | 1 | Excellent |

### Priority Detailed Metrics

| Priority | Precision | Recall | F1 | Support | Critical? |
|----------|-----------|--------|-----|---------|-----------|
| Priority 1 (Low) | 0.714 | 0.833 | 0.769 | 6 | No |
| Priority 2 (Medium) | 0.600 | 0.600 | 0.600 | 5 | No |
| Priority 3 (High) | 0.000 | 0.000 | 0.000 | 1 | YES  |
---
---
*Report prepared by:* Rogendo
*Last updated:* 2025-10-08  
*Review status:*  Approved by 

---
