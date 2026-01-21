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
The **cls-gbv-distilbert-v1** classifier model is a multi-task DistilBERT-based model fine-tuned for **Gender-Based Violence (GBV) case classification** in the context of child helpline services. This model is specifically trained on conversations from the **116 Child Helpline in Tanzania**, making it domain-specific for sensitive topics including abuse, violence, emergency situations, and child welfare cases.

### Key Features
- **Architecture:** Multi-task DistilBERT with custom classification heads
- **Domain:** Child helpline GBV case classification
- **Deployment:** Available via AI Service API and Hugging Face Hub
- **Repository:** openchs/cls-gbv-distilbert-v1
- **Special Capabilities:** Multi-task classification, confidence-weighted aggregation, priority escalation, automatic chunking for long narratives

### Classification Tasks

The model performs four simultaneous classification tasks:

1. **Main Category:** Primary case type classification
2. **Sub Category:** Detailed case sub-classification
3. **Intervention:** Recommended intervention type
4. **Priority:** Case urgency level (low, medium, high, urgent)

### Integration in AI Service Pipeline

The classification model is a critical component of the BITZ AI Service pipeline:

```
Audio Input → Transcription → Translation → English Text → Classification Model → Categories + Priority
                                                                ↓
                                                          NER/Summarization/QA
```

The model receives English translations (from the translation model or Whisper) and outputs structured classification results with confidence scores for downstream decision-making, agent notifications, and case management.

---

## 2. Integration in AI Service Architecture

The classification model is deeply integrated into the AI service through multiple layers:

### 2.1. Configuration Layer

The classification model is configured through the central settings system:

```python
class Settings(BaseSettings):
    # Hugging Face configuration
    classifier_hf_repo_id: str = "openchs/cls-gbv-distilbert-v1"
    hf_classifier_model: str = "openchs/cls-gbv-distilbert-v1"
    use_hf_models: bool = True
    models_path: str = "./models"  # Auto-adjusted for Docker
```

The system automatically detects whether it's running in Docker or local development and adjusts paths accordingly.

### 2.2. Model Architecture

**Custom Multi-Task DistilBERT:**

The model uses a shared DistilBERT base with four separate classification heads:

```python
class MultiTaskDistilBert(DistilBertPreTrainedModel):
    def __init__(self, config, num_main, num_sub, num_interv, num_priority):
        super().__init__(config)
        self.distilbert = DistilBertModel(config)
        self.pre_classifier = nn.Linear(config.dim, config.dim)
        
        # Four separate classification heads
        self.classifier_main = nn.Linear(config.dim, num_main)
        self.classifier_sub = nn.Linear(config.dim, num_sub)
        self.classifier_interv = nn.Linear(config.dim, num_interv)
        self.classifier_priority = nn.Linear(config.dim, num_priority)
```

**Category Configuration:**

The model loads category definitions from JSON files (main_categories.json, sub_categories.json, interventions.json, priorities.json) either from local storage or HuggingFace Hub.

### 2.3. Model Loading and Initialization

The model is loaded during FastAPI startup:

```python
class ClassifierModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = 256  # Model's maximum token limit
        self.hf_repo_id = "openchs/cls-gbv-distilbert-v1"
        
    def load(self) -> bool:
        """Load tokenizer, model weights, and category configs"""
        # Load category configs first
        self._load_category_configs()
        
        # Load model from Hugging Face Hub
        self.tokenizer = AutoTokenizer.from_pretrained(self.hf_repo_id)
        self.model = MultiTaskDistilBert.from_pretrained(
            self.hf_repo_id,
            num_main=len(self.main_categories),
            num_sub=len(self.sub_categories),
            num_interv=len(self.interventions),
            num_priority=len(self.priorities)
        )
        self.model.to(self.device)
        self.model.eval()
```

### 2.4. API Endpoints Layer

**Classification Endpoint:**

