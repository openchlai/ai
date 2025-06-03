import os
import torch
import pandas as pd
from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Check for MPS availability and set device
if torch.backends.mps.is_available():
    torch.mps.empty_cache()
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

# -------- CONFIGURATION -------- #
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 256
BATCH_SIZE = 16
EPOCHS = 10
# ------------------------------- #

# 1. Load and preprocess the synthetic data
try:
    df = pd.read_csv('child_protection_cases_kenya.csv')
except FileNotFoundError:
    raise FileNotFoundError("Could not find 'child_protection_cases_complete.csv'. Please generate it first.")

print("Columns in your CSV:", df.columns.tolist())

# 2. Prepare text and label columns
# Combine relevant fields to create comprehensive text input
def create_text_input(row):
    text_parts = [
        f"Case Narrative: {row['narrative']}",
        f"Client Details: {row['client_name']}, {row['client_age']} year old {row['client_sex']}",
        f"Location: {row['client_location']}",
        f"Reporter: {row['reporter_name']} ({row['client_relationship_with_reporter']})"  # Fixed column name here
    ]
    
    if pd.notna(row.get('perpetrator_name')):
        text_parts.append(
            f"Perpetrator: {row['perpetrator_name']} ({row['perpetrator_relationship_with_client']})"
        )
    
    return " ".join(text_parts)

df['text'] = df.apply(create_text_input, axis=1)
df['label'] = df['category_name']  # Using the category name as label

# 3. Filter out rows with missing or invalid data
print(f"Total rows before cleaning: {len(df)}")
df = df.dropna(subset=['text', 'label'])
df = df[df['text'].apply(lambda x: isinstance(x, str) and len(x) > 10)]
df = df[df['label'].apply(lambda x: isinstance(x, str))]
print(f"Total rows after cleaning: {len(df)}")

# 4. Create Hugging Face Dataset
dataset = Dataset.from_pandas(df)

# 5. Split into train/test
split_dataset = dataset.train_test_split(test_size=0.2, shuffle=True)
train_dataset = split_dataset["train"]
test_dataset = split_dataset["test"]

print(f"\nTrain examples: {len(train_dataset)}")
print(f"Test examples: {len(test_dataset)}")
print("Sample training example:", train_dataset[0]['text'][:200] + "...")

# Encode labels
label_encoder = LabelEncoder()
label_encoder.fit(df['label'])

num_labels = len(label_encoder.classes_)
print(f"\nNumber of categories: {num_labels}")
print("Categories:", label_encoder.classes_)

id2label = dict(enumerate(label_encoder.classes_))
label2id = {v: k for k, v in id2label.items()}

def encode_labels(example):
    example["label"] = label2id[example["label"]]
    return example

train_dataset = train_dataset.map(encode_labels)
test_dataset = test_dataset.map(encode_labels)

# Tokenize texts
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def tokenize_function(example):
    return tokenizer(
        example["text"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH
    )

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Set format for PyTorch
train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
test_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

# Load model
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id
).to(device)

# Metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# Training arguments
# training_args = TrainingArguments(
#     output_dir="./case_category_model",
#     evaluation_strategy="steps",
#     eval_steps=500,
#     save_strategy="steps",
#     save_steps=500,
#     learning_rate=2e-5,
#     per_device_train_batch_size=BATCH_SIZE,
#     per_device_eval_batch_size=BATCH_SIZE,
#     num_train_epochs=EPOCHS,
#     weight_decay=0.01,
#     logging_dir="./logs",
#     logging_steps=10,
#     save_total_limit=2,
#     load_best_model_at_end=True,
# )

from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir='./case_category_model',
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    learning_rate=2e-5,
    save_total_limit=2,
    do_train=True,
    do_eval=True
)


# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

# Train the model
print("\nStarting training...")
trainer.train()

# Save the final model
trainer.save_model("./case_category_model")
tokenizer.save_pretrained("./case_category_model")
print("\n✅ Model and tokenizer saved to ./case_category_model")

# Inference Example
def predict_category(text, model, tokenizer, id2label):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LENGTH)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    pred_id = torch.argmax(logits, dim=1).item()
    return id2label[pred_id]

# Example usage with synthetic-like examples
print("\nExample Predictions:")
test_cases = [
    "Case Narrative: A 12 year old female child was reported by a teacher for physical abuse. The incident occurred at school. "
    "Client Details: Mary Wanjiru, 12 year old female Location: Nairobi Reporter: John Kamau (Teacher)",
    
    "Case Narrative: A 5 year old male child was found wandering alone in the market. Reported by a neighbor who noticed the child begging. "
    "Client Details: Peter Otieno, 5 year old male Location: Kisumu Reporter: Sarah Atieno (Neighbor)",
    
    "Case Narrative: A 15 year old female child reports sexual abuse by her uncle. This was reported after the child disclosed to her teacher. "
    "Client Details: Grace Akinyi, 15 year old female Location: Mombasa Reporter: Mrs. Wambui (Teacher) "
    "Perpetrator: James Odhiambo (Relative)"
]

for text in test_cases:
    prediction = predict_category(text, model, tokenizer, id2label)
    print(f"Text: {text[:150]}...\nPredicted Category: {prediction}\n")