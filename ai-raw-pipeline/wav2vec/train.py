import os
import re
import json
import torch
import random
import numpy as np
import pandas as pd
import evaluate
import torchaudio
from time import time, strftime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datasets import Audio, ClassLabel, load_dataset
from transformers import (
    Trainer,
    Wav2Vec2ForCTC,
    TrainingArguments,
    Wav2Vec2Processor,
    Wav2Vec2CTCTokenizer,
    Wav2Vec2FeatureExtractor
)

# Set random seed for reproducibility
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(42)

# Create output directory
output_dir = "wav2vec2-swahili-finetuned"
os.makedirs(output_dir, exist_ok=True)

print("Loading Common Voice Swahili dataset...")
# Load and combine train and validation data
common_voice_train = load_dataset(
    "mozilla-foundation/common_voice_11_0",
    "sw",
    split="train+validation",
    trust_remote_code=True
)

common_voice_test = load_dataset(
    "mozilla-foundation/common_voice_11_0",
    "sw",
    split="test",
    trust_remote_code=True
)

print(f"Train dataset size: {len(common_voice_train)}")
print(f"Test dataset size: {len(common_voice_test)}")

# Remove unnecessary columns
columns_to_remove = ["accent", "age", "client_id", "down_votes", "gender", "locale", "segment", "up_votes"]
common_voice_train = common_voice_train.remove_columns(columns_to_remove)
common_voice_test = common_voice_test.remove_columns(columns_to_remove)

# Text preprocessing
chars_to_ignore_regex = r'[\_\…\(\)\*\•\,\?\.\!\-\;\:\"\"\%\'\"\�]'

def remove_special_characters(batch):
    batch["sentence"] = re.sub(chars_to_ignore_regex, '', batch["sentence"]).lower() + " "
    return batch

print("Preprocessing text data...")
common_voice_train = common_voice_train.map(remove_special_characters)
common_voice_test = common_voice_test.map(remove_special_characters)

# Extract vocabulary
def extract_all_chars(batch):
    all_text = " ".join(batch["sentence"])
    vocab = list(set(all_text))
    return {"vocab": [vocab], "all_text": [all_text]}

print("Extracting vocabulary...")
vocab_train = common_voice_train.map(
    extract_all_chars,
    batched=True,
    batch_size=-1,
    keep_in_memory=True,
    remove_columns=common_voice_train.column_names
)

vocab_test = common_voice_test.map(
    extract_all_chars,
    batched=True,
    batch_size=-1,
    keep_in_memory=True,
    remove_columns=common_voice_test.column_names
)

# Create vocabulary dictionary
vocab_list = list(set(vocab_train["vocab"][0]) | set(vocab_test["vocab"][0]))
vocab_dict = {v: k for k, v in enumerate(vocab_list)}

# Replace space with a more visible character
vocab_dict["|"] = vocab_dict[" "]
del vocab_dict[" "]

# Add special tokens
vocab_dict["[UNK]"] = len(vocab_dict)
vocab_dict["[PAD]"] = len(vocab_dict)

print(f"Vocabulary size: {len(vocab_dict)}")

# Save vocabulary to file
vocab_file_path = os.path.join(output_dir, "vocab.json")
with open(vocab_file_path, 'w') as vocab_file:
    json.dump(vocab_dict, vocab_file)

# Create tokenizer
tokenizer = Wav2Vec2CTCTokenizer(
    vocab_file_path,
    unk_token="[UNK]",
    pad_token="[PAD]",
    word_delimiter_token="|"
)

# Create feature extractor
feature_extractor = Wav2Vec2FeatureExtractor(
    feature_size=1,
    sampling_rate=16000,
    padding_value=0.0,
    do_normalize=True,
    return_attention_mask=True
)

# Create processor (combines feature extractor and tokenizer)
processor = Wav2Vec2Processor(
    feature_extractor=feature_extractor,
    tokenizer=tokenizer
)

# Prepare audio data - ensure 16kHz sampling rate
print("Processing audio data...")
common_voice_train = common_voice_train.cast_column("audio", Audio(sampling_rate=16_000))
common_voice_test = common_voice_test.cast_column("audio", Audio(sampling_rate=16_000))

# Process data for model input
def prepare_dataset(batch):
    audio = batch["audio"]
    
    # Process audio
    batch["input_values"] = processor(
        audio["array"],
        sampling_rate=audio["sampling_rate"]
    ).input_values[0]
    
    batch["input_length"] = len(batch["input_values"])
    
    # Process text
    with processor.as_target_processor():
        batch["labels"] = processor(batch["sentence"]).input_ids
    
    return batch

print("Preparing train dataset...")
common_voice_train = common_voice_train.map(
    prepare_dataset,
    remove_columns=common_voice_train.column_names,
    num_proc=4  # Adjust based on CPU cores
)