```python
@router.post("/classify", response_model=ClassifierResponse)
async def classify_narrative(request: ClassifierRequest):
    """Classify case narrative with automatic chunking"""
    
    # Check model readiness
    if not model_loader.is_model_ready("classifier_model"):
        raise HTTPException(status_code=503)
    
    # Get classifier and initialize chunker
    classifier = model_loader.models.get("classifier_model")
    chunker = ClassificationChunker(
        tokenizer_name="distilbert-base-uncased",
        max_tokens=256,        # aligned with model max_length
        overlap_tokens=150
    )
    
    # Check if chunking is needed
    token_count = chunker.count_tokens(request.narrative)
    
    if token_count <= 256:
        # Direct classification
        classification = classifier.classify(request.narrative)
    else:
        # Chunk, classify each chunk, then aggregate
        chunks = chunker.chunk_transcript(request.narrative)
        chunk_predictions = [classifier.classify(c['text']) for c in chunks]
        classification = aggregator.aggregate_case_classification(chunk_predictions)
```

**Other Endpoints:**
- `GET /classifier/info` - Get classifier model information
- `POST /classifier/demo` - Demo with sample narrative

### 2.5. Classification Chunking Strategy

**Why Chunking is Needed:**
- DistilBERT models have a maximum context length of 256 tokens
- Long helpline case narratives often exceed this limit
- Direct truncation would lose critical information
- Chunking with overlap preserves context across segments

**Key Implementation:**

```python
class ClassificationChunker:
    def chunk_transcript(self, text: str) -> List[Dict]:
        """Create overlapping chunks from text"""
        sentences = self._split_sentences(text)
        chunks = []
        
        for sentence in sentences:
            # Add sentence to current chunk
            # If chunk exceeds max_tokens, save it and start new chunk
            # Include overlap from previous chunk
            
        return chunks  # Each with metadata: text, token_count, position_ratio
```

The 150-token overlap ensures context preservation across segment boundaries.

### 2.6. Classification Aggregation Strategy

For multi-chunk classifications, the system uses **confidence-weighted voting**:

```python
class ClassificationAggregator:
    def aggregate_case_classification(self, chunk_predictions: List[Dict]) -> Dict:
        """Aggregate using confidence-weighted voting"""
        
        # Weight each prediction by its confidence score
        for pred in chunk_predictions:
            weight = pred['confidence_scores']['main_category']
            main_votes[pred['main_category']] += weight
            sub_votes[pred['sub_category']] += weight
            # ... same for intervention and priority
        
        # Get most voted predictions
        final_main = main_votes.most_common(1)[0][0]
        final_sub = sub_votes.most_common(1)[0][0]
        # ...
        
        # Apply priority escalation
        if 'urgent' in priorities_seen:
            final_priority = 'urgent'
        elif 'high' in priorities_seen:
            final_priority = 'high'
```

**Key Features:**
1. **Confidence-Weighted Voting:** High-confidence chunks have more influence
2. **Priority Escalation:** Any "urgent" chunk escalates the entire classification
3. **Independent Task Aggregation:** Each of the 4 tasks aggregated separately

### 2.7. Health Monitoring

The classification model integrates with the health monitoring system at `/health/models`.

**Model Readiness States:**
- **Ready:** Model loaded and available for classification
- **Implementable:** Model can be loaded but not yet initialized
- **Blocked:** Missing dependencies preventing model loading

### 2.8. Pipeline Integration

The classification model integrates into two processing modes:

#### Real-time Processing
For live calls, classification works progressively on text windows as they arrive. High/urgent priority classifications trigger immediate agent notifications.

#### Post-call Processing
For completed calls, full pipeline execution with chunked classification if needed:
```
Audio → Transcription → Translation → Classification → Priority Routing → NER/QA/Summarization
```

### 2.9. Memory Management

The classification model implements automatic GPU memory cleanup after each request and every 5 chunks during long classifications to prevent memory issues.

---

## 3. Using the Model

### 3.1. Via AI Service API (Production Use)

The classification model is deployed as part of the AI Service and accessible via REST API. The current implementation exposes a synchronous endpoint for on-demand inference. The route performs automatic chunking and aggregation when needed and returns the final classification result in a single response. Errors and readiness checks are returned with standard HTTP status codes.

#### Endpoint (synchronous)

```
POST /classifier/classify
```

#### Request

Headers:

```
Content-Type: application/json
```

Body:

```json
{
  "narrative": "string"
}
```

- `narrative` (required, string): The case narrative text to be classified

#### Success Response (HTTP 200 OK)

