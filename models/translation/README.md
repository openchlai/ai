# Translation Models

This directory contains models, utilities, and evaluation tools for translating structured and unstructured case documents related to child protection services.

## Purpose

The translation module is designed to:

- Translate case documents and transcripts between multiple languages
- Support multilingual communication between agents, clients, and partner organizations
- Maintain terminology consistency and preserve contextual meaning
- Handle both structured (transcripts) and unstructured (notes, messages) text formats

## Structure

- `seq2seq.py`: Sequence-to-sequence translation model implementation
- `evaluate.py`: Evaluation scripts for translation quality (BLEU, COMET, human scoring)
- `integration/`: Pipeline integration with voice transcription
- `data/`: Sample test sets and language-specific corpora
- `reports/`: Performance evaluation outputs and documentation

## Setup

```bash
# Install required dependencies
pip install -r requirements.txt

# Download pre-trained translation models
python download_translation_models.py --languages "en,sw,lug,nyn,teo"
```

## Usage

### Basic Translation

```python
from translation.seq2seq import Translator

# Initialize translator with language pair
translator = Translator(source_lang="en", target_lang="sw")

# Translate text
translated_text = translator.translate("The child reported feeling unsafe at home.")
print(f"Translated text: {translated_text}")
```

### Batch Translation of Documents

```python
from translation.utils import batch_translate

batch_translate(
    source_files=["case1.txt", "case2.txt"],
    source_lang="en",
    target_lang="lug",
    output_dir="./translated_cases/"
)
```

## Development Guidelines

When working with translation models:

- Ensure critical terminology is retained (e.g. protection concerns, service referrals)
- Validate translations with native speakers and domain experts
- Maintain data privacy in handling sensitive information
- Evaluate translation quality regularly across both structured and unstructured data
- Record limitations, edge cases, and improvements in evaluation reports

## Quality Assurance

We have implemented both automated and manual translation quality checks.

```bash
# Run BLEU and COMET evaluation
python evaluate.py --model baseline --language-pair en-lug --test-set test_cases_transcripts.csv
```

Reports include:

- BLEU, COMET, and chrF++ metrics
- Human evaluation (fluency/adequacy scores)
- Comparative charts by language and text type

📄 See reports/translation_performance_evaluation.md for detailed analysis

## Supported Languages

Current translation support includes:

- English (en)
- Swahili (sw)
- Luganda (lug)
- Runyankore (nyn)
- Ateso (teo)
- French (fr)
- Spanish (es)

Additional language support is planned based on regional needs and data availability.

## Recent Milestone Achievements

- ✅ Developed initial translation models for structured/unstructured text
- ✅ Integrated translation with voice transcription pipeline
- ✅ Evaluated translation quality across 5+ local languages
- ✅ Identified key challenges in low-resource language translation
- ✅ Published performance evaluation report with improvement recommendations
