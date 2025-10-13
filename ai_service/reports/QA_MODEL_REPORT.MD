# Experiment Report: QA Multi-Head DistilBERT - Quality Assurance for Helpline Transcripts

*Date:* 2025-10-08  
*AI Lead:* Rogendo  
*Status:* ⁠ Completed ⁠  
*Project:* OpenCHS  
*Model Type:* Classification

---


## Executive Summary
This report details the performance of a multi-head DistilBERT model developed to automate quality assurance for helpline call transcripts. The model was designed to classify calls against 17 sub-metrics across 6 quality dimensions. The evaluation revealed that while the model excels at identifying positive cases (high recall), it suffers from critically low precision due to a strong bias towards positive predictions. The overall accuracy is 42.2%, which is below the acceptable threshold. The primary recommendation is to not deploy the model in its current state and to proceed with further iterations to address the precision issue.

*Key Metrics:*
•⁠  ⁠Primary Metric: Overall F1-Score: ~87.5%

---

## 1. Experiment Metadata

| Field | Value |
|-------|-------|
| Model Version | v1.0.0 |
| Base Model | distilbert-base-uncased |
| MLflow Run ID | a86060a18b304d8b87f5606c94584ff2 |
| GitHub Branch |  |
| Hugging Face Model | [openchs/qa-helpline-distilbert-v1](https://huggingface.co/openchs/qa-helpline-distilbert-v1) |
| Training Duration | 20 |
| Compute Resources |  |

---

## 2. Objective & Hypothesis

### Problem Statement
Supervisors in child helplines and crisis support call centers manually review calls for quality assurance, a process that is not scalable. This leads to most calls going unmonitored, creating a gap in quality control and agent feedback. This experiment aims to automate the QA process using a multi-head classification model to evaluate call transcripts against a set of quality metrics.

### Hypothesis
By fine-tuning a DistilBERT model with a multi-head classification architecture on a custom dataset of helpline transcripts, we can achieve high accuracy in automatically assessing call quality across multiple dimensions, thereby reducing manual effort and improving the consistency of service.

### Success Criteria
<!-- Define clear, measurable targets -->
•⁠  ⁠*Primary Metric:* Overall F1-Score > 90%
•⁠  ⁠*Secondary Metrics:*
  - Per-Head F1-Score: > 85%
  - Overall Accuracy: > 85%
•⁠  ⁠*Qualitative Goals:* The model should provide reliable and actionable feedback for agent performance improvement.


## QA Heads Configuration

| Head | Submetrics | Description |
|------|------------|-------------|
| **Opening** | 1 | Use of proper call opening phrase |
| **Listening** | 5 | Interruption, empathy, paraphrasing, politeness, confidence |
| **Proactiveness** | 3 | Extra issue solving, satisfaction confirmation, follow-up |
| **Resolution** | 5 | Information accuracy, language use, consultation, process steps, explanation clarity |
| **Hold** | 2 | Pre-hold explanation, post-hold courtesy |
| **Closing** | 1 | Proper call closing phrase |


---

## 3. Dataset

### Data Sources
•⁠  ⁠*Source 1:* Custom internal dataset of child helpline and crisis support transcripts.
•⁠  ⁠*Total:* 102 synthtic records

### Data Split
| Split | Size | Percentage |
|-------|------|------------|
| Train | 82 | 0.8 |
| Validation | 10 | 0.1 |
| Test | 10 samples | 0.1 |

### Data Characteristics
*For Classification:*
•⁠  ⁠Number of classes: 17 (distributed across 6 heads)
•⁠  ⁠Class distribution: Imbalanced
•⁠  ⁠Average text length: 500 tokens

### Preprocessing Steps
- ⁠Text normalization

- ⁠PII removal (trained on synthetic data)

- Tokenization and padding to 512 tokens


### Data Quality Issues
•⁠  ⁠The evaluation dataset is very small (10 samples), which may not be representative of the model's true performance.

•  The training set dataset is very minimal, (82 samples), which may not fully represent the data features and metrics.

•⁠  ⁠The labels in the dataset are highly imbalanced, with a strong skew towards positive examples for some metrics.

### Data Ethics & Compliance
•⁠  ⁠ Child data protection measures implemented (trained on synthetic data)
•⁠  ⁠ Consent/licensing verified

---

## 4. Model Architecture & Configuration

### Base Model
•⁠  ⁠*Model:* DistilBERT (distilbert-base-uncased)

•⁠  ⁠*Source:* Hugging Face hub

•⁠  ⁠*Parameters:* 66 million

•⁠  ⁠*Modifications:* A multi-head classification layer was added on top of the base model, with each head corresponding to a QA dimension (67 million parameters).

**Training Approach**: Multi-task learning with BCEWithLogitsLoss per head

**Evaluation**: Comprehensive metrics across all QA dimensions


### Training Configuration

*Hyperparameters:*

learning_rate: 2.0e-05

batch_size: 4

epochs: 5

optimizer: AdamW

max_sequence_length: 512

 ⁠
*Training Strategy:*

•⁠  ⁠Approach: Fine-tuning

•⁠  ⁠Freezing strategy: No layers frozen

•⁠  ⁠Loss function: BCEWithLogitsLoss (per head)

•⁠  ⁠Regularization: Dropout (0.2)

### Infrastructure
- ⁠*Hardware:*  NVIDIA GeForce RTX 4060 Ti

- ⁠*Framework:* PyTorch

-  ⁠*Key Libraries:* transformers, torch



---

## 5. Results

### Quantitative Metrics

### Overall Performance Summary

| Metric | Score | Interpretation |
|--------|-------|----------------|
| **Overall Accuracy** | 42.2% | Below acceptable threshold |
| **Overall Precision** | 14.7% | **Critical Issue**: High false positive rate |
| **Overall Recall** | 90.9% | **Strength**: Captures most positive cases |
| **Overall F1** | 25.3% | Poor balance between precision and recall |
| **Hamming Loss** | 57.8% | High error rate across all labels |


## Detailed Per-Head Performance

### Key Finding
** Primary Issue**: The model exhibits extreme bias toward positive predictions, resulting in high recall but critically low precision.

## Head-by-Head Performance Analysis

###  Best Performing Heads

#### 1. HOLD (Rank #1)
- **Exact Match Ratio**: 66.7% 
- **Key Strength**: Best overall head performance
- **Issue**: Zero F1 score due to prediction misalignment
- **Submetrics**:
  - *Explains before placing on hold*: 66.7% accuracy
  - *Thanks caller for holding*: 83.3% accuracy

#### 2. CLOSING (Rank #2)
- **Exact Match Ratio**: 50.0%
- **F1 Score**: 40.0%  (Highest F1)
- **Balanced Performance**: Reasonable precision-recall trade-off
- **Submetric**: *Proper call closing phrase*: 50% accuracy, 25% precision

###  Moderate Performance

#### 3. OPENING (Rank #3)
- **Exact Match Ratio**: 33.3%
- **F1 Score**: 33.3%
- **Performance**: Acceptable for single-metric head
- **Submetric**: *Use of call opening phrase*: Perfect recall (100%) but low precision (20%)

###  Underperforming Heads

#### 4. RESOLUTION (Rank #4)
- **Exact Match Ratio**: 16.7%
- **F1 Score**: 25.7%
- **Challenge**: Complex 5-submetric evaluation
- **Critical Submetrics**:
  -  *Gives accurate information*: 33.3% F1
  -  *Correct language use*: 28.6% F1
  -  *Consults if unsure*: 0% F1 (no support data)

#### 5. PROACTIVENESS (Rank #5)
- **Exact Match Ratio**: 16.7%
- **F1 Score**: 13.3%
- **Major Issues**: 2 out of 3 submetrics have zero performance
- **Only Working Submetric**: *Confirms satisfaction* (40% F1)

#### 6. LISTENING (Rank #6)
- **Exact Match Ratio**: 0% 
- **F1 Score**: 20.4%
- **Critical Failure**: No samples achieved perfect 5-submetric match
- **Submetric Breakdown**:
  - *Paraphrases or rephrases*: 40% F1 (best in head)
  - *Uses please and thank you*: 33.3% F1
  - *Caller was not interrupted*: 28.6% F1
  - *Empathizes with caller*: 0% F1
  - *Does not hesitate*: 0% F1

### Confusion Matrices
  - for each individual metric and it's sub metrics.




### Performance Insights

### Qualitative Observations
•⁠  ⁠*What works well:* The model is not so bad at identifying when a quality metric has been met . It  misses a positive case but not as often.
•⁠  ⁠*What needs improvement:* The model has an extremely high false positive rate (low precision). It predicts "Yes" for most metrics, regardless of the actual content of the transcript. This makes the model unreliable for practical use. Needs more training data.

### Performance by Subset
The dataset was too small to perform a meaningful analysis by subset.

### Confusion Matrices
![alt text](qa_confusion_matrices/opening_confusion_matrix3.png)
![alt text](qa_confusion_matrices/hold_confusion_matrix3.png)
![alt text](qa_confusion_matrices/listening_confusion_matrix3.png)
![alt text](qa_confusion_matrices/resolution_confusion_matrix3.png)
![alt text](qa_confusion_matrices/proactiveness_confusion_matrix3.png)
![alt text](qa_confusion_matrices/closing_confusion_matrix3.png)
---

## 6. Analysis & Insights

### What Worked
1.⁠ ⁠**High Recall:** The training strategy was successful in ensuring the model learned to capture nearly all instances of positive behavior. This suggests the features for positive classes are being learned.

### What Didn't Work
1.⁠ ⁠**Low Precision:** The model failed to learn the distinction between positive and negative cases, resulting in an unacceptably high number of false positives. This could be due to the imbalanced dataset, the choice of loss function, or the model architecture not being complex enough to capture the nuances of the negative class.
2.⁠ ⁠**Overall Performance:** The model's overall performance is  low for any practical application, particularly on noisy data such as helpline data. 

### Key Learnings
•⁠  ⁠A small and imbalanced dataset can lead to a model with high bias.
•⁠  ⁠For multi-label classification tasks with imbalanced data, accuracy and recall are not sufficient metrics to judge performance. Precision and F1-score are more informative.

---

## 7. Challenges & Limitations

### Technical Challenges
•⁠  ⁠**Model Bias:** The most significant challenge is the model's bias towards the positive class.

### Dataset Limitations
•⁠  ⁠**Size:** The training data comprised of 102 records, which is very minimal and evaluation was conducted on a very small dataset of 10 samples, which is not sufficient to draw robust conclusions.
•⁠  ⁠**Imbalance:** The dataset is heavily imbalanced, which likely contributed to the model's  performance.

### Model Limitations
•⁠  ⁠**Generalization:** The model, in its current state, generalize neearly well and is not suitable for production use, but it could get better as the small sample size indicated that we need more data.

### Risks & Considerations
•⁠  ⁠*Fairness:* The model's current bias makes it almost unfair and unreliable for evaluating agent performance, but the misclassifcations are not nearly correct, when introducing a threshold.
•⁠  ⁠*Safety:* Deploying this model could lead to incorrect assessments of critical interactions, potentially masking some metrics.

---

## 8. Reproducibility

#### Clone repository
git clone https://github.com/BITZ-IT-Consulting-LTD/ai.git
cd ai/ai_service
git checkout [ai-service-dev]

# Install dependencies
pip install -r requirements.txt
 ⁠

### Training Command
⁠ bash
# Exact command to reproduce this experiment
python ai_service/training&processes/scripts/classification/multitask_classifier_trainer.py 
 ⁠

### Evaluation Command

python eval.py \
    --model_path all_qa_distilbert_v1 \
    --test_data eval_data.json
 ⁠

### Configuration Files
•⁠  ⁠Training config: See section 4
•⁠  ⁠Environment: ⁠ requirements.txt ⁠

---

## 9. Next Steps & Recommendations

### Immediate Actions
•⁠  ⁠Do not deploy the model.

•⁠  ⁠Augment the training and evaluation datasets with more balanced examples, especially for negative cases.

•⁠  Label more training dataset.


### Future Experiments
⁠ ⁠*Hypothesis:* A larger, more balanced dataset will improve the model's precision.
   - *Approach:* Collect and label more data, ensuring a better balance between positive and negative examples for each sub-metric. Retrain the model on the new dataset.
   - *Expected impact:* A significant increase in precision and F1-score.



### Decision Point
*Recommendation:*
•⁠  Model needs significant improvement

*Justification:* The model's performance, particularly its low precision, makes it unsuitable for its intended purpose. The high rate of false positives would provide misleading and inaccurate feedback, undermining the goal of improving quality assurance.

---

## 10. References & Links

### Code & Models
•⁠  ⁠*Hugging Face Model:* [openchs/qa-helpline-distilbert-v1](https://huggingface.co/opeenchs/qa-helpline-distilbert-v1)

•⁠  *Dataset:* [openchs/synthetic_helpline_qa_scoring_v1](https://huggingface.co/datasets/openchs/synthetic_helpline_qa_scoring_v1)

---


*Report prepared by:* Rogendo
*Last updated:* 2025-10-08  
*Review status:* [✅] Approved by 