```json
{
  "main_category": "sexual_abuse",
  "sub_category": "child_sexual_abuse",
  "intervention": "emergency_response",
  "priority": "urgent",
  "confidence_scores": {
    "main_category": 0.96,
    "sub_category": 0.93,
    "intervention": 0.95,
    "priority": 0.97
  },
  "chunks_processed": 1,
  "processing_time": 0.52,
  "model_info": {
    "model_path": "/app/models/classifier",
    "loaded": true,
    "device": "cpu"
  },
  "timestamp": "2025-10-17T10:30:45Z"
}
```

#### Errors / Status Codes
- 400 Bad Request — invalid input (e.g. empty `narrative`)
- 503 Service Unavailable — model not loaded or not ready
- 500 Internal Server Error — unexpected server error during classification

#### Other endpoints
- `GET /classifier/info` — returns model status and metadata
- `POST /classifier/demo` — returns classification for a pre-configured sample narrative

#### cURL examples (synchronous)

Submit classification request:

```bash
curl -sS -X POST "http://<your-host>:8125/classifier/classify" \
  -H "Content-Type: application/json" \
  -d '{"narrative":"A 16-year-old girl called to report sexual abuse by her stepfather. Immediate intervention needed."}'
```

Get model info:

```bash
curl -sS http://<your-host>:8125/classifier/info
```

Run demo endpoint:

```bash
curl -sS -X POST http://<your-host>:8125/classifier/demo -H "Content-Type: application/json" -d '{}'
```

#### Python client example (synchronous)

```python
import requests

def classify(base_url: str, narrative: str, timeout: int = 30):
    resp = requests.post(
        f"{base_url.rstrip('/')}/classifier/classify",
        json={"narrative": narrative},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()

# Usage
result = classify("http://your-host:8125", "A child reported abuse and needs urgent help.")
print(result)
```

#### **4.2. Input Text Processing**

The Classify function expects a raw, clean transcript string. The model's serving pipeline handles all necessary preprocessing steps, including:

  * **Normalization**: Converting all text to lowercase and removing irrelevant characters.
  * **Tokenization**: Segmenting the text into tokens using the DistilBERT tokenizer, which handles sub-word units and special characters.

-----

### **5. Confidence Thresholds**

The confidence score returned for each prediction is a probability value (0 to 1) indicating the model's certainty. The choice of threshold is a business decision that should be tuned based on the application's risk tolerance.

  * **High Thresholds (e.g., \> 0.90)**: Recommended for **critical, automated actions** like case escalation. This ensures high precision and minimizes false positives, but may result in lower recall (i.e., missing some relevant cases).
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
#### Example cURL Request

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




curl -X POST "https://your-api-domain.com/classifier/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "A 16-year-old girl called to report sexual abuse by her stepfather. She is pregnant and being threatened. Immediate intervention needed."
  }'
```

#### Additional Endpoints

**Get Classifier Info:**
```
GET /classifier/info
```

Returns model status, configuration, and category counts.

**Demo Endpoint:**
```
POST /classifier/demo
```
Returns classification for a pre-configured sample narrative.

#### Features
- **Automatic Chunking:** Long narratives handled automatically with 150-token overlap
- **Confidence-Weighted Aggregation:** Multiple chunk predictions combined intelligently
- **Priority Escalation:** Automatic escalation for high/urgent cases
- **GPU Memory Management:** Automatic cleanup between requests

---

### 3.2. Via Hugging Face Hub

The model is publicly available on Hugging Face for direct inference and fine-tuning.

#### Model Repository
- **Organization:** [openchs](https://huggingface.co/openchs)
- **Model:** [openchs/cls-gbv-distilbert-v1](https://huggingface.co/openchs/cls-gbv-distilbert-v1)

#### Installation

```bash
pip install transformers torch
```

#### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer
model_name = "openchs/cls-gbv-distilbert-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Prepare input
narrative = "A 16-year-old girl called to report sexual abuse..."
inputs = tokenizer(narrative, return_tensors="pt", truncation=True, max_length=256)

# Get predictions
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=1)
    confidences = torch.softmax(outputs.logits, dim=1)

print(f"Category: {predictions[0].item()}, Confidence: {confidences[0].max():.3f}")
```

