import os
import re
import json
import torch
import random
import numpy as np
import pandas as pd
import evaluate
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datasets import Audio, load_dataset
from transformers import (
    Trainer,
    Wav2Vec2ForCTC,
    TrainingArguments,
    Wav2Vec2Processor,
    Wav2Vec2CTCTokenizer,
    Wav2Vec2FeatureExtractor,
    set_seed
)
from transformers.trainer_utils import get_last_checkpoint
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
set_seed(42)

# Create output directory
output_dir = "wav2vec2-swahili-finetuned"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "checkpoints"), exist_ok=True)

# Check if we have a GPU available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")
if torch.cuda.is_available():
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"Available VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")

# Load and combine train and validation data
logger.info("Loading Common Voice Swahili dataset...")
try:
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

    logger.info(f"Train dataset size: {len(common_voice_train)}")
    logger.info(f"Test dataset size: {len(common_voice_test)}")
except Exception as e:
    logger.error(f"Error loading dataset: {e}")
    logger.info("Trying alternative dataset loading approach...")
    
    # Alternative approach if the above fails
    try:
        common_voice_train = load_dataset(
            "common_voice",
            "sw",
            split="train+validation"
        )
        
        common_voice_test = load_dataset(
            "common_voice",
            "sw",
            split="test"
        )
        
        logger.info(f"Train dataset size: {len(common_voice_train)}")
        logger.info(f"Test dataset size: {len(common_voice_test)}")
    except Exception as e2:
        logger.error(f"Alternative loading also failed: {e2}")
        logger.info("Please check your HuggingFace credentials and internet connection.")
        sys.exit(1)

# Remove unnecessary columns
columns_to_remove = ["accent", "age", "client_id", "down_votes", "gender", "locale", "segment", "up_votes"]
try:
    # Check which columns actually exist in the dataset
    existing_columns = [col for col in columns_to_remove if col in common_voice_train.column_names]
    common_voice_train = common_voice_train.remove_columns(existing_columns)
    common_voice_test = common_voice_test.remove_columns([col for col in existing_columns if col in common_voice_test.column_names])
except Exception as e:
    logger.warning(f"Error removing columns: {e}")
    logger.info("Continuing with available columns...")

# Display dataset information
logger.info(f"Train dataset columns: {common_voice_train.column_names}")
logger.info(f"Test dataset columns: {common_voice_test.column_names}")

# Sample data to inspect
logger.info("Sampling data for inspection...")
try:
    sample_data = common_voice_train.select(range(min(5, len(common_voice_train))))
    for i, item in enumerate(sample_data):
        if 'sentence' in item:
            logger.info(f"Sample {i}: {item['sentence'][:100]}...")
        else:
            logger.info(f"Sample {i} structure: {list(item.keys())}")
except Exception as e:
    logger.warning(f"Error displaying samples: {e}")

# Text preprocessing
chars_to_ignore_regex = r'[\_\…\(\)\*\•\,\?\.\!\-\;\:\"\"\%\'\"\�]'

def remove_special_characters(batch):
    try:
        if 'sentence' in batch:
            batch["sentence"] = re.sub(chars_to_ignore_regex, '', batch["sentence"]).lower() + " "
        elif 'text' in batch:  # Some datasets use 'text' instead of 'sentence'
            batch["sentence"] = re.sub(chars_to_ignore_regex, '', batch["text"]).lower() + " "
            
        return batch
    except Exception as e:
        logger.warning(f"Error in text preprocessing: {e}")
        return batch

logger.info("Preprocessing text data...")
try:
    # Adapt to different dataset structures
    text_column = 'sentence' if 'sentence' in common_voice_train.column_names else 'text'
    if text_column not in common_voice_train.column_names:
        logger.error(f"Text column not found. Available columns: {common_voice_train.column_names}")
        sys.exit(1)
        
    # If needed, rename 'text' to 'sentence' for consistency
    if text_column == 'text':
        common_voice_train = common_voice_train.rename_column('text', 'sentence')
        common_voice_test = common_voice_test.rename_column('text', 'sentence')
        
    common_voice_train = common_voice_train.map(remove_special_characters)
    common_voice_test = common_voice_test.map(remove_special_characters)