print("Preparing test dataset...")
common_voice_test = common_voice_test.map(
    prepare_dataset,
    remove_columns=common_voice_test.column_names,
    num_proc=4  # Adjust based on CPU cores
)

# Filter out long audio samples to save memory
max_input_length_in_sec = 5.0
print(f"Filtering out samples longer than {max_input_length_in_sec} seconds...")
print(f"Before filtering: {len(common_voice_train)} samples")
common_voice_train = common_voice_train.filter(
    lambda x: x < max_input_length_in_sec * processor.feature_extractor.sampling_rate,
    input_columns=["input_length"]
)
print(f"After filtering: {len(common_voice_train)} samples")

# Data collator for dynamic padding
@dataclass
class DataCollatorCTCWithPadding:
    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True
    max_length: Optional[int] = None
    max_length_labels: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    pad_to_multiple_of_labels: Optional[int] = None

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # Split inputs and labels
        input_features = [{"input_values": feature["input_values"]} for feature in features]
        label_features = [{"input_ids": feature["labels"]} for feature in features]

        batch = self.processor.pad(
            input_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(
                label_features,
                padding=self.padding,
                max_length=self.max_length_labels,
                pad_to_multiple_of=self.pad_to_multiple_of_labels,
                return_tensors="pt",
            )

        # Replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        batch["labels"] = labels

        return batch

data_collator = DataCollatorCTCWithPadding(processor=processor, padding=True)

# Define evaluation metric - Word Error Rate
wer_metric = evaluate.load("wer")

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_ids = np.argmax(pred_logits, axis=-1)

    # Replace -100 with pad token id
    pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

    # Decode predictions and references
    pred_str = processor.batch_decode(pred_ids)
    label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

    # Compute WER
    wer = wer_metric.compute(predictions=pred_str, references=label_str)

    return {"wer": wer}

# Load pre-trained model
print("Loading pre-trained XLSR-Wav2Vec2 model...")
model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-large-xlsr-53", 
    attention_dropout=0.1,
    hidden_dropout=0.1,
    feat_proj_dropout=0.0,
    mask_time_prob=0.05,
    layerdrop=0.1,
    ctc_loss_reduction="mean", 
    pad_token_id=processor.tokenizer.pad_token_id,
    vocab_size=len(processor.tokenizer)
)

# Freeze feature extractor part
print("Freezing feature extractor parameters...")
model.freeze_feature_extractor()

# Save processor for later use
processor.save_pretrained(output_dir)

# Define training arguments with TensorBoard logging
training_args = TrainingArguments(
    output_dir=output_dir,
    group_by_length=True,
    per_device_train_batch_size=8,  # Adjusted for 16GB VRAM
    gradient_accumulation_steps=4,  # Increased to compensate for smaller batch size
    evaluation_strategy="steps",
    num_train_epochs=30,
    gradient_checkpointing=True,
    fp16=True,
    save_steps=400,
    eval_steps=400,
    logging_steps=100,
    learning_rate=3e-4,
    warmup_steps=500,
    save_total_limit=2,
    push_to_hub=False,
    # TensorBoard specific settings
    report_to=["tensorboard"],
    logging_dir=os.path.join(output_dir, "logs"),
    logging_strategy="steps",
)

# Initialize trainer
print("Initializing trainer...")
trainer = Trainer(
    model=model,
    data_collator=data_collator,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=common_voice_train,
    eval_dataset=common_voice_test,
    tokenizer=processor.feature_extractor,
)

# Start training
print("Starting training...")
trainer.train()

# Save final model
print("Saving final model...")
model.save_pretrained(os.path.join(output_dir, "final_model"))

# Evaluation on test set
print("Evaluating model on test set...")
eval_results = trainer.evaluate()
print(f"Final WER: {eval_results['eval_wer']:.4f}")

# Example prediction
def transcribe_audio(audio_path):
    """Transcribe an audio file using the fine-tuned model"""
    # Load audio
    audio_input, sample_rate = torchaudio.load(audio_path)
    
    # Resample if needed
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        audio_input = resampler(audio_input)
    
    # Convert to mono if stereo
    if audio_input.shape[0] > 1:
        audio_input = torch.mean(audio_input, dim=0, keepdim=True)
    
    # Process audio
    input_values = processor(audio_input.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_values
    
    # Get logits
    with torch.no_grad():
        logits = model(input_values).logits
    
    # Get predictions
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    
    return transcription

print("Training complete!")
print(f"Model and processor saved to {output_dir}")
print("To visualize training metrics with TensorBoard, run:")
print(f"tensorboard --logdir {os.path.join(output_dir, 'logs')}")