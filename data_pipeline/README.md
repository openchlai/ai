# Data Pre-Processing Pipeline

## Project Overview

This pipeline is designed to process voice data and generate meaningful case predictions using open-source AI models. The core functionalities include:

1. **Voice Recognition & Transcription** – Convert voice recordings into text
2. **Translation Pipeline** – Translate transcribed text into English
3. **NLP-Based Case Prediction** – Apply AI models to classify and predict case outcomes
4. **Workflow Automation** – Manage tasks using orchestration tools
5. **Data Storage & Visualization** – Store and display processed data for insights

The entire system relies only on open-source tools and models, which will be fine-tuned for domain-specific applications.

## Pipeline Architecture

| Component | Description | Open-Source Tools Used |
|-----------|-------------|------------------------|
| Data Sources | Voice & text data from helplines & historical records | Mozilla Common Voices, Helpline Data, SALT dataset |
| Data Storage | Store raw audio, transcriptions, translations, and case data | On-premise Storage (Object Storage), PostgreSQL, MySQL |
| Speech-to-Text | Convert speech into text | OpenAI Whisper, Meta's Wav2Vec |
| Translation | Convert transcribed text into English | NLLB, OpenAI Whisper |
| NLP Processing | Text cleaning, feature extraction, and structuring | SpaCy, FastText, Hugging Face Transformers |
| Case Prediction | Train models to classify case types and severity | BERT, DistilBERT, XLM-R, PyTorch, Scikit-learn |
| Data Visualization | Generate reports and insights | Custom in-house tool |
| API & Model Serving | Deploy models and expose endpoints | Django |
| Workflow Orchestration | Automate and schedule tasks | Celery |

## End-to-End Pipeline Workflow

### Step 1: Data Ingestion (Raw Data Collection & Storage)

#### Voice Data Collection
- **Sources:**
  - Call center recordings from telephony systems (WAV, MP3)
  - Mobile app-recorded messages
  - Uploaded voice files (manual inputs from helpline operators)
- **Storage:**
  - Save audio files in On-Premise Storage with metadata (file ID, timestamp, speaker, duration)

#### Text Data Collection
- **Sources:**
  - Historical case records (CSV, JSON, database tables)
  - Transcriptions of audio by people
  - Transcriptions of audio made by STT models
- **Storage:**
  - Store in PostgreSQL/SQLite, making it available for model training

### Step 2: Voice Recognition & Transcription

This step focuses on converting audio into text while ensuring data quality, accuracy, and efficiency.

#### Transcription Models (Open Source)

| Model | Description | Best Use Case |
|-------|-------------|---------------|
| OpenAI Whisper | High accuracy, multi-language support | General-purpose transcription |
| Wav2Vec | Learns speech representations from unlabeled audio | Strong performance with limited training data |
| Vosk | Lightweight, offline ASR | Real-time processing, low latency |
| Kaldi | Highly customizable, used for ASR research | Large-scale transcription |

- **Primary model:** Whisper (fine-tuned for dialects and accents)
- **Fallback models:** Vosk/Kaldi (for low-resource or offline cases)

#### Audio Preprocessing Steps
1. Load Raw Audio Data
   - Retrieve audio from object storage
   - Extract metadata (caller ID, timestamp, region)
2. Remove Silences & Background Noise
   - Voice Activity Detection (VAD) removes long silent pauses
   - Noise reduction filters out background sounds
   - Tools: SoX, ffmpeg, WebRTC VAD, PyDub
3. Detect & Handle Speaker Diarization
   - Use PyAnnote to separate speakers
4. Normalize & Convert to Standard Format
   - Convert all audio to 16 kHz WAV (standard for ASR)
   - Normalize volume levels to prevent distortion
5. Break Audio into Small Chunks
   - Long recordings are split into smaller segments (5–10 seconds per chunk)
   - Reduces memory usage and latency in model processing

#### Speech-to-Text Conversion Process
1. Load Preprocessed Audio Chunks
   - Each chunk is fed into the Whisper/Wav2Vec/Vosk/Kaldi model
   - Process in parallel to speed up transcription
2. Convert Speech to Text
   - Each model generates a text output + confidence score
   - If confidence is below threshold (e.g., 80%), reprocess with another model
3. Reconstruct Full Transcription
   - If audio was chunked, merge back into full text
   - Ensure proper sentence breaks (punctuation, speaker identification)
