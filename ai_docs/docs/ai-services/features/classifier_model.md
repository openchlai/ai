## **DistilBERT Multi-Label Classification Model Documentation**

**Objective**

This document serves as the official guide for the fine-tuned DistilBERT-Uncased classification model. Its purpose is to provide a complete technical and functional overview for engineering and product teams, enabling them to understand, integrate, and effectively use the model for automated case categorization in call center scenarios.

-----

### **1. Model Overview** 

The model is a **multi-label text classification model** built on the **DistilBERT-base-uncased** architecture. DistilBERT, a distilled version of BERT, was chosen for its optimal balance of performance and computational efficiency, which is critical for real-time inference in a high-volume call center environment.

  * **Architecture**: The model consists of the pre-trained DistilBERT encoder followed by a custom **classification head**. This head is a linear layer with a sigmoid activation function, which is essential for multi-label classification as it allows the model to predict multiple independent labels for a single input.
  * **Training Data**: The model was fine-tuned on a proprietary dataset of over 1,000 anonymized call transcripts and 10,000 Synthetic call transcripts. The dataset was meticulously cleaned, annotated, balanced and stratified strategically to minimize bias and maximize generalization.
      * **Data Characteristics**: The data includes transcripts from diverse call types, ensuring the model can handle various linguistic patterns, from formal inquiries to informal complaints. The multi-label nature of the data required each transcript to be annotated with one or more relevant categories.
  * **Fine-Tuning Process**: The model was trained with the following key configurations:
      * **Loss Function**: Binary Cross-Entropy (BCE) with logits, which is appropriate for multi-label tasks where each label is treated as a separate binary classification problem.
      * **Optimizer**: AdamW.
      * **Training Schedule**: A learning rate scheduler with a warm-up phase was used to ensure stable training.

-----

### **2. Classification Tasks and Class Definitions**

The model performs multi-label classification across four distinct classification tasks. For each task, the model can assign one or more labels. The full list of supported categories and their definitions is provided below.

| Classification Task | Labels | Definition |
| :--- | :--- | :--- |
| **Sub-Topic Categorization** | `Adoption`, `Albinism`, `Balanced Diet`, `Birth Registration`,`Breast Feeding`, `etc` | Categorizes the caller's reason for the call. This is crucial for real-time agent feedback and post-call analysis. |
| **Priority/Urgency Detection** | `Low`, `Medium`, `High` | Assesses the criticality of the customer's issue. `High` urgency cases are flagged for immediate escalation to a supervisor queue. |
| **Main Topic Categorization** | `Advice and Counselling`, `Child Maintenance & Custody`, `Disability`, `GBV`, `VANE`, `Nutrition`, `Information` | The primary function of the model, used to tag the call's content. |
| **Intervention** | `Referred`, `Counselling`, `Signposting`, `Awareness/Information Provided` | Predicts the final state of the call based on the conversation, helping to automate case management and follow-up procedures. |

-----

### **3. Performance Metrics**

The model's performance is monitored continuously on a separate, un-seen validation set. The metrics are reported using a **"micro-average"** approach, which aggregates the contributions of all classes to compute the average metric. This is particularly useful for multi-label classification with imbalanced classes.

  * **Micro-F1 Score**: The primary metric for overall model performance. It provides a single score that balances precision and recall across all labels. A high micro-F1 score indicates that the model is performing well on all classes, including minority ones.
  * **Precision, Recall by Class**: These metrics are tracked for each individual label to provide granular insight into the model's performance. For instance, high precision on the "Urgent" label is critical to avoid false escalations, while high recall on "VANE" is vital to catch every instance of a major issue.
  * **Confusion Matrices**: Given the multi-label nature of the model, a standard confusion matrix is replaced by a set of **per-class confusion matrices**. Each matrix shows the performance of the model for one specific label, treating it as a binary classification problem (e.g., "Is this call `VANE` related?").

-----

### **4. Usage Examples**

#### **4.0 Response Format**

The response from the `/classifier/classify` endpoint is a JSON object with the following fields:

