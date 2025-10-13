


# FLAN-T5 base Case Summarization Training Notebook
# Step 1: Install Dependencies

import pip
get_ipython().run_line_magic('pip', 'install torch transformers rouge-score wandb tqdm datasets accelerate')
import os wandb


# Step 2: Import Libraries

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer, 
    get_linear_schedule_with_warmup
)
import json
import numpy as np
from tqdm.auto import tqdm
import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rouge_score import rouge_scorer
import re
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("✅ All libraries imported successfully!")



# Step 3: Configuration
config = {
    'model_name': 'google/flan-t5-base',
    'train_data_path': 'data/train_data.jsonl',  # Change to your data path
    'val_data_path': 'data/test_data.jsonl',      # Change to your data path
    'output_dir': 'output/flan_t5_case_summarization',
    'batch_size': 1,                    # Adjust based on your GPU memory
    'learning_rate': 3e-5,
    'weight_decay': 0.01,
    'adam_epsilon': 1e-8,
    'num_epochs': 3,
    'max_source_length': 1024,
    'max_target_length': 256,
    'warmup_ratio': 0.1,
    'save_checkpoints': True,
    'use_wandb': False,                 # Set to True if you want to use wandb
    'wandb_project': 'flan-t5-case-summarization',
    'run_name': 'flan-t5-large-legal-cases'
}

print("📝 Configuration set:")
for key, value in config.items():
    print(f"  {key}: {value}")




# step 4: Check GPU and Set Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🖥️  Using device: {device}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("⚠️  No GPU available, using CPU (training will be slower)")





# Step 5: Dataset Class
class CaseSummarizationDataset(Dataset):
    """Dataset class for case summarization with Long Text and Summary format"""

    def __init__(self, data_path: str, tokenizer: T5Tokenizer, max_source_length: int = 1024, max_target_length: int = 256):
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        self.data = self.load_data(data_path)
        logger.info(f"Loaded {len(self.data)} samples from {data_path}")

    def load_data(self, data_path: str) -> List[Dict[str, str]]:
        """Load case data from various formats"""
        data = []

        if not os.path.exists(data_path):
            print(f"⚠️  Data file not found: {data_path}")
            return []

        if data_path.endswith('.json'):
            with open(data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            if isinstance(raw_data, list):
                for item in raw_data:
                    if 'Long Text:' in item and 'Summary:' in item:
                        data.append({
                            'long_text': item['Long Text:'],
                            'summary': item['Summary:']
                        })
                    elif 'long_text' in item and 'summary' in item:
                        data.append({
                            'long_text': item['long_text'],
                            'summary': item['summary']
                        })

        elif data_path.endswith('.jsonl'):
            with open(data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line)
                    if 'transcript' in item and 'summary' in item:
                        data.append({
                            'transcript': item['transcript'],
                            'summary': item['summary']
                        })

        elif data_path.endswith('.txt'):
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()

            cases = content.split('\n\n')

            for case in cases:
                if 'transcript:' in case and 'Summary:' in case:
                    long_text_match = re.search(r'transcript:\s*(.*?)\s*Summary:', case, re.DOTALL)
                    summary_match = re.search(r'Summary:\s*(.*?)$', case, re.DOTALL)

                    if long_text_match and summary_match:
                        data.append({
                            'transcript': long_text_match.group(1).strip(),
                            'summary': summary_match.group(1).strip()
                        })

        return data


    def __len__(self):
            return len(self.data)

    def __getitem__(self, idx):
            item = self.data[idx]

            source_text = f"Summarize the following legal case: {item['transcript']}"
            target_text = item['summary']

            source_encoding = self.tokenizer(
                source_text,
                max_length=self.max_source_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )

            target_encoding = self.tokenizer(
                target_text,
                max_length=self.max_target_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )

            return {
                'input_ids': source_encoding['input_ids'].flatten(),
                'attention_mask': source_encoding['attention_mask'].flatten(),
                'labels': target_encoding['input_ids'].flatten()
            }

    print("✅ Dataset class defined")





# Step 6: Load Model and Tokenizer
print("📥 Loading model and tokenizer...")
tokenizer = T5Tokenizer.from_pretrained(config['model_name'])
model = T5ForConditionalGeneration.from_pretrained(config['model_name'])
model.to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"✅ Model loaded: {total_params:,} parameters")




