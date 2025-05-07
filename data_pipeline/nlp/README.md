# Text Pre-Processing Pipeline for Helpline & Legal Case Data

**Version 1.2** | *Modularized for Automation & Classification*

---

## Project Structure

```bash
.
├── Case_Category_Classification/           # Case classification resources
│   └── original_case_catagories_data/      # Raw narrative data files
├── benchmarks/                             # Evaluation metrics & test results
├── data/
│   ├── Cleaned/                            # Cleaned outputs (from textcleaner)
│   │   ├── Q2_Report.md
│   │   └── textcleaner.py
│   ├── normalized/                         # Normalized outputs (from text_normalizer)
│   ├── pipeline_controller.py              # Master pipeline script
│   ├── text_normalizer.py                  # Handles domain-specific normalization
│   └── textcleaner.py                      # Cleans raw helpline narratives
├── logs/                                   # Runtime logs for audit & debugging
├── stopwords-sw.json                       # Swahili stopwords
└── synthetic_data/                         # Synthetic data generation tools
```

## 1. Objectives

- Automate cleaning and normalization of helpline call text data
- Preserve critical information (e.g., abuse types, event descriptions)
- Prepare data for case classification using Kenya's Children Act taxonomy

## 2. Modular Pipeline Overview

### 🧠 Stage 0: Pipeline Controller (pipeline_controller.py)

Centralized script to coordinate data flow through:

- textcleaner.py: Cleans raw text (HTML stripping, PII masking, whitespace fixes)
- text_normalizer.py: Handles domain-specific expansions, date parsing, lemmatization

Features:

- Auto-detects .csv, .json, .txt input files
- Outputs cleaned and normalized files in separate subfolders
- Logs each run (logs/pipeline_YYYYMMDD.log) for reproducibility

CLI Usage:

```bash
# Process single file
python pipeline_controller.py --input path/to/file.txt  

# Process all files in default input folder  
python pipeline_controller.py
```

### 🧹 Stage 1: Raw Text Cleaning (textcleaner.py)

| Step | Description | Methods |
|------|-------------|---------|
| Remove HTML/URLs | Strip out formatting artifacts | BeautifulSoup, Regex |
| Mask PII | Redact emails, phone numbers | Presidio + Custom Regex |
| Fix Encoding | Clean special characters | Unicode normalization |
| Whitespace Fixes | Collapse duplicate whitespace | re.sub(r'\s+', ' ', text) |

Reference: Implemented from our earlier text cleaner solution with Swahili enhancements

### 🛠️ Stage 2: Domain-Specific Normalization (text_normalizer.py)

| Step | Example | Implementation |
|------|---------|----------------|
| Standardize Dates | 4th Nov 2022 → 04 November 2022 | dateparser |
| Expand Abbreviations | FGM → Female Genital Mutilation | Custom dictionary replace |
| Lowercase | Optional normalization step | .lower() |

Benchmark: Achieves 92% spelling accuracy (SymSpell) as noted in our performance tests

### 🧹 Stage 3: Stopword Removal

- English + domain-specific stopwords (e.g., "call", "helpline")
- Swahili stopword support (stopwords-sw.json) with language detection

```python
# Sample implementation from our integration
if lang == 'sw':
    stopwords = json.load(open('stopwords-sw.json'))
```

## 3. Pipeline Output

| Format | Use Case | Output Directory |
|--------|----------|------------------|
| Cleaned | Manual QA or review | data/Cleaned/ |
| Normalized | Model training input | data/normalized/ |

## 4. Quality Assurance

Tests & Metrics (Located in benchmarks/):

- Noise Reduction: Fewer special characters and unstructured patterns
- Manual test samples available in test_cases block

Reference: Uses the benchmarking template we developed earlier

## 5. Case Category Classification (HuggingFace)

Fine-tuned transformer using Kenya's taxonomy:

- Trained on cleaned + normalized text
- Scripts and model checkpoints under Case_Category_Classification/

## 6. Synthetic Data Generation

Automates creation of training samples using:

- Template injection (e.g., trafficking, GBV, early marriage)
- Anonymized entities (name/location pools)

```python
# From our synthetic data implementation
synthetic_cases = generate_synthetic_cases(
    category="child_trafficking",
    count=100,
    template_file="./synthetic_data/templates/trafficking_template.txt",
    entities_pool="./synthetic_data/entities/anonymized_entities.json"
)
```

## 7. Multi-Language Support

English + Swahili pre-processing pipelines

Language detection routing:

```python
# Based on our language detection implementation
if detect(text) == 'sw':
    apply_swahili_normalization(text)
else:
    apply_english_normalization(text)
```

## 8. Appendix: Customization Tips

- ✅ Add more abbreviations in abbrev_map
- ✅ Integrate new legal definitions by modifying normalization rules
- ✅ Batch operations using pipeline_controller.py
- ✅ Extend language support using spacy.blank("sw")