```json
{
  "main_category": "The main category of the case.",
  "sub_category": "The sub-category of the case.",
  "intervention": "The recommended intervention for the case.",
  "priority": "The priority of the case.",
  "processing_time": "The time taken to process the request.",
  "model_info": {
    "model_path": "The path to the model.",
    "loaded": "Whether the model is loaded.",
    "load_time": "The time when the model was loaded.",
    "device": "The device on which the model is running.",
    "error": "Any error that occurred during model loading."
  },
  "timestamp": "The timestamp of the request."
}
```
#### **4.1. API Endpoints**

  * **Primary Endpoint**: `POST /classifier/classify`
  * **Request Body (JSON)**:
    ```json
    {
      "text_transcript": "The transcript of the call goes here. It needs to be a single string."
    }
    ```
  * **Example Response (JSON)**:
    ```json
    {
      "case_id": "c-1a2b3c4d",
      "predictions": {
        "sub_category": {
          "label": "Information",
          "confidence": 0.92
        },
        "priority": {
          "label": "1",
          "confidence": 0.85
        },
        "main_category": 
          {
            "label": "Nutrition",
            "confidence": 0.95
          }
        ,
        "intervention": {
          "label": "Counseling",
          "confidence": 0.89
        }
      }
    }
    ```
  - Curl request

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"narrative": "A 12-year-old girl is being abused by her stepfather."}' \
      http://localhost:8123/classifier/classify
    ```

#### **4.2. Input Text Processing**

The Classify function expects a raw, clean transcript string. The model's serving pipeline handles all necessary preprocessing steps, including:

  * **Normalization**: Converting all text to lowercase and removing irrelevant characters.
  * **Tokenization**: Segmenting the text into tokens using the DistilBERT tokenizer, which handles sub-word units and special characters.

-----

### **5. Confidence Thresholds**

The confidence score returned for each prediction is a probability value (0 to 1) indicating the model's certainty. The choice of threshold is a business decision that should be tuned based on the application's risk tolerance.

  * **High Thresholds (e.g., \> 0.90)**: Recommended for **critical, automated actions** like case escalation or auto-creation of a trouble ticket. This ensures high precision and minimizes false positives, but may result in lower recall (i.e., missing some relevant cases).
  * **Medium Thresholds (e.g., \> 0.75)**: Ideal for **data enrichment and analytics**. This provides a broader set of tags for dashboards and reports, balancing precision and recall to get a more complete picture of call trends.
  * **Low Thresholds (e.g., \> 0.50)**: Can be used for **human-in-the-loop applications**, where predictions serve as suggestions to an agent or reviewer. A lower threshold increases recall, ensuring a human sees a potential label even if the model isn't highly confident.

-----

### **6. Integration Guide: NLP Pipeline Flow**

The classification model is a critical component of our overall NLP pipeline. The standard flow for a call center interaction is as follows:

1.  **Audio Ingestion**: Raw audio from the call is captured and streamed to the transcription service.
2.  **ASR (Automatic Speech Recognition)**: The audio is converted into a text transcript in real time using Finetuned Whisper ASR model.
3.  **Real-Time Analytics**:
      * The transcript is fed to the **DistilBERT Classification Model**.
      * The model returns labels and confidence scores.

### **7. Fine-Tuning**

This section provides comprehensive documentation for the fine-tuning process of the DistilBERT multi-label classification model, including the continuous learning framework and automated version control system.

-----

#### **7.1. Architecture & Model Configuration**

The fine-tuning module implements a **multi-task learning approach** using a custom `MultiTaskDistilBert` class that extends the base DistilBERT architecture:

**Model Structure:**
- **Base Model**: DistilBERT-base-uncased (6 layers, 768 hidden units)
- **Pre-classifier**: Linear layer (768 → 768) with ReLU activation
- **Classification Heads**: Four separate linear classifiers for each task:
  - Main Category: 768 → 7 classes
  - Sub Category: 768 → 50+ classes
  - Intervention: 768 → 4 classes  
  - Priority: 768 → 3 classes
- **Loss Function**: Combined Cross-Entropy loss across all tasks
- **Dropout**: Configurable dropout layer for regularization

**Training Configuration:**
```python
TrainingArguments(
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=12,
    weight_decay=0.01,
    eval_strategy="epoch",
    metric_for_best_model="eval_avg_acc"
)
```

-----

#### **7.2. Data Processing Pipeline**

**Dataset Preparation:**
- **Input Format**: JSON files containing call transcripts with multi-label annotations
- **Train/Test Split**: 90/10 stratified split based on sub-category distribution
- **Text Processing**: Raw transcripts are tokenized using DistilBERT tokenizer with:
  - Maximum sequence length: 512 tokens
  - Padding: "max_length"
  - Truncation: Enabled

**Label Mapping System:**
The fine-tuning process includes a hierarchical label mapping that connects sub-categories to main categories:
```python
# Example mapping structure
sub_to_main_mapping = {
    "Bullying": "Advice and Counselling",
    "Child Labor": "VANE",
    "Malnutrition": "Nutrition",
    # ... additional mappings
}
```

-----

#### **7.3. Continuous Learning & Version Control**

The fine-tuning module implements an **automated continuous learning system** with intelligent version management:

**Version Control Features:**
- **Automatic Model Versioning**: Each improved model is saved as a new version (v1, v2, v3, etc.)
- **Performance-Based Saving**: New models are only saved if they outperform the previous best model
- **Metadata Tracking**: Complete training history with timestamps, metrics, and model paths
- **Rollback Capability**: Ability to load any previous model version for comparison or deployment

**Continuous Learning Workflow:**
1. **Model Discovery**: System checks for existing best model in version directory
2. **Warm Start**: If found, loads previous best model for continued training
3. **Training**: Fine-tunes on new data using MultiTaskTrainer
4. **Evaluation**: Compares performance against previous best model
5. **Conditional Saving**: Only saves if `eval_avg_acc` improves
6. **Metadata Update**: Records training session details and performance metrics

**Directory Structure:**
```
/multitask_distilbert_version/
├── model_metadata.json
├── CHS_tz_classifier_distilbert1/
├── CHS_tz_classifier_distilbert2/
└── CHS_tz_classifier_distilbert3/
```

-----

#### **7.4. Performance Monitoring**

**Evaluation Metrics:**
The system tracks comprehensive metrics across all classification tasks:

- **Task-Specific Metrics**: Accuracy, Precision, Recall, F1-score for each task
- **Overall Performance**: Weighted averages across all tasks
- **Primary Metric**: `eval_avg_acc` (average accuracy across all tasks) used for model selection

**MLflow Integration:**
- **Experiment Tracking**: All training runs logged to MLflow server
- **Parameter Logging**: Hyperparameters, model architecture details
- **Metric Tracking**: Real-time performance monitoring during training
- **Model Registry**: Integration ready for model lifecycle management

-----

#### **7.5. Embeddings Generation**

The fine-tuning process includes **category embedding generation** for enhanced semantic understanding:

**Features:**
- **Category Embeddings**: Pre-computed embeddings for all category names
- **Semantic Similarity**: Enable similarity-based classification and error analysis
- **Storage Format**: NumPy arrays saved for efficient loading during inference
- **Generated Files**:
  - `embeddings/main_cat_embeddings.npy`
  - `embeddings/sub_cat_embeddings.npy`
  - Category mapping JSON files

-----

#### **7.6. Usage Instructions**

**Prerequisites:**
- CUDA-compatible GPU (recommended)
- Python 3.8+ with required dependencies
- MLflow tracking server (optional)
- Sufficient disk space for model versions

**Running Fine-Tuning:**
```bash
# Set environment variables (optional)
export CUDA_VISIBLE_DEVICES=0