4. Store Transcription Results
   - Transcribed text saved in PostgreSQL
   - Metadata stored (file ID, timestamp, language detected, confidence score)
   - Backup stored in object storage for future reference

#### Quality Evaluation & Error Handling
- **Confidence Score Evaluation:**
  - Each transcription has a confidence score (0–100%)
  - If below 80%, transcription is flagged for review or reprocessing
- **Automated Quality Checks:**
  - Word Error Rate (WER) → Measures transcription accuracy by comparing with a reference transcript
  - Text Coherence Check → Uses NLP to detect gibberish text or incomplete sentences
  - Speaker Identification Consistency → Ensures speaker labels remain consistent throughout
- **Manual Review for Edge Cases:**
  - If transcription is incoherent, send to human reviewers for correction
  - Flagged cases stored in "Low Confidence Queue" for analysis

#### Real-Time vs. Batch Processing

| Mode | Description | Use Case |
|------|-------------|----------|
| Batch Mode | Processes pre-recorded audio files in bulk | Helpline recordings, historical data |
| Streaming Mode | Converts live audio streams into text | Real-time transcription for helpline calls |

### Step 3: Translation Pipeline (Native-to-English Conversion)

Once audio has been transcribed into text, the next step is to detect the language and, if necessary, translate it into English.

#### Language Detection
- **Models Used:**
  - FastText (pre-trained for 170+ languages, fast inference)
  - LangID.py (machine learning-based classifier, accurate)
  - CLD2/CLD3 (Google's Compact Language Detector)
- **Process:**
  1. Receive transcribed text from Step 2
  2. Detect the language using FastText
  3. If English, skip translation; if not English, send text for translation
  4. Store detected language in PostgreSQL

#### Text Translation
- **Models Used:**
  - NLLB (Supports numerous African languages)
  - OpenAI Whisper (supports text translation and text transcription tasks on a number of languages)
  - Fairseq (Facebook's AI model for multilingual tasks)
- **Process:**
  1. Receive transcribed text
  2. Identify source language (from previous step)
  3. Translate text into English using NLLB/OpenAI Whisper
  4. Store results (original text, translated text, confidence score)
  5. Perform quality evaluation (BLEU Score, METEOR, ROUGE metrics)

#### Handling Translation Errors
- **Automated Quality Checks:**
  - Confidence Score Thresholds (< 75% = "Needs Review", > 90% = "Approved")
  - Back-Translation Check (translate English → Native Language → English)
  - Parallel Corpus Matching (compare against existing human-translated cases)

### Step 4: NLP-Based Data Preprocessing

Following transcription and translation, the text undergoes preprocessing to prepare it for machine learning tasks, such as case prediction.

📜 **[Pre-Processing Pipeline for Helpline & Legal Case Data](nlp/README.md)** –  Details the text preprocessing steps and methodologies.

#### Data Cleaning
- **Tools Used:** SpaCy, NLTK, FastText, Regex
- **Steps:**
  1. Load Text Data (retrieve translated text from PostgreSQL)
  2. Lowercasing (convert all text to lowercase for uniformity)
  3. Remove Punctuation & Special Characters
  4. Stop Word Removal (remove common, non-informative words)
  5. Tokenization (break text into individual words)
  6. Stemming & Lemmatization (convert words to root forms)
  7. Detect & Remove Non-Language Text
  8. Store Cleaned Text

#### Feature Engineering
- **Named Entity Recognition (NER):**
  - Identify key entities (people, locations, organizations)
  - Tool: HugginFace/SpaCy (pre-trained models + custom fine-tuning)
  - Example: "A worker was mistreated by XYZ Company in Nairobi" → {"ORG": "XYZ Company", "LOC": "Nairobi"}

- **Sentiment Analysis:**
  - Determine urgency & severity of a case
  - Tool: Pre-trained BERT model (fine-tuned on case-specific data)
  - Classifies: Positive (resolved), Neutral (needs attention), Negative (critical/urgent)

- **Vectorization (Text-to-Numeric Representation):**

| Method | Description | Best Use Case |
|--------|-------------|---------------|
| TF-IDF | Measures importance of words in a document | Traditional ML models |
| Word2Vec | Learns word relationships | Deep learning |
| FastText | Handles out-of-vocabulary words | Case-specific embeddings |

### Step 5: Case Prediction (Machine Learning Pipeline)

This step involves training, evaluating, and deploying a machine learning model to predict case outcomes based on processed text.

#### Model Training
- **Data Preparation:**
  - Text Features: Complaint descriptions, NER entities
  - Numerical Features: Sentiment score, urgency level, case type
  - Splitting: Training (80%), Validation (10%), Test (10%)

- **Machine Learning Models:**

| Model | Description | Use Case |
|-------|-------------|----------|
| BERT (Fine-tuned) | Transformer-based NLP model | Text classification |
| DistilBERT | Lightweight version of BERT | Faster inference |
| XLM-R | Multilingual transformer model | Handling multiple languages |
| Random Forest | Traditional ML model | Handling structured features |
| XGBoost | Boosted tree-based model | High-performance structured data classification |

- **Training Process:**
  1. Prepare training data (convert text to numerical format)
  2. Train transformer models (fine-tune pre-trained models)
  3. Train traditional models on structured features
  4. Evaluate performance (accuracy, precision, recall, F1-score)

#### Model Deployment
- **Inference API:**
  - Tool Used: FastAPI (lightweight & high-performance)
  - Deployment: Docker container / Kubernetes for scaling
- **Inference Process:**
  1. API receives a translated case report
  2. NLP model predicts case category (e.g., "Urgent", "Fraud", "Legal Assistance")
  3. Return JSON response with case classification & confidence score

#### Model Monitoring & Optimization
- **Performance Tracking:**
  - Log predictions & actual outcomes
  - Use TensorBoard to monitor training loss & accuracy
- **Retraining Strategy:**
  - If model performance degrades, retrain with latest cases
  - Automate retraining pipeline using Apache Airflow
- **Error Analysis:**
  - Identify misclassified cases and fine-tune models
  - Adjust training weights based on false positives/negatives

### Step 6: Reporting & Visualization

The reporting module provides real-time monitoring, analytics, and insights into case distributions, model performance, and translation accuracy.

#### Dashboard & Metrics
- **Tools Used:** Vue 3 + Chart.js/Recharts.js, Metabase / Apache Superset, Celery, PostgreSQL
- **Insights Generated:**
  - Case Distribution Dashboard (number of cases by category)
  - Model Performance Dashboard (accuracy, precision, recall trends)
  - Translation Accuracy Dashboard (correct vs. incorrect translations)
  - Sentiment & Urgency Analysis Dashboard
  - Anomaly & Alert Dashboard

#### Real-Time Data Pipeline for Reporting
- Celery Workers fetch data from storage
- Processing & aggregation via scheduled batch jobs
- Dashboard updates in real-time using API calls
- Vue 3 frontend displays visualizations

#### User Roles & Access Control
- Role-Based Access Control (RBAC) with JWT Tokens
- Different dashboard views for case managers, AI trainers, translators, and admins

#### Alert & Notification System
- Automated alerts via Celery for fraud spikes, low model accuracy, etc.
- Integration with WhatsApp API for instant notifications

## Scalability & Optimization

### Performance Enhancements
- **Parallel Processing:** Celery Workers distribute tasks across multiple nodes
- **Model Optimization:** ONNX Runtime, Parameter Efficient Finetuning (peft & LoRa), model pruning & quantization
- **Batch Processing:** Translate multiple texts at once to optimize API calls
- **Processing Modes:** Streaming for high-priority cases, Batch Mode for non-urgent processing

## Monitoring & Alerts

### System Monitoring
- **Logging & Audit Trail:** Elastic Stack (ELK) logs each pipeline stage
- **Automated Alerts:** Triggers for failed transcriptions, high translation errors, model drift
- **Performance Metrics:** Real-time monitoring of latency, throughput, accuracy trends

## Summary

This fully open-source AI pipeline integrates:
1. Speech-to-Text (Whisper, Vosk, Kaldi)
2. Translation (NLLB, Whisper)
3. Case Prediction (BERT, PyTorch, Hugging Face)
4. Automation (Celery for task orchestration)
5. Data Storage (PostgreSQL, MinIO, SQLite)
6. Reporting (Vue 3, Chart.js,Rechart.js, Metabase, Superset)
7. Monitoring (ELK Stack, Prometheus, Celery Alerts)

### Next Steps & Recommendations
1. Integrate Grafana for advanced system health monitoring
2. Fine-tune models with real-world case data to improve accuracy
3. Expand language support in the Translation Pipeline