except Exception as e:
    logger.error(f"Error in text preprocessing: {e}")
    sys.exit(1)

# Extract vocabulary
def extract_all_chars(batch):
    all_text = " ".join(batch["sentence"])
    vocab = list(set(all_text))
    return {"vocab": [vocab], "all_text": [all_text]}

logger.info("Extracting vocabulary...")
try:
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
except Exception as e:
    logger.error(f"Error extracting vocabulary: {e}")
    sys.exit(1)

# Create vocabulary dictionary
vocab_list = list(set(vocab_train["vocab"][0]) | set(vocab_test["vocab"][0]))
vocab_dict = {v: k for k, v in enumerate(vocab_list)}

# Replace space with a more visible character
vocab_dict["|"] = vocab_dict[" "]
del vocab_dict[" "]

# Add special tokens
vocab_dict["[UNK]"] = len(vocab_dict)
vocab_dict["[PAD]"] = len(vocab_dict)

logger.info(f"Vocabulary size: {len(vocab_dict)}")
logger.info(f"Vocabulary: {sorted(vocab_dict.keys())}")

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
logger.info("Processing audio data...")
try:
    common_voice_train = common_voice_train.cast_column("audio", Audio(sampling_rate=16_000))
    common_voice_test = common_voice_test.cast_column("audio", Audio(sampling_rate=16_000))
except Exception as e:
    logger.error(f"Error preparing audio data: {e}")
    sys.exit(1)

# Process data for model input
def prepare_dataset(batch):
    try:
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
    except Exception as e:
        logger.warning(f"Error processing batch: {e}")
        return None

logger.info("Preparing train dataset...")
try:
    # Use fewer processes to avoid memory issues
    num_proc = min(4, os.cpu_count() or 1)
    logger.info(f"Using {num_proc} processes for data processing")
    
    common_voice_train = common_voice_train.map(
        prepare_dataset,
        remove_columns=common_voice_train.column_names,
        num_proc=num_proc
    )

    logger.info("Preparing test dataset...")
    common_voice_test = common_voice_test.map(
        prepare_dataset,
        remove_columns=common_voice_test.column_names,
        num_proc=num_proc
    )
except Exception as e:
    logger.error(f"Error preparing dataset: {e}")
    sys.exit(1)

# Filter out long audio samples to save memory
max_input_length_in_sec = 5.0
logger.info(f"Filtering out samples longer than {max_input_length_in_sec} seconds...")
logger.info(f"Before filtering: {len(common_voice_train)} train samples")

try:
    common_voice_train = common_voice_train.filter(
        lambda x: x < max_input_length_in_sec * processor.feature_extractor.sampling_rate,
        input_columns=["input_length"]
    )
    logger.info(f"After filtering: {len(common_voice_train)} train samples")
except Exception as e:
    logger.warning(f"Error filtering long samples: {e}")
    logger.info("Continuing with all samples...")

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
try:
    wer_metric = evaluate.load("wer")
except Exception as e:
    logger.warning(f"Error loading 'wer' metric from evaluate: {e}")
    logger.info("Loading alternative WER implementation...")
    
    # Alternative WER implementation using jiwer
    import jiwer
    def compute_wer(predictions, references):
        return jiwer.wer(references, predictions)

def compute_metrics(pred):
    try:
        pred_logits = pred.predictions
        pred_ids = np.argmax(pred_logits, axis=-1)

        # Replace -100 with pad token id
        pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

        # Decode predictions and references
        pred_str = processor.batch_decode(pred_ids)
        label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

        # Compute WER
        if 'wer_metric' in globals():
            wer = wer_metric.compute(predictions=pred_str, references=label_str)
        else:
            # Use alternative implementation
            wer = compute_wer(pred_str, label_str)

        return {"wer": wer}
    except Exception as e:
        logger.error(f"Error computing metrics: {e}")
        return {"wer": 1.0}  # Return worst possible WER on error

# Function to estimate batch size based on available VRAM
def estimate_batch_size():
    if not torch.cuda.is_available():
        return 4  # Default for CPU
    
    # Get GPU memory info in GB
    vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    
    # Simple heuristic based on VRAM
    if vram_total > 20:  # High-end GPU (24GB+)
        return 16
    elif vram_total > 10:  # Mid-range GPU (16GB)
        return 8
    elif vram_total > 6:  # Lower-end GPU (8GB)
        return 4
    else:  # Very limited VRAM
        return 2

