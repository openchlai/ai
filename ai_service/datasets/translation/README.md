---
language:
- lg
- en
license:
- apache-2.0
- mit
task_categories:
- translation
tags:
- luganda
- child-protection
- helpline
- low-resource
- machine-translation
pretty_name: Luganda-English Parallel Translation Corpus for Child Helpline Services
size_categories:
- 10K<n<100K
dataset_info:
  features:
  - name: luganda_text
    dtype: string
  - name: english_text
    dtype: string
  - name: source
    dtype: string
  - name: domain
    dtype: string
  - name: quality_score
    dtype: float32
  splits:
  - name: train
    num_examples: 35008
  - name: validation
    num_examples: 10002
  - name: test
    num_examples: 5002
  download_size: [SIZE_IN_BYTES]
  dataset_size: 50012
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
  - split: validation
    path: data/validation-*
  - split: test
    path: data/test-*
---

# Luganda-English Parallel Translation Corpus for Child Helpline Services

## Dataset Description

### Dataset Summary

This dataset contains 50,012 parallel Luganda-English translation pairs developed to support machine translation systems for child helpline operations in Uganda. The corpus combines synthetically generated translation pairs with domain-adapted terminology relevant to child protection, psychological support, and helpline communication scenarios.

The dataset addresses the critical gap in Luganda language resources for NLP applications, enabling the development of translation models that can facilitate communication between Luganda-speaking callers and service providers. The data has been carefully processed to remove personally identifiable information (PII) while maintaining the linguistic characteristics and contextual nuances essential for helpline environments.

Special attention has been given to translating sensitive topics related to child welfare, family issues, and mental health support in culturally appropriate ways. The dataset supports both the translation of real-time helpline conversations and the analysis of historical call data for service improvement and reporting purposes.

### Supported Tasks and Leaderboards

- **Machine Translation**: Bidirectional translation between Luganda (lg) and English (en)
- **Domain Adaptation**: Fine-tuning translation models for child protection and helpline contexts
- **Low-Resource NLP**: Supporting research in Luganda language processing

### Languages

- **Source Language**: Luganda (lg)
- **Target Language**: English (en)
- **Domain**: Child helpline services, child protection, mental health support, family services

## Dataset Structure

### Data Instances

A typical data instance contains:

```json
{
  "luganda_text": "Omwana wange alina obuzibu bw'okweyongera mu ssomero",
  "english_text": "My child is having difficulties concentrating in school",
  "source": "synthetic",
  "domain": "child_protection",
  "quality_score": 0.85
}
```

### Data Fields

- `luganda_text` (string): Source text in Luganda language
- `english_text` (string): Target text in English language
- `source` (string): Origin of translation pair - values include:
  - `human`: Human-translated pairs
  - `synthetic`: Synthetically generated using LLMs
  - `augmented`: Back-translation or augmentation techniques
- `domain` (string): Content category - values include:
  - `child_protection`: Child safety and protection scenarios
  - `general`: General helpline communication
  - `mental_health`: Psychological support conversations
  - `family_support`: Family and parenting guidance
- `quality_score` (float): Quality assessment score (0.0-1.0), with overall corpus quality at 80%

### Data Splits

The dataset is split into three subsets:

| Split | Size | Percentage |
|-------|------|------------|
| Train | 35,008 | 70% |
| Validation | 10,002 | 20% |
| Test | 5,002 | 10% |

## Dataset Creation

### Curation Rationale

This dataset was created to address the critical shortage of Luganda-English parallel corpora, particularly in specialized domains like child helpline services. The motivation stems from the need to:

1. Enable effective communication between Luganda-speaking children and families and helpline services
2. Support the development of translation tools for child protection workers in Uganda
3. Facilitate the analysis of helpline data for service improvement while maintaining privacy
4. Contribute to the broader ecosystem of low-resource African language NLP tools

### Source Data

#### Data Collection and Processing

The dataset combines multiple sources and collection methods:

1. **Synthetic Generation**: Large language models fine-tuned for Luganda-English translation were used with helpline-specific prompts to generate contextually appropriate translation pairs
2. **Human Translation**: Professional translation of child protection resources, helpline scripts, and educational materials
3. **Anonymized Transcripts**: Extraction and sanitization of parallel text from child helpline service records
4. **Government Resources**: Translation of bilingual government documents related to child protection
5. **Back-Translation**: Augmentation techniques to expand the corpus while maintaining quality

All data underwent rigorous quality control and anonymization before inclusion.

#### Who are the source data producers?

- Professional translators with expertise in Luganda and English
- Child protection specialists and helpline operators
- Computational linguists and NLP researchers
- Government child protection agencies in Uganda
- Synthetic data generated using language models under expert supervision

### Annotations

The dataset includes several annotation layers:

#### Annotation process

- **Source Annotation**: Each translation pair is labeled with its origin (human/synthetic/augmented)
- **Domain Classification**: Manual categorization into child_protection, mental_health, family_support, or general domains
- **Quality Scoring**: Automated and manual quality assessment resulting in quality scores
- **PII Verification**: Multi-stage review to ensure complete anonymization

#### Who are the annotators?

- Bilingual annotators fluent in Luganda and English
- Child protection specialists with cultural context knowledge
- Data privacy experts for PII verification
- Native Luganda speakers for linguistic quality assessment

### Personal and Sensitive Information

**PII Handling:**

All data has been rigorously processed through a multi-stage PII detection and anonymization pipeline:

1. **Automated Detection**: Presidio framework with custom spaCy NER models for both English and Luganda
2. **Entity Replacement**: Personal names, phone numbers, locations, identification numbers, and other identifiable information were replaced with category-appropriate placeholders (e.g., [PERSON_1], [LOCATION], [PHONE])
3. **De-anonymization with Synthetic Data**: Faker library used to generate culturally appropriate fake entities to replace placeholders
4. **Manual Review**: Trained annotators reviewed flagged entities for accuracy
5. **Statistical Validation**: Analysis to ensure no identifying patterns remain
6. **Differential Privacy**: Applied to synthetic data generation to prevent memorization of real cases

Transcripts were de-identified before translation to ensure no sensitive information appears in either language. Any cases that could not be adequately anonymized were removed from the dataset.

## Considerations for Using the Data

### Social Impact of Dataset

**Positive Impact:**
- Enables better support for Luganda-speaking children and families accessing helpline services
- Reduces language barriers in critical child protection scenarios
- Supports service providers in understanding and responding to Luganda-language calls
- Contributes to the preservation and technological development of the Luganda language
- Provides infrastructure for mental health and family support services

**Potential Risks:**
- Translation errors in sensitive contexts could lead to misunderstandings
- Over-reliance on automated translation may reduce human interaction quality
- Biases in training data could perpetuate stereotypes or cultural misconceptions
- Privacy risks if PII anonymization is incomplete (though extensively mitigated)

### Discussion of Biases

**Known Biases:**

1. **Urban-Rural Bias**: Source data may overrepresent urban language patterns from helpline centers located in cities
2. **Synthetic Data Bias**: Synthetically generated examples may reflect biases present in the underlying language models
3. **Register Bias**: Translation may favor formal registers over colloquial speech patterns common in actual helpline calls
4. **Demographic Representation**: Gender and age representation in synthetic scenarios may not perfectly reflect actual caller demographics
5. **Topic Limitation**: Limited representation of certain sensitive topics due to ethical constraints in generating appropriate training examples
6. **Code-Switching**: Minimal representation of Luganda-English code-switching that commonly occurs in real conversations

### Other Known Limitations

1. **Translationese Effects**: Synthetic data may exhibit characteristics of translated text rather than natural speech
2. **Dialect Coverage**: Domain-specific vocabulary may not cover all regional dialects of Luganda spoken across Uganda
3. **Cultural Nuance**: Some culturally nuanced expressions may lose meaning in direct translation
4. **Dataset Size**: The corpus may be insufficient for training very large models without transfer learning approaches
5. **Real-time Performance**: Models trained on this data should be validated for real-time translation scenarios
6. **Domain Specificity**: Performance on general-domain translation may be limited

## Additional Information

### Dataset Curators

This dataset was curated by **OpenCHS** in collaboration with child protection organizations, linguistic experts, and NLP researchers.

### Licensing Information

This dataset is released under dual licensing:
- Apache License 2.0
- MIT License

Users may choose either license for their use case.

### Citation Information

If you use this dataset, please cite:

```bibtex
@dataset{luganda_english_helpline_2025,
  title={Luganda-English Parallel Translation Corpus for Child Helpline Services},
  author={OpenCHS},
  year={2025},
  publisher={Hugging Face},
  howpublished={\url{https://huggingface.co/datasets/openchs/luganda-english-translation}}
}
```

### Contributions

This dataset was made possible through:
- **Funding**: UNICEF
- **Organization**: OpenCHS
- **Contributors**: Child protection specialists, professional translators, NLP researchers, and helpline operators

### Contact

For questions, feedback, or collaboration opportunities:
- **Email**: info@bitz-itc.com
- **Organization**: OpenCHS

### Evaluation Metrics

**Translation Quality:**
- BLEU Score: 49.51 on test set
- Human Evaluation:
  - Adequacy: 4.0/5.0
  - Fluency: 3.8/5.0
- Domain Expert Review: 75% approved for helpline use (improvements ongoing)
- Back-translation BLEU: Integration planned for second dataset version

### Intended Use Cases

✅ **Recommended Uses:**
- Training and evaluating Helsinki/OPUS multilingual translation models
- Developing real-time translation assistance tools for helpline operators
- Translating helpline resources and educational materials for Luganda-speaking communities
- Analyzing Luganda-language call transcripts through translation to English for case management and reporting
- Research in low-resource machine translation
- Domain adaptation for child protection and helpline NLP applications

❌ **Out-of-Scope Uses:**
- Commercial translation services without additional quality validation
- Medical or legal translation requiring certified accuracy
- Applications requiring real-time safety-critical translation without human oversight
- Any purpose that could identify or harm vulnerable children or families
- High-stakes decision-making without human review

### Recommendations

Users should be aware of the following:

1. **Human Oversight Required**: Always include human review for helpline communications, especially for sensitive or safety-critical content
2. **Cultural Sensitivity**: Consider engaging native Luganda speakers and cultural experts when deploying systems using this data
3. **Continuous Improvement**: The dataset represents an ongoing effort; quality metrics indicate room for improvement
4. **Privacy Vigilance**: While PII has been removed, users should implement additional privacy safeguards in production systems
5. **Bias Mitigation**: Implement bias detection and mitigation strategies when training models on this data
6. **Domain Validation**: Validate model performance on your specific use case, as performance may vary across domains
7. **Ethical Deployment**: Follow ethical AI principles and child safeguarding protocols in any deployment

### Version History

- **v1.0** (2025): Initial release with 50,012 translation pairs
- Future versions will include back-translation evaluation and expanded dialect coverage

### Acknowledgments

We thank the child helpline workers, translators, and families who made this dataset possible while maintaining privacy and dignity. Special thanks to UNICEF for funding this critical work in child protection technology.