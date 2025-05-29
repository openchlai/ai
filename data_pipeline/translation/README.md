# Translation Pipeline

## Overview

The Translation Pipeline is a critical component of the Data Pre-Processing Pipeline, responsible for detecting the language of transcribed text and translating non-English content into English. This module serves as a bridge between the Speech-to-Text transcription and the NLP-based case prediction components, ensuring all data is in a consistent language format for downstream processing.

This module processes text that has been transcribed from audio recordings of helpline calls, mobile app messages, and other voice sources. It enables the system to handle multilingual input while maintaining a standardized English output for the machine learning models.

## Key Features

- **Automatic Language Detection**: Identifies the source language of transcribed text
- **High-Quality Machine Translation**: Converts non-English text to English using state-of-the-art open-source translation models
- **Quality Assurance**: Implements confidence scoring and automated quality checks
- **Error Handling**: Flags low-confidence translations for human review
- **Batch and Real-time Processing**: Supports both bulk translation and on-demand requests
- **Scalable Architecture**: Designed to handle large volumes of text efficiently

## Models and Tools Used

### Language Detection
- **FastText**: Pre-trained for 170+ languages with fast inference capability
- **LangID.py**: Machine learning-based classifier for accurate language identification
- **CLD2/CLD3**: Google's Compact Language Detector as a fallback option

### Translation Models
- **Marian-NMT**: Neural Machine Translation engine with good support for African languages
- **OpenNMT**: Customizable open-source neural machine translation framework
- **Fairseq**: Facebook's sequence-to-sequence toolkit for neural machine translation

### Quality Evaluation
- **BLEU Score**: Measures translation quality by comparing against reference translations
- **METEOR**: Metric for evaluating translation output
- **ROUGE**: Recall-Oriented Understudy for Gisting Evaluation

## Implementation Details

### Language Detection Process
1. Receive transcribed text from the Speech-to-Text component
2. Apply FastText language detection model to identify the source language
3. If confidence is low, use LangID.py or CLD2/CLD3 as fallbacks
4. Store detected language information with the text
5. Determine if translation is needed (skip if already English)

### Translation Process
1. Select the appropriate translation model based on the detected source language
2. For African languages, prioritize Marian-NMT with specialized language pairs
3. Process text through the neural translation engine
4. Generate translated English text along with confidence scores
5. Store both original and translated text in the database

### Translation Quality Control
1. Calculate confidence scores for each translation
2. Apply back-translation check for critical content (translate English back to source language)
3. Compare against parallel corpus of human translations when available
4. Flag translations below confidence threshold (75%) for manual review
5. Store quality metrics for monitoring and improvement

## Usage Instructions

### As a Library
```python
from translation import TranslationPipeline

# Initialize the pipeline
translator = TranslationPipeline(
    language_detection_model="fasttext",
    translation_model="marian-nmt"
)

# Process a single text
result = translator.process_text("Mfanyikazi alionyeshwa ukatili na kampuni ya XYZ huko Nairobi")
print(f"Detected language: {result.detected_language}")
print(f"Translation: {result.translated_text}")
print(f"Confidence: {result.confidence_score}")

# Process a batch of texts
results = translator.process_batch([text1, text2, text3])
```

### As a Service
The translation component can be accessed via API endpoints:

- **POST /api/v1/translation/detect**
  - Detects the language of provided text
  - Returns language code and confidence

- **POST /api/v1/translation/translate**
  - Translates text to English
  - Returns translated text and quality metrics

- **POST /api/v1/translation/batch**
  - Processes multiple texts in a single request
  - Returns array of results

## Quality Control

### Automatic Quality Assessment
The translation pipeline implements several automatic quality checks:

1. **Confidence Scoring**
   - High (>90%): Automatically approved
   - Medium (75-90%): Used with caution
   - Low (<75%): Flagged for review

2. **Back-Translation Validation**
   - Translated English text is re-translated back to source language
   - Original and back-translated texts are compared for semantic similarity
   - Significant divergence triggers manual review

3. **Named Entity Preservation**
   - Checks that named entities (people, organizations, locations) are preserved
   - Uses NER models to compare entities before and after translation

### Human Review Process
For translations flagged as low confidence:

1. Texts are queued in the "Review Required" database
2. Translators can access these through the review interface
3. Human-corrected translations are fed back to improve model performance

### Performance Metrics
The translation component tracks the following metrics:

- Language detection accuracy
- Translation quality scores (BLEU, METEOR, ROUGE)
- Processing time per text
- Percentage of texts requiring human review

## Integration with Other Components

The Translation Pipeline connects with:

- **Upstream**: Receives text from the Speech-to-Text Transcription component
- **Downstream**: Feeds translated English text to the NLP Processing component
- **Storage**: Stores results in PostgreSQL with metadata
- **Reporting**: Provides metrics to the Visualization component

## Future Improvements

- Expand language support with additional specialized models
- Implement domain-specific fine-tuning for legal/case terminology
- Add support for dialect variations within languages
- Integrate adaptive learning to improve translations based on corrections