**Note:** When using the model directly from Hugging Face, you'll need to:
- Load the category configuration files separately (main_categories.json, etc.)
- Implement your own chunking logic for narratives longer than 256 tokens
- Handle multi-task output parsing (4 separate classification heads)

The AI Service API handles all of this automatically.

---

## 4. Production Considerations

### Token Limits
- **Maximum Input Length:** 256 tokens per chunk
- **Recommended Chunk Size:** 200-250 tokens for optimal performance
- **Chunk Overlap:** 150 tokens between segments

### Processing Time
- **Short narratives (< 100 tokens):** ~0.3-0.5 seconds
- **Medium narratives (100-250 tokens):** ~0.5-1.0 seconds
- **Long narratives (> 250 tokens):** ~1.0-3.0 seconds (with chunking)

Times vary based on GPU availability, narrative complexity, and system load.

### Automatic Chunking
The API automatically handles long narratives through:
1. Token counting and limit checking
2. Sentence-based segmentation with overlap
3. Independent chunk classification
4. Confidence-weighted aggregation

### Confidence Scores

- **High Confidence (> 0.85):** Reliable classification, safe for automated routing
- **Medium Confidence (0.60-0.85):** Good classification, consider human review for critical cases
- **Low Confidence (< 0.60):** Manual review recommended

### Priority Escalation

Automatic escalation occurs when:
- Any chunk predicts "urgent" priority
- Multiple chunks predict "high" priority
- Main category indicates emergency situation

### Error Handling

**Common errors:**
- Empty narrative (400 error)
- Model not ready (503 error)
- Service unavailable (500 error)

Check `/health/models` endpoint for model status.

---

## 5. Model Limitations

### Domain Specificity
- **Optimized for:** GBV cases, child abuse, emergency situations in helpline context
- **May require adaptation for:** General case management, non-GBV cases, different cultural contexts
- **Performance varies on:** Out-of-distribution data, highly specialized case types

### Technical Constraints
- **Maximum Context:** 256 tokens per chunk (handled automatically via chunking)
- **Memory Requirements:** GPU recommended for production (CPU fallback available)
- **Processing Speed:** Dependent on hardware and narrative length

### Known Considerations
- **Multi-Task Learning:** Individual task performance may vary
- **Long Narratives:** Chunking may occasionally affect classification consistency
- **Cultural Context:** Trained on Tanzanian helpline data; may need calibration for other regions
- **Priority Escalation:** May over-escalate in ambiguous cases (by design for safety)

### Recommendations
- Monitor classification accuracy for edge cases
- Implement human-in-the-loop review for high-stakes decisions
- Use confidence scores to route low-confidence cases for manual review
- Consider fine-tuning for specific organizational needs
- Regularly evaluate priority escalation rules

---

## 6. Classification Categories

### Main Categories (12)
Sexual Abuse, Physical Abuse, Emotional Abuse, Neglect, General Inquiry, Emergency, Child Protection Concern, Family Issues, Educational Issues, Health Issues, Economic Issues, Other

### Sub-Categories (48)
Multiple detailed sub-categories under each main category for granular case classification.

### Intervention Types (8)
Emergency Response, Immediate Assessment, Standard Assessment, Counseling Support, Referral to Services, Information Provision, Follow-up Required, Case Monitoring

### Priority Levels (4)
- **Urgent:** Immediate life-threatening situation
- **High:** Serious case requiring rapid response
- **Medium:** Standard case requiring timely response
- **Low:** General inquiry or information request

---

## 7. Citation

```bibtex
@misc{cls_gbv_distilbert_v1,
  title={cls-gbv-distilbert-v1: Multi-task Classification for GBV Cases},
  author={OpenCHS Team},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/openchs/cls-gbv-distilbert-v1}
}
```

---

## 8. Support and Contact

### Issues and Questions
- **Email:** info@bitz-itc.com
- **Hugging Face:** [openchs organization](https://huggingface.co/openchs)

### Contributing
For dataset contributions, model improvements, or bug reports, contact the BITZ AI Team at info@bitz-itc.com.

---

## 9. License

This model is released under the **Apache 2.0 License**, allowing for both commercial and non-commercial use with proper attribution.

---