# Run fine-tuning script
python fine_tune_distilbert.py
```

**Configuration Options:**
- **Data Path**: Update `df = pd.read_json()` line with your dataset path
- **MLflow URI**: Modify `mlflow.set_tracking_uri()` for your tracking server
- **Model Directory**: Change `model_output_dir` for different storage location
- **Training Arguments**: Adjust hyperparameters in `TrainingArguments`

-----

#### **7.7. Best Practices & Recommendations**

**Training Optimization:**
- **Batch Size**: Start with 16, adjust based on GPU memory (8GB+ recommended)
- **Learning Rate**: 2e-5 works well; consider 1e-5 for stable models, 5e-5 for aggressive fine-tuning
- **Epochs**: 12 epochs typically sufficient; monitor for overfitting beyond 15
- **Early Stopping**: Enabled via `load_best_model_at_end=True`

**Data Quality:**
- **Balanced Dataset**: Ensure adequate representation across all categories
- **Clean Annotations**: Verify multi-label annotations are consistent
- **Regular Updates**: Retrain periodically with new call center data

**Production Deployment:**
- **Model Selection**: Always use the latest version from metadata file
- **A/B Testing**: Compare new model versions against current production model
- **Rollback Plan**: Keep previous model versions for quick rollback if needed
- **Monitoring**: Continuously monitor model performance in production

**Troubleshooting:**
- **Memory Issues**: Reduce batch size or sequence length
- **Performance Degradation**: Check data quality and class imbalance
- **Version Loading Errors**: Verify model directory structure and metadata file
- If the classifier model is not loaded, the API will return a `503 Service Unavailable` error. If the request is invalid, the API will return a `400 Bad Request` error.

-----




