# Text Pre-Processing Pipeline for Helpline & Legal Case Data
Version 1.1 | Designed for NLP Training (NER & Classification)

## Project Structure
```
.
├── Case_Category_Classification/   # Case category classification resources
│   └── original_case_catagories_data/
├── README.md                       # This documentation file
├── stopwords-sw.json               # Swahili stopwords for text processing
└── synthetic_data/                 # Generated synthetic training data
```

## 1. Objectives
Clean and standardize unstructured helpline call narratives.

Preserve critical entities (names, dates, abuse types) for case management.

Prepare text for two downstream tasks:

Named Entity Recognition (NER): Extract victims, perpetrators, locations.

Text Classification: Categorize cases using Kenya's Children Act taxonomy.

## 2. Pipeline Stages
### Stage 1: Raw Text Cleaning
| Step | Description | Tools/Methods |
|------|-------------|---------------|
| Remove HTML/URLs | Strip web artifacts | BeautifulSoup, Regex |
| Remove PII | Mask emails/phones (optional) | Regex (\S+@\S+, \+\d{3,}) |
| Fix Encoding | Handle special chars (e.g., â€™ → ') | ftfy or unicodedata.normalize |
| Standardize Whitespace | Collapse multiple spaces | re.sub(r'\s+', ' ', text) |

Code:
```python
from bs4 import BeautifulSoup  
import re  

def clean_raw_text(text):  
    text = BeautifulSoup(text, "html.parser").get_text()  
    text = re.sub(r'http\S+|www\.\S+|\S+@\S+|\+\d{3,}', '', text)  # Remove URLs/emails/phones  
    text = text.encode('ascii', 'ignore').decode('ascii')  # Basic encoding fix  
    return re.sub(r'\s+', ' ', text).strip()  
```

### Stage 2: Domain-Specific Normalization
| Step | Example | Implementation |
|------|---------|----------------|
| Standardize Dates | 4th Nov 2022 → 04 November 2022 | dateparser.parse(date_str).strftime(...) |
| Expand Abbreviations | FGM → Female Genital Mutilation | Custom dictionary replacement |
| Lowercase (Optional) | Gender-Based Violence → gender-based violence | text.lower() |

Code:
```python
import dateparser  

def normalize_text(text):  
    # Dates  
    dates = re.findall(r'\b\d{1,2}(?:st|nd|rd|th)?\s(?:Jan|Feb|Nov)[a-z]*\s\d{4}\b', text, flags=re.IGNORECASE)  
    for date in dates:  
        text = text.replace(date, dateparser.parse(date).strftime("%d %B %Y"))  
    
    # Abbreviations  
    abbrev_map = {"FGM": "Female Genital Mutilation", "VAC": "Violence Against Children"}  
    for abbrev, full in abbrev_map.items():  
        text = re.sub(rf'\b{abbrev}\b', full, text, flags=re.IGNORECASE)  
    return text  
```

### Stage 3: Entity-Aware Processing
Goal: Protect key entities (names, locations) during tokenization.

Code (SpaCy):
```python
import spacy  

nlp = spacy.load("en_core_web_sm")  

def tokenize_preserve_entities(text):  
    doc = nlp(text)  
    tokens = []  
    for token in doc:  
        if token.ent_type_ in ["PERSON", "GPE", "DATE"]:  # Preserve entities  
            tokens.append(token.text)  
        elif not token.is_stop and not token.is_punct:  
            tokens.append(token.lemma_.lower())  # Lemmatize non-entities  
    return " ".join(tokens)  
```

Output Example:
"Mustafa (PERSON) asked about FGM in Nairobi (GPE)" → "Mustafa ask female genital mutilation Nairobi"

### Stage 4: Custom Stopword Removal
Domain-Specific Stopwords List:
```python
CUSTOM_STOPWORDS = {"call", "helpline", "said", "please", "thank"}  

def remove_stopwords(tokens):  
    return [t for t in tokens if t not in CUSTOM_STOPWORDS]  
```

## 3. Quality Assurance
Test Cases:
```python
test_cases = [  
    "On 4th Nov 2022, Mustafa (age 12) reported FGM by uncle in Nairobi.",  
    "Caller said: 'Child marriage case in Mombasa. Urgent!'"  
]  
```

Validation Metrics:
- Entity preservation rate (e.g., 95% of names/dates retained)
- Noise reduction (e.g., 90% fewer special chars)

## 4. Output for Model Training
For NER (SpaCy):
```python
import spacy  
from spacy.tokens import DocBin  

db = DocBin()  
for text, annotations in labeled_data:  # Annotated data  
    doc = nlp.make_doc(text)  
    doc.ents = [doc.char_span(start, end, label=label) for (start, end, label) in annotations]  
    db.add(doc)  
db.to_disk("train.spacy")  
```

For Classification (HuggingFace):
```python
from datasets import Dataset  

dataset = Dataset.from_dict({"text": processed_texts, "label": labels})  
dataset.save_to_disk("classification_data")  
```

## 5. Case Category Classification

The `Case_Category_Classification` directory contains resources for categorizing cases according to Kenya's Children Act taxonomy and other relevant legal frameworks:

- Original case categories data for training classification models
- Annotation guidelines for consistent labeling
- Pre-processed training data samples
- Evaluation metrics and benchmarks

Implementation example:
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load pre-trained model for case categorization
tokenizer = AutoTokenizer.from_pretrained("./Case_Category_Classification/model")
model = AutoModelForSequenceClassification.from_pretrained("./Case_Category_Classification/model")

def classify_case_category(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return {
        "category": model.config.id2label[predictions.argmax().item()],
        "confidence": predictions.max().item()
    }
```

## 6. Synthetic Data Generation

The `synthetic_data` directory contains tools and resources for generating synthetic training data:

- Template-based generation for rare case types
- Privacy-preserving data augmentation
- Balanced dataset creation for model training

Example usage:
```python
from synthetic_data_generator import generate_synthetic_cases

# Generate synthetic cases for under-represented categories
synthetic_cases = generate_synthetic_cases(
    category="child_trafficking",
    count=100,
    template_file="./synthetic_data/templates/trafficking_template.txt",
    entities_pool="./synthetic_data/entities/anonymized_entities.json"
)

# Use synthetic data for model training
train_data.extend(synthetic_cases)
```

## 7. Multi-language Support

The pipeline includes support for Swahili text processing:

- `stopwords-sw.json` contains Swahili stopwords for text preprocessing
- Language detection to apply appropriate processing rules
- Bilingual entity recognition capabilities

Example usage:
```python
import json

# Load Swahili stopwords
with open("stopwords-sw.json", "r") as f:
    sw_stopwords = json.load(f)

def process_text_multilingual(text, language="en"):
    if language == "sw":
        # Apply Swahili-specific processing
        tokens = tokenize_swahili(text)
        tokens = [t for t in tokens if t not in sw_stopwords]
    else:
        # Apply English processing
        tokens = tokenize_english(text)
    
    return " ".join(tokens)
```

## 8. Appendix: Customization Guide
- Swahili Support: Use spacy.blank("sw") + Swahili Stopwords
- Legal Terms: Extend abbrev_map with Kenya's Children Act terminology
- Template Files
