# Text Data Preprocessing and Normalization Pipeline

**Project:** [Your AI Project Name]  
**Last Updated:** [YYYY-MM-DD]  
**Months:** 4–5  

---

## 📌 Overview

This pipeline cleans, de-identifies, and normalizes structured/unstructured text data for downstream NLP tasks. Key features:

- **Cleaning:** Removes duplicates, noise, PII, and inconsistencies.  
- **Normalization:** Spelling correction, stemming, and standardization.  
- **Modular Components:** Reusable code for future pipelines.  
- **Documentation:** Step-by-step guides and benchmarks.  

---

## 🛠️ Deliverables

### 1. Cleaned Datasets

**Input:** Raw text (JSON/CSV/TXT)  
**Output:** Standardized, PII-free text, ready for analysis.  

#### Steps

1. **Remove duplicates** (`deduplicate.py`)  
2. **Filter noise** (HTML, special characters, non-UTF-8 text) using regex  
3. **Handle missing values** (impute or drop)  
4. **Standardize** whitespace and casing  
5. **Detect and redact PII** using rule-based + ML detection  

📌 **PII Types Detected:**

- Names, emails, phone numbers  
- National IDs, addresses  
- Location metadata and IPs  

🛡 **Tools Used:**

- `presidio` (Microsoft) for NLP-based entity recognition  
- Custom regex for structured formats (e.g. phone, email)

📂 **Outputs:**

| Deliverable         | Location/Format                    |
|---------------------|------------------------------------|
| Cleaned datasets    | `data/cleaned/` (CSV/Parquet)      |
| Cleaning logs       | `logs/preprocessing_logs.csv`      |
| PII redaction report| `logs/pii_redaction_[date].csv`    |

📄 **Sample Log Entry:**

```csv
timestamp,operation,affected_items
2024-05-01 14:30,removed_duplicates,1258
2024-05-01 14:32,redacted_pii,email: 142 | phone: 87 | names: 21
```

## 2. Text Normalization

### Techniques Applied

| Technique | Tool/Library | Example Transformation |
|-----------|-------------|------------------------|
| Spelling Correction | SymSpell | "recieve" → "receive" |
| Stemming | NLTK PorterStemmer | "running" → "run" |
| Contractions | Custom mapping | "don't" → "do not" |

### 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Spelling Accuracy | 92% (10k samples) |
| Stemming Speed | 1,500 docs/sec |
| Vocabulary Reduction (stemming) | 22% |

### 📂 Outputs

| Deliverable | Location/Format |
|-------------|----------------|
| Normalized datasets | data/normalized/ |
| Benchmarking results | benchmarks/normalization_results.md |

## 3. Reusable Components

Reusable code to support ongoing and future text processing pipelines.

```python
from preprocessing import TextCleaner, Normalizer

cleaner = TextCleaner(remove_html=True, fix_encoding=True, redact_pii=True)  
normalizer = Normalizer(spell_check=True, stemmer="porter")  

cleaned_text = cleaner.transform(raw_text)  
normalized_text = normalizer.transform(cleaned_text)  
```

### 📂 Outputs

| Deliverable | Location/Format |
|-------------|----------------|
| Codebase | src/preprocessing/ |
| Integration docs | docs/components_guide.md |

## 4. Pipeline Documentation

Step-by-step guides and notebooks for reproducibility.

### Workflow Steps

Data ingestion → Cleaning (incl. PII redaction) → Normalization → Export

### Logging and benchmarking

Optional: Mermaid diagrams for visualizing flow (to be added)

### Setup Guide

```bash
pip install -r requirements.txt
python run_pipeline.py --input_dir ./data/raw
```

### Troubleshooting

- Slow processing → Use --batch_size 1000
- Over-stemming → Switch to lemmatization
- PII missed → Add custom regex to pii_patterns.yaml

### 📂 Outputs

| Deliverable | Location/Format |
|-------------|----------------|
| Full documentation | docs/pipeline_documentation.md |
| Interactive demo | notebooks/pipeline_demo.ipynb |

### 🚧 Challenges and Resolutions

| Challenge | Resolution |
|-----------|------------|
| Noisy social media text | Added custom regex filters |
| Spelling false positives | Adjusted SymSpell edit distance |
| Incomplete PII detection | Integrated hybrid PII detection (rules + ML) |
