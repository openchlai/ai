---
library_name: transformers
license: apache-2.0
base_model: openai/whisper-large-v2
tags:
- generated_from_trainer
- swahili
- asr
- whisper
- common-voice
- tanzania
- child-helpline
datasets:
- mozilla-foundation/common_voice_17_0
metrics:
- wer
model-index:
- name: asr-whisper-helpline-sw-v1
  results:
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: common_voice_17_0
      type: common_voice_17_0
      config: sw
      split: validation
      args: sw
    metrics:
    - name: Wer
      type: wer
      value: 23.61977361977362
  - task:
      name: Automatic Speech Recognition
      type: automatic-speech-recognition
    dataset:
      name: common_voice_17_0
      type: common_voice_17_0
      config: sw
      split: test
      args: sw
    metrics:
    - name: Wer
      type: wer
      value: 29.34
language:
- sw
pipeline_tag: automatic-speech-recognition
---

# asr-whisper-helpline-sw-v1

This model is a fine-tuned version of [openai/whisper-large-v2](https://huggingface.co/openai/whisper-large-v2) on the Common Voice 17.0 Swahili dataset.

## Model Description

This ASR model is specifically fine-tuned for **Swahili speech recognition** in the context of the **Tanzania Child Helpline**, powered by [OpenCHS](https://github.com/openchlai/ai) (Open Source Child Helpline System). The model is designed to transcribe Swahili spoken in Tanzanian call center environments.

**Performance Highlights:**
- **Validation WER:** 23.62%
- **Test WER:** 29.34%
- **Baseline WER:** 89.05% (Whisper Large v2 zero-shot)
- **Validation Improvement:** approx. 65 percentage point reduction in WER (approx. 75% error rate reduction)
- **Test Improvement:** approx. 60 percentage point reduction in WER (approx. 67% error rate reduction)

This represents a significant improvement over the base Whisper Large v2 model for Swahili transcription tasks.

## Intended Uses & Limitations

### Intended Uses
- **Primary:** Transcribing Swahili speech in call center environments, specifically for child helpline services in Tanzania
- **General:** Swahili automatic speech recognition tasks
- **Research:** Baseline for domain adaptation studies (general speech → telephony/call center audio)

### Limitations
- **Domain Shift:** Model is trained on Common Voice 17.0 (clean, read speech) but intended for call center audio. Performance on actual telephony audio may differ and requires validation.
- **Language Variety:** Training data may not fully represent all Tanzanian Swahili dialects and speaking styles.
- **Audio Quality:** Performance may degrade with low-quality audio, background noise, or poor recording conditions typical in telephony.
- **Code-Switching:** May not handle code-switching between Swahili and English/other languages well.
- **Generalization Gap:** ~5.7 percentage point gap between validation (23.62%) and test (29.34%) WER.

### Known Issues
- Domain-specific evaluation on actual call center audio is pending

## Training and Evaluation Data

### Dataset: Common Voice 17.0 (Swahili)

**Training Configuration:**
- **Training samples:** Streamed entire Common Voice 17.0 Swahili training split (~999,999 streaming mode)
- **Validation samples:** 2,000 samples
- **Source:** [Mozilla Common Voice 17.0](https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0/viewer/sw)
- **Language:** Swahili (sw)
- **Data type:** Read speech from diverse speakers
- **Streaming mode:** Used dataset streaming to minimize disk usage

**Baseline Performance:**
- Base Whisper Large v2 (zero-shot): **89.05% WER** on 2,000 validation samples
- This model (validation): **23.62% WER**
- This model (test): **29.34% WER** on 2,000 test samples

## Training Procedure

### Training Hyperparameters

The following hyperparameters were used during training:

**Optimization:**
- learning_rate: 1e-05
- lr_scheduler_type: linear
- lr_scheduler_warmup_steps: 500
- optimizer: AdamW (torch) with betas=(0.9, 0.999) and epsilon=1e-08
- training_steps: 10,000

**Batch Configuration:**
- train_batch_size: 16
- eval_batch_size: 16
- gradient_accumulation_steps: 1

**Memory Optimization:**
- gradient_checkpointing: true
- mixed_precision_training: Native AMP (FP16)
- dataloader_num_workers: 2

**Evaluation & Checkpointing:**
- evaluation_strategy: steps (every 500 steps)
- save_steps: 500
- logging_steps: 50
- save_total_limit: 3
- early_stopping_patience: 5 evaluations

**Model Selection:**
- load_best_model_at_end: true
- metric_for_best_model: wer
- greater_is_better: false

**Other:**
- seed: 42
- num_workers: 8
- preprocessing_batch_size: 100

### Training Results

| Training Loss | Epoch  | Step  | Validation Loss | WER     |
|:-------------:|:------:|:-----:|:---------------:|:-------:|
| 0.5275        | 0.05   | 500   | 0.7083          | 43.68   |
| 0.4754        | 0.10   | 1000  | 0.5733          | 42.07   |
| 0.2844        | 0.15   | 1500  | 0.5390          | 36.21   |
| 0.2647        | 0.20   | 2000  | 0.5060          | 34.32   |
| 0.2939        | 0.25   | 2500  | 0.4761          | 34.89   |
| 0.2850        | 1.01   | 3000  | 0.4610          | 35.04   |
| 0.1837        | 1.06   | 3500  | 0.4516          | 34.07   |
| 0.2148        | 1.11   | 4000  | 0.4309          | 33.10   |
| 0.2611        | 1.16   | 4500  | 0.4328          | 29.09   |
| 0.1923        | 1.21   | 5000  | 0.4180          | 31.24   |
| 0.0849        | 1.26   | 5500  | 0.4229          | 25.80   |
| 0.1913        | 2.02   | 6000  | 0.4051          | 28.46   |
| 0.0693        | 2.07   | 6500  | 0.4256          | 29.18   |
| 0.1261        | 2.12   | 7000  | 0.4057          | 28.88   |
| 0.0808        | 2.17   | 7500  | 0.4054          | 28.39   |
| 0.0524        | 2.22   | 8000  | 0.4248          | 25.68   |
| 0.0845        | 2.27   | 8500  | 0.4159          | 26.51   |
| 0.0611        | 3.03   | 9000  | 0.4142          | 25.44   |
| 0.0562        | 3.08   | 9500  | 0.4104          | 25.69   |
| 0.0867        | 3.13   | 10000 | 0.4024          | 23.62   |

**Training Observations:**
- Rapid initial improvement: WER dropped from 43.68% → 36.21% in first 1,500 steps
- Steady progress: Continued improvement from ~36% → ~29% (steps 1,500-6,000)
- Final optimization: Reached 23.62% WER by step 10,000
- No signs of overfitting observed
- Training completed in ~3 epochs through the dataset

### Test Set Results

**Evaluation Details:**
- Test samples: 2,000
- Test WER: 29.34%
- WER Statistics:
  - Mean: 32.14%
  - Median: 22.22%
  - Min: 0.0%
  - Max: 2200.0% (outlier)

**Analysis:** The model shows strong performance on the test set with a median WER of 22.22%, close to the validation performance. The presence of outliers (max WER of 2200%) suggests some challenging samples that may require additional attention or preprocessing.

## Performance Comparison

| Model | Split | WER | Improvement from Baseline |
|-------|-------|-----|---------------------------|
| Whisper Large v2 (baseline) | Validation | 89.05% | - |
| **This model** | **Validation** | **23.62%** | **-65.43 pp (75% reduction)** |
| **This model** | **Test** | **29.34%** | **-59.71 pp (67% reduction)** |

**Note:** The substantial error rate reductions on both validation and test sets demonstrate effective domain adaptation through fine-tuning on Swahili data. The ~5.7 percentage point generalization gap between validation and test sets is reasonable and indicates good model generalization.

## Usage

```python
from transformers import pipeline

# Load the model
pipe = pipeline("automatic-speech-recognition", 
                model="openchs/asr-whisper-helpline-sw-v1")

# Transcribe audio
result = pipe("path/to/swahili_audio.wav")
print(result["text"])
```

## Future Work

- **Domain Evaluation:** Assessment on actual Tanzania Child Helpline call center audio to measure domain shift impact
- **Domain Adaptation:** Fine-tuning on telephony/call center audio for improved production performance
- **Error Analysis:** Detailed analysis of failure cases on test set to identify improvement opportunities

## Citation

If you use this model, please cite:

```bibtex
@misc{openchs-swahili-asr-v1,
  title={Swahili ASR Model for Tanzania Child Helpline},
  author={OpenCHS Team},
  year={2025},
  publisher={HuggingFace},
  howpublished={\url{https://huggingface.co/openchs/asr-whisper-helpline-sw-v1}}
}
```

## Framework Versions

- Transformers: 4.56.2
- PyTorch: 2.8.0+cu128
- Datasets: 2.21.0
- Tokenizers: 0.22.1

## License

Apache 2.0

## Acknowledgments

- Base model: [OpenAI Whisper Large v2](https://huggingface.co/openai/whisper-large-v2)
- Training data: [Mozilla Common Voice 17.0](https://commonvoice.mozilla.org/)
- Project: [OpenCHS](https://github.com/openchlai/ai)