# Load pre-trained model
logger.info("Loading pre-trained XLSR-Wav2Vec2 model...")
try:
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
except Exception as e:
    logger.error(f"Error loading pre-trained model: {e}")
    sys.exit(1)

# Freeze feature extractor part
logger.info("Freezing feature extractor parameters...")
model.freeze_feature_extractor()

# Save processor for later use
processor.save_pretrained(output_dir)

# Resume from checkpoint if exists
last_checkpoint = get_last_checkpoint(output_dir)
resume_from_checkpoint = last_checkpoint if last_checkpoint is not None else None

if resume_from_checkpoint:
    logger.info(f"Resuming from checkpoint: {resume_from_checkpoint}")
    checkpoint_step = int(resume_from_checkpoint.split("-")[-1]) if len(resume_from_checkpoint.split("-")) > 1 else 0
    logger.info(f"Continuing training with new learning rate schedule from step {checkpoint_step}")
    logger.info(f"Using cosine learning rate scheduler with restarts to continue learning")
else:
    checkpoint_step = 0
    logger.info("Starting fresh training run")

# Estimate appropriate batch size for this GPU
batch_size = estimate_batch_size()
logger.info(f"Using batch size: {batch_size}")

# Define training arguments with TensorBoard logging
training_args = TrainingArguments(
    output_dir=output_dir,
    group_by_length=True,
    per_device_train_batch_size=batch_size,
    gradient_accumulation_steps=max(1, 16 // batch_size),  # Adjust for effective batch size
    eval_strategy="steps",
    num_train_epochs=60,  # Increased from 30 to 60 epochs
    fp16=torch.cuda.is_available(),  # Use mixed precision if available
    gradient_checkpointing=True,
    save_steps=500,
    eval_steps=500,
    logging_steps=100,
    learning_rate=1e-4,  # Reduced from 3e-4 to 1e-4 for more stable continued training
    warmup_steps=0,  # Set to 0 since we're continuing training
    save_total_limit=3,
    push_to_hub=False,
    # For recovery from crashes
    save_safetensors=True,
    # TensorBoard specific settings
    report_to=["tensorboard"],
    logging_dir=os.path.join(output_dir, "logs"),
    logging_strategy="steps",
    # Performance optimization
    dataloader_num_workers=min(4, os.cpu_count() or 1),
    dataloader_pin_memory=True,
    # Learning rate scheduler
    lr_scheduler_type="cosine_with_restarts",  # Use cosine with restarts for better continued training
)

# Initialize trainer
logger.info("Initializing trainer...")
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
logger.info(f"Starting training from step {checkpoint_step}...")
try:
    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
except Exception as e:
    logger.error(f"Error during training: {e}")
    # Try to save checkpoint even if training fails
    logger.info("Attempting to save partial progress...")
    trainer.save_model(os.path.join(output_dir, "partial_checkpoint"))
    sys.exit(1)

# Save final model
logger.info("Saving final model...")
trainer.save_model(os.path.join(output_dir, "final_model"))
processor.save_pretrained(os.path.join(output_dir, "final_model"))

# Evaluation on test set
logger.info("Evaluating model on test set...")
eval_results = trainer.evaluate()
logger.info(f"Final WER: {eval_results.get('eval_wer', 'N/A')}")

# Generate a simple report
with open(os.path.join(output_dir, "training_report.txt"), "w") as f:
    f.write(f"Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Final WER: {eval_results.get('eval_wer', 'N/A')}\n")
    f.write(f"Vocabulary size: {len(vocab_dict)}\n")
    f.write(f"Training samples: {len(common_voice_train)}\n")
    f.write(f"Test samples: {len(common_voice_test)}\n")
    f.write(f"Training duration: {trainer.state.log_history[-1].get('epoch', 0):.2f} epochs\n")
    
logger.info("Training complete!")
logger.info(f"Model and processor saved to {output_dir}")
logger.info("To visualize training metrics with TensorBoard, run:")
logger.info(f"tensorboard --logdir {os.path.join(output_dir, 'logs')}")