# Text Pre-Processing Pipeline for Helpline & Legal Case Data
Version 1.0 | Designed for NLP Training (NER & Classification)

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

## 5. Appendix: Customization Guide
- Swahili Support: Use spacy.blank("sw") + Swahili Stopwords
- Legal Terms: Extend abbrev_map with Kenya's Children Act terminology
- Template Files