# Step 7: Create Sample Data (if you don't have data yet)
def create_sample_data():
    """Create sample data for testing"""
    sample_data = [
        {"transcript": "Hello, is this 116? Yes, thank you for your call. Who am I speaking with? My name is Ahmed, and I'm calling from Mombasa. I have a problem that requires immediate attention. A friend of mine has a daughter, only 5 years old, who is being forced into child labor at a local factory. This sounds dire, Ahmed. Thank you for bringing this to our notice. Has anyone else noticed this? Sadly, no one seems to care. She looks exhausted and malnourished. I'm worried sick. I understand your concern. The best thing you can do is report it to the Mombasa Child Welfare Society and also to the police. We can follow up on this case too. Please don't hesitate to call again.", "summary": "Ahmed reported a case of child labor involving a 5-year-old girl in Mombasa. The child appears exhausted and malnourished. Immediate action is necessary as no one else seems aware."},

        {"transcript": "Hello, is this the Childline helpline? Yes, good day. This is Jane speaking from Kisumu. I'm seeking help because my younger brother, who is only 12, has been forced into child labor at a local workshop. That sounds concerning, Jane. I appreciate you reaching out. Have others noticed this too? Yes, but they are afraid to speak up. He comes home with cuts and bruises. I'm worried about his safety. I understand your concerns. The best step is to report it to the Kisumu Child Protection Unit and also to the local police. We can follow up on the situation as well. Please don't hesitate to call again.", "summary": "Jane from Kisumu reported a case of child labor involving her younger brother. The issue is urgent due to visible signs of abuse and fear of retaliation. Referral is made to local Child Protection Unit and police, with follow-up promised."}

    ]

    # Create directories
    os.makedirs('data', exist_ok=True)

    # Save sample data
    with open('data/train_data.jsonl', 'w') as f:
        json.dump(sample_data * 50, f, indent=2)  # Multiply for more samples

    with open('data/test_data.jsonl', 'w') as f:
        json.dump(sample_data * 10, f, indent=2)

    print("✅ Sample data created in data/ folder")

# Uncomment the next line if you want to create sample data
#create_sample_data()





# Step 8: Load Datasets
print("📊 Loading datasets...")

train_dataset = CaseSummarizationDataset(
    config['train_data_path'],
    tokenizer,
    config['max_source_length'],
    config['max_target_length']
)

val_dataset = CaseSummarizationDataset(
    config['val_data_path'],
    tokenizer,
    config['max_source_length'],
    config['max_target_length']
) if os.path.exists(config['val_data_path']) else None

print(f"📈 Training samples: {len(train_dataset)}")
print(f"📊 Validation samples: {len(val_dataset) if val_dataset else 0}")





# Step 9: Create Data Loaders
train_loader = DataLoader(
    train_dataset,
    batch_size=config['batch_size'],
    shuffle=True,
    num_workers=2,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=config['batch_size'],
    shuffle=False,
    num_workers=2,
    pin_memory=True
) if val_dataset else None

print(f"🔄 Training batches: {len(train_loader)}")
print(f"🔄 Validation batches: {len(val_loader) if val_loader else 0}")




# Step 10: Define which parameters not to apply weight decay to
no_decay = ["bias", "LayerNorm.weight"]
# Initialize Optimizer and Scheduler
optimizer_grouped_parameters = [
    {
        "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
        "weight_decay": config['weight_decay'],
    },
    {
        "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
        "weight_decay": 0.0,
    },
]

optimizer = AdamW(
    optimizer_grouped_parameters,
    lr=config['learning_rate'],
    eps=config['adam_epsilon']
)

total_steps = len(train_loader) * config['num_epochs']
warmup_steps = int(config['warmup_ratio'] * total_steps)

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps
)

rouge_scorer_obj = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

print("✅ Optimizer and scheduler initialized")




# Step 11: Training Functions
def train_epoch(epoch: int):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    num_batches = len(train_loader)

    progress_bar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{config["num_epochs"]}')

    for batch_idx, batch in enumerate(progress_bar):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        labels[labels == tokenizer.pad_token_id] = -100

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss
        total_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        scheduler.step()

        current_lr = scheduler.get_last_lr()[0]
        progress_bar.set_postfix({
            'Loss': f'{loss.item():.4f}',
            'Avg Loss': f'{total_loss / (batch_idx + 1):.4f}',
            'LR': f'{current_lr:.2e}'
        })

    avg_loss = total_loss / len(train_loader)
    print(f'Epoch {epoch+1} - Average training loss: {avg_loss:.4f}')
    return avg_loss

def generate_summary(text: str, max_length: int = 256) -> str:
    """Generate summary for a child helpline case call transcript"""
    input_text = f"Summarize this helpline call: {text}"

    inputs = tokenizer(
        input_text,
        max_length=config['max_source_length'],
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=max_length,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True,
            no_repeat_ngram_size=2
        )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

def validate():
    """Validate the model"""
    if not val_loader:
        return None

    model.eval()
    total_loss = 0
    rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}

    with torch.no_grad():
        for batch_idx, batch in enumerate(tqdm(val_loader, desc='Validating')):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            labels[labels == tokenizer.pad_token_id] = -100

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            total_loss += outputs.loss.item()

            # Calculate ROUGE scores for first 5 batches
            if batch_idx < 5:
                generated_ids = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_length=config['max_target_length'],
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True,
                    no_repeat_ngram_size=2
                )

                for i in range(len(generated_ids)):
                    generated_summary = tokenizer.decode(generated_ids[i], skip_special_tokens=True)
                    reference_summary = tokenizer.decode(
                        labels[i][labels[i] != -100], skip_special_tokens=True
                    )

                    scores = rouge_scorer_obj.score(reference_summary, generated_summary)
                    rouge_scores['rouge1'].append(scores['rouge1'].fmeasure)
                    rouge_scores['rouge2'].append(scores['rouge2'].fmeasure)
                    rouge_scores['rougeL'].append(scores['rougeL'].fmeasure)

    avg_loss = total_loss / len(val_loader)
    avg_rouge_scores = {k: np.mean(v) for k, v in rouge_scores.items()}

    print(f'Validation loss: {avg_loss:.4f}')
    print(f'ROUGE-1: {avg_rouge_scores["rouge1"]:.4f}')
    print(f'ROUGE-2: {avg_rouge_scores["rouge2"]:.4f}')
    print(f'ROUGE-L: {avg_rouge_scores["rougeL"]:.4f}')

    return avg_loss, avg_rouge_scores

print("✅ Training functions defined")





# Step 12: Test with Sample Data
if len(train_dataset) > 0:
    print("🧪 Testing with sample data...")
    sample_item = train_dataset[0]
    print(f"Input length: {len(sample_item['input_ids'])}")
    print(f"Label length: {len(sample_item['labels'])}")

    # Test generation before training
    sample_text = train_dataset.data[0]['transcript'][:500]  # First 500 chars
    print("\n📝 Sample text:")
    print(sample_text)

    print("\n🎯 Original summary:")
    print(train_dataset.data[0]['summary'])

    print("\n🤖 Generated summary (before training):")
    generated = generate_summary(sample_text)
    print(generated)
else:
    print("⚠️  No training data found. Please check your data path.")






get_ipython().run_line_magic('pip', 'install mlflow')
import mlflow
import mlflow.pytorch
def train_model():
    """Main training function with real-time MLflow logging"""
    print('🚀 Starting FLAN-T5 Case Summarization training...')

    # Create output directory
    os.makedirs(config['output_dir'], exist_ok=True)

    # Track training history
    train_losses = []
    val_losses = []
    rouge_scores_history = []

    best_val_loss = float('inf')
    best_rouge_l = 0.0

    # 🧠 START MLflow run here
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("flan_t5_case_summarization_3")

    with mlflow.start_run():
        # Log config parameters once
        for key, value in config.items():
            mlflow.log_param(key, value)

        for epoch in range(config['num_epochs']):
            print(f"\n📅 Epoch {epoch+1}/{config['num_epochs']}")
            print("=" * 50)

            # Training
            train_loss = train_epoch(epoch)
            train_losses.append(train_loss)
            mlflow.log_metric("train_loss", train_loss, step=epoch)  # ✅ Log train loss

            # ✅ Log current learning rate from scheduler
            current_lr = scheduler.get_last_lr()[0]  # For most PyTorch schedulers
            mlflow.log_metric("learning_rate", current_lr, step=epoch)

            # Validation
            val_results = validate()
            if val_results:
                val_loss, rouge_scores = val_results
                val_losses.append(val_loss)
                rouge_scores_history.append(rouge_scores)

                # ✅ Log validation loss and ROUGE metrics
                mlflow.log_metric("val_loss", val_loss, step=epoch)
                mlflow.log_metric("rouge1", rouge_scores['rouge1'], step=epoch)
                mlflow.log_metric("rouge2", rouge_scores['rouge2'], step=epoch)
                mlflow.log_metric("rougeL", rouge_scores['rougeL'], step=epoch)

                # Save best model
                if rouge_scores['rougeL'] > best_rouge_l:
                    best_rouge_l = rouge_scores['rougeL']
                    best_model_path = os.path.join(config['output_dir'], 'best_model')
                    model.save_pretrained(best_model_path)
                    tokenizer.save_pretrained(best_model_path)
                    print(f'💾 Best model saved with ROUGE-L: {best_rouge_l:.4f}')

                    # ✅ Log best model and tokenizer
                    mlflow.pytorch.log_model(model, artifact_path="best_model")
                    mlflow.log_artifacts(best_model_path, artifact_path="tokenizer")

            # Save checkpoint
            if config['save_checkpoints']:
                checkpoint_path = os.path.join(config['output_dir'], f'checkpoint_epoch_{epoch+1}.pt')
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'loss': train_loss,
                    'config': config
                }, checkpoint_path)

                mlflow.log_artifact(checkpoint_path)  # ✅ Log checkpoint

        print('\n🎉 Training completed!')

    return train_losses, val_losses, rouge_scores_history




# Step 14: Run Training
train_losses, val_losses, rouge_scores_history = train_model()


# In[15]:


# Test Generation After Training
def test_generation():
    """Test the model after training"""
    print("🧪 Testing model generation...")

    if len(train_dataset) > 0:
        # Test with a few samples
        for i in range(min(3, len(train_dataset))):
            sample = train_dataset.data[i]
            print(f"\n📝 Test Case {i+1}:")
            print("-" * 30)
            print(f"Original text: {sample['long_text'][:200]}...")
            print(f"\nOriginal summary: {sample['summary']}")
            print(f"\nGenerated summary: {generate_summary(sample['long_text'])}")
            print("-" * 50)






# Save and Load Model Functions
def save_final_model():
    """Save the final trained model"""
    final_model_path = os.path.join(config['output_dir'], 'final_model')
    model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"💾 Final model saved to: {final_model_path}")

def load_trained_model(model_path):
    """Load a trained model"""
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model.to(device)
    print(f"✅ Model loaded from: {model_path}")
    return model, tokenizer

print("✅ All functions defined and ready to use!")
print("\n🚀 To start training, run: train_losses, val_losses, rouge_history = train_model()")
print("🧪 To test generation, run: test_generation()")





save_final_model()




# Final cleanup cell — run this manually after each training round
import gc
import torch

# Clear Python garbage
gc.collect()

# Empty GPU cache
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Optional: Print GPU memory summary
print("🧹 GPU cache cleared.")

