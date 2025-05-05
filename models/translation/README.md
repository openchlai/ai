# Translation Models

This directory contains models and utilities for translating case documents and communications related to child protection services.

## Purpose

The translation module provides tools to:
- Translate case documents between multiple languages
- Support multilingual communication with stakeholders
- Maintain terminology consistency across translations
- Preserve sensitive context in child protection communications

## Structure

- `seq2seq.py`: Sequence-to-sequence translation model implementation
- `evaluate.py`: Scripts for evaluating translation quality
- Future additions will include specialized models for different language pairs and domains

## Setup

```bash
# Install required dependencies
pip install -r requirements.txt

# Download pre-trained translation models
python download_translation_models.py --languages "en,fr,es,sw"
```

## Usage

### Basic Translation

```python
from translation.seq2seq import Translator

# Initialize translator with language pair
translator = Translator(source_lang="en", target_lang="fr")

# Translate text
translated_text = translator.translate("The child reported feeling unsafe at home.")
print(f"Translated text: {translated_text}")
```

### Batch Translation of Documents

```python
from translation.utils import batch_translate

# Batch translate a collection of documents
batch_translate(
    source_files=["case1.txt", "case2.txt"],
    source_lang="en",
    target_lang="sw",
    output_dir="./translated_cases/"
)
```

## Development Guidelines

When working with translation models:

1. Ensure translations preserve child protection terminology accurately
2. Validate translations with domain experts when adding new language pairs
3. Handle sensitive information with appropriate privacy measures
4. Test translations extensively before deployment
5. Document any domain-specific adaptations to base translation models

## Quality Assurance

```bash
# Evaluate translation quality
python evaluate.py --model standard --language-pair en-fr --test-set clinical_terms.csv

# Check for terminology consistency
python check_terminology.py --glossary child_protection_terms.csv --translated-files ./output/*.txt
```

## Supported Languages

Current translation support includes:
- English (en)
- French (fr)
- Spanish (es)
- Swahili (sw)

Additional languages can be added based on project requirements.

