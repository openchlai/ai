# OpenCHS AI Datasets Documentation

This directory contains all datasets used for training and evaluating AI models in the OpenCHS (Open Child Helpline System) platform. All datasets are version-controlled using DVC (Data Version Control) and tagged in the repository for easy reference.

## 🔗 Dataset Repositories

**GitHub Repository:** [https://github.com/openchlai/ai](https://github.com/openchlai/ai)  
**Datasets Directory:** `ai_service/datasets/`  
**Hugging Face Organization:** [https://huggingface.co/openchs/datasets](https://huggingface.co/openchs/datasets)

All datasets are accessible under open licenses to support Digital Public Good (DPG) requirements and promote research in child protection AI systems.

---

## 📊 Dataset Overview

| Task | Dataset Count | Latest Version | Git Tag | Quality Control | Status |
|------|--------------|----------------|---------|-----------------|--------|
| ASR | 1 | v1.0.1 | `asr-label-studio-v1.0.1` | ✓ | Production |
| Classification | 4 | v005 | `clean_synthetic_generated_data_v005` | ✓ | Production |
| NER | 2 | v2 | - | ✓ | Production |
| QA Scoring | 3 | v1 | `qa_data_v1_classifier_scripts` | ✓ | Production |
| Summarization | 2 | v1.0 | `summarization-v1.0` | ✓ | Production |
| Translation | 7 | v1 | - | ✓ | Production |

---

## 🏷️ Version Tags

All major dataset versions are tagged in the repository for reproducibility:

| Tag | Date | Description | Link |
|-----|------|-------------|------|
| `qa_data_v1_classifier_scripts` | Sep 2, 2025 | QA scoring and classification scripts | [View Tag](https://github.com/openchlai/ai/releases/tag/qa_data_v1_classifier_scripts) |
| `asr-label-studio-v1.0.1` | Aug 28, 2025 | ASR Label Studio export v1.0.1 | [View Tag](https://github.com/openchlai/ai/releases/tag/asr-label-studio-v1.0.1) |
| `clean_synthetic_generated_data_v005` | Aug 27, 2025 | Cleaned synthetic classification data v005 | [View Tag](https://github.com/openchlai/ai/releases/tag/clean_synthetic_generated_data_v005) |
| `summarization-v1.0` | Aug 26, 2025 | Summarization dataset v1.0 | [View Tag](https://github.com/openchlai/ai/releases/tag/summarization-v1.0) |
| `asr-label-studio-v1.0` | Aug 26, 2025 | ASR Label Studio export v1.0 | [View Tag](https://github.com/openchlai/ai/releases/tag/asr-label-studio-v1.0) |

---

## 1. Automatic Speech Recognition (ASR)

### 📁 Directory: `asr/`

Speech recognition datasets for transcribing child helpline calls in multiple languages (English, Swahili, Luganda).

#### Datasets

| Dataset | Version | Git Tag | Date | Description | Links |
|---------|---------|---------|------|-------------|-------|
| ASR Dataset v1 | v1.0.1 | `asr-label-studio-v1.0.1` | 2025-08-28 | Multi-lingual speech corpus exported from Label Studio | [GitHub](https://github.com/openchlai/ai/releases/tag/asr-label-studio-v1.0.1) \| [Hugging Face](https://huggingface.co/datasets/openchs/asr-dataset-v1) |

**DVC Files:**
- `asr-dataset-v1-2025-07-14.dvc`

**Format:** Audio files (WAV/MP3) with JSON transcriptions  
**Languages:** English, Swahili, Luganda  
**Duration:** ~100 hours of labeled audio  
**Use Case:** Fine-tuning Whisper models for child helpline ASR  
**Annotation Tool:** Label Studio

**Documentation:** See [asr/README.md](./asr/README.md)

---

## 2. Call Classification

### 📁 Directory: `classification/`

Datasets for categorizing helpline calls into predefined case types (abuse, counseling, information, etc.).

#### Datasets

| Dataset | Version | Git Tag | Description | Links |
|---------|---------|---------|-------------|-------|
| Cleaned Synthetic Cases | v005 | `clean_synthetic_generated_data_v005` | Cleaned and validated synthetic classification data | [GitHub](https://github.com/openchlai/ai/releases/tag/clean_synthetic_generated_data_v005) \| [Hugging Face](https://huggingface.co/datasets/openchs/synthetic-cases-cleaned-v0005) |
| Augmented TZ Call Center Data | - | - | Augmented Tanzanian call center conversations | [Hugging Face](https://huggingface.co/datasets/openchs/tz-call-center-augmented) |
| Balanced Synthetic Cases | - | - | Balanced synthetic helpline cases for classification | [Hugging Face](https://huggingface.co/datasets/openchs/synthetic-cases-balanced) |
| Synthetic Helpline Classification | v1 | - | Primary classification training dataset | [Hugging Face](https://huggingface.co/datasets/openchs/helpline-classification-v1) |

**DVC Files:**
- `augmented_TZ_call_center_data.csv.dvc`
- `balanced_synthetic_cases_generated_data.json.dvc`
- `cleaned_synthetic_cases_generated_data_v0005.json.dvc`
- `synthetic_helpine_classification_v1.json.dvc`

**Format:** JSON/CSV with conversation text and labels  
**Labels:** Abuse, Neglect, Counseling, Information, Referral, Emergency, Other  
**Quality Control:**
- Classification profile report: `classification_profile.html`
- QC report: `classification_profile.qc_report.json`

**Documentation:** See [classification/README.MD](./classification/README.MD)

---

## 3. Named Entity Recognition (NER)

### 📁 Directory: `ner/`

Datasets for extracting key entities from helpline conversations (names, locations, dates, incident types).

#### Datasets

| Dataset | Version | Description | Links |
|---------|---------|-------------|-------|
| NER Synthetic Dataset | v1 | Initial synthetic NER annotations | [Hugging Face](https://huggingface.co/datasets/openchs/ner-synthetic-v1) |
| NER Synthetic Dataset | v2 | Enhanced NER dataset with improved entity coverage | [Hugging Face](https://huggingface.co/datasets/openchs/ner-synthetic-v2) |

**DVC Files:**
- `ner_synthetic_dataset_v1.jsonl.dvc`
- `ner_synthetic_dataset_v2.jsonl.dvc`

**Format:** JSONL with BIO/IOB2 tagging scheme  
**Entities:** PERSON, LOCATION, DATE, TIME, AGE, INCIDENT_TYPE, ORGANIZATION  
**Use Case:** Information extraction for case management automation

---

## 4. QA Scoring

### 📁 Directory: `qa-scoring/`

Datasets for evaluating conversation quality and counselor performance on helpline calls.

#### Datasets

| Dataset | Version | Git Tag | Description | Links |
|---------|---------|---------|-------------|-------|
| QA Score Data | v1 | `qa_data_v1_classifier_scripts` | Quality scoring dataset with classifier scripts | [GitHub](https://github.com/openchlai/ai/releases/tag/qa_data_v1_classifier_scripts) \| [Hugging Face](https://huggingface.co/datasets/openchs/qa-scoring-v01) |
| Synthetic Helpline QA Scoring | v1 | - | Synthetic conversations with quality scores | [Hugging Face](https://huggingface.co/datasets/openchs/qa-scoring-v1) |
| Synthetic Helpline QA Scoring | v2 | - | Enhanced QA scoring with additional metrics | [Hugging Face](https://huggingface.co/datasets/openchs/qa-scoring-v2) |

**DVC Files:**
- `qa_score_data_v01.json.dvc`
- `synthetic_helpline_qa_scoring_v1.json.dvc`
- `synthetic_helpline_qa_scoring_v2.json.dvc`

**Format:** JSON with conversation + quality score annotations  
**Metrics:** Empathy, Professionalism, Resolution, Safety, Overall Score  
**Quality Control:**
- Profile report: `synthetic_helpline_qa_scoring_v1_profile.html`
- QC report: `synthetic_helpline_qa_scoring_v1.qc_report.json`
- Failed validation cases: `synthetic_helpline_qa_scoring_v1_failed.csv`

**Documentation:** See [qa-scoring/README.MD](./qa-scoring/README.MD)

---

## 5. Summarization

### 📁 Directory: `summarization/`

Datasets for generating concise case summaries from helpline call transcripts.

#### Datasets

| Dataset | Version | Git Tag | Description | Links |
|---------|---------|---------|-------------|-------|
| Train Data v1 | v1.0 | `summarization-v1.0` | Production summarization training dataset | [GitHub](https://github.com/openchlai/ai/releases/tag/summarization-v1.0) \| [Hugging Face](https://huggingface.co/datasets/openchs/summarization-train-v1) |
| Train Data (legacy) | v1 | - | Initial summarization training data | [Hugging Face](https://huggingface.co/datasets/openchs/summarization-v1) |

**DVC Files:**
- `train_data.jsonl.dvc`
- `dataset_v1/train_data1.jsonl.dvc`

**Format:** JSONL with conversation and summary pairs  
**Summary Types:** Executive summary, case notes, action items  
**Quality Control:**
- Profile report: `summarization_profile.html`
- QC report: `train_data1_qc_report_qc_report.json`
- Failed cases: `summarization_failed.csv`

**Documentation:** See [summarization/dataset_v1/README.md](./summarization/dataset_v1/README.md)

---

## 6. Translation

### 📁 Directory: `translation/`

Parallel translation datasets for multi-lingual support (English ↔ Swahili ↔ Luganda).

#### Datasets

| Dataset | Version | Source | Description | Links |
|---------|---------|--------|-------------|-------|
| CCMatrix EN-SW | - | CCMatrix | English-Swahili parallel corpus | [Hugging Face](https://huggingface.co/datasets/openchs/ccmatrix-en-sw) |
| NLLB EN-SW | - | NLLB | English-Swahili from NLLB dataset | [Hugging Face](https://huggingface.co/datasets/openchs/nllb-en-sw) |
| Cleaned Dataset | - | Multiple | Cleaned and deduplicated translation pairs | [Hugging Face](https://huggingface.co/datasets/openchs/translation-cleaned) |
| EN-SW Second Dataset | - | CCMatrix | Additional English-Swahili pairs | [Hugging Face](https://huggingface.co/datasets/openchs/en-sw-second) |
| Luganda Parallel | - | Custom | English-Luganda parallel corpus | [Hugging Face](https://huggingface.co/datasets/openchs/luganda-parallel) |
| SW-EN Dataset | v1 | Multiple | Swahili-English production dataset | [Hugging Face](https://huggingface.co/datasets/openchs/sw-en-v1) |

**DVC Files:**
- `ccmatrix_dataset/en_sw_second_dataset.jsonl.dvc`
- `nllb_dataset/en_sw_dataset.jsonl.dvc`
- `cleaned_dataset.csv.dvc`
- `en_sw_second_dataset.jsonl.dvc`
- `luganda_parallel.jsonl.dvc`
- `sw_en_dataset_v1.jsonl.dvc`

**Format:** JSONL with source-target language pairs  
**Language Pairs:** English ↔ Swahili, English ↔ Luganda  
**Quality Control:**
- Luganda QC report: `luganda_parallel_qc_report_qc_report.json`
- Profile report: `translation_profile_luganda_parallel.html`
- Failed cases: `translation_failed_luganda_parallel.csv`

**Documentation:** See [translation/README.md](./translation/README.md)

---

## 🔧 Version Control with DVC

All datasets are tracked using [DVC (Data Version Control)](https://dvc.org/). The `.dvc` files in this repository contain pointers to the actual data stored in remote storage.

### Accessing Datasets

**Via Hugging Face (Recommended)**

Publicly shareable datasets are available on Hugging Face for easy access and use in training pipelines:

```bash
# Install Hugging Face datasets library
pip install datasets

# Load a dataset
from datasets import load_dataset
dataset = load_dataset("openchs/asr-dataset-v1")
```

**Via Git Tags (Version Reference)**

To reference specific dataset versions in the repository:

```bash
# Clone repository
git clone https://github.com/openchlai/ai.git
cd ai/ai_service/datasets

# Checkout specific version
git checkout asr-label-studio-v1.0.1
```

**Note:** DVC-tracked files require access to the remote storage. Publicly available datasets should be accessed via Hugging Face.

---

## 📋 Quality Control Process

All datasets undergo rigorous quality control:

1. **Automated Validation:** Schema validation, format checks, duplicate detection
2. **Statistical Profiling:** Distribution analysis, outlier detection
3. **Manual Review:** Sample-based human verification
4. **Inter-Annotator Agreement:** For labeled datasets (Kappa score > 0.75)
5. **Signed QC Logs:** All QC reports are reviewed and signed off

### QC Artifacts

- **Profile Reports (`.html`):** Statistical analysis and data profiling
- **QC Reports (`.qc_report.json`):** Automated quality check results
- **Failed Cases (`.failed.csv`):** Records that failed validation for review

---

## 📜 Licensing

All datasets are released under **Creative Commons Attribution 4.0 International (CC BY 4.0)** to comply with Digital Public Good requirements.

**Citation:**
```bibtex
@misc{openchs_datasets_2025,
  title={OpenCHS AI Datasets: Multi-lingual Child Helpline System Training Data},
  author={BITZ IT Consulting Ltd and UNICEF Venture Fund},
  year={2025},
  publisher={GitHub and Hugging Face},
  howpublished={\url{https://github.com/openchlai/ai}},
  note={Available at: https://huggingface.co/openchs/datasets}
}
```

---

## 🔄 Dataset Updates

Datasets are updated regularly based on:
- New data collection from partner helplines
- Feedback from model performance evaluation
- Data quality improvements and cleaning
- Privacy compliance reviews (ODPC, GDPR, KE-DECA)

All updates follow versioning scheme: `v{MAJOR}.{MINOR}.{PATCH}`

**Version tags** are created for each significant dataset release to ensure reproducibility.

---

## 📂 Repository Structure

```
ai_service/datasets/
├── DATASETS.md              # This file
├── asr/                     # Speech recognition datasets
├── classification/          # Call classification datasets
├── ner/                     # Named entity recognition datasets
├── qa-scoring/             # Quality assurance scoring datasets
├── summarization/          # Conversation summarization datasets
└── translation/            # Multi-lingual translation datasets
```

---

## 📞 Support

For dataset access issues, quality concerns, or collaboration inquiries:
- **GitHub Issues:** [openchs/ai/issues](https://github.com/openchlai/ai/issues)
- **GitHub Repository:** [openchs/ai](https://github.com/openchlai/ai)
- **Hugging Face:** [openchs/datasets](https://huggingface.co/openchs/datasets)
- **UNICEF Venture Fund:** [Contact Page](https://www.unicefinnovationfund.org/)

---

**Last Updated:** October 2025  
**Maintained by:** BITZ IT Consulting Ltd R&D Team  
**Project:** OpenCHS - Digital Public Good for Child Protection  
**Git Repository:** https://github.com/openchlai